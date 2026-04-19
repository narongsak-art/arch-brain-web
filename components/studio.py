"""Studio · gallery-first landing · inspired by drafted.ai with Thai identity

Shows user's work as a curated gallery:
- 📌 My Pins · favorited designs (empty state friendly)
- 🏠 My Designs · all past analyses as cards with feasibility badges
- 🎨 Renders · generated mockup images

Click a card → load that analysis back as current result.
"""

from datetime import datetime
from typing import Literal

import streamlit as st

from components import history


FEAS_META = {
    "green":  ("🟢", "ทำได้เลย"),
    "yellow": ("🟡", "ระวัง"),
    "red":    ("🔴", "ต้องปรับ"),
}


# ============================================================================
# Pin management (bookmark favorites)
# ============================================================================

def _pins() -> list[str]:
    return st.session_state.setdefault("studio_pins", [])


def toggle_pin(entry_id: str):
    pins = _pins()
    if entry_id in pins:
        pins.remove(entry_id)
    else:
        pins.insert(0, entry_id)


def is_pinned(entry_id: str) -> bool:
    return entry_id in _pins()


# ============================================================================
# Studio CSS (editorial gallery cards)
# ============================================================================

STUDIO_CSS = """
<style>
  .studio-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 28px 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }
  .studio-section-header h3 {
    font-family: var(--font-display);
    font-size: 1.5em;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--text);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .studio-section-header .count {
    color: var(--text-subtle);
    font-size: 0.75em;
    font-weight: 500;
  }

  .design-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px;
    transition: all 0.15s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
    position: relative;
  }
  .design-card:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }
  .design-card .feas-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    font-size: 0.8em;
    background: var(--surface-alt);
    padding: 3px 8px;
    border-radius: 999px;
    border: 1px solid var(--border);
  }
  .design-card .card-title {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.1em;
    color: var(--text);
    line-height: 1.3;
    margin-right: 40px; /* leave space for feas badge */
  }
  .design-card .card-meta {
    font-size: 0.82em;
    color: var(--text-muted);
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  .design-card .card-meta .separator { color: var(--text-subtle); }
  .design-card .card-score {
    font-family: var(--font-display);
    font-size: 1.6em;
    font-weight: 700;
    color: var(--primary);
    line-height: 1;
  }
  .design-card .card-score small {
    font-family: var(--font-body);
    font-size: 0.6em;
    color: var(--text-subtle);
    font-weight: 400;
  }

  .empty-state {
    background: var(--surface-alt);
    border: 2px dashed var(--border-strong);
    border-radius: var(--radius-md);
    padding: 40px 28px;
    text-align: center;
  }
  .empty-state-icon { font-size: 2.4em; margin-bottom: 8px; }
  .empty-state h4 {
    font-family: var(--font-display);
    margin: 0 0 6px 0;
    color: var(--text);
  }
  .empty-state p {
    color: var(--text-muted);
    margin: 0;
    font-size: 0.92em;
  }
</style>
"""


def _inject_studio_css():
    st.markdown(STUDIO_CSS, unsafe_allow_html=True)


# ============================================================================
# Card renderer
# ============================================================================

