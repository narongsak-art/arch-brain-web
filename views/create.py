"""Create view · sidebar = inputs · main = result only

UX split:
- All form fields + analyze button live in the Streamlit sidebar
- Main area is dedicated to OUTPUT: welcome state OR analysis result
- Keeps the work area uncluttered · mirrors drafted.ai pattern
"""

import json
import time
from datetime import datetime

import streamlit as st

from core import analysis, llm, theme


# ============================================================================
# Presets
# ============================================================================

PRESETS = {
    "townhome": {
        "label": "🏘 ทาวน์เฮาส์ · 4×16 · 3 ลบ.",
        "data": {"name": "ทาวน์เฮาส์-A", "land_w": 4.0, "land_d": 16.0,
                 "province": "กรุงเทพมหานคร", "zone": "ย.4", "street_w": 6.0,
                 "family_size": 4, "has_elderly": "ไม่", "floors": "2",
                 "bedrooms": "3", "budget": 3.0, "fengshui": "น้อย", "special": ""},
    },
    "small": {
        "label": "🏠 บ้านเดี่ยวเล็ก · 15×20 · 5 ลบ.",
        "data": {"name": "บ้านเดี่ยว-S", "land_w": 15.0, "land_d": 20.0,
                 "province": "นนทบุรี", "zone": "ย.3", "street_w": 6.0,
                 "family_size": 4, "has_elderly": "ไม่", "floors": "2",
                 "bedrooms": "3", "budget": 5.0, "fengshui": "ปานกลาง", "special": ""},
    },
    "large": {
        "label": "🏡 บ้านเดี่ยวใหญ่ · 20×30 · 12 ลบ.",
        "data": {"name": "บ้านเดี่ยว-L", "land_w": 20.0, "land_d": 30.0,
                 "province": "กรุงเทพมหานคร", "zone": "ย.2", "street_w": 8.0,
                 "family_size": 5, "has_elderly": "ใช่", "floors": "2",
                 "bedrooms": "4", "budget": 12.0, "fengshui": "มาก",
                 "special": "ห้องพระ · ผู้สูงอายุชั้นล่าง · home office"},
    },
    "luxury": {
        "label": "🏛 บ้านหรู · 25×40 · 25 ลบ.",
        "data": {"name": "บ้านหรู-A", "land_w": 25.0, "land_d": 40.0,
                 "province": "กรุงเทพมหานคร", "zone": "ย.1", "street_w": 10.0,
                 "family_size": 6, "has_elderly": "ใช่", "floors": "3",
                 "bedrooms": "5", "budget": 25.0, "fengshui": "มาก",
                 "special": "สระว่ายน้ำ · ลิฟต์บ้าน · ห้องพระ · walk-in"},
    },
    "compact_bkk": {
        "label": "🏙 บ้านเล็ก กทม. · 8×12 · 4 ลบ.",
        "data": {"name": "บ้านเล็ก-BKK", "land_w": 8.0, "land_d": 12.0,
                 "province": "กรุงเทพมหานคร", "zone": "ย.5", "street_w": 6.0,
                 "family_size": 2, "has_elderly": "ไม่", "floors": "3",
                 "bedrooms": "2", "budget": 4.0, "fengshui": "น้อย",
                 "special": "home office 2 คน"},
    },
}

PROVINCES = ["กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี", "สมุทรปราการ",
             "นครปฐม", "เชียงใหม่", "ภูเก็ต", "อื่นๆ"]
ZONES = ["ย.1", "ย.2", "ย.3", "ย.4", "ย.5", "ย.6", "ย.7",
         "ย.8", "ย.9", "ย.10", "พ.1", "พ.2", "ไม่ทราบ"]

_FORM_MAP = {
    "name": "cf_name", "land_w": "cf_w", "land_d": "cf_d",
    "province": "cf_province", "zone": "cf_zone", "street_w": "cf_street",
    "family_size": "cf_family", "floors": "cf_floors",
    "bedrooms": "cf_bedrooms", "budget": "cf_budget",
    "fengshui": "cf_fs", "special": "cf_special",
}


