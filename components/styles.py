import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
       
        :root {
            --neon-cyan: #00f5ff;
            --neon-magenta: #ff00aa;
            --electric-blue: #0066ff;
            --sunset-orange: #ff6b35;
            --lime-green: #39ff14;
            --deep-purple: #6b2cf5;
            --hot-pink: #ff1493;
            
            --bg-void: #05050a;
            --bg-dark: #0d0d15;
            --bg-card: #15151f;
            --bg-elevated: #1a1a28;
            
            --text-bright: #ffffff;
            --text-main: #e0e0ff;
            --text-dim: #9090b0;
            
            --glow-cyan: 0 0 20px rgba(0, 245, 255, 0.4);
            --glow-magenta: 0 0 20px rgba(255, 0, 170, 0.4);
            --glow-purple: 0 0 20px rgba(107, 44, 245, 0.4);
            
            --space-xs: 0.375rem;
            --space-sm: 0.625rem;
            --space-md: 1rem;
            --space-lg: 1.5rem;
            --space-xl: 2rem;
            --space-2xl: 3rem;
            
            --radius-sm: 0.625rem;
            --radius-md: 0.875rem;
            --radius-lg: 1.125rem;
            --radius-xl: 1.5rem;
            
            --transition: 0.3s cubic-bezier(0.22, 1, 0.36, 1);
        }
       
        * {
            font-family: 'Space Grotesk', 'Inter', -apple-system, sans-serif !important;
            box-sizing: border-box;
        }
       
        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }
       
        .stApp {
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(0, 102, 255, 0.15) 0%, transparent 40%),
                radial-gradient(ellipse at 80% 80%, rgba(255, 0, 170, 0.12) 0%, transparent 40%),
                radial-gradient(ellipse at 50% 50%, rgba(107, 44, 245, 0.08) 0%, transparent 50%),
                var(--bg-void);
            min-height: 100vh;
        }
       
        .block-container {
            padding: var(--space-2xl) var(--space-2xl) !important;
            max-width: 1700px !important;
            margin: 0 auto;
        }
       
        h1 {
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            text-align: center !important;
            background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--electric-blue) 50%, var(--neon-magenta) 100%);
            -webkit-background-clip: text;
            background-clip: text;
            padding: var(--space-xl) var(--space-2xl) !important;
            margin-bottom: var(--space-xl) !important;
            position: relative;
            filter: drop-shadow(var(--glow-cyan));
            letter-spacing: -0.03em;
        }
       
        h1::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--neon-cyan), var(--neon-magenta), transparent);
            box-shadow: var(--glow-cyan);
        }
       
        h2 {
            font-size: 2.25rem !important;
            font-weight: 700 !important;
            color: var(--text-bright) !important;
            background: linear-gradient(135deg, rgba(0, 245, 255, 0.08) 0%, rgba(107, 44, 245, 0.08) 100%);
            padding: var(--space-lg) var(--space-xl) !important;
            border-radius: var(--radius-lg) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-left: 4px solid var(--neon-cyan) !important;
            margin: var(--space-xl) 0 var(--space-lg) 0 !important;
            backdrop-filter: blur(20px);
            box-shadow: var(--glow-cyan);
        }
       
        h3 {
            font-size: 1.75rem !important;
            font-weight: 600 !important;
            background: linear-gradient(135deg, var(--neon-cyan), var(--electric-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: white;
            background-clip: text;
            margin: var(--space-lg) 0 var(--space-md) 0 !important;
        }
       
        p, div:not([class*="st"]), span {
            color: var(--text-main) !important;
            line-height: 1.7;
            font-size: revert;
        }
       
        strong {
            color: var(--text-bright) !important;
            font-weight: 600;
        }
       
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--bg-dark) 0%, var(--bg-void) 100%) !important;
            border-right: 1px solid rgba(0, 245, 255, 0.15) !important;
            padding: 0;
            min-width: 320px;
            max-width: 360px;
            box-shadow: inset -1px 0 20px rgba(0, 245, 255, 0.1);
        }
       
        [data-testid="stSidebar"] .block-container {
            padding: 0 !important;
        }
       
        .stSelectbox label,
        .stRadio label,
        .stCheckbox label,
        .stSlider label {
            color: var(--neon-cyan) !important;
            font-weight: 700 !important;
            font-size: 0.75rem !important;
            margin-bottom: var(--space-xs);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            text-shadow: var(--glow-cyan);
        }
       
        .stSelectbox > div > div,
        .stTextInput > div > div,
        .stNumberInput > div > div {
            background: var(--bg-card) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-bright) !important;
            transition: all var(--transition);
            padding: var(--space-sm) var(--space-md);
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.5);
        }
       
        .stSelectbox > div > div:hover,
        .stTextInput > div > div:hover,
        .stNumberInput > div > div:hover {
            border-color: var(--neon-cyan) !important;
            background: var(--bg-elevated) !important;
            box-shadow: var(--glow-cyan);
        }
       
        .stButton > button {
            background: linear-gradient(135deg, var(--electric-blue) 0%, var(--deep-purple) 100%) !important;
            color: white !important;
            border: 1px solid rgba(0, 245, 255, 0.3) !important;
            border-radius: var(--radius-md) !important;
            padding:0 !important;
            font-weight: 700 !important;
            font-size: 0.9375rem !important;
            transition: all var(--transition) !important;
            box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3), var(--glow-cyan) !important;
            margin: var(--space-sm) 0;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
       
        .stButton > button:hover {
            background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--electric-blue) 100%) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 25px rgba(0, 245, 255, 0.5), var(--glow-cyan) !important;
            border-color: var(--neon-cyan) !important;
        }
       
        .stButton > button:active {
            transform: translateY(0) !important;
        }
       
        div[data-testid="stMetric"] {
            background: var(--bg-card) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: var(--radius-lg) !important;
            padding: var(--space-lg) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), var(--glow-cyan) !important;
            transition: all var(--transition);
            backdrop-filter: blur(10px);
        }
       
        div[data-testid="stMetric"]:hover {
            border-color: var(--neon-cyan);
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 245, 255, 0.4) !important;
        }
       
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, var(--neon-cyan), var(--electric-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
       
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
            color: var(--text-dim) !important;
            font-weight: 600 !important;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
       
        .stCheckbox {
            background: var(--bg-card) !important;
            padding: var(--space-md) !important;
            border-radius: var(--radius-sm) !important;
            border: 1px solid rgba(0, 245, 255, 0.15) !important;
            margin: var(--space-sm) 0 !important;
            transition: all var(--transition);
        }
       
        .stCheckbox:hover {
            border-color: var(--neon-cyan) !important;
            background: var(--bg-elevated) !important;
            box-shadow: var(--glow-cyan);
        }
       
        .stSlider {
            padding: var(--space-md) 0 !important;
        }
       
        .stSlider > div > div > div {
            background: linear-gradient(90deg, var(--electric-blue), var(--neon-cyan)) !important;
            box-shadow: var(--glow-cyan);
        }
       
        .stSlider > div > div > div > div {
            background: white !important;
            border: 3px solid var(--neon-cyan) !important;
            box-shadow: 0 0 15px rgba(0, 245, 255, 0.6);
            width: 22px !important;
            height: 22px !important;
        }
       
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: var(--radius-lg) !important;
            overflow: hidden;
            background: var(--bg-card) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
       
        div[data-testid="stDataFrame"] thead tr th {
            background: linear-gradient(135deg, rgba(0, 245, 255, 0.1) 0%, rgba(0, 102, 255, 0.1) 100%) !important;
            color: var(--neon-cyan) !important;
            font-weight: 700 !important;
            border-bottom: 2px solid var(--neon-cyan) !important;
            padding: var(--space-lg) !important;
            font-size: 0.8125rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
       
        div[data-testid="stDataFrame"] tbody tr td {
            background: transparent !important;
            color: var(--text-main) !important;
            padding: var(--space-md) var(--space-lg) !important;
            border-bottom: 1px solid rgba(0, 245, 255, 0.05) !important;
        }
       
        div[data-testid="stDataFrame"] tbody tr:hover td {
            background: rgba(0, 245, 255, 0.05) !important;
        }
       
        .streamlit-expanderHeader {
            background: var(--bg-card) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-bright) !important;
            font-weight: 600 !important;
            padding: var(--space-md) var(--space-lg) !important;
            transition: all var(--transition);
        }
       
        .streamlit-expanderHeader: shover {
            border-color: var(--neon-cyan) !important;
            background: var(--bg-elevated) !important;
            box-shadow: var(--glow-cyan);
        }
       
        .streamlit-expanderContent {
            background: var(--bg-card) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
            padding: var(--space-lg) !important;
        }
       
        .stRadio > div {
            background: var(--bg-card) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: var(--radius-md) !important;
            padding: var(--space-sm) !important;
            display: flex !important;
            gap: var(--space-sm) !important;
        }
       
        .stRadio > div > label {
            background: rgba(0, 245, 255, 0.05) !important;
            padding: var(--space-md) var(--space-lg) !important;
            border-radius: var(--radius-sm) !important;
            margin: 0 !important;
            transition: all var(--transition);
            flex: 1;
            text-align: center;
            border: 1px solid transparent;
            font-weight: 600;
        }
       
        .stRadio > div > label:hover {
            background: rgba(0, 245, 255, 0.1) !important;
            border-color: var(--neon-cyan);
            box-shadow: var(--glow-cyan);
        }
       
        .stSuccess {
            background: rgba(57, 255, 20, 0.08) !important;
            border: 1px solid rgba(57, 255, 20, 0.3) !important;
            border-left: 4px solid var(--lime-green) !important;
            border-radius: var(--radius-md) !important;
            color: #d4ffcc !important;
            padding: var(--space-lg) !important;
        }
       
        .stError {
            background: rgba(255, 0, 170, 0.08) !important;
            border: 1px solid rgba(255, 0, 170, 0.3) !important;
            border-left: 4px solid var(--neon-magenta) !important;
            border-radius: var(--radius-md) !important;
            color: #ffd4f0 !important;
            padding: var(--space-lg) !important;
        }
       
        .stInfo {
            background: rgba(0, 245, 255, 0.08) !important;
            border: 1px solid rgba(0, 245, 255, 0.3) !important;
            border-left: 4px solid var(--neon-cyan) !important;
            border-radius: var(--radius-md) !important;
            color: #ccf7ff !important;
            padding: var(--space-lg) !important;
        }
       
        .stWarning {
            background: rgba(255, 107, 53, 0.08) !important;
            border: 1px solid rgba(255, 107, 53, 0.3) !important;
            border-left: 4px solid var(--sunset-orange) !important;
            border-radius: var(--radius-md) !important;
            color: #ffe4cc !important;
            padding: var(--space-lg) !important;
        }
       
        hr {
            border-color: rgba(0, 245, 255, 0.2) !important;
            margin: var(--space-xl) 0 !important;
        }
       
        pre {
            background: var(--bg-void) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: var(--radius-md) !important;
            padding: var(--space-lg) !important;
        }
       
        code {
            background: rgba(0, 245, 255, 0.1) !important;
            color: var(--neon-cyan) !important;
            padding: 0.15rem var(--space-sm) !important;
            border-radius: 0.25rem !important;
            font-size: 0.875em !important;
            border: 1px solid rgba(0, 245, 255, 0.2);
        }
       
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
       
        ::-webkit-scrollbar-track {
            background: var(--bg-dark);
            border-radius: var(--radius-sm);
        }
       
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, var(--neon-cyan), var(--electric-blue));
            border-radius: var(--radius-sm);
            border: 2px solid var(--bg-dark);
            box-shadow: var(--glow-cyan);
        }
       
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, var(--electric-blue), var(--neon-cyan));
        }
    </style>
    """, unsafe_allow_html=True)