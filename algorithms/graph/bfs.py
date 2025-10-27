import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import time, copy, random, string, io, os
from matplotlib.backends.backend_pdf import PdfPages
from components.graphStyle import COLORS, GRAPH_LAYOUT_CONFIG

try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
    AG_OK = True
except Exception:
    AG_OK = False

SAMPLES = {
    "Straight Chain": {"A":["B"],"B":["C"],"C":["D"],"D":[]},
    "Simple Branch": {"A":["B","C"],"B":["D"],"C":[],"D":[]},
    "Small Cycle": {"A":["B"],"B":["C"],"C":["A"]},
    "Mini Tree": {"Root":["L1","R1"],"L1":["L2"],"R1":["R2"],"L2":[],"R2":[]},
    "Cross Path": {"P":["Q","R"],"Q":["R"],"R":["S"],"S":[]}
}

class BFSVisualizer:
    def __init__(self):
        self.ns = "bfs"

  
    def _sample_df(self, name):
        base = SAMPLES[name]
        V = list(base.keys())
        W = pd.DataFrame(0, index=V, columns=V, dtype=int)
        for u, neis in base.items():
            for v in neis:
                if u in V and v in V:
                    W.loc[u, v] = 1
                    W.loc[v, u] = 1
        return W

    def _sanitize(self, df):
        df = pd.DataFrame(df).copy()
        cols = [c for c in df.columns if not str(c).startswith("::")]
        df = df.loc[:, cols]
        idx = df.index.astype(str).tolist()
        cols = pd.Index(df.columns).astype(str).tolist()
        V = sorted(set(idx) | set(cols))
        if len(V) == 0:
            return pd.DataFrame(0, index=[], columns=[])
        df.index = pd.Index(df.index).astype(str)
        df.columns = pd.Index(df.columns).astype(str)
        M = df.reindex(index=V, columns=V)
        M = pd.to_numeric(M.stack(), errors="coerce").unstack()
        M = M.replace([np.inf, -np.inf], 0).fillna(0.0)
        M = (M > 0.5).astype(int)
        for i, v in enumerate(V):
            M.iloc[i, i] = 0
        M = ((M + M.T) > 0).astype(int)
        return M

    def _ensure_state(self, V, start_v, gkey):
        tag = f"{self.ns}_inited"
        if (not st.session_state.get(tag)) or st.session_state.get(f"{self.ns}_gkey") != gkey or st.session_state.get(f"{self.ns}_start") != start_v:
            st.session_state[f"{self.ns}_visited"] = {v: False for v in V}
            st.session_state[f"{self.ns}_queue"] = [start_v] if (start_v in V) else (V[:1] if V else [])
            st.session_state[f"{self.ns}_current"] = None
            st.session_state[f"{self.ns}_order"] = []
            st.session_state[f"{self.ns}_edges"] = []
            st.session_state[f"{self.ns}_step"] = 0
            init_queue = st.session_state[f"{self.ns}_queue"]
            queue_txt = f"<span class='vertex'>{init_queue[0]}</span>" if init_queue else "Empty"
            st.session_state[f"{self.ns}_exp"] = f'''<div class="step-content">
<div class="step-header">Initialization</div>
<div class="action">Starting BFS traversal from vertex <span class="vertex">{start_v if start_v else 'N/A'}</span></div>
<div style="margin-top:1rem;color:var(--text-secondary)">
Algorithm: Breadth-First Search explores nodes level by level, visiting all neighbors before moving deeper.
</div>
<div class="queue-display">Queue: {queue_txt}</div>
</div>'''
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_gkey"] = gkey
            st.session_state[f"{self.ns}_start"] = start_v
            st.session_state[tag] = True
            self._push()

    def _push(self):
        h = {
            "visited": copy.deepcopy(st.session_state[f"{self.ns}_visited"]),
            "queue": copy.deepcopy(st.session_state[f"{self.ns}_queue"]),
            "current": st.session_state[f"{self.ns}_current"],
            "order": copy.deepcopy(st.session_state[f"{self.ns}_order"]),
            "edges": copy.deepcopy(st.session_state[f"{self.ns}_edges"]),
            "exp": st.session_state[f"{self.ns}_exp"],
            "fin": st.session_state[f"{self.ns}_fin"],
            "step": st.session_state[f"{self.ns}_step"],
        }
        st.session_state[f"{self.ns}_hist"].append(h)

    def _restore(self, s):
        st.session_state[f"{self.ns}_visited"] = copy.deepcopy(s["visited"])
        st.session_state[f"{self.ns}_queue"] = copy.deepcopy(s["queue"])
        st.session_state[f"{self.ns}_current"] = s["current"]
        st.session_state[f"{self.ns}_order"] = copy.deepcopy(s["order"])
        st.session_state[f"{self.ns}_edges"] = copy.deepcopy(s["edges"])
        st.session_state[f"{self.ns}_exp"] = s["exp"]
        st.session_state[f"{self.ns}_fin"] = s["fin"]
        st.session_state[f"{self.ns}_step"] = s["step"]

    def _graph_from_matrix(self, W):
        V = list(W.index)
        G = {u: [] for u in V}
        for u in V:
            for v in V:
                try:
                    on = (u != v) and (int(W.loc[u, v]) == 1)
                except Exception:
                    on = False
                if on:
                    G[u].append(v)
        return G

    # ---------- One BFS Step ----------
    def _bfs_step(self, G):
        if st.session_state[f"{self.ns}_fin"]:
            return
        st.session_state[f"{self.ns}_step"] += 1

        if not st.session_state[f"{self.ns}_queue"]:
            st.session_state[f"{self.ns}_fin"] = True
            order_str = " → ".join(st.session_state[f"{self.ns}_order"])
            exp = f'''<div class="step-content">
<div class="step-header">Traversal Complete!</div>
<div class="completion">
✓ All reachable vertices have been visited<br>
<strong>Final Order:</strong> {order_str}
</div>
<div class="queue-display">Queue: Empty</div>
</div>'''
            st.session_state[f"{self.ns}_exp"] = exp
            return

        u = st.session_state[f"{self.ns}_queue"].pop(0)
        st.session_state[f"{self.ns}_current"] = u

        exp_parts = [f'<div class="step-content"><div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>']

        if not st.session_state[f"{self.ns}_visited"][u]:
            st.session_state[f"{self.ns}_visited"][u] = True
            st.session_state[f"{self.ns}_order"].append(u)

            exp_parts.append(f'<div class="action">Dequeued vertex <span class="vertex">{u}</span></div>')
            exp_parts.append(f'<div class="action">Marked <span class="vertex">{u}</span> as visited</div>')

            new_edges = []
            neighbors = sorted(G[u])

            if neighbors:
                exp_parts.append('<div style="margin-top:0.75rem">Exploring neighbors:</div>')
                for v in neighbors:
                    if not st.session_state[f"{self.ns}_visited"][v] and v not in st.session_state[f"{self.ns}_queue"]:
                        st.session_state[f"{self.ns}_queue"].append(v)
                        new_edges.append((u, v))
                        exp_parts.append(f'<div class="action">→ Enqueued <span class="vertex">{v}</span></div>')
                    elif st.session_state[f"{self.ns}_visited"][v]:
                        exp_parts.append(f'<div style="color:var(--text-muted);margin-left:1rem">→ <span class="vertex">{v}</span> already visited</div>')
                    else:
                        exp_parts.append(f'<div style="color:var(--text-muted);margin-left:1rem">→ <span class="vertex">{v}</span> already in queue</div>')
            else:
                exp_parts.append('<div style="color:var(--text-muted);margin-top:0.5rem">No neighbors to explore</div>')

            st.session_state[f"{self.ns}_edges"] = new_edges
        else:
            exp_parts.append(f'<div style="color:var(--warning)">Vertex <span class="vertex">{u}</span> was already visited (skipped)</div>')
            st.session_state[f"{self.ns}_edges"] = []

        qtxt = " ← ".join([f"<span class='vertex'>{x}</span>" for x in st.session_state[f"{self.ns}_queue"]]) if st.session_state[f"{self.ns}_queue"] else "Empty"
        exp_parts.append(f'<div class="queue-display">Queue: {qtxt}</div>')
        exp_parts.append('</div>')

        st.session_state[f"{self.ns}_exp"] = "".join(exp_parts)

    # ---------- Tables / Editors ----------
    def _ag_clean(self, original_df, ag_out):
        df_out = pd.DataFrame(ag_out.data if hasattr(ag_out, "data") else ag_out)
        bad = [c for c in df_out.columns if str(c).startswith("::") or c in ("index",)]
        df_out = df_out.drop(columns=bad, errors="ignore")
        df_out = df_out.reindex(columns=list(original_df.columns), fill_value=0)
        df_out.index = list(original_df.index)
        return df_out

    def _ag_matrix(self, df):
        if AG_OK:
            g = GridOptionsBuilder.from_dataframe(df)
            g.configure_default_column(editable=True, resizable=True, suppressMenu=True)
            g.configure_grid_options(
                domLayout="autoHeight",
                suppressMovableColumns=True,
                rowSelection="multiple",
                rowHeight=36,
                enableRangeSelection=True
            )
            ag_out = AgGrid(
                df,
                gridOptions=g.build(),
                theme="streamlit",
                height=300,
                fit_columns_on_grid_load=True,
                update_mode=GridUpdateMode.VALUE_CHANGED,
                data_return_mode=DataReturnMode.AS_INPUT,
                allow_unsafe_jscode=True
            )
            cleaned = self._ag_clean(df, ag_out)
            res = self._sanitize(cleaned)
        else:
            raw = st.data_editor(
                df,
                height=300,
                key=f"{self.ns}_editor",
                use_container_width=True,
                num_rows="dynamic"
            )
            res = self._sanitize(raw)
        return res

    def _state_table(self, V):
        vis = st.session_state[f"{self.ns}_visited"]
        order = st.session_state[f"{self.ns}_order"]
        queue = st.session_state[f"{self.ns}_queue"]
        df = pd.DataFrame({
            "Vertex": V,
            "Visited": ["✓" if vis.get(v, False) else "-" for v in V],
            "Visit Order": [order.index(v) + 1 if v in order else "-" for v in V],
            "In Queue": ["✓" if v in queue else "-" for v in V],
        })
        if AG_OK:
            g = GridOptionsBuilder.from_dataframe(df)
            g.configure_grid_options(domLayout="autoHeight", suppressMovableColumns=True, rowSelection="none", enableSorting=False, rowHeight=34)
            g.configure_default_column(editable=False, resizable=True)
            AgGrid(df, gridOptions=g.build(), theme="streamlit", height=220, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.NO_UPDATE, data_return_mode=DataReturnMode.AS_INPUT)
        else:
            st.dataframe(df, height=220, use_container_width=True)

    def _html_to_plain(self, html_text):
        import re
        text = html_text
        text = re.sub(r'<div class="step-header">([^<]+)</div>', r'\n\1\n' + '='*40 + '\n', text)
        text = re.sub(r'<div class="action">([^<]*(?:<span[^>]*>([^<]+)</span>[^<]*)*)</div>', lambda m: '→ ' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n', text)
        text = re.sub(r'<span class=["\']vertex["\']>([^<]+)</span>', r'[\1]', text)
        text = re.sub(r'<div class="queue-display">([^<]*(?:<span[^>]*>[^<]+</span>[^<]*)*)</div>', lambda m: '\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n', text)
        text = re.sub(r'<div class="completion">([^<]*(?:<[^>]+>[^<]*)*)</div>', lambda m: '\n' + '='*40 + '\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n' + '='*40 + '\n', text)
        text = re.sub(r'<div[^>]*>([^<]*)</div>', r'\1\n', text)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text.strip()

    # ---------- Drawing ----------
    def _draw(self, V, W, start_v):
        if len(V) == 0:
            st.info("No vertices to display")
            return
        fig, ax = plt.subplots(figsize=(7, 4.8))
        fig.patch.set_facecolor(COLORS["background"])
        Gx = nx.Graph()
        for u in V:
            Gx.add_node(u)
        for u in V:
            for v in V:
                try:
                    on = (u < v) and (int(W.loc[u, v]) == 1)
                except Exception:
                    on = False
                if on:
                    Gx.add_edge(u, v)
        pos = nx.spring_layout(Gx, seed=4, k=1.25) if len(Gx) > 1 else {V[0]: (0.5, 0.5)}
        node_colors = []
        for v in Gx.nodes():
            if v == start_v:
                node_colors.append(COLORS["source"])
            elif st.session_state[f"{self.ns}_current"] == v and not st.session_state[f"{self.ns}_fin"]:
                node_colors.append(COLORS["current"])
            elif st.session_state[f"{self.ns}_visited"].get(v, False):
                node_colors.append(COLORS["visited"])
            else:
                node_colors.append(COLORS["unvisited"])
        ec, ew = [], []
        for (u, v) in Gx.edges():
            if (u, v) in st.session_state[f"{self.ns}_edges"] or (v, u) in st.session_state[f"{self.ns}_edges"]:
                ec.append(GRAPH_LAYOUT_CONFIG["edge_color_highlight"])
                ew.append(GRAPH_LAYOUT_CONFIG["edge_width_highlight"])
            else:
                ec.append(GRAPH_LAYOUT_CONFIG["edge_color_regular"])
                ew.append(GRAPH_LAYOUT_CONFIG["edge_width_regular"])
        nx.draw_networkx_nodes(Gx, pos, node_color=node_colors, node_size=GRAPH_LAYOUT_CONFIG["node_size"], edgecolors=GRAPH_LAYOUT_CONFIG["node_border_color"], linewidths=GRAPH_LAYOUT_CONFIG["node_border_width"], ax=ax)
        nx.draw_networkx_labels(Gx, pos, font_size=GRAPH_LAYOUT_CONFIG["font_size"], font_weight=GRAPH_LAYOUT_CONFIG["font_weight"], font_color=GRAPH_LAYOUT_CONFIG["font_color"], ax=ax)
        for i, e in enumerate(Gx.edges()):
            nx.draw_networkx_edges(Gx, pos, [e], edge_color=[ec[i]], width=[ew[i]], ax=ax)
        ax.set_facecolor(COLORS["background"])
        ax.axis("off")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    def _frame_figure(self, V, W, start_v, step_text):
        fig = plt.figure(figsize=(8, 7), layout="constrained")
        fig.patch.set_facecolor(COLORS["background"])
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])
        ax = fig.add_subplot(gs[0])
        Gx = nx.Graph()
        for u in V: Gx.add_node(u)
        for u in V:
            for v in V:
                try:
                    on = (u < v) and (int(W.loc[u, v]) == 1)
                except Exception:
                    on = False
                if on:
                    Gx.add_edge(u, v)
        pos = nx.spring_layout(Gx, seed=4, k=1.25) if len(Gx) > 1 else ({V[0]: (0.5, 0.5)} if V else {})
        node_colors = []
        for v in Gx.nodes():
            if v == start_v:
                node_colors.append(COLORS["source"])
            elif st.session_state[f"{self.ns}_current"] == v and not st.session_state[f"{self.ns}_fin"]:
                node_colors.append(COLORS["current"])
            elif st.session_state[f"{self.ns}_visited"].get(v, False):
                node_colors.append(COLORS["visited"])
            else:
                node_colors.append(COLORS["unvisited"])
        ec, ew = [], []
        for (u, v) in Gx.edges():
            if (u, v) in st.session_state[f"{self.ns}_edges"] or (v, u) in st.session_state[f"{self.ns}_edges"]:
                ec.append(GRAPH_LAYOUT_CONFIG["edge_color_highlight"])
                ew.append(GRAPH_LAYOUT_CONFIG["edge_width_highlight"])
            else:
                ec.append(GRAPH_LAYOUT_CONFIG["edge_color_regular"])
                ew.append(GRAPH_LAYOUT_CONFIG["edge_width_regular"])
        nx.draw_networkx_nodes(Gx, pos, node_color=node_colors, node_size=950, edgecolors="#9aa4d3", linewidths=2, ax=ax)
        nx.draw_networkx_labels(Gx, pos, font_size=13, font_weight="bold", font_color="#eef3ff", ax=ax)
        for i, e in enumerate(Gx.edges()):
            nx.draw_networkx_edges(Gx, pos, [e], edge_color=[ec[i]], width=[ew[i]], ax=ax)
        ax.set_facecolor(COLORS["background"])
        ax.set_xticks([]); ax.set_yticks([])
        ax2 = fig.add_subplot(gs[1])
        ax2.set_facecolor("#0d1220"); ax2.set_xticks([]); ax2.set_yticks([])
        plain_text = self._html_to_plain(step_text)
        ax2.text(0.02, 0.95, "Step-by-step", fontsize=12, color="#9fb3ff", fontweight="bold", va="top")
        ax2.text(0.02, 0.75, plain_text, fontsize=10, color="#e6ecff", va="top", family="monospace", wrap=True, linespacing=1.5)
        return fig

    def _export(self, fmt, fps, V, W, start_v):
        frames = []
        saved = []
        for s in st.session_state[f"{self.ns}_hist"]:
            self._restore(s)
            fig = self._frame_figure(V, W, start_v, s["exp"])
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=140, facecolor=fig.get_facecolor())
            plt.close(fig)
            buf.seek(0)
            frames.append(buf.read())
        outdir = "exports"; os.makedirs(outdir, exist_ok=True)
        if fmt == "PDF":
            path = os.path.join(outdir, "bfs_run.pdf")
            with PdfPages(path) as pdf:
                for s in st.session_state[f"{self.ns}_hist"]:
                    self._restore(s)
                    fig = self._frame_figure(V, W, start_v, s["exp"])
                    pdf.savefig(fig, facecolor=fig.get_facecolor())
                    plt.close(fig)
            saved.append(path)
        elif fmt in ("GIF", "MP4"):
            import imageio.v2 as imageio
            imgs = [imageio.imread(io.BytesIO(b)) for b in frames]
            if fmt == "GIF":
                path = os.path.join(outdir, "bfs_run.gif")
                imageio.mimsave(path, imgs, duration=1 / max(fps, 1))
                saved.append(path)
            else:
                path = os.path.join(outdir, "bfs_run.mp4")
                try:
                    imageio.mimsave(path, imgs, fps=fps, quality=8)
                    saved.append(path)
                except Exception:
                    fallback = os.path.join(outdir, "bfs_run.gif")
                    imageio.mimsave(fallback, imgs, duration=1 / max(fps, 1))
                    saved.append(fallback)
        return saved

    # ---------- UI / Render ----------
    def render(self, *payload, **kwargs):
        s = st.session_state
        src = s.get("sb_src", "Sample graph")
        sample = s.get("sb_sample", "Straight Chain")
        auto = s.get("sb_auto", False)
        speed = s.get("sb_speed", 0.8)
        next_clicked = s.get("sb_next", False)
        back_clicked = s.get("sb_back", False)
        reset_clicked = s.get("sb_reset", False)
        export_clicked = s.get("sb_export", False)

        # --- Source selection ---
        if src == "Sample graph":
            W = self._sample_df(sample)
            hint = f"Sample: {sample}. Edit 0/1 to add or remove edges. Symmetry is enforced."
            # keep a copy so builder widgets have something if user switches later
            s.setdefault(f"{self.ns}_matrix_df", W.copy())
        else:
            # SINGLE SOURCE OF TRUTH for custom graph
            if f"{self.ns}_matrix_df" not in s:
                # init once
                Vnames = list(string.ascii_uppercase[:6])
                base = pd.DataFrame(0, index=Vnames, columns=Vnames, dtype=int)
                s[f"{self.ns}_matrix_df"] = base.copy()
            W = s[f"{self.ns}_matrix_df"].copy()
            hint = "Edit 0/1 to add or remove edges. Use Add/Delete to change vertices. Symmetry is enforced."

        # sanitize & ensure state
        W = self._sanitize(W)
        V = list(W.index)

        # if saved start is invalid after vertex changes → fallback
        if V and s.get(f"{self.ns}_start_sel") not in V:
            s[f"{self.ns}_start_sel"] = V[0]

        sv = s.get(f"{self.ns}_start_sel", V[0] if V else None)
        gkey = f"{src}::{sample or 'custom'}::{','.join(V)}"
        self._ensure_state(V, sv if V else None, gkey)

        col1, col2 = st.columns(2)

        # ---------- left: matrix + builder ----------
        with col1:
            st.markdown('<div class="frame-title">Adjacency Matrix</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frame-hint">{hint}</div>', unsafe_allow_html=True)

            if src != "Sample graph":
                col_add, col_del = st.columns(2)

                # Add vertex
                with col_add:
                    new_vertex = st.text_input("Add vertex", key=f"{self.ns}_add_vertex", placeholder="Enter name")
                    if st.button("Add Vertex", key=f"{self.ns}_btn_add"):
                        nv = (new_vertex or "").strip()
                        if nv and nv not in W.index:
                            V_new = list(W.index) + [nv]
                            W2 = pd.DataFrame(0, index=V_new, columns=V_new, dtype=int)
                            W2.loc[W.index, W.columns] = W
                            s[f"{self.ns}_matrix_df"] = self._sanitize(W2)
                            # reset algo state because vertex set changed
                            s[f"{self.ns}_inited"] = False
                            st.rerun()

                # Delete vertex
                with col_del:
                    if len(list(W.index)) > 1:
                        del_vertex = st.selectbox("Delete vertex", list(W.index), key=f"{self.ns}_del_vertex")
                        if st.button("Delete Vertex", key=f"{self.ns}_btn_del"):
                            if del_vertex in W.index:
                                W2 = W.drop(index=[del_vertex], columns=[del_vertex])
                                s[f"{self.ns}_matrix_df"] = self._sanitize(W2)
                                # fix start if it was deleted
                                if s.get(f"{self.ns}_start_sel") == del_vertex:
                                    left = list(W2.index)
                                    if left:
                                        s[f"{self.ns}_start_sel"] = left[0]
                                s[f"{self.ns}_inited"] = False
                                st.rerun()

            # interactive editor
            W = self._ag_matrix(W)
            W = self._sanitize(W)
            s[f"{self.ns}_matrix_df"] = W.copy()

        # ---------- right: state ----------
        with col2:
            st.markdown('<div class="frame-title">BFS State</div>', unsafe_allow_html=True)
            V = list(W.index)

            # keep start valid
            if V and s.get(f"{self.ns}_start_sel") not in V:
                s[f"{self.ns}_start_sel"] = V[0]

            sv = st.selectbox("Start vertex", V, index=(0 if V else 0),
                               key=f"{self.ns}_start_sel",
                               disabled=(len(V) == 0),
                               label_visibility="collapsed")
            gkey = f"{src}::{sample or 'custom'}::{','.join(V)}"
            self._ensure_state(V, sv if V else None, gkey)

            if V:
                self._state_table(V)
            else:
                st.info("No vertices available")

            visited_count = sum(st.session_state.get(f"{self.ns}_visited", {}).values()) if V else 0
            remaining = (len(V) - visited_count) if V else 0
            status = "Completed" if st.session_state.get(f"{self.ns}_fin", False) else "Running"
            cls = "ok" if status == "Completed" else "run"

            st.markdown(f'''
            <div class="bfs-meta">
                <div class="pill"><div class="h">Step</div><div class="v">{st.session_state.get(f"{self.ns}_step", 0)}</div></div>
                <div class="pill"><div class="h">Visited</div><div class="v">{visited_count}</div></div>
                <div class="pill"><div class="h">Remaining</div><div class="v">{remaining}</div></div>
                <div class="pill"><div class="h">Status</div><div class="v {cls}">{status}</div></div>
            </div>
            ''', unsafe_allow_html=True)

        # ---------- bottom: graph + explanation ----------
        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="frame-title">Graph Visualization</div>', unsafe_allow_html=True)
            self._draw(list(W.index), W, st.session_state.get(f"{self.ns}_start"))
            st.markdown('<div class="legend"><span><i style="background:#7c4dff"></i>Source</span><span><i style="background:#34d399"></i>Visited</span><span><i style="background:#f59e0b"></i>Current</span><span><i style="background:#3a3f55"></i>Unvisited</span></div>', unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="frame-title">Step-by-Step Explanation</div>', unsafe_allow_html=True)
            exp_html = st.session_state.get(f'{self.ns}_exp', '')
            st.markdown(f'<div class="step-explanation">{exp_html}</div>', unsafe_allow_html=True)

        # ---------- controls ----------
        manual = next_clicked or back_clicked or reset_clicked

        if next_clicked and not st.session_state.get(f"{self.ns}_fin", False) and len(W.index) > 0:
            G = self._graph_from_matrix(W)
            self._bfs_step(G)
            self._push()
            st.rerun()

        if back_clicked and len(st.session_state.get(f"{self.ns}_hist", [])) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            self._restore(st.session_state[f"{self.ns}_hist"][-1])
            st.rerun()

        if reset_clicked:
            st.session_state[f"{self.ns}_inited"] = False
            self._ensure_state(list(W.index), st.session_state.get(f"{self.ns}_start_sel"), gkey)
            st.rerun()

        if export_clicked and len(st.session_state.get(f"{self.ns}_hist", [])) > 0 and len(W.index) > 0:
            paths = self._export(st.session_state.get("sb_fmt", "GIF"), max(1, st.session_state.get("sb_fps", 6)), list(W.index), W, st.session_state.get(f"{self.ns}_start"))
            for p in paths:
                with open(p, "rb") as f:
                    st.sidebar.download_button("Download " + p.split("/")[-1], f, file_name=p.split("/")[-1], mime="application/octet-stream")

        if auto and not st.session_state.get(f"{self.ns}_fin", False) and not manual and len(W.index) > 0:
            G = self._graph_from_matrix(W)
            self._bfs_step(G)
            self._push()
            time.sleep(speed)
            st.rerun()