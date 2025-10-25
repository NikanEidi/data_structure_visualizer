# Data Structure Visualizer

An interactive Streamlit application for visualizing classic data structure and algorithm concepts with step-by-step explanations, intuitive UI/UX, and a modern design.

## Features

**Graph Algorithms**
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Dijkstra's Shortest Path

**Sorting Algorithms**
- Bubble Sort
- Insertion Sort
- Merge Sort
- Quick Sort

**Searching Algorithms**
- Linear Search
- Binary Search

**Visualization Features**
- Step-by-step control (Next / Back / Reset)
- Auto-Play with adjustable speed
- Live metric updates per step
- Interactive explanations with real code blocks
- Editable adjacency matrices and array inputs
- Real-time state visualization for each iteration

---

## Project Structure
```
data_structure_visualizer/
│
├── app.py                      # Main Streamlit app entry
│
├── components/                 # UI / UX & styling modules
│   ├── sidebar.py              # Sidebar logic and navigation
│   ├── styles.py               # Global CSS and color styling
│
├── algorithms/
│   ├── graph/                  # Graph algorithms
│   │   ├── bfs.py
│   │   ├── dfs.py
│   │   ├── dijkstra.py
│   │   └── graphStyle.py
│   │
│   ├── searching/              # Searching algorithms
│   │   ├── linear_search.py
│   │   └── binary_search.py
│   │
│   ├── sorting/                # Sorting algorithms
│       ├── bubble_sort.py
│       ├── insertion_sort.py
│       ├── merge_sort.py
│       └── quick_sort.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation and Usage

### 1. Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## How It Works

Each algorithm visualizer follows a modular design pattern:

- A Visualizer Class (e.g., `BFSVisualizer`, `BubbleSortVisualizer`) encapsulates logic
- `render()` handles UI rendering and state control
- `step_*()` defines what happens per iteration
- `push()` and `restore()` manage navigation between steps
- Each visualizer generates step-by-step explanations with syntax-highlighted Python code and execution analysis

---

## Design and UI

The interface is styled via `components/styles.py`, following these principles:
- Dark theme with gradients and glassmorphism
- Tight spacing and clean typography
- Step cards use shadows and accent borders for readability
- Sidebar and controls are structured for clarity and minimalism

---

## Controls and Interactions

| Button | Description |
|--------|-------------|
| Next | Move to the next algorithmic step |
| Back | Return to the previous step |
| Reset | Restart the current algorithm |
| Auto-Play | Automatically run with adjustable delay per step |

**Metrics displayed:**
- Current Step Count
- Visited Nodes or Elements
- Remaining Nodes or Elements
- Completion Status

---

## Built-in Samples

### Searching Samples
- `[7, 2, 6, 1, 9, 4]` with targets such as 6 or 8
- `[1, 1, 2, 3, 5, 8]` with multiple targets
- `[10, 20, 30, 40, 50]` (sorted for binary search)

### Sorting Samples
- `[7, 2, 6, 1, 9, 4]` (random order)
- `[5, 4, 3, 2, 1]` (reverse order)
- `[3, 3, 2, 1, 2]` (with duplicates)

### Graph Samples
- Straight Chain (A → B → C → D)
- Simple Branch
- Small Cycle
- Mini Tree
- Cross Path

All samples are editable. Users can modify nodes, edges, or weights dynamically.

---

## Extending the Project

To add a new algorithm, follow this structure:
```python
class MyAlgorithmVisualizer:
    def __init__(self):
        self.ns = "myalgo"

    def render(self):
        # Initialize inputs
        # Setup st.session_state
        # Define step logic
        # Render controls and visualization
        pass
```

Then register it in `app.py` and `sidebar.py`.

---

## Troubleshooting

- **Widgets reset unexpectedly:** Use unique namespaced keys per visualizer
- **StreamlitAPIException:** Initialize `st.session_state` keys before widget creation
- **Auto-Play speed issues:** Adjust delay in the speed slider
- **Font loading errors:** Check internet connection or remove font imports from `styles.py`

---

## License

Open source for educational and personal use.

---

## Author

**Nikan Eidi**  
Toronto, Canada  
GitHub: [NikanEidi](https://github.com/NikanEidi)