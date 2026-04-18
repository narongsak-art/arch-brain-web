"""Preset project templates · quick-start defaults for common Thai home types"""

import streamlit as st


PRESETS = {
    "townhome": {
        "label": "🏘 ทาวน์เฮาส์",
        "desc": "4×16 ม. · 2 ชั้น · 3 BR · 3 ลบ.",
        "data": {
            "name": "ทาวน์เฮาส์-A",
            "land_w": 4.0, "land_d": 16.0,
            "province": "กรุงเทพมหานคร", "zone": "ย.4", "street_w": 6.0,
            "family_size": 4, "has_elderly": "ไม่",
            "floors": "2", "bedrooms": "3",
            "budget": 3.0, "fengshui": "น้อย", "special": "",
        },
    },
    "single_small": {
        "label": "🏠 บ้านเดี่ยวเล็ก",
        "desc": "15×20 ม. · 2 ชั้น · 3 BR · 5 ลบ.",
        "data": {
            "name": "บ้านเดี่ยว-S",
            "land_w": 15.0, "land_d": 20.0,
            "province": "นนทบุรี", "zone": "ย.3", "street_w": 6.0,
            "family_size": 4, "has_elderly": "ไม่",
            "floors": "2", "bedrooms": "3",
            "budget": 5.0, "fengshui": "ปานกลาง", "special": "",
        },
    },
    "single_large": {
        "label": "🏡 บ้านเดี่ยวใหญ่",
        "desc": "20×30 ม. · 2 ชั้น · 4 BR + ห้องพระ · 12 ลบ.",
        "data": {
            "name": "บ้านเดี่ยว-L",
            "land_w": 20.0, "land_d": 30.0,
            "province": "กรุงเทพมหานคร", "zone": "ย.2", "street_w": 8.0,
            "family_size": 5, "has_elderly": "ใช่",
            "floors": "2", "bedrooms": "4",
            "budget": 12.0, "fengshui": "มาก",
            "special": "ห้องพระ · walk-in · ผู้สูงอายุชั้นล่าง · home office 1 ห้อง",
        },
    },
    "luxury": {
        "label": "🏛 บ้านหรู",
        "desc": "25×40 ม. · 3 ชั้น · 5 BR · สระน้ำ · 25 ลบ.",
        "data": {
            "name": "บ้านหรู-A",
            "land_w": 25.0, "land_d": 40.0,
            "province": "กรุงเทพมหานคร", "zone": "ย.1", "street_w": 10.0,
            "family_size": 6, "has_elderly": "ใช่",
            "floors": "3", "bedrooms": "5",
            "budget": 25.0, "fengshui": "มาก",
            "special": "สระว่ายน้ำ · ห้องพระ · ลิฟต์บ้าน · home theater · walk-in · ห้องแม่บ้าน",
        },
    },
    "compact_bkk": {
        "label": "🏙 บ้านเล็ก กทม.",
        "desc": "8×12 ม. · 3 ชั้น · 2 BR · 4 ลบ.",
        "data": {
            "name": "บ้านเล็ก-BKK",
            "land_w": 8.0, "land_d": 12.0,
            "province": "กรุงเทพมหานคร", "zone": "ย.5", "street_w": 6.0,
            "family_size": 2, "has_elderly": "ไม่",
            "floors": "3", "bedrooms": "2",
            "budget": 4.0, "fengshui": "น้อย",
            "special": "home office 2 คน · พื้นที่นอกจำกัด",
        },
    },
}


# Map from legacy preset keys to v3 form widget session_state keys
_FORM_KEY_MAP = {
    "name": "form_name",
    "land_w": "form_land_w",
    "land_d": "form_land_d",
    "province": "form_province",
    "zone": "form_zone",
    "street_w": "form_street",
    "family_size": "form_family",
    "floors": "form_floors",
    "bedrooms": "form_bedrooms",
    "budget": "form_budget",
    "fengshui": "form_fs",
    "special": "form_special",
}


def apply_preset(preset_key: str):
    """Button on_click callback → writes preset values into form_* session state.
    Runs BEFORE the next script execution, so the next render picks up new defaults.
    """
    preset = PRESETS.get(preset_key)
    if not preset:
        return
    data = preset["data"]
    for src_key, dst_key in _FORM_KEY_MAP.items():
        if src_key in data:
            st.session_state[dst_key] = data[src_key]
    # Elderly is displayed as "มี" / "ไม่มี" in the v3 form
    st.session_state["form_elderly"] = "มี" if data.get("has_elderly") == "ใช่" else "ไม่มี"


def render_chips():
    """Horizontal row of preset buttons. Uses on_click callback (no st.rerun needed)."""
    st.caption("⚡ เริ่มเร็ว · คลิก template แล้วปรับต่อได้")
    cols = st.columns(len(PRESETS))
    for i, (key, p) in enumerate(PRESETS.items()):
        with cols[i]:
            st.button(
                p["label"],
                key=f"preset_btn_{key}",
                help=p["desc"],
                use_container_width=True,
                on_click=apply_preset,
                args=(key,),
            )
