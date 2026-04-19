"""Studio view · gallery of past analyses · pin + load"""

from datetime import datetime

import streamlit as st

from core import analysis, theme


FEAS = {"green": ("🟢", "ทำได้เลย"),
        "yellow": ("🟡", "ระวัง"),
        "red": ("🔴", "ต้องปรับ")}


def _pins() -> list:
    return st.session_state.setdefault("studio_pins", [])


def _toggle_pin(entry_id: str):
    pins = _pins()
    if entry_id in pins:
        pins.remove(entry_id)
    else:
        pins.insert(0, entry_id)


def _load_entry(entry: dict):
    """Push an entry back into the Create view as current result"""
    st.session_state["cf_result"] = entry.get("result")
    st.session_state["cf_raw"] = entry.get("raw_text")
    st.session_state["cf_pd"] = entry.get("project_data")
    st.session_state["cf_provider"] = entry.get("provider", "ai")


def _delete(entry_id: str):
    st.session_state["history"] = [
        e for e in st.session_state.get("history", []) if e.get("id") != entry_id
    ]
    pins = _pins()
    if entry_id in pins:
        pins.remove(entry_id)


CARD_CSS = """
<style>
.studio-card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
  height: 100%;
  transition: all 0.15s ease;
  position: relative;
}
.studio-card:hover {
  border-color: var(--teak);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.studio-card .feas {
  position: absolute;
  top: 14px;
  right: 14px;
  font-size: 0.78em;
  background: var(--sand);
  padding: 2px 8px;
  border-radius: 999px;
}
.studio-card h4 {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.05em;
  margin: 0 0 6px 0;
  line-height: 1.3;
  padding-right: 46px;
}
.studio-card .score {
  font-family: var(--font-display);
  font-size: 1.6em;
  font-weight: 700;
  color: var(--teak);
  line-height: 1;
  margin: 4px 0 8px 0;
}
.studio-card .score small {
  font-family: var(--font-body);
  font-size: 0.58em;
  color: var(--subtle);
  font-weight: 400;
}
.studio-card .meta {
  font-size: 0.82em;
  color: var(--muted);
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.studio-card .meta .sep { color: var(--subtle); }
.empty {
  background: var(--sand);
  border: 2px dashed var(--border-strong);
  border-radius: 10px;
  padding: 48px 28px;
  text-align: center;
}
.empty h3 { font-family: var(--font-display); margin: 0 0 6px 0; }
.empty p { color: var(--muted); margin: 0; }
</style>
"""


def _card(entry: dict, idx: int, section: str):
    pd = entry.get("project_data") or {}
    result = entry.get("result") or {}
    s = result.get("summary") or {}
    feas = s.get("feasibility") or "yellow"
    feas_emoji, feas_label = FEAS.get(feas, ("❔", "-"))
    score = s.get("score", "—")
    try:
        ts = datetime.fromisoformat(entry["ts"]).strftime("%d %b")
    except Exception:
        ts = "-"
    area = pd.get("land_area", 0)
    area_str = f"{area:.0f} ตร.ม." if area else "-"

    st.markdown(
        f'<div class="studio-card">'
        f'<div class="feas">{feas_emoji} {feas_label}</div>'
        f'<h4>{entry.get("name", "-")}</h4>'
        f'<div class="score">{score}<small> /100</small></div>'
        f'<div class="meta">'
        f'<span>📍 {pd.get("province", "-")}</span>'
        f'<span class="sep">·</span>'
        f'<span>{pd.get("zone", "-")}</span>'
        f'<span class="sep">·</span>'
        f'<span>{area_str}</span>'
        f'</div>'
        f'<div class="meta"><span>🕐 {ts}</span>'
        f'<span class="sep">·</span><span>{entry.get("provider", "ai")}</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    eid = entry["id"]
    if c1.button("🔄 เปิด", key=f"st_open_{section}_{idx}_{eid}", use_container_width=True):
        _load_entry(entry)
        st.success("โหลดแล้ว · ไปแท็บ Create")
    pin_label = "📌 pinned" if eid in _pins() else "📍 pin"
    if c2.button(pin_label, key=f"st_pin_{section}_{idx}_{eid}", use_container_width=True):
        _toggle_pin(eid)
        st.rerun()
    if c3.button("🗑", key=f"st_del_{section}_{idx}_{eid}", use_container_width=True):
        _delete(eid)
        st.rerun()


def _section(title: str, entries: list, section_key: str):
    st.markdown(
        f'<div style="display:flex; align-items:center; justify-content:space-between;'
        f'margin: 24px 0 12px 0; border-bottom: 1px solid var(--border); padding-bottom: 8px;">'
        f'<h3 style="margin:0; font-family:var(--font-display);">{title}</h3>'
        f'<span style="color:var(--subtle); font-size:0.9em;">· {len(entries)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if not entries:
        return None
    cols = st.columns(3)
    for i, e in enumerate(entries):
        with cols[i % 3]:
            _card(e, i, section_key)


def render():
    """Studio view · 2 sections: pinned + all designs"""
    st.markdown(CARD_CSS, unsafe_allow_html=True)
    theme.hero(
        "สตูดิโอของฉัน",
        "งานทั้งหมดของคุณ · ปักหมุด · เปิดกลับมาแก้",
        eyebrow="MY STUDIO",
    )

    entries = st.session_state.get("history", [])
    entries_by_id = {e["id"]: e for e in entries}
    pinned = [entries_by_id[eid] for eid in _pins() if eid in entries_by_id]

    if not entries:
        st.markdown(
            '<div class="empty">'
            '<h3>✨ ยังไม่มีงาน</h3>'
            '<p>ไปแท็บ <b>Create</b> · วิเคราะห์โปรเจคแรก · ผลจะเก็บเป็นการ์ดในนี้</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    if pinned:
        _section("📌 ที่ปักหมุด", pinned[:6], "pin")

    _section("🏠 ผลงานทั้งหมด", entries, "all")
