"""Theme system · design tokens + light/dark + consistent CSS

Design principles (learned from previous iterations):
- Only target data-testid selectors (stable across Streamlit versions)
- NEVER target Streamlit's internal class names (e.g. .css-xyz) — those change
- Keep CSS under ~200 lines · simpler = more resilient
- Use CSS variables (tokens) so component styling stays consistent
- Inject via st.markdown(..., unsafe_allow_html=True) — not st.html (1.32+ only)
- No external <link> fonts · rely on system Thai fonts
"""

import streamlit as st


# ============================================================================
# Design tokens
# ============================================================================

TOKENS = {
    "light": {
        # Surfaces
        "bg":           "#f7f8fc",
        "surface":      "#ffffff",
        "surface_alt":  "#f1f3f9",
        "surface_hover":"#eef1f7",
        "border":       "#e2e8f0",
        "border_strong":"#cbd5e1",
        # Text
        "text":         "#0f172a",
        "text_muted":   "#64748b",
        "text_subtle":  "#94a3b8",
        # Brand
        "primary":      "#6366f1",
        "primary_hover":"#4f46e5",
        "primary_soft": "#eef2ff",
        "accent":       "#ec4899",
        # Feedback
        "success":      "#10b981",
        "warning":      "#f59e0b",
        "danger":       "#ef4444",
        "info":         "#06b6d4",
        # Gradient for hero
        "grad_1":       "#6366f1",
        "grad_2":       "#8b5cf6",
        "grad_3":       "#ec4899",
        # Shadows
        "shadow_sm":    "0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06)",
        "shadow_md":    "0 4px 6px -1px rgba(15,23,42,0.08), 0 2px 4px -2px rgba(15,23,42,0.06)",
    },
    "dark": {
        "bg":           "#0b0f19",
        "surface":      "#161c2d",
        "surface_alt":  "#1e2438",
        "surface_hover":"#252c42",
        "border":       "#2a3246",
        "border_strong":"#3b4561",
        "text":         "#f1f5f9",
        "text_muted":   "#94a3b8",
        "text_subtle":  "#64748b",
        "primary":      "#818cf8",
        "primary_hover":"#a5b4fc",
        "primary_soft": "#1e1b4b",
        "accent":       "#f472b6",
        "success":      "#34d399",
        "warning":      "#fbbf24",
        "danger":       "#f87171",
        "info":         "#22d3ee",
        "grad_1":       "#818cf8",
        "grad_2":       "#a78bfa",
        "grad_3":       "#f472b6",
        "shadow_sm":    "0 1px 2px rgba(0,0,0,0.3)",
        "shadow_md":    "0 4px 6px -1px rgba(0,0,0,0.4)",
    },
}


# ============================================================================
# State
# ============================================================================

def get() -> str:
    return st.session_state.get("theme", "light")


def set_theme(name: str):
    if name in TOKENS:
        st.session_state["theme"] = name


def toggle_theme():
    set_theme("dark" if get() == "light" else "light")


# ============================================================================
# CSS template (uses var(--token) throughout)
# ============================================================================

