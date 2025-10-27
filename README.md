# 🔷 Data Structure Visualizer

An interactive Streamlit application for visualizing classic data structure and algorithm concepts with step-by-step explanations, intuitive UI/UX, and a modern design.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Streamlit 1.33.0](https://img.shields.io/badge/streamlit-1.33.0-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 📊 Graph Algorithms
- **Breadth-First Search (BFS)** - Enhanced with AG Grid & export features
- **Depth-First Search (DFS)** - Complete traversal visualization
- **Dijkstra's Shortest Path** - Weighted graph pathfinding

### 🔄 Sorting Algorithms
- **Bubble Sort** - Visual comparison-based sorting
- **Insertion Sort** - Incremental array building
- **Merge Sort** - Divide-and-conquer approach
- **Quick Sort** - Efficient partition-based sorting

### 🔍 Searching Algorithms
- **Linear Search** - Sequential element scanning
- **Binary Search** - Logarithmic search on sorted arrays

### 🎯 Visualization Capabilities
- ✔️ **Step-by-step control** - Navigate through algorithm execution (Next / Back / Reset)
- ⚡ **Auto-Play mode** - Watch algorithms run automatically with adjustable speed
- 📈 **Live metrics** - Real-time tracking of algorithm progress and statistics
- 💡 **Interactive explanations** - Detailed code blocks with syntax highlighting
- ✏️ **Editable inputs** - Modify adjacency matrices, arrays, and algorithm parameters
- 🎬 **State visualization** - See internal data structures change in real-time
- 📤 **Export functionality** - Save visualizations as PDF, GIF, or MP4 files

---

## 🚀 What's New in v1.1.1

| Feature | Description |
|---------|-------------|
| 🔥 **Enhanced BFS Visualization** | Complete rewrite with AG Grid support for interactive adjacency matrix editing |
| 🎨 **Modern Dark UI** | Sleek glassmorphism design with `#7c4dff` accent color and refined layouts |
| 📥 **Multi-Format Export** | Export algorithm visualizations to PDF, GIF, or MP4 via dedicated export module |
| 📝 **Rich Step Explanations** | HTML-formatted explanations with code highlighting for each algorithm step |
| 🔧 **Technical Upgrades** | Full compatibility with Python 3.12 and Streamlit 1.33.0 |
| 💾 **Persistent State Management** | Robust session state handling with `_push()` and `_restore()` navigation |
| 📐 **Four-Panel Layout** | Organized interface: Adjacency Matrix, State Table, Graph Display, and Explanations |
| 🎯 **Graph Styling System** | Centralized graph configuration and styling via `graphStyle.py` component |

---

## 🏗️ Project Structure

```
data_structure_visualizer/
│
├── app.py                          # Main Streamlit application entry point
│
├── components/                     # UI/UX components and utilities
│   ├── sidebar.py                  # Navigation sidebar with algorithm selection
│   ├── styles.py                   # Global CSS styling and theme configuration
│   ├── graphStyle.py               # Graph visualization styling and layout config
│   └── viz_export.py               # Export functionality (PDF, GIF, MP4)
│
├── algorithms/
│   ├── graph/                      # Graph algorithm implementations
│   │   ├── bfs.py                  # Breadth-First Search with enhanced features
│   │   ├── dfs.py                  # Depth-First Search
│   │   └── dijkstra.py             # Dijkstra's shortest path algorithm
│   │
│   ├── searching/                  # Searching algorithm implementations
│   │   ├── linear_search.py        # Linear search visualization
│   │   └── binary_search.py        # Binary search visualization
│   │
│   └── sorting/                    # Sorting algorithm implementations
│       ├── bubble_sort.py          # Bubble sort visualization
│       ├── insertion_sort.py       # Insertion sort visualization
│       ├── merge_sort.py           # Merge sort visualization
│       └── quick_sort.py           # Quick sort visualization
│
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
└── .gitignore                      # Git ignore rules
```

---

## ⚙️ Installation and Usage

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/NikanEidi/data-structure-visualizer.git
cd data-structure-visualizer
```

### 2️⃣ Create and Activate Virtual Environment

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📦 Dependencies

```txt
streamlit==1.33.0
pandas==2.2.3
numpy==1.26.4
matplotlib==3.9.2
networkx==3.2.1
pillow==10.2.0
imageio==2.35.1
pyarrow==17.0.0
streamlit-aggrid==1.0.5
```

**Key Libraries:**
- **Streamlit** - Web application framework
- **NetworkX** - Graph data structure and algorithms
- **Matplotlib** - Visualization rendering
- **AG Grid** - Interactive data tables for adjacency matrices
- **ImageIO** - Export to GIF and MP4 formats
- **Pandas/NumPy** - Data manipulation and processing

---

## 🎯 How It Works

Each algorithm visualizer follows a **modular and consistent design pattern**:

### Architecture Components

| Component | Purpose |
|-----------|---------|
| 🏗️ **Visualizer Class** | Encapsulates algorithm logic (e.g., `BFSVisualizer`, `BubbleSortVisualizer`) |
| 🎨 **`render()` method** | Handles UI rendering, input controls, and state management |
| 📊 **`step_*()` methods** | Define the logic executed during each algorithm iteration |
| 💾 **`_push()` method** | Saves current state to history stack for backward navigation |
| 🔙 **`_restore()` method** | Restores previous state from history when user clicks "Back" |
| 📝 **Explanation generator** | Creates step-by-step explanations with syntax-highlighted code |

### Session State Management

All visualizers use **namespaced session state keys** to prevent conflicts:

```python
self.ns = "bfs"  # Unique namespace
st.session_state[f"{self.ns}_step"] = 0
st.session_state[f"{self.ns}_visited"] = set()
```

---

## 🎨 Design and UI

The interface is styled through **`components/styles.py`** and **`components/graphStyle.py`**, following modern design principles:

### Design Philosophy

- 🌙 **Dark theme** with smooth gradients and glassmorphism effects
- 🎨 **Primary accent**: `#7c4dff` (vibrant purple) with complementary colors
- 📐 **Clean typography** with optimal spacing and hierarchy
- ✨ **Elevated cards** with subtle shadows and accent borders
- 🧭 **Intuitive navigation** through structured sidebar and control panels

### Graph Visualization Configuration

The `graphStyle.py` component provides:
- 🎨 Consistent node and edge styling
- 📐 Layout algorithms (spring, circular, hierarchical)
- 🎯 Color schemes for different node states (visited, active, unvisited)
- 📏 Size and spacing configurations

### BFS Enhanced Layout (Four-Panel Interface)

| Panel | Description |
|-------|-------------|
| 🔢 **Adjacency Matrix** | Interactive AG Grid for editing graph connections |
| 📊 **Algorithm State** | Live display of queue contents and visited nodes |
| 🗺️ **Graph Visualization** | NetworkX-rendered graph with highlighted active nodes |
| 📝 **Step Explanation** | Detailed HTML breakdown of current algorithm step |

---

## 🎮 Controls and Interactions

### Navigation Controls

| Button | Icon | Description |
|--------|------|-------------|
| **Next** | ▶️ | Advance to the next algorithm step |
| **Back** | ◀️ | Return to the previous step (uses state history) |
| **Reset** | 🔄 | Restart the algorithm from the beginning |
| **Auto-Play** | ⏯️ | Automatically execute steps with configurable delay |
| **Export** | 📤 | Download visualization as PDF, GIF, or MP4 |

### Export Options (via `viz_export.py`)

| Format | Use Case | Features |
|--------|----------|----------|
| 📄 **PDF** | Documentation, reports | Multi-page support, high resolution |
| 🎞️ **GIF** | Web sharing, presentations | Animated loop, optimized size |
| 🎬 **MP4** | Video embedding, lectures | Smooth playback, customizable FPS |

### Real-Time Metrics

Each algorithm displays live statistics:

- 📍 **Current Step** - Step number in the execution sequence
- ✅ **Visited/Processed** - Elements or nodes already processed
- ⏳ **Remaining** - Elements or nodes yet to be processed
- 🎯 **Completion Status** - Progress percentage and final state

### Speed Control

Auto-Play mode includes adjustable delay:
- ⚡ **Fast**: 0.1s per step
- ⚙️ **Normal**: 0.5s per step
- 🐌 **Slow**: 2.0s per step

---

## 🧪 Built-in Samples

### 🔍 Searching Algorithm Samples

| Sample Array | Type | Use Case |
|--------------|------|----------|
| `[7, 2, 6, 1, 9, 4]` | Unsorted | Linear search with targets 6, 8 |
| `[1, 1, 2, 3, 5, 8]` | Fibonacci | Duplicate handling tests |
| `[10, 20, 30, 40, 50]` | Sorted | Binary search optimal case |

### 🔄 Sorting Algorithm Samples

| Sample Array | Characteristic | Purpose |
|--------------|----------------|---------|
| `[7, 2, 6, 1, 9, 4]` | Random order | General sorting behavior |
| `[5, 4, 3, 2, 1]` | Reverse sorted | Worst-case scenario testing |
| `[3, 3, 2, 1, 2]` | With duplicates | Stability verification |

### 🗺️ Graph Algorithm Samples

| Sample Name | Structure | Node Count | Description |
|-------------|-----------|------------|-------------|
| 🔗 **Straight Chain** | Linear | 4 | A → B → C → D (simple path) |
| 🌿 **Simple Branch** | Tree | 5 | Root with 2-3 branches |
| 🔄 **Small Cycle** | Cyclic | 4 | Circular connections (cycle detection) |
| 🌳 **Mini Tree** | Hierarchical | 6 | Binary tree structure |
| ✖️ **Cross Path** | Complex | 6 | Intersecting paths (multiple routes) |

> **ℹ️ Note:** All samples are **fully interactive and editable**. Modify nodes, edges, weights, or create custom inputs directly in the UI.

---

## 🔧 Extending the Project

### Adding a New Algorithm

Follow this template to add your own algorithm visualizer:

```python
class MyAlgorithmVisualizer:
    def __init__(self):
        self.ns = "myalgo"  # Unique namespace for session state
        
    def render(self):
        """Main rendering function called by app.py"""
        # 1. Initialize inputs (arrays, graphs, parameters)
        st.subheader("My Algorithm")
        
        # 2. Setup session state with namespaced keys
        if f"{self.ns}_initialized" not in st.session_state:
            st.session_state[f"{self.ns}_initialized"] = True
            st.session_state[f"{self.ns}_step"] = 0
            st.session_state[f"{self.ns}_history"] = []
        
        # 3. Define step logic
        def step_forward():
            self._push()  # Save current state
            # Your algorithm logic here
            st.session_state[f"{self.ns}_step"] += 1
        
        # 4. Render controls
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Next", on_click=step_forward, key=f"{self.ns}_next")
        with col2:
            st.button("Back", on_click=self._restore, key=f"{self.ns}_back")
        with col3:
            st.button("Reset", on_click=self._reset, key=f"{self.ns}_reset")
        
        # 5. Render visualization
        self._render_visualization()
    
    def _push(self):
        """Save current state to history stack"""
        state = {
            "step": st.session_state[f"{self.ns}_step"],
            # Add other state variables
        }
        st.session_state[f"{self.ns}_history"].append(state)
    
    def _restore(self):
        """Restore previous state from history"""
        if st.session_state[f"{self.ns}_history"]:
            state = st.session_state[f"{self.ns}_history"].pop()
            st.session_state[f"{self.ns}_step"] = state["step"]
            # Restore other state variables
    
    def _reset(self):
        """Reset algorithm to initial state"""
        st.session_state[f"{self.ns}_step"] = 0
        st.session_state[f"{self.ns}_history"] = []
        # Reset other state variables
    
    def _render_visualization(self):
        """Render the visual representation"""
        pass
```

### Registration Steps

1. **Create algorithm file** in appropriate folder (`algorithms/graph/`, `algorithms/sorting/`, or `algorithms/searching/`)
2. **Import in `app.py`**:
   ```python
   from algorithms.category.my_algorithm import MyAlgorithmVisualizer
   ```
3. **Add to sidebar** in `components/sidebar.py`:
   ```python
   if selected == "My Algorithm":
       visualizer = MyAlgorithmVisualizer()
       visualizer.render()
   ```

---

## 🛠️ Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| ⚠️ **Widgets reset unexpectedly** | Key collision between visualizers | Use unique namespaced keys (e.g., `f"{self.ns}_button"`) |
| 🐛 **StreamlitAPIException** | Accessing uninitialized session state | Initialize all session state keys before widget creation |
| 🐌 **Auto-Play lag/speed issues** | Heavy computation in step function | Optimize algorithm logic; adjust speed slider (0.1s - 2.0s) |
| 🎨 **Styling not applied** | CSS not loaded or overridden | Check `components/styles.py` import and call `inject_custom_css()` |
| 📦 **Import/dependency errors** | Wrong Python version or missing packages | Use Python 3.12 and install exact versions from `requirements.txt` |
| 🖼️ **Export fails** | Missing imageio or matplotlib | Verify `viz_export.py` dependencies are installed correctly |
| 🗺️ **Graph not displaying** | NetworkX layout issue | Check `graphStyle.py` configuration and graph data structure |

### Common Fixes

**Problem:** State persists between algorithm switches
```python
# Solution: Use unique namespace for each visualizer
self.ns = "unique_algo_name"
```

**Problem:** Back button doesn't work
```python
# Solution: Ensure _push() is called before state changes
def step_forward():
    self._push()  # Must be called first
    # Then modify state
```

**Problem:** Export produces empty file
```python
# Solution: Verify viz_export.py has access to current visualization state
from components.viz_export import export_to_pdf, export_to_gif, export_to_mp4
```

---

## 🌐 Deployment

### Local Development

```bash
streamlit run app.py --server.port 8501
```

### Streamlit Cloud Deployment

1. **Push to GitHub** - Ensure `requirements.txt` is up to date
2. **Connect repository** at [share.streamlit.io](https://share.streamlit.io)
3. **Set Python version** to 3.12 in Streamlit Cloud settings
4. **Deploy** - Automatic deployment on push

**Deployment Checklist:**
- ✅ Python 3.12 compatibility verified
- ✅ All dependencies in `requirements.txt` with pinned versions
- ✅ No hard-coded file paths (use relative paths)
- ✅ Session state properly namespaced
- ✅ Export functionality tested locally

### Performance Tips

- 🚀 Use `@st.cache_data` for expensive computations
- 💾 Minimize session state size (store only necessary data)
- 🎨 Optimize graph rendering for large networks (>50 nodes)
- ⚡ Use lazy loading for algorithm explanations

---

## 📄 License

Open source for educational and personal use.

---

## 👨‍💻 Author

**Nikan Eidi**  
📍 Toronto, Canada  
🔗 GitHub: [@NikanEidi](https://github.com/NikanEidi)  
📧 Contact: [GitHub Profile](https://github.com/NikanEidi)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 **Fork the repository**
2. 🔧 **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. 💾 **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. 📤 **Push to the branch** (`git push origin feature/AmazingFeature`)
5. 🎉 **Open a Pull Request**

### Contribution Ideas

- 🎯 Add new algorithms (Bellman-Ford, A*, Kruskal's, etc.)
- 🎨 Improve UI/UX with new themes or layouts
- 📊 Add complexity analysis visualizations
- 🌍 Internationalization (i18n) support
- 📱 Mobile responsiveness improvements
- 📚 Additional documentation and tutorials

---

## ⭐ Show Your Support

If you find this project helpful, please consider:
- ⭐ **Starring the repository** on GitHub
- 🐛 **Reporting bugs** or suggesting features via [Issues](https://github.com/NikanEidi/data-structure-visualizer/issues)
- 📢 **Sharing** with classmates, colleagues, or on social media
- 💬 **Providing feedback** to help improve the project

---

## 📚 Resources

- 📖 [Streamlit Documentation](https://docs.streamlit.io)
- 🔗 [NetworkX Documentation](https://networkx.org/documentation/stable/)
- 🎨 [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- 📊 [AG Grid for Streamlit](https://github.com/PablocFonseca/streamlit-aggrid)

---

<div align="center">

**Built with 💜 using Streamlit**

[🐛 Report Bug](https://github.com/NikanEidi/data-structure-visualizer/issues) · [✨ Request Feature](https://github.com/NikanEidi/data-structure-visualizer/issues) · [📖 Documentation](https://github.com/NikanEidi/data-structure-visualizer/wiki)

---

*Making algorithms visual, one step at a time* 🚀

</div>