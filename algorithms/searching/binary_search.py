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
    "Sorted 6": [1, 3, 4, 7, 9, 12],
    "Sorted 10": [2, 5, 8, 11, 14, 17, 20, 23, 26, 29],
    "Near-Duplicates": [1, 2, 2, 2, 3, 4, 4, 5],
}

class BinarySearchVisualizer:
    def __init__(self):
        self.ns = "binary"

    def _sample_df(self, name):
        arr = SAMPLES_A.get(name, SAMPLES_A["Sorted 6"])
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
        try:
            return int(txt) if "." not in txt else float(txt)
        except Exception:
            try:
                return float(txt)
            except Exception:
                return txt

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

    def _ensure_state(self, A, target, gkey):
        tag = f"{self.ns}_inited"
        if (not st.session_state.get(tag)) or st.session_state.get(f"{self.ns}_gkey") != gkey:
            n = len(A)
            st.session_state[f"{self.ns}_visited"] = {i: False for i in range(n)}
            st.session_state[f"{self.ns}_lo"] = 0 if n > 0 else None
            st.session_state[f"{self.ns}_hi"] = n - 1 if n > 0 else None
            st.session_state[f"{self.ns}_mid"] = None
            st.session_state[f"{self.ns}_current"] = None
            st.session_state[f"{self.ns}_found_idx"] = None
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_fin"] = (n == 0)
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_exp"] = self._exp_init(target, n)
            st.session_state[f"{self.ns}_gkey"] = gkey
            st.session_state[tag] = True
            self._push()

    def _code_block(self, stage="start", lo=None, hi=None, mid=None):
        lines = [
            "lo = 0; hi = n - 1",
            "while lo <= hi:",
            "    mid = (lo + hi) // 2",
            "    if A[mid] == target: return mid",
            "    elif A[mid] < target: lo = mid + 1",
            "    else: hi = mid - 1",
            "return -1",
        ]
        if stage == "start":
            hi_idx = {0}
        elif stage == "choose_mid":
            hi_idx = {1, 2}
        elif stage == "found":
            hi_idx = {3}
        elif stage == "go_right":
            hi_idx = {4}
        elif stage == "go_left":
            hi_idx = {5}
        else:
            hi_idx = {6}
        out = []
        for k, L in enumerate(lines):
            esc = html.escape(L)
            if k in hi_idx:
                line = f"▶ <span style='background:#1f2a4a;border-radius:4px;padding:0 4px'>{esc}</span>"
            else:
                line = f"&nbsp; {esc}"
            out.append(line)
        ex = []
        if lo is not None and hi is not None:
            ex.append(f"lo = {lo}")
            ex.append(f"hi = {hi}")
        if mid is not None:
            ex.append(f"mid = {mid}")
        ex_txt = "" if not ex else f"<div style='margin-top:0.25rem;color:#9fb3ff'>{' , '.join(ex)}</div>"
        return "<pre style='margin:0;white-space:pre-wrap'><code>" + "\n".join(out) + "</code></pre>" + ex_txt

    def _exp_init(self, target, n):
        tshow = str(target) if target != "" else "N/A"
        code = self._code_block(stage="start", lo=0 if n > 0 else None, hi=n - 1 if n > 0 else None)
        return f"""<div class="step-content">
<div class="step-header">Initialization</div>
<div class="action">Target = <span class="vertex">{tshow}</span>, n = {n}</div>
<div class="action">lo = <span class="vertex">{0 if n>0 else 'N/A'}</span>, hi = <span class="vertex">{(n-1) if n>0 else 'N/A'}</span></div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""

    def _push(self):
        h = {
            "visited": copy.deepcopy(st.session_state[f"{self.ns}_visited"]),
            "lo": st.session_state[f"{self.ns}_lo"],
            "hi": st.session_state[f"{self.ns}_hi"],
            "mid": st.session_state[f"{self.ns}_mid"],
            "current": st.session_state[f"{self.ns}_current"],
            "found_idx": st.session_state[f"{self.ns}_found_idx"],
            "exp": st.session_state[f"{self.ns}_exp"],
            "fin": st.session_state[f"{self.ns}_fin"],
            "step": st.session_state[f"{self.ns}_step"],
        }
        st.session_state[f"{self.ns}_hist"].append(h)

    def _restore(self, s):
        st.session_state[f"{self.ns}_visited"] = copy.deepcopy(s["visited"])
        st.session_state[f"{self.ns}_lo"] = s["lo"]
        st.session_state[f"{self.ns}_hi"] = s["hi"]
        st.session_state[f"{self.ns}_mid"] = s["mid"]
        st.session_state[f"{self.ns}_current"] = s["current"]
        st.session_state[f"{self.ns}_found_idx"] = s["found_idx"]
        st.session_state[f"{self.ns}_exp"] = s["exp"]
        st.session_state[f"{self.ns}_fin"] = s["fin"]
        st.session_state[f"{self.ns}_step"] = s["step"]

    def _binary_step(self, A, target):
        if st.session_state[f"{self.ns}_fin"]:
            return
        st.session_state[f"{self.ns}_step"] += 1
        lo = st.session_state[f"{self.ns}_lo"]
        hi = st.session_state[f"{self.ns}_hi"]
        if lo is None or hi is None or lo > hi:
            code = self._code_block(stage="done", lo=lo, hi=hi)
            st.session_state[f"{self.ns}_fin"] = True
            st.session_state[f"{self.ns}_mid"] = None
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="completion">lo > hi ⇒ target not found.</div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""
            return
        mid = (lo + hi) // 2
        st.session_state[f"{self.ns}_mid"] = mid
        st.session_state[f"{self.ns}_current"] = mid
        st.session_state[f"{self.ns}_visited"][mid] = True
        code0 = self._code_block(stage="choose_mid", lo=lo, hi=hi, mid=mid)
        val = A[mid]
        c = self._cmp(val, target)
        if c == 0:
            st.session_state[f"{self.ns}_found_idx"] = mid
            st.session_state[f"{self.ns}_fin"] = True
            code = self._code_block(stage="found", lo=lo, hi=hi, mid=mid)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">mid = ⌊(lo + hi)/2⌋ = <span class="vertex">{mid}</span></div>
<div class="action">Compare A[{mid}] = <span class="vertex">{val}</span> with target ⇒ match ✓</div>
<div class="completion">Return index <span class="vertex">{mid}</span></div>
<div style="margin-top:0.5rem">{code0}</div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""
        elif c < 0:
            st.session_state[f"{self.ns}_lo"] = mid + 1
            code = self._code_block(stage="go_right", lo=st.session_state[f"{self.ns}_lo"], hi=hi, mid=mid)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">mid = ⌊(lo + hi)/2⌋ = <span class="vertex">{mid}</span></div>
<div class="action">A[{mid}] = <span class="vertex">{val}</span> &lt; target ⇒ search right half</div>
<div class="action">lo ← mid + 1 ⇒ <span class="vertex">{st.session_state[f"{self.ns}_lo"]}</span></div>
<div style="margin-top:0.5rem">{code0}</div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""
        else:
            st.session_state[f"{self.ns}_hi"] = mid - 1
            code = self._code_block(stage="go_left", lo=lo, hi=st.session_state[f"{self.ns}_hi"], mid=mid)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">mid = ⌊(lo + hi)/2⌋ = <span class="vertex">{mid}</span></div>
<div class="action">A[{mid}] = <span class="vertex">{val}</span> &gt; target ⇒ search left half</div>
<div class="action">hi ← mid - 1 ⇒ <span class="vertex">{st.session_state[f"{self.ns}_hi"]}</span></div>
<div style="margin-top:0.5rem">{code0}</div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""

    def _ag_clean(self, original_df, ag_out):
        df_out = pd.DataFrame(ag_out.data if hasattr(ag_out, "data") else ag_out)
        bad = [c for c in df_out.columns if str(c).startswith("::") or c in ("index",)]
        df_out = df_out.drop(columns=bad, errors="ignore")
        if "Value" not in df_out.columns and len(df_out.columns) > 0:
            df_out = df_out.rename(columns={df_out.columns[0]: "Value"})
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
        lo = st.session_state[f"{self.ns}_lo"]
        hi = st.session_state[f"{self.ns}_hi"]
        idxs = list(range(len(A)))
        df = pd.DataFrame({
            "Index": idxs,
            "Value": [A[i] for i in idxs],
            "Visited": ["✓" if vis.get(i, False) else "-" for i in idxs],
            "Current(mid)": ["✓" if i == cur and not st.session_state[f"{self.ns}_fin"] else "-" for i in idxs],
            "Found": ["✓" if i == found else "-" for i in idxs],
        })
        if AG_OK:
            g = GridOptionsBuilder.from_dataframe(df)
            g.configure_grid_options(domLayout="autoHeight", suppressMovableColumns=True, rowSelection="none", enableSorting=False, rowHeight=34)
            g.configure_default_column(editable=False, resizable=True)
            AgGrid(df, gridOptions=g.build(), theme="streamlit", height=260, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.NO_UPDATE, data_return_mode=DataReturnMode.AS_INPUT)
        else:
            st.dataframe(df, height=260, use_container_width=True)
        st.markdown(f"""<div class="bfs-meta">
            <div class="pill"><div class="h">lo</div><div class="v">{lo if lo is not None else "-"}</div></div>
            <div class="pill"><div class="h">hi</div><div class="v">{hi if hi is not None else "-"}</div></div>
            <div class="pill"><div class="h">mid</div><div class="v">{st.session_state.get(f"{self.ns}_mid","-")}</div></div>
        </div>""", unsafe_allow_html=True)

    def _html_to_plain(self, html_text):
        import re
        text = html_text
        text = re.sub(r'<div class="step-header">([^<]+)</div>', r'\n\1\n' + '='*40 + '\n', text)
        text = re.sub(r'<div class="action">([^<]*(?:<span[^>]*>([^<]+)</span>[^<]*)*)</div>', lambda m: '→ ' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n', text)
        text = re.sub(r'<span class=["\']vertex["\']>([^<]+)</span>', r'[\1]', text)
        text = re.sub(r'<div class="completion">([^<]*(?:<[^>]+>[^<]*)*)</div>', lambda m: '\n' + '='*40 + '\n' + re.sub(r'<[^>]+>', '', m.group(1)) + '\n' + '='*40 + '\n', text)
        text = re.sub(r'<pre[^>]*><code>(.*?)</code></pre>', lambda m: "\n" + re.sub(r'<[^>]+>', '', m.group(1)).replace("&nbsp;", " ").replace("\n\n", "\n") + "\n", text, flags=re.DOTALL)
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
        fig, ax = plt.subplots(figsize=(max(7, min(12, 1.1*n + 2)), 4.8))
        fig.patch.set_facecolor(COLORS["background"])
        ax.set_facecolor(COLORS["background"])
        cur = st.session_state[f"{self.ns}_current"]
        visited = st.session_state[f"{self.ns}_visited"]
        found = st.session_state[f"{self.ns}_found_idx"]
        lo = st.session_state[f"{self.ns}_lo"]
        hi = st.session_state[f"{self.ns}_hi"]
        pad = 0.2
        if lo is not None and hi is not None and lo <= hi:
            x0 = lo + pad - 0.05
            w = (hi - lo + 1) - (1 - pad) + 0.1
            rect_range = patches.FancyBboxPatch((x0, 1.25), w, 1.5, boxstyle="round,pad=0.03,rounding_size=0.04", linewidth=1.5, edgecolor="#ef4444", facecolor="#ef4444", alpha=0.12)
            ax.add_patch(rect_range)
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
        ttxt = str(target) if target != "" else "N/A"
        ax.text(0.02, 0.3, f"target = {ttxt}", fontsize=12, color="#9fb3ff", transform=ax.transAxes, fontweight="bold")
        ax.set_xlim(0, n + 1.2)
        ax.set_ylim(0.8, 3.2)
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
        lo = st.session_state[f"{self.ns}_lo"]
        hi = st.session_state[f"{self.ns}_hi"]
        pad = 0.2
        if lo is not None and hi is not None and lo <= hi:
            x0 = lo + pad - 0.05
            w = (hi - lo + 1) - (1 - pad) + 0.1
            rect_range = patches.FancyBboxPatch((x0, 1.25), w, 1.5, boxstyle="round,pad=0.03,rounding_size=0.04", linewidth=1.5, edgecolor="#ef4444", facecolor="#ef4444", alpha=0.12)
            ax.add_patch(rect_range)
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
        ttxt = str(target) if target != "" else "N/A"
        ax.text(0.02, 0.3, f"target = {ttxt}", fontsize=12, color="#9fb3ff", transform=ax.transAxes, fontweight="bold")
        ax.set_xlim(0, n + 1.2); ax.set_ylim(0.8, 3.2); ax.set_xticks([]); ax.set_yticks([])

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
        sample = s.get("sb_sample", "Sorted 6")
        auto = s.get("sb_auto", False)
        speed = s.get("sb_speed", 0.8)
        next_clicked = s.get("sb_next", False)
        back_clicked = s.get("sb_back", False)
        reset_clicked = s.get("sb_reset", False)
        export_clicked = s.get("sb_export", False)

        if src == "Sample graph":
            DF = self._sample_df(sample if sample in SAMPLES_A else "Sorted 6")
            s.setdefault(f"{self.ns}_array_df", DF.copy())
            hint = f"Sample: {sample if sample in SAMPLES_A else 'Sorted 6'}. Keep array sorted."
        else:
            if f"{self.ns}_array_df" not in s:
                base = pd.DataFrame({"Value": [1, 3, 4, 7, 9, 12]}, dtype=object)
                s[f"{self.ns}_array_df"] = base.copy()
            DF = s[f"{self.ns}_array_df"].copy()
            hint = "Edit values. Use Add/Delete to change elements (keep sorted)."

        DF = self._sanitize_array(DF)
        A = DF["Value"].tolist()

        s.setdefault(f"{self.ns}_target_raw", str(A[len(A)//2]) if A else "")
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
                    new_val = st.text_input("Add item", key=f"{self.ns}_add_item", placeholder="e.g. 13")
                    if st.button("Add", key=f"{self.ns}_btn_add"):
                        nv = (new_val or "").strip()
                        if nv != "":
                            DF2 = DF.copy()
                            DF2.loc[len(DF2)] = [nv]
                            s[f"{self.ns}_array_df"] = self._sanitize_array(DF2).sort_values("Value").reset_index(drop=True)
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
            st.markdown('<div class="frame-title">Binary Search State</div>', unsafe_allow_html=True)
            s.setdefault(f"{self.ns}_target_raw", str(A[len(A)//2]) if A else "")
            st.text_input("Target value", key=f"{self.ns}_target_raw")
            target = self._parse_target(s)
            gkey = f"{src}::{sample or 'custom'}::A={','.join(map(str,A))}::t={target}"
            self._ensure_state(A, target, gkey)
            self._state_table(A)
            visited_count = sum(st.session_state.get(f"{self.ns}_visited", {}).values()) if A else 0
            remaining = max(0, (st.session_state.get(f"{self.ns}_hi",-1) - st.session_state.get(f"{self.ns}_lo",0) + 1)) if A else 0
            status = "Completed" if st.session_state.get(f"{self.ns}_fin", False) else "Running"
            cls = "ok" if status == "Completed" else "run"
            st.markdown(f'''
            <div class="bfs-meta">
                <div class="pill"><div class="h">Step</div><div class="v">{st.session_state.get(f"{self.ns}_step", 0)}</div></div>
                <div class="pill"><div class="h">Checked</div><div class="v">{visited_count}</div></div>
                <div class="pill"><div class="h">Interval</div><div class="v">[{st.session_state.get(f"{self.ns}_lo","-")}, {st.session_state.get(f"{self.ns}_hi","-")}]</div></div>
                <div class="pill"><div class="h">Status</div><div class="v {cls}">{status}</div></div>
            </div>
            ''', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="frame-title">Visualization</div>', unsafe_allow_html=True)
            self._draw(A, target)
            st.markdown('<div class="legend"><span><i style="background:#ef4444"></i>Search Range</span><span><i style="background:#f59e0b"></i>Current(mid)</span><span><i style="background:#34d399"></i>Visited</span><span><i style="background:#7c4dff"></i>Found</span><span><i style="background:#3a3f55"></i>Unvisited</span></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="frame-title">Step-by-Step Explanation</div>', unsafe_allow_html=True)
            exp_html = st.session_state.get(f'{self.ns}_exp', '')
            st.markdown(f'<div class="step-explanation">{exp_html}</div>', unsafe_allow_html=True)

        manual = next_clicked or back_clicked or reset_clicked
        if next_clicked and not st.session_state.get(f"{self.ns}_fin", False) and len(A) > 0:
            self._binary_step(A, target)
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
            self._binary_step(A, target)
            self._push()
            time.sleep(speed)
            st.rerun()