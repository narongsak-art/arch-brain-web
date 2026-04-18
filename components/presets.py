"""Preset project templates · quick-start defaults for common Thai home types"""

import streamlit as st

PRESETS = {
    "townhome": {
        "label": "🏘 ทาวน์เฮาส์",
        "desc": "บ้าน 4×16 ม. · 2 ชั้น · 3 ห้องนอน · งบ 3 ลบ.",
        "data": {
            "name": "ทาวน์เฮาส์-A",
            "land_w": 4.0,
            "land_d": 16.0,
            "province": "กรุงเทพมหานคร",
            "zone": "ย.4",
            "street_w": 6.0,
            "family_size": 4,
            "has_elderly": "ไม่",
            "floors": "2",
            "bedrooms": "3",
            "budget": 3.0,
            "fengshui": "น้อย",
            "special": "",
        },
    },
    "single_small": {
        "label": "🏠 บ้านเดี่ยวเล็ก",
        "desc": "15×20 ม. · 2 ชั้น · 3 ห้องนอน · งบ 5 ลบ.",
        "data": {
            "name": "บ้านเดี่ยว-S",
            "land_w": 15.0,
            "land_d": 20.0,
            "province": "นนทบุรี",
            "zone": "ย.3",
            "street_w": 6.0,
            "family_size": 4,
            "has_elderly": "ไม่",
            "floors": "2",
            "bedrooms": "3",
            "budget": 5.0,
            "fengshui": "ปานกลาง",
            "special": "",
        },
    },
    "single_large": {
        "label": "🏡 บ้านเดี่ยวใหญ่",
        "desc": "20×30 ม. · 2 ชั้น · 4 ห้องนอน + ห้องพระ · งบ 12 ลบ.",
        "data": {
            "name": "บ้านเดี่ยว-L",
            "land_w": 20.0,
            "land_d": 30.0,
            "province": "กรุงเทพมหานคร",
            "zone": "ย.2",
            "street_w": 8.0,
            "family_size": 5,
            "has_elderly": "ใช่",
            "floors": "2",
            "bedrooms": "4",
            "budget": 12.0,
            "fengshui": "มาก",
            "special": "ห้องพระ · walk-in · ผู้สูงอายุชั้นล่าง · home office 1 ห้อง",
        },
    },
    "luxury": {
        "label": "🏛 บ้านหรู",
        "desc": "25×40 ม. · 3 ชั้น · 5 ห้องนอน · สระว่ายน้ำ · งบ 25 ลบ.",
        "data": {
            "name": "บ้านหรู-A",
            "land_w": 25.0,
            "land_d": 40.0,
            "province": "กรุงเทพมหานคร",
            "zone": "ย.1",
            "street_w": 10.0,
            "family_size": 6,
            "has_elderly": "ใช่",
            "floors": "3",
            "bedrooms": "5",
            "budget": 25.0,
            "fengshui": "มาก",
            "special": "สระว่ายน้ำ · ห้องพระ · ลิฟต์บ้าน · home theater · walk-in · ห้องแม่บ้าน",
        },
    },
    "compact_bkk": {
        "label": "🏙 บ้านเล็ก กทม.",
        "desc": "8×12 ม. · 3 ชั้น · 2 ห้องนอน · งบ 4 ลบ.",
        "data": {
            "name": "บ้านเล็ก-BKK",
            "land_w": 8.0,
            "land_d": 12.0,
            "province": "กรุงเทพมหานคร",
            "zone": "ย.5",
            "street_w": 6.0,
            "family_size": 2,
            "has_elderly": "ไม่",
            "floors": "3",
            "bedrooms": "2",
            "budget": 4.0,
            "fengshui": "น้อย",
            "special": "home office 2 คน · พื้นที่นอกจำกัด",
        },
    },
}


def render_preset_chips(on_apply):
    """
    Render preset quick-start buttons at top of wizard.
    `on_apply(preset_data_dict)` is called when a preset is clicked.
    """
    st.markdown(
        '<div class="ab-preset-hint">⚡ เริ่มเร็ว · เลือก template แล้วปรับต่อได้</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(PRESETS))
    for i, (key, p) in enumerate(PRESETS.items()):
        with cols[i]:
            if st.button(
                f"{p['label']}\n\n_{p['desc']}_",
                use_container_width=True,
                key=f"preset_{key}",
                help=p["desc"],
            ):
                on_apply(p["data"])
                st.rerun()
