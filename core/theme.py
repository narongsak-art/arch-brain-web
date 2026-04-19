"""Minimal Thai editorial theme · cream + teak + Bai Jamjuree

Design principles:
- Target data-testid selectors only (never internal .css-* names)
- Warm Thai palette (ไม้สัก · ทอง · กลีบบัว · คราม · ดินเผา)
- Bai Jamjuree for display + Sarabun for body (Google Fonts)
- One theme only (no light/dark switching · keep it focused)
- ~150 lines · small enough to fully understand
"""

import streamlit as st


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap');

:root {
  --cream: #faf7f0;
  --sand: #f4efe3;
  --border: #e5dfcf;
  --border-strong: #c9bfa3;
  --teak: #8b5a2b;
  --teak-hover: #6d4621;
  --teak-soft: #f0e6d8;
  --gold: #c9a961;
  --terra: #c97864;
  --lotus: #e8a5b0;
  --indigo: #4a5d7e;
  --sage: #5b7a5a;
  --ink: #2d1f15;
  --muted: #6b5842;
  --subtle: #9c8970;
  --font-display: 'Bai Jamjuree', 'Sarabun', serif;
  --font-body: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif;
  --radius: 10px;
  --shadow-sm: 0 1px 2px rgba(45,31,21,0.05), 0 1px 3px rgba(45,31,21,0.08);
  --shadow-md: 0 4px 12px -2px rgba(45,31,21,0.10), 0 2px 4px -2px rgba(45,31,21,0.06);
}

html, body { font-family: var(--font-body); }
.stApp, .stApp * { font-family: var(--font-body); }
.stApp { background: var(--cream); color: var(--ink); }

.main .block-container {
  max-width: 960px;
  padding-top: 1.5rem;
  padding-bottom: 3rem;
}

/* Hide Streamlit chrome but KEEP sidebar toggle reachable */
[data-testid="stHeader"] { background: transparent !important; height: auto; }
[data-testid="stDeployButton"] { display: none !important; }
footer { visibility: hidden; }

/* Force-show sidebar toggle across all Streamlit versions */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[kind="header"],
button[kind="headerNoPadding"] {
  visibility: visible !important;
  display: block !important;
  z-index: 9999 !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display);
  color: var(--ink);
  letter-spacing: -0.015em;
  font-weight: 700;
}
h1 { font-size: 2.6em; line-height: 1.1; }
h2 { font-size: 1.8em; margin-top: 1em; }
h3 { font-size: 1.3em; }

/* Eyebrow · small-caps lead line */
.eyebrow {
  font-family: var(--font-display);
  font-size: 0.82em;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--teak);
  margin-bottom: 6px;
}

/* Hero banner */
.hero {
  padding: 48px 36px;
  margin: 0 0 28px 0;
  color: #fff;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--teak) 0%, var(--gold) 50%, var(--terra) 100%);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}
.hero::after {
  content: "";
  position: absolute; inset: 0;
  background: radial-gradient(circle at 20% 20%, rgba(255,255,255,0.15) 0%, transparent 45%),
              radial-gradient(circle at 80% 80%, rgba(255,255,255,0.10) 0%, transparent 45%);
  pointer-events: none;
}
.hero .eyebrow { color: rgba(255,255,255,0.9); }
.hero h1 { color: #fff !important; margin: 0 0 10px 0; font-size: 2.8em; }
.hero p { margin: 0; opacity: 0.96; font-size: 1.1em; max-width: 640px; position: relative; }

/* Cards */
.card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 22px;
  box-shadow: var(--shadow-sm);
  transition: all 0.15s ease;
}
.card:hover {
  border-color: var(--teak);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

/* Buttons · Thai-teak primary */
[data-testid="stBaseButton-primary"] {
  background: var(--teak) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600;
}
[data-testid="stBaseButton-primary"]:hover {
  background: var(--teak-hover) !important;
  box-shadow: var(--shadow-md);
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
  background: #fff;
  border-color: var(--border) !important;
  color: var(--ink) !important;
}

/* Metrics */
[data-testid="stMetric"] {
  background: var(--sand);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
}
[data-testid="stMetricValue"] {
  color: var(--teak) !important;
  font-family: var(--font-display) !important;
  font-weight: 700 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: #fff;
  border-right: 1px solid var(--border);
}

/* Tabs (used sparingly · only 3) */
[data-baseweb="tab-list"] {
  background: var(--sand);
  border-radius: var(--radius);
  padding: 4px;
  gap: 4px;
}
[data-baseweb="tab"] { font-weight: 600; }
[aria-selected="true"] { background: #fff !important; color: var(--teak) !important; }

/* Dividers */
hr { border: none; height: 1px; background: var(--border); margin: 1.2em 0; }

/* Responsive */
@media (max-width: 640px) {
  .hero { padding: 28px 20px; }
  .hero h1 { font-size: 1.8em; }
  h1 { font-size: 1.6em; }
  h2 { font-size: 1.3em; }
}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str = "", eyebrow: str = ""):
    parts = ['<div class="hero">']
    if eyebrow:
        parts.append(f'<div class="eyebrow">{eyebrow}</div>')
    parts.append(f"<h1>{title}</h1>")
    if subtitle:
        parts.append(f"<p>{subtitle}</p>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
