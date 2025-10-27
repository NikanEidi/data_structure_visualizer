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
    "Nearly Sorted": [1, 2, 3, 5, 6, 7, 8],
    "Reverse": [9, 7, 5, 4, 3, 2, 1],
    "Duplicates": [5, 1, 5, 2, 5, 3],
}

class QuickSortVisualizer:
    def __init__(self):
        self.ns = "quick"

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
            if aa < bb: return -1
            if aa > bb: return 1
            return 0
        sa, sb = str(aa), str(bb)
        if sa < sb: return -1
        if sa > sb: return 1
        return 0

    def _code_block(self, stage="start", l=None, r=None, p=None, i=None, j=None):
        qs = [
            "def quick_sort(A, l, r):",
            "    if l >= r: return",
            "    p = partition(A, l, r)",
            "    quick_sort(A, l, p - 1)",
            "    quick_sort(A, p + 1, r)",
        ]
        pt = [
            "def partition(A, l, r):",
            "    pivot = A[r]",
            "    i = l - 1",
            "    for j in range(l, r):",
            "        if A[j] <= pivot:",
            "            i += 1; swap(A, i, j)",
            "    swap(A, i + 1, r)",
            "    return i + 1",
        ]
        hi_qs = set()
        hi_pt = set()
        if stage == "base":
            hi_qs = {1}
        elif stage == "call_partition":
            hi_qs = {2}
        elif stage == "recurse_left":
            hi_qs = {3}
        elif stage == "recurse_right":
            hi_qs = {4}
        elif stage == "pick_pivot":
            hi_pt = {0,1,2}
        elif stage == "scan":
            hi_pt = {3,4}
        elif stage == "swap_ij":
            hi_pt = {5}
        elif stage == "place_pivot":
            hi_pt = {6,7}

        def render(lines, hi):
            out = []
            for idx, L in enumerate(lines):
                prefix = "&#9654; " if idx in hi else "&nbsp; "
                bg = "background:#1f2a4a;border-radius:4px;padding:0 4px" if idx in hi else ""
                out.append(f"<div style='font-family:monospace;white-space:pre;{bg}'>{prefix}{html.escape(L)}</div>")
            return "\n".join(out)

        ex = []
        if l is not None and r is not None: ex.append(f"l = {l} , r = {r}")
        if p is not None: ex.append(f"p = {p}")
        if i is not None: ex.append(f"i = {i}")
        if j is not None: ex.append(f"j = {j}")
        info = "" if not ex else f"<div style='margin-top:0.25rem;color:#9fb3ff'>{' , '.join(ex)}</div>"

        return (
            "<div style='margin:0'>" +
            render(qs, hi_qs) +
            "<div style='height:6px'></div>" +
            render(pt, hi_pt) +
            info +
            "</div>"
        )

    def _exp_init(self, A):
        n = len(A)
        code = self._code_block(stage=("base" if n <= 1 else "call_partition"), l=0, r=max(0, n-1))
        return f"""<div class="step-content">
<div class="step-header">Initialization</div>
<div class="action">n = <span class="vertex">{n}</span>, segment <span class="vertex">[0..{max(0,n-1)}]</span></div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div>
</div>"""

    def _push(self):
        h = {
            "A": copy.deepcopy(st.session_state[f"{self.ns}_A"]),
            "tasks": copy.deepcopy(st.session_state[f"{self.ns}_tasks"]),
            "cur": copy.deepcopy(st.session_state[f"{self.ns}_cur"]),
            "i": st.session_state[f"{self.ns}_i"],
            "j": st.session_state[f"{self.ns}_j"],
            "pivot_idx": st.session_state[f"{self.ns}_pivot_idx"],
            "step": st.session_state[f"{self.ns}_step"],
            "fin": st.session_state[f"{self.ns}_fin"],
            "exp": st.session_state[f"{self.ns}_exp"],
            "swap_pair": st.session_state[f"{self.ns}_swap_pair"],
        }
        st.session_state[f"{self.ns}_hist"].append(h)

    def _restore(self, s):
        st.session_state[f"{self.ns}_A"] = copy.deepcopy(s["A"])
        st.session_state[f"{self.ns}_tasks"] = copy.deepcopy(s["tasks"])
        st.session_state[f"{self.ns}_cur"] = copy.deepcopy(s["cur"])
        st.session_state[f"{self.ns}_i"] = s["i"]
        st.session_state[f"{self.ns}_j"] = s["j"]
        st.session_state[f"{self.ns}_pivot_idx"] = s["pivot_idx"]
        st.session_state[f"{self.ns}_step"] = s["step"]
        st.session_state[f"{self.ns}_fin"] = s["fin"]
        st.session_state[f"{self.ns}_exp"] = s["exp"]
        st.session_state[f"{self.ns}_swap_pair"] = s["swap_pair"]
        st.session_state[f"{self.ns}_array_df"] = pd.DataFrame({"Value": st.session_state[f"{self.ns}_A"]}, dtype=object)

    def _ensure_state(self, A, gkey):
        tag = f"{self.ns}_inited"
        if (not st.session_state.get(tag)) or st.session_state.get(f"{self.ns}_gkey") != gkey:
            n = len(A)
            st.session_state[f"{self.ns}_A"] = list(A)
            st.session_state[f"{self.ns}_tasks"] = ([{"kind":"sort","l":0,"r":n-1}] if n>0 else [])
            st.session_state[f"{self.ns}_cur"] = {"l":0,"r":(n-1 if n>0 else None),"stage":"start"}
            st.session_state[f"{self.ns}_i"] = None
            st.session_state[f"{self.ns}_j"] = None
            st.session_state[f"{self.ns}_pivot_idx"] = None
            st.session_state[f"{self.ns}_swap_pair"] = (-1,-1)
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_fin"] = (n<=1)
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_exp"] = self._exp_init(A)
            st.session_state[f"{self.ns}_gkey"] = gkey
            st.session_state[tag] = True
            self._push()

    def _step(self):
        if st.session_state[f"{self.ns}_fin"]:
            return
        A = st.session_state[f"{self.ns}_A"]
        tasks = st.session_state[f"{self.ns}_tasks"]
        st.session_state[f"{self.ns}_step"] += 1
        st.session_state[f"{self.ns}_swap_pair"] = (-1,-1)

        if not tasks:
            st.session_state[f"{self.ns}_fin"] = True
            st.session_state[f"{self.ns}_cur"] = {"l":0,"r":len(A)-1,"stage":"done"}
            code = self._code_block(stage="recurse_right", l=0, r=len(A)-1)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="completion">Sorted!</div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
            return

        t = tasks[-1]

        if t["kind"] == "sort":
            l, r = t["l"], t["r"]
            st.session_state[f"{self.ns}_cur"] = {"l":l,"r":r,"stage":"sort"}
            if l >= r:
                tasks.pop()
                code = self._code_block(stage="base", l=l, r=r)
                st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">Segment [{l}..{r}] length ≤ 1 ⇒ base case</div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
                return
            tasks.pop()
            tasks.append({"kind":"after_partition","l":l,"r":r,"p":None})
            tasks.append({"kind":"part","l":l,"r":r,"stage":"pick","i":l-1,"j":l,"pivot_idx":r})
            st.session_state[f"{self.ns}_cur"] = {"l":l,"r":r,"stage":"pick"}
            st.session_state[f"{self.ns}_i"] = l-1
            st.session_state[f"{self.ns}_j"] = l
            st.session_state[f"{self.ns}_pivot_idx"] = r
            code = self._code_block(stage="call_partition", l=l, r=r)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">Call partition on [{l}..{r}]</div>
