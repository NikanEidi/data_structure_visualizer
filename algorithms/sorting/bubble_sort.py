import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import copy, random, time

from ...components.graphStyle import CSS, COLORS  

SAMPLES = {
    "Sample 1 – Nearly Sorted With Tail": [1, 2, 3, 4, 5, 6, 7, 2],
    "Sample 2 – Reverse With Duplicates": [9, 9, 7, 7, 5, 3, 3, 1],
    "Sample 3 – Mixed Range (Negatives)": [4, -2, 0, 11, -5, 4, 8, -1],
}

PSEUDOCODE = """\
def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""

class BubbleSortVisualizer:
    def __init__(self):
        self.ns = "bs"

    def render(self):
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Bubble Sort</h2>', unsafe_allow_html=True)

        # Input configuration
        mode = st.sidebar.radio("Input mode:", ["Use sample array", "Build your own"], key=f"{self.ns}_mode")
        if mode == "Use sample array":
            sample = st.sidebar.selectbox("Select sample:", list(SAMPLES.keys()), key=f"{self.ns}_sample")
            arr = list(map(int, SAMPLES[sample]))
            akey = f"sample::{sample}"
        else:
            n = st.sidebar.slider("Number of elements", 2, 24, 8, key=f"{self.ns}_n")
            if f"{self.ns}_arr_seed" not in st.session_state or st.session_state[f"{self.ns}_arr_seed"] != n:
                st.session_state[f"{self.ns}_arr_list"] = [random.randint(-20, 20) for _ in range(n)]
                st.session_state[f"{self.ns}_arr_seed"] = n
            df = pd.DataFrame({"Value": st.session_state[f"{self.ns}_arr_list"]})
            edited = st.data_editor(df, num_rows="fixed", use_container_width=True, key=f"{self.ns}_editor")
            vals = [int(x) if str(x).lstrip("-").isdigit() else 0 for x in edited["Value"].tolist()]
            arr = list(vals)
            st.session_state[f"{self.ns}_arr_list"] = arr
            akey = f"custom::{','.join(map(str, arr))}"

        st.sidebar.markdown("---")
        auto = st.sidebar.checkbox("Auto-Play", value=False, key=f"{self.ns}_auto")
        speed = st.sidebar.slider("Speed (sec/step)", 0.2, 2.5, 0.7, 0.1, key=f"{self.ns}_speed")

        # --- Helpers ---
        def ns(key): return f"{self.ns}_{key}"

        def push():
            st.session_state[ns("hist")].append(copy.deepcopy({
                "a": list(st.session_state[ns("a")]),
                "i": st.session_state[ns("i")],
                "j": st.session_state[ns("j")],
                "fin": st.session_state[ns("fin")],
                "step": st.session_state[ns("step")],
                "exp": st.session_state[ns("exp")],
                "last_swap": st.session_state[ns("last_swap")],
            }))

        def restore(s):
            st.session_state[ns("a")] = list(s["a"])
            st.session_state[ns("i")] = int(s["i"])
            st.session_state[ns("j")] = int(s["j"])
            st.session_state[ns("fin")] = bool(s["fin"])
            st.session_state[ns("step")] = int(s["step"])
            st.session_state[ns("exp")] = s["exp"]
            st.session_state[ns("last_swap")] = s["last_swap"]

        def init_state():
            st.session_state[ns("akey")] = akey
            st.session_state[ns("a")] = list(arr)
            st.session_state[ns("i")] = 0
            st.session_state[ns("j")] = 0
            st.session_state[ns("last_swap")] = None
            st.session_state[ns("fin")] = False
            st.session_state[ns("step")] = 0
            st.session_state[ns("hist")] = []
            st.session_state[ns("exp")] = f"""
<h3 class="step-header">[INITIALIZATION]</h3>
<div class="step-info">
  <strong>Array:</strong> <code>{arr}</code><br>
  <strong>n = len(arr):</strong> <code>{len(arr)}</code><br>
  Each outer pass moves the largest unsorted value to the right end.
</div>
"""
            push()

        # --- Core algorithm logic ---
        def step_bubble():
            if st.session_state[ns("fin")]:
                return
            a = st.session_state[ns("a")]
            n = len(a)
            i = st.session_state[ns("i")]
            j = st.session_state[ns("j")]

            if i >= n - 1:
                st.session_state[ns("fin")] = True
                st.session_state[ns("exp")] = f"""
<h3 class="completed-text">✓ Sorting Complete</h3>
<div class="step-info"><strong>Final Array:</strong> <code>{a}</code></div>"""
                return

            j_max = n - 2 - i
            if j > j_max:
                i += 1
                j = 0
                st.session_state[ns("i")] = i
                st.session_state[ns("j")] = j
                st.session_state[ns("step")] += 1
                st.session_state[ns("exp")] = f"""
