import streamlit as st

GRAPH_SAMPLES = ["Straight Chain","Simple Branch","Small Cycle","Mini Tree","Cross Path"]
DIJKSTRA_SAMPLES = ["Tiny Weighted","Triangle 3","Grid 4x4","Random 6"]

ARRAY_SAMPLES = ["Random Small","Sorted","Duplicates","Mixed"]          # Linear Search
BINARY_SAMPLES = ["Sorted 6","Sorted 10","Near-Duplicates"]             # Binary Search

SORT_SAMPLES = ["Random Small","Nearly Sorted","Reverse","Duplicates"]  # Bubble/Insertion/Merge/Quick

def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="sb-logo"><div class="ring"></div>'
            '<div class="brand">ALGO <span class="accent">VISION</span></div></div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="sb-sec">Category</div>', unsafe_allow_html=True)
        category = st.selectbox(
            "Category",
            ["Graph Algorithms","Sorting Algorithms","Searching Algorithms"],
            index=0, key="sb_cat", label_visibility="collapsed"
        )

        algo_map = {
            "Graph Algorithms": ["BFS","DFS","Dijkstra"],
            "Sorting Algorithms": ["Bubble Sort","Insertion Sort","Merge Sort","Quick Sort"],
            "Searching Algorithms": ["Linear Search","Binary Search"],
        }
        st.markdown('<div class="sb-sec">Algorithm</div>', unsafe_allow_html=True)
        algorithm = st.selectbox(
            "Algorithm",
            algo_map[category],
            index=0, key="sb_algo", label_visibility="collapsed"
        )

        is_graph = (category == "Graph Algorithms")
        source_title = "Graph source" if is_graph else "Array source"
        st.markdown(f'<div class="sb-sec">{source_title}</div>', unsafe_allow_html=True)

        source = st.radio(
            "Source",
            ["Sample graph","Build your own"],         
            key="sb_src", horizontal=False, label_visibility="collapsed"
        )

        samples_map = {
            ("Graph Algorithms","BFS"): GRAPH_SAMPLES,
            ("Graph Algorithms","DFS"): GRAPH_SAMPLES,
            ("Graph Algorithms","Dijkstra"): DIJKSTRA_SAMPLES,
            ("Searching Algorithms","Linear Search"): ARRAY_SAMPLES,
            ("Searching Algorithms","Binary Search"): BINARY_SAMPLES,
            ("Sorting Algorithms","Bubble Sort"): SORT_SAMPLES,
            ("Sorting Algorithms","Insertion Sort"): SORT_SAMPLES,
            ("Sorting Algorithms","Merge Sort"): SORT_SAMPLES,
            ("Sorting Algorithms","Quick Sort"): SORT_SAMPLES,
        }

        if source == "Sample graph":
            opts = samples_map.get((category, algorithm), [])
            if opts:
                if st.session_state.get("sb_sample") not in opts:
                    st.session_state["sb_sample"] = opts[0]
                sample_label = "Sample" 
                st.selectbox(
                    sample_label, opts,
                    index=opts.index(st.session_state.get("sb_sample", opts[0])),
                    key="sb_sample", label_visibility="collapsed"
                )
            else:
                st.session_state["sb_sample"] = ""
        else:
            st.session_state["sb_sample"] = ""

        auto = st.checkbox("Auto-Play", value=st.session_state.get("sb_auto", False), key="sb_auto")
        speed = st.slider("Speed (sec/step)", 0.2, 2.5, st.session_state.get("sb_speed", 0.8), 0.1, key="sb_speed")

        st.markdown('<div class="sb-sec">Algorithm Controls</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        next_clicked = c1.button("Next", key="sb_next", use_container_width=True)
        back_clicked = c2.button("Back", key="sb_back", use_container_width=True)
        reset_clicked = c3.button("Reset", key="sb_reset", use_container_width=True)

        st.markdown('<div class="sb-sec">Export</div>', unsafe_allow_html=True)
        fmt = st.selectbox(
            "Format", ["GIF","MP4","PDF"],
            index=["GIF","MP4","PDF"].index(st.session_state.get("sb_fmt","GIF")),
            key="sb_fmt", label_visibility="collapsed"
        )
        fps = st.slider("FPS", 1, 12, st.session_state.get("sb_fps", 6), 1, key="sb_fps")
        export_clicked = st.button("Export", key="sb_export", use_container_width=True)

        return (
            category, algorithm, source, st.session_state.get("sb_sample",""),
            fmt, fps, next_clicked, back_clicked, reset_clicked, export_clicked
        )