

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Data Structure Visualizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    from components.styles import load_custom_css
    load_custom_css()
except Exception:
    pass

from components.sidebar import render_sidebar

st.markdown('<h1 class="main-title">Data Structure Visualizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Interactive visualization of algorithms with step-by-step explanations</p>', unsafe_allow_html=True)

category, algorithm = render_sidebar()

current_selection = f"{category}_{algorithm}"
if "last_selection" not in st.session_state:
    st.session_state.last_selection = current_selection
elif st.session_state.last_selection != current_selection:
    st.session_state.last_selection = current_selection

if category == "Graph Algorithms":
    if algorithm == "BFS":
        from algorithms.graph.bfs import BFSVisualizer
        BFSVisualizer().render()
    elif algorithm == "DFS":
        from algorithms.graph.dfs import DFSVisualizer
        DFSVisualizer().render()
    elif algorithm == "Dijkstra":
        from algorithms.graph.dijkstra import DijkstraVisualizer
        DijkstraVisualizer().render()

elif category == "Sorting Algorithms":
    if algorithm == "Bubble Sort":
        from algorithms.sorting.bubble_sort import BubbleSortVisualizer
        BubbleSortVisualizer().render()
    elif algorithm == "Insertion Sort":
        from algorithms.sorting.insertion_sort import InsertionSortVisualizer
        InsertionSortVisualizer().render()
    elif algorithm == "Merge Sort":
        from algorithms.sorting.merge_sort import MergeSortVisualizer
        MergeSortVisualizer().render()
    elif algorithm == "Quick Sort":
        from algorithms.sorting.quick_sort import QuickSortVisualizer
        QuickSortVisualizer().render()

elif category == "Searching Algorithms":
    if algorithm == "Linear Search":
        from algorithms.searching.linear_search import LinearSearchVisualizer
        LinearSearchVisualizer().render()
    elif algorithm == "Binary Search":
        from algorithms.searching.binary_search import BinarySearchVisualizer
        BinarySearchVisualizer().render() 