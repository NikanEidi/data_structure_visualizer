import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time, copy, io, os, html
from matplotlib.backends.backend_pdf import PdfPages
from components.graphStyle import COLORS, GRAPH_LAYOUT_CONFIG

try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
    AG_OK = True
except Exception:
    AG_OK = False

SAMPLES_A = {
    "Random Small": [4, 1, 7, 3, 9, 2],
    "Nearly Sorted": [1, 2, 3, 5, 4, 6, 7],
    "Reverse": [9, 7, 5, 4, 3, 2, 1],
    "Duplicates": [5, 1, 5, 2, 5, 3],
}

class BubbleSortVisualizer:
    def __init__(self):
        self.ns = "bubble"

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

    def _to_num_or_str(self, x):
        try:
            if isinstance(x, str) and "." in x:
                return float(x)
            return int(x)
        except Exception:
            try:
                return float(x)
            except Exception:
                return str(x)

    def _cmp(self, a, b):
        aa = self._to_num_or_str(a)
        bb = self._to_num_or_str(b)
        if isinstance(aa, (int, float)) and isinstance(bb, (int, float)):
            return -1 if aa < bb else (1 if aa > bb else 0)
        sa, sb = str(aa), str(bb)
        return -1 if sa < sb else (1 if sa > sb else 0)

    def _code_block(self, stage="compare", i=None, j=None, swapped=False):
        lines = [
            "for i in range(n - 1):",
            "    swapped = False",
            "    for j in range(0, n - 1 - i):",
            "        if A[j] > A[j + 1]:",
            "            A[j], A[j + 1] = A[j + 1], A[j]",
            "            swapped = True",
            "    if not swapped: break",
        ]
        if stage == "start":
            hi = {0,1}
        elif stage == "compare":
            hi = {2,3}
        elif stage == "swap":
            hi = {3,4,5}
        elif stage == "end_pass":
            hi = {6}
        elif stage == "done":
            hi = {6}
        else:
            hi = set()
        out = []
        for k, L in enumerate(lines):
            esc = html.escape(L)
            if k in hi:
                line = f"▶ <span style='background:#1f2a4a;border-radius:4px;padding:0 4px'>{esc}</span>"
            else:
                line = f"&nbsp; {esc}"
            out.append(line)
        ex = []
        if i is not None: ex.append(f"i = {i}")
        if j is not None: ex.append(f"j = {j}")
        if swapped: ex.append("swapped = True")
        info = "" if not ex else f"<div style='margin-top:0.25rem;color:#9fb3ff'>{' , '.join(ex)}</div>"
        return "<pre style='margin:0;white-space:pre-wrap'><code>" + "\n".join(out) + "</code></pre>" + info

    def _exp_init(self, A):
        n = len(A)
        code = self._code_block(stage="start", i=0, j=0)
        return f"""<div class="step-content">
<div class="step-header">Initialization</div>
<div class="action">n = <span class="vertex">{n}</span>, start from i = <span class="vertex">0</span>, j = <span class="vertex">0</span></div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""

    def _push(self):
        h = {
            "A": copy.deepcopy(st.session_state[f"{self.ns}_A"]),
            "i": st.session_state[f"{self.ns}_i"],
            "j": st.session_state[f"{self.ns}_j"],
            "swapped": st.session_state[f"{self.ns}_swapped"],
            "fin": st.session_state[f"{self.ns}_fin"],
            "step": st.session_state[f"{self.ns}_step"],
            "exp": st.session_state[f"{self.ns}_exp"],
            "pair": st.session_state[f"{self.ns}_pair"],
        }
        st.session_state[f"{self.ns}_hist"].append(h)

    def _restore(self, s):
        st.session_state[f"{self.ns}_A"] = copy.deepcopy(s["A"])
        st.session_state[f"{self.ns}_i"] = s["i"]
        st.session_state[f"{self.ns}_j"] = s["j"]
        st.session_state[f"{self.ns}_swapped"] = s["swapped"]
        st.session_state[f"{self.ns}_fin"] = s["fin"]
        st.session_state[f"{self.ns}_step"] = s["step"]
        st.session_state[f"{self.ns}_exp"] = s["exp"]
        st.session_state[f"{self.ns}_pair"] = s["pair"]
        st.session_state[f"{self.ns}_array_df"] = pd.DataFrame({"Value": st.session_state[f"{self.ns}_A"]}, dtype=object)

    def _ensure_state(self, A, gkey):
        tag = f"{self.ns}_inited"
        if (not st.session_state.get(tag)) or st.session_state.get(f"{self.ns}_gkey") != gkey:
            st.session_state[f"{self.ns}_A"] = list(A)
            st.session_state[f"{self.ns}_i"] = 0 if len(A) > 1 else None
            st.session_state[f"{self.ns}_j"] = 0 if len(A) > 1 else None
            st.session_state[f"{self.ns}_swapped"] = False
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_fin"] = (len(A) <= 1)
            st.session_state[f"{self.ns}_pair"] = (-1, -1)
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_exp"] = self._exp_init(A)
            st.session_state[f"{self.ns}_gkey"] = gkey
            st.session_state[tag] = True
            self._push()

    def _bubble_step(self):
        if st.session_state[f"{self.ns}_fin"]:
            return
        A = st.session_state[f"{self.ns}_A"]
        n = len(A)
        i = st.session_state[f"{self.ns}_i"]
        j = st.session_state[f"{self.ns}_j"]
        swapped = st.session_state[f"{self.ns}_swapped"]
        st.session_state[f"{self.ns}_step"] += 1

        if i is None or j is None or i >= n - 1:
            st.session_state[f"{self.ns}_fin"] = True
            code = self._code_block(stage="done", i=i, j=j, swapped=swapped)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="completion">Sorted!</div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
            return

        if j > n - 2 - i:
            if not swapped:
                st.session_state[f"{self.ns}_fin"] = True
                code = self._code_block(stage="end_pass", i=i, j=j, swapped=False)
                st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="completion">No swap in pass i={i} ⇒ array already sorted (early break)</div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
                return
            st.session_state[f"{self.ns}_i"] = i + 1
            st.session_state[f"{self.ns}_j"] = 0
            st.session_state[f"{self.ns}_swapped"] = False
            code = self._code_block(stage="end_pass", i=i+1, j=0, swapped=False)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">End of pass i={i}. Largest element fixed at index {n-1-i}.</div>
<div class="action">Next pass ⇒ i ← <span class="vertex">{i+1}</span>, j ← <span class="vertex">0</span></div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
            return

        st.session_state[f"{self.ns}_pair"] = (j, j+1)
        v1, v2 = A[j], A[j+1]
        if self._cmp(v1, v2) > 0:
            A[j], A[j+1] = A[j+1], A[j]
            st.session_state[f"{self.ns}_swapped"] = True
            st.session_state[f"{self.ns}_array_df"] = pd.DataFrame({"Value": A}, dtype=object)
            code = self._code_block(stage="swap", i=i, j=j, swapped=True)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">Compare A[{j}]={v1} and A[{j+1}]={v2} ⇒ out of order ⇒ swap</div>
<div class="action">A[{j}] ↔ A[{j+1}]</div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
        else:
            code = self._code_block(stage="compare", i=i, j=j, swapped=st.session_state[f"{self.ns}_swapped"])
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">Compare A[{j}]={v1} and A[{j+1}]={v2} ⇒ OK (no swap)</div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""

        st.session_state[f"{self.ns}_j"] = j + 1

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
        i = st.session_state[f"{self.ns}_i"]
        j = st.session_state[f"{self.ns}_j"]
        cur_j, cur_k = st.session_state[f"{self.ns}_pair"]
        idxs = list(range(len(A)))
        df = pd.DataFrame({
            "Index": idxs,
            "Value": [A[i] for i in idxs],
            "Compared": ["✓" if (i==cur_j or i==cur_k) and not st.session_state[f"{self.ns}_fin"] else "-" for i in idxs],
            "Sorted (suffix)": ["✓" if i >= len(A)-max(i or 0,0) else "-" for i in idxs],
        })
        if AG_OK:
            g = GridOptionsBuilder.from_dataframe(df)
            g.configure_grid_options(domLayout="autoHeight", suppressMovableColumns=True, rowSelection="none", enableSorting=False, rowHeight=34)
            g.configure_default_column(editable=False, resizable=True)
            AgGrid(df, gridOptions=g.build(), theme="streamlit", height=260, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.NO_UPDATE, data_return_mode=DataReturnMode.AS_INPUT)
        else:
            st.dataframe(df, height=260, use_container_width=True)
        status = "Completed" if st.session_state.get(f"{self.ns}_fin", False) else "Running"
        cls = "ok" if status == "Completed" else "run"
        st.markdown(f"""<div class="bfs-meta">
            <div class="pill"><div class="h">Step</div><div class="v">{st.session_state.get(f"{self.ns}_step",0)}</div></div>
            <div class="pill"><div class="h">Pass i</div><div class="v">{i if i is not None else "-"}</div></div>
            <div class="pill"><div class="h">j</div><div class="v">{j if j is not None else "-"}</div></div>
            <div class="pill"><div class="h">Status</div><div class="v {cls}">{status}</div></div>
        </div>""", unsafe_allow_html=True)

    def _html_to_plain(self, html_text):
        import re
        text = html_text
        text = re.sub(r'<div class="step-header">([^<]+)</div>', r'\n\1\n' + '='*40 + '\n', text)
        text = re.sub(r'<div class="action">([^<]*(?:<span[^>]*>([^<]+)</span>[^<]*)*)</div>', lambda m: '→ ' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n', text)
        text = re.sub(r'<span class=["\']vertex["\']>([^<]+)</span>', r'[\1]', text)
        text = re.sub(r'<div class="queue-display">([^<]*(?:<span[^>]*>[^<]+</span>[^<]*)*)</div>', lambda m: '\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n', text)
        text = re.sub(r'<div class="completion">([^<]*(?:<[^>]+>[^<]*)*)</div>', lambda m: '\n' + '='*40 + '\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n' + '='*40 + '\n', text)
        text = re.sub(r'<pre[^>]*><code>(.*?)</code></pre>', lambda m: "\n" + html.unescape(re.sub(r'<[^>]+>', '', m.group(1))) + "\n", text, flags=re.DOTALL)
        text = re.sub(r'<div[^>]*>([^<]*)</div>', r'\1\n', text)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text.strip()

    def _draw(self, A):
        n = len(A)
        if n == 0:
            st.info("No elements to display")
            return
        fig, ax = plt.subplots(figsize=(max(7, min(12, 1.1*n + 2)), 4.8))
        fig.patch.set_facecolor(COLORS["background"])
        ax.set_facecolor(COLORS["background"])
        i = st.session_state[f"{self.ns}_i"] or 0
        cur_j, cur_k = st.session_state[f"{self.ns}_pair"]
        pad = 0.2
        for idx, val in enumerate(A):
            x = idx + pad; y = 1.4; w = 0.85; h = 1.2
            if st.session_state[f"{self.ns}_fin"] and idx >= n - i:
                fc = COLORS["visited"]
            elif idx >= n - i and i is not None:
                fc = COLORS["visited"]
            elif idx == cur_j or idx == cur_k:
                fc = COLORS["current"]
            else:
                fc = COLORS["unvisited"]
            rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.06",
                                          linewidth=2, edgecolor=GRAPH_LAYOUT_CONFIG["node_border_color"], facecolor=fc)
            ax.add_patch(rect)
            ax.text(x + w/2, y + h/2 + 0.18, str(val), ha="center", va="center",
                    fontsize=GRAPH_LAYOUT_CONFIG["font_size"], color=GRAPH_LAYOUT_CONFIG["font_color"],
                    fontweight=GRAPH_LAYOUT_CONFIG["font_weight"])
            ax.text(x + w/2, y - 0.05, f"{idx}", ha="center", va="top", fontsize=10, color="#9fb3ff")
        ax.set_xlim(0, n + 1.2); ax.set_ylim(0.8, 3.2); ax.axis("off")
        st.pyplot(fig); plt.close(fig)

    def _frame_figure(self, A, step_text):
        fig = plt.figure(figsize=(10, 7.2), layout="constrained")
        fig.patch.set_facecolor(COLORS["background"])
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])
        ax = fig.add_subplot(gs[0])
        n = len(A)
        ax.set_facecolor(COLORS["background"])
        i = st.session_state[f"{self.ns}_i"] or 0
        cur_j, cur_k = st.session_state[f"{self.ns}_pair"]
        pad = 0.2
        for idx, val in enumerate(A):
            x = idx + pad; y = 1.4; w = 0.85; h = 1.2
            if st.session_state[f"{self.ns}_fin"] and idx >= n - i:
                fc = COLORS["visited"]
            elif idx >= n - i and i is not None:
                fc = COLORS["visited"]
            elif idx == cur_j or idx == cur_k:
                fc = COLORS["current"]
            else:
                fc = COLORS["unvisited"]
            rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.06",
                                          linewidth=2, edgecolor="#9aa4d3", facecolor=fc)
            ax.add_patch(rect)
            ax.text(x + w/2, y + h/2 + 0.18, str(val), ha="center", va="center",
                    fontsize=12, color="#eef3ff", fontweight="bold")
            ax.text(x + w/2, y - 0.05, f"{idx}", ha="center", va="top", fontsize=10, color="#9fb3ff")
        ax.set_xlim(0, n + 1.2); ax.set_ylim(0.8, 3.2); ax.set_xticks([]); ax.set_yticks([])

        ax2 = fig.add_subplot(gs[1])
        ax2.set_facecolor("#0d1220"); ax2.set_xticks([]); ax2.set_yticks([])
        plain_text = self._html_to_plain(step_text)
        ax2.text(0.02, 0.95, "Step-by-step", fontsize=12, color="#9fb3ff", fontweight="bold", va="top")
        ax2.text(0.02, 0.75, plain_text, fontsize=10, color="#e6ecff", va="top", family="monospace", wrap=True, linespacing=1.5)
        return fig

    def _export(self, fmt, fps, A):
        frames = []; saved = []
        for s in st.session_state[f"{self.ns}_hist"]:
            self._restore(s)
            fig = self._frame_figure(st.session_state[f"{self.ns}_A"], s["exp"])
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=140, facecolor=fig.get_facecolor())
            plt.close(fig)
            buf.seek(0); frames.append(buf.read())
        outdir = "exports"; os.makedirs(outdir, exist_ok=True)
        if fmt == "PDF":
            path = os.path.join(outdir, f"{self.ns}_run.pdf")
            with PdfPages(path) as pdf:
                for s in st.session_state[f"{self.ns}_hist"]:
                    self._restore(s)
                    fig = self._frame_figure(st.session_state[f"{self.ns}_A"], s["exp"])
                    pdf.savefig(fig, facecolor=fig.get_facecolor()); plt.close(fig)
            saved.append(path)
        elif fmt in ("GIF","MP4"):
            import imageio.v2 as imageio
            imgs = [imageio.imread(io.BytesIO(b)) for b in frames]
            if fmt == "GIF":
                path = os.path.join(outdir, f"{self.ns}_run.gif")
                imageio.mimsave(path, imgs, duration=1/max(fps,1)); saved.append(path)
            else:
                path = os.path.join(outdir, f"{self.ns}_run.mp4")
                try:
                    imageio.mimsave(path, imgs, fps=fps, quality=8); saved.append(path)
                except Exception:
                    fallback = os.path.join(outdir, f"{self.ns}_run.gif")
                    imageio.mimsave(fallback, imgs, duration=1/max(fps,1)); saved.append(fallback)
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
                base = pd.DataFrame({"Value": SAMPLES_A["Random Small"]}, dtype=object)
                s[f"{self.ns}_array_df"] = base.copy()
            DF = s[f"{self.ns}_array_df"].copy()
            hint = "Edit values. Use Add/Delete to change elements."

        DF = self._sanitize_array(DF)
        A = DF["Value"].tolist()
        s.setdefault(f"{self.ns}_array_df", DF.copy())

        gkey = f"{src}::{sample or 'custom'}::A={','.join(map(str,A))}"
        self._ensure_state(A, gkey)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="frame-title">Array Values</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="frame-hint">{hint}</div>', unsafe_allow_html=True)
            if src != "Sample graph":
                c1, c2 = st.columns(2)
                with c1:
                    new_val = st.text_input("Add item", key=f"{self.ns}_add_item", placeholder="e.g. 42")
                    if st.button("Add", key=f"{self.ns}_btn_add"):
                        nv = (new_val or "").strip()
                        if nv != "":
                            DF2 = DF.copy(); DF2.loc[len(DF2)] = [nv]
                            s[f"{self.ns}_array_df"] = self._sanitize_array(DF2)
                            s[f"{self.ns}_inited"] = False
                            st.rerun()
                with c2:
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
            st.markdown('<div class="frame-title">Bubble Sort State</div>', unsafe_allow_html=True)
            self._ensure_state(A, f"{src}::{sample or 'custom'}::A={','.join(map(str,A))}")
            self._state_table(st.session_state[f"{self.ns}_A"])

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="frame-title">Visualization</div>', unsafe_allow_html=True)
            self._draw(st.session_state[f"{self.ns}_A"])
            st.markdown('<div class="legend"><span><i style="background:#f59e0b"></i>Compared</span><span><i style="background:#34d399"></i>Sorted suffix</span><span><i style="background:#3a3f55"></i>Unvisited</span></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="frame-title">Step-by-Step Explanation</div>', unsafe_allow_html=True)
            exp_html = st.session_state.get(f'{self.ns}_exp', '')
            st.markdown(f'<div class="step-explanation">{exp_html}</div>', unsafe_allow_html=True)

        manual = next_clicked or back_clicked or reset_clicked
        if next_clicked and not st.session_state.get(f"{self.ns}_fin", False) and len(A) > 0:
            self._bubble_step()
            self._push()
            st.rerun()
        if back_clicked and len(st.session_state.get(f"{self.ns}_hist", [])) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            self._restore(st.session_state[f"{self.ns}_hist"][-1])
            st.rerun()
        if reset_clicked:
            st.session_state[f"{self.ns}_inited"] = False
            self._ensure_state(A, f"{src}::{sample or 'custom'}::A={','.join(map(str,A))}")
            st.rerun()
        if export_clicked and len(st.session_state.get(f"{self.ns}_hist", [])) > 0 and len(A) > 0:
            paths = self._export(s.get("sb_fmt", "GIF"), max(1, s.get("sb_fps", 6)), st.session_state[f"{self.ns}_A"])
            for p in paths:
                with open(p, "rb") as f:
                    st.sidebar.download_button("Download " + p.split("/")[-1], f, file_name=p.split("/")[-1], mime="application/octet-stream")
        if auto and not st.session_state.get(f"{self.ns}_fin", False) and not manual and len(A) > 0:
            self._bubble_step()
            self._push()
            time.sleep(speed)
            st.rerun()