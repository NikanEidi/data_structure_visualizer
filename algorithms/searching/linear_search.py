import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import time, copy, random, io, os, string
from matplotlib.backends.backend_pdf import PdfPages
from components.graphStyle import COLORS, GRAPH_LAYOUT_CONFIG

try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
    AG_OK = True
except Exception:
    AG_OK = False

SAMPLES_A = {
    "Random Small": [4, 1, 7, 3, 9, 2],
    "Sorted": [1, 2, 3, 4, 5, 6],
    "Duplicates": [5, 1, 5, 2, 5, 3],
    "Mixed": [10, -2, 10, 7, 0, 3, 8],
}

class LinearSearchVisualizer:
    def __init__(self):
        self.ns = "linear"

    def _sample_df(self, name):
        arr = SAMPLES_A.get(name, SAMPLES_A["Random Small"])
        return pd.DataFrame({"Value": arr}, dtype=object)

    def _sanitize_array(self, df):
        df = pd.DataFrame(df).copy()
        cols = [c for c in df.columns if not str(c).startswith("::")]
        if "Value" not in cols and len(cols) > 0:
            df = df.rename(columns={cols[0]: "Value"})
        df = df[["Value"]] if "Value" in df.columns else pd.DataFrame({"Value": []})
        df["Value"] = df["Value"].astype(str).fillna("").map(lambda x: x.strip())
        df = df.reset_index(drop=True)
        return df

    def _parse_target(self, s):
        t = s.get(f"{self.ns}_target_raw", "")
        txt = (t if t is not None else "").strip()
        def to_num(x):
            try:
                if "." in x:
                    return float(x)
                return int(x)
            except Exception:
                return None
        num = to_num(txt)
        return num if num is not None else txt

    def _equal(self, a, b):
        def to_num(x):
            try:
                if isinstance(x, str) and "." in x:
                    return float(x)
                return int(x)
            except Exception:
                try:
                    return float(x)
                except Exception:
                    return None
        na, nb = to_num(a), to_num(b)
        if na is not None and nb is not None:
            return (na == nb)
        return str(a).strip().lower() == str(b).strip().lower()

    def _ensure_state(self, A, target, gkey):
        tag = f"{self.ns}_inited"
        if (not st.session_state.get(tag)) or st.session_state.get(f"{self.ns}_gkey") != gkey:
            st.session_state[f"{self.ns}_visited"] = {i: False for i in range(len(A))}
            st.session_state[f"{self.ns}_i"] = 0 if len(A) > 0 else None
            st.session_state[f"{self.ns}_current"] = None
            st.session_state[f"{self.ns}_found_idx"] = None
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_edges"] = []
            st.session_state[f"{self.ns}_fin"] = (len(A) == 0)
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_exp"] = self._exp_init(target, len(A))
            st.session_state[f"{self.ns}_gkey"] = gkey
            st.session_state[tag] = True
            self._push()


    def _code_block(self, stage="check", i=None):
        lines = [
            "for i in range(n):",
            "    if A[i] == target:",
            "        return i",
            "return -1",
        ]
        # خطوط برجسته
        if stage == "found":
            hl_idx = {1, 2}
        elif stage == "done_not_found":
            hl_idx = {3}
        else:
            hl_idx = {0, 1}
        out = []
        for k, L in enumerate(lines):
            mark = "▶ " if k in hl_idx else "  "
            out.append(f"{mark}{L}")
        idx_txt = "" if i is None else f"\ni = {i}"
        return "<pre><code>" + "\n".join(out) + idx_txt + "</code></pre>"

    def _exp_init(self, target, n):
        tshow = str(target) if target != "" else "N/A"
        code = self._code_block(stage="check", i=0 if n>0 else None)
        return f"""<div class="step-content">
<div class="step-header">Initialization</div>
<div class="action">Target = <span class="vertex">{tshow}</span>, n = {n}</div>
<div class="action">Start at index <span class="vertex">0</span></div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""

    def _push(self):
        h = {
            "visited": copy.deepcopy(st.session_state[f"{self.ns}_visited"]),
            "i": st.session_state[f"{self.ns}_i"],
            "current": st.session_state[f"{self.ns}_current"],
            "found_idx": st.session_state[f"{self.ns}_found_idx"],
            "exp": st.session_state[f"{self.ns}_exp"],
            "fin": st.session_state[f"{self.ns}_fin"],
            "step": st.session_state[f"{self.ns}_step"],
            "edges": copy.deepcopy(st.session_state[f"{self.ns}_edges"]),
        }
        st.session_state[f"{self.ns}_hist"].append(h)

    def _restore(self, s):
        st.session_state[f"{self.ns}_visited"] = copy.deepcopy(s["visited"])
        st.session_state[f"{self.ns}_i"] = s["i"]
        st.session_state[f"{self.ns}_current"] = s["current"]
        st.session_state[f"{self.ns}_found_idx"] = s["found_idx"]
        st.session_state[f"{self.ns}_exp"] = s["exp"]
        st.session_state[f"{self.ns}_fin"] = s["fin"]
        st.session_state[f"{self.ns}_step"] = s["step"]
        st.session_state[f"{self.ns}_edges"] = copy.deepcopy(s["edges"])

    def _linear_step(self, A, target):
        if st.session_state[f"{self.ns}_fin"]:
            return
        i = st.session_state[f"{self.ns}_i"]
        st.session_state[f"{self.ns}_step"] += 1
        if i is None or i >= len(A):
            st.session_state[f"{self.ns}_fin"] = True
            code = self._code_block(stage="done_not_found", i=None)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="completion">Reached end of array, target not found.</div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""
            return
        st.session_state[f"{self.ns}_current"] = i
        val = A[i]
        st.session_state[f"{self.ns}_visited"][i] = True
        eq = self._equal(val, target)
        if eq:
            st.session_state[f"{self.ns}_found_idx"] = i
            st.session_state[f"{self.ns}_fin"] = True
            code = self._code_block(stage="found", i=i)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">Compare A[{i}] = <span class="vertex">{val}</span> with target ⇒ match ✓</div>
<div class="completion">Return index <span class="vertex">{i}</span></div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""
        else:
            nxt = i + 1
            st.session_state[f"{self.ns}_i"] = nxt
            code = self._code_block(stage="check", i=nxt if nxt < len(A) else None)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">Compare A[{i}] = <span class="vertex">{val}</span> with target ⇒ not equal</div>
<div class="action">Move to next index: <span class="vertex">{nxt}</span></div>
<div class="queue-display">Checked: {" , ".join([str(k) for k,v in st.session_state[f"{self.ns}_visited"].items() if v])}</div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""

    def _ag_clean(self, original_df, ag_out):
        df_out = pd.DataFrame(ag_out.data if hasattr(ag_out, "data") else ag_out)
        bad = [c for c in df_out.columns if str(c).startswith("::") or c in ("index",)]
        df_out = df_out.drop(columns=bad, errors="ignore")
        if "Value" not in df_out.columns and len(df_out.columns)>0:
            df_out = df_out.rename(columns={df_out.columns[0]:"Value"})
        df_out = df_out.reindex(columns=["Value"], fill_value="")
        df_out.index = list(original_df.index)
        return df_out

    def _ag_array(self, df):
        if AG_OK:
            g = GridOptionsBuilder.from_dataframe(df)
            g.configure_default_column(editable=True, resizable=True, suppressMenu=True)
            g.configure_grid_options(domLayout="autoHeight", suppressMovableColumns=True, rowSelection="multiple", rowHeight=36, enableRangeSelection=True)
            ag_out = AgGrid(df, gridOptions=g.build(), theme="streamlit", height=260, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.VALUE_CHANGED, data_return_mode=DataReturnMode.AS_INPUT, allow_unsafe_jscode=True)
            cleaned = self._ag_clean(df, ag_out)
            res = self._sanitize_array(cleaned)
        else:
            raw = st.data_editor(df, height=260, key=f"{self.ns}_editor", use_container_width=True, num_rows="dynamic")
            res = self._sanitize_array(raw)
        return res

    def _state_table(self, A):
        vis = st.session_state[f"{self.ns}_visited"]
        cur = st.session_state[f"{self.ns}_current"]
        found = st.session_state[f"{self.ns}_found_idx"]
        idxs = list(range(len(A)))
        df = pd.DataFrame({
            "Index": idxs,
            "Value": [A[i] for i in idxs],
            "Visited": ["✓" if vis.get(i, False) else "-" for i in idxs],
            "Current": ["✓" if i == cur and not st.session_state[f"{self.ns}_fin"] else "-" for i in idxs],
            "Found": ["✓" if i == found else "-" for i in idxs],
        })
        if AG_OK:
            g = GridOptionsBuilder.from_dataframe(df)
            g.configure_grid_options(domLayout="autoHeight", suppressMovableColumns=True, rowSelection="none", enableSorting=False, rowHeight=34)
            g.configure_default_column(editable=False, resizable=True)
            AgGrid(df, gridOptions=g.build(), theme="streamlit", height=260, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.NO_UPDATE, data_return_mode=DataReturnMode.AS_INPUT)
        else:
            st.dataframe(df, height=260, use_container_width=True)

    def _html_to_plain(self, html_text):
        import re
        text = html_text
        text = re.sub(r'<div class="step-header">([^<]+)</div>', r'\n\1\n' + '='*40 + '\n', text)
        text = re.sub(r'<div class="action">([^<]*(?:<span[^>]*>([^<]+)</span>[^<]*)*)</div>', lambda m: '→ ' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n', text)
        text = re.sub(r'<span class=["\']vertex["\']>([^<]+)</span>', r'[\1]', text)
        text = re.sub(r'<div class="queue-display">([^<]*(?:<span[^>]*>[^<]+</span>[^<]*)*)</div>', lambda m: '\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n', text)
        text = re.sub(r'<div class="completion">([^<]*(?:<[^>]+>[^<]*)*)</div>', lambda m: '\n' + '='*40 + '\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n' + '='*40 + '\n', text)
        # کدِ بدون span: تبدیل ساده‌ی محتوا
        text = re.sub(r'<pre[^>]*><code>(.*?)</code></pre>', lambda m: "\n" + re.sub(r'<[^>]+>', '', m.group(1)) + "\n", text, flags=re.DOTALL)
        text = re.sub(r'<div[^>]*>([^<]*)</div>', r'\1\n', text)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text.strip()

    def _draw(self, A, target):
        n = len(A)
        if n == 0:
            st.info("No elements to display")
            return
        fig, ax = plt.subplots(figsize=(max(7, min(12, 1.1*n + 2)), 4.6))
        fig.patch.set_facecolor(COLORS["background"])
        ax.set_facecolor(COLORS["background"])
        cur = st.session_state[f"{self.ns}_current"]
        visited = st.session_state[f"{self.ns}_visited"]
        found = st.session_state[f"{self.ns}_found_idx"]
        pad = 0.2
        for i, val in enumerate(A):
            x = i + pad
            y = 1.4
            w = 0.85
            h = 1.2
            if i == found:
                fc = COLORS["source"]
            elif i == cur and not st.session_state[f"{self.ns}_fin"]:
                fc = COLORS["current"]
            elif visited.get(i, False):
                fc = COLORS["visited"]
            else:
                fc = COLORS["unvisited"]
            rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.06", linewidth=2, edgecolor=GRAPH_LAYOUT_CONFIG["node_border_color"], facecolor=fc)
            ax.add_patch(rect)
            ax.text(x + w/2, y + h/2 + 0.18, str(val), ha="center", va="center", fontsize=GRAPH_LAYOUT_CONFIG["font_size"], color=GRAPH_LAYOUT_CONFIG["font_color"], fontweight=GRAPH_LAYOUT_CONFIG["font_weight"])
            ax.text(x + w/2, y - 0.05, f"{i}", ha="center", va="top", fontsize=10, color="#9fb3ff")
        ttxt = str(target) if target!="" else "N/A"
        ax.text(0.02, 0.35, f"target = {ttxt}", fontsize=12, color="#9fb3ff", transform=ax.transAxes, fontweight="bold")
        ax.set_xlim(0, n + 1.2)
        ax.set_ylim(0.8, 3.1)
        ax.axis("off")
        st.pyplot(fig)
        plt.close(fig)

    def _frame_figure(self, A, target, step_text):
        fig = plt.figure(figsize=(10, 7.2), layout="constrained")
        fig.patch.set_facecolor(COLORS["background"])
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])
        ax = fig.add_subplot(gs[0])
        n = len(A)
        ax.set_facecolor(COLORS["background"])
        cur = st.session_state[f"{self.ns}_current"]
        visited = st.session_state[f"{self.ns}_visited"]
        found = st.session_state[f"{self.ns}_found_idx"]
        pad = 0.2
        for i, val in enumerate(A):
            x = i + pad
            y = 1.4
            w = 0.85
            h = 1.2
            if i == found:
                fc = COLORS["source"]
            elif i == cur and not st.session_state[f"{self.ns}_fin"]:
                fc = COLORS["current"]
            elif visited.get(i, False):
                fc = COLORS["visited"]
            else:
                fc = COLORS["unvisited"]
            rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.06", linewidth=2, edgecolor="#9aa4d3", facecolor=fc)
            ax.add_patch(rect)
            ax.text(x + w/2, y + h/2 + 0.18, str(val), ha="center", va="center", fontsize=12, color="#eef3ff", fontweight="bold")
            ax.text(x + w/2, y - 0.05, f"{i}", ha="center", va="top", fontsize=10, color="#9fb3ff")
        ttxt = str(target) if target!="" else "N/A"
        ax.text(0.02, 0.35, f"target = {ttxt}", fontsize=12, color="#9fb3ff", transform=ax.transAxes, fontweight="bold")
        ax.set_xlim(0, n + 1.2); ax.set_ylim(0.8, 3.1); ax.set_xticks([]); ax.set_yticks([])
        ax2 = fig.add_subplot(gs[1])
        ax2.set_facecolor("#0d1220"); ax2.set_xticks([]); ax2.set_yticks([])
        plain_text = self._html_to_plain(step_text)
        ax2.text(0.02, 0.95, "Step-by-step", fontsize=12, color="#9fb3ff", fontweight="bold", va="top")
        ax2.text(0.02, 0.75, plain_text, fontsize=10, color="#e6ecff", va="top", family="monospace", wrap=True, linespacing=1.5)
        return fig

    def _export(self, fmt, fps, A, target):
        frames = []
        saved = []
        for s in st.session_state[f"{self.ns}_hist"]:
            self._restore(s)
            fig = self._frame_figure(A, target, s["exp"])
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=140, facecolor=fig.get_facecolor())
            plt.close(fig)
            buf.seek(0)
            frames.append(buf.read())
        outdir = "exports"; os.makedirs(outdir, exist_ok=True)
        if fmt == "PDF":
            path = os.path.join(outdir, f"{self.ns}_run.pdf")
            with PdfPages(path) as pdf:
                for s in st.session_state[f"{self.ns}_hist"]:
                    self._restore(s)
                    fig = self._frame_figure(A, target, s["exp"])
                    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)
            saved.append(path)
        elif fmt in ("GIF", "MP4"):
            import imageio.v2 as imageio
            imgs = [imageio.imread(io.BytesIO(b)) for b in frames]
            if fmt == "GIF":
                path = os.path.join(outdir, f"{self.ns}_run.gif")
                imageio.mimsave(path, imgs, duration=1 / max(fps, 1)); saved.append(path)
            else:
                path = os.path.join(outdir, f"{self.ns}_run.mp4")
                try:
                    imageio.mimsave(path, imgs, fps=fps, quality=8); saved.append(path)
                except Exception:
                    fallback = os.path.join(outdir, f"{self.ns}_run.gif")
                    imageio.mimsave(fallback, imgs, duration=1 / max(fps, 1)); saved.append(fallback)
        return saved

    def render(self, *payload, **kwargs):
        s = st.session_state
        src = s.get("sb_src", "Sample graph")
        sample = s.get("sb_sample", "Random Small")
        auto = s.get("sb_auto", False)
        speed = s.get("sb_speed", 0.8)
        next_clicked = s.get("sb_next", False)
        back_clicked = s.get("sb_back", False)
        reset_clicked = s.get("sb_reset", False)
        export_clicked = s.get("sb_export", False)

        if src == "Sample graph":
            DF = self._sample_df(sample if sample in SAMPLES_A else "Random Small")
            s.setdefault(f"{self.ns}_array_df", DF.copy())
            hint = f"Sample: {sample if sample in SAMPLES_A else 'Random Small'}. Edit values freely."
        else:
            if f"{self.ns}_array_df" not in s:
                base = pd.DataFrame({"Value": list(range(1,7))}, dtype=object)
                s[f"{self.ns}_array_df"] = base.copy()
            DF = s[f"{self.ns}_array_df"].copy()
            hint = "Edit values. Use Add/Delete to change elements."

        DF = self._sanitize_array(DF)
        A = DF["Value"].tolist()

       
        if f"{self.ns}_target_raw" not in s:
            s[f"{self.ns}_target_raw"] = (str(A[-1]) if A else "")
        target = self._parse_target(s)
        gkey = f"{src}::{sample or 'custom'}::A={','.join(map(str,A))}::t={target}"
        self._ensure_state(A, target, gkey)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="frame-title">Array Values</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frame-hint">{hint}</div>', unsafe_allow_html=True)
            if src != "Sample graph":
                col_add, col_del = st.columns(2)
                with col_add:
                    new_val = st.text_input("Add item", key=f"{self.ns}_add_item", placeholder="e.g. 42 or hello")
                    if st.button("Add", key=f"{self.ns}_btn_add"):
                        nv = (new_val or "").strip()
                        if nv != "":
                            DF2 = DF.copy()
                            DF2.loc[len(DF2)] = [nv]
                            s[f"{self.ns}_array_df"] = self._sanitize_array(DF2)
                            s[f"{self.ns}_inited"] = False
                            st.rerun()
                with col_del:
                    if len(DF) > 0:
                        del_idx = st.number_input("Delete index", min_value=0, max_value=max(0, len(DF)-1), step=1, value=0, key=f"{self.ns}_del_idx")
                        if st.button("Delete", key=f"{self.ns}_btn_del"):
                            if 0 <= del_idx < len(DF):
                                DF2 = DF.drop(index=[del_idx]).reset_index(drop=True)
                                s[f"{self.ns}_array_df"] = self._sanitize_array(DF2)
                                s[f"{self.ns}_inited"] = False
                                st.rerun()
            DF = self._ag_array(DF)
            DF = self._sanitize_array(DF)
            s[f"{self.ns}_array_df"] = DF.copy()
            A = DF["Value"].tolist()

        with col2:
            st.markdown('<div class="frame-title">Linear Search State</div>', unsafe_allow_html=True)
            _ = st.text_input("Target value", key=f"{self.ns}_target_raw")  
            target = self._parse_target(s)
            gkey = f"{src}::{sample or 'custom'}::A={','.join(map(str,A))}::t={target}"
            self._ensure_state(A, target, gkey)
            self._state_table(A)
            visited_count = sum(st.session_state.get(f"{self.ns}_visited", {}).values()) if A else 0
            remaining = (len(A) - visited_count) if A else 0
            status = "Completed" if st.session_state.get(f"{self.ns}_fin", False) else "Running"
            cls = "ok" if status == "Completed" else "run"
            st.markdown(f'''
            <div class="bfs-meta">
                <div class="pill"><div class="h">Step</div><div class="v">{st.session_state.get(f"{self.ns}_step", 0)}</div></div>
                <div class="pill"><div class="h">Checked</div><div class="v">{visited_count}</div></div>
                <div class="pill"><div class="h">Remaining</div><div class="v">{remaining}</div></div>
                <div class="pill"><div class="h">Status</div><div class="v {cls}">{status}</div></div>
            </div>
            ''', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="frame-title">Visualization</div>', unsafe_allow_html=True)
            self._draw(A, target)
            st.markdown('<div class="legend"><span><i style="background:#7c4dff"></i>Found</span><span><i style="background:#f59e0b"></i>Current</span><span><i style="background:#34d399"></i>Visited</span><span><i style="background:#3a3f55"></i>Unvisited</span></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="frame-title">Step-by-Step Explanation</div>', unsafe_allow_html=True)
            exp_html = st.session_state.get(f'{self.ns}_exp', '')
            st.markdown(f'<div class="step-explanation">{exp_html}</div>', unsafe_allow_html=True)

     
        next_clicked = s.get("sb_next", False)
        back_clicked = s.get("sb_back", False)
        reset_clicked = s.get("sb_reset", False)
        export_clicked = s.get("sb_export", False)
        auto = s.get("sb_auto", False)
        speed = s.get("sb_speed", 0.8)

        manual = next_clicked or back_clicked or reset_clicked
        if next_clicked and not st.session_state.get(f"{self.ns}_fin", False) and len(A) > 0:
            self._linear_step(A, target)
            self._push()
            st.rerun()
        if back_clicked and len(st.session_state.get(f"{self.ns}_hist", [])) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            self._restore(st.session_state[f"{self.ns}_hist"][-1])
            st.rerun()
        if reset_clicked:
            st.session_state[f"{self.ns}_inited"] = False
            self._ensure_state(A, target, gkey)
            st.rerun()
        if export_clicked and len(st.session_state.get(f"{self.ns}_hist", [])) > 0 and len(A) > 0:
            paths = self._export(s.get("sb_fmt", "GIF"), max(1, s.get("sb_fps", 6)), A, target)
            for p in paths:
                with open(p, "rb") as f:
                    st.sidebar.download_button("Download " + p.split("/")[-1], f, file_name=p.split("/")[-1], mime="application/octet-stream")
        if auto and not st.session_state.get(f"{self.ns}_fin", False) and not manual and len(A) > 0:
            self._linear_step(A, target)
            self._push()
            time.sleep(speed)
            st.rerun()