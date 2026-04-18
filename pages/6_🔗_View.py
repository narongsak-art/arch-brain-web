"""
🔗 View · Read-only viewer for shared analyses

Loads analysis from:
1. `?data=<base64>` URL param (primary)
2. File upload (fallback for oversized links)
"""

import streamlit as st
from datetime import datetime

from components import theme, share, structured_analysis


st.set_page_config(
    page_title="View · สมองจำลองของสถาปนิก",
    page_icon="🔗",
    layout="wide",
)

theme.inject_css()


# ============================================================================
# Load payload
# ============================================================================

def _load_payload() -> dict | None:
    # Try URL query param first
    data_param = st.query_params.get("data")
    if data_param:
        payload = share.decode_payload(data_param)
        if payload:
            return payload
        st.error("❌ ลิงก์เสียหายหรือไม่ถูกต้อง · ลองเปิดใหม่อีกครั้ง หรือ upload ไฟล์ด้านล่าง")
    return None


payload = _load_payload()


# ============================================================================
# Header
# ============================================================================

st.markdown("""
<div style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; color: white; margin-bottom: 24px;">
    <h1 style="color: white; font-size: 2.4em; margin: 0;">🔗 ผลวิเคราะห์โครงการ</h1>
    <p style="font-size: 1.1em; margin-top: 8px; opacity: 0.95;">
        Read-only view · วิเคราะห์ด้วย AI + Knowledge Graph 5 ชั้น
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# Body
# ============================================================================

if not payload:
    st.info(
        "ลิงก์นี้ใช้สำหรับดูผลวิเคราะห์แบบ **read-only** ที่ได้รับจากสถาปนิก · "
        "เปิดลิงก์ที่มี `?data=...` เพื่อดูผล · "
        "ถ้าลิงก์ใหญ่เกิน · ใช้การ upload ไฟล์ `.json` แทน"
    )
    st.markdown("---")

    # Demo payload so visitors can see what a share link looks like
    col_demo, col_upload = st.columns(2)
    with col_demo:
        st.markdown("#### 🎬 Demo")
        st.caption("ตัวอย่างหน้าผลวิเคราะห์ · ไม่ต้อง login")
        if st.button("▶ ดู Demo", type="primary", use_container_width=True):
            st.session_state["_view_demo"] = True
            st.rerun()
    with col_upload:
        st.markdown("#### 📥 Upload file")
        uploaded_payload = share.upload_share_file()
        if uploaded_payload:
            payload = uploaded_payload
            st.rerun()

    if st.session_state.get("_view_demo"):
        payload = {
            "v": "1.0",
            "project_data": {
                "name": "บ้านเดี่ยว-Demo",
                "land_w": 15, "land_d": 20, "land_area": 300,
                "province": "กรุงเทพมหานคร", "zone": "ย.3",
                "street_w": 6.0, "family_size": 4, "has_elderly": "ใช่",
                "floors": "2", "bedrooms": "3", "budget": 8.0,
                "fengshui": "ปานกลาง",
                "special": "ห้องพระ · ผู้สูงอายุชั้นล่าง",
            },
            "structured": {
                "summary": {
                    "feasibility": "green",
                    "feasibility_note": "ที่ดิน 300 ตร.ม. เพียงพอต่อบ้าน 2 ชั้น 3 ห้องนอน · FAR ใช้ประมาณ 0.8 จากที่อนุญาต 1.5",
                    "overall_score": 82,
                    "key_concern": "ระยะร่นข้างบ้านต้องตรวจวัดกับที่ดินข้างเคียง",
                    "key_strength": "ที่ดินกว้างพอที่จะออกแบบแยกโซนผู้สูงอายุ-หลัก-บริการได้ชัด",
                },
                "metrics": {
                    "land_area_sqm": 300,
                    "buildable_area_sqm": 210,
                    "far_allowed": 1.5,
                    "far_estimated": 0.8,
                    "osr_required_pct": 30,
                    "setback_front_m": 3.0,
                    "setback_side_m": 2.0,
                    "setback_back_m": 2.0,
                    "max_height_m": 12,
                    "estimated_floor_area_sqm": 240,
                    "estimated_cost_mbaht": 7.5,
                },
                "layers": {
                    "law": {"status": "pass", "score": 88, "findings": [
                        {"severity": "info", "title": "FAR 0.8 ภายในที่อนุญาต",
                         "detail": "ย.3 ให้ FAR 1.5 · แปลนปัจจุบันใช้ 0.8 · เหลือพื้นที่ขยาย",
                         "citation": "ข้อบัญญัติ กทม. 2544"},
                    ]},
                    "eng": {"status": "pass", "score": 80, "findings": [
                        {"severity": "info", "title": "Span สมเหตุสมผล",
                         "detail": "Span 4-6 ม. สำหรับคอนกรีต · OK", "citation": ""},
                    ]},
                    "design": {"status": "warning", "score": 78, "findings": [
                        {"severity": "warning", "title": "Cross-ventilation จำกัด",
                         "detail": "ควรเพิ่มหน้าต่างฝั่งตะวันออก-ตะวันตก", "citation": ""},
                    ]},
                    "thai": {"status": "pass", "score": 85, "findings": [
                        {"severity": "info", "title": "ห้องพระตำแหน่งดี",
                         "detail": "ชั้น 2 ทิศตะวันออก · เหมาะสม", "citation": ""},
                    ]},
                    "fengshui": {"status": "warning", "score": 72, "findings": [
                        {"severity": "warning", "title": "ประตูหลักตรงกับห้องน้ำ",
                         "detail": "ควรปรับ layout หรือใส่ screen กั้น", "citation": ""},
                    ]},
                },
                "rooms": [
                    {"name": "ห้องนอนใหญ่ (MBR)", "type": "bedroom",
                     "recommended_size_min_sqm": 18, "recommended_size_max_sqm": 25,
                     "orientation_best": "ทิศเหนือ/ตะวันออก · หลีกเลี่ยงตะวันตก",
                     "thai_culture_note": "เตียงไม่หันเท้าชี้ประตู",
                     "fengshui_note": "หัวเตียงแนบผนัง · ไม่ใต้คาน",
                     "key_points": ["walk-in ที่เหมาะสม 4-6 ตร.ม.", "หน้าต่างคู่เพื่อระบายอากาศ"],
                     "issues": []},
                    {"name": "ห้องนอนผู้สูงอายุ", "type": "bedroom",
                     "recommended_size_min_sqm": 14, "recommended_size_max_sqm": 18,
                     "orientation_best": "ชั้นล่าง · ทิศที่เงียบ",
                     "thai_culture_note": "ใกล้ห้องพระเพื่อสะดวกในการสวดมนต์",
                     "fengshui_note": None,
                     "key_points": ["พื้นเรียบ · ไม่มีขั้น", "ห้องน้ำติดห้อง (en-suite)", "ราวจับในห้องน้ำ"],
                     "issues": []},
                    {"name": "ครัวไทย", "type": "kitchen",
                     "recommended_size_min_sqm": 8, "recommended_size_max_sqm": 14,
                     "orientation_best": "ทิศใต้/ตะวันออกเฉียงใต้",
                     "thai_culture_note": "แยกจากครัวฝรั่ง · ระบายอากาศดี",
                     "fengshui_note": "เตาไม่หันเข้าประตู",
                     "key_points": ["พัดลมดูดควัน 1,000+ m³/h", "กันไฟ-กันน้ำเต็มผนัง"],
                     "issues": []},
                    {"name": "ห้องพระ", "type": "prayer",
                     "recommended_size_min_sqm": 4, "recommended_size_max_sqm": 8,
                     "orientation_best": "ชั้นบน · ทิศตะวันออก",
                     "thai_culture_note": "ไม่อยู่ใต้ห้องน้ำ · ไม่ติดผนังห้องน้ำ",
                     "fengshui_note": "โต๊ะพระสูงเสมอสายตาในขณะยืน",
                     "key_points": ["ห้ามเอาของอื่นมาเก็บ", "ระบายอากาศดี"],
                     "issues": []},
                ],
                "issues": [
                    {"rank": 1, "severity": "medium", "title": "ประตูหลักตรงห้องน้ำ (ฮวงจุ้ย)",
                     "detail": "ทางฮวงจุ้ยมองว่าไม่ดี · ลูกค้าสนใจฮวงจุ้ยจะกังวล",
                     "action": "ย้ายห้องน้ำ หรือเพิ่ม screen กั้น"},
                    {"rank": 2, "severity": "medium", "title": "Cross-ventilation จำกัด",
                     "detail": "หน้าต่างอยู่ด้านเดียว · ลมพัดไม่ผ่าน",
                     "action": "เพิ่มหน้าต่างฝั่งตรงข้าม หรือ clerestory"},
                    {"rank": 3, "severity": "low", "title": "ระยะร่นข้างบ้าน",
                     "detail": "ต้องวัดกับที่ดินข้างเคียงจริงก่อน",
                     "action": "สำรวจรังวัดก่อนออกแบบขั้นถัดไป"},
                ],
                "strengths": [
                    {"rank": 1, "title": "ที่ดินสมดุลพอเหมาะ",
                     "detail": "300 ตร.ม. พอจะจัด 3 โซน (หลัก / ผู้สูงอายุ / บริการ) แยกชัด"},
                    {"rank": 2, "title": "ห้องพระตำแหน่งดี",
                     "detail": "ชั้นบนทิศตะวันออก · ไม่ใต้ห้องน้ำ"},
                    {"rank": 3, "title": "งบสมเหตุสมผล",
                     "detail": "8 ลบ. ต่อพื้นที่ใช้สอย 240 ตร.ม. = ~33,000 บาท/ตร.ม. · grade กลาง-ดี"},
                ],
                "next_actions": [
                    {"step": 1, "action": "รังวัดที่ดินจริง", "who": "เจ้าของ", "when": "ก่อนออกแบบ"},
                    {"step": 2, "action": "ทดสอบดิน (soil test)", "who": "วิศวกร", "when": "ก่อนออกแบบ"},
                    {"step": 3, "action": "แก้ layout ประตูหลัก-ห้องน้ำ", "who": "สถาปนิก", "when": "ก่อนออกแบบ"},
                    {"step": 4, "action": "คำนวณโหลด + ฐานราก", "who": "วิศวกร", "when": "ก่อนก่อสร้าง"},
                ],
                "confidence": "medium",
                "caveats": [
                    "ไม่มีข้อมูลดินจริง · สมมติว่าเป็นดินเหนียวพอใช้ได้",
                    "ไม่ได้วัดทิศจริง · สมมติตามข้อมูลใน brief",
                ],
            },
            "analysis": None,
            "provider": "gemini",
            "timestamp": datetime.now().isoformat(),
        }

if payload:
    project_data = payload.get("project_data", {})
    structured = payload.get("structured")
    raw_analysis = payload.get("analysis")
    provider = payload.get("provider", "ai")
    timestamp = payload.get("timestamp", "")

    # Project header
    st.markdown(f"## 🏠 {project_data.get('name', '-')}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ที่ดิน", f"{project_data.get('land_w', '-')}×{project_data.get('land_d', '-')} ม.")
    col2.metric("จังหวัด", project_data.get("province", "-"))
    col3.metric("สีผังเมือง", project_data.get("zone", "-"))
    col4.metric("งบ", f"{project_data.get('budget', '-')} ลบ.")

    try:
        ts = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
    except Exception:
        ts = timestamp
    st.caption(f"🕐 วิเคราะห์เมื่อ: {ts} · Provider: {provider.title()}")

    st.markdown("---")

    # Main analysis
    if structured:
        structured_analysis.render_analysis(structured)
    elif raw_analysis:
        st.markdown(raw_analysis)
    else:
        st.warning("ไม่พบเนื้อหาใน payload")

    # Project brief (expandable)
    st.markdown("---")
    with st.expander("📋 ข้อมูลโครงการที่ใช้ในการวิเคราะห์"):
        st.json(project_data)

    # Disclaimer footer
    st.markdown("---")
    st.warning("""
**⚠ Disclaimer**

ผลวิเคราะห์นี้เป็นการประเมินเบื้องต้นโดย AI ·
**ไม่แทนที่**สถาปนิกใบอนุญาต · วิศวกรโยธาใบอนุญาต · การปรึกษาจริงหน้างาน

การขออนุญาตก่อสร้างต้องมีลายเซ็นผู้ประกอบวิชาชีพ (พรบ.ควบคุมอาคาร 2522 มาตรา 49 ทวิ) ·
Verify important decisions ก่อนทำจริง
""")

    # CTA to book consult
    st.markdown("---")
    col_cta1, col_cta2 = st.columns(2)
    with col_cta1:
        if st.button("📅 จองปรึกษากับสถาปนิกตัวจริง", type="primary", use_container_width=True):
            st.switch_page("pages/2_📅_Book_Consultation.py")
    with col_cta2:
        if st.button("🏠 กลับหน้าหลัก (วิเคราะห์ใหม่)", use_container_width=True):
            st.switch_page("app.py")


# Sidebar
with st.sidebar:
    st.markdown("### 🔗 View Mode")
    st.caption("นี่คือโหมด read-only · ไม่สามารถแก้ไขผลวิเคราะห์ได้")
    theme.theme_toggle()
    st.markdown("---")
    st.markdown("**ต้องการวิเคราะห์โปรเจคของคุณเอง?**")
    if st.button("🏠 เริ่มวิเคราะห์", use_container_width=True, key="side_start"):
        st.switch_page("app.py")
