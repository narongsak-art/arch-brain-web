"""Project Save/Load · export + import session state as JSON files

Use cases:
- User wants to keep a project brief for next time (without setting up an account)
- Share a brief+analysis bundle with a teammate (offline)
- Import/export history in bulk

Two payload schemas (version 1):
  arch-brain-project — one project (form + result)
  arch-brain-history — multiple entries from history
"""

import json
from datetime import datetime

import streamlit as st


SCHEMA_VERSION = "1.0"


# ============================================================================
# Payload builders
# ============================================================================

def build_project_payload(project_data: dict, result: dict | None = None,
                          raw_text: str | None = None, provider: str | None = None) -> dict:
    return {
        "schema": "arch-brain-project",
        "version": SCHEMA_VERSION,
        "exported_at": datetime.now().isoformat(),
        "project_data": project_data,
        "result": result,
        "raw_text": raw_text,
        "provider": provider,
    }


def build_history_payload(entries: list) -> dict:
    return {
        "schema": "arch-brain-history",
        "version": SCHEMA_VERSION,
        "exported_at": datetime.now().isoformat(),
        "count": len(entries),
        "entries": entries,
    }


# ============================================================================
# Loader / validator
# ============================================================================

ALLOWED_SCHEMAS = {"arch-brain-project", "arch-brain-history"}


def load_payload(raw: bytes | str) -> dict:
    """Parse+validate uploaded JSON. Raises ValueError on bad schema."""
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    data = json.loads(raw)
    schema = data.get("schema")
    if schema not in ALLOWED_SCHEMAS:
        raise ValueError(f"Unknown schema: {schema!r} (expected one of {ALLOWED_SCHEMAS})")
    return data


# ============================================================================
# Apply to session state
# ============================================================================

# Form widget keys (match app.py render_form())
_FORM_KEYS = [
    "form_name", "form_land_w", "form_land_d", "form_province", "form_zone",
    "form_street", "form_family", "form_elderly", "form_floors", "form_bedrooms",
    "form_budget", "form_fs", "form_special",
]
# Mapping: project_data key → form widget key + optional value transform
_PD_TO_FORM = {
    "name": ("form_name", None),
    "land_w": ("form_land_w", float),
    "land_d": ("form_land_d", float),
    "province": ("form_province", None),
    "zone": ("form_zone", None),
    "street_w": ("form_street", float),
    "family_size": ("form_family", int),
    "has_elderly": ("form_elderly", lambda v: "มี" if v == "ใช่" else "ไม่มี"),
    "floors": ("form_floors", str),
    "bedrooms": ("form_bedrooms", str),
    "budget": ("form_budget", float),
    "fengshui": ("form_fs", None),
    "special": ("form_special", None),
}


def apply_project(payload: dict, also_load_result: bool = True):
    """Load a single-project payload into the form + result area"""
    pd = payload.get("project_data") or {}

    # Populate form via session_state (BEFORE widgets render on next run)
    for pd_key, (form_key, transform) in _PD_TO_FORM.items():
        if pd_key in pd and pd[pd_key] is not None:
            val = pd[pd_key]
            if transform is not None:
                try:
                    val = transform(val)
                except Exception:
                    pass
            st.session_state[form_key] = val

    # Also load the analysis result if present and desired
    if also_load_result and (payload.get("result") or payload.get("raw_text")):
        st.session_state["result"] = payload.get("result")
        st.session_state["raw_text"] = payload.get("raw_text")
        st.session_state["project_data"] = pd
        st.session_state["last_provider"] = payload.get("provider") or "imported"


def apply_history(payload: dict) -> int:
    """Merge a history-payload into session history (dedup by id). Returns count added."""
    incoming = payload.get("entries") or []
    st.session_state.setdefault("history", [])
    existing_ids = {e.get("id") for e in st.session_state["history"]}
    added = 0
    for e in incoming:
        if e.get("id") and e["id"] in existing_ids:
            continue
        st.session_state["history"].insert(0, e)
        added += 1
    # Cap 30
    st.session_state["history"] = st.session_state["history"][:30]
    return added


# ============================================================================
# UI panel
# ============================================================================