def _render_card(entry: dict, idx: int, variant: Literal["full", "pin"] = "full"):
    """Render one design card in a column · call inside `with col:` context"""
    pd = entry.get("project_data") or {}
    result = entry.get("result") or {}
    summary = result.get("summary") or {}

    feas = summary.get("feasibility") or "yellow"
    feas_emoji, feas_label = FEAS_META.get(feas, ("❔", "-"))
    score = summary.get("score", "—")

    try:
        ts = datetime.fromisoformat(entry["ts"]).strftime("%d %b %y")
    except Exception:
        ts = "—"

    province = pd.get("province", "-")[:15]
    zone = pd.get("zone", "-")
    area = pd.get("land_area", 0)
    area_str = f"{area:.0f} ตร.ม." if area else "-"

    card_html = f"""
    <div class="design-card">
      <div class="feas-badge">{feas_emoji} {feas_label}</div>
      <div class="card-title">{entry.get('name', '-')}</div>
      <div class="card-score">{score}<small> /100</small></div>
      <div class="card-meta">
        <span>📍 {province}</span>
        <span class="separator">·</span>
        <span>{zone}</span>
        <span class="separator">·</span>
        <span>{area_str}</span>
      </div>
      <div class="card-meta">
        <span>🕐 {ts}</span>
        <span class="separator">·</span>
        <span>{entry.get('provider', 'ai').title()}</span>
      </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # Action buttons below card
    c1, c2 = st.columns(2)
    if c1.button("🔄 เปิด", key=f"studio_open_{variant}_{idx}_{entry['id']}", use_container_width=True):
        history.load_into_current(entry)
        st.rerun()
    pin_label = "📌 unpin" if is_pinned(entry["id"]) else "📍 pin"
    if c2.button(pin_label, key=f"studio_pin_{variant}_{idx}_{entry['id']}", use_container_width=True):
        toggle_pin(entry["id"])
        st.rerun()


# ============================================================================
# Sections
# ============================================================================

def _section_header(title: str, count: int):
    st.markdown(
        f'<div class="studio-section-header">'
        f'<h3>{title} <span class="count">· {count}</span></h3>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_pins_section(entries_by_id: dict):
    pinned_ids = _pins()
    pinned_entries = [entries_by_id[eid] for eid in pinned_ids if eid in entries_by_id]
    _section_header("📌 ที่ปักหมุด", len(pinned_entries))

    if not pinned_entries:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">📌</div>'
            '<h4>ยังไม่ได้ปักหมุดงานไหน</h4>'
            '<p>ปักหมุดงานที่ชอบไว้ดูเร็วๆ · กดปุ่ม <b>📍 pin</b> ใต้การ์ดด้านล่าง</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    cols = st.columns(3)
    for i, entry in enumerate(pinned_entries[:6]):
        with cols[i % 3]:
            _render_card(entry, i, variant="pin")


def _render_designs_section(entries: list):
    _section_header("🏠 ผลงานของฉัน", len(entries))

    if not entries:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">✨</div>'
            '<h4>เริ่มวิเคราะห์โปรเจคแรก</h4>'
            '<p>กดปุ่ม <b>"เริ่มวิเคราะห์"</b> ด้านล่าง · หรือเลือก preset เร็วๆ · '
            'ผลวิเคราะห์แต่ละชิ้นจะเก็บเป็นการ์ดในนี้โดยอัตโนมัติ</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("👇 ไปที่ฟอร์ม", type="primary", use_container_width=True, key="studio_goto_form"):
            # Streamlit can't scroll natively; just rerun and hope for the best
            st.rerun()
        return

    cols = st.columns(3)
    for i, entry in enumerate(entries):
        with cols[i % 3]:
            _render_card(entry, i, variant="full")


def _render_renders_section():
    """Show generated mockup images in a gallery if any exist"""
    renders = st.session_state.get("generated_images") or []
    _section_header("🎨 ภาพ render", len(renders))

    if not renders:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">🎨</div>'
            '<h4>ยังไม่มีภาพ render</h4>'
            '<p>สร้างภาพ mockup จาก brief ได้ที่แท็บ <b>🎨 ภาพ mockup</b></p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    cols = st.columns(3)
    for i, img in enumerate(renders[:6]):
        with cols[i % 3]:
            st.image(img["bytes"], use_container_width=True)
            st.caption(f"{img.get('view_type', '?')} · {img.get('model', '?')}")


# ============================================================================
# Main entry
# ============================================================================

def render_panel():
    """Full Studio view · call from a tab"""
    _inject_studio_css()

    # Eyebrow + heading
    st.markdown(
        '<div class="ab-eyebrow">ARCHITECT\'S STUDIO</div>'
        '<h2 style="margin-top: 4px; margin-bottom: 12px;">สตูดิโอของฉัน</h2>'
        '<p style="color: var(--text-muted); margin-bottom: 18px;">'
        'ผลงานวิเคราะห์ทั้งหมดของคุณ · ปักหมุดชิ้นที่ชอบ · เปิดกลับมาแก้ไขได้ทุกเมื่อ'
        '</p>',
        unsafe_allow_html=True,
    )

    entries = history.get_all()
    entries_by_id = {e["id"]: e for e in entries}

    _render_pins_section(entries_by_id)
    _render_designs_section(entries)
    _render_renders_section()
