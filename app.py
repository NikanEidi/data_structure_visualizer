import sys
from pathlib import Path
import importlib
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Data Structure Visualizer",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.styles import load_custom_css
load_custom_css()

from components.sidebar import render_sidebar

st.markdown('<h1 class="main-title">Data Structure Visualizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Interactive visualization of algorithms with step-by-step explanations</p>', unsafe_allow_html=True)

category, algorithm, *_ = render_sidebar()

def clear_algorithm_state():
    prefixes = ("bfs_", "dfs_", "dijkstra_", "linear_", "binary_", "bubble_", "insertion_", "merge_", "quick_")
    for k in list(st.session_state.keys()):
        if any(k.startswith(p) for p in prefixes):
            del st.session_state[k]

selection = f"{category}::{algorithm}"
if st.session_state.get("_last_selection") != selection:
    clear_algorithm_state()
    st.session_state["_last_selection"] = selection

routes = {
    ("Graph Algorithms", "BFS"): ("algorithms.graph.bfs", "BFSVisualizer"),
    ("Graph Algorithms", "DFS"): ("algorithms.graph.dfs", "DFSVisualizer"),
    ("Graph Algorithms", "Dijkstra"): ("algorithms.graph.dijkstra", "DijkstraVisualizer"),
    ("Sorting Algorithms", "Bubble Sort"): ("algorithms.sorting.bubble_sort", "BubbleSortVisualizer"),
    ("Sorting Algorithms", "Insertion Sort"): ("algorithms.sorting.insertion_sort", "InsertionSortVisualizer"),
    ("Sorting Algorithms", "Merge Sort"): ("algorithms.sorting.merge_sort", "MergeSortVisualizer"),
    ("Sorting Algorithms", "Quick Sort"): ("algorithms.sorting.quick_sort", "QuickSortVisualizer"),
    ("Searching Algorithms", "Linear Search"): ("algorithms.searching.linear_search", "LinearSearchVisualizer"),
    ("Searching Algorithms", "Binary Search"): ("algorithms.searching.binary_search", "BinarySearchVisualizer"),
}

mod_path, cls_name = routes.get((category, algorithm), (None, None))
if not mod_path:
    st.error("No visualizer found for this selection.")
else:
    try:
        module = importlib.import_module(mod_path)
        cls = getattr(module, cls_name)
        cls().render()
    except Exception as e:
        st.error(f"Failed to load visualizer: {e}")