<h3 class="step-header">Pass {i} Completed</h3>
<div class="step-info">
  Largest element bubbled to position <code>{n - 1 - (i - 1)}</code>.
  Next pass will ignore last {i} element(s).
</div>"""
                return

            val_j, val_next = a[j], a[j + 1]
            st.session_state[ns("step")] += 1
            swapped = False
            if val_j > val_next:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                st.session_state[ns("last_swap")] = (j, j + 1)
            else:
                st.session_state[ns("last_swap")] = None

            st.session_state[ns("a")] = a
            st.session_state[ns("i")] = i
            st.session_state[ns("j")] = j + 1

            result_line = "Swap" if swapped else "No Swap"
            rationale = """
<div class="step-info">
  <strong>Why i range(n-1):</strong> Each pass fixes one largest element.<br>
  <strong>Why j range(n-1-i):</strong> Skip already fixed largest elements.<br>
  <strong>Condition arr[j] > arr[j+1]:</strong> Swaps out-of-order adjacent values.
</div>"""

            st.session_state[ns("exp")] = f"""
<h3 class="step-header">Step {st.session_state[ns("step")]}</h3>
<pre><code>{PSEUDOCODE}</code></pre>
<div class="step-info">
  <strong>Compare:</strong> arr[{j}] = {val_j}  vs  arr[{j + 1}] = {val_next}<br>
  <strong>Decision:</strong> {result_line}<br>
  <strong>Array:</strong> <code>{a}</code>
</div>
<h3>Explanation</h3>
{rationale}
"""

        
        if ns("akey") not in st.session_state:
            init_state()
        elif st.session_state[ns("akey")] != akey:
            init_state()

        
        st.sidebar.markdown("---")
        st.sidebar.markdown('<h3>Algorithm Controls</h3>', unsafe_allow_html=True)
        c1, c2, c3 = st.sidebar.columns(3)
        next_clicked = c1.button("Next", use_container_width=True, type="primary", disabled=st.session_state[ns("fin")])
        back_clicked = c2.button("Back", use_container_width=True, type="primary", disabled=len(st.session_state[ns("hist")]) <= 1)
        reset_clicked = c3.button("Reset", use_container_width=True, type="primary")

        manual = False
        if next_clicked:
            step_bubble(); push(); manual = True
        if back_clicked and len(st.session_state[ns("hist")]) > 1:
            st.session_state[ns("hist")].pop()
            restore(st.session_state[ns("hist")][-1])
            manual = True
        if reset_clicked:
            init_state(); manual = True

        
        st.markdown("---")
        st.markdown('<h2 class="section-header">Array Visualization</h2>', unsafe_allow_html=True)
        a = st.session_state[ns("a")]
        n = len(a)
        i = st.session_state[ns("i")]
        j = st.session_state[ns("j")]
        last_swap = st.session_state[ns("last_swap")]

        fig, ax = plt.subplots(figsize=(12, 4.2))
        vmin, vmax = (min(a), max(a)) if a else (0, 1)
        rng = vmax - vmin if vmax != vmin else 1

        for idx, val in enumerate(a):
            if last_swap and idx in last_swap:
                fc = COLORS["source"]       # purple highlight for swap
            elif not st.session_state[ns("fin")] and (idx == j or idx == min(j + 1, n - 1)):
                fc = COLORS["current"]      # amber = current comparison
            elif idx >= n - i:
                fc = COLORS["visited"]      # green = sorted portion
            else:
                base = (val - vmin) / rng
                fc = plt.cm.Blues(0.35 + 0.45 * base)
            h = max(0.05, (val - vmin) / rng)
            rect = Rectangle((idx, 0), 0.9, h, facecolor=fc, edgecolor="#0f172a", linewidth=2)
            ax.add_patch(rect)
            ax.text(idx + 0.45, h + 0.05, str(val), ha="center", va="bottom", fontsize=11, color="white", fontweight="bold")
            ax.text(idx + 0.45, -0.12, str(idx), ha="center", va="top", fontsize=10, color="#94a3b8")

        ax.set_xlim(-0.2, max(8, n) + 0.2)
        ax.set_ylim(-0.35, 1.6)
        ax.set_facecolor(COLORS["background"])
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

       
        st.markdown("---")
        st.markdown('<h2 class="section-header">Step-by-Step Explanation</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-card">{st.session_state[ns("exp")]}</div>', unsafe_allow_html=True)
        if st.session_state[ns("fin")]:
            st.success("Sorting complete!")

       
        if auto and not st.session_state[ns("fin")] and not manual:
            step_bubble(); push(); time.sleep(speed); st.rerun() 