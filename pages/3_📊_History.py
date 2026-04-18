"""
📊 History Page · ประวัติการวิเคราะห์ของ session นี้
"""

import streamlit as st
from components import theme, tiers, history

st.set_page_config(
    page_title="History · สมองจำลองของสถาปนิก",
    page_icon="📊",
    layout="wide",
)

theme.inject_css()

st.title("📊 ประวัติการวิเคราะห์")
st.caption("ผลวิเคราะห์ที่ทำใน session นี้ · ดาวน์โหลดหรือดูอีกครั้ง")

# Tier check
cfg = tiers.tier_config()
max_count = cfg["limits"]["history_count"]
st.caption(f"Tier ของคุณเก็บได้ {max_count} รายการ")

st.markdown("---")

history.render_history_panel()

# Sidebar
with st.sidebar:
    theme.theme_toggle()
    st.markdown("---")
    tiers.sidebar_tier_badge()
