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

# Thai editorial palette · inspired by drafted.ai minimalism + Thai warmth
# - Cream/sand bg (like old paper · editorial feel)
# - Teak brown primary (ไม้สัก · warm, confident)
# - Lotus pink accent (กลีบบัว · subtle Thai)
# - Indigo info (คราม · traditional Thai dye)
# - Gold highlight (ทอง · auspicious)
TOKENS = {
    "light": {
        # Surfaces — warm Thai cream tones
        "bg":           "#faf7f0",   # ครีมอ่อน · paper white
        "surface":      "#ffffff",
        "surface_alt":  "#f4efe3",   # sand
        "surface_hover":"#ede6d4",   # warm beige
        "border":       "#e5dfcf",   # faded parchment
        "border_strong":"#c9bfa3",   # teak-ish border
        # Text — warm dark (not pure black)
        "text":         "#2d1f15",   # deep teak brown
        "text_muted":   "#6b5842",   # brown 60%
        "text_subtle":  "#9c8970",   # brown 40%
        # Brand — teak + lotus + indigo Thai heritage palette
        "primary":      "#8b5a2b",   # teak brown (ไม้สัก)
        "primary_hover":"#6d4621",
        "primary_soft": "#f0e6d8",
        "accent":       "#c97864",   # terracotta (ดินเผา)
        # Feedback
        "success":      "#5b7a5a",   # sage green (ใบข่า)
        "warning":      "#c9a961",   # gold (ทอง)
        "danger":       "#a8432e",   # brick red (อิฐ)
        "info":         "#4a5d7e",   # indigo (คราม)
        # Hero gradient — warm Thai sunset/evening
        "grad_1":       "#8b5a2b",   # teak
        "grad_2":       "#c9a961",   # gold
        "grad_3":       "#c97864",   # terracotta
        # Shadows — softer, warmer
        "shadow_sm":    "0 1px 2px rgba(45,31,21,0.05), 0 1px 3px rgba(45,31,21,0.08)",
        "shadow_md":    "0 4px 12px -2px rgba(45,31,21,0.10), 0 2px 4px -2px rgba(45,31,21,0.06)",
    },
    "dark": {
        # Dark Thai · obsidian + teak accents
        "bg":           "#1a1410",   # very dark brown
        "surface":      "#2a1f17",   # dark teak
        "surface_alt":  "#3a2c20",
        "surface_hover":"#4a382a",
        "border":       "#4a382a",
        "border_strong":"#6b5842",
        "text":         "#f5ecd9",   # cream on dark
        "text_muted":   "#b8a589",
        "text_subtle":  "#8a7860",
        "primary":      "#c9a961",   # gold (ทอง) · glows on dark
        "primary_hover":"#e5c77c",
        "primary_soft": "#3d2f1e",
        "accent":       "#e8a5b0",   # lotus pink (กลีบบัว) · soft glow
        "success":      "#8cb088",
        "warning":      "#e5c77c",
        "danger":       "#d97060",
        "info":         "#8ba3c4",
        "grad_1":       "#c9a961",
        "grad_2":       "#e8a5b0",
        "grad_3":       "#8ba3c4",
        "shadow_sm":    "0 1px 2px rgba(0,0,0,0.4)",
        "shadow_md":    "0 4px 12px -2px rgba(0,0,0,0.5)",
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
  /* Thai editorial fonts · Bai Jamjuree (modern Thai serif-sans for display)
     + Sarabun (body) + Playfair Display (Latin display fallback) */
  @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@500;600;700&family=Sarabun:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700;800;900&display=swap');

  :root {{
    {vars_block}
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --font-display: 'Bai Jamjuree', 'Playfair Display', 'Sarabun', Georgia, serif;
    --font-body: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif;
  }}

  html, body {{ font-family: var(--font-body); }}
  .stApp, .stApp * {{ font-family: var(--font-body); }}

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

  /* ---- Typography · editorial Thai feel ---- */
  h1, h2, h3, h4, h5, h6 {{
    color: var(--text);
    font-family: var(--font-display);
    letter-spacing: -0.015em;
    font-weight: 700;
  }}
  h1 {{ font-size: 2.4em; line-height: 1.15; }}
  h2 {{ font-size: 1.75em; margin-top: 1em; font-weight: 600; }}
  h3 {{ font-size: 1.3em; font-weight: 600; }}
  h4 {{ font-weight: 600; }}

  /* ---- Hero banner · Thai editorial style ---- */
  .ab-hero {{
    padding: 48px 36px;
    border-radius: var(--radius-lg);
    color: #fff;
    background:
      radial-gradient(circle at 15% 20%, rgba(255,255,255,0.12) 0%, transparent 40%),
      radial-gradient(circle at 85% 80%, rgba(255,255,255,0.08) 0%, transparent 40%),
      linear-gradient(135deg, var(--grad-1) 0%, var(--grad-2) 50%, var(--grad-3) 100%);
    margin-bottom: 24px;
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
  }}
  .ab-hero h1 {{
    color: #fff !important;
    margin: 0 0 10px 0;
    font-size: 2.6em;
    font-weight: 700;
    font-family: var(--font-display);
    letter-spacing: -0.02em;
  }}
  .ab-hero p {{
    margin: 0;
    opacity: 0.96;
    font-size: 1.1em;
    font-family: var(--font-body);
    max-width: 640px;
  }}

  /* Editorial small-caps lead (for use above a heading) */
  .ab-eyebrow {{
    font-family: var(--font-display);
    font-size: 0.85em;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--primary);
    margin-bottom: 6px;
  }}

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


def hero(title: str, subtitle: str = "", eyebrow: str = ""):
    """Gradient hero banner · optional eyebrow small-caps line on top

    Usage:
        theme.hero("สมองจำลอง", "วิเคราะห์บ้านไทย", eyebrow="Architect's Studio")
    """
    parts = ['<div class="ab-hero">']
    if eyebrow:
        parts.append(f'<div class="ab-eyebrow">{eyebrow}</div>')
    parts.append(f"<h1>{title}</h1>")
    if subtitle:
        parts.append(f"<p>{subtitle}</p>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
