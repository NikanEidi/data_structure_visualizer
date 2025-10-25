import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import copy
import random
import string
import time
from .graphStyle import CSS, GRAPH_LAYOUT_CONFIG, COLORS

SAMPLES = {

    "Straight Chain": {
        "A": ["B"],
        "B": ["C"],
        "C": ["D"],
        "D": []
    },


    "Simple Branch": {
        "A": ["B", "C"],
        "B": ["D"],
        "C": [],
        "D": []
    },

    "Small Cycle": {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"]
    },

    
    "Mini Tree": {
        "Root": ["L1", "R1"],
        "L1": ["L2"],
        "R1": ["R2"],
        "L2": [],
        "R2": []
    },

    "Cross Path": {
        "P": ["Q", "R"],
        "Q": ["R"],
        "R": ["S"],
        "S": []
    }
}

class DFSVisualizer:
    def __init__(self):
        self.ns = "dfs"

    def render(self):
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Directed Graph (DFS Traversal)</h2>', unsafe_allow_html=True)

        mode = st.sidebar.radio("Input mode:", ["Use sample graph", "Build your own"], key=f"{self.ns}_mode")

        if mode == "Use sample graph":
            sample = st.sidebar.selectbox("Select sample:", list(SAMPLES.keys()), key=f"{self.ns}_sample")
            base = SAMPLES[sample]
            V = list(base.keys())
            W = pd.DataFrame(0, index=V, columns=V)
            for u, nbrs in base.items():
                for v in nbrs:
                    W.loc[u, v] = 1
            editable = False
            gkey = f"sample::{sample}"
        else:
            n = st.sidebar.slider("Number of vertices", 2, 10, 5, key=f"{self.ns}_n")
            names = [x.strip() for x in st.sidebar.text_input("Vertex names", ",".join(string.ascii_uppercase[:n]), key=f"{self.ns}_names").split(",") if x.strip()]
            if len(names) < 2:
                st.stop()
            key = f"custom::{','.join(names)}::{n}"
            if f"{self.ns}_adj_key" not in st.session_state or st.session_state[f"{self.ns}_adj_key"] != key:
                M = pd.DataFrame(0, index=names, columns=names)
                for i, u in enumerate(names):
                    for j, v in enumerate(names):
                        if u != v and random.random() > 0.55:
                            M.loc[u, v] = 1
                st.session_state[f"{self.ns}_adj_df"] = M
                st.session_state[f"{self.ns}_adj_key"] = key
            W = st.session_state[f"{self.ns}_adj_df"].copy()
            editable = True
            gkey = key

        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3 style="margin-top:1rem;">DFS Options</h3>', unsafe_allow_html=True)
        st.sidebar.selectbox("Start vertex:", W.index, key=f"{self.ns}_start")
        start_vertex = st.session_state[f"{self.ns}_start"]
        auto = st.sidebar.checkbox("Auto-Play", False, key=f"{self.ns}_auto")
        speed = st.sidebar.slider("Speed (sec/step)", 0.3, 2.5, 0.9, 0.1, key=f"{self.ns}_speed")

        st.markdown('<h2 class="section-header">Adjacency Matrix</h2>', unsafe_allow_html=True)
        if editable:
            edited = st.data_editor(W, num_rows="fixed", disabled=False, key=f"{self.ns}_editor", use_container_width=True)
            st.session_state[f"{self.ns}_adj_df"] = edited.astype(int)
            W = edited.astype(int)
        else:
            st.dataframe(W, use_container_width=True)

        G = {u: [v for v in W.columns if W.loc[u, v] == 1] for u in W.index}

        def push_state():
            st.session_state[f"{self.ns}_hist"].append(copy.deepcopy({
                "visited": st.session_state[f"{self.ns}_visited"],
                "path": st.session_state[f"{self.ns}_path"],
                "current": st.session_state[f"{self.ns}_current"],
                "order": st.session_state[f"{self.ns}_order"],
                "edges": st.session_state[f"{self.ns}_edges"],
                "exp": st.session_state[f"{self.ns}_exp"],
                "fin": st.session_state[f"{self.ns}_fin"],
                "step": st.session_state[f"{self.ns}_step"],
            }))

        def restore_state(s):
            st.session_state[f"{self.ns}_visited"] = copy.deepcopy(s["visited"])
            st.session_state[f"{self.ns}_path"] = copy.deepcopy(s["path"])
            st.session_state[f"{self.ns}_current"] = s["current"]
            st.session_state[f"{self.ns}_order"] = copy.deepcopy(s["order"])
            st.session_state[f"{self.ns}_edges"] = copy.deepcopy(s["edges"])
            st.session_state[f"{self.ns}_exp"] = s["exp"]
            st.session_state[f"{self.ns}_fin"] = s["fin"]
            st.session_state[f"{self.ns}_step"] = s["step"]

        def init_state():
            st.session_state[f"{self.ns}_visited"] = {v: False for v in W.index}
            st.session_state[f"{self.ns}_path"] = [start_vertex]
            st.session_state[f"{self.ns}_current"] = None
            st.session_state[f"{self.ns}_order"] = []
            st.session_state[f"{self.ns}_edges"] = []
            st.session_state[f"{self.ns}_exp"] = f'<div class="step-header">[INITIALIZATION]</div><div class="step-info">Start at {start_vertex}. Begin exploring paths.</div>'
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_gkey"] = gkey
            st.session_state[f"{self.ns}_step"] = 0
            push_state()

        def step_dfs():
            if st.session_state[f"{self.ns}_fin"]:
                return
            st.session_state[f"{self.ns}_step"] += 1
            lines = [f'<div class="step-header">[STEP {st.session_state[f"{self.ns}_step"]}]</div>']

            if not st.session_state[f"{self.ns}_path"]:
                st.session_state[f"{self.ns}_fin"] = True
                order = " → ".join(st.session_state[f"{self.ns}_order"])
                lines.append(f'<div class="completed-text">Traversal finished. Path explored: {order}</div>')
                st.session_state[f"{self.ns}_exp"] = "".join(lines)
                return

            u = st.session_state[f"{self.ns}_path"].pop()
            st.session_state[f"{self.ns}_current"] = u

            if not st.session_state[f"{self.ns}_visited"][u]:
                st.session_state[f"{self.ns}_visited"][u] = True
                st.session_state[f"{self.ns}_order"].append(u)
                lines.append(f'<div class="step-info">Now visiting vertex: <strong>{u}</strong></div>')
                next_vertices = [v for v in G[u] if not st.session_state[f"{self.ns}_visited"][v]]

                if next_vertices:
                    lines.append('<div class="neighbors-header">Connected vertices:</div>')
                    for v in reversed(next_vertices):
                        st.session_state[f"{self.ns}_path"].append(v)
                    st.session_state[f"{self.ns}_edges"] = [(u, v) for v in next_vertices]
                    lines.append(f'<div class="update-text">Edges explored: {" , ".join([f"{u}→{v}" for v in next_vertices])}</div>')
                    lines.append(f'<div class="step-info">Path to explore next: {" → ".join(reversed(st.session_state[f"{self.ns}_path"]))}</div>')
                else:
                    st.session_state[f"{self.ns}_edges"] = []
                    lines.append('<div class="visited-text">No outgoing edges from this vertex.</div>')
            else:
                lines.append(f'<div class="visited-text">Vertex <strong>{u}</strong> already visited, skipping.</div>')
                st.session_state[f"{self.ns}_edges"] = []

            # Table
            lines.append('<div class="table-header">Current Exploration Table:</div>')
            lines.append('<table class="custom-table"><tr><th>Vertex</th><th>Visited</th><th>Visit Order</th></tr>')
            for v in sorted(W.index):
                visited = "Yes" if st.session_state[f"{self.ns}_visited"][v] else "No"
                order = st.session_state[f"{self.ns}_order"].index(v)+1 if v in st.session_state[f"{self.ns}_order"] else "-"
                row_class = "visited-row" if st.session_state[f"{self.ns}_visited"][v] else "current-row" if v == st.session_state[f"{self.ns}_current"] else "unvisited-row"
                lines.append(f'<tr class="{row_class}"><td>{v}</td><td>{visited}</td><td>{order}</td></tr>')
            lines.append('</table>')

            st.session_state[f"{self.ns}_exp"] = "".join(lines)

        if f"{self.ns}_gkey" not in st.session_state:
            init_state()
        elif st.session_state[f"{self.ns}_gkey"] != gkey:
            init_state()

        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3>Algorithm Controls</h3>', unsafe_allow_html=True)
        c1, c2, c3 = st.sidebar.columns(3)
        next_clicked = c1.button("Next", use_container_width=True, type="primary", disabled=st.session_state[f"{self.ns}_fin"])
        back_clicked = c2.button("Back", use_container_width=True, type="primary", disabled=len(st.session_state[f"{self.ns}_hist"]) <= 1)
        reset_clicked = c3.button("Reset", use_container_width=True, type="primary")

        if next_clicked:
            step_dfs()
            push_state()
        if back_clicked and len(st.session_state[f"{self.ns}_hist"]) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            restore_state(st.session_state[f"{self.ns}_hist"][-1])
        if reset_clicked:
            init_state()

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Step", st.session_state[f"{self.ns}_step"])
        with m2: st.metric("Visited", sum(st.session_state[f"{self.ns}_visited"].values()))
        with m3: st.metric("Remaining", len(W.index) - sum(st.session_state[f"{self.ns}_visited"].values()))
        with m4: st.metric("Status", "Done" if st.session_state[f"{self.ns}_fin"] else "Exploring")

        col1, col2 = st.columns([1.4, 1])
        with col1:
            st.markdown('<h2 class="section-header">Directed Graph Visualization</h2>', unsafe_allow_html=True)
            self.draw_graph(W, start_vertex)
        with col2:
            st.markdown('<h2 class="section-header">Traversal Table</h2>', unsafe_allow_html=True)
            self.display_state_table(W.index)

        st.markdown("---")
        st.markdown('<h2 class="section-header">Exploration Steps</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-card">{st.session_state[f"{self.ns}_exp"]}</div>', unsafe_allow_html=True)
        if st.session_state[f"{self.ns}_fin"]:
            st.success("DFS traversal complete")

        if auto and not st.session_state[f"{self.ns}_fin"]:
            step_dfs()
            push_state()
            time.sleep(speed)
            st.rerun()

    def draw_graph(self, W, start_vertex):
        fig, ax = plt.subplots(figsize=(10, 8))
        G = nx.DiGraph()
        for u in W.index:
            for v in W.columns:
                if W.loc[u, v] == 1:
                    G.add_edge(u, v)
        pos = nx.spring_layout(G, seed=42, k=1.4)
        node_colors = []
        for v in G.nodes():
            if v == start_vertex:
                node_colors.append(COLORS['source'])
            elif st.session_state[f"{self.ns}_visited"][v]:
                node_colors.append(COLORS['visited'])
            elif v == st.session_state[f"{self.ns}_current"]:
                node_colors.append(COLORS['current'])
            else:
                node_colors.append(COLORS['unvisited'])
        edge_colors, edge_widths = [], []
        for e in G.edges():
            if e in st.session_state[f"{self.ns}_edges"]:
                edge_colors.append(GRAPH_LAYOUT_CONFIG['edge_color_highlight'])
                edge_widths.append(2.6)
            else:
                edge_colors.append(GRAPH_LAYOUT_CONFIG['edge_color_regular'])
                edge_widths.append(1.3)
        nx.draw(
            G, pos,
            with_labels=True, arrows=True, arrowsize=22,
            node_color=node_colors, edge_color=edge_colors, width=edge_widths,
            node_size=GRAPH_LAYOUT_CONFIG['node_size'],
            font_size=13, font_color="#fff", ax=ax
        )
        ax.set_facecolor(COLORS['background'])
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    def display_state_table(self, V):
        df = pd.DataFrame({
            "Vertex": V,
            "Visited": ["Yes" if st.session_state[f"{self.ns}_visited"][v] else "No" for v in V],
            "Visit Order": [
                str(st.session_state[f"{self.ns}_order"].index(v) + 1)
                if v in st.session_state[f"{self.ns}_order"] else "-"
                for v in V
            ]
        })
        df = df.astype(str)
        st.dataframe(df, width='stretch', hide_index=True)