def _apply_preset():
    """Callback fired before re-rendering widgets · safe to mutate state"""
    preset_key = st.session_state.get("cf_preset_key", "")
    p = PRESETS.get(preset_key)
    if not p:
        return
    for src, dst in _FORM_MAP.items():
        if src in p["data"]:
            st.session_state[dst] = p["data"][src]
    st.session_state["cf_elderly"] = "มี" if p["data"].get("has_elderly") == "ใช่" else "ไม่มี"


def _init_defaults():
    defaults = {
        "cf_name": "บ้าน-A", "cf_w": 15.0, "cf_d": 20.0,
        "cf_province": "กรุงเทพมหานคร", "cf_zone": "ย.3",
        "cf_street": 6.0, "cf_family": 4, "cf_elderly": "ไม่มี",
        "cf_floors": "2", "cf_bedrooms": "3", "cf_budget": 8.0,
        "cf_fs": "ปานกลาง", "cf_special": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


# ============================================================================
# Sidebar form (INPUTS live here)
# ============================================================================

def render_sidebar_form(provider: str, api_key: str, model: str):
    """Render form + analyze button inside sidebar"""
    _init_defaults()

    with st.sidebar:
        st.markdown(
            '<div class="eyebrow">PROJECT BRIEF</div>'
            '<div style="font-family: var(--font-display); font-size: 1.05em; '
            'font-weight: 700; margin-bottom: 8px;">กรอกข้อมูลโปรเจค</div>',
            unsafe_allow_html=True,
        )

        # Preset picker · select OR "custom"
        st.selectbox(
            "⚡ Quick preset (optional)",
            options=["_custom"] + list(PRESETS.keys()),
            format_func=lambda k: "— เลือก template —" if k == "_custom" else PRESETS[k]["label"],
            key="cf_preset_key",
            on_change=_apply_preset,
        )

        st.divider()

        st.text_input("ชื่อโปรเจค", key="cf_name")

        c1, c2 = st.columns(2)
        c1.number_input("กว้าง (ม.)", 3.0, 100.0, step=0.5, key="cf_w")
        c2.number_input("ลึก (ม.)", 3.0, 100.0, step=0.5, key="cf_d")

        st.selectbox("จังหวัด", PROVINCES, key="cf_province")
        st.selectbox("สีผังเมือง", ZONES, key="cf_zone",
                     help="ย. = ที่อยู่อาศัย · พ. = พาณิชย์")
        st.number_input("ถนนติด (ม.)", 1.0, 50.0, step=0.5, key="cf_street")

        st.divider()
        st.slider("สมาชิกครอบครัว", 1, 15, key="cf_family")
        st.radio("ผู้สูงอายุ", ["ไม่มี", "มี"], horizontal=True, key="cf_elderly")

        c3, c4 = st.columns(2)
        c3.selectbox("ชั้น", ["1", "2", "3", "4+"], key="cf_floors")
        c4.selectbox("ห้องนอน", ["1", "2", "3", "4", "5+"], key="cf_bedrooms")

        st.number_input("งบ (ล้านบาท)", 0.5, 200.0, step=0.5, key="cf_budget")
        st.selectbox("ฮวงจุ้ย", ["มาก", "ปานกลาง", "น้อย", "ไม่สน"], key="cf_fs")

        st.text_area(
            "ข้อพิเศษ (optional)",
            placeholder="เช่น · ห้องพระ · สระ · home office",
            height=80,
            key="cf_special",
        )

        st.divider()

        uploaded = st.file_uploader(
            "📎 แปลน (optional · .jpg/.png)",
            type=["jpg", "jpeg", "png"],
        )
        image_bytes = uploaded.getvalue() if uploaded else None
        if image_bytes:
            st.image(image_bytes, caption="แปลนที่จะส่ง",
                     use_container_width=True)

        st.divider()

        # THE BIG CTA
        if not api_key:
            st.warning(
                "👆 ใส่ **API Key** ที่ส่วน AI ด้านบนก่อน · "
                "[รับ Gemini ฟรี](https://aistudio.google.com/apikey)"
            )
        else:
            if st.button("🔍 วิเคราะห์โครงการ",
                         type="primary", use_container_width=True,
                         key="cf_run_btn"):
                st.session_state["_cf_pending"] = True

    # Return project_data for use in run
    land_w = st.session_state["cf_w"]
    land_d = st.session_state["cf_d"]
    return {
        "name": st.session_state["cf_name"],
        "land_w": land_w, "land_d": land_d, "land_area": land_w * land_d,
        "province": st.session_state["cf_province"],
        "zone": st.session_state["cf_zone"],
        "street_w": st.session_state["cf_street"],
        "family_size": st.session_state["cf_family"],
        "has_elderly": "ใช่" if st.session_state["cf_elderly"] == "มี" else "ไม่",
        "floors": st.session_state["cf_floors"],
        "bedrooms": st.session_state["cf_bedrooms"],
        "budget": st.session_state["cf_budget"],
        "fengshui": st.session_state["cf_fs"],
        "special": st.session_state["cf_special"],
    }, image_bytes


# ============================================================================
# Analysis runner (main area · shows progress · saves result)
# ============================================================================

def _run_analysis(provider: str, api_key: str, model: str,
                  project_data: dict, image_bytes: bytes | None):
    system = analysis.build_system_prompt()
    user_text = analysis.build_user_prompt(project_data)

    status = st.status(f"🧠 วิเคราะห์ด้วย {provider.title()}", expanded=True)
    try:
        status.update(label="📚 โหลด Knowledge Graph · 104 nodes")
        time.sleep(0.1)
        status.update(label="🧠 เรียก AI · ~30-60 วินาที")
        t0 = time.time()
        raw = llm.dispatch(provider, api_key, system, user_text, image_bytes, model)
        elapsed = time.time() - t0

        status.update(label=f"📊 parse · {len(raw):,} chars")
        parsed = analysis.extract_json(raw)

        label = f"✅ เสร็จใน {elapsed:.1f} วิ"
        label += " · JSON" if parsed else " · markdown"
        status.update(label=label, state="complete", expanded=False)

        _save(project_data, raw, parsed, provider)
        st.session_state["cf_result"] = parsed
        st.session_state["cf_raw"] = raw
        st.session_state["cf_pd"] = project_data
        st.session_state["cf_provider"] = provider
    except Exception as e:
        status.update(label=f"❌ ล้มเหลว: {e}", state="error", expanded=True)
        st.error(str(e))


def _save(pd: dict, raw: str, result: dict | None, provider: str):
    entry = {
        "id": datetime.now().strftime("%Y%m%d-%H%M%S-%f"),
        "ts": datetime.now().isoformat(),
        "name": pd.get("name", "-"),
        "province": pd.get("province", "-"),
        "zone": pd.get("zone", "-"),
        "land_area": pd.get("land_area", 0),
        "provider": provider,
        "project_data": pd,
        "raw_text": raw,
        "result": result,
    }
    st.session_state.setdefault("history", [])
    st.session_state["history"].insert(0, entry)
    st.session_state["history"] = st.session_state["history"][:30]


# ============================================================================
# Main area (OUTPUTS live here)
# ============================================================================

def _render_welcome():
    """Empty state when no analysis yet"""
    theme.hero(
        "สมองจำลองของสถาปนิก",
        "วิเคราะห์บ้านไทยด้วย AI + 5 ชั้นความรู้ · กรอกข้อมูลที่ sidebar ซ้าย · กด วิเคราะห์",
        eyebrow="CREATE",
    )
    st.markdown(
        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));'
        'gap: 14px; margin: 20px 0;">'
        '<div class="card"><div style="font-size:1.6em;">📐</div>'
        '<strong>Metrics</strong><div style="color:var(--muted); font-size:0.88em;">'
        'FAR · OSR · setback · buildable area · cost</div></div>'
        '<div class="card"><div style="font-size:1.6em;">🧩</div>'
        '<strong>5-Layer</strong><div style="color:var(--muted); font-size:0.88em;">'
        'กฎหมาย · วิศวกรรม · ออกแบบ · วัฒนธรรม · ฮวงจุ้ย</div></div>'
        '<div class="card"><div style="font-size:1.6em;">🚪</div>'
        '<strong>Rooms</strong><div style="color:var(--muted); font-size:0.88em;">'
        'ขนาดแนะนำ · ทิศ · วัฒนธรรม · ฮวงจุ้ย</div></div>'
        '<div class="card"><div style="font-size:1.6em;">🎯</div>'
        '<strong>Next Actions</strong><div style="color:var(--muted); font-size:0.88em;">'
        'ลำดับ step · โดย · เมื่อ</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "💡 **เริ่มต้น:** เลือก **preset** ที่ sidebar ซ้าย (เช่น 🏠 บ้านเดี่ยวเล็ก) "
        "→ ข้อมูลจะ fill อัตโนมัติ → กด **🔍 วิเคราะห์โครงการ** "
        "→ รอ ~60 วินาที · ผลจะขึ้นในพื้นที่นี้"
    )


def _render_result():
    data = st.session_state.get("cf_result")
    raw = st.session_state.get("cf_raw")
    pd = st.session_state.get("cf_pd")
    provider = st.session_state.get("cf_provider", "ai")

    if not pd:
        _render_welcome()
        return

    st.markdown(
        f'<div class="eyebrow">ANALYSIS · {provider.upper()}</div>'
        f'<h1 style="margin-top:4px;">{pd["name"]}</h1>',
        unsafe_allow_html=True,
    )

    if data:
        analysis.render(data)
    else:
        st.warning("⚠ AI ไม่ตอบเป็น JSON · markdown fallback")
        st.markdown(raw or "")

    # Downloads
    st.divider()
    st.markdown(
        '<div class="eyebrow">EXPORT</div>'
        '<h3 style="margin-top:4px;">📥 ดาวน์โหลด</h3>',
        unsafe_allow_html=True,
    )
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    md_content = analysis.to_markdown(data) if data else (raw or "")
    full_md = f"""# ผลวิเคราะห์ — {pd['name']}

วันที่: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Provider: {provider.title()}

## ข้อมูลโครงการ

```json
{json.dumps(pd, ensure_ascii=False, indent=2)}
```

{md_content}

---

_สมองจำลองของสถาปนิก · Thai Architect's Studio_
"""
    c1, c2, c3 = st.columns(3)
    c1.download_button("📥 Markdown", full_md,
                       file_name=f"{pd['name']}-{ts}.md",
                       mime="text/markdown", use_container_width=True)
    if data:
        c2.download_button(
            "📋 JSON",
            json.dumps({"project_data": pd, "result": data, "provider": provider,
                        "timestamp": datetime.now().isoformat()},
                       ensure_ascii=False, indent=2),
            file_name=f"{pd['name']}-{ts}.json",
            mime="application/json", use_container_width=True,
        )
    c3.download_button("📝 Raw text", raw or "",
                       file_name=f"{pd['name']}-{ts}-raw.txt",
                       mime="text/plain", use_container_width=True)


def render_main(provider: str, api_key: str, model: str,
                project_data: dict, image_bytes: bytes | None):
    """Main area · only result (or welcome empty state)"""
    # Check if we should run
    if st.session_state.pop("_cf_pending", False):
        _run_analysis(provider, api_key, model, project_data, image_bytes)

    _render_result()
