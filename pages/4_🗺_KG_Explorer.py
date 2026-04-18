"""
🗺 Knowledge Graph Explorer · ดูโครงสร้างความรู้ทั้งหมด
"""

import streamlit as st
from components import theme, tiers, kg_explorer

st.set_page_config(
    page_title="KG Explorer · สมองจำลองของสถาปนิก",
    page_icon="🗺",
    layout="wide",
)

theme.inject_css()

st.title("🗺 Knowledge Graph Explorer")
st.caption(
    "ดูฐานความรู้ทั้งหมดที่ AI ใช้ในการวิเคราะห์ · เลือก node เพื่อดูรายละเอียด"
)

st.markdown("---")

kg_explorer.render_kg_explorer()

# Sidebar
with st.sidebar:
    theme.theme_toggle()
    st.markdown("---")
    tiers.sidebar_tier_badge()
