"""Multi-step form wizard · 3 steps: Land → Family → Special"""

import streamlit as st

STEPS = [
    ("land", "🏞 ที่ดิน"),
    ("family", "👨‍👩‍👧 ครอบครัว"),
    ("special", "📝 รายละเอียด"),
]

PROVINCES = [
    "กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี", "สมุทรปราการ",
    "สมุทรสาคร", "นครปฐม", "เชียงใหม่", "ภูเก็ต", "อื่นๆ",
]
ZONES = [
    "ย.1", "ย.2", "ย.3", "ย.4", "ย.5", "ย.6", "ย.7",
    "ย.8", "ย.9", "ย.10",
    "พ.1", "พ.2", "พ.3", "พ.4", "พ.5",
    "อ.1", "อ.2", "อ.3", "ก.1", "ก.2", "ก.3", "ก.4", "ก.5",
    "ไม่ทราบ",
]


def _init_state():
    st.session_state.setdefault("wizard_step", 0)
    st.session_state.setdefault("form_data", {
        "name": "บ้าน-A",
        "land_w": 15.0,
        "land_d": 20.0,
        "province": "กรุงเทพมหานคร",
        "zone": "ย.3",
        "street_w": 6.0,
        "family_size": 4,
        "has_elderly": "ไม่",
        "floors": "2",
        "bedrooms": "3",
        "budget": 8.0,
        "fengshui": "ปานกลาง",
        "special": "",
    })


def apply_preset(preset: dict):
    """Fill form_data from a preset template"""
    _init_state()
    st.session_state["form_data"].update(preset)
    st.session_state["wizard_step"] = 0


def render_step_indicator():
    step = st.session_state.get("wizard_step", 0)
    html = '<div class="ab-steps">'
    for i, (_, label) in enumerate(STEPS):
        if i < step:
            cls = "ab-step done"
            circle = "✓"
        elif i == step:
            cls = "ab-step active"
            circle = str(i + 1)
        else:
            cls = "ab-step"
            circle = str(i + 1)
        html += (
            f'<div class="{cls}">'
            f'<div class="ab-step-circle">{circle}</div>'
            f'<div class="ab-step-label">{label}</div>'
            f"</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _step_land():
    fd = st.session_state["form_data"]
    col1, col2 = st.columns(2)
    with col1:
        fd["name"] = st.text_input("ชื่อโปรเจค (alias)", value=fd.get("name", "บ้าน-A"))
        fd["land_w"] = st.number_input("กว้าง (ม.)", min_value=1.0, value=float(fd.get("land_w", 15.0)), step=0.5)
        fd["land_d"] = st.number_input("ลึก (ม.)", min_value=1.0, value=float(fd.get("land_d", 20.0)), step=0.5)
    with col2:
        fd["province"] = st.selectbox("จังหวัด", PROVINCES, index=PROVINCES.index(fd.get("province", "กรุงเทพมหานคร")) if fd.get("province") in PROVINCES else 0)
        fd["zone"] = st.selectbox("สีผังเมือง", ZONES, index=ZONES.index(fd.get("zone", "ย.3")) if fd.get("zone") in ZONES else 2, help="ย. = ที่อยู่อาศัย · พ. = พาณิชย์ · อ. = อุตสาหกรรม · ก. = เกษตร")
        fd["street_w"] = st.number_input("ถนนติดกว้าง (ม.)", min_value=1.0, value=float(fd.get("street_w", 6.0)), step=0.5)

    area = fd["land_w"] * fd["land_d"]
    st.info(f"📐 พื้นที่ดิน: **{area:.0f} ตร.ม.** ({area/4:.1f} ตร.วา · {area/1600:.2f} ไร่)")


def _step_family():
    fd = st.session_state["form_data"]
    col1, col2 = st.columns(2)
    with col1:
        fd["family_size"] = st.slider("จำนวนสมาชิก", 1, 15, value=int(fd.get("family_size", 4)))
        fd["has_elderly"] = st.radio("มีผู้สูงอายุ", ["ใช่", "ไม่"], horizontal=True, index=0 if fd.get("has_elderly") == "ใช่" else 1)
        fd["floors"] = st.selectbox("ชั้น", ["1", "2", "3", "4+"], index=["1", "2", "3", "4+"].index(str(fd.get("floors", "2"))))
    with col2:
        fd["bedrooms"] = st.selectbox("ห้องนอน", ["1", "2", "3", "4", "5+"], index=["1", "2", "3", "4", "5+"].index(str(fd.get("bedrooms", "3"))))
        fd["budget"] = st.number_input("งบ (ล้านบาท)", min_value=0.5, value=float(fd.get("budget", 8.0)), step=0.5)
        fs_opts = ["มาก", "ปานกลาง", "น้อย", "ไม่สน"]
        fd["fengshui"] = st.selectbox("สนใจฮวงจุ้ย", fs_opts, index=fs_opts.index(fd.get("fengshui", "ปานกลาง")) if fd.get("fengshui") in fs_opts else 1)


def _step_special():
    fd = st.session_state["form_data"]
    fd["special"] = st.text_area(
        "ความต้องการพิเศษ",
        value=fd.get("special", ""),
        placeholder="ตัวอย่าง: ห้องพระ · walk-in · home office 2 คน · สระว่ายน้ำ · ผู้สูงอายุใช้ wheelchair · ลูก 2 คนต้องการห้องแยก",
        height=140,
    )

    st.markdown("### 📋 สรุปข้อมูล")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        **ที่ดิน**
        - {fd['land_w']} × {fd['land_d']} ม.
        - {fd['land_w']*fd['land_d']:.0f} ตร.ม.
        - {fd['province']} · {fd['zone']}
        """)
    with col2:
        st.markdown(f"""
        **ครอบครัว**
        - {fd['family_size']} คน
        - ผู้สูงอายุ: {fd['has_elderly']}
        - ชั้น {fd['floors']} · {fd['bedrooms']} ห้องนอน
        """)
    with col3:
        st.markdown(f"""
        **งบ + อื่นๆ**
        - {fd['budget']} ล้านบาท
        - ฮวงจุ้ย: {fd['fengshui']}
        - ถนน: {fd['street_w']} ม.
        """)


def render_wizard():
    """Render wizard UI. Returns (form_data_dict, is_ready_flag)."""
    _init_state()
    render_step_indicator()

    step = st.session_state["wizard_step"]
    key, _ = STEPS[step]

    if key == "land":
        _step_land()
    elif key == "family":
        _step_family()
    elif key == "special":
        _step_special()

    st.markdown("---")
    col_back, col_spacer, col_next = st.columns([1, 2, 1])
    with col_back:
        if step > 0:
            if st.button("◀ ย้อนกลับ", use_container_width=True, key="wiz_back"):
                st.session_state["wizard_step"] -= 1
                st.rerun()
    with col_next:
        if step < len(STEPS) - 1:
            if st.button("ถัดไป ▶", type="primary", use_container_width=True, key="wiz_next"):
                st.session_state["wizard_step"] += 1
                st.rerun()

    fd = dict(st.session_state["form_data"])
    fd["land_area"] = fd["land_w"] * fd["land_d"]
    is_ready = (step == len(STEPS) - 1)
    return fd, is_ready


def reset_wizard():
    st.session_state["wizard_step"] = 0
