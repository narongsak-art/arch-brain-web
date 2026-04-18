"""Session history · list past analyses with load/download/delete"""

import json
from datetime import datetime

import streamlit as st

from components import analysis


FEAS_EMOJI = {"green": "🟢", "yellow": "🟡", "red": "🔴"}


def add(project_data: dict, raw_text: str, result: dict | None, provider: str):
    """Append new analysis to session history (most recent first)"""
    st.session_state.setdefault("history", [])
    entry = {
        "id": datetime.now().strftime("%Y%m%d-%H%M%S-%f"),
        "ts": datetime.now().isoformat(),
        "name": project_data.get("name", "ไม่ระบุ"),
        "province": project_data.get("province", "-"),
        "zone": project_data.get("zone", "-"),
        "land_area": project_data.get("land_area", 0),
        "provider": provider,
        "project_data": project_data,
        "raw_text": raw_text,
        "result": result,
    }
    st.session_state["history"].insert(0, entry)
    # Cap at 30 entries to prevent bloat
    st.session_state["history"] = st.session_state["history"][:30]


def get_all() -> list:
    return st.session_state.get("history", [])


def clear():
    st.session_state["history"] = []


def delete(entry_id: str):
    hist = st.session_state.get("history", [])
    st.session_state["history"] = [e for e in hist if e.get("id") != entry_id]


def load_into_current(entry: dict):
    """Restore an entry as the current result"""
    st.session_state["result"] = entry.get("result")
    st.session_state["raw_text"] = entry.get("raw_text")
    st.session_state["project_data"] = entry.get("project_data")
    st.session_state["last_provider"] = entry.get("provider")


def _build_md(entry: dict) -> str:
    """Build download markdown for one entry"""
    pd = entry["project_data"]
    result = entry.get("result")
    raw = entry.get("raw_text", "")
    provider = entry.get("provider", "ai")
    try:
        ts = datetime.fromisoformat(entry["ts"]).strftime("%Y-%m-%d %H:%M")
    except Exception:
        ts = entry.get("ts", "")
    body = analysis.to_markdown(result) if result else raw
    return f"""# ผลวิเคราะห์ — {pd.get('name','-')}

**วันที่:** {ts}
**Provider:** {provider.title()}

## ข้อมูลโครงการ

```json
{json.dumps(pd, ensure_ascii=False, indent=2)}
```

## ผลวิเคราะห์

{body}

---

*สร้างโดย สมองจำลองของสถาปนิก · ผลเบื้องต้น ไม่แทนสถาปนิก/วิศวกรใบอนุญาต*
"""


def render_panel():
    """Full history panel. Renders list of past analyses with controls."""
    hist = get_all()
    if not hist:
        st.info("🕐 ยังไม่มีประวัติ · วิเคราะห์โปรเจคแรกเพื่อเริ่มบันทึก")
        return

    # Header row with clear-all
    col_t, col_c = st.columns([4, 1])
    col_t.markdown(f"### 📚 ประวัติ session นี้ · {len(hist)} รายการ")
    if col_c.button("🗑 ล้างทั้งหมด", use_container_width=True, key="hist_clear_all"):
        clear()
        st.rerun()

    for entry in hist:
        try:
            ts = datetime.fromisoformat(entry["ts"]).strftime("%m-%d %H:%M")
        except Exception:
            ts = entry.get("ts", "")

        # Feasibility badge from structured result if available
        feas_badge = ""
        score_badge = ""
        if entry.get("result"):
            s = entry["result"].get("summary", {})
            feas = s.get("feasibility")
            if feas:
                feas_badge = f" · {FEAS_EMOJI.get(feas, '')} {feas}"
            score = s.get("score")
            if score is not None:
                score_badge = f" · {score}/100"

        title = (
            f"🏠 **{entry['name']}** · {entry['province']} · {entry['zone']} · "
            f"{entry['land_area']:.0f} ตร.ม. · {ts}{feas_badge}{score_badge}"
        )

        with st.expander(title):
            # Show the analysis
            if entry.get("result"):
                analysis.render(entry["result"])
            elif entry.get("raw_text"):
                st.markdown(entry["raw_text"])
            else:
                st.caption("(ไม่มีข้อมูล)")

            # Per-item controls
            st.divider()
            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("🔄 ใช้เป็นผลปัจจุบัน", key=f"hist_load_{entry['id']}", use_container_width=True):
                    load_into_current(entry)
                    st.rerun()

            with c2:
                st.download_button(
                    "📥 .md",
                    data=_build_md(entry),
                    file_name=f"{entry['name']}-{entry['id']}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"hist_dl_{entry['id']}",
                )

            with c3:
                if st.button("🗑 ลบ", key=f"hist_del_{entry['id']}", use_container_width=True):
                    delete(entry["id"])
                    st.rerun()
