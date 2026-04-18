"""
💼 Pricing Page · เปรียบเทียบ Free vs Pro · Upgrade path
"""

import streamlit as st
from components import theme, tiers

st.set_page_config(
    page_title="Pricing · สมองจำลองของสถาปนิก",
    page_icon="💼",
    layout="wide",
)

theme.inject_css()

st.title("💼 แพ็กเกจและราคา")
st.caption("เลือกแพ็กเกจที่เหมาะกับการใช้งาน · ยกเลิกได้ทุกเมื่อ")

st.markdown("---")

# Tier comparison
tiers.render_tier_comparison()

st.markdown("---")

# Pricing FAQ
st.header("🤔 คำถามที่พบบ่อย")

with st.expander("Pro ต่างจาก Free ยังไง?", expanded=True):
    st.markdown("""
    **Free** = ทดลองใช้ · เหมาะสำหรับลูกค้าทั่วไปที่อยากรู้จักบ้าน 1-2 ครั้ง

    **Pro** = ใช้งานจริง · สถาปนิก · developer · คนที่ทำหลายโปรเจค
    - **PDF ระดับโปร** ส่งให้ลูกค้าได้เลย
    - **Save project** เก็บงานไว้เปิดภายหลัง
    - **Chat follow-up** ถามเพิ่มเติมหลังวิเคราะห์
    - **เปรียบเทียบ 2+ แปลน** ใน 1 session
    - **ส่วนลด consultation 20%**
    """)

with st.expander("ยกเลิก Pro ได้ไหม?"):
    st.markdown("ยกเลิกได้ทุกเมื่อ · ไม่มี lock-in · จะกลับไปใช้ Free tier")

with st.expander("ทำไม Pro ยังเป็น waitlist?"):
    st.markdown("""
    ขณะนี้ระบบ payment ยังไม่ถูกรวม ·
    สนใจ Pro · **[ลงชื่อจองผ่าน booking form](/Book_Consultation)** ·
    ทีมจะติดต่อเพื่อ activate + รับชำระ
    """)

with st.expander("มีส่วนลดสำหรับทีมไหม?"):
    st.markdown("""
    **Team plan** (3+ users): ลด 30% · ติดต่อเรา
    **Academic**: 50% off (ต้องมี .ac.th email)
    **Startup**: 3 เดือนแรก 50% off
    """)

with st.expander("ต้องมี Gemini API key ด้วยไหม?"):
    st.markdown("""
    **ใช่** · คุณต้องมี Gemini API key ของคุณเอง (รับฟรีได้ที่ aistudio.google.com)
    Key ของคุณ = billing ของคุณ · ไม่ผ่านเรา

    ทำไม: เพื่อ privacy + cost transparency · คุณควบคุมค่าใช้จ่ายเอง
    """)

st.markdown("---")

# CTA
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### 🚀 พร้อมเริ่มใช้งานแล้ว?")
    if st.button("📅 จองปรึกษากับสถาปนิก", type="primary", use_container_width=True):
        st.switch_page("pages/2_📅_Book_Consultation.py")

# Sidebar
with st.sidebar:
    theme.theme_toggle()
    st.markdown("---")
    tiers.sidebar_tier_badge()