<div class="queue-display">pivot = A[{r}] = {A[r]}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
            return

        if t["kind"] == "part":
            l, r = t["l"], t["r"]
            i, j, pv_idx = t["i"], t["j"], t["pivot_idx"]
            pivot = A[pv_idx]
            st.session_state[f"{self.ns}_cur"] = {"l":l,"r":r,"stage":t["stage"]}
            st.session_state[f"{self.ns}_i"] = i
            st.session_state[f"{self.ns}_j"] = j
            st.session_state[f"{self.ns}_pivot_idx"] = pv_idx

            if t["stage"] == "pick":
                t["stage"] = "scan"
                code = self._code_block(stage="pick_pivot", l=l, r=r, i=i, j=j)
                st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">pivot = <span class="vertex">{pivot}</span> at index {pv_idx}</div>
<div class="action">i = l - 1 = {l-1}, j = l = {l}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
                return

            if t["stage"] == "scan":
                if j < r:
                    if self._cmp(A[j], pivot) <= 0:
                        t["stage"] = "swap_ij"
                        t["i"] = i + 1
                        st.session_state[f"{self.ns}_i"] = i + 1
                        code = self._code_block(stage="scan", l=l, r=r, i=i+1, j=j)
                        st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">A[{j}] = {A[j]} ≤ pivot {pivot} ⇒ i ← {i+1}, swap(A[i], A[j])</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
                        return
                    else:
                        t["j"] = j + 1
                        st.session_state[f"{self.ns}_j"] = j + 1
                        code = self._code_block(stage="scan", l=l, r=r, i=i, j=j+1)
                        st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">A[{j}] = {A[j]} > pivot {pivot} ⇒ j ← {j+1}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
                        return
                t["stage"] = "place"
                code = self._code_block(stage="place_pivot", l=l, r=r, i=i, j=j)
                st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">End of scan ⇒ swap pivot into position i+1 = {i+1}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
                return

            if t["stage"] == "swap_ij":
                ai, aj = t["i"], t["j"]
                if ai != aj:
                    A[ai], A[aj] = A[aj], A[ai]
                    st.session_state[f"{self.ns}_swap_pair"] = (ai, aj)
                t["j"] = aj + 1
                t["stage"] = "scan"
                st.session_state[f"{self.ns}_j"] = aj + 1
                code = self._code_block(stage="swap_ij", l=l, r=r, i=ai, j=aj)
                st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">swap(A[{ai}], A[{aj}]) ⇒ Array: {', '.join(map(str,A))}</div>
