import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import copy, random, time
from algorithms.graph.graphStyle import CSS, COLORS


SAMPLES = {
    "Sample 1": [7, 2, 6, 1, 9, 3, 5],
    "Sample 2": [10, 4, 8, 2, 14, 12, 6, 18],
    "Sample 3": [5, 1, 4, 2, 8, 0, 2]
}

class QuickSortVisualizer:
    def __init__(self):
        self.ns = "qs"

    def render(self):
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Quick Sort Visualization</h2>', unsafe_allow_html=True)

        mode = st.sidebar.radio("Input mode:", ["Use sample array", "Build your own"], key=f"{self.ns}_mode")
        if mode == "Use sample array":
            s = st.sidebar.selectbox("Select sample:", list(SAMPLES.keys()), key=f"{self.ns}_sample")
            arr = list(map(int, SAMPLES[s]))
            akey = f"sample::{s}"
        else:
            n = st.sidebar.slider("Number of elements", 2, 20, 7, key=f"{self.ns}_n")
            if f"{self.ns}_arr_seed" not in st.session_state or st.session_state[f"{self.ns}_arr_seed"] != n:
                st.session_state[f"{self.ns}_arr_list"] = [random.randint(0, 99) for _ in range(n)]
                st.session_state[f"{self.ns}_arr_seed"] = n
            df = pd.DataFrame({"Value": st.session_state[f"{self.ns}_arr_list"]})
            e = st.data_editor(df, num_rows="fixed", use_container_width=True, key=f"{self.ns}_editor")
            vals = [int(x) if str(x).strip().lstrip('-').isdigit() else 0 for x in e["Value"].tolist()]
            st.session_state[f"{self.ns}_arr_list"] = vals
            arr = list(vals)
            akey = f"custom::{','.join(map(str, arr))}"

        st.sidebar.markdown("---")
        auto = st.sidebar.checkbox("Enable Auto-Play", False, key=f"{self.ns}_auto")
        speed = st.sidebar.slider("Speed (seconds per step)", 0.2, 2.5, 0.9, 0.1, key=f"{self.ns}_speed")

        def push():
            snap = {
                "a": list(st.session_state[f"{self.ns}_a"]),
                "stack": list(st.session_state[f"{self.ns}_stack"]),
                "phase": st.session_state[f"{self.ns}_phase"],
                "lo": st.session_state[f"{self.ns}_lo"],
                "hi": st.session_state[f"{self.ns}_hi"],
                "i": st.session_state[f"{self.ns}_i"],
                "j": st.session_state[f"{self.ns}_j"],
                "pivot": st.session_state[f"{self.ns}_pivot"],
                "step": st.session_state[f"{self.ns}_step"],
                "exp": st.session_state[f"{self.ns}_exp"],
                "fixed": set(st.session_state[f"{self.ns}_fixed"]),
                "fin": st.session_state[f"{self.ns}_fin"]
            }
            st.session_state.setdefault(f"{self.ns}_hist", []).append(copy.deepcopy(snap))

        def restore(s):
            for k, v in s.items():
                st.session_state[f"{self.ns}_{k}"] = copy.deepcopy(v)

        def init_state():
            st.session_state[f"{self.ns}_akey"] = akey
            st.session_state[f"{self.ns}_a"] = list(arr)
            st.session_state[f"{self.ns}_stack"] = [(0, len(arr)-1)] if arr else []
            st.session_state[f"{self.ns}_phase"] = "start" if arr else "done"
            st.session_state[f"{self.ns}_lo"] = 0
            st.session_state[f"{self.ns}_hi"] = len(arr)-1
            st.session_state[f"{self.ns}_i"] = None
            st.session_state[f"{self.ns}_j"] = None
            st.session_state[f"{self.ns}_pivot"] = None
            st.session_state[f"{self.ns}_fixed"] = set()
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_hist"] = []
            full_code = """def quick_sort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1"""
            st.session_state[f"{self.ns}_exp"] = f"""
<h3>Step 0 — Initialization</h3>
<pre><code>{full_code}</code></pre>
<div class="step-info">
Array initialized: <code>{arr}</code><br>
Stack starts with full range [0, {len(arr)-1}].<br>
Algorithm uses divide-and-conquer to sort by recursively partitioning.
</div>"""
            push()

        def begin_partition():
            lo, hi = st.session_state[f"{self.ns}_stack"].pop()
            st.session_state[f"{self.ns}_lo"], st.session_state[f"{self.ns}_hi"] = lo, hi
            st.session_state[f"{self.ns}_pivot"] = st.session_state[f"{self.ns}_a"][hi]
            st.session_state[f"{self.ns}_i"] = lo - 1
            st.session_state[f"{self.ns}_j"] = lo
            st.session_state[f"{self.ns}_phase"] = "scan"
            full_code = """def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1"""
            st.session_state[f"{self.ns}_exp"] = f"""
<h3>Step {st.session_state[f"{self.ns}_step"]} — Begin Partition</h3>
<pre><code>{full_code}</code></pre>
<div class="step-info">
Pivot = <code>{st.session_state[f"{self.ns}_pivot"]}</code> chosen at index {hi}.<br>
Pointers start: i = {lo - 1}, j = {lo}.<br>
We will now move through the range [{lo}, {hi-1}] comparing each value to the pivot.
</div>"""

        def step_quick():
            if st.session_state[f"{self.ns}_fin"]: return
            st.session_state[f"{self.ns}_step"] += 1
            a = st.session_state[f"{self.ns}_a"]
            phase = st.session_state[f"{self.ns}_phase"]

            if phase == "start":
                if not st.session_state[f"{self.ns}_stack"]:
                    st.session_state[f"{self.ns}_fin"] = True
                    full_code = """def quick_sort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)"""
                    st.session_state[f"{self.ns}_exp"] = f"""
<h3>Final Step — Sorting Complete</h3>
<pre><code>{full_code}</code></pre>
<div class="step-info">
All partitions have been processed.<br>
Final sorted array: <code>{a}</code>
</div>"""
                else:
                    begin_partition()

            elif phase == "scan":
                j = st.session_state[f"{self.ns}_j"]
                hi = st.session_state[f"{self.ns}_hi"]
                lo = st.session_state[f"{self.ns}_lo"]
                p = st.session_state[f"{self.ns}_pivot"]
                i = st.session_state[f"{self.ns}_i"]
                full_code = """if arr[j] <= pivot:
    i += 1
    arr[i], arr[j] = arr[j], arr[i]
else:
    continue"""
                if j >= hi:
                    st.session_state[f"{self.ns}_phase"] = "pivot_swap"
                    st.session_state[f"{self.ns}_exp"] = f"""
<h3>Step {st.session_state[f"{self.ns}_step"]} — End of Scan</h3>
<pre><code>{full_code}</code></pre>
<div class="step-info">
Finished scanning elements in range [{lo}, {hi-1}].<br>
Now pivot = {p} will be placed in its correct position.
</div>"""
                else:
                    val = a[j]
                    if val <= p:
                        st.session_state[f"{self.ns}_i"] += 1
                        ni = st.session_state[f"{self.ns}_i"]
                        a[ni], a[j] = a[j], a[ni]
                        st.session_state[f"{self.ns}_exp"] = f"""
<h3>Step {st.session_state[f"{self.ns}_step"]} — Swap</h3>
<pre><code>{full_code}</code></pre>
<div class="step-info">
Compare arr[{j}] = {val} ≤ pivot({p}) → swap positions.<br>
Array becomes: <code>{a}</code>
</div>"""
                    else:
                        st.session_state[f"{self.ns}_exp"] = f"""
<h3>Step {st.session_state[f"{self.ns}_step"]} — No Swap</h3>
<pre><code>{full_code}</code></pre>
<div class="step-info">
Compare arr[{j}] = {val} > pivot({p}) → no swap.<br>
Array remains unchanged.
</div>"""
                    st.session_state[f"{self.ns}_j"] += 1

            elif phase == "pivot_swap":
                i = st.session_state[f"{self.ns}_i"]
                hi = st.session_state[f"{self.ns}_hi"]
                lo = st.session_state[f"{self.ns}_lo"]
                p = st.session_state[f"{self.ns}_pivot"]
                a[i + 1], a[hi] = a[hi], a[i + 1]
                pindex = i + 1
                st.session_state[f"{self.ns}_fixed"].add(pindex)
                st.session_state[f"{self.ns}_phase"] = "start"
                if pindex - 1 > lo:
                    st.session_state[f"{self.ns}_stack"].append((lo, pindex - 1))
                if pindex + 1 < hi:
                    st.session_state[f"{self.ns}_stack"].append((pindex + 1, hi))
                full_code = """arr[i + 1], arr[high] = arr[high], arr[i + 1]
return i + 1"""
                st.session_state[f"{self.ns}_exp"] = f"""
<h3>Step {st.session_state[f"{self.ns}_step"]} — Pivot Swap</h3>
<pre><code>{full_code}</code></pre>
<div class="step-info">
Pivot {p} placed correctly at index {pindex}.<br>
Left subarray: [{lo}, {pindex-1}]<br>
Right subarray: [{pindex+1}, {hi}]<br>
New subranges added to stack.
</div>"""

        if f"{self.ns}_akey" not in st.session_state or st.session_state[f"{self.ns}_akey"] != akey:
            init_state()

        st.sidebar.markdown("---")
        c1, c2, c3 = st.sidebar.columns(3)
        next_clicked = c1.button("Next", use_container_width=True, type="primary",
                                 disabled=st.session_state[f"{self.ns}_fin"])
        back_clicked = c2.button("Back", use_container_width=True, type="primary",
                                 disabled=len(st.session_state.get(f"{self.ns}_hist", [])) <= 1)
        reset_clicked = c3.button("Reset", use_container_width=True, type="primary")

        manual = False
        if next_clicked:
            step_quick(); push(); manual = True
        if back_clicked and len(st.session_state[f"{self.ns}_hist"]) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            restore(st.session_state[f"{self.ns}_hist"][-1]); manual = True
        if reset_clicked:
            init_state(); manual = True

        st.markdown("---")
        st.markdown('<h2 class="section-header">Array Visualization</h2>', unsafe_allow_html=True)
        a = st.session_state[f"{self.ns}_a"]
        lo, hi = st.session_state[f"{self.ns}_lo"], st.session_state[f"{self.ns}_hi"]
        i, j = st.session_state[f"{self.ns}_i"], st.session_state[f"{self.ns}_j"]
        phase = st.session_state[f"{self.ns}_phase"]
        fixed = st.session_state[f"{self.ns}_fixed"]

        fig, ax = plt.subplots(figsize=(12, 3.2))
        for idx, val in enumerate(a):
            if idx in fixed:
                fc = COLORS["visited"]
            elif phase in ("scan", "pivot_swap") and lo <= idx <= hi and idx == hi:
                fc = COLORS["source"]
            elif phase == "scan" and idx == j:
                fc = COLORS["current"]
            else:
                fc = COLORS["unvisited"]
            rect = Rectangle((idx, 0), 0.95, 0.8, facecolor=fc, edgecolor="#111", linewidth=2)
            ax.add_patch(rect)
            ax.text(idx + 0.475, 0.4, str(val), ha="center", va="center", fontsize=12, color="white", fontweight="bold")
            ax.text(idx + 0.475, -0.25, str(idx), ha="center", va="center", fontsize=10, color="#d8b4fe")
        ax.set_xlim(-0.2, max(6, len(a)) + 0.2)
        ax.set_ylim(-0.6, 1.2)
        ax.set_facecolor(COLORS["background"])
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown("---")
        st.markdown('<h2 class="section-header">Step-by-Step Explanation</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-card">{st.session_state[f"{self.ns}_exp"]}</div>', unsafe_allow_html=True)
        if st.session_state[f"{self.ns}_fin"]:
            st.success("Quick Sort Complete!")

        if auto and not st.session_state[f"{self.ns}_fin"] and not manual:
            step_quick(); push(); time.sleep(speed); st.rerun() 