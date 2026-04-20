"""
สมองจำลองของสถาปนิก · v6
Thai Architect's Studio · minimal sidebar-first rebuild

Layout:
  SIDEBAR  · brand · view switcher · AI config · project form + Analyze
  MAIN     · output only (welcome / result / gallery / explore detail)

3 views:
  🎨 Create    · form in sidebar → analyze → result in main
  📚 Studio    · gallery of past analyses
  🌐 Explore   · community + KG browse (with detail view)

Files: app.py (this · UI/flow) + brain.py (AI + rendering)
"""

import json
import time
from datetime import datetime

import streamlit as st

import brain


# =============================================================================
# Config
# =============================================================================

st.set_page_config(
    page_title="สมองจำลอง · Thai Architect's Studio",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Theme · embedded CSS (no separate module)
# =============================================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap');

:root {
  /* Softer, more editorial palette */
  --cream: #fbf9f3;
  --sand: #f5f0e4;
  --white: #ffffff;
  --border: #ebe4d2;
  --border-strong: #d8cfb9;
  --teak: #7a4e24;
  --teak-hover: #5d3a1a;
  --teak-soft: #f2ead9;
  --gold: #b89755;
  --terra: #b16a57;
  --sage: #6b7f64;
  --ink: #241a11;
  --muted: #6e5d48;
  --subtle: #a89879;
  --font-display: 'Bai Jamjuree', 'Sarabun', serif;
  --font-body: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif;
  --radius-sm: 8px;
  --radius: 12px;
  --radius-lg: 16px;
  --shadow-xs: 0 1px 2px rgba(36,26,17,0.04);
  --shadow-sm: 0 1px 3px rgba(36,26,17,0.06), 0 1px 2px rgba(36,26,17,0.04);
  --shadow-md: 0 4px 10px -2px rgba(36,26,17,0.08), 0 2px 6px -2px rgba(36,26,17,0.05);
  --shadow-lg: 0 12px 32px -8px rgba(36,26,17,0.12), 0 6px 16px -4px rgba(36,26,17,0.06);
  --transition: 180ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Base */
html, body { font-family: var(--font-body); }
.stApp, .stApp * { font-family: var(--font-body); }
.stApp { background: var(--cream); color: var(--ink); }
.main .block-container {
  max-width: 1040px;
  padding-top: 1.8rem;
  padding-bottom: 4rem;
}

/* Streamlit chrome */
[data-testid="stHeader"] { background: transparent !important; height: auto; }
[data-testid="stDeployButton"] { display: none !important; }
footer { visibility: hidden; }
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[kind="header"], button[kind="headerNoPadding"] {
  visibility: visible !important; display: block !important; z-index: 9999 !important;
}

/* Typography · refined scale + more breathing room */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display); color: var(--ink);
  letter-spacing: -0.02em; font-weight: 700;
}
h1 { font-size: 2.4em; line-height: 1.12; margin: 0 0 0.5em 0; }
h2 { font-size: 1.55em; line-height: 1.25; margin: 1.4em 0 0.6em 0; font-weight: 650; }
h3 { font-size: 1.2em; line-height: 1.3; margin: 1em 0 0.4em 0; font-weight: 600; }
p { line-height: 1.65; color: var(--ink); }

.eyebrow {
  font-family: var(--font-display);
  font-size: 0.78em;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--teak);
  margin-bottom: 4px;
}

/* Hero · more refined, layered */
.hero {
  padding: 56px 40px 52px;
  margin: 0 0 32px 0;
  color: #fff;
  border-radius: var(--radius-lg);
  background:
    linear-gradient(135deg, rgba(255,255,255,0.06) 0%, transparent 30%),
    linear-gradient(135deg, var(--teak) 0%, #a07240 55%, var(--terra) 100%);
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: ""; position: absolute; top: 0; right: 0;
  width: 360px; height: 360px; opacity: 0.08;
  background-image:
    repeating-linear-gradient(45deg, #fff 0 1px, transparent 1px 14px);
  pointer-events: none;
}
.hero::after {
  content: ""; position: absolute; inset: 0;
  background:
    radial-gradient(ellipse at 15% 25%, rgba(255,255,255,0.14) 0%, transparent 45%),
    radial-gradient(ellipse at 85% 75%, rgba(255,255,255,0.08) 0%, transparent 50%);
  pointer-events: none;
}
.hero .eyebrow { color: rgba(255,255,255,0.82); position: relative; }
.hero h1 {
  color: #fff !important;
  margin: 0 0 10px 0;
  font-size: 2.5em;
  letter-spacing: -0.025em;
  position: relative;
}
.hero p {
  margin: 0;
  color: rgba(255,255,255,0.93);
  font-size: 1.08em;
  line-height: 1.55;
  max-width: 620px;
  position: relative;
}

/* Page header (cleaner · for Studio/Explore · no hero gradient) */
.page-header {
  margin: 6px 0 28px 0;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
}
.page-header h1 {
  font-size: 2em;
  margin: 2px 0 4px 0;
}
.page-header p {
  color: var(--muted);
  margin: 0;
  font-size: 1em;
}

/* Cards · gentler */
.card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 22px;
  box-shadow: var(--shadow-xs);
  transition: all var(--transition);
  height: 100%;
}
.card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

/* Feature card (welcome state) */
.feat-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px 22px 20px;
  height: 100%;
  transition: all var(--transition);
}
.feat-card:hover {
  border-color: var(--teak-soft);
  box-shadow: var(--shadow-sm);
}
.feat-card .feat-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 44px; height: 44px;
  background: var(--teak-soft);
  color: var(--teak);
  border-radius: var(--radius-sm);
  font-size: 1.4em;
  margin-bottom: 12px;
}
.feat-card h4 {
  margin: 0 0 4px 0;
  font-size: 1.02em;
  font-family: var(--font-display);
  color: var(--ink);
  font-weight: 700;
}
.feat-card p {
  margin: 0;
  color: var(--muted);
  font-size: 0.88em;
  line-height: 1.5;
}

/* Design card (Studio gallery) */
.design-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  transition: all var(--transition);
  height: 100%;
  position: relative;
  overflow: hidden;
}
.design-card:hover {
  border-color: var(--teak-soft);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.design-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--teak) 0%, var(--gold) 100%);
  opacity: 0;
  transition: opacity var(--transition);
}
.design-card:hover::before { opacity: 1; }

.design-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.04em;
  line-height: 1.3;
  margin: 0 0 8px 0;
  color: var(--ink);
  padding-right: 60px; /* space for feasibility badge */
}
.design-score {
  font-family: var(--font-display);
  font-size: 2em;
  font-weight: 700;
  color: var(--teak);
  line-height: 1;
  letter-spacing: -0.02em;
}
.design-score small {
  font-family: var(--font-body);
  font-size: 0.45em;
  color: var(--subtle);
  font-weight: 400;
  margin-left: 2px;
}
.design-meta {
  font-size: 0.82em;
  color: var(--muted);
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.design-meta .sep { color: var(--subtle); }
.design-badge {
  position: absolute;
  top: 16px; right: 16px;
  font-size: 0.72em;
  background: var(--sand);
  color: var(--muted);
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  font-weight: 500;
}

/* Explore card */
.ex-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px 18px;
  transition: all var(--transition);
  height: 100%;
}
.ex-card:hover {
  border-color: var(--teak-soft);
  box-shadow: var(--shadow-sm);
}
.ex-type {
  font-size: 0.7em;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--teak);
  font-weight: 600;
}
.ex-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1em;
  line-height: 1.3;
  margin: 4px 0 8px 0;
  color: var(--ink);
}
.ex-preview {
  color: var(--muted);
  font-size: 0.86em;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ex-layers {
  font-size: 0.72em;
  color: var(--subtle);
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}

/* Tag pill */
.tag-pill {
  display: inline-block;
  background: var(--teak-soft);
  color: var(--teak);
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.76em;
  font-weight: 500;
  margin: 0 4px 4px 0;
}

/* Primary button · refined teak */
[data-testid="stBaseButton-primary"] {
  background: var(--teak) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em;
  padding: 10px 20px !important;
  border-radius: var(--radius-sm) !important;
  transition: all var(--transition) !important;
  box-shadow: var(--shadow-xs);
}
[data-testid="stBaseButton-primary"]:hover {
  background: var(--teak-hover) !important;
  box-shadow: var(--shadow-md) !important;
  transform: translateY(-1px);
}
[data-testid="stBaseButton-primary"]:active {
  transform: translateY(0);
  box-shadow: var(--shadow-xs) !important;
}

/* Secondary buttons · cleaner */
[data-testid="stBaseButton-secondary"] {
  background: var(--white) !important;
  border: 1px solid var(--border) !important;
  color: var(--ink) !important;
  border-radius: var(--radius-sm) !important;
  transition: all var(--transition) !important;
}
[data-testid="stBaseButton-secondary"]:hover {
  border-color: var(--teak) !important;
  color: var(--teak) !important;
  background: var(--teak-soft) !important;
}

/* Metrics · cleaner */
[data-testid="stMetric"] {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 18px;
  box-shadow: var(--shadow-xs);
}
[data-testid="stMetricLabel"] {
  font-size: 0.82em !important;
  color: var(--muted) !important;
  font-weight: 500 !important;
  letter-spacing: 0.02em;
}
[data-testid="stMetricValue"] {
  color: var(--ink) !important;
  font-family: var(--font-display) !important;
  font-weight: 700 !important;
  font-size: 1.4em !important;
}

/* Inputs · softer */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] > div > div {
  background: var(--white) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--ink) !important;
  transition: border-color var(--transition);
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--teak) !important;
  box-shadow: 0 0 0 3px rgba(122,78,36,0.12) !important;
}

/* Sidebar · elegant */
[data-testid="stSidebar"] {
  background: var(--white);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stRadio label {
  font-weight: 500;
}
[data-testid="stSidebar"] hr {
  margin: 0.8em 0;
}

/* Expanders · softer borders */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  background: var(--white);
}
[data-testid="stExpander"] summary {
  font-weight: 600;
  padding: 10px 14px !important;
}

/* Dividers */
hr {
  border: none;
  height: 1px;
  background: var(--border);
  margin: 1.4em 0;
}

/* Alerts · warmer */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  padding: 14px 18px !important;
}

/* Status widget · cleaner */
[data-testid="stStatusWidget"] {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
}

/* Responsive */
@media (max-width: 768px) {
  .main .block-container { padding: 1rem 1.2rem 2rem; }
  .hero { padding: 36px 24px 32px; }
  .hero h1 { font-size: 1.8em; }
  h1 { font-size: 1.7em; }
  h2 { font-size: 1.35em; }
}

/* Preset showcase card · visual · gallery-style */
.preset-tile {
  position: relative;
  aspect-ratio: 4 / 3;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all 260ms cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: block;
}
.preset-tile:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px) scale(1.01);
}
.preset-tile::before {
  content: "";
  position: absolute; inset: 0;
  background-image:
    radial-gradient(circle at 30% 20%, rgba(255,255,255,0.20) 0%, transparent 45%),
    radial-gradient(circle at 85% 85%, rgba(0,0,0,0.18) 0%, transparent 50%);
  pointer-events: none;
  z-index: 1;
}
.preset-tile::after {
  content: "";
  position: absolute; inset: 0;
  background-image: repeating-linear-gradient(
    45deg, rgba(255,255,255,0.06) 0 1px, transparent 1px 16px);
  pointer-events: none;
  z-index: 1;
}
.preset-tile .preset-content {
  position: relative; z-index: 2;
  padding: 22px 22px 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #fff;
}
.preset-tile .preset-icon {
  font-size: 2.4em;
  line-height: 1;
  opacity: 0.92;
}
.preset-tile .preset-info h4 {
  color: #fff !important;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.3em;
  margin: 0 0 4px 0;
  letter-spacing: -0.01em;
}
.preset-tile .preset-info .tagline {
  font-size: 0.86em;
  opacity: 0.88;
  margin-bottom: 10px;
}
.preset-tile .preset-info .meta {
  font-size: 0.78em;
  opacity: 0.78;
  border-top: 1px solid rgba(255,255,255,0.25);
  padding-top: 10px;
  line-height: 1.5;
}

/* Compass · visual orientation indicator */
.compass {
  position: relative;
  width: 96px; height: 96px;
  border: 1.5px solid var(--border-strong);
  border-radius: 50%;
  margin: 0 auto 10px auto;
  background: var(--white);
  box-shadow: var(--shadow-xs);
}
.compass::before {
  content: "N";
  position: absolute;
  top: -1px; left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.76em;
  color: var(--teak);
  background: var(--white);
  padding: 0 4px;
  line-height: 1;
}
.compass .needle {
  position: absolute;
  left: 50%; top: 50%;
  width: 2px; height: 40%;
  background: linear-gradient(to top, var(--terra) 0%, var(--teak) 100%);
  transform-origin: bottom center;
  transform: translate(-50%, -100%) rotate(0deg);
  transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 2px;
}
.compass .needle::after {
  content: "";
  position: absolute;
  top: -4px; left: -3px;
  width: 0; height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 6px solid var(--teak);
}
.compass .center {
  position: absolute;
  top: 50%; left: 50%;
  width: 6px; height: 6px;
  background: var(--teak);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}
.compass-label {
  text-align: center;
  font-size: 0.85em;
  color: var(--muted);
  margin-top: -4px;
}

/* Priority pills (mini chips) */
.prio-pill {
  display: inline-block;
  background: var(--white);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.75em;
  font-weight: 500;
  margin: 0 4px 4px 0;
}
.prio-pill.on {
  background: var(--teak-soft);
  border-color: var(--teak);
  color: var(--teak);
}

/* Preset chosen ribbon · for when a preset is active */
.preset-active-ribbon {
  background: var(--sand);
  border: 1px solid var(--border);
  border-left: 4px solid var(--teak);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
  gap: 14px;
}
.preset-active-ribbon .icon {
  font-size: 1.8em;
}
.preset-active-ribbon .text {
  flex: 1;
}
.preset-active-ribbon .text strong {
  font-family: var(--font-display);
  font-size: 1.05em;
  color: var(--ink);
}
.preset-active-ribbon .text div {
  font-size: 0.86em;
  color: var(--muted);
  margin-top: 2px;
}

/* Subtle page-load fade-in */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.hero, .page-header, .card, .feat-card, .design-card, .ex-card, .preset-tile, .preset-active-ribbon {
  animation: fadeInUp 0.35s ease-out;
}
</style>
"""


# =============================================================================
# Presets (form templates)
# =============================================================================

PRESETS = {
    "townhome": {
        "label": "ทาวน์เฮาส์",
        "tagline": "บ้านในเมือง · พื้นที่จำกัด",
        "meta": "4×16 ม. · 2 ชั้น · 3 ห้องนอน · 3 ลบ.",
        "icon": "🏘",
        "gradient": "linear-gradient(135deg, #c9a961 0%, #b89755 100%)",
        "data": {"name": "ทาวน์เฮาส์", "land_w": 4.0, "land_d": 16.0,
                 "province": "กรุงเทพมหานคร", "zone": "ย.4", "street_w": 6.0,
                 "family_size": 4, "has_elderly": "ไม่", "floors": "2",
                 "bedrooms": "3", "budget": 3.0, "fengshui": "น้อย",
                 "special": ""},
    },
    "small": {
        "label": "บ้านเดี่ยวเล็ก",
        "tagline": "คู่แต่งงาน · ครอบครัวเริ่มต้น",
        "meta": "15×20 ม. · 2 ชั้น · 3 ห้องนอน · 5 ลบ.",
        "icon": "🏠",
        "gradient": "linear-gradient(135deg, #6b7f64 0%, #5a6e53 100%)",
        "data": {"name": "บ้านเดี่ยว-S", "land_w": 15.0, "land_d": 20.0,
                 "province": "นนทบุรี", "zone": "ย.3", "street_w": 6.0,
                 "family_size": 4, "has_elderly": "ไม่", "floors": "2",
                 "bedrooms": "3", "budget": 5.0, "fengshui": "ปานกลาง",
                 "special": ""},
    },
    "large": {
        "label": "บ้านเดี่ยวใหญ่",
        "tagline": "ครอบครัวหลายรุ่น",
        "meta": "20×30 ม. · 2 ชั้น · 4 ห้องนอน + ห้องพระ · 12 ลบ.",
        "icon": "🏡",
        "gradient": "linear-gradient(135deg, #7a4e24 0%, #5d3a1a 100%)",
        "data": {"name": "บ้านเดี่ยว-L", "land_w": 20.0, "land_d": 30.0,
                 "province": "กรุงเทพมหานคร", "zone": "ย.2", "street_w": 8.0,
                 "family_size": 5, "has_elderly": "ใช่", "floors": "2",
                 "bedrooms": "4", "budget": 12.0, "fengshui": "มาก",
                 "special": "ห้องพระ · ผู้สูงอายุชั้นล่าง · home office"},
    },
    "luxury": {
        "label": "บ้านหรู",
        "tagline": "premium · สระส่วนตัว",
        "meta": "25×40 ม. · 3 ชั้น · 5 ห้องนอน · 25 ลบ.",
        "icon": "🏛",
        "gradient": "linear-gradient(135deg, #241a11 0%, #4a3622 100%)",
        "data": {"name": "บ้านหรู", "land_w": 25.0, "land_d": 40.0,
                 "province": "กรุงเทพมหานคร", "zone": "ย.1", "street_w": 10.0,
                 "family_size": 6, "has_elderly": "ใช่", "floors": "3",
                 "bedrooms": "5", "budget": 25.0, "fengshui": "มาก",
                 "special": "สระว่ายน้ำ · ลิฟต์ · ห้องพระ · walk-in"},
    },
    "compact": {
        "label": "บ้านเล็ก กทม.",
        "tagline": "ลอตแคบ · 3 ชั้น",
        "meta": "8×12 ม. · 3 ชั้น · 2 ห้องนอน · 4 ลบ.",
        "icon": "🏙",
        "gradient": "linear-gradient(135deg, #b16a57 0%, #8e5143 100%)",
        "data": {"name": "บ้านเล็ก", "land_w": 8.0, "land_d": 12.0,
                 "province": "กรุงเทพมหานคร", "zone": "ย.5", "street_w": 6.0,
                 "family_size": 2, "has_elderly": "ไม่", "floors": "3",
                 "bedrooms": "2", "budget": 4.0, "fengshui": "น้อย",
                 "special": "home office 2 คน"},
    },
}

PROVINCES = ["กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี", "สมุทรปราการ",
             "นครปฐม", "เชียงใหม่", "ภูเก็ต", "อื่นๆ"]
ZONES = ["ย.1", "ย.2", "ย.3", "ย.4", "ย.5", "ย.6", "ย.7", "ย.8", "ย.9", "ย.10",
         "พ.1", "พ.2", "ไม่ทราบ"]

FORM_DEFAULTS = {
    # Core
    "name": "บ้าน-A", "land_w": 15.0, "land_d": 20.0,
    "province": "กรุงเทพมหานคร", "zone": "ย.3", "street_w": 6.0,
    "family_size": 4, "has_elderly": "ไม่มี", "floors": "2",
    "bedrooms": "3", "budget": 8.0, "fengshui": "ปานกลาง", "special": "",
    # Professional (new · for architects)
    "orientation": "ใต้",      # plot's main facing: N/E/S/W
    "topography": "ราบเรียบ",   # ราบ · ลาดเอียง · ลาดชัน
    "adjacent": "",             # context: neighbors · road · canal
    "priority": ["งบ", "คุณภาพ"],  # multiselect: cost/quality/time/sustain
    "timeline": "1 ปี",         # project duration estimate
    "grade": "มาตรฐาน",         # construction grade: eco/std/premium
}

ORIENTATIONS = ["เหนือ", "ตะวันออก", "ใต้", "ตะวันตก",
                "ตะวันออกเฉียงเหนือ", "ตะวันออกเฉียงใต้",
                "ตะวันตกเฉียงเหนือ", "ตะวันตกเฉียงใต้"]
ORIENTATION_COMPASS = {
    "เหนือ": ("N", 0), "ตะวันออกเฉียงเหนือ": ("NE", 45),
    "ตะวันออก": ("E", 90), "ตะวันออกเฉียงใต้": ("SE", 135),
    "ใต้": ("S", 180), "ตะวันตกเฉียงใต้": ("SW", 225),
    "ตะวันตก": ("W", 270), "ตะวันตกเฉียงเหนือ": ("NW", 315),
}

TOPOGRAPHY = ["ราบเรียบ", "ลาดเอียงเล็กน้อย", "ลาดชัน", "ลุ่มต่ำ"]
PRIORITIES = ["งบ", "คุณภาพ", "เวลา", "ความยั่งยืน", "ดีไซน์"]
GRADES = ["ประหยัด", "มาตรฐาน", "ลักชัวรี"]
TIMELINES = ["6 เดือน", "1 ปี", "1.5 ปี", "2 ปี", "> 2 ปี"]


def _apply_preset():
    key = st.session_state.get("form_preset", "_custom")
    if key == "_custom" or key not in PRESETS:
        return
    data = PRESETS[key]["data"]
    for k, v in data.items():
        sk = f"form_{k}"
        # UI uses "มี/ไม่มี" but data uses "ใช่/ไม่"
        if k == "has_elderly":
            st.session_state[sk] = "มี" if v == "ใช่" else "ไม่มี"
        else:
            st.session_state[sk] = v


def apply_preset_direct(key: str):
    """Called from welcome-state big card buttons · also flips preset dropdown"""
    st.session_state["form_preset"] = key
    _apply_preset()


def _init_form_state():
    for k, v in FORM_DEFAULTS.items():
        sk = f"form_{k}"
        st.session_state.setdefault(sk, v)


# =============================================================================
# Hero helper
# =============================================================================

def hero(title: str, subtitle: str = "", eyebrow: str = ""):
    parts = ['<div class="hero">']
    if eyebrow:
        parts.append(f'<div class="eyebrow">{eyebrow}</div>')
    parts.append(f"<h1>{title}</h1>")
    if subtitle:
        parts.append(f"<p>{subtitle}</p>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


# =============================================================================
# Sidebar
# =============================================================================

def render_sidebar() -> tuple[str, str, str, str, dict, bytes | None]:
    """Returns (view, provider, api_key, model, project_data, image_bytes)"""
    _init_form_state()

    with st.sidebar:
        # Brand
        st.markdown(
            '<div style="padding: 6px 0 14px 0;">'
            '<div class="eyebrow">THAI STUDIO</div>'
            '<div style="font-family: var(--font-display); font-size: 1.3em; '
            'font-weight: 700; color: var(--ink);">สมองจำลอง</div>'
            '<div style="font-size: 0.8em; color: var(--muted);">'
            'ของสถาปนิก · v6</div></div>',
            unsafe_allow_html=True,
        )

        # View switcher
        view = st.radio(
            "View",
            options=["create", "studio", "explore"],
            format_func=lambda v: {
                "create":  "🎨 Create",
                "studio":  "📚 My Studio",
                "explore": "🌐 Explore",
            }[v],
            label_visibility="collapsed",
            key="_view",
        )

        st.divider()

        # AI config
        key_present = bool(
            st.session_state.get("_gemini_key") or
            st.session_state.get("_claude_key")
        )
        with st.expander("⚙ AI Settings", expanded=not key_present):
            provider = st.radio(
                "Provider",
                options=["gemini", "claude"],
                format_func=lambda x: {"gemini": "🆓 Gemini (ฟรี)",
                                        "claude": "💎 Claude"}[x],
                horizontal=True,
                key="_provider",
            )
            if provider == "gemini":
                api_key = st.text_input(
                    "Gemini API Key", type="password",
                    placeholder="AIza...", key="_gemini_key",
                )
                st.caption("📎 [รับ Gemini ฟรี](https://aistudio.google.com/apikey)")
                model = st.selectbox(
                    "Model",
                    options=list(brain.GEMINI_MODELS.keys()),
                    format_func=lambda x: brain.GEMINI_MODELS[x],
                    key="_gemini_model",
                )
            else:
                api_key = st.text_input(
                    "Claude API Key", type="password",
                    placeholder="sk-ant-...", key="_claude_key",
                )
                st.caption("📎 [สมัคร Claude](https://console.anthropic.com)")
                model = "claude-sonnet-4-6"

        # Project form · only in Create view
        project_data = None
        image_bytes = None
        if view == "create":
            st.divider()
            st.markdown(
                '<div class="eyebrow">PROJECT BRIEF</div>'
                '<div style="font-family: var(--font-display); font-size: 1.1em; '
                'font-weight: 700; margin-bottom: 6px;">ข้อมูลโปรเจค</div>',
                unsafe_allow_html=True,
            )

            st.selectbox(
                "⚡ Quick preset (optional)",
                options=["_custom"] + list(PRESETS.keys()),
                format_func=lambda k: "— เลือก template —" if k == "_custom"
                    else f"{PRESETS[k]['icon']} {PRESETS[k]['label']} · {PRESETS[k]['meta']}",
                key="form_preset",
                on_change=_apply_preset,
            )

            st.text_input("ชื่อ", key="form_name")
            c1, c2 = st.columns(2)
            c1.number_input("กว้าง (ม.)", 3.0, 100.0, step=0.5, key="form_land_w")
            c2.number_input("ลึก (ม.)", 3.0, 100.0, step=0.5, key="form_land_d")

            st.selectbox("จังหวัด", PROVINCES, key="form_province")
            st.selectbox("สีผังเมือง", ZONES, key="form_zone",
                         help="ย. = ที่อยู่อาศัย · พ. = พาณิชย์")
            st.number_input("ถนน (ม.)", 1.0, 50.0, step=0.5, key="form_street_w")

            st.divider()
            st.slider("สมาชิก", 1, 15, key="form_family_size")
            st.radio("ผู้สูงอายุ", ["ไม่มี", "มี"], horizontal=True, key="form_has_elderly")
            c3, c4 = st.columns(2)
            c3.selectbox("ชั้น", ["1", "2", "3", "4+"], key="form_floors")
            c4.selectbox("ห้องนอน", ["1", "2", "3", "4", "5+"], key="form_bedrooms")
            st.number_input("งบ (ลบ.)", 0.5, 200.0, step=0.5, key="form_budget")
            st.selectbox("ฮวงจุ้ย", ["มาก", "ปานกลาง", "น้อย", "ไม่สน"],
                         key="form_fengshui")
            st.text_area(
                "ข้อพิเศษ",
                placeholder="เช่น · ห้องพระ · สระ · home office",
                height=80, key="form_special",
            )

            # Professional expander · advanced architect fields
            with st.expander("🧭 Architect detail", expanded=False):
                st.selectbox(
                    "ทิศที่ดิน (ด้านยาวหันไปทาง)",
                    ORIENTATIONS, key="form_orientation",
                    help="ทิศที่ด้านยาวของที่ดินหันไป · กำหนด sun path + ventilation",
                )
                # Visual compass
                direction = st.session_state.get("form_orientation", "ใต้")
                _, rot = ORIENTATION_COMPASS.get(direction, ("S", 180))
                st.markdown(
                    f'<div class="compass">'
                    f'<div class="needle" style="transform: translate(-50%, -100%) rotate({rot}deg);"></div>'
                    f'<div class="center"></div>'
                    f'</div>'
                    f'<div class="compass-label">ด้านยาวหัน <b>{direction}</b></div>',
                    unsafe_allow_html=True,
                )

                st.selectbox("ภูมิประเทศ", TOPOGRAPHY, key="form_topography")
                st.text_area(
                    "บริบทรอบที่ดิน",
                    placeholder="เช่น ทิศเหนือติดถนน · ใต้ติดคลอง · ตะวันตกมีบ้าน 2 ชั้น",
                    height=68,
                    key="form_adjacent",
                )

                st.multiselect(
                    "ลำดับความสำคัญ",
                    PRIORITIES, key="form_priority",
                    help="เลือก 2-3 อันดับสำคัญสุด",
                )
                c5, c6 = st.columns(2)
                c5.selectbox("Grade", GRADES, key="form_grade",
                             help="ระดับงานก่อสร้าง")
                c6.selectbox("Timeline", TIMELINES, key="form_timeline")

            st.divider()
            uploaded = st.file_uploader(
                "📎 แปลน (optional)",
                type=["jpg", "jpeg", "png"], key="form_upload",
            )
            image_bytes = uploaded.getvalue() if uploaded else None
            if image_bytes:
                st.image(image_bytes, use_container_width=True)

            st.divider()
            if not api_key:
                st.warning("👆 ใส่ API Key ด้านบนก่อน")
            else:
                if st.button("🔍 วิเคราะห์โครงการ",
                             type="primary", use_container_width=True,
                             key="_run"):
                    st.session_state["_pending_run"] = True

            # Build project_data
            project_data = {
                # Core
                "name": st.session_state["form_name"],
                "land_w": st.session_state["form_land_w"],
                "land_d": st.session_state["form_land_d"],
                "land_area": st.session_state["form_land_w"] * st.session_state["form_land_d"],
                "province": st.session_state["form_province"],
                "zone": st.session_state["form_zone"],
                "street_w": st.session_state["form_street_w"],
                "family_size": st.session_state["form_family_size"],
                "has_elderly": "ใช่" if st.session_state["form_has_elderly"] == "มี" else "ไม่",
                "floors": st.session_state["form_floors"],
                "bedrooms": st.session_state["form_bedrooms"],
                "budget": st.session_state["form_budget"],
                "fengshui": st.session_state["form_fengshui"],
                "special": st.session_state["form_special"],
                # Professional
                "orientation": st.session_state.get("form_orientation", "ใต้"),
                "topography": st.session_state.get("form_topography", "ราบเรียบ"),
                "adjacent": st.session_state.get("form_adjacent", ""),
                "priority": st.session_state.get("form_priority", []),
                "grade": st.session_state.get("form_grade", "มาตรฐาน"),
                "timeline": st.session_state.get("form_timeline", "1 ปี"),
            }

        # Footer
        st.divider()
        hist_n = len(st.session_state.get("history", []))
        st.caption(f"📚 Session: **{hist_n}** งาน")
        st.caption("⚠ ผลเบื้องต้น · ไม่แทนสถาปนิกใบอนุญาต")

    return view, provider, api_key, model, project_data, image_bytes


# =============================================================================
# Analysis runner
# =============================================================================

def run_analysis(provider: str, api_key: str, model: str,
                 project_data: dict, image_bytes: bytes | None):
    system = brain.build_system_prompt()
    user = brain.build_user_prompt(project_data)

    status = st.status(f"🧠 กำลังวิเคราะห์ด้วย {provider.title()}", expanded=True)
    try:
        status.update(label="📚 โหลด Knowledge Graph · 104 nodes")
        time.sleep(0.1)
        status.update(label="🧠 เรียก AI · 30-60 วินาที")
        t0 = time.time()
        raw = brain.run_ai(provider, api_key, system, user, image_bytes, model)
        elapsed = time.time() - t0

        status.update(label=f"📊 parse · {len(raw):,} chars")
        parsed = brain.extract_json(raw)

        label = f"✅ เสร็จใน {elapsed:.1f} วิ"
        label += " · JSON ✓" if parsed else " · markdown fallback"
        status.update(label=label, state="complete", expanded=False)

        # Save to history
        entry = {
            "id": datetime.now().strftime("%Y%m%d-%H%M%S-%f"),
            "ts": datetime.now().isoformat(),
            "name": project_data.get("name", "-"),
            "province": project_data.get("province", "-"),
            "zone": project_data.get("zone", "-"),
            "land_area": project_data.get("land_area", 0),
            "provider": provider,
            "project_data": project_data,
            "raw_text": raw,
            "result": parsed,
        }
        st.session_state.setdefault("history", [])
        st.session_state["history"].insert(0, entry)
        st.session_state["history"] = st.session_state["history"][:30]

        st.session_state["current"] = entry
    except Exception as e:
        status.update(label=f"❌ ล้มเหลว: {e}", state="error", expanded=True)
        st.error(str(e))


# =============================================================================
# Views
# =============================================================================

def _render_welcome_gallery():
    """Gallery-first welcome: big visual preset tiles · click to start"""
    selected = st.session_state.get("form_preset", "_custom")
    has_preset = selected != "_custom" and selected in PRESETS
    api_key_present = bool(
        st.session_state.get("_gemini_key") or st.session_state.get("_claude_key")
    )

    # Compact hero
    hero("สมองจำลองของสถาปนิก",
         "เลือกแบบบ้านด้านล่าง → AI วิเคราะห์ 5 ชั้นความรู้ → ได้ผลใน ~60 วินาที",
         eyebrow="THAI ARCHITECT'S STUDIO")

    # If preset chosen, show a "ready" ribbon
    if has_preset:
        p = PRESETS[selected]
        st.markdown(
            f'<div class="preset-active-ribbon">'
            f'<div class="icon">{p["icon"]}</div>'
            f'<div class="text">'
            f'<strong>{p["label"]}</strong> · <span style="color:var(--muted);">{p["tagline"]}</span>'
            f'<div>{p["meta"]}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if api_key_present:
            st.success("✅ พร้อมวิเคราะห์ · กด **🔍 วิเคราะห์โครงการ** ที่ sidebar ซ้าย")
        else:
            st.warning("⚠ ใส่ **Gemini API Key** ที่ sidebar ก่อนวิเคราะห์ · "
                       "[รับฟรีที่นี่](https://aistudio.google.com/apikey)")

        st.markdown(
            '<p style="color:var(--muted); font-size:0.9em; margin-top:14px;">'
            'หรือเลือกแบบอื่นด้านล่าง:</p>',
            unsafe_allow_html=True,
        )

    # Section header
    if not has_preset:
        st.markdown(
            '<div class="eyebrow" style="margin-top:8px;">START WITH A TEMPLATE</div>'
            '<h2 style="margin:2px 0 6px 0;">เลือกแบบที่ใกล้เคียงโปรเจคคุณ</h2>'
            '<p style="color:var(--muted); margin:0 0 20px 0;">'
            'กรอกเองใน sidebar ซ้ายก็ได้ · หรือคลิกแบบด้านล่างเพื่อ fill form อัตโนมัติ</p>',
            unsafe_allow_html=True,
        )

    # Big gallery tiles · 2 rows of up to 3 cards
    preset_items = list(PRESETS.items())
    # Row 1: 3 cards
    cols1 = st.columns(3)
    for i, (key, p) in enumerate(preset_items[:3]):
        with cols1[i]:
            _render_preset_tile(key, p, is_selected=(selected == key))

    # Row 2: 2 cards (left-aligned)
    if len(preset_items) > 3:
        cols2 = st.columns(3)
        for i, (key, p) in enumerate(preset_items[3:]):
            with cols2[i]:
                _render_preset_tile(key, p, is_selected=(selected == key))

    # Below tiles: features strip · condensed
    st.markdown('<div style="margin-top: 36px;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="eyebrow">WHAT YOU GET</div>'
        '<h3 style="margin:2px 0 14px 0;">ผลวิเคราะห์ที่ได้</h3>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));'
        'gap: 14px; margin: 0 0 20px 0;">'

        '<div class="feat-card">'
        '<div class="feat-icon">📐</div>'
        '<h4>Metrics ครบ</h4>'
        '<p>FAR · OSR · ระยะร่น · พื้นที่สร้างได้ · ค่าก่อสร้าง</p>'
        '</div>'

        '<div class="feat-card">'
        '<div class="feat-icon">🧩</div>'
        '<h4>5 ชั้นความรู้</h4>'
        '<p>กฎหมาย · วิศวกรรม · ออกแบบ · ไทย · ฮวงจุ้ย</p>'
        '</div>'

        '<div class="feat-card">'
        '<div class="feat-icon">🚪</div>'
        '<h4>วิเคราะห์ห้อง</h4>'
        '<p>ขนาด · ทิศ · ข้อควรระวัง ทีละห้อง</p>'
        '</div>'

        '<div class="feat-card">'
        '<div class="feat-icon">🎯</div>'
        '<h4>Action list</h4>'
        '<p>step · ใครทำ · เมื่อ · Top 3 ประเด็น</p>'
        '</div>'

        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="margin-top:8px; padding:14px 18px; background:var(--sand); '
        'border-left:3px solid var(--teak); border-radius:var(--radius-sm); '
        'color:var(--muted); font-size:0.9em;">'
        '🔒 <strong>Privacy:</strong> API key + ข้อมูลโปรเจค '
        'ไม่ถูกเก็บ · ไม่ใช้ train AI · หายเมื่อปิด tab'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_preset_tile(key: str, p: dict, is_selected: bool = False):
    """Render one big preset tile with gradient background + click-to-select button"""
    border = "3px solid var(--teak)" if is_selected else "1px solid var(--border)"
    badge = (
        '<div style="position:absolute; top:12px; right:12px; background:var(--teak); '
        'color:#fff; padding:4px 10px; border-radius:999px; font-size:0.72em; '
        'font-weight:600; z-index:3;">SELECTED</div>' if is_selected else ''
    )
    st.markdown(
        f'<div class="preset-tile" style="background: {p["gradient"]}; border: {border};">'
        f'{badge}'
        f'<div class="preset-content">'
        f'<div class="preset-icon">{p["icon"]}</div>'
        f'<div class="preset-info">'
        f'<h4>{p["label"]}</h4>'
        f'<div class="tagline">{p["tagline"]}</div>'
        f'<div class="meta">{p["meta"]}</div>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    label = "✓ เลือกแล้ว" if is_selected else "เลือกแบบนี้"
    if st.button(label, key=f"tile_{key}", use_container_width=True,
                 type="primary" if is_selected else "secondary"):
        apply_preset_direct(key)
        st.rerun()


def view_create():
    # Run analysis if pending
    if st.session_state.pop("_pending_run", False):
        pd = st.session_state.get("_project_data")
        img = st.session_state.get("_image_bytes")
        provider = st.session_state.get("_provider", "gemini")
        api_key = (st.session_state.get("_gemini_key")
                   if provider == "gemini"
                   else st.session_state.get("_claude_key"))
        model = st.session_state.get("_gemini_model", "gemini-2.5-flash")
        if pd and api_key:
            run_analysis(provider, api_key, model, pd, img)

    current = st.session_state.get("current")
    if not current:
        _render_welcome_gallery()
        return

    # Show current result
    pd = current["project_data"]
    data = current.get("result")
    raw = current.get("raw_text", "")
    provider = current.get("provider", "ai")

    st.markdown(
        f'<div class="eyebrow">ANALYSIS · {provider.upper()}</div>'
        f'<h1 style="margin-top:4px;">{pd["name"]}</h1>',
        unsafe_allow_html=True,
    )

    if data:
        brain.render(data)
    else:
        st.warning("⚠ AI ไม่ตอบเป็น JSON · แสดง markdown")
        st.markdown(raw)

    # Downloads
    st.divider()
    st.markdown(
        '<div class="eyebrow">EXPORT</div>'
        '<h3 style="margin-top:4px;">📥 ดาวน์โหลด</h3>',
        unsafe_allow_html=True,
    )
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    md_body = brain.to_markdown(data) if data else raw
    full_md = f"""# ผลวิเคราะห์ — {pd['name']}

วันที่: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Provider: {provider.title()}

## ข้อมูลโครงการ
```json
{json.dumps(pd, ensure_ascii=False, indent=2)}
```

{md_body}

---
_สมองจำลองของสถาปนิก · Thai Architect's Studio v6_
"""
    c1, c2, c3 = st.columns(3)
    c1.download_button(
        "📥 Markdown", full_md,
        file_name=f"{pd['name']}-{ts}.md",
        mime="text/markdown", use_container_width=True,
    )
    if data:
        c2.download_button(
            "📋 JSON",
            json.dumps({"project_data": pd, "result": data, "provider": provider,
                        "timestamp": datetime.now().isoformat()},
                       ensure_ascii=False, indent=2),
            file_name=f"{pd['name']}-{ts}.json",
            mime="application/json", use_container_width=True,
        )
    c3.download_button(
        "📝 Raw", raw,
        file_name=f"{pd['name']}-{ts}-raw.txt",
        mime="text/plain", use_container_width=True,
    )


def view_studio():
    hist = st.session_state.get("history", [])

    # Clean page header (no colorful hero)
    st.markdown(
        '<div class="page-header">'
        '<div class="eyebrow">MY STUDIO</div>'
        f'<h1>สตูดิโอของฉัน</h1>'
        f'<p>งานวิเคราะห์ทั้งหมด · {len(hist)} ชิ้น · คลิก <b>เปิด</b> ดูผลอีกครั้ง</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if not hist:
        st.markdown(
            '<div style="text-align:center; padding:60px 20px; '
            'background:var(--white); border:2px dashed var(--border-strong); '
            'border-radius:var(--radius); margin-top:20px;">'
            '<div style="font-size:2.4em; margin-bottom:10px;">✨</div>'
            '<h3 style="margin:0 0 4px 0;">ยังไม่มีงาน</h3>'
            '<p style="color:var(--muted); margin:0;">'
            'ไปที่ <b>🎨 Create</b> · วิเคราะห์โปรเจคแรก · ผลจะเก็บที่นี่อัตโนมัติ</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    cols = st.columns(3)
    for i, entry in enumerate(hist):
        pd = entry["project_data"]
        r = entry.get("result") or {}
        s = r.get("summary") or {}
        feas = s.get("feasibility") or "-"
        feas_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(feas, "❔")
        score = s.get("score", "—")
        try:
            ts = datetime.fromisoformat(entry["ts"]).strftime("%d %b · %H:%M")
        except Exception:
            ts = "-"
        area = pd.get("land_area", 0)

        with cols[i % 3]:
            st.markdown(
                f'<div class="design-card">'
                f'<div class="design-badge">{feas_emoji} {feas}</div>'
                f'<div class="design-title">{entry["name"]}</div>'
                f'<div class="design-score">{score}<small>/100</small></div>'
                f'<div class="design-meta">'
                f'<span>📍 {pd.get("province", "-")[:12]}</span>'
                f'<span class="sep">·</span>'
                f'<span>{pd.get("zone", "-")}</span>'
                f'<span class="sep">·</span>'
                f'<span>{area:.0f} ตร.ม.</span>'
                f'</div>'
                f'<div class="design-meta" style="margin-top:4px;">'
                f'<span>🕐 {ts}</span>'
                f'<span class="sep">·</span>'
                f'<span>{entry.get("provider", "ai")}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            c_open, c_del = st.columns([3, 1])
            if c_open.button("เปิดดูผล", key=f"st_open_{i}_{entry['id']}",
                             use_container_width=True, type="primary"):
                st.session_state["current"] = entry
                st.session_state["_view"] = "create"
                st.rerun()
            if c_del.button("🗑", key=f"st_del_{i}_{entry['id']}",
                            use_container_width=True,
                            help="ลบรายการนี้"):
                st.session_state["history"] = [
                    e for e in hist if e["id"] != entry["id"]
                ]
                if st.session_state.get("current", {}).get("id") == entry["id"]:
                    st.session_state["current"] = None
                st.rerun()


def view_explore():
    # Detail mode
    opened = st.session_state.get("_ex_open")
    kg = brain.load_kg_parsed()
    nodes = kg.get("nodes", [])
    nodes_by_id = {n["id"]: n for n in nodes}

    if opened and opened in nodes_by_id:
        node = nodes_by_id[opened]
        if st.button("← กลับ Gallery", key="ex_back"):
            del st.session_state["_ex_open"]
            st.rerun()

        layer_emoji = {"law": "🏛", "eng": "🔧", "design": "🎨",
                       "thai": "🪷", "fengshui": "☯"}
        layers_html = " ".join(
            f'<span class="tag-pill">{layer_emoji.get(l, "")} {l}</span>'
            for l in node.get("layers", [])
        )

        st.markdown(
            '<div class="page-header">'
            f'<div class="eyebrow">{node.get("type", "concept").upper()}</div>'
            f'<h1>{node.get("title", opened)}</h1>'
            + (f'<div style="margin-top:8px;">{layers_html}</div>' if layers_html else '')
            + f'<p style="margin-top:10px; font-size:0.82em; color:var(--subtle);">'
              f'id <code style="font-size:0.9em;">{opened}</code></p>'
            + '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(node.get("summary", "(no summary)"))

        # Related (from KG edges)
        edges = kg.get("edges", [])
        rel_ids = set()
        for e in edges:
            if e.get("from") == opened:
                rel_ids.add(e.get("to"))
            elif e.get("to") == opened:
                rel_ids.add(e.get("from"))
        related = [nodes_by_id[rid] for rid in list(rel_ids)[:6] if rid in nodes_by_id]

        if related:
            st.divider()
            st.markdown(
                '<div class="eyebrow">RELATED</div>'
                '<h3 style="margin-top:4px;">🕸 หน้าที่เกี่ยวข้อง</h3>',
                unsafe_allow_html=True,
            )
            cols = st.columns(2)
            for i, r in enumerate(related):
                with cols[i % 2]:
                    st.markdown(
                        f'<div class="card" style="padding:12px;">'
                        f'<div style="font-family:var(--font-display); font-weight:700;">{r["title"]}</div>'
                        f'<div style="color:var(--muted); font-size:0.86em; margin-top:4px;">{(r.get("summary") or "")[:140]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(f"→ {r['title'][:25]}",
                                 key=f"ex_rel_{i}_{r['id']}",
                                 use_container_width=True):
                        st.session_state["_ex_open"] = r["id"]
                        st.rerun()
        return

    # Gallery mode · clean header (no hero gradient)
    st.markdown(
        '<div class="page-header">'
        '<div class="eyebrow">EXPLORE</div>'
        '<h1>สำรวจความรู้</h1>'
        f'<p>Knowledge Graph {len(nodes)} หน้า · คลิกอ่านแต่ละเรื่อง · '
        'ลิงก์หน้าที่เกี่ยวข้องให้ท่องต่อ</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Filter
    all_layers = sorted({l for n in nodes for l in n.get("layers", [])})
    c_f, c_s = st.columns([1, 2])
    selected = c_f.multiselect(
        "Filter ชั้น",
        options=all_layers,
        format_func=lambda x: {"law": "🏛 กฎหมาย", "eng": "🔧 วิศวกรรม",
                                "design": "🎨 ออกแบบ", "thai": "🪷 ไทย",
                                "fengshui": "☯ ฮวงจุ้ย"}.get(x, x),
        key="ex_layers",
    )
    search = c_s.text_input("🔎 ค้นหา title หรือ summary", key="ex_search")

    filtered = [n for n in nodes if n.get("summary")]
    if selected:
        filtered = [n for n in filtered if any(l in (n.get("layers") or []) for l in selected)]
    if search:
        sl = search.lower()
        filtered = [n for n in filtered
                    if sl in n.get("title", "").lower()
                    or sl in n.get("summary", "").lower()]

    st.caption(f"แสดง {min(len(filtered), 30)}/{len(filtered)}")

    if not filtered:
        st.info("ไม่เจอรายการ · ลอง clear filter")
        return

    cols = st.columns(3)
    layer_emoji = {"law": "🏛", "eng": "🔧", "design": "🎨",
                   "thai": "🪷", "fengshui": "☯"}
    for i, n in enumerate(filtered[:30]):
        with cols[i % 3]:
            layers_html = " ".join(
                f'<span class="tag-pill">{layer_emoji.get(l, "")} {l}</span>'
                for l in n.get("layers", [])[:3]
            )
            st.markdown(
                f'<div class="ex-card">'
                f'<div class="ex-type">{n.get("type", "concept")}</div>'
                f'<div class="ex-title">{n.get("title", n["id"])}</div>'
                f'<div class="ex-preview">{(n.get("summary") or "")[:220]}</div>'
                + (f'<div class="ex-layers">{layers_html}</div>' if layers_html else '')
                + '</div>',
                unsafe_allow_html=True,
            )
            if st.button("อ่านเพิ่มเติม", key=f"ex_{i}_{n['id']}",
                         use_container_width=True):
                st.session_state["_ex_open"] = n["id"]
                st.rerun()

    if len(filtered) > 30:
        st.caption(f"...อีก {len(filtered) - 30} · narrow filter เพื่อหาเจอง่ายขึ้น")


# =============================================================================
# Main
# =============================================================================

def main():
    st.markdown(CSS, unsafe_allow_html=True)

    view, provider, api_key, model, project_data, image_bytes = render_sidebar()

    # Pass inputs for Create flow via session_state
    if view == "create":
        st.session_state["_project_data"] = project_data
        st.session_state["_image_bytes"] = image_bytes

    if view == "create":
        view_create()
    elif view == "studio":
        view_studio()
    elif view == "explore":
        view_explore()


if __name__ == "__main__":
    main()
