"""
ℹ️ About Page · เกี่ยวกับสมองจำลองของสถาปนิก
"""

import streamlit as st
from components import theme, tiers

st.set_page_config(
    page_title="About · สมองจำลองของสถาปนิก",
    page_icon="ℹ️",
    layout="wide",
)

theme.apply_theme()

# Hero
st.markdown("""
<div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; color: white; margin-bottom: 30px;">
    <h1 style="color: white; font-size: 3em; margin: 0;">🏠 สมองจำลองของสถาปนิก</h1>
    <p style="font-size: 1.3em; margin-top: 10px; opacity: 0.95;">
        AI + Knowledge Graph 5 ชั้น · สำหรับสถาปัตยกรรมที่อยู่อาศัยไทย
    </p>
</div>
""", unsafe_allow_html=True)

# Mission
st.header("🎯 Mission")
st.markdown("""
ช่วยให้**เจ้าของบ้าน · สถาปนิก · นักเรียนสถาปัตย์**
วิเคราะห์แปลนและตัดสินใจออกแบบบ้านได้ดีขึ้น · **โดยใช้ความรู้ครอบคลุม 5 ชั้น**:

- 🏛 **กฎหมาย** — พรบ.ควบคุมอาคาร · กฎกระทรวง · ผังเมือง
- 🔧 **วิศวกรรม** — โครงสร้าง · MEP · วัสดุ
- 🎨 **ออกแบบ** — Passive · ergonomics · space planning
- 🪷 **วัฒนธรรมไทย** — บ้านไทย · ห้องพระ · ครัวไทย
- ☯ **ฮวงจุ้ย** — ทิศ · เตียง · เตา · ห้องน้ำ
""")

st.markdown("---")

# Stats
st.header("📊 ฐานความรู้")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Wiki Pages", "88+")
col2.metric("Categories", "8")
col3.metric("Sources", "25+")
col4.metric("Knowledge Nodes", "63")

st.markdown("---")

# How it works
st.header("🛠 วิธีใช้งาน")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1️⃣ กรอกข้อมูล")
    st.markdown("""
    - ขนาดที่ดิน
    - เขตผังเมือง
    - ครอบครัว
    - ความต้องการ
    - Upload แปลน (optional)
    """)

with col2:
    st.markdown("### 2️⃣ AI วิเคราะห์")
    st.markdown("""
    - ใช้ Gemini (ฟรี) หรือ Claude
    - Apply 5-layer KG
    - Cite ตัวเลขกฎหมายจริง
    - ~30-60 วินาที
    """)

with col3:
    st.markdown("### 3️⃣ รับผล")
    st.markdown("""
    - Feasibility check
    - 5-layer analysis
    - Top 3 issues
    - Top 3 strengths
    - Next actions
    """)

st.markdown("---")

# Technology
st.header("💻 Technology")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    ### 🔧 Stack
    - **Python** + **Streamlit**
    - **Gemini 2.5 Flash** (free tier)
    - **Claude Sonnet 4.6** (optional)
    - **Knowledge Graph** (JSON · 63 nodes · 248 edges)
    - **Open-source sources**
    """)

with col2:
    st.markdown("""
    ### 🔐 Privacy
    - ไม่เก็บแปลนที่ upload
    - ไม่เทรน AI ด้วยข้อมูลคุณ
    - Session-based · ล้างตอนปิดหน้า
    - API key ของคุณเอง (controlled by you)
    """)

st.markdown("---")

# Disclaimer
st.header("⚠ Disclaimer")
st.warning("""
**ผลวิเคราะห์เป็นการประเมินเบื้องต้น · ไม่แทนที่:**
- สถาปนิกใบอนุญาต (พรบ.สถาปนิก 2543)
- วิศวกรโยธาใบอนุญาต (พรบ.วิศวกรรม)
- การขออนุญาตก่อสร้างต้องมีลายเซ็นผู้ประกอบวิชาชีพ
  (พรบ.ควบคุมอาคาร 2522 มาตรา 49 ทวิ)
- การปรึกษาจริงหน้างาน

**AI ไม่ผิดเลยไม่ได้** · Verify important decisions ก่อนทำจริง
""")

st.markdown("---")

# Contact
st.header("📞 ติดต่อ")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📧 Email**")
    st.markdown("narongsak.bimtts2004@gmail.com")

with col2:
    st.markdown("**💬 Book Consultation**")
    if st.button("📅 จองนัด", type="primary"):
        st.switch_page("pages/2_📅_Book_Consultation.py")

with col3:
    st.markdown("**🔗 Source code**")
    st.markdown("[GitHub](https://github.com/narongsak-art/arch-brain-web)")

st.markdown("---")

# Credits
st.caption("""
**Credits:**
- Wiki knowledge base built with Claude Code (Anthropic)
- Inspired by the LLM Wiki pattern
- Based on Thai building codes · open-access research · Chula Press ergonomics
- Icons from emoji-based design

**Built with ❤ for Thai architects and homeowners**
""")

# Sidebar
with st.sidebar:
    theme.theme_toggle()
    st.markdown("---")
    tiers.sidebar_tier_badge()
