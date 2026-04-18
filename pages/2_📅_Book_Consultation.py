"""
📅 Book Consultation · จองนัดปรึกษากับสถาปนิกตัวจริง
"""

import streamlit as st
from components import theme, tiers, booking

st.set_page_config(
    page_title="จองปรึกษา · สมองจำลองของสถาปนิก",
    page_icon="📅",
    layout="wide",
)

theme.inject_css()

# Header
st.title("📅 จองนัดปรึกษาสถาปนิก")
st.caption(
    "AI ช่วยวิเคราะห์เบื้องต้น · แต่บางเรื่องต้องคุยกับสถาปนิกตัวจริง · "
    "จองนัดเพื่อรับคำแนะนำเฉพาะโปรเจคคุณ"
)

st.markdown("---")

# 2 columns: info + form
left, right = st.columns([1, 2])

with left:
    st.markdown("### 💡 เมื่อไรควรจอง")
    st.markdown("""
    - AI วิเคราะห์แล้วมี **ข้อสงสัย**
    - ต้องการ **second opinion** จากสถาปนิก
    - มีโปรเจค **ซับซ้อน** ต้องคุยรายละเอียด
    - อยากเริ่มต้นออกแบบ **บ้านใหม่**
    - ต้องการ **renovate** บ้านเก่า
    """)

    st.markdown("---")

    st.markdown("### 🎯 สิ่งที่จะได้")
    st.markdown("""
    - **1-2 ชั่วโมง** คุยแบบ focused
    - **Written summary** หลังคุย
    - **Initial concept** (ถ้า advanced)
    - **Next steps** ชัดเจน
    - **Quote** สำหรับโครงการเต็ม (ถ้าสนใจ)
    """)

    # Show Pro benefit if relevant
    if tiers.get_tier() == "free":
        st.markdown("---")
        st.info("💎 **Pro ลด 20%** · [ดูแพ็กเกจ](/Pricing)")

with right:
    booking.render_booking_form()

# History at bottom
st.markdown("---")
booking.render_bookings_history()

# Sidebar
with st.sidebar:
    theme.theme_toggle()
    st.markdown("---")
    tiers.sidebar_tier_badge()