<div class="action">j ← {aj+1}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
                return

            if t["stage"] == "place":
                pi = i + 1
                if pi != r:
                    A[pi], A[r] = A[r], A[pi]
                    st.session_state[f"{self.ns}_swap_pair"] = (pi, r)
                tasks.pop()
                ap = tasks[-1] if tasks and tasks[-1]["kind"] == "after_partition" else None
                if ap:
                    ap["p"] = pi
                st.session_state[f"{self.ns}_pivot_idx"] = pi
                code = self._code_block(stage="place_pivot", l=l, r=r, p=pi)
                st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="completion">pivot placed at index <span class="vertex">{pi}</span></div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
                return

        if t["kind"] == "after_partition":
            l, r, p = t["l"], t["r"], t["p"]
            tasks.pop()
            tasks.append({"kind":"sort","l":p+1,"r":r})
            tasks.append({"kind":"sort","l":l,"r":p-1})
            st.session_state[f"{self.ns}_cur"] = {"l":l,"r":r,"stage":"recurse"}
            code = self._code_block(stage="recurse_left", l=l, r=r, p=p)
            st.session_state[f"{self.ns}_exp"] = f"""<div class="step-content">
<div class="step-header">Step {st.session_state[f"{self.ns}_step"]}</div>
<div class="action">Recurse on left [{l}..{p-1}] and right [{p+1}..{r}]</div>
<div class="queue-display">Array: {', '.join(map(str,A))}</div>
<div style="margin-top:0.5rem">{code}</div></div>"""
            return

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
        cur = st.session_state[f"{self.ns}_cur"] or {}
        l = cur.get("l", "-"); r = cur.get("r", "-"); stage = cur.get("stage","-")
        i = st.session_state.get(f"{self.ns}_i"); j = st.session_state.get(f"{self.ns}_j"); pidx = st.session_state.get(f"{self.ns}_pivot_idx")
        idxs = list(range(len(A)))
        in_seg = lambda x: (isinstance(l,int) and isinstance(r,int) and l <= x <= r)
        left_ok = set()
        if isinstance(i,int) and isinstance(l,int):
            left_ok = set(range(l, max(i, l-1)+1))
        df = pd.DataFrame({
            "Index": idxs,
            "Value": [A[x] for x in idxs],
            "In segment": ["✓" if in_seg(x) else "-" for x in idxs],
            "≤ pivot region": ["✓" if x in left_ok else "-" for x in idxs],
            "i ptr": ["✓" if (i is not None and x == i) else "-" for x in idxs],
            "j ptr": ["✓" if (j is not None and x == j) else "-" for x in idxs],
            "pivot": ["✓" if (pidx is not None and x == pidx) else "-" for x in idxs],
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
            <div class="pill"><div class="h">Stage</div><div class="v">{stage}</div></div>
            <div class="pill"><div class="h">l..r</div><div class="v">{l}..{r}</div></div>
            <div class="pill"><div class="h">i/j/p</div><div class="v">{i if i is not None else '-'} / {j if j is not None else '-'} / {pidx if pidx is not None else '-'}</div></div>
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
        cur = st.session_state.get(f"{self.ns}_cur", {})
        l, r = cur.get("l"), cur.get("r")
        i = st.session_state.get(f"{self.ns}_i")
        j = st.session_state.get(f"{self.ns}_j")
        pidx = st.session_state.get(f"{self.ns}_pivot_idx")
        sp_i, sp_j = st.session_state.get(f"{self.ns}_swap_pair",( -1,-1))

        fig, ax = plt.subplots(figsize=(max(7, min(12, 1.1*n + 2)), 5.0))
        fig.patch.set_facecolor(COLORS["background"])
        ax.set_facecolor(COLORS["background"])

        pad = 0.2
        for idx, val in enumerate(A):
            x = idx + pad; y = 1.7; w = 0.85; h = 1.2
            fc = COLORS["unvisited"]
            if isinstance(l,int) and isinstance(r,int) and l <= idx <= r:
                fc = COLORS["unvisited"]
            if isinstance(i,int) and isinstance(l,int) and l <= idx <= max(i,l-1):
                fc = COLORS["visited"]
            if pidx is not None and idx == pidx:
                fc = COLORS["source"]
            if (j is not None and idx == j) or (i is not None and idx == i):
                fc = COLORS["current"]
            if idx in (sp_i, sp_j) and sp_i != -1:
                fc = COLORS["current"]
            rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.06",
                                          linewidth=2, edgecolor=GRAPH_LAYOUT_CONFIG["node_border_color"], facecolor=fc)
            ax.add_patch(rect)
            ax.text(x + w/2, y + h/2 + 0.18, str(val), ha="center", va="center",
                    fontsize=GRAPH_LAYOUT_CONFIG["font_size"], color=GRAPH_LAYOUT_CONFIG["font_color"],
                    fontweight=GRAPH_LAYOUT_CONFIG["font_weight"])
            ax.text(x + w/2, y - 0.05, f"{idx}", ha="center", va="top", fontsize=10, color="#9fb3ff")

        if isinstance(l,int) and isinstance(r,int):
            ax.text((l + r + 2*pad)/2, 3.05, f"[{l}..{r}]", ha="center", va="bottom", fontsize=11, color="#9fb3ff")
        if pidx is not None:
            ax.text(pidx + pad + 0.42, 3.05, f"pivot@{pidx}", ha="center", va="bottom", fontsize=10, color="#9fb3ff")

        ax.set_xlim(0, n + 1.2); ax.set_ylim(0.9, 3.3); ax.axis("off")
        st.pyplot(fig)
        plt.close(fig)

    def _frame_figure(self, A, step_text):
        fig = plt.figure(figsize=(10.5, 7.4), layout="constrained")
        fig.patch.set_facecolor(COLORS["background"])
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])
        ax = fig.add_subplot(gs[0])
        n = len(A)
        cur = st.session_state.get(f"{self.ns}_cur", {})
        l, r = cur.get("l"), cur.get("r")
        i = st.session_state.get(f"{self.ns}_i")
        j = st.session_state.get(f"{self.ns}_j")
        pidx = st.session_state.get(f"{self.ns}_pivot_idx")
        sp_i, sp_j = st.session_state.get(f"{self.ns}_swap_pair",( -1,-1))

        ax.set_facecolor(COLORS["background"])
        pad = 0.2
        for idx, val in enumerate(A):
            x = idx + pad; y = 1.7; w = 0.85; h = 1.2
            fc = COLORS["unvisited"]
            if isinstance(l,int) and isinstance(r,int) and l <= idx <= r:
                fc = COLORS["unvisited"]
            if isinstance(i,int) and isinstance(l,int) and l <= idx <= max(i,l-1):
                fc = COLORS["visited"]
            if pidx is not None and idx == pidx:
                fc = COLORS["source"]
            if (j is not None and idx == j) or (i is not None and idx == i):
                fc = COLORS["current"]
            if idx in (sp_i, sp_j) and sp_i != -1:
                fc = COLORS["current"]
            rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.06",
                                          linewidth=2, edgecolor="#9aa4d3", facecolor=fc)
            ax.add_patch(rect)
            ax.text(x + w/2, y + h/2 + 0.18, str(val), ha="center", va="center",
                    fontsize=12, color="#eef3ff", fontweight="bold")
            ax.text(x + w/2, y - 0.05, f"{idx}", ha="center", va="top", fontsize=10, color="#9fb3ff")

        if isinstance(l,int) and isinstance(r,int):
            ax.text((l + r + 2*pad)/2, 3.05, f"[{l}..{r}]", ha="center", va="bottom", fontsize=11, color="#9fb3ff")
        if pidx is not None:
            ax.text(pidx + pad + 0.42, 3.05, f"pivot@{pidx}", ha="center", va="bottom", fontsize=10, color="#9fb3ff")

        ax.set_xlim(0, n + 1.2); ax.set_ylim(0.9, 3.3); ax.set_xticks([]); ax.set_yticks([])

        ax2 = fig.add_subplot(gs[1])
        ax2.set_facecolor("#0d1220"); ax2.set_xticks([]); ax2.set_yticks([])
        plain = self._html_to_plain(step_text)
        ax2.text(0.02, 0.95, "Step-by-step", fontsize=12, color="#9fb3ff", fontweight="bold", va="top")
        ax2.text(0.02, 0.75, plain, fontsize=10, color="#e6ecff", va="top", family="monospace", wrap=True, linespacing=1.5)
        return fig

    def _export(self, fmt, fps, A):
        frames = []; saved = []
        for s in st.session_state[f"{self.ns}_hist"]:
            self._restore(s)
            fig = self._frame_figure(st.session_state[f"{self.ns}_A"], s["exp"])
            buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=140, facecolor=fig.get_facecolor())
            plt.close(fig); buf.seek(0); frames.append(buf.read())
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
            st.markdown('<div class="frame-title">Quick Sort State</div>', unsafe_allow_html=True)
            self._ensure_state(A, f"{src}::{sample or 'custom'}::A={','.join(map(str,A))}")
            self._state_table(st.session_state[f"{self.ns}_A"])

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="frame-title">Visualization</div>', unsafe_allow_html=True)
            self._draw(st.session_state[f"{self.ns}_A"])
            st.markdown('<div class="legend"><span><i style="background:#7c4dff"></i>Pivot</span><span><i style="background:#34d399"></i>≤ pivot region</span><span><i style="background:#f59e0b"></i>i / j / swap</span><span><i style="background:#3a3f55"></i>Unvisited</span></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="frame-title">Step-by-Step Explanation</div>', unsafe_allow_html=True)
            exp_html = st.session_state.get(f'{self.ns}_exp', '')
            st.markdown(f'<div class="step-explanation">{exp_html}</div>', unsafe_allow_html=True)

        manual = next_clicked or back_clicked or reset_clicked
        if next_clicked and not st.session_state.get(f"{self.ns}_fin", False) and len(A) > 0:
            self._step()
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
            self._step()
            self._push()
            time.sleep(speed)
            st.rerun()