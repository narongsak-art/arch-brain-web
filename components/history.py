"""Analysis history · session-based storage with view/delete"""

import streamlit as st
from datetime import datetime


def _init_state():
    st.session_state.setdefault("history", [])


def add_to_history(project_data: dict, analysis: str, provider: str, structured: dict | None = None):
    """Append a new analysis to history. `structured` is parsed JSON if available."""
    _init_state()
    entry = {
        "id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "name": project_data.get("name", "ไม่ระบุ"),
        "province": project_data.get("province", "-"),
        "zone": project_data.get("zone", "-"),
        "land_area": project_data.get("land_area", 0),
        "provider": provider,
        "project_data": project_data,
        "analysis": analysis,
        "structured": structured,
    }
    st.session_state["history"].insert(0, entry)


def get_history():
    _init_state()
    return st.session_state["history"]


def clear_history():
    st.session_state["history"] = []


def delete_entry(entry_id: str):
    _init_state()
    st.session_state["history"] = [e for e in st.session_state["history"] if e["id"] != entry_id]


def render_history_panel():
    """Render the full history tab"""
    _init_state()
    history = st.session_state["history"]

    if not history:
        st.info("🕐 ยังไม่มีประวัติ · วิเคราะห์โครงการแรกเพื่อเริ่มบันทึก")
        return

    col_title, col_clear = st.columns([4, 1])
    with col_title:
        st.markdown(f"### 📚 ประวัติการวิเคราะห์ ({len(history)} รายการ)")
    with col_clear:
        if st.button("🗑 ล้างทั้งหมด", use_container_width=True, key="hist_clear_all"):
            clear_history()
            st.rerun()

    st.markdown("---")

    for entry in history:
        ts = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
        has_struct = bool(entry.get("structured"))
        struct_badge = " · ✨ Structured" if has_struct else ""
        with st.expander(
            f"🏠 **{entry['name']}** · {entry['province']} · {entry['zone']} · "
            f"{entry['land_area']:.0f} ตร.ม. · {ts} · _{entry['provider']}_{struct_badge}"
        ):
            tab_a, tab_b = st.tabs(["📊 ผลวิเคราะห์", "📋 ข้อมูลโครงการ"])
            with tab_a:
                if has_struct:
                    from components import structured_analysis
                    structured_analysis.render_analysis(entry["structured"])
                    with st.expander("📝 raw markdown / JSON"):
                        st.code(entry["analysis"], language="json")
                else:
                    st.markdown(entry["analysis"])
            with tab_b:
                st.json(entry["project_data"])

            col_dl, col_del = st.columns([3, 1])
            with col_dl:
                report = _format_report(entry)
                st.download_button(
                    "📥 ดาวน์โหลด .md",
                    data=report,
                    file_name=f"analysis-{entry['name']}-{entry['id']}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"dl_{entry['id']}",
                )
            with col_del:
                if st.button("🗑 ลบ", use_container_width=True, key=f"del_{entry['id']}"):
                    delete_entry(entry["id"])
                    st.rerun()


def _format_report(entry: dict) -> str:
    import json
    ts = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
    return f"""# ผลวิเคราะห์ — {entry['name']}

**วันที่:** {ts}
**Provider:** {entry['provider']}

## ข้อมูลโครงการ

```json
{json.dumps(entry['project_data'], ensure_ascii=False, indent=2)}
```

## ผลวิเคราะห์

{entry['analysis']}

---

*สร้างโดย สมองจำลองของสถาปนิก · Thai Residential Architecture Analysis*
"""
