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

theme.apply_theme()

st.title("📊 ประวัติการวิเคราะห์")
st.caption("ผลวิเคราะห์ที่ทำใน session นี้ · ดาวน์โหลดหรือดูอีกครั้ง")

# Tier check
cfg = tiers.tier_config()
max_count = cfg["limits"]["history_count"]
st.caption(f"Tier ของคุณเก็บได้ {max_count} รายการ")

st.markdown("---")

# Render history
try:
    history.render_history_page()
except AttributeError:
    # Fallback if history.py doesn't have render_history_page
    hist = st.session_state.get("analysis_history", [])
    if not hist:
        st.info("ยังไม่มีประวัติ · ไปวิเคราะห์โปรเจคที่หน้าหลักก่อน")
        if st.button("← ไปหน้าหลัก"):
            st.switch_page("app.py")
    else:
        for i, item in enumerate(reversed(hist[-max_count:])):
            with st.expander(f"#{len(hist) - i} · {item.get('name', 'untitled')} · {item.get('timestamp', '')}"):
                st.markdown(item.get("analysis", "(no result)"))
                if item.get("project_data"):
                    with st.popover("📋 ข้อมูลโปรเจค"):
                        st.json(item["project_data"])

# Sidebar
with st.sidebar:
    theme.theme_toggle()
    st.markdown("---")
    tiers.sidebar_tier_badge()
