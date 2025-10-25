import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math, copy, random, string, time
from .graphStyle import CSS, GRAPH_LAYOUT_CONFIG, COLORS

SAMPLES = {
    "Simple 1": {"A":{"B":4,"C":2},"B":{"A":4,"C":1,"D":5},"C":{"A":2,"B":1,"D":8},"D":{"B":5,"C":8}},
    "Simple 2": {"S":{"A":6,"B":2},"A":{"S":6,"C":3},"B":{"S":2,"C":1},"C":{"A":3,"B":1,"D":5},"D":{"C":5}},
    "Triangle": {"X":{"Y":3,"Z":5},"Y":{"X":3,"Z":2},"Z":{"X":5,"Y":2}}
}

class DijkstraVisualizer:
    def __init__(self):
        self.ns = "dij"

    def render(self):
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Graph Configuration</h2>', unsafe_allow_html=True)

        mode = st.sidebar.radio("Input mode:", ["Use sample graph", "Build your own"], key=f"{self.ns}_mode")
        if mode == "Use sample graph":
            sample = st.sidebar.selectbox("Select sample:", list(SAMPLES.keys()), key=f"{self.ns}_sample")
            base = SAMPLES[sample]
            V = list(base.keys())
            W = pd.DataFrame(0.0, index=V, columns=V)
            for u, nbrs in base.items():
                for v, w in nbrs.items():
                    W.loc[u, v] = float(w)
                    W.loc[v, u] = float(w)
            gkey = f"sample::{sample}"
        else:
            n = st.sidebar.slider("Number of vertices", 2, 8, 4, key=f"{self.ns}_n")
            V = list(string.ascii_uppercase[:n])
            M = pd.DataFrame(0.0, index=V, columns=V)
            for i, u in enumerate(V):
                for j, v in enumerate(V):
                    if i != j and random.random() > 0.5:
                        w = float(random.randint(1, 9))
                        M.loc[u, v] = w
                        M.loc[v, u] = w
            W = M
            gkey = f"custom::{','.join(V)}"

        src = st.sidebar.selectbox("Source vertex:", V, key=f"{self.ns}_src")
        dst = st.sidebar.selectbox("Destination vertex:", V, key=f"{self.ns}_dst")
        st.sidebar.markdown("---")
        auto = st.sidebar.checkbox("Auto-Play", value=False, key=f"{self.ns}_auto")
        speed = st.sidebar.slider("Speed (seconds per step)", 0.5, 3.0, 1.0, 0.1, key=f"{self.ns}_speed")

        st.markdown('<h2 class="section-header">Weight Matrix</h2>', unsafe_allow_html=True)
        st.dataframe(W.astype(float), use_container_width=True)

        Gtab = {u: {} for u in V}
        for u in V:
            for v in V:
                if u == v:
                    continue
                w = float(W.loc[u, v])
                if w > 0:
                    Gtab[u][v] = w

        def push():
            st.session_state[f"{self.ns}_hist"].append(copy.deepcopy({
                "dist": st.session_state[f"{self.ns}_dist"],
                "prev": st.session_state[f"{self.ns}_prev"],
                "vis": st.session_state[f"{self.ns}_vis"],
                "cur": st.session_state[f"{self.ns}_cur"],
                "exp": st.session_state[f"{self.ns}_exp"],
                "edges": st.session_state[f"{self.ns}_edges"],
                "fin": st.session_state[f"{self.ns}_fin"],
                "step": st.session_state[f"{self.ns}_step"],
            }))

        def restore(s):
            st.session_state[f"{self.ns}_dist"] = copy.deepcopy(s["dist"])
            st.session_state[f"{self.ns}_prev"] = copy.deepcopy(s["prev"])
            st.session_state[f"{self.ns}_vis"] = copy.deepcopy(s["vis"])
            st.session_state[f"{self.ns}_cur"] = s["cur"]
            st.session_state[f"{self.ns}_exp"] = s["exp"]
            st.session_state[f"{self.ns}_edges"] = copy.deepcopy(s["edges"])
            st.session_state[f"{self.ns}_fin"] = s["fin"]
            st.session_state[f"{self.ns}_step"] = s["step"]

        def init_state():
            st.session_state[f"{self.ns}_dist"] = {v: (0 if v == src else math.inf) for v in V}
            st.session_state[f"{self.ns}_prev"] = {v: None for v in V}
            st.session_state[f"{self.ns}_vis"] = {v: False for v in V}
            st.session_state[f"{self.ns}_cur"] = src
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_edges"] = []
            st.session_state[f"{self.ns}_exp"] = f'<div class="step-header">[INITIALIZATION]</div><div class="step-info">Start at {src}. Distance({src}) = 0, others = ∞.</div>'
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_gkey"] = gkey
            st.session_state[f"{self.ns}_src_val"] = src
            st.session_state[f"{self.ns}_dst_val"] = dst
            st.session_state[f"{self.ns}_step"] = 0
            push()

        def step_dijkstra():
            if st.session_state[f"{self.ns}_fin"]:
                return
            dist = st.session_state[f"{self.ns}_dist"]
            vis = st.session_state[f"{self.ns}_vis"]
            prev = st.session_state[f"{self.ns}_prev"]

            unvisited = {k: v for k, v in dist.items() if not vis[k]}
            if not unvisited:
                st.session_state[f"{self.ns}_fin"] = True
                st.session_state[f"{self.ns}_exp"] += '<div class="completed-text">✓ All vertices visited. Done.</div>'
                return

            st.session_state[f"{self.ns}_step"] += 1
            u = min(unvisited, key=unvisited.get)
            st.session_state[f"{self.ns}_cur"] = u
            vis[u] = True

            lines = [f'<div class="step-header">[STEP {st.session_state[f"{self.ns}_step"]}]</div>']
            lines.append(f'<div class="step-info">Pick {u} (smallest distance = {dist[u] if dist[u]!=math.inf else "∞"}). Mark visited.</div>')
            lines.append('<div class="neighbors-header">Relax neighbors:</div>')

            explored = []
            for v, w in Gtab[u].items():
                if vis[v]:
                    lines.append(f'<div class="visited-text">- {v} already visited</div>')
                    continue
                nd = dist[u] + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    explored.append((u, v))
                    lines.append(f'<div class="update-text">- Update {v}: distance = {nd} via {u}</div>')
                else:
                    keep_val = dist[v] if dist[v] != math.inf else "∞"
                    lines.append(f'<div class="keep-text">- Keep {v}: distance = {keep_val}</div>')

            st.session_state[f"{self.ns}_edges"] = explored

            lines.append('<div class="table-header">Current Distances</div>')
            lines.append('<table class="custom-table"><tr><th>Vertex</th><th>Distance</th><th>Visited</th></tr>')
            for x in sorted(V):
                d = dist[x]
                dstr = str(int(d)) if d != math.inf else "∞"
                row_class = "visited-row" if vis[x] else "current-row" if x == u else "unvisited-row"
                lines.append(f'<tr class="{row_class}"><td>{x}</td><td>{dstr}</td><td>{"Yes" if vis[x] else "No"}</td></tr>')
            lines.append('</table>')

            lines.append('<div class="table-header">Previous Nodes</div>')
            lines.append('<table class="custom-table"><tr><th>Vertex</th><th>Previous</th></tr>')
            for x in sorted(V):
                p = prev[x] if prev[x] else "-"
                row_class = "visited-row" if vis[x] else "current-row" if x == u else "unvisited-row"
                lines.append(f'<tr class="{row_class}"><td>{x}</td><td>{p}</td></tr>')
            lines.append('</table>')

            unvisited = {k: v for k, v in dist.items() if not vis[k]}
            if not unvisited:
                st.session_state[f"{self.ns}_fin"] = True
                lines.append('<div class="completed-text">✓ Finished. All nodes processed.</div>')
            else:
                nxt = min(unvisited, key=unvisited.get)
                st.session_state[f"{self.ns}_cur"] = nxt
                lines.append(f'<div class="next-step">Next: {nxt}</div>')

            st.session_state[f"{self.ns}_exp"] = "".join(lines)

        if f"{self.ns}_gkey" not in st.session_state:
            init_state()
        elif st.session_state[f"{self.ns}_gkey"] != gkey or st.session_state[f"{self.ns}_src_val"] != src or st.session_state[f"{self.ns}_dst_val"] != dst:
            init_state()

        st.sidebar.markdown("---")
        c1, c2, c3 = st.sidebar.columns(3)
        nxt = c1.button("Next Step", use_container_width=True, disabled=st.session_state[f"{self.ns}_fin"])
        back = c2.button("Back", use_container_width=True, disabled=len(st.session_state[f"{self.ns}_hist"]) <= 1)
        reset = c3.button("Reset", use_container_width=True)

        if nxt and not st.session_state[f"{self.ns}_fin"]:
            step_dijkstra(); push()
        if back and len(st.session_state[f"{self.ns}_hist"]) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            restore(st.session_state[f"{self.ns}_hist"][-1])
        if reset:
            init_state()

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Step", st.session_state[f"{self.ns}_step"])
        m2.metric("Visited", sum(st.session_state[f"{self.ns}_vis"].values()))
        m3.metric("Remaining", len(V) - sum(st.session_state[f"{self.ns}_vis"].values()))
        m4.metric("Status", "Complete" if st.session_state[f"{self.ns}_fin"] else "Running")

        st.markdown("---")
        cL, cR = st.columns([1.4, 1])
        with cL:
            st.markdown('<h2 class="section-header">Graph Visualization</h2>', unsafe_allow_html=True)
            self.draw_graph(V, W, src, dst)
        with cR:
            st.markdown('<h2 class="section-header">Distance Table</h2>', unsafe_allow_html=True)
            self.display_table(V, src)
            if st.session_state[f"{self.ns}_fin"]:
                self.final_path(dst)

        st.markdown("---")
        st.markdown('<h2 class="section-header">Step-by-Step Explanation</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-card">{st.session_state[f"{self.ns}_exp"]}</div>', unsafe_allow_html=True)

        if st.session_state[f"{self.ns}_fin"]:
            st.success("Dijkstra finished!")

        if auto and not st.session_state[f"{self.ns}_fin"] and not (nxt or back or reset):
            step_dijkstra(); push(); time.sleep(speed); st.rerun()

    def draw_graph(self, V, W, src, dst):
        fig, ax = plt.subplots(figsize=(10, 8))
        G = nx.Graph()
        for u in V:
            for v in V:
                if u < v and float(W.loc[u, v]) > 0:
                    G.add_edge(u, v, weight=float(W.loc[u, v]))
        pos = nx.spring_layout(G, seed=42, k=1.8)

        colors = []
        for v in V:
            if v == src:
                colors.append(COLORS['source'])
            elif v == dst and st.session_state[f"{self.ns}_fin"]:
                colors.append(COLORS['destination'])
            elif st.session_state[f"{self.ns}_vis"][v]:
                colors.append(COLORS['visited'])
            elif v == st.session_state[f"{self.ns}_cur"]:
                colors.append(COLORS['current'])
            else:
                colors.append(COLORS['unvisited'])

        edge_colors = []
        for (u, v) in G.edges():
            if (u, v) in st.session_state[f"{self.ns}_edges"] or (v, u) in st.session_state[f"{self.ns}_edges"]:
                edge_colors.append(GRAPH_LAYOUT_CONFIG['edge_color_highlight'])
            else:
                edge_colors.append(GRAPH_LAYOUT_CONFIG['edge_color_regular'])

        nx.draw(
            G, pos,
            with_labels=True,
            node_color=colors,
            edge_color=edge_colors,
            node_size=GRAPH_LAYOUT_CONFIG['node_size'],
            font_weight="bold",
            ax=ax
        )

        edge_attr = nx.get_edge_attributes(G, "weight")
        label_map = {e: int(w) for e, w in edge_attr.items()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=label_map)

        ax.set_facecolor(COLORS['background'])
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    def display_table(self, V, src):
        df = pd.DataFrame({
            "Vertex": V,
            f"Dist from {src}": [
                str(int(st.session_state[f"{self.ns}_dist"][v])) if st.session_state[f"{self.ns}_dist"][v] != math.inf else "∞"
                for v in V
            ],
            "Prev": [
                st.session_state[f"{self.ns}_prev"][v] if st.session_state[f"{self.ns}_prev"][v] else "-"
                for v in V
            ],
            "Visited": ["Yes" if st.session_state[f"{self.ns}_vis"][v] else "No" for v in V]
        })
        st.dataframe(df, width='stretch', hide_index=True)

    def final_path(self, dst):
        dist = st.session_state[f"{self.ns}_dist"][dst]
        if dist == math.inf:
            st.error("No path exists.")
            return
        path = []
        v = dst
        while v is not None:
            path.insert(0, v)
            v = st.session_state[f"{self.ns}_prev"][v]
        st.markdown(
            f'''<div class="path-result-card"><h3>Shortest Path</h3>
            <p>Path: {' → '.join(path)}</p><p>Total Distance: {int(dist)}</p></div>''',
            unsafe_allow_html=True
        ) 