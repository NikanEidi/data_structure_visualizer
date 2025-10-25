import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import copy, random, time
from components.graphStyle import CSS, COLORS

SAMPLES = {
    "Sample 1 – Random": [9, 3, 7, 2, 5],
    "Sample 2 – Nearly Sorted": [1, 3, 4, 6, 5, 7],
    "Sample 3 – Reverse Sorted": [10, 8, 6, 4, 2]
}

CANON_CODE = """def insertion_sort(arr):
    for i in range(1, len(arr)):            # L1
        key = arr[i]                         # L2
        j = i - 1                            # L3
        while j >= 0 and arr[j] > key:       # L4
            arr[j + 1] = arr[j]              # L5
            j -= 1                            # L6
        arr[j + 1] = key                     # L7
    return arr                                # L8"""

def code_with_pointer(active_lines):
   
    lines = CANON_CODE.splitlines()
    out = []
    for ln in lines:
        tag = ln.split('#')[-1].strip() if '#' in ln else ""
        marker = "  ◀" if tag in active_lines else ""
        out.append(f"{ln}{marker}")
    return "<pre><code>" + "\n".join(out) + "</code></pre>"

class InsertionSortVisualizer:
    def __init__(self):
        self.ns = "ins"

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
            d = {
                "a": list(st.session_state[f"{self.ns}_a"]),
                "i": st.session_state[f"{self.ns}_i"],
                "j": st.session_state[f"{self.ns}_j"],
                "key": st.session_state[f"{self.ns}_key"],
                "phase": st.session_state[f"{self.ns}_phase"],
                "fin": st.session_state[f"{self.ns}_fin"],
                "step": st.session_state[f"{self.ns}_step"],
                "exp": st.session_state[f"{self.ns}_exp"]
            }
            st.session_state.setdefault(f"{self.ns}_hist", []).append(copy.deepcopy(d))

        def restore(s):
            for k, v in s.items():
                st.session_state[f"{self.ns}_{k}"] = copy.deepcopy(v)

        def finish(a):
            st.session_state[f"{self.ns}_fin"] = True
            st.session_state[f"{self.ns}_exp"] = (
                '<h3 class="step-header">Sorting Complete</h3>'
                + code_with_pointer({"L8"})
                + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Final array:</strong> <code>{a}</code></div>
  <div class="step-info-line"><strong>Loop invariant (prefix sorted):</strong> For every step k, the subarray <code>arr[0..k-1]</code> was sorted. When i passes the end, the whole array is sorted.</div>
</div>"""
            )

        def init_state():
            st.session_state[f"{self.ns}_akey"] = akey
            st.session_state[f"{self.ns}_a"] = list(arr)
            st.session_state[f"{self.ns}_i"] = 1
            st.session_state[f"{self.ns}_j"] = 0
            st.session_state[f"{self.ns}_key"] = arr[1] if len(arr) > 1 else None
            st.session_state[f"{self.ns}_phase"] = "start_i"  # marks entering the for-loop body
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_hist"] = []

            i = st.session_state[f"{self.ns}_i"]
            key = st.session_state[f"{self.ns}_key"]
            st.session_state[f"{self.ns}_exp"] = (
                '<h3 class="step-header">Initialization</h3>'
                + code_with_pointer({"L1","L2","L3"})
                + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Array:</strong> <code>{arr}</code></div>
  <div class="step-info-line"><strong>Start:</strong> The first element is considered sorted. We begin the loop with <code>i = 1</code>.</div>
  <div class="step-info-line"><strong>Key:</strong> <code>{key if key is not None else 'N/A'}</code> (the value we will insert into the sorted prefix).</div>
  <div class="step-info-line"><strong>Loop invariant:</strong> Before processing index <code>i</code>, <code>arr[0..i-1]</code> is sorted.</div>
</div>"""
            )
            push()

        def step_insertion():
            if st.session_state[f"{self.ns}_fin"]:
                return

            a = st.session_state[f"{self.ns}_a"]
            i = st.session_state[f"{self.ns}_i"]
            j = st.session_state[f"{self.ns}_j"]
            key = st.session_state[f"{self.ns}_key"]
            phase = st.session_state[f"{self.ns}_phase"]
            st.session_state[f"{self.ns}_step"] += 1

            if i >= len(a):
                return finish(a)

            if phase == "start_i":
                st.session_state[f"{self.ns}_phase"] = "compare"
                st.session_state[f"{self.ns}_j"] = i - 1
                st.session_state[f"{self.ns}_exp"] = (
                    f'<h3 class="step-header">Step {st.session_state[f"{self.ns}_step"]}: Pick key for position i={i}</h3>'
                    + code_with_pointer({"L2","L3"})
                    + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Set:</strong> <code>key = arr[{i}] = {a[i]}</code>, <code>j = {i-1}</code>.</div>
  <div class="step-info-line"><strong>Goal:</strong> Insert <code>key</code> into the correct place among <code>arr[0..{i-1}]</code> (which is sorted by invariant).</div>
</div>"""
                )

            elif phase == "compare":
                j = st.session_state[f"{self.ns}_j"]
                key = a[i] if key is None and i < len(a) else key  # safety
                if j >= 0 and a[j] > key:
                    st.session_state[f"{self.ns}_phase"] = "shift"
                    st.session_state[f"{self.ns}_exp"] = (
                        f'<h3 class="step-header">Step {st.session_state[f"{self.ns}_step"]}: Compare & decide to shift</h3>'
                        + code_with_pointer({"L4"})
                        + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Check:</strong> <code>j >= 0</code> and <code>arr[{j}]({a[j]}) &gt; key({key})</code> → <strong>TRUE</strong>.</div>
  <div class="step-info-line"><strong>Meaning:</strong> <code>{a[j]}</code> is too large to stay left of key; make space by shifting it right.</div>
  <div class="step-info-line"><strong>Invariant preserved:</strong> Shifting does not break the sorted order of <code>arr[0..{j}]</code>, it just duplicates <code>arr[{j}]</code> at <code>{j+1}</code> temporarily.</div>
</div>"""
                    )
                else:
                    st.session_state[f"{self.ns}_phase"] = "place"
                    cond = "Reached array start" if j < 0 else f"arr[{j}]({a[j]}) ≤ key({key})"
                    st.session_state[f"{self.ns}_exp"] = (
                        f'<h3 class="step-header">Step {st.session_state[f"{self.ns}_step"]}: Found insertion point</h3>'
                        + code_with_pointer({"L4","L7"})
                        + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Condition:</strong> {cond} → stop shifting.</div>
  <div class="step-info-line"><strong>Action:</strong> Place <code>key</code> at index <code>{j+1}</code>.</div>
  <div class="step-info-line"><strong>Why valid:</strong> All elements left of <code>{j+1}</code> are ≤ key, and all elements to the right (up to i-1) are &gt; key.</div>
</div>"""
                    )

            elif phase == "shift":
                j = st.session_state[f"{self.ns}_j"]
                a[j + 1] = a[j]
                st.session_state[f"{self.ns}_j"] = j - 1
                st.session_state[f"{self.ns}_phase"] = "compare"
                st.session_state[f"{self.ns}_exp"] = (
                    f'<h3 class="step-header">Step {st.session_state[f"{self.ns}_step"]}: Shift right</h3>'
                    + code_with_pointer({"L5","L6"})
                    + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Moved:</strong> <code>{a[j]}</code> from index <code>{j}</code> → <code>{j+1}</code>.</div>
  <div class="step-info-line"><strong>Update:</strong> <code>j = {j-1}</code>. Next, re-check the condition to see if more shifting is needed.</div>
  <div class="step-info-line"><strong>Invariant:</strong> The prefix excluding the hole where key will go remains sorted.</div>
</div>"""
                )

            elif phase == "place":
                j = st.session_state[f"{self.ns}_j"]
                a[j + 1] = key
                i += 1
                if i >= len(a):
                    return finish(a)
                st.session_state[f"{self.ns}_i"] = i
                st.session_state[f"{self.ns}_key"] = a[i]
                st.session_state[f"{self.ns}_j"] = i - 1
                st.session_state[f"{self.ns}_phase"] = "start_i"
                st.session_state[f"{self.ns}_exp"] = (
                    f'<h3 class="step-header">Step {st.session_state[f"{self.ns}_step"]}: Place key</h3>'
                    + code_with_pointer({"L7","L1"})
                    + f"""
<div class="step-info">
  <div class="step-info-line"><strong>Inserted:</strong> <code>{key}</code> at index <code>{j+1}</code>.</div>
  <div class="step-info-line"><strong>Prefix sorted:</strong> Now <code>arr[0..{i-1}]</code> is sorted.</div>
  <div class="step-info-line"><strong>Next iteration:</strong> <code>i = {i}</code>, <code>key = arr[{i}] = {a[i]}</code> (if exists).</div>
</div>"""
                )

      
        if f"{self.ns}_akey" not in st.session_state or st.session_state[f"{self.ns}_akey"] != akey:
            init_state()

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
            step_insertion(); push(); manual = True
        if back_clicked and len(st.session_state[f"{self.ns}_hist"]) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            restore(st.session_state[f"{self.ns}_hist"][-1]); manual = True
        if reset_clicked:
            init_state(); manual = True

  
        st.markdown("---")
        st.markdown('<h2 class="section-header">Array Visualization</h2>', unsafe_allow_html=True)
        a = st.session_state[f"{self.ns}_a"]
        i = st.session_state[f"{self.ns}_i"]
        j = st.session_state[f"{self.ns}_j"]
        phase = st.session_state[f"{self.ns}_phase"]

        fig, ax = plt.subplots(figsize=(12, 4))
        for idx, val in enumerate(a):
            if st.session_state[f"{self.ns}_fin"]:
                fc = COLORS["visited"]
            elif phase in ("shift",) and idx in (j, j + 1):
                fc = COLORS["source"]
            elif phase in ("compare", "start_i") and idx in (i, j):
                fc = COLORS["current"]
            elif phase == "place" and idx == j + 1:
                fc = COLORS["source"]
            elif idx < i:
                fc = COLORS["visited"]
            else:
                fc = COLORS["unvisited"]
            rect = Rectangle((idx, 0), .9, .8, facecolor=fc, edgecolor="#111", linewidth=2)
            ax.add_patch(rect)
            ax.text(idx + .45, .4, str(val), ha="center", va="center", fontsize=12, fontweight="bold", color="white")
            ax.text(idx + .45, -.25, str(idx), ha="center", va="center", fontsize=10, color="#d8b4fe")
        ax.set_xlim(-.2, max(6, len(a)) + .2)
        ax.set_ylim(-.6, 1.3)
        ax.set_facecolor(COLORS["background"])
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

      
        st.markdown("---")
        st.markdown('<h2 class="section-header">Step-by-Step Explanation</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="step-card">{st.session_state[f"{self.ns}_exp"]}</div>', unsafe_allow_html=True)
        if st.session_state[f"{self.ns}_fin"]:
            st.success("Sorting complete")


        if auto and not st.session_state[f"{self.ns}_fin"] and not manual:
            step_insertion(); push(); time.sleep(speed); st.rerun() 