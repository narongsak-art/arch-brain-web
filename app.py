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
  --cream: #faf7f0; --sand: #f4efe3; --border: #e5dfcf; --border-strong: #c9bfa3;
  --teak: #8b5a2b; --teak-hover: #6d4621; --teak-soft: #f0e6d8;
  --gold: #c9a961; --terra: #c97864;
  --ink: #2d1f15; --muted: #6b5842; --subtle: #9c8970;
  --font-display: 'Bai Jamjuree', 'Sarabun', serif;
  --font-body: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif;
  --radius: 10px;
  --shadow-sm: 0 1px 2px rgba(45,31,21,0.05), 0 1px 3px rgba(45,31,21,0.08);
  --shadow-md: 0 4px 12px -2px rgba(45,31,21,0.10);
}

html, body { font-family: var(--font-body); }
.stApp, .stApp * { font-family: var(--font-body); }
.stApp { background: var(--cream); color: var(--ink); }
.main .block-container { max-width: 1000px; padding-top: 1.5rem; padding-bottom: 3rem; }

/* Keep sidebar toggle reachable (past bugs) */
[data-testid="stHeader"] { background: transparent !important; height: auto; }
[data-testid="stDeployButton"] { display: none !important; }
footer { visibility: hidden; }
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[kind="header"], button[kind="headerNoPadding"] {
  visibility: visible !important; display: block !important; z-index: 9999 !important;
}

h1, h2, h3, h4 {
  font-family: var(--font-display); color: var(--ink);
  letter-spacing: -0.015em; font-weight: 700;
}
h1 { font-size: 2.6em; line-height: 1.1; }
h2 { font-size: 1.7em; margin-top: 1em; }
h3 { font-size: 1.25em; }

.eyebrow {
  font-family: var(--font-display); font-size: 0.82em; font-weight: 600;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--teak); margin-bottom: 6px;
}

.hero {
  padding: 44px 32px; margin: 0 0 24px 0; color: #fff;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--teak) 0%, var(--gold) 50%, var(--terra) 100%);
  box-shadow: var(--shadow-md); position: relative; overflow: hidden;
}
.hero::after {
  content: ""; position: absolute; inset: 0;
  background: radial-gradient(circle at 20% 20%, rgba(255,255,255,0.15) 0%, transparent 45%);
  pointer-events: none;
}
.hero .eyebrow { color: rgba(255,255,255,0.9); }
.hero h1 { color: #fff !important; margin: 0 0 8px 0; font-size: 2.6em; }
.hero p { margin: 0; opacity: 0.96; font-size: 1.05em; max-width: 640px; position: relative; }

.card {
  background: #fff; border: 1px solid var(--border); border-radius: var(--radius);
  padding: 18px 22px; box-shadow: var(--shadow-sm); transition: all 0.15s ease;
}
.card:hover {
  border-color: var(--teak); box-shadow: var(--shadow-md); transform: translateY(-1px);
}

/* Primary button · teak */
[data-testid="stBaseButton-primary"] {
  background: var(--teak) !important; border: none !important; color: #fff !important;
  font-weight: 600;
}
[data-testid="stBaseButton-primary"]:hover {
  background: var(--teak-hover) !important; box-shadow: var(--shadow-md);
}

[data-testid="stMetric"] {
  background: var(--sand); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 12px 16px;
}
[data-testid="stMetricValue"] {
  color: var(--teak) !important;
  font-family: var(--font-display) !important; font-weight: 700 !important;
}

[data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--border); }

hr { border: none; height: 1px; background: var(--border); margin: 1em 0; }

