import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import copy, random, time

from ..graph.graphStyle import CSS, COLORS 

SAMPLES = {
    "A1": [7, 2, 6, 1, 9, 4],
    "A2": [1, 1, 2, 3, 5, 8],
    "A3": [10, 20, 30, 40, 50],
    "A4": [5, 5, 5, 5],
    "A5": [-3, -1, 0, 2, 2, 9],
}

PSEUDOCODE = """\
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
"""

class LinearSearchVisualizer:
    def __init__(self):
        self.ns = "lin"

    def render(self):
        st.markdown(CSS, unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Linear Search</h2>', unsafe_allow_html=True)

        mode = st.sidebar.radio("Input mode:", ["Use sample array", "Build your own"], key=f"{self.ns}_mode")

        if mode == "Use sample array":
            sample = st.sidebar.selectbox("Select sample:", list(SAMPLES.keys()), key=f"{self.ns}_sample")
            base = SAMPLES[sample]
            arr = list(map(int, base))
            akey = f"sample::{sample}"
        else:
            n = st.sidebar.slider("Number of elements", 2, 20, 7, key=f"{self.ns}_n")
            if f"{self.ns}_arr_seed" not in st.session_state or st.session_state[f"{self.ns}_arr_seed"] != n:
                st.session_state[f"{self.ns}_arr_list"] = [random.randint(-9, 99) for _ in range(n)]
                st.session_state[f"{self.ns}_arr_seed"] = n
            df = pd.DataFrame({"Value": st.session_state[f"{self.ns}_arr_list"]})
            edited = st.data_editor(df, num_rows="fixed", use_container_width=True, key=f"{self.ns}_editor")
            vals = []
            for x in edited["Value"].tolist():
                try:
                    vals.append(int(x))
                except:
                    vals.append(0)
            arr = list(vals)
            st.session_state[f"{self.ns}_arr_list"] = arr
            akey = f"custom::{','.join(map(str, arr))}"

        st.sidebar.markdown("---")
        st.sidebar.number_input("Target", value=6, step=1, key=f"{self.ns}_target")  # do NOT overwrite this key elsewhere

        st.sidebar.markdown("---")
        auto = st.sidebar.checkbox("Auto-Play", value=False, key=f"{self.ns}_auto")
        speed = st.sidebar.slider("Speed (sec/step)", 0.3, 2.5, 0.9, 0.1, key=f"{self.ns}_speed")

        def step_card(title, body_html):
            return f"""
<div class="step-card">
  <div class="step-header">{title}</div>
  <pre><code>{PSEUDOCODE}</code></pre>
  {body_html}
</div>
"""

        def push():
            st.session_state[f"{self.ns}_hist"].append(copy.deepcopy({
                "i": st.session_state[f"{self.ns}_i"],
                "checked": list(st.session_state[f"{self.ns}_checked"]),
                "found": st.session_state[f"{self.ns}_found"],
                "fin": st.session_state[f"{self.ns}_fin"],
                "step": st.session_state[f"{self.ns}_step"],
                "exp": st.session_state[f"{self.ns}_exp"],
            }))

        def restore(s):
            st.session_state[f"{self.ns}_i"] = s["i"]
            st.session_state[f"{self.ns}_checked"] = list(s["checked"])
            st.session_state[f"{self.ns}_found"] = s["found"]
            st.session_state[f"{self.ns}_fin"] = s["fin"]
            st.session_state[f"{self.ns}_step"] = s["step"]
            st.session_state[f"{self.ns}_exp"] = s["exp"]

        def init_state():
            arr_val = list(arr)
            target_val = int(st.session_state.get(f"{self.ns}_target", 6))
            st.session_state[f"{self.ns}_arr"] = arr_val
            st.session_state[f"{self.ns}_akey"] = akey + f"::t={target_val}"
            st.session_state[f"{self.ns}_i"] = 0
            st.session_state[f"{self.ns}_checked"] = []
            st.session_state[f"{self.ns}_found"] = None
            st.session_state[f"{self.ns}_fin"] = False
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_hist"] = []
            st.session_state[f"{self.ns}_exp"] = step_card(
                "[INITIALIZATION]",
                f"""
<div class="step-info">
  <strong>Array:</strong> <code>{arr_val}</code><br>
  <strong>Target:</strong> <code>{target_val}</code><br>
  <strong>Start:</strong> <code>i = 0</code>
</div>
"""
            )
            push()

        def step_linear():
            if st.session_state[f"{self.ns}_fin"]:
                return

            a = st.session_state[f"{self.ns}_arr"]
            t = int(st.session_state.get(f"{self.ns}_target", 6))
            i = st.session_state[f"{self.ns}_i"]

            if i >= len(a):
                st.session_state[f"{self.ns}_fin"] = True
                st.session_state[f"{self.ns}_step"] += 1
                st.session_state[f"{self.ns}_exp"] = step_card(
                    "✓ Search Completed",
                    "<div class='completed-text'>Target not found.</div>"
                )
                return

            st.session_state[f"{self.ns}_step"] += 1

            if a[i] == t:
                st.session_state[f"{self.ns}_found"] = i
                st.session_state[f"{self.ns}_fin"] = True
                st.session_state[f"{self.ns}_checked"].append(i)
                body = f"""
<div class="step-info">
  <strong>Index:</strong> i = {i}<br>
  <strong>Value:</strong> arr[{i}] = {a[i]}<br>
  <strong>Compare:</strong> {a[i]} == {t}<br>
  <strong>Decision:</strong> Found at index <code>{i}</code>.
</div>
"""
                st.session_state[f"{self.ns}_exp"] = step_card("✓ Target Found", body)
            else:
                st.session_state[f"{self.ns}_checked"].append(i)
                st.session_state[f"{self.ns}_i"] = i + 1
                body = f"""
<div class="step-info">
  <strong>Index:</strong> i = {i}<br>
  <strong>Value:</strong> arr[{i}] = {a[i]}<br>
  <strong>Compare:</strong> {a[i]} != {t}<br>
  <strong>Decision:</strong> Move to next index <code>{i + 1}</code>.
</div>
"""
                st.session_state[f"{self.ns}_exp"] = step_card(f"Step {st.session_state[f'{self.ns}_step']}", body)

        # init / re-init when array or target changes
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
            step_linear(); push()
        if back_clicked and len(st.session_state[f"{self.ns}_hist"]) > 1:
            st.session_state[f"{self.ns}_hist"].pop()
            restore(st.session_state[f"{self.ns}_hist"][-1])
        if reset_clicked:
            init_state()

        st.markdown("---")
        st.markdown('<h2 class="section-header">Array Visualization</h2>', unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(12, 2.9))
        a = st.session_state[f"{self.ns}_arr"]
        found = st.session_state[f"{self.ns}_found"]
        i = st.session_state[f"{self.ns}_i"]
        fin = st.session_state[f"{self.ns}_fin"]
        checked = set(st.session_state[f"{self.ns}_checked"])

        for idx, val in enumerate(a):
            if found is not None and idx == found:
                fc = COLORS["source"]          # purple = found
            elif (idx == i) and (not fin) and (i < len(a)):
                fc = COLORS["current"]         # amber = current index
            elif idx in checked:
                fc = COLORS["visited"]         # green = checked
            else:
                fc = COLORS["unvisited"]       # dark gray = untouched

            rect = Rectangle((idx, 0), 0.95, 0.8, facecolor=fc, edgecolor=COLORS["text_primary"], linewidth=2)
            ax.add_patch(rect)
            ax.text(idx + 0.475, 0.4, str(val), ha="center", va="center",
                    fontsize=13, color="white", fontweight="bold")
            ax.text(idx + 0.475, -0.25, str(idx), ha="center", va="center",
                    fontsize=11, color="#cbd5e1")

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
            step_linear(); push(); time.sleep(st.session_state[f"{self.ns}_speed"]); st.rerun() 