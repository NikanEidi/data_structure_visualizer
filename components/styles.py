import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
      :root{
        --bg-primary:#0a0e1a;
        --bg-secondary:#0f1420;
        --bg-card:#161b2e;
        --bg-card-hover:#1a2037;
        --primary:#6366f1;
        --primary-light:#818cf8;
        --primary-dark:#4f46e5;
        --secondary:#8b5cf6;
        --accent:#06b6d4;
        --accent-light:#22d3ee;
        --success:#10b981;
        --success-light:#34d399;
        --warning:#f59e0b;
        --warning-light:#fbbf24;
        --text:#e2e8f0;
        --text-secondary:#94a3b8;
        --text-muted:#64748b;
        --border:rgba(99,102,241,.15);
        --border-light:rgba(148,163,184,.1);
        --glow-primary:0 0 20px rgba(99,102,241,.4);
        --glow-accent:0 0 20px rgba(6,182,212,.4);
        --glow-success:0 0 20px rgba(16,185,129,.4);
      }
      
      @keyframes float{
        0%,100%{transform:translateY(0px)}
        50%{transform:translateY(-10px)}
      }
      
      @keyframes glow-pulse{
        0%,100%{box-shadow:var(--glow-primary)}
        50%{box-shadow:0 0 30px rgba(99,102,241,.6)}
      }
      
      @keyframes shimmer{
        0%{background-position:200% center}
        100%{background-position:-200% center}
      }
      
      @keyframes gradient-shift{
        0%,100%{background-position:0% 50%}
        50%{background-position:100% 50%}
      }
      
      *{
        font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
      }
      
      .stApp{
        background:
          radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99,102,241,.15), transparent),
          radial-gradient(ellipse 60% 40% at 0% 100%, rgba(139,92,246,.12), transparent),
          radial-gradient(ellipse 60% 40% at 100% 100%, rgba(6,182,212,.1), transparent),
          linear-gradient(180deg,#0a0e1a 0%,#0d1117 100%);
        background-attachment:fixed;
      }
      
      .block-container{
        max-width:1800px;
        padding:2rem 2rem 3rem;
      }
      
      h1{
        font-size:3rem;
        font-weight:900;
        background:linear-gradient(135deg,#818cf8 0%,#06b6d4 50%,#8b5cf6 100%);
        background-size:200% 200%;
        -webkit-background-clip:text;
        background-clip:text;
        margin-bottom:0.5rem;
        letter-spacing:-0.03em;
        animation:gradient-shift 8s ease infinite;
        filter:drop-shadow(0 0 30px rgba(99,102,241,.3));
      }
      
      .subtitle{
        color:var(--text-secondary);
        font-size:1.125rem;
        margin-bottom:2.5rem;
        font-weight:400;
      }

      [data-testid="column"]{
        background:linear-gradient(135deg,rgba(22,27,46,.95) 0%,rgba(26,32,55,.98) 100%);
        border:1px solid var(--border);
        border-radius:20px;
        padding:1.75rem;
        transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
        position:relative;
        overflow:visible;
        backdrop-filter:blur(10px);
      }
      
      [data-testid="column"]::before{
        content:'';
        position:absolute;
        inset:-1px;
        border-radius:20px;
        padding:1px;
        background:linear-gradient(135deg,rgba(99,102,241,.3),rgba(6,182,212,.2),rgba(139,92,246,.3));
        -webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);
        -webkit-mask-composite:xor;
        mask-composite:exclude;
        opacity:0;
        transition:opacity 0.4s;
      }
      
      [data-testid="column"]::after{
        content:'';
        position:absolute;
        top:-50%;
        left:-50%;
        width:200%;
        height:200%;
        background:radial-gradient(circle,rgba(99,102,241,.08) 0%,transparent 70%);
        opacity:0;
        transition:opacity 0.4s;
        pointer-events:none;
      }
      
      [data-testid="column"]:hover{
        background:linear-gradient(135deg,rgba(26,32,55,.98) 0%,rgba(30,36,64,.99) 100%);
        border-color:rgba(99,102,241,.4);
        box-shadow:0 20px 40px -10px rgba(0,0,0,.5),0 0 40px rgba(99,102,241,.15);
        transform:translateY(-4px);
      }
      
      [data-testid="column"]:hover::before{
        opacity:1;
      }
      
      [data-testid="column"]:hover::after{
        opacity:1;
      }
      
      .frame-title{
        font-size:1.375rem;
        font-weight:800;
        color:var(--text);
        margin-bottom:0.875rem;
        padding-bottom:0.875rem;
        border-bottom:2px solid transparent;
        border-image:linear-gradient(90deg,var(--primary),var(--accent),transparent) 1;
        display:flex;
        align-items:center;
        gap:0.75rem;
        position:relative;
      }
      
      .frame-title::before{
        content:'';
        width:5px;
        height:24px;
        background:linear-gradient(180deg,var(--primary),var(--accent));
        border-radius:3px;
        box-shadow:var(--glow-primary);
        animation:glow-pulse 2s ease-in-out infinite;
      }
      
      .frame-hint{
        color:var(--text-muted);
        font-size:0.875rem;
        margin-bottom:1.5rem;
        line-height:1.7;
        padding:0.75rem 1rem;
        background:rgba(99,102,241,.05);
        border-left:3px solid var(--primary);
        border-radius:8px;
      }

      .bfs-meta{
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:0.875rem;
        margin-top:1.25rem;
      }
      
      .pill{
        background:linear-gradient(135deg,rgba(99,102,241,.12) 0%,rgba(139,92,246,.08) 100%);
        border:1px solid rgba(99,102,241,.3);
        border-radius:14px;
        padding:1.25rem;
        text-align:center;
        transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
        position:relative;
        overflow:hidden;
      }
      
      .pill::before{
        content:'';
        position:absolute;
        top:0;
        left:-100%;
        width:100%;
        height:100%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,.1),transparent);
        transition:left 0.6s;
      }
      
      .pill::after{
        content:'';
        position:absolute;
        inset:0;
        border-radius:14px;
        padding:1px;
        background:linear-gradient(135deg,var(--primary),var(--accent));
        -webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);
        -webkit-mask-composite:xor;
        mask-composite:exclude;
        opacity:0;
        transition:opacity 0.3s;
      }
      
      .pill:hover{
        border-color:rgba(99,102,241,.6);
        transform:translateY(-3px) scale(1.02);
        box-shadow:0 8px 25px rgba(99,102,241,.25);
      }
      
      .pill:hover::before{
        left:100%;
      }
      
      .pill:hover::after{
        opacity:1;
      }
      
      .pill .h{
        color:var(--text-secondary);
        font-size:0.75rem;
        text-transform:uppercase;
        letter-spacing:0.1em;
        font-weight:700;
        margin-bottom:0.625rem;
      }
      
      .pill .v{
        font-size:2rem;
        font-weight:900;
        background:linear-gradient(135deg,var(--primary-light),var(--accent-light));
        -webkit-background-clip:text;
        background-clip:text;
        -webkit-text-fill-color:transparent;
        line-height:1;
        filter:drop-shadow(0 2px 8px rgba(99,102,241,.4));
      }
      
      .pill .v.ok{
        background:linear-gradient(135deg,var(--success),var(--success-light));
        -webkit-background-clip:text;
        background-clip:text;
        -webkit-text-fill-color:transparent;
        filter:drop-shadow(0 2px 8px rgba(16,185,129,.4));
        animation:float 3s ease-in-out infinite;
      }
      
      .pill .v.run{
        background:linear-gradient(135deg,var(--accent),var(--primary-light));
        background-size:200% 200%;
        -webkit-background-clip:text;
        background-clip:text;
        -webkit-text-fill-color:transparent;
        animation:gradient-shift 3s ease infinite;
        filter:drop-shadow(0 2px 8px rgba(6,182,212,.4));
      }
      
      .step-explanation{
        background:linear-gradient(135deg,rgba(15,20,32,.95) 0%,rgba(20,25,40,.98) 100%);
        border:1px solid rgba(99,102,241,.2);
        border-radius:16px;
        padding:1.5rem;
        min-height:350px;
        position:relative;
        overflow:hidden;
        box-shadow:inset 0 2px 20px rgba(0,0,0,.3);
      }
      
      .step-explanation::before{
        content:'';
        position:absolute;
        top:0;
        left:0;
        right:0;
        height:2px;
        background:linear-gradient(90deg,var(--primary),var(--accent),var(--secondary));
        background-size:200% 100%;
        animation:shimmer 3s linear infinite;
      }
      
      .step-content{
        font-family:'Fira Code','Courier New',monospace;
        font-size:0.95rem;
        line-height:1.9;
        color:var(--text);
      }
      
      .step-content .step-header{
        color:var(--accent-light);
        font-weight:800;
        font-size:1.1rem;
        margin-bottom:1rem;
        padding-bottom:0.5rem;
        border-bottom:1px solid rgba(6,182,212,.3);
        display:flex;
        align-items:center;
        gap:0.5rem;
      }
      
      .step-content .step-header::before{
        content:'▶';
        color:var(--primary-light);
        animation:float 2s ease-in-out infinite;
      }
      
      .step-content .action{
        color:var(--success-light);
        font-weight:700;
        background:rgba(16,185,129,.1);
        padding:0.2rem 0.5rem;
        border-radius:4px;
        margin:0.3rem 0;
        display:inline-block;
      }
      
      .step-content .vertex{
        color:var(--primary-light);
        font-weight:800;
        background:rgba(99,102,241,.15);
        padding:0.15rem 0.5rem;
        border-radius:4px;
        border:1px solid rgba(99,102,241,.3);
      }
      
      .step-content .queue-display{
        background:rgba(6,182,212,.08);
        border-left:3px solid var(--accent);
        padding:0.75rem 1rem;
        margin-top:1rem;
        border-radius:6px;
        color:var(--accent-light);
        font-weight:600;
      }
      
      .step-content .completion{
        background:linear-gradient(135deg,rgba(16,185,129,.15),rgba(52,211,153,.1));
        border:1px solid var(--success);
        padding:1rem;
        border-radius:8px;
        text-align:center;
        margin-top:1rem;
        font-weight:700;
        color:var(--success-light);
        animation:glow-pulse 2s ease-in-out infinite;
      }
      
      .legend{
        display:flex;
        gap:1rem;
        margin-top:1.25rem;
        flex-wrap:wrap;
      }
      
      .legend span{
        display:flex;
        align-items:center;
        gap:0.625rem;
        color:var(--text-secondary);
        font-size:0.875rem;
        font-weight:600;
        padding:0.625rem 1rem;
        background:rgba(99,102,241,.08);
        border:1px solid rgba(99,102,241,.2);
        border-radius:10px;
        transition:all 0.3s;
      }
      
      .legend span:hover{
        background:rgba(99,102,241,.15);
        border-color:rgba(99,102,241,.4);
        transform:translateY(-2px);
        box-shadow:0 4px 12px rgba(99,102,241,.2);
      }
      
      .legend i{
        width:14px;
        height:14px;
        border-radius:50%;
        display:inline-block;
        box-shadow:0 0 10px currentColor;
      }

      [data-testid="stSidebar"]{
        background:linear-gradient(180deg,rgba(15,20,32,.98) 0%,rgba(10,14,26,.99) 100%);
        border-right:1px solid var(--border-light);
        backdrop-filter:blur(20px);
      }
      
      [data-testid="stSidebar"]::before{
        content:'';
        position:absolute;
        top:0;
        right:0;
        width:1px;
        height:100%;
        background:linear-gradient(180deg,transparent,var(--primary-light),transparent);
        opacity:0.3;
      }
      
      .sb-logo{
        display:flex;
        align-items:center;
        gap:0.75rem;
        padding-bottom:1.5rem;
        margin-bottom:1.5rem;
        border-bottom:1px solid var(--border-light);
      }
      
      .sb-logo .ring{
        width:12px;
        height:12px;
        border-radius:50%;
        background:linear-gradient(135deg,var(--accent),var(--primary));
        box-shadow:0 0 20px var(--primary-light),0 0 40px rgba(99,102,241,.4);
        animation:glow-pulse 3s ease-in-out infinite;
      }
      
      .sb-logo .brand{
        font-weight:900;
        font-size:1.25rem;
        color:var(--text);
        letter-spacing:0.02em;
      }
      
      .sb-logo .brand .accent{
        background:linear-gradient(135deg,var(--accent),var(--primary-light));
        -webkit-background-clip:text;
        background-clip:text;
        -webkit-text-fill-color:transparent;
      }
      
      .sb-sec{
        color:var(--primary-light);
        text-transform:uppercase;
        font-size:0.75rem;
        font-weight:800;
        letter-spacing:0.12em;
        margin:2rem 0 1rem;
        padding-top:1.5rem;
        border-top:1px solid var(--border-light);
        position:relative;
      }
      
      .sb-sec::before{
        content:'';
        position:absolute;
        top:-1px;
        left:0;
        width:50px;
        height:2px;
        background:linear-gradient(90deg,var(--primary),transparent);
      }

      [data-testid="stDataEditor"],
      .ag-theme-streamlit{
        background:rgba(15,20,32,.6);
        border:1px solid var(--border-light);
        border-radius:12px;
        overflow:hidden;
        transition:all 0.3s;
      }
      
      [data-testid="stDataEditor"]:hover,
      .ag-theme-streamlit:hover{
        border-color:rgba(99,102,241,.3);
        box-shadow:0 4px 20px rgba(0,0,0,.2);
      }
      
      .ag-theme-streamlit{
        --ag-background-color:rgba(15,20,32,.6);
        --ag-header-background-color:rgba(99,102,241,.12);
        --ag-odd-row-background-color:rgba(99,102,241,.04);
        --ag-border-color:var(--border-light);
        --ag-header-foreground-color:var(--text);
        --ag-foreground-color:var(--text);
        --ag-row-hover-color:rgba(99,102,241,.1);
      }
      
      .stButton>button{
        background:linear-gradient(135deg,var(--primary-dark),var(--primary));
        border:none;
        color:white;
        font-weight:700;
        border-radius:12px;
        padding:0.75rem 1.75rem;
        transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
        box-shadow:0 4px 15px rgba(99,102,241,.3);
        position:relative;
        overflow:hidden;
      }
      
      .stButton>button::before{
        content:'';
        position:absolute;
        top:50%;
        left:50%;
        width:0;
        height:0;
        border-radius:50%;
        background:rgba(255,255,255,.3);
        transform:translate(-50%,-50%);
        transition:width 0.6s,height 0.6s;
      }
      
      .stButton>button:hover{
        background:linear-gradient(135deg,var(--primary),var(--primary-light));
        transform:translateY(-2px);
        box-shadow:0 8px 25px rgba(99,102,241,.4);
      }
      
      .stButton>button:hover::before{
        width:400px;
        height:400px;
      }
      
      .stButton>button:active{
        transform:translateY(0);
      }
      
      .stSelectbox>div>div,
      .stRadio>div,
      .stCheckbox>div{
        background:rgba(15,20,32,.8);
        border:1px solid var(--border-light);
        border-radius:10px;
        transition:all 0.3s;
      }
      
      .stSelectbox>div>div:hover,
      .stSelectbox>div>div:focus-within{
        border-color:var(--primary);
        box-shadow:0 0 0 3px rgba(99,102,241,.12);
      }
      
      .stSlider>div>div>div>div{
        background:linear-gradient(90deg,var(--primary),var(--accent));
      }
      
      .stSlider>div>div>div>div>div{
        background:white;
        box-shadow:0 0 0 4px rgba(99,102,241,.2),0 4px 12px rgba(99,102,241,.3);
      }
      
      input,textarea,select{
        background:rgba(15,20,32,.8);
        border:1px solid var(--border-light);
        color:var(--text);
        border-radius:10px;
        transition:all 0.3s;
      }
      
      input:focus,textarea:focus,select:focus{
        border-color:var(--primary);
        box-shadow:0 0 0 3px rgba(99,102,241,.12);
        outline:none;
      }
      
      textarea[disabled]{
        background:rgba(15,20,32,.95);
        color:var(--text);
        font-family:'Fira Code','Courier New',monospace;
        font-size:0.95rem;
        line-height:1.9;
        border:1px solid rgba(99,102,241,.2);
      }
      
      [data-testid="stMarkdownContainer"] p{
        color:var(--text-secondary);
        line-height:1.8;
      }
      
      hr{
        border:none;
        height:1px;
        background:linear-gradient(90deg,transparent,var(--border),transparent);
        margin:2.5rem 0;
      }
      
      [data-testid="stVerticalBlock"]:has(> [data-testid="stImage"]){
        background:transparent;
        border:none;
        padding:0;
      }
      
      ::-webkit-scrollbar{
        width:10px;
        height:10px;
      }
      
      ::-webkit-scrollbar-track{
        background:rgba(15,20,32,.5);
        border-radius:5px;
      }
      
      ::-webkit-scrollbar-thumb{
        background:linear-gradient(180deg,var(--primary),var(--accent));
        border-radius:5px;
        transition:background 0.3s;
      }
      
      ::-webkit-scrollbar-thumb:hover{
        background:linear-gradient(180deg,var(--primary-light),var(--accent-light));
      }
      /* Force compact AG Grid rendering */
    [data-testid="stDataFrame"] div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    [data-testid="stDataFrame"] table {
        border-collapse: collapse !important;
    }

    [data-testid="stDataFrame"] th, 
    [data-testid="stDataFrame"] td {
        padding: 4px 6px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 10px !important;
        overflow: hidden !important;
        background-color: #0d0d15 !important;
    }
    </style>
    """, unsafe_allow_html=True)