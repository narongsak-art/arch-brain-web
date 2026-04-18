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
    uploaded_payload = share.upload_share_file()
    if uploaded_payload:
        payload = uploaded_payload
        st.rerun()

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