def _build_css(theme_name: str) -> str:
    t = TOKENS[theme_name]
    vars_block = "\n    ".join(f"--{k.replace('_','-')}: {v};" for k, v in t.items())

    return f"""
<style>
  :root {{
    {vars_block}
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
  }}

  /* ---- App shell ---- */
  .stApp {{
    background: var(--bg);
    color: var(--text);
  }}
  .main .block-container {{
    max-width: 1100px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
  }}

  /* Hide Streamlit chrome carefully · NEVER hide parents of the
     sidebar toggle (e.g. stToolbar contains it in newer versions) */
  [data-testid="stHeader"] {{
    background: transparent !important;
    height: auto;
  }}
  [data-testid="stDeployButton"] {{ display: none !important; }}
  footer {{ visibility: hidden; }}

  /* Force sidebar toggle to always be visible + fixed-positioned so it
     stays clickable even if Streamlit restructures the header.
     Cover all known variant selectors across Streamlit versions. */
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="stSidebarCollapseButton"],
  [data-testid="collapsedControl"],
  button[kind="header"],
  button[kind="headerNoPadding"] {{
    visibility: visible !important;
    opacity: 1 !important;
    display: block !important;
    pointer-events: auto !important;
    z-index: 9999 !important;
  }}
  /* Fallback anchor: position the collapsed control fixed at top-left */
  [data-testid="stSidebarCollapsedControl"] {{
    position: fixed !important;
    top: 8px !important;
    left: 8px !important;
    background: var(--surface) !important;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 2px;
    box-shadow: var(--shadow-sm);
  }}

  /* ---- Typography ---- */
  h1, h2, h3, h4, h5, h6 {{
    color: var(--text);
    letter-spacing: -0.01em;
    font-weight: 700;
  }}
  h1 {{ font-size: 2em; }}
  h2 {{ font-size: 1.5em; margin-top: 1em; }}
  h3 {{ font-size: 1.2em; }}

  /* ---- Hero banner ---- */
  .ab-hero {{
    padding: 32px 28px;
    border-radius: var(--radius-lg);
    color: #fff;
    background: linear-gradient(135deg, var(--grad-1) 0%, var(--grad-2) 50%, var(--grad-3) 100%);
    margin-bottom: 20px;
    box-shadow: var(--shadow-md);
  }}
  .ab-hero h1 {{ color: #fff !important; margin: 0 0 8px 0; font-size: 2.2em; }}
  .ab-hero p {{ margin: 0; opacity: 0.95; font-size: 1.05em; }}

  /* ---- Cards / surfaces ---- */
  .ab-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    box-shadow: var(--shadow-sm);
  }}

  /* ---- Buttons ---- */
  [data-testid="stButton"] > button,
  [data-testid="stDownloadButton"] > button {{
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    font-weight: 600;
    padding: 6px 14px;
    transition: all 0.15s ease;
  }}
  [data-testid="stButton"] > button:hover,
  [data-testid="stDownloadButton"] > button:hover {{
    border-color: var(--primary);
    color: var(--primary);
    background: var(--primary-soft);
  }}
  [data-testid="stButton"] > button[kind="primary"],
  [data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, var(--grad-1), var(--grad-2)) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 700;
    box-shadow: var(--shadow-sm);
  }}
  [data-testid="stButton"] > button[kind="primary"]:hover {{
    background: linear-gradient(135deg, var(--grad-2), var(--grad-3)) !important;
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }}

  /* ---- Inputs ---- */
  [data-testid="stTextInput"] input,
  [data-testid="stNumberInput"] input,
  [data-testid="stTextArea"] textarea {{
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
  }}

  /* ---- Metrics ---- */
  [data-testid="stMetric"] {{
    background: var(--primary-soft);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 10px 14px;
  }}
  [data-testid="stMetricValue"] {{
    color: var(--primary) !important;
    font-weight: 800 !important;
  }}

  /* ---- Sidebar ---- */
  [data-testid="stSidebar"] {{
    background: var(--surface);
    border-right: 1px solid var(--border);
  }}

  /* ---- Alerts ---- */
  [data-testid="stAlert"] {{
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
  }}

  /* ---- Expanders ---- */
  [data-testid="stExpander"] {{
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background: var(--surface);
  }}
  [data-testid="stExpander"] summary {{
    font-weight: 600;
  }}

  /* ---- Dataframe ---- */
  [data-testid="stDataFrame"] {{
    border-radius: var(--radius-md);
    overflow: hidden;
    border: 1px solid var(--border);
  }}

  /* ---- Dividers ---- */
  hr {{
    border: none;
    height: 1px;
    background: var(--border);
    margin: 1.2em 0;
  }}

  /* ---- File uploader ---- */
  [data-testid="stFileUploaderDropzone"] {{
    background: var(--surface-alt);
    border: 2px dashed var(--border-strong);
    border-radius: var(--radius-md);
  }}

  /* ---- Responsive (mobile) ---- */
  @media (max-width: 640px) {{
    .ab-hero {{ padding: 20px 16px; }}
    .ab-hero h1 {{ font-size: 1.5em; }}
    .main .block-container {{ padding: 1rem; }}
  }}
</style>
"""


# ============================================================================
# Public API
# ============================================================================

def inject():
    """Inject full theme CSS · call once at top of every Streamlit script"""
    st.markdown(_build_css(get()), unsafe_allow_html=True)


def toggle_widget(container=None):
    """Theme toggle button · pass container=st.sidebar etc. or leave None"""
    target = container if container is not None else st.sidebar
    current = get()
    label = "🌙 Dark mode" if current == "light" else "☀ Light mode"
    if target.button(label, use_container_width=True, key="theme_toggle_btn"):
        toggle_theme()
        st.rerun()


def hero(title: str, subtitle: str = ""):
    """Gradient hero banner · use at top of pages"""
    sub_html = f'<p>{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="ab-hero"><h1>{title}</h1>{sub_html}</div>',
        unsafe_allow_html=True,
    )
