"""Project comparison · side-by-side view of 2 analyses"""

import streamlit as st
from datetime import datetime

from components import history


def render_compare_panel():
    """Render compare tab — pick 2 from history, show side-by-side"""
    entries = history.get_history()

    if len(entries) < 2:
        st.info(
            f"🔀 ต้องมีประวัติอย่างน้อย **2 รายการ** เพื่อเปรียบเทียบ "
            f"(ตอนนี้มี {len(entries)} รายการ)"
        )
        return

    st.markdown("### 🔀 เปรียบเทียบ 2 โครงการ")

    # Selectors
    options = {e["id"]: f"{e['name']} · {e['province']} · {datetime.fromisoformat(e['timestamp']).strftime('%m-%d %H:%M')}" for e in entries}
    col_a, col_b = st.columns(2)
    with col_a:
        id_a = st.selectbox("โครงการ A", options=list(options.keys()), format_func=lambda x: options[x], key="cmp_a")
    with col_b:
        default_b = list(options.keys())[1] if len(options) > 1 else list(options.keys())[0]
        id_b = st.selectbox("โครงการ B", options=list(options.keys()), format_func=lambda x: options[x], index=1 if len(options) > 1 else 0, key="cmp_b")

    if id_a == id_b:
        st.warning("⚠ เลือกโครงการเดียวกัน · กรุณาเลือกคนละโครงการ")
        return

    entry_a = next(e for e in entries if e["id"] == id_a)
    entry_b = next(e for e in entries if e["id"] == id_b)

    st.markdown("---")
    st.markdown("#### 📋 ข้อมูลโครงการ")
    _render_data_comparison(entry_a["project_data"], entry_b["project_data"])

    st.markdown("---")
    st.markdown("#### 📊 ผลวิเคราะห์")
    col_aa, col_bb = st.columns(2)
    with col_aa:
        st.markdown(f"##### 🟦 {entry_a['name']}")
        st.caption(f"_{entry_a['provider']} · {datetime.fromisoformat(entry_a['timestamp']).strftime('%Y-%m-%d %H:%M')}_")
        with st.container(height=600):
            st.markdown(entry_a["analysis"])
    with col_bb:
        st.markdown(f"##### 🟥 {entry_b['name']}")
        st.caption(f"_{entry_b['provider']} · {datetime.fromisoformat(entry_b['timestamp']).strftime('%Y-%m-%d %H:%M')}_")
        with st.container(height=600):
            st.markdown(entry_b["analysis"])


_FIELDS = [
    ("land_w", "กว้าง (ม.)", "m"),
    ("land_d", "ลึก (ม.)", "m"),
    ("land_area", "พื้นที่ดิน (ตร.ม.)", "m2"),
    ("province", "จังหวัด", "str"),
    ("zone", "สีผังเมือง", "str"),
    ("street_w", "ถนน (ม.)", "m"),
    ("family_size", "สมาชิก", "int"),
    ("has_elderly", "ผู้สูงอายุ", "str"),
    ("floors", "ชั้น", "str"),
    ("bedrooms", "ห้องนอน", "str"),
    ("budget", "งบ (ลบ.)", "float"),
    ("fengshui", "ฮวงจุ้ย", "str"),
]


def _render_data_comparison(pa: dict, pb: dict):
    """Show a diff table for project data"""
    rows = []
    for key, label, _fmt in _FIELDS:
        va, vb = pa.get(key), pb.get(key)
        same = va == vb
        marker = "" if same else "⚠"
        rows.append((label, va, vb, marker))

    import pandas as pd
    df = pd.DataFrame(rows, columns=["Field", f"A · {pa.get('name','-')}", f"B · {pb.get('name','-')}", "Δ"])
    st.dataframe(df, use_container_width=True, hide_index=True)
