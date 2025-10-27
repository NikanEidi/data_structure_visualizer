# 🔷 Data Structure Visualizer

Interactive Streamlit visualizations for classic data structures and algorithms — step-by-step execution, editable inputs, and exportable visual output (PDF / GIF / MP4).

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Streamlit 1.33.0](https://img.shields.io/badge/streamlit-1.33.0-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Features](#features)
- [Built-in Samples](#built-in-samples)
- [How it Works](#how-it-works)
- [Project Structure](#project-structure)
- [Extending the Project](#extending-the-project)
- [Troubleshooting](#troubleshooting)
- [Developing & Testing](#developing--testing)
- [Contributing](#contributing)
- [License & Author](#license--author)

---

## Overview
This repository contains a Streamlit application that visualizes algorithm execution and internal data structures. It aims to help learners and educators explore algorithms interactively with clear step-by-step explanations, autoplay controls, and export functionality.

Key goals:
- Make algorithms understandable with visual state and explanation.
- Allow users to edit inputs (adjacency matrices, arrays, weights).
- Provide export options to save visualizations as PDF, GIF, or MP4.

---

## Quick Start

Clone, create a venv, install deps, and run:

```bash
git clone https://github.com/NikanEidi/data-structure-visualizer.git
cd data-structure-visualizer

python -m venv venv
source venv/bin/activate           # macOS / Linux
# venv\Scripts\activate            # Windows

pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 in a browser.

---

## Features

- Graph algorithms
  - Breadth-First Search (BFS) — interactive adjacency matrix editing (AG Grid)
  - Depth-First Search (DFS)
  - Dijkstra's shortest path (weighted graphs)
- Sorting algorithms
  - Bubble, Insertion, Merge, Quick
- Searching algorithms
  - Linear search, Binary search
- Visualization & Controls
  - Step / Back / Reset navigation, Auto-play with speed control
  - Live metrics (current step, visited / remaining items)
  - Syntax-highlighted explanations for each step
  - Export visualizations to PDF, GIF, MP4
- UI & Styling
  - Dark theme with glassmorphism design and centralized styling via `components/graphStyle.py`

---

## Built-in Samples
Some ready-to-run sample inputs:
- Searching: `[7, 2, 6, 1, 9, 4]`, `[1, 1, 2, 3, 5, 8]`, `[10,20,30,40,50]`
- Sorting: Random, reversed, and arrays with duplicates
- Graphs: Straight chain, small cycles, mini tree, cross path

---

## How it Works

Each visualizer follows a consistent pattern:

- A Visualizer class (for example `BFSVisualizer`) implements:
  - `render()` — builds Streamlit UI and widgets
  - `step_*()` methods — single-step algorithm logic
  - `_push()` / `_restore()` — history stack for Back navigation
  - `_reset()` — reset to initial state

Session state is namespaced per visualizer to avoid collisions, e.g.:
```python
self.ns = "bfs"
st.session_state[f"{self.ns}_step"] = 0
```

---

## Project Structure

Top-level layout:

```
app.py                          # Main Streamlit entrypoint
requirements.txt                # Python dependencies
README.md
algorithms/
  graph/
    bfs.py
    dfs.py
    dijkstra.py
  searching/
    linear_search.py
    binary_search.py
  sorting/
    bubble_sort.py
    insertion_sort.py
    merge_sort.py
    quick_sort.py
components/
  sidebar.py
  styles.py
  graphStyle.py
  viz_export.py
```

- `app.py` wires the selected visualizer from `components/sidebar.py`.
- `components/` holds UI helpers, CSS injection, and export utilities.
- `algorithms/` holds per-category visualizers and their step logic.

---

## Extending the Project

Add a new visualizer:

1. Create a file under an appropriate folder, e.g. `algorithms/sorting/my_algorithm.py`.
2. Implement a Visualizer class with `self.ns`, `render()`, `_push()`, `_restore()`, `_reset()`.
3. Import and register it in `components/sidebar.py`:
```python
from algorithms.sorting.my_algorithm import MyAlgorithmVisualizer

if selected == "My Algorithm":
    visualizer = MyAlgorithmVisualizer()
    visualizer.render()
```

See the sample template in this repo (README contains a short template example).

---

## Troubleshooting

- Widgets reset unexpectedly: ensure unique session keys (use namespacing).
- StreamlitAPIException (accessing uninitialized state): initialize session keys before widget construction.
- Export fails: verify `matplotlib`, `imageio`, and `pillow` are installed.
- Graph display issues: check layout selection & `graphStyle.py` parameters.

---

## Developing & Testing

- Run the app locally (see Quick Start).
- For fast checks, open only a single visualizer to avoid session collisions.
- Use `@st.cache_data` for expensive computations inside visualizers.
- Suggested tests (manual/unit):
  - Run algorithm on known inputs and verify the final state matches expected output.
  - Test Back/Reset to ensure `_push()` is called before state changes.

---

## Dependencies

Pinned versions used in the project:

```
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

Install with:
```bash
pip install -r requirements.txt
```

---

## Contributing

Contributions are welcome.

Steps:
1. Fork repository.
2. Create branch `git checkout -b feature/your-feature`.
3. Commit and push.
4. Open a Pull Request with a clear description and, if applicable, screenshots and tests.

Ideas:
- Add more algorithms (A*, Bellman-Ford, Kruskal)
- Add complexity graphs and step counters
- Add server-side tests and CI (GitHub Actions)
- Improve mobile layout & accessibility

---

## License & Author

MIT License — open source for educational and personal use.

Author: **Nikan Eidi**  
GitHub: https://github.com/NikanEidi

---

## Next steps & suggestions
- Add a small screenshot or GIF in the README to improve onboarding (place under Overview).
- Add a "Try it online" badge if deployed to Streamlit Cloud or a demo link.
- Add GitHub Actions (CI) to run quick lint/tests and optionally build a demo deployment.