@media (max-width: 640px) {
  .hero { padding: 28px 20px; }
  .hero h1 { font-size: 1.7em; }
}
</style>
"""


# =============================================================================
# Presets (form templates)
# =============================================================================

PRESETS = {
    "townhome":   ("🏘 ทาวน์เฮาส์ 4×16 · 3 ลบ.",
                   {"name": "ทาวน์เฮาส์", "land_w": 4.0, "land_d": 16.0,
                    "province": "กรุงเทพมหานคร", "zone": "ย.4", "street_w": 6.0,
                    "family_size": 4, "has_elderly": "ไม่", "floors": "2",
                    "bedrooms": "3", "budget": 3.0, "fengshui": "น้อย",
                    "special": ""}),
    "small":      ("🏠 บ้านเดี่ยวเล็ก 15×20 · 5 ลบ.",
                   {"name": "บ้านเดี่ยว-S", "land_w": 15.0, "land_d": 20.0,
                    "province": "นนทบุรี", "zone": "ย.3", "street_w": 6.0,
                    "family_size": 4, "has_elderly": "ไม่", "floors": "2",
                    "bedrooms": "3", "budget": 5.0, "fengshui": "ปานกลาง",
                    "special": ""}),
    "large":      ("🏡 บ้านเดี่ยวใหญ่ 20×30 · 12 ลบ.",
                   {"name": "บ้านเดี่ยว-L", "land_w": 20.0, "land_d": 30.0,
                    "province": "กรุงเทพมหานคร", "zone": "ย.2", "street_w": 8.0,
                    "family_size": 5, "has_elderly": "ใช่", "floors": "2",
                    "bedrooms": "4", "budget": 12.0, "fengshui": "มาก",
                    "special": "ห้องพระ · ผู้สูงอายุชั้นล่าง · home office"}),
    "luxury":     ("🏛 บ้านหรู 25×40 · 25 ลบ.",
                   {"name": "บ้านหรู", "land_w": 25.0, "land_d": 40.0,
                    "province": "กรุงเทพมหานคร", "zone": "ย.1", "street_w": 10.0,
                    "family_size": 6, "has_elderly": "ใช่", "floors": "3",
                    "bedrooms": "5", "budget": 25.0, "fengshui": "มาก",
                    "special": "สระว่ายน้ำ · ลิฟต์ · ห้องพระ · walk-in"}),
    "compact":    ("🏙 บ้านเล็ก กทม. 8×12 · 4 ลบ.",
                   {"name": "บ้านเล็ก", "land_w": 8.0, "land_d": 12.0,
                    "province": "กรุงเทพมหานคร", "zone": "ย.5", "street_w": 6.0,
                    "family_size": 2, "has_elderly": "ไม่", "floors": "3",
                    "bedrooms": "2", "budget": 4.0, "fengshui": "น้อย",
                    "special": "home office 2 คน"}),
}

PROVINCES = ["กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี", "สมุทรปราการ",
             "นครปฐม", "เชียงใหม่", "ภูเก็ต", "อื่นๆ"]
ZONES = ["ย.1", "ย.2", "ย.3", "ย.4", "ย.5", "ย.6", "ย.7", "ย.8", "ย.9", "ย.10",
         "พ.1", "พ.2", "ไม่ทราบ"]

FORM_DEFAULTS = {
    "name": "บ้าน-A", "land_w": 15.0, "land_d": 20.0,
    "province": "กรุงเทพมหานคร", "zone": "ย.3", "street_w": 6.0,
    "family_size": 4, "has_elderly": "ไม่มี", "floors": "2",
    "bedrooms": "3", "budget": 8.0, "fengshui": "ปานกลาง", "special": "",
}


def _apply_preset():
    key = st.session_state.get("form_preset", "_custom")
    if key == "_custom" or key not in PRESETS:
        return
    _, data = PRESETS[key]
    for k, v in data.items():
        sk = f"form_{k}"
        # UI uses "มี/ไม่มี" but data uses "ใช่/ไม่"
        if k == "has_elderly":
            st.session_state[sk] = "มี" if v == "ใช่" else "ไม่มี"
        else:
            st.session_state[sk] = v


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
                    else PRESETS[k][0],
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
        # Welcome state
        hero("สมองจำลองของสถาปนิก",
             "วิเคราะห์บ้านไทยด้วย AI + 5 ชั้นความรู้ · กรอกข้อมูลที่ sidebar · กด วิเคราะห์",
             eyebrow="CREATE")
        st.markdown(
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));'
            'gap: 12px; margin: 16px 0;">'
            '<div class="card"><div style="font-size:1.6em;">📐</div>'
            '<strong>Metrics</strong><div style="color:var(--muted); font-size:0.88em;">'
            'FAR · OSR · setback · cost</div></div>'
            '<div class="card"><div style="font-size:1.6em;">🧩</div>'
            '<strong>5-Layer</strong><div style="color:var(--muted); font-size:0.88em;">'
            'กฎหมาย · eng · ออกแบบ · ไทย · ฮวงจุ้ย</div></div>'
            '<div class="card"><div style="font-size:1.6em;">🚪</div>'
            '<strong>Rooms</strong><div style="color:var(--muted); font-size:0.88em;">'
            'ขนาด · ทิศ · ฮวงจุ้ย</div></div>'
            '<div class="card"><div style="font-size:1.6em;">🎯</div>'
            '<strong>Next Actions</strong><div style="color:var(--muted); font-size:0.88em;">'
            'step · โดย · เมื่อ</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.info(
            "💡 **เริ่ม:** sidebar ซ้าย → ⚡ เลือก preset → 🔍 วิเคราะห์ · ผลขึ้นที่นี่ใน ~60 วิ"
        )
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
    hero("สตูดิโอของฉัน",
         "งานวิเคราะห์ทั้งหมด · คลิก 🔄 เปิด เพื่อดูผลอีกครั้ง",
         eyebrow="MY STUDIO")

    hist = st.session_state.get("history", [])
    if not hist:
        st.info("✨ ยังไม่มีงาน · ไปที่ **🎨 Create** · วิเคราะห์โปรเจคแรก · ผลจะเก็บที่นี่")
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
                f'<div class="card" style="height:100%;">'
                f'<div style="font-family:var(--font-display); font-weight:700; '
                f'font-size:1.05em; line-height:1.3; margin-bottom:6px;">'
                f'{entry["name"]}</div>'
                f'<div style="font-family:var(--font-display); font-size:1.7em; '
                f'font-weight:700; color:var(--teak); line-height:1;">'
                f'{score}<small style="font-size:0.55em; color:var(--subtle);"> /100</small>'
                f'</div>'
                f'<div style="font-size:0.8em; color:var(--muted); margin-top:4px;">'
                f'{feas_emoji} {feas} · {pd.get("province", "-")[:10]} · '
                f'{pd.get("zone", "-")} · {area:.0f} ตร.ม.'
                f'</div>'
                f'<div style="font-size:0.75em; color:var(--subtle); margin-top:4px;">'
                f'🕐 {ts} · {entry.get("provider", "ai")}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            c_open, c_del = st.columns(2)
            if c_open.button("🔄 เปิด", key=f"st_open_{i}_{entry['id']}",
                             use_container_width=True):
                st.session_state["current"] = entry
                st.session_state["_view"] = "create"
                st.rerun()
            if c_del.button("🗑", key=f"st_del_{i}_{entry['id']}",
                            use_container_width=True):
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
        st.divider()
        layers = ", ".join(node.get("layers", [])) or "-"
        st.markdown(
            f'<div class="eyebrow">{node.get("type", "concept").upper()}</div>'
            f'<h2 style="margin-top:4px;">{node.get("title", opened)}</h2>'
            f'<div style="color:var(--muted); margin-bottom:12px;">'
            f'layers: {layers} · id: <code>{opened}</code></div>',
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

    # Gallery mode
    hero("Explore ความรู้",
         f"Knowledge Graph {len(nodes)} หน้า · คลิกอ่านแต่ละเรื่อง",
         eyebrow="EXPLORE")

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
    for i, n in enumerate(filtered[:30]):
        with cols[i % 3]:
            layers_str = " · ".join(n.get("layers", []))
            st.markdown(
                f'<div class="card">'
                f'<div style="font-size:0.72em; letter-spacing:0.1em; '
                f'text-transform:uppercase; color:var(--teak); font-weight:600;">'
                f'{n.get("type", "concept")}</div>'
                f'<div style="font-family:var(--font-display); font-weight:700; '
                f'font-size:1.05em; line-height:1.3; margin:4px 0 6px 0;">'
                f'{n.get("title", n["id"])}</div>'
                f'<div style="color:var(--muted); font-size:0.86em; line-height:1.5; '
                f'display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; '
                f'overflow:hidden;">{(n.get("summary") or "")[:220]}</div>'
                + (f'<div style="font-size:0.72em; color:var(--subtle); margin-top:6px;">{layers_str}</div>' if layers_str else '')
                + '</div>',
                unsafe_allow_html=True,
            )
            if st.button("📖 เปิดอ่าน", key=f"ex_{i}_{n['id']}",
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
