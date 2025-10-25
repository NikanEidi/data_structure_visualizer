import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import copy
import random
import string
import time
from ...components.graphStyle import CSS, COLORS 

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

class BFSVisualizer:
    def __init__(self):
        self.ns = "bfs"

    def render(self):
        st.markdown(CSS, unsafe_allow_html=True)
        mode = st.sidebar.radio("Input mode:", ["Use sample graph", "Build your own"], key=f"{self.ns}_mode")
        
        if mode == "Use sample graph":
            sample = st.sidebar.selectbox("Select sample:", list(SAMPLES.keys()), key=f"{self.ns}_sample")
            base = SAMPLES[sample]
            V = list(base.keys())
            W = pd.DataFrame(0, index=V, columns=V)
            for u, neighbors in base.items():
                for v in neighbors:
                    W.loc[u, v] = 1
            editable = False
            gkey = f"sample::{sample}"
        else:
            n = st.sidebar.slider("Number of vertices", 2, 12, 5, key=f"{self.ns}_n")
            default = list(string.ascii_uppercase[:n])
            names = st.sidebar.text_input("Vertex names (comma-separated)", ",".join(default), key=f"{self.ns}_names")
            V = [x.strip() for x in names.split(",") if x.strip()]
            if len(V) < 2:
                st.stop()
            init_key = f"custom::{','.join(V)}::{n}"
            if f"{self.ns}_weight_key" not in st.session_state or st.session_state[f"{self.ns}_weight_key"] != init_key:
                M = pd.DataFrame(0, index=V, columns=V, dtype=int)
                for i, u in enumerate(V):
                    for j, v in enumerate(V):
                        if i != j and random.random() > 0.4:
                            M.loc[u, v] = 1
                st.session_state[f"{self.ns}_weight_df"] = M.copy()
                st.session_state[f"{self.ns}_weight_key"] = init_key
            W = st.session_state[f"{self.ns}_weight_df"].copy()
            editable = True
            gkey = init_key

        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3 style="margin-top:1rem;">BFS Configuration</h3>', unsafe_allow_html=True)
        st.sidebar.selectbox("Start vertex:", V, key=f"{self.ns}_start")
        start_vertex = st.session_state[f"{self.ns}_start"]

        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3>Auto-Play</h3>', unsafe_allow_html=True)
        auto = st.sidebar.checkbox("Enable Auto-Play", value=False, key=f"{self.ns}_auto")
        speed = st.sidebar.slider("Speed (seconds per step)", 0.5, 3.0, 1.0, 0.1, key=f"{self.ns}_speed")

        st.markdown('<h2 class="section-header">Adjacency Matrix</h2>', unsafe_allow_html=True)
        if editable:
            edited = st.data_editor(W, num_rows="fixed", disabled=False, key=f"{self.ns}_adj_editor", use_container_width=True)
            sym = edited.copy()
            for i, u in enumerate(V):
                for j, v in enumerate(V):
                    if i != j:
                        val = max(edited.loc[u, v], edited.loc[v, u])
                        sym.loc[u, v] = val
                        sym.loc[v, u] = val
            st.session_state[f"{self.ns}_weight_df"] = sym.astype(int).copy()
            W = sym.astype(int).copy()
        else:
            st.dataframe(W.astype(int).copy(), use_container_width=True)

        G = {u: [] for u in V}
        for u in V:
            for v in V:
                if u != v and W.loc[u, v] == 1:
                    G[u].append(v)

        def push():
            st.session_state[f"{self.ns}_hist"].append(copy.deepcopy({
                "visited": st.session_state[f"{self.ns}_visited"],
                "queue": st.session_state[f"{self.ns}_queue"],
                "current": st.session_state[f"{self.ns}_current"],
                "order": st.session_state[f"{self.ns}_order"],
                "edges": st.session_state[f"{self.ns}_edges"],
                "exp": st.session_state[f"{self.ns}_exp"],
                "fin": st.session_state[f"{self.ns}_fin"],
                "step": st.session_state[f"{self.ns}_step"],
            }))

        def restore(s):
            st.session_state[f"{self.ns}_visited"] = copy.deepcopy(s["visited"])
            st.session_state[f"{self.ns}_queue"] = copy.deepcopy(s["queue"])
            st.session_state[f"{self.ns}_current"] = s["current"]
            st.session_state[f"{self.ns}_order"] = copy.deepcopy(s["order"])
            st.session_state[f"{self.ns}_edges"] = copy.deepcopy(s["edges"])
            st.session_state[f"{self.ns}_exp"] = s["exp"]
            st.session_state[f"{self.ns}_fin"] = s["fin"]
            st.session_state[f"{self.ns}_step"] = s["step"]

        def init_state():
            st.session_state[f"{self.ns}_visited"] = {v: False for v in V}
            st.session_state[f"{self.ns}_queue"] = [start_vertex]
            st.session_state[f"{self.ns}_current"] = None
            st.session_state[f"{self.ns}_order"] = []
            st.session_state[f"{self.ns}_edges"] = []
            st.session_state[f"{self.ns}_exp"] = (
                f'<div class="step-header">[INITIALIZATION]</div>'
                f'<div class="step-info">Start at {start_vertex}. Put {start_vertex} in the line.</div>'
            )
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_gkey"] = gkey
            st.session_state[f"{self.ns}_start_val"] = start_vertex
            st.session_state[f"{self.ns}_step"] = 0
            push()

        def step_bfs():
            if st.session_state[f"{self.ns}_fin"]:
                return

            st.session_state[f"{self.ns}_step"] += 1
            lines = [f'<div class="step-header">[STEP {st.session_state[f"{self.ns}_step"]}]</div>']

            if not st.session_state[f"{self.ns}_queue"]:
                st.session_state[f"{self.ns}_fin"] = True
                lines.append('<div class="step-info">No vertices left in the line. Done.</div>')
                lines.append(f'<div class="completed-text">Order: {" → ".join(st.session_state[f"{self.ns}_order"])}</div>')
                st.session_state[f"{self.ns}_exp"] = "".join(lines)
                return

            u = st.session_state[f"{self.ns}_queue"].pop(0)
            st.session_state[f"{self.ns}_current"] = u

            if not st.session_state[f"{self.ns}_visited"][u]:
                st.session_state[f"{self.ns}_visited"][u] = True
                st.session_state[f"{self.ns}_order"].append(u)

                lines.append(f'<div class="step-info">Take {u} from the front. Mark {u} as visited.</div>')
                next_vertices = [v for v in sorted(G[u]) if not st.session_state[f"{self.ns}_visited"][v]]

                new_edges = []
                if next_vertices:
                    lines.append('<div class="neighbors-header">Add unvisited neighbors to the end:</div>')
                    for v in next_vertices:
                        if v not in st.session_state[f"{self.ns}_queue"]:
                            st.session_state[f"{self.ns}_queue"].append(v)
                            new_edges.append((u, v))
                            lines.append(f'<div class="update-text">- Add {v}</div>')
                    st.session_state[f"{self.ns}_edges"] = new_edges
                    lines.append(
                        f'<div class="step-info">Edges used: '
                        f'{" , ".join([f"{u}—{v}" for v in next_vertices])}</div>'
                    )
                else:
                    st.session_state[f"{self.ns}_edges"] = []
                    lines.append('<div class="visited-text">No neighbors to add.</div>')
            else:
                lines.append(f'<div class="visited-text">{u} is already visited. Skip it.</div>')
                st.session_state[f"{self.ns}_edges"] = []

            lines.append('<div class="table-header">Current State:</div>')
            lines.append('<table class="custom-table">')
            lines.append('<tr><th>Vertex</th><th>Visited</th><th>Visit Order</th></tr>')
            for v in sorted(V):
                visited = "Yes" if st.session_state[f"{self.ns}_visited"][v] else "No"
                order = st.session_state[f"{self.ns}_order"].index(v) + 1 if v in st.session_state[f"{self.ns}_order"] else "-"
                row_class = (
                    "visited-row" if st.session_state[f"{self.ns}_visited"][v]
                    else "current-row" if v == st.session_state[f"{self.ns}_current"]
                    else "unvisited-row"
                )
                lines.append(f'<tr class="{row_class}"><td>{v}</td><td>{visited}</td><td>{order}</td></tr>')
            lines.append('</table>')

            lines.append('<div class="table-header">Line (Queue):</div>')
            queue_display = " ← ".join([f"[{v}]" for v in st.session_state[f"{self.ns}_queue"]]) if st.session_state[f"{self.ns}_queue"] else "Empty"
            lines.append(f'<div class="step-info">{queue_display}</div>')

            if st.session_state[f"{self.ns}_queue"]:
                lines.append(f'<div class="next-step">Next to take: {st.session_state[f"{self.ns}_queue"][0]}</div>')
            else:
                lines.append('<div class="next-step">Line is empty.</div>')

            st.session_state[f"{self.ns}_exp"] = "".join(lines)

        if f"{self.ns}_gkey" not in st.session_state:
            init_state()
        elif st.session_state[f"{self.ns}_gkey"] != gkey or st.session_state[f"{self.ns}_start_val"] != start_vertex:
            init_state()

        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3>Algorithm Controls</h3>', unsafe_allow_html=True)
        c1, c2, c3 = st.sidebar.columns(3)
        next_clicked = c1.button("Next Step", use_container_width=True, type="primary", disabled=st.session_state[f"{self.ns}_fin"])
        back_clicked = c2.button("Back", use_container_width=True, type="primary", disabled=len(st.session_state[f"{self.ns}_hist"]) <= 1)
        reset_clicked = c3.button("Reset", use_container_width=True, type="primary")

        manual_advanced = False
        if next_clicked:
            if not st.session_state[f"{self.ns}_fin"]:
                step_bfs()
                push()
                manual_advanced = True
        if back_clicked and len(st.session_state[f"{self.ns}_hist"]) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            restore(st.session_state[f"{self.ns}_hist"][-1])
            manual_advanced = True
        if reset_clicked:
            init_state()
            manual_advanced = True

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Current Step", st.session_state[f"{self.ns}_step"])
            st.markdown('</div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Vertices Visited", sum(st.session_state[f"{self.ns}_visited"].values()))
            st.markdown('</div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Vertices Remaining", len(V) - sum(st.session_state[f"{self.ns}_visited"].values()))
            st.markdown('</div>', unsafe_allow_html=True)
        with m4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Status", "Complete" if st.session_state[f"{self.ns}_fin"] else "Running")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        col1, col2 = st.columns([1.4, 1])
        with col1:
            st.markdown('<h2 class="section-header">Graph Visualization</h2>', unsafe_allow_html=True)
            self.draw_graph(V, W, start_vertex)
        with col2:
            st.markdown('<h2 class="section-header">BFS State</h2>', unsafe_allow_html=True)
            self.display_state_table(V)

        st.markdown("---")
        st.markdown('<h2 class="section-header">Step-by-Step Explanation</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-card">{st.session_state[f"{self.ns}_exp"]}</div>', unsafe_allow_html=True)
        
        if st.session_state[f"{self.ns}_fin"]:
            st.success("BFS traversal completed successfully!")

        manual_advanced = next_clicked or back_clicked or reset_clicked
        if auto and not st.session_state[f"{self.ns}_fin"] and not manual_advanced:
            step_bfs()
            push()
            time.sleep(speed)
            st.rerun()

    def draw_graph(self, V, W, start_vertex):
        fig, ax = plt.subplots(figsize=(11, 9))
        G = nx.Graph()
        for u in V:
            G.add_node(u)
        for u in V:
            for v in V:
                if u < v and W.loc[u, v] == 1:
                    G.add_edge(u, v)
        pos = nx.spring_layout(G, seed=42, k=1.8)

        node_colors = []
        for v in G.nodes():
            if v == start_vertex:
                node_colors.append(COLORS['source'])
            elif st.session_state[f"{self.ns}_visited"].get(v, False):
                node_colors.append(COLORS['visited'])
            elif v == st.session_state[f"{self.ns}_current"] and not st.session_state[f"{self.ns}_fin"]:
                node_colors.append(COLORS['current'])
            else:
                node_colors.append(COLORS['unvisited'])

        edge_colors = []
        edge_widths = []
        for (u, v) in G.edges():
            if (u, v) in st.session_state[f"{self.ns}_edges"] or (v, u) in st.session_state[f"{self.ns}_edges"]:
                edge_colors.append(GRAPH_LAYOUT_CONFIG['edge_color_highlight'])
                edge_widths.append(GRAPH_LAYOUT_CONFIG['edge_width_highlight'])
            else:
                edge_colors.append(GRAPH_LAYOUT_CONFIG['edge_color_regular'])
                edge_widths.append(GRAPH_LAYOUT_CONFIG['edge_width_regular'])

        nx.draw_networkx_nodes(
            G, pos, 
            node_color=node_colors, 
            node_size=GRAPH_LAYOUT_CONFIG['node_size'], 
            ax=ax, 
            edgecolors=GRAPH_LAYOUT_CONFIG['node_border_color'], 
            linewidths=GRAPH_LAYOUT_CONFIG['node_border_width']
        )
        nx.draw_networkx_labels(
            G, pos, 
            font_size=GRAPH_LAYOUT_CONFIG['font_size'], 
            font_weight=GRAPH_LAYOUT_CONFIG['font_weight'], 
            ax=ax, 
            font_color=GRAPH_LAYOUT_CONFIG['font_color']
        )
        for i, (uu, vv) in enumerate(G.edges()):
            nx.draw_networkx_edges(
                G, pos, 
                [(uu, vv)], 
                edge_color=[edge_colors[i]], 
                width=[edge_widths[i]], 
                ax=ax
            )

        ax.set_facecolor(COLORS['background'])
        ax.axis("off")
        plt.tight_layout()
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