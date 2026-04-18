"""Theme system · Dark/Light + polished design system"""

import streamlit as st

THEMES = {
    "light": {
        "bg": "#f7f8fc",
        "bg_elev": "#ffffff",
        "surface": "#ffffff",
        "surface_alt": "#f1f3f9",
        "surface_hover": "#eef1f7",
        "text": "#0f172a",
        "text_muted": "#64748b",
        "text_subtle": "#94a3b8",
        "border": "#e2e8f0",
        "border_strong": "#cbd5e1",
        "primary": "#6366f1",
        "primary_hover": "#4f46e5",
        "primary_soft": "#eef2ff",
        "accent": "#ec4899",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#06b6d4",
        "gradient_start": "#6366f1",
        "gradient_mid": "#8b5cf6",
        "gradient_end": "#ec4899",
        "shadow_sm": "0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06)",
        "shadow_md": "0 4px 6px -1px rgba(15,23,42,0.08), 0 2px 4px -2px rgba(15,23,42,0.06)",
        "shadow_lg": "0 10px 15px -3px rgba(15,23,42,0.10), 0 4px 6px -4px rgba(15,23,42,0.08)",
        "shadow_glow": "0 0 0 3px rgba(99,102,241,0.15)",
    },
    "dark": {
        "bg": "#0b0f19",
        "bg_elev": "#111827",
        "surface": "#161c2d",
        "surface_alt": "#1e2438",
        "surface_hover": "#252c42",
        "text": "#f1f5f9",
        "text_muted": "#94a3b8",
        "text_subtle": "#64748b",
        "border": "#2a3246",
        "border_strong": "#3b4561",
        "primary": "#818cf8",
        "primary_hover": "#a5b4fc",
        "primary_soft": "#1e1b4b",
        "accent": "#f472b6",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#f87171",
        "info": "#22d3ee",
        "gradient_start": "#818cf8",
        "gradient_mid": "#a78bfa",
        "gradient_end": "#f472b6",
        "shadow_sm": "0 1px 2px rgba(0,0,0,0.3), 0 1px 3px rgba(0,0,0,0.2)",
        "shadow_md": "0 4px 6px -1px rgba(0,0,0,0.4), 0 2px 4px -2px rgba(0,0,0,0.3)",
        "shadow_lg": "0 10px 15px -3px rgba(0,0,0,0.5), 0 4px 6px -4px rgba(0,0,0,0.4)",
        "shadow_glow": "0 0 0 3px rgba(129,140,248,0.25)",
    },
}


def get_theme():
    return st.session_state.get("theme", "light")


def set_theme(theme: str):
    st.session_state["theme"] = theme


def inject_css():
    """Inject polished theme + responsive CSS"""
    theme = get_theme()
    c = THEMES[theme]

    css = f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
      :root {{
        --bg: {c['bg']};
        --bg-elev: {c['bg_elev']};
        --surface: {c['surface']};
        --surface-alt: {c['surface_alt']};
        --surface-hover: {c['surface_hover']};
        --text: {c['text']};
        --text-muted: {c['text_muted']};
        --text-subtle: {c['text_subtle']};
        --border: {c['border']};
        --border-strong: {c['border_strong']};
        --primary: {c['primary']};
        --primary-hover: {c['primary_hover']};
        --primary-soft: {c['primary_soft']};
        --accent: {c['accent']};
        --success: {c['success']};
        --warning: {c['warning']};
        --danger: {c['danger']};
        --info: {c['info']};
        --grad-start: {c['gradient_start']};
        --grad-mid: {c['gradient_mid']};
        --grad-end: {c['gradient_end']};
        --shadow-sm: {c['shadow_sm']};
        --shadow-md: {c['shadow_md']};
        --shadow-lg: {c['shadow_lg']};
        --shadow-glow: {c['shadow_glow']};
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
      }}

      html, body, [class*="css"] {{
        font-family: 'Sarabun', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      }}

      .stApp {{
        background: var(--bg);
        color: var(--text);
      }}

      /* hide default Streamlit chrome */
      #MainMenu, header[data-testid="stHeader"] {{ visibility: hidden; }}
      .stDeployButton {{ display: none; }}
      footer {{ visibility: hidden; }}

      /* Main container */
      .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
      }}

      /* ============ HERO ============ */
      .ab-hero {{
        position: relative;
        text-align: center;
        padding: 48px 28px;
        background: linear-gradient(135deg, var(--grad-start) 0%, var(--grad-mid) 50%, var(--grad-end) 100%);
        border-radius: var(--radius-xl);
        color: #fff;
        margin-bottom: 28px;
        box-shadow: var(--shadow-lg);
        overflow: hidden;
      }}
      .ab-hero::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
          radial-gradient(circle at 20% 30%, rgba(255,255,255,0.15) 0%, transparent 50%),
          radial-gradient(circle at 80% 70%, rgba(255,255,255,0.1) 0%, transparent 50%);
        pointer-events: none;
      }}
      .ab-hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 999px;
        font-size: 0.8em;
        font-weight: 500;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
      }}
      .ab-hero h1 {{
        color: #fff !important;
        font-size: 2.8em;
        margin: 0 0 12px 0;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.15;
        position: relative;
      }}
      .ab-hero .tagline {{
        font-size: 1.25em;
        margin: 0;
        font-weight: 400;
        opacity: 0.98;
        position: relative;
      }}
      .ab-hero .subtagline {{
        display: inline-flex;
        gap: 12px;
        flex-wrap: wrap;
        justify-content: center;
        font-size: 0.92em;
        margin-top: 20px;
        opacity: 0.92;
        position: relative;
      }}
      .ab-hero .subtagline span {{
        padding: 4px 10px;
        background: rgba(255,255,255,0.12);
        border-radius: 999px;
        font-weight: 500;
      }}

      /* ============ CARDS ============ */
      .ab-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 20px;
        height: 100%;
        box-shadow: var(--shadow-sm);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        position: relative;
        overflow: hidden;
      }}
      .ab-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary);
      }}
      .ab-card-icon {{
        width: 44px;
        height: 44px;
        border-radius: var(--radius-md);
        background: var(--primary-soft);
        color: var(--primary);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5em;
        margin-bottom: 12px;
      }}
      .ab-card h4 {{
        color: var(--text) !important;
        margin: 0 0 8px 0;
        font-size: 1.08em;
        font-weight: 700;
        letter-spacing: -0.01em;
      }}
      .ab-card p {{
        color: var(--text-muted) !important;
        margin: 0;
        font-size: 0.9em;
        line-height: 1.6;
      }}

      /* ============ STEP INDICATOR ============ */
      .ab-steps {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 18px 0 26px 0;
        position: relative;
        padding: 0 10px;
      }}
      .ab-steps::before {{
        content: '';
        position: absolute;
        top: 22px;
        left: 10%;
        right: 10%;
        height: 2px;
        background: var(--border);
        z-index: 0;
      }}
      .ab-step {{
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        gap: 8px;
      }}
      .ab-step-circle {{
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--surface);
        border: 2px solid var(--border);
        color: var(--text-muted);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1em;
        transition: all 0.3s ease;
      }}
      .ab-step.active .ab-step-circle {{
        background: linear-gradient(135deg, var(--grad-start), var(--grad-mid));
        border-color: transparent;
        color: #fff;
        box-shadow: var(--shadow-glow);
        transform: scale(1.08);
      }}
      .ab-step.done .ab-step-circle {{
        background: var(--success);
        border-color: transparent;
        color: #fff;
      }}
      .ab-step-label {{
        font-size: 0.88em;
        color: var(--text-muted);
        font-weight: 500;
        text-align: center;
      }}
      .ab-step.active .ab-step-label {{
        color: var(--text);
        font-weight: 700;
      }}
      .ab-step.done .ab-step-label {{
        color: var(--success);
      }}

      /* ============ TABS ============ */
      .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: var(--surface-alt);
        padding: 6px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
      }}
      .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: var(--radius-sm);
        color: var(--text-muted);
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.2s ease;
        border: none;
      }}
      .stTabs [data-baseweb="tab"]:hover {{
        background: var(--surface-hover);
        color: var(--text);
      }}
      .stTabs [aria-selected="true"] {{
        background: var(--surface) !important;
        color: var(--primary) !important;
        box-shadow: var(--shadow-sm);
      }}
      .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

      /* ============ BUTTONS ============ */
      .stButton>button {{
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-family: 'Sarabun', sans-serif;
        transition: all 0.2s ease;
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--text);
        padding: 8px 16px;
      }}
      .stButton>button:hover {{
        background: var(--surface-hover);
        border-color: var(--primary);
        color: var(--primary);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
      }}
      .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, var(--grad-start), var(--grad-mid)) !important;
        border: none !important;
        color: #fff !important;
        font-weight: 700;
        box-shadow: var(--shadow-md);
      }}
      .stButton>button[kind="primary"]:hover {{
        background: linear-gradient(135deg, var(--grad-mid), var(--grad-end)) !important;
        color: #fff !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
      }}
      .stDownloadButton>button {{
        border-radius: var(--radius-sm);
        font-weight: 600;
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--text);
        transition: all 0.2s ease;
      }}
      .stDownloadButton>button:hover {{
        border-color: var(--primary);
        color: var(--primary);
        background: var(--primary-soft);
      }}

      /* ============ INPUTS ============ */
      .stTextInput>div>div>input,
      .stNumberInput>div>div>input,
      .stTextArea textarea,
      .stSelectbox>div>div {{
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        font-family: 'Sarabun', sans-serif;
      }}
      .stTextInput>div>div>input:focus,
      .stNumberInput>div>div>input:focus,
      .stTextArea textarea:focus {{
        border-color: var(--primary) !important;
        box-shadow: var(--shadow-glow) !important;
      }}
      .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label,
      .stSlider label, .stRadio label, .stFileUploader label {{
        color: var(--text) !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
      }}

      /* slider */
      .stSlider [data-baseweb="slider"] [role="slider"] {{
        background: linear-gradient(135deg, var(--grad-start), var(--grad-mid)) !important;
        border: 3px solid var(--surface) !important;
        box-shadow: var(--shadow-md) !important;
      }}

      /* ============ SIDEBAR ============ */
      section[data-testid="stSidebar"] {{
        background: var(--bg-elev);
        border-right: 1px solid var(--border);
      }}
      section[data-testid="stSidebar"] .stMarkdown h2,
      section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: var(--text);
        font-weight: 700;
        letter-spacing: -0.01em;
      }}

      /* ============ METRICS ============ */
      [data-testid="stMetric"] {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 12px 16px;
        transition: all 0.2s ease;
      }}
      [data-testid="stMetric"]:hover {{
        border-color: var(--primary);
        box-shadow: var(--shadow-sm);
      }}
      [data-testid="stMetricValue"] {{
        color: var(--primary) !important;
        font-weight: 800 !important;
      }}

      /* ============ ALERTS ============ */
      .stAlert {{
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        padding: 14px 18px;
      }}

      /* ============ FILE UPLOADER ============ */
      [data-testid="stFileUploader"] section {{
        border: 2px dashed var(--border-strong) !important;
        border-radius: var(--radius-md) !important;
        background: var(--surface-alt) !important;
        transition: all 0.2s ease;
      }}
      [data-testid="stFileUploader"] section:hover {{
        border-color: var(--primary) !important;
        background: var(--primary-soft) !important;
      }}

      /* ============ EXPANDER ============ */
      .streamlit-expanderHeader {{
        background: var(--surface) !important;
        border-radius: var(--radius-sm);
        font-weight: 600;
      }}

      /* ============ HISTORY ITEMS ============ */
      .ab-history-item {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
      }}
      .ab-history-item:hover {{
        border-color: var(--primary);
        box-shadow: var(--shadow-sm);
      }}

      /* ============ STATUS ============ */
      [data-testid="stStatusWidget"] {{
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
      }}

      /* ============ CHAT ============ */
      [data-testid="stChatMessage"] {{
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        background: var(--surface);
      }}
      [data-testid="stChatInput"] {{
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border);
      }}

      /* ============ HEADINGS ============ */
      h1, h2, h3, h4, h5, h6 {{
        color: var(--text);
        font-weight: 700;
        letter-spacing: -0.01em;
      }}
      h2 {{ font-size: 1.6em; margin-top: 1em !important; }}
      h3 {{ font-size: 1.3em; }}

      /* ============ CODE ============ */
      code, pre {{
        font-family: 'JetBrains Mono', 'Consolas', monospace !important;
      }}
      .stCodeBlock {{
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
      }}

      /* ============ DATAFRAME ============ */
      [data-testid="stDataFrame"] {{
        border-radius: var(--radius-md);
        overflow: hidden;
        border: 1px solid var(--border);
      }}

      /* ============ HR ============ */
      hr {{
        border: none;
        height: 1px;
        background: var(--border);
        margin: 1.4em 0;
      }}

      /* ============ FOOTER ============ */
      .ab-footer-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        text-align: center;
        height: 100%;
      }}
      .ab-footer-card strong {{ display: block; margin-bottom: 4px; }}

      /* ============ THEME TOGGLE ============ */
      .ab-theme-toggle {{
        display: flex;
        gap: 4px;
        background: var(--surface-alt);
        padding: 4px;
        border-radius: 999px;
        border: 1px solid var(--border);
      }}

      /* ============ PRESETS ============ */
      .ab-preset-hint {{
        font-size: 0.85em;
        color: var(--text-muted);
        font-weight: 500;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
      }}

      /* ============ RESPONSIVE ============ */
      @media (max-width: 900px) {{
        .main .block-container {{ padding: 1rem; }}
        .ab-hero {{ padding: 32px 20px; }}
        .ab-hero h1 {{ font-size: 2em; }}
        .ab-hero .tagline {{ font-size: 1.05em; }}
      }}
      @media (max-width: 640px) {{
        .ab-hero {{ padding: 24px 16px; }}
        .ab-hero h1 {{ font-size: 1.5em; }}
        .ab-hero .tagline {{ font-size: 0.92em; }}
        .ab-hero .subtagline {{ font-size: 0.78em; margin-top: 14px; }}
        .ab-card {{ padding: 14px; }}
        .ab-step-circle {{ width: 34px; height: 34px; font-size: 0.85em; }}
        .ab-step-label {{ font-size: 0.72em; }}
        .ab-steps::before {{ top: 17px; }}
        div[data-testid="column"] {{
          width: 100% !important;
          flex: 1 1 100% !important;
          min-width: 100% !important;
        }}
        .stTabs [data-baseweb="tab"] {{ padding: 6px 10px; font-size: 0.85em; }}
      }}

      /* ============ SUBTLE ANIMATIONS ============ */
      @keyframes ab-fadeInUp {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
      .ab-hero, .ab-card {{ animation: ab-fadeInUp 0.4s ease-out; }}

      /* ============ SCROLLBAR ============ */
      ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
      ::-webkit-scrollbar-track {{ background: var(--bg); }}
      ::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 5px; }}
      ::-webkit-scrollbar-thumb:hover {{ background: var(--primary); }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def theme_toggle(container=None):
    """Render theme toggle button"""
    target = container if container is not None else st.sidebar
    current = get_theme()
    label = "🌙  Dark mode" if current == "light" else "☀️  Light mode"
    if target.button(label, use_container_width=True, key="theme_toggle_btn"):
        set_theme("dark" if current == "light" else "light")
        st.rerun()