def render_panel():
    """Full Save/Load panel · 2 columns for export, file uploader below for import"""
    st.markdown("### 💾 Save / Load Project")
    st.caption(
        "บันทึก brief + ผลวิเคราะห์เป็น `.json` · แชร์ให้ทีมหรือโหลดกลับมาใน session ถัดไป"
    )

    col_cur, col_hist = st.columns(2)

    # Export current project
    with col_cur:
        st.markdown("#### 📤 Export โปรเจคปัจจุบัน")
        pd = st.session_state.get("project_data") or _build_pd_from_form()
        if not pd or not pd.get("name"):
            st.info("กรอกฟอร์มแล้ว export ได้เลย · ถ้ามีผลวิเคราะห์จะถูกรวมด้วย")
        payload = build_project_payload(
            pd,
            result=st.session_state.get("result"),
            raw_text=st.session_state.get("raw_text"),
            provider=st.session_state.get("last_provider"),
        )
        name = (pd.get("name") or "project").replace("/", "-")
        ts = datetime.now().strftime("%Y%m%d-%H%M")
        st.download_button(
            "📥 Download project .json",
            data=json.dumps(payload, ensure_ascii=False, indent=2),
            file_name=f"project-{name}-{ts}.json",
            mime="application/json",
            use_container_width=True,
            key="pio_dl_project",
        )
        with st.expander("👁 ดูเนื้อหา"):
            st.json(payload)

    # Export full history
    with col_hist:
        st.markdown("#### 📚 Export ประวัติทั้งหมด")
        hist = st.session_state.get("history") or []
        if not hist:
            st.caption("ยังไม่มีประวัติ")
        else:
            payload = build_history_payload(hist)
            st.download_button(
                f"📥 Download history ({len(hist)} รายการ)",
                data=json.dumps(payload, ensure_ascii=False, indent=2),
                file_name=f"history-{datetime.now().strftime('%Y%m%d-%H%M')}.json",
                mime="application/json",
                use_container_width=True,
                key="pio_dl_history",
            )

    st.divider()

    # Import
    st.markdown("#### 📥 Import จากไฟล์ .json")
    uploaded = st.file_uploader(
        "เลือกไฟล์ .json (project หรือ history)",
        type=["json"],
        key="pio_upload",
    )
    if uploaded is not None:
        try:
            raw = uploaded.read()
            payload = load_payload(raw)
        except Exception as e:
            st.error(f"❌ ไฟล์ไม่ถูกต้อง: {e}")
            return

        schema = payload.get("schema")
        st.success(f"✅ โหลดไฟล์สำเร็จ · schema: `{schema}` · version: `{payload.get('version', '?')}`")

        with st.expander("👁 ดูเนื้อหา", expanded=False):
            st.json(payload)

        if schema == "arch-brain-project":
            col_a, col_b = st.columns(2)
            if col_a.button("📝 โหลดเข้าฟอร์ม (brief) เท่านั้น", use_container_width=True, key="pio_apply_form"):
                apply_project(payload, also_load_result=False)
                st.rerun()
            if col_b.button(
                "📊 โหลด brief + ผลวิเคราะห์",
                type="primary", use_container_width=True, key="pio_apply_all",
                disabled=not (payload.get("result") or payload.get("raw_text")),
            ):
                apply_project(payload, also_load_result=True)
                st.rerun()

        elif schema == "arch-brain-history":
            if st.button(
                f"📚 เพิ่ม {payload.get('count', 0)} รายการเข้าประวัติ",
                type="primary", use_container_width=True, key="pio_apply_hist",
            ):
                added = apply_history(payload)
                st.success(f"✅ เพิ่ม {added} รายการ (ข้าม duplicate)")
                st.rerun()


def _build_pd_from_form() -> dict:
    """Fallback: if project_data hasn't been built yet, assemble from current form widgets"""
    ss = st.session_state
    has_elderly = ss.get("form_elderly", "ไม่มี")
    land_w = ss.get("form_land_w", 15.0)
    land_d = ss.get("form_land_d", 20.0)
    return {
        "name": ss.get("form_name", ""),
        "land_w": land_w, "land_d": land_d, "land_area": land_w * land_d,
        "province": ss.get("form_province", ""),
        "zone": ss.get("form_zone", ""),
        "street_w": ss.get("form_street", 0),
        "family_size": ss.get("form_family", 0),
        "has_elderly": "ใช่" if has_elderly == "มี" else "ไม่",
        "floors": ss.get("form_floors", ""),
        "bedrooms": ss.get("form_bedrooms", ""),
        "budget": ss.get("form_budget", 0),
        "fengshui": ss.get("form_fs", ""),
        "special": ss.get("form_special", ""),
    }
