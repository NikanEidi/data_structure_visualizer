import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import copy, random, time
from components.graphStyle import CSS, COLORS

SAMPLES = {
    "Sample 1": [1, 3, 5, 7, 9, 11, 13, 15],
    "Sample 2": [2, 4, 6, 8, 10, 12, 14, 16, 18],
    "Sample 3": [5, 5, 5, 6, 7, 8, 9, 12]
}

PSEUDOCODE = """\
def binary_search(arr, target):
    lo, hi = 0, len(arr)-1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
"""

class BinarySearchVisualizer:
    def __init__(self):
        self.ns = "bin"

    def render(self):
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Binary Search (Sorted Array)</h2>', unsafe_allow_html=True)

        mode = st.sidebar.radio("Input mode:", ["Use sample array", "Build your own"], key=f"{self.ns}_mode")
        if mode == "Use sample array":
            sample = st.sidebar.selectbox("Select sample:", list(SAMPLES.keys()), key=f"{self.ns}_sample")
            base = SAMPLES[sample]
            arr = sorted(list(map(int, base)))
            akey = f"sample::{sample}"
        else:
            n = st.sidebar.slider("Number of elements", 2, 20, 8, key=f"{self.ns}_n")
            if f"{self.ns}_arr_seed" not in st.session_state or st.session_state[f"{self.ns}_arr_seed"] != n:
                st.session_state[f"{self.ns}_arr_list"] = sorted([random.randint(0, 99) for _ in range(n)])
                st.session_state[f"{self.ns}_arr_seed"] = n
            df = pd.DataFrame({"Value": st.session_state[f"{self.ns}_arr_list"]})
            edited = st.data_editor(df, num_rows="fixed", use_container_width=True, key=f"{self.ns}_editor")
            vals = []
            for x in edited["Value"].tolist():
                try:
                    vals.append(int(x))
                except:
                    vals.append(0)
            arr = sorted(vals)
            st.session_state[f"{self.ns}_arr_list"] = arr
            akey = f"custom::{','.join(map(str, arr))}"

        st.sidebar.markdown("---")
        # IMPORTANT: we never assign to this key ourselves (to avoid Streamlit mutation error)
        st.sidebar.number_input("Target", value=6, step=1, key=f"{self.ns}_target")

        st.sidebar.markdown("---")
        auto = st.sidebar.checkbox("Auto-Play", value=False, key=f"{self.ns}_auto")
        speed = st.sidebar.slider("Speed (sec/step)", 0.3, 2.5, 0.9, 0.1, key=f"{self.ns}_speed")

        def push():
            st.session_state[f"{self.ns}_hist"].append(copy.deepcopy({
                "lo": st.session_state[f"{self.ns}_lo"],
                "hi": st.session_state[f"{self.ns}_hi"],
                "mid": st.session_state[f"{self.ns}_mid"],
                "found": st.session_state[f"{self.ns}_found"],
                "fin": st.session_state[f"{self.ns}_fin"],
                "step": st.session_state[f"{self.ns}_step"],
                "exp": st.session_state[f"{self.ns}_exp"],
                "dead": list(st.session_state[f"{self.ns}_dead"]),
            }))

        def restore(s):
            st.session_state[f"{self.ns}_lo"] = s["lo"]
            st.session_state[f"{self.ns}_hi"] = s["hi"]
            st.session_state[f"{self.ns}_mid"] = s["mid"]
            st.session_state[f"{self.ns}_found"] = s["found"]
            st.session_state[f"{self.ns}_fin"] = s["fin"]
            st.session_state[f"{self.ns}_step"] = s["step"]
            st.session_state[f"{self.ns}_exp"] = s["exp"]
            st.session_state[f"{self.ns}_dead"] = list(s["dead"])

        def step_text(title, body_html):
            return f"""
<div class="step-card">
  <div class="step-header">{title}</div>
  <pre><code>{PSEUDOCODE}</code></pre>
  {body_html}
</div>
"""

        def init_state():
            arr_val = list(arr)
            target_val = int(st.session_state.get(f"{self.ns}_target", 6))
            st.session_state[f"{self.ns}_arr"] = arr_val
            st.session_state[f"{self.ns}_akey"] = akey + f"::t={target_val}"
            st.session_state[f"{self.ns}_lo"] = 0
            st.session_state[f"{self.ns}_hi"] = len(arr_val) - 1
            st.session_state[f"{self.ns}_mid"] = None
            st.session_state[f"{self.ns}_found"] = None
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_dead"] = []
            st.session_state[f"{self.ns}_exp"] = step_text(
                "[INITIALIZATION]",
                f"""
<div class="step-info">
  <strong>Array:</strong> <code>{arr_val}</code><br>
  <strong>Target:</strong> <code>{target_val}</code><br>
  <strong>Range:</strong> <code>lo = 0</code>, <code>hi = {len(arr_val)-1}</code>
</div>
"""
            )
            push()

        def step_binary():
            if st.session_state[f"{self.ns}_fin"]:
                return

            a = st.session_state[f"{self.ns}_arr"]
            t = int(st.session_state.get(f"{self.ns}_target", 6))
            lo = st.session_state[f"{self.ns}_lo"]
            hi = st.session_state[f"{self.ns}_hi"]

            if lo > hi:
                st.session_state[f"{self.ns}_fin"] = True
                st.session_state[f"{self.ns}_step"] += 1
                st.session_state[f"{self.ns}_exp"] = step_text(
                    "✓ Search Completed",
                    "<div class='completed-text'>Target not found.</div>"
                )
                return

            mid = (lo + hi) // 2
            val = a[mid]
            st.session_state[f"{self.ns}_mid"] = mid
            st.session_state[f"{self.ns}_step"] += 1

            if val == t:
                st.session_state[f"{self.ns}_found"] = mid
                st.session_state[f"{self.ns}_fin"] = True
                body = f"""
<div class="step-info">
  <strong>Range:</strong> lo = {lo}, hi = {hi}<br>
  <strong>Mid:</strong> mid = {mid}, arr[mid] = {val}<br>
  <strong>Compare:</strong> {val} == {t}<br>
  <strong>Decision:</strong> Found target at index <code>{mid}</code>.
</div>
"""
                st.session_state[f"{self.ns}_exp"] = step_text("✓ Target Found", body)
                return

            if val < t:
                st.session_state[f"{self.ns}_dead"].extend(range(lo, mid + 1))
                st.session_state[f"{self.ns}_lo"] = mid + 1
                body = f"""
<div class="step-info">
  <strong>Range:</strong> lo = {lo}, hi = {hi}<br>
  <strong>Mid:</strong> mid = {mid}, arr[mid] = {val}<br>
  <strong>Compare:</strong> {val} &lt; {t}<br>
  <strong>Decision:</strong> Move right.<br>
  <strong>Next Range:</strong> lo = {mid + 1}, hi = {hi}
</div>
"""
                st.session_state[f"{self.ns}_exp"] = step_text(f"Step {st.session_state[f'{self.ns}_step']}", body)
            else:
                st.session_state[f"{self.ns}_dead"].extend(range(mid, hi + 1))
                st.session_state[f"{self.ns}_hi"] = mid - 1
                body = f"""
<div class="step-info">
  <strong>Range:</strong> lo = {lo}, hi = {hi}<br>
  <strong>Mid:</strong> mid = {mid}, arr[mid] = {val}<br>
  <strong>Compare:</strong> {val} &gt; {t}<br>
  <strong>Decision:</strong> Move left.<br>
  <strong>Next Range:</strong> lo = {lo}, hi = {mid - 1}
</div>
"""
                st.session_state[f"{self.ns}_exp"] = step_text(f"Step {st.session_state[f'{self.ns}_step']}", body)

        if f"{self.ns}_akey" not in st.session_state:
            init_state()
        else:
            current_key = akey + f"::t={int(st.session_state.get(f'{self.ns}_target', 6))}"
            if st.session_state[f"{self.ns}_akey"] != current_key:
                init_state()

        st.sidebar.markdown("---")
        c1, c2, c3 = st.sidebar.columns(3)
        next_clicked = c1.button("Next", use_container_width=True, type="primary", disabled=st.session_state[f"{self.ns}_fin"])
        back_clicked = c2.button("Back", use_container_width=True, type="primary", disabled=len(st.session_state[f"{self.ns}_hist"]) <= 1)
        reset_clicked = c3.button("Reset", use_container_width=True, type="primary")

        if next_clicked:
            step_binary(); push()
        if back_clicked and len(st.session_state[f"{self.ns}_hist"]) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            restore(st.session_state[f"{self.ns}_hist"][-1])
        if reset_clicked:
            init_state()

        st.markdown("---")
        st.markdown('<h2 class="section-header">Array Visualization</h2>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(12, 3.2))
        a = st.session_state[f"{self.ns}_arr"]
        lo = st.session_state[f"{self.ns}_lo"]
        hi = st.session_state[f"{self.ns}_hi"]
        mid = st.session_state[f"{self.ns}_mid"]
        found = st.session_state[f"{self.ns}_found"]
        dead = set(st.session_state[f"{self.ns}_dead"])

        for idx, val in enumerate(a):
            if found is not None and idx == found:
                fc = COLORS["source"]         # purple = found
            elif mid is not None and idx == mid and not st.session_state[f"{self.ns}_fin"]:
                fc = COLORS["current"]        # amber = current mid
            elif idx < lo or idx > hi or idx in dead:
                fc = "#4b5563"                # dark gray = eliminated
            else:
                fc = COLORS["visited"]        # green = active range
            rect = Rectangle((idx, 0), 0.95, 0.8, facecolor=fc, edgecolor=COLORS["text_primary"], linewidth=2)
            ax.add_patch(rect)
            ax.text(idx + 0.475, 0.4, str(val), ha="center", va="center", fontsize=13, color="white", fontweight="bold")
            ax.text(idx + 0.475, -0.25, str(idx), ha="center", va="center", fontsize=11, color="#cbd5e1")

        ax.set_xlim(-0.2, max(6, len(a)) + 0.2)
        ax.set_ylim(-0.7, 1.3)
        ax.set_facecolor(COLORS["background"])
        ax.axis("off")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown("---")
        st.markdown('<h2 class="section-header">Step-by-Step Explanation</h2>', unsafe_allow_html=True)
        st.markdown(st.session_state[f"{self.ns}_exp"], unsafe_allow_html=True)

        if st.session_state[f"{self.ns}_fin"]:
            if st.session_state[f"{self.ns}_found"] is not None:
                st.success(f"Found at index {st.session_state[f'{self.ns}_found']}.")
            else:
                st.error("Target not found.")

        if auto and not st.session_state[f"{self.ns}_fin"]:
            step_binary(); push(); time.sleep(st.session_state[f"{self.ns}_speed"]); st.rerun() 