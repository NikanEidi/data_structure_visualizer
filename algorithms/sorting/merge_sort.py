import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import copy, random, time


from algorithms.graph.graphStyle import CSS, COLORS

SAMPLES = {
    "Sample 1 – Random": [9, 3, 7, 2, 5],
    "Sample 2 – Nearly Sorted": [1, 3, 4, 6, 5, 7],
    "Sample 3 – Reverse Sorted": [10, 8, 6, 4, 2]
}

CANON_CODE = """def merge_sort(arr):            # L1
    if len(arr) > 1:               # L2
        mid = len(arr)//2          # L3
        left = arr[:mid]           # L4
        right = arr[mid:]          # L5
        merge_sort(left)           # L6
        merge_sort(right)          # L7
        i = j = k = 0              # L8
        while i < len(left) and j < len(right):  # L9
            if left[i] <= right[j]:              # L10
                arr[k] = left[i]; i += 1         # L11
            else:
                arr[k] = right[j]; j += 1        # L12
            k += 1                                # L13
        while i < len(left):                     # L14
            arr[k] = left[i]; i += 1; k += 1     # L15
        while j < len(right):                    # L16
            arr[k] = right[j]; j += 1; k += 1    # L17
    return arr                                   # L18"""

def code_with_pointer(active):
    lines = CANON_CODE.splitlines()
    out = []
    for ln in lines:
        tag = ln.split('#')[-1].strip() if '#' in ln else ""
        mark = "  ◀" if tag in active else ""
        out.append(f"{ln}{mark}")
    return "<pre><code>" + "\n".join(out) + "</code></pre>"

class MergeSortVisualizer:
    def __init__(self):
        self.ns = "ms"

    def render(self):
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Array Configuration</h2>', unsafe_allow_html=True)

        mode = st.sidebar.radio("Input mode:", ["Use sample array", "Build your own"], key=f"{self.ns}_mode")
        if mode == "Use sample array":
            s = st.sidebar.selectbox("Select sample:", list(SAMPLES.keys()), key=f"{self.ns}_sample")
            arr = list(map(int, SAMPLES[s]))
            akey = f"sample::{s}"
        else:
            n = st.sidebar.slider("Number of elements", 2, 20, 7, key=f"{self.ns}_n")
            if f"{self.ns}_arr_seed" not in st.session_state or st.session_state[f"{self.ns}_arr_seed"] != n:
                st.session_state[f"{self.ns}_arr_list"] = [random.randint(-20, 99) for _ in range(n)]
                st.session_state[f"{self.ns}_arr_seed"] = n
            df = pd.DataFrame({"Value": st.session_state[f"{self.ns}_arr_list"]})
            e = st.data_editor(df, num_rows="fixed", use_container_width=True, key=f"{self.ns}_editor")
            vals = [int(x) if str(x).strip().lstrip('-').isdigit() else 0 for x in e["Value"].tolist()]
            st.session_state[f"{self.ns}_arr_list"] = vals
            arr = list(vals)
            akey = f"custom::{','.join(map(str, arr))}"

        st.sidebar.markdown("---")
        auto = st.sidebar.checkbox("Enable Auto-Play", False, key=f"{self.ns}_auto")
        speed = st.sidebar.slider("Speed (seconds per step)", 0.2, 2.5, 0.8, 0.1, key=f"{self.ns}_speed")

        def push():
            snap = {
                "a": list(st.session_state[f"{self.ns}_a"]),
                "stack": copy.deepcopy(st.session_state[f"{self.ns}_stack"]),
                "step": st.session_state[f"{self.ns}_step"],
                "exp": st.session_state[f"{self.ns}_exp"],
                "fin": st.session_state[f"{self.ns}_fin"],
                "hilite": copy.deepcopy(st.session_state[f"{self.ns}_hilite"]),
            }
            st.session_state.setdefault(f"{self.ns}_hist", []).append(snap)

        def restore(s):
            st.session_state[f"{self.ns}_a"] = list(s["a"])
            st.session_state[f"{self.ns}_stack"] = copy.deepcopy(s["stack"])
            st.session_state[f"{self.ns}_step"] = s["step"]
            st.session_state[f"{self.ns}_exp"] = s["exp"]
            st.session_state[f"{self.ns}_fin"] = s["fin"]
            st.session_state[f"{self.ns}_hilite"] = copy.deepcopy(s["hilite"])

        def finish(a):
            st.session_state[f"{self.ns}_fin"] = True
            st.session_state[f"{self.ns}_exp"] = (
                '<h3 class="step-header">Sorting Complete</h3>'
                + code_with_pointer({"L18"})
                + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Final array:</strong> <code>{a}</code></div>
  <div class="step-info-line"><strong>Correctness idea:</strong> Each merge combines two sorted halves into a larger sorted segment; by induction, the whole array is sorted.</div>
</div>"""
            )

        def init_state():
            st.session_state[f"{self.ns}_akey"] = akey
            st.session_state[f"{self.ns}_a"] = list(arr)
            st.session_state[f"{self.ns}_stack"] = [(0, len(arr), "split")]
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_hilite"] = {"seg": (0, len(arr)), "left": None, "right": None}
            st.session_state[f"{self.ns}_exp"] = (
                '<h3 class="step-header">Initialization</h3>'
                + code_with_pointer({"L1","L2"})
                + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Array:</strong> <code>{arr}</code></div>
  <div class="step-info-line"><strong>Strategy:</strong> Recursively split until size ≤ 1, then merge sorted halves upward.</div>
  <div class="step-info-line"><strong>Initial frame:</strong> <code>(l=0, r={len(arr)}, phase='split')</code></div>
</div>"""
            )
            push()

        def step_merge_sort():
            if st.session_state.get(f"{self.ns}_fin"):
                return

            a = st.session_state[f"{self.ns}_a"]
            stack = st.session_state[f"{self.ns}_stack"]
            st.session_state[f"{self.ns}_step"] += 1

            if not stack:
                return finish(a)

            l, r, phase = stack.pop()

            if phase == "split":
                st.session_state[f"{self.ns}_hilite"] = {"seg": (l, r), "left": None, "right": None}
                if r - l <= 1:
                    st.session_state[f"{self.ns}_exp"] = (
                        f'<h3 class="step-header">Step {st.session_state[f"{self.ns}_step"]}: Base Case</h3>'
                        + code_with_pointer({"L2"})
                        + f"""
<div class="step-info">
  <div class="step-info-line">Segment <code>[{l}:{r})</code> has size ≤ 1 → already sorted.</div>
  <div class="step-info-line"><strong>Invariant:</strong> Any length-1 segment is sorted.</div>
</div>"""
                    )
                else:
                    mid = (l + r) // 2
                    stack.append((l, r, "merge"))
                    stack.append((mid, r, "split"))
                    stack.append((l, mid, "split"))
                    st.session_state[f"{self.ns}_hilite"] = {"seg": (l, r), "left": (l, mid), "right": (mid, r)}
                    st.session_state[f"{self.ns}_exp"] = (
                        f'<h3 class="step-header">Step {st.session_state[f"{self.ns}_step"]}: Split</h3>'
                        + code_with_pointer({"L3","L4","L5","L6","L7"})
                        + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Divide:</strong> <code>[{l}:{r})</code> → <code>[{l}:{mid})</code> and <code>[{mid}:{r})</code></div>
  <div class="step-info-line"><strong>Plan:</strong> Sort each half, then merge.</div>
</div>"""
                    )

            elif phase == "merge":
                mid = (l + r) // 2
                left = a[l:mid]
                right = a[mid:r]
                i = j = 0
                k = l
                while i < len(left) and j < len(right):
                    if left[i] <= right[j]:
                        a[k] = left[i]; i += 1
                    else:
                        a[k] = right[j]; j += 1
                    k += 1
                while i < len(left):
                    a[k] = left[i]; i += 1; k += 1
                while j < len(right):
                    a[k] = right[j]; j += 1; k += 1

                st.session_state[f"{self.ns}_hilite"] = {"seg": (l, r), "left": (l, mid), "right": (mid, r)}
                st.session_state[f"{self.ns}_exp"] = (
                    f'<h3 class="step-header">Step {st.session_state[f"{self.ns}_step"]}: Merge</h3>'
                    + code_with_pointer({"L8","L9","L10","L11","L12","L13","L14","L15","L16","L17"})
                    + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Left:</strong> <code>{left}</code>  |  <strong>Right:</strong> <code>{right}</code></div>
  <div class="step-info-line"><strong>Result [{l}:{r}):</strong> <code>{a[l:r]}</code></div>
  <div class="step-info-line"><strong>Why correct:</strong> Always take the smaller head; appending the rest preserves order.</div>
</div>"""
                )

            st.session_state[f"{self.ns}_stack"] = stack

        # Initialize on first load or when the array changes
        if f"{self.ns}_akey" not in st.session_state or st.session_state[f"{self.ns}_akey"] != akey:
            init_state()
        # Safety: ensure hilite exists even if user hot-swapped files / reloaded
        st.session_state.setdefault(f"{self.ns}_a", list(arr))
        st.session_state.setdefault(f"{self.ns}_hilite", {"seg": (0, len(st.session_state[f'{self.ns}_a'])), "left": None, "right": None})
        st.session_state.setdefault(f"{self.ns}_stack", [(0, len(st.session_state[f'{self.ns}_a']), "split")])
        st.session_state.setdefault(f"{self.ns}_step", 0)
        st.session_state.setdefault(f"{self.ns}_fin", False)
        st.session_state.setdefault(f"{self.ns}_hist", [])

        # Controls
        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3>Algorithm Controls</h3>', unsafe_allow_html=True)
        c1, c2, c3 = st.sidebar.columns(3)
        next_clicked = c1.button("Next", use_container_width=True, type="primary",
                                 disabled=st.session_state[f"{self.ns}_fin"])
        back_clicked = c2.button("Back", use_container_width=True, type="primary",
                                 disabled=len(st.session_state[f"{self.ns}_hist"]) <= 1)
        reset_clicked = c3.button("Reset", use_container_width=True, type="primary")

        manual = False
        if next_clicked:
            step_merge_sort(); push(); manual = True
        if back_clicked and len(st.session_state[f"{self.ns}_hist"]) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            restore(st.session_state[f"{self.ns}_hist"][-1]); manual = True
        if reset_clicked:
            init_state(); manual = True

        # Visualization
        st.markdown("---")
        st.markdown('<h2 class="section-header">Array Visualization</h2>', unsafe_allow_html=True)
        a = st.session_state[f"{self.ns}_a"]
        hi = st.session_state[f"{self.ns}_hilite"]  # now guaranteed to exist
        seg = hi.get("seg")
        left = hi.get("left")
        right = hi.get("right")

        fig, ax = plt.subplots(figsize=(12, 4))
        n = len(a)
        for idx, val in enumerate(a):
            fc = COLORS["unvisited"]
            if seg and seg[0] <= idx < seg[1]:
                fc = COLORS["current"]
            if left and left[0] <= idx < left[1]:
                fc = COLORS["source"]
            if right and right[0] <= idx < right[1]:
                fc = COLORS["visited"]
            if st.session_state[f"{self.ns}_fin"]:
                fc = COLORS["visited"]

            rect = Rectangle((idx, 0), .9, .8, facecolor=fc, edgecolor="#111", linewidth=2)
            ax.add_patch(rect)
            ax.text(idx + .45, .4, str(val), ha="center", va="center",
                    fontsize=12, fontweight="bold", color="white")
            ax.text(idx + .45, -.25, str(idx), ha="center", va="center",
                    fontsize=10, color="#d8b4fe")
        ax.set_xlim(-.2, max(6, n) + .2)
        ax.set_ylim(-.6, 1.3)
        ax.set_facecolor(COLORS["background"])
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # Explanation panel
        st.markdown("---")
        st.markdown('<h2 class="section-header">Step-by-Step Explanation</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-card">{st.session_state[f"{self.ns}_exp"]}</div>', unsafe_allow_html=True)
        if st.session_state[f"{self.ns}_fin"]:
            st.success("Sorting complete")

        # Auto-play
        if auto and not st.session_state[f"{self.ns}_fin"] and not manual:
            step_merge_sort(); push(); time.sleep(speed); st.rerun()