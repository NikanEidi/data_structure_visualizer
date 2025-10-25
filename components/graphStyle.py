CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
   
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
   
    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        margin: 1.5rem 0 1rem !important;
        padding: 1.25rem 1.5rem !important;
        border-radius: 1rem !important;
        background: linear-gradient(135deg,
            rgba(139, 92, 246, 0.12) 0%,
            rgba(6, 182, 212, 0.08) 100%) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        line-height: 1.3 !important;
        letter-spacing: -0.02em !important;
    }
   
    h1 {
        font-size: 2.75rem !important;
        text-align: center !important;
        padding: 2rem 2.5rem !important;
        background: linear-gradient(135deg,
            rgba(139, 92, 246, 0.15) 0%,
            rgba(6, 182, 212, 0.1) 100%) !important;
        border-left: 6px solid #8b5cf6 !important;
        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.5),
            0 0 24px rgba(139, 92, 246, 0.3) !important;
    }
   
    h2 {
        font-size: 2rem !important;
        padding: 1.5rem 2rem !important;
        border-left: 5px solid #a78bfa !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
    }
   
    h3 {
        font-size: 1.6rem !important;
        padding: 1.25rem 1.75rem !important;
        border-left: 4px solid #c4b5fd !important;
    }
   
    h4 {
        font-size: 1.5rem !important;
        padding: 1rem 1.5rem !important;
        border-left: 4px solid #ddd6fe !important;
    }
   
    h5 {
        font-size: 1.25rem !important;
        padding: 0.875rem 1.25rem !important;
        border-left: 3px solid #e9d5ff !important;
    }
   
    h6 {
        font-size: 1.125rem !important;
        padding: 0.75rem 1rem !important;
        border-left: 3px solid #f3e8ff !important;
    }
   
    .section-header {
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        color: #fafafa !important;
        margin: 2rem 0 1.25rem !important;
        padding: 1.25rem 1.5rem !important;
        border-radius: 0.875rem !important;
        background: linear-gradient(135deg,
            rgba(139, 92, 246, 0.1) 0%,
            rgba(6, 182, 212, 0.06) 100%) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(139, 92, 246, 0.18) !important;
        border-left: 5px solid #8b5cf6 !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        line-height: 1.4;
        letter-spacing: -0.015em;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
   
    .step-card {
        background: linear-gradient(135deg,
            rgba(30, 30, 42, 0.96) 0%,
            rgba(22, 22, 29, 0.98) 100%) !important;
        padding: 2rem !important;
        border-radius: 1rem !important;
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(139, 92, 246, 0.15) !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        border-left: 5px solid #8b5cf6 !important;
        line-height: 1.65 !important;
        max-height: 600px !important;
        overflow: auto !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        color: #fafafa !important;
    }
   
    .step-card *:not(code):not(pre) {
        color: #fafafa !important;
    }
   
    .path-result-card {
        background: linear-gradient(135deg,
            rgba(139, 92, 246, 0.95) 0%,
            rgba(6, 182, 212, 0.9) 100%) !important;
        padding: 2rem !important;
        border-radius: 1rem !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow:
            0 12px 40px rgba(139, 92, 246, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.1) !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        font-weight: 500 !important;
    }
   
    .step-header {
        color: #a78bfa !important;
        font-weight: 700 !important;
        margin-bottom: 1.125rem !important;
        font-size: 1.375rem !important;
        border-left: 4px solid #8b5cf6;
        padding: 0.875rem 1.25rem !important;
        background: rgba(139, 92, 246, 0.08);
        border-radius: 0 0.75rem 0.75rem 0;
        line-height: 1.4;
        letter-spacing: -0.01em;
    }
   
    .step-info {
        color: #d4d4d8 !important;
        margin-bottom: 1.125rem !important;
        font-size: 1.0625rem !important;
        line-height: 1.65;
        padding: 0.375rem 0;
        font-weight: 400 !important;
    }
   
    .neighbors-header {
        color: #a78bfa !important;
        font-weight: 600 !important;
        margin: 1.375rem 0 1rem !important;
        font-size: 1.25rem !important;
        background: rgba(139, 92, 246, 0.08);
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        border-left: 3px solid #8b5cf6;
    }
   
    .update-text {
        color: #34d399 !important;
        font-weight: 600 !important;
        margin: 0.5rem 0 !important;
        background: rgba(16, 185, 129, 0.08);
        padding: 0.625rem 0.875rem;
        border-radius: 0.5rem;
        border-left: 3px solid #10b981;
        font-size: 1rem;
    }
   
    .keep-text {
        color: #fbbf24 !important;
        font-weight: 600 !important;
        margin: 0.5rem 0 !important;
        background: rgba(245, 158, 11, 0.08);
        padding: 0.625rem 0.875rem;
        border-radius: 0.5rem;
        border-left: 3px solid #f59e0b;
        font-size: 1rem;
    }
   
    .visited-text {
        color: #a1a1aa !important;
        font-weight: 600 !important;
        margin: 0.5rem 0 !important;
        background: rgba(161, 161, 170, 0.08);
        padding: 0.625rem 0.875rem;
        border-radius: 0.5rem;
        border-left: 3px solid #71717a;
        font-size: 1rem;
    }
   
    .table-header {
        color: #a78bfa !important;
        font-weight: 700 !important;
        margin: 1.5rem 0 1rem !important;
        font-size: 1.25rem !important;
        border-bottom: 2px solid #8b5cf6;
        padding-bottom: 0.625rem;
    }
   
    .next-step {
        color: #8b5cf6 !important;
        font-weight: 600 !important;
        margin-top: 1.375rem !important;
        font-size: 1.0625rem !important;
        background: rgba(139, 92, 246, 0.08);
        padding: 0.875rem 1.25rem;
        border-radius: 0.75rem;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
   
    .completed-text {
        color: #34d399 !important;
        font-weight: 600 !important;
        margin-top: 1.375rem !important;
        font-size: 1.0625rem !important;
        background: rgba(16, 185, 129, 0.08);
        padding: 0.875rem 1.25rem;
        border-radius: 0.75rem;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
   
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.25rem 0;
        font-size: 0.9375rem;
        background: rgba(22, 22, 29, 0.95);
        border-radius: 0.875rem;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(139, 92, 246, 0.15);
    }
   
    .custom-table th {
        background: linear-gradient(135deg,
            rgba(139, 92, 246, 0.12) 0%,
            rgba(6, 182, 212, 0.08) 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.2) !important;
        padding: 0.875rem 1rem !important;
        text-align: left;
        font-weight: 700 !important;
        color: #c4b5fd !important;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
   
    .custom-table td {
        border: 1px solid rgba(139, 92, 246, 0.12) !important;
        padding: 0.75rem 1rem !important;
        color: #d4d4d8 !important;
        font-size: 0.9375rem;
        font-weight: 400;
    }
   
    .visited-row {
        background: rgba(16, 185, 129, 0.06) !important;
    }
   
    .current-row {
        background: rgba(245, 158, 11, 0.06) !important;
    }
   
    .unvisited-row {
        background: transparent;
    }
   
    .metric-card {
        background: linear-gradient(135deg,
            rgba(30, 30, 42, 0.96) 0%,
            rgba(22, 22, 29, 0.98) 100%) !important;
        padding: 1.5rem !important;
        border-radius: 0.875rem !important;
        border-left: 4px solid #8b5cf6 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
        color: #fafafa !important;
        backdrop-filter: blur(24px) saturate(180%);
    }
   
    .step-card pre {
        background: rgba(10, 10, 15, 0.98) !important;
        color: #d4d4d8 !important;
        padding: 1.125rem;
        border-radius: 0.75rem;
        overflow-x: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.875rem;
        margin: 1rem 0;
        border: 1px solid rgba(139, 92, 246, 0.15);
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
        line-height: 1.5;
    }
   
    .step-card code {
        background: rgba(139, 92, 246, 0.12);
        padding: 0.1875rem 0.5rem;
        border-radius: 0.375rem;
        font-family: 'JetBrains Mono', monospace;
        color: #c4b5fd !important;
        border: 1px solid rgba(139, 92, 246, 0.2);
        font-weight: 500;
        font-size: 0.875rem;
    }
   
    .stMarkdown p, .stMarkdown div, .stMarkdown span:not(code) {
        color: #d4d4d8 !important;
        line-height: 1.65;
    }
   
    .stMarkdown strong {
        color: #a78bfa !important;
        font-weight: 600;
    }
   
    .stMarkdown em {
        color: #8b5cf6 !important;
        font-style: italic;
    }
   
    .stSuccess {
        background: rgba(16, 185, 129, 0.06) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        border-left: 4px solid #10b981 !important;
        color: #d1fae5 !important;
    }
   
    .stError {
        background: rgba(239, 68, 68, 0.06) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-left: 4px solid #ef4444 !important;
        color: #fee2e2 !important;
    }
</style>
"""

GRAPH_LAYOUT_CONFIG = {
    'node_size': 1600,
    'node_border_width': 4,
    'node_border_color': "#a78bfa",
    'font_size': 18,
    'font_weight': "bold",
    'font_color': "white",
    'edge_width_regular': 3.5,
    'edge_width_highlight': 5,
    'edge_width_path': 6,
    'edge_color_regular': "#3f3f46",
    'edge_color_highlight': "#fbbf24",
    'edge_color_path': "#34d399"
}

COLORS = {
    'source': "#8b5cf6",
    'destination': "#a78bfa",
    'visited': "#10b981",
    'current': "#f59e0b",
    'unvisited': "#27272a",
    'active': "#06b6d4",
    'comparing': "#fbbf24",
    'swapping': "#f87171",
    'pivot': "#c084fc",
    'sorted': "#34d399",
    'background': "#0a0a0f",
    'text_primary': "#fafafa",
    'text_secondary': "#d4d4d8",
    'text_tertiary': "#a1a1aa",
    'border_color': "#3f3f46",
    'highlight_glow': "rgba(139, 92, 246, 0.4)"
}