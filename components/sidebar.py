import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem; margin-bottom: 1rem;">
            <h2 style="
                font-size: 2rem !important;
                font-weight: 900 !important;
                background: linear-gradient(135deg, #00f5ff 0%, #0066ff 50%, #ff00aa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: balck;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                letter-spacing: -0.02em;
                filter: drop-shadow(0 0 10px rgba(0, 245, 255, 0.5));
            ">
                ALGO VISION
            </h2>
            <div style="
                width: 80px;
                height: 2px;
                background: linear-gradient(90deg, transparent, #00f5ff, #ff00aa, transparent);
                margin: 0.75rem auto 0;
                box-shadow: 0 0 10px rgba(0, 245, 255, 0.6);
            "></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            font-size: 0.625rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: #00f5ff;
            margin-bottom: 0.625rem;
            text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
        ">
            Category
        </div>
        """, unsafe_allow_html=True)
        
        categories = {
            "Graph Algorithms": ["BFS", "DFS", "Dijkstra"],
            "Sorting Algorithms": ["Bubble Sort", "Insertion Sort", "Merge Sort", "Quick Sort"],
            "Searching Algorithms": ["Linear Search", "Binary Search"]
        }
        
        category = st.selectbox(
            "Category",
            options=list(categories.keys()),
            key="category_select",
            label_visibility="collapsed"
        )
        
        st.markdown("""
        <div style="
            font-size: 0.625rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: #00f5ff;
            margin: 1rem 0 0.625rem 0;
            text-shadow: 0 0 10px rgba(0, 245, 255, 0.5);
        ">
            Algorithm
        </div>
        """, unsafe_allow_html=True)
        
        algorithm = st.selectbox(
            "Algorithm",
            options=categories[category],
            key="algorithm_select",
            label_visibility="collapsed"
        )
        
        st.markdown('<div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.3), transparent); margin: 1.25rem 0;"></div>', unsafe_allow_html=True)
        
        algorithm_info = {
            "Linear Search": {
                "desc": "Sequentially checks each element until the target is found or the list ends.",
                "complexity": "O(n)",
                "color": "#0066ff",
                "type": "Search",
                
            },
            "Binary Search": {
                "desc": "Repeatedly divides a sorted list in half to find the target efficiently.",
                "complexity": "O(log n)",
                "color": "#39ff14",
                "type": "Search",
               
            },
            "Bubble Sort": {
                "desc": "Repeatedly swaps adjacent elements if they are in the wrong order.",
                "complexity": "O(n²)",
                "color": "#ff6b35",
                "type": "Sort",
               
            },
            "Insertion Sort": {
                "desc": "Builds a sorted list by inserting each new element in the correct position.",
                "complexity": "O(n²)",
                "color": "#ff6b35",
                "type": "Sort",
               
            },
            "Merge Sort": {
                "desc": "Divides the list into halves, sorts them, and merges the sorted halves.",
                "complexity": "O(n log n)",
                "color": "#39ff14",
                "type": "Sort",
               
            },
            "Quick Sort": {
                "desc": "Picks a pivot and partitions the list, recursively sorting the partitions.",
                "complexity": "O(n log n)",
                "color": "#39ff14",
                "type": "Sort",
                
            },
            "BFS": {
                "desc": "Explores graph level by level from the starting node.",
                "complexity": "O(V + E)",
                "color": "#00f5ff",
                "type": "Graph",
               
            },
            "DFS": {
                "desc": "Explores as far as possible along each branch before backtracking.",
                "complexity": "O(V + E)",
                "color": "#00f5ff",
                "type": "Graph",
                
            },
            "Dijkstra": {
                "desc": "Finds the shortest path in a graph with non-negative edge weights.",
                "complexity": "O(E + V log V)",
                "color": "#00f5ff",
                "type": "Graph",
                
            }
        }
        
        if algorithm in algorithm_info:
            info = algorithm_info[algorithm]
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(5, 5, 10, 0.95) 0%, rgba(15, 15, 25, 0.98) 100%);
                border: 1px solid {info['color']}40;
                border-left: 3px solid {info['color']};
                border-radius: 1rem;
                padding: 1.5rem;
                margin: 1rem 0;
                backdrop-filter: blur(20px);
                box-shadow: 0 0 20px {info['color']}30, 0 4px 20px rgba(0, 0, 0, 0.5);
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 1rem;
                ">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="
                            font-size: 0.625rem;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.1em;
                            color: {info['color']};
                            text-shadow: 0 0 10px {info['color']}80;
                        ">
                            {info['type']}
                        </span>
                    </div>
                    <span style="
                        font-size: 0.9375rem;
                        font-weight: 800;
                        color: {info['color']};
                        font-family: 'JetBrains Mono', monospace;
                        padding: 0.375rem 0.75rem;
                        background: {info['color']}15;
                        border-radius: 0.5rem;
                        border: 1px solid {info['color']}40;
                        text-shadow: 0 0 10px {info['color']}80;
                    ">
                        {info['complexity']}
                    </span>
                </div>
                <div style="
                    font-size: 0.875rem;
                    color: #e0e0ff;
                    line-height: 1.6;
                    font-weight: 400;
                ">
                    {info['desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        return category, algorithm