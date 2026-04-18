"""Save/Load · export/import full project state as JSON for sharing"""

import json
from datetime import datetime

import streamlit as st

from components import history, wizard

SCHEMA_VERSION = "1.0"


def build_export_payload(project_data: dict, analysis: str | None = None, provider: str | None = None) -> dict:
    return {
        "schema": "arch-brain-project",
        "version": SCHEMA_VERSION,
        "exported_at": datetime.now().isoformat(),
        "project_data": project_data,
        "analysis": analysis,
        "provider": provider,
    }


def build_history_export() -> dict:
    return {
        "schema": "arch-brain-history",
        "version": SCHEMA_VERSION,
        "exported_at": datetime.now().isoformat(),
        "entries": history.get_history(),
    }


def load_payload(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw)
    schema = data.get("schema")
    if schema not in ("arch-brain-project", "arch-brain-history"):
        raise ValueError(f"Unknown schema: {schema}")
    return data


def apply_project(payload: dict):
    """Load a single-project payload into the wizard form"""
    pd = payload.get("project_data", {})
    wizard.apply_preset(pd)
    if payload.get("analysis") and payload.get("provider"):
        history.add_to_history(pd, payload["analysis"], payload["provider"])


def apply_history(payload: dict):
    """Append all entries from a history export (dedup by id)"""
    incoming = payload.get("entries", [])
    existing_ids = {e["id"] for e in history.get_history()}
    added = 0
    for e in incoming:
        if e.get("id") in existing_ids:
            continue
        st.session_state.setdefault("history", []).insert(0, e)
        added += 1
    return added


def render_io_panel():
    """Render the Save/Load tab"""
    st.markdown("### 💾 Save / Load")
    st.caption("บันทึก/โหลดโครงการเป็นไฟล์ JSON · แชร์ต่อเพื่อนร่วมงานได้")

    col_current, col_all = st.columns(2)

    with col_current:
        st.markdown("#### 📤 Export โครงการปัจจุบัน")
        fd = st.session_state.get("form_data")
        if not fd:
            st.info("ยังไม่มีข้อมูลในฟอร์ม · กรอกข้อมูลที่แท็บ 'วิเคราะห์ใหม่' ก่อน")
        else:
            payload = build_export_payload(fd)
            st.download_button(
                "📥 ดาวน์โหลด .json",
                data=json.dumps(payload, ensure_ascii=False, indent=2),
                file_name=f"project-{fd.get('name','untitled')}-{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
            )
            with st.expander("👁 ดูเนื้อหา"):
                st.json(payload)

    with col_all:
        st.markdown("#### 📚 Export ประวัติทั้งหมด")
        entries = history.get_history()
        if not entries:
            st.info(f"ยังไม่มีประวัติ")
        else:
            payload = build_history_export()
            st.download_button(
                f"📥 ดาวน์โหลด history ({len(entries)} รายการ)",
                data=json.dumps(payload, ensure_ascii=False, indent=2),
                file_name=f"arch-brain-history-{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
            )

    st.markdown("---")
    st.markdown("#### 📥 Import จากไฟล์ JSON")
    uploaded = st.file_uploader(
        "เลือกไฟล์ .json (project หรือ history)",
        type=["json"],
        key="io_upload",
    )
    if uploaded is not None:
        try:
            raw = uploaded.read()
            payload = load_payload(raw)
            schema = payload.get("schema")
            st.success(f"✅ โหลดไฟล์สำเร็จ · schema = `{schema}` · version = `{payload.get('version')}`")

            col_preview, col_apply = st.columns([3, 1])
            with col_preview:
                with st.expander("👁 ดูเนื้อหา", expanded=False):
                    st.json(payload)
            with col_apply:
                if schema == "arch-brain-project":
                    if st.button("✅ ใช้ข้อมูล", type="primary", use_container_width=True, key="io_apply_project"):
                        apply_project(payload)
                        st.success("โหลดเข้าฟอร์มแล้ว · ไปแท็บ 'วิเคราะห์ใหม่'")
                elif schema == "arch-brain-history":
                    if st.button("✅ เพิ่มในประวัติ", type="primary", use_container_width=True, key="io_apply_history"):
                        added = apply_history(payload)
                        st.success(f"เพิ่ม {added} รายการในประวัติ (ข้าม duplicate)")
                        st.rerun()
        except Exception as e:
            st.error(f"❌ โหลดไฟล์ล้มเหลว: {e}")
