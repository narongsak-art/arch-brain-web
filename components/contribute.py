"""Contribute · ให้คนอื่นช่วยเติมเนื้อหาลงใน wiki

Phase 0: เก็บ contributions ใน session · download เป็น .json
(Phase later: push to GitHub → admin review → merge to wiki/)

Schema per contribution:
{
  id, timestamp, type, category, title, body, author,
  related_pages: [], status: pending
}
"""

import json
import uuid
from datetime import datetime

import streamlit as st


# ============================================================================
# Taxonomy — 12 หัวข้อ × 4 ประเภท
# ============================================================================

CATEGORIES = {
    "law-zoning":      ("🏛", "กฎหมายและผังเมือง",       "ระยะร่น · FAR · OSR · ข้อบัญญัติ"),
    "structure":       ("🔧", "โครงสร้างและวัสดุ",       "ฐานราก · คาน · เสา · คอนกรีต · เหล็ก"),
    "mep":             ("⚡", "ระบบงานอาคาร",            "ไฟฟ้า · ประปา · แอร์ · ระบายอากาศ"),
    "design":          ("🎨", "ออกแบบและสัดส่วน",        "space planning · ergonomics · passive"),
    "thai-culture":    ("🪷", "วัฒนธรรมวิถีไทย",         "ห้องพระ · ครัวไทย · ศาลภูมิ · บ้านพื้นถิ่น"),
    "fengshui":        ("☯",  "ฮวงจุ้ย",                 "ทิศ · ประตู · เตียง · เตา · กระจก"),
    "landscape":       ("🌳", "ภูมิสถาปัตย์และสวน",       "สวน · ต้นไม้ · สระ · pergola · hardscape"),
    "sustainability":  ("🌱", "ความยั่งยืนและพลังงาน",   "solar · rainwater · LEED · EDGE · WELL"),
    "renovation":      ("🏚", "รีโนเวทและซ่อมแซม",       "บ้านเก่า · ต่อเติม · termite · ตรวจโครงสร้าง"),
    "cost":            ("💰", "งบประมาณและต้นทุน",       "ราคา/ตร.ม. · BOQ · value engineering"),
    "smart-home":      ("🤖", "สมาร์ทโฮมและเทคโนโลยี",    "IoT · security · Matter · automation"),
    "bim-tools":       ("📐", "BIM และเครื่องมือออกแบบ", "Revit · ArchiCAD · SketchUp · Rhino"),
}

TYPES = {
    "correction": ("📝", "แก้ไข · ทักท้วง", "เจอข้อผิดในเว็ป · ช่วยแก้"),
    "proposal":   ("💡", "เสนอเรื่องใหม่",  "เสนอหัวข้อ wiki ใหม่ที่ยังไม่มี"),
    "case":       ("🏗", "เคสจริง",         "แชร์โปรเจคจริง · lesson learned"),
    "question":   ("❓", "คำถาม",            "ถามเรื่องที่ยังหาคำตอบไม่เจอ"),
}


# ============================================================================
# Session storage
# ============================================================================

def _init():
    st.session_state.setdefault("contributions", [])


def add(c_type: str, category: str, title: str, body: str,
        author: str = "", related_pages: list | None = None) -> dict:
    _init()
    entry = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "type": c_type,
        "category": category,
        "title": title.strip(),
        "body": body.strip(),
        "author": author.strip(),
        "related_pages": related_pages or [],
        "status": "pending",
    }
    st.session_state["contributions"].insert(0, entry)
    return entry


def get_all() -> list:
    _init()
    return st.session_state["contributions"]


def delete(entry_id: str):
    st.session_state["contributions"] = [
        e for e in get_all() if e["id"] != entry_id
    ]


def clear():
    st.session_state["contributions"] = []


def to_markdown(entry: dict) -> str:
    """Convert a contribution into the wiki page format (for eventual ingestion)"""
    cat_meta = CATEGORIES.get(entry["category"], ("", entry["category"], ""))
    type_meta = TYPES.get(entry["type"], ("", entry["type"], ""))
    ts = entry["timestamp"][:10]  # date only

    fm = f"""---
title: "{entry['title']}"
type: contribution
created: {ts}
updated: {ts}
tags: [{entry['category']}, {entry['type']}, community]
author: "{entry['author'] or 'anonymous'}"
source_status: unverified
status: {entry['status']}
---
"""
    body = f"""
_{type_meta[0]} {type_meta[1]} · {cat_meta[0]} {cat_meta[1]}_

{entry['body']}
"""
    if entry["related_pages"]:
        body += "\n\n## เกี่ยวข้องกับ\n" + "\n".join(f"- [[{p}]]" for p in entry["related_pages"])

    return fm + body


# ============================================================================
# UI
# ============================================================================

def _render_new_form():
    """Form for creating a new contribution"""
    st.markdown("### 💡 ช่วยเติมเรื่องใหม่")
    st.caption("ช่วยให้ AI ฉลาดขึ้น · ทุกคนได้ประโยชน์")

    c1, c2 = st.columns(2)
    with c1:
        c_type = st.selectbox(
            "ประเภท",
            options=list(TYPES.keys()),
            format_func=lambda k: f"{TYPES[k][0]} {TYPES[k][1]}",
            key="contrib_type",
            help=lambda k: TYPES[k][2] if False else None,
        )
        st.caption(f"_{TYPES[c_type][2]}_")
    with c2:
        category = st.selectbox(
            "หัวข้อ",
            options=list(CATEGORIES.keys()),
            format_func=lambda k: f"{CATEGORIES[k][0]} {CATEGORIES[k][1]}",
            key="contrib_category",
        )
        st.caption(f"_{CATEGORIES[category][2]}_")

    title = st.text_input(
        "หัวเรื่องสั้นๆ *",
        placeholder="เช่น · \"ระยะร่นข้างบ้านเขต ย.5 ควรใส่ 2 ม. ไม่ใช่ 3 ม.\"",
        key="contrib_title",
        max_chars=120,
    )

    body = st.text_area(
        "รายละเอียด *",
        placeholder=(
            "อธิบายให้ชัดเจน · ถ้ามี source อ้างอิงได้ · ถ้าเป็นเคสจริงบอกโครงการ/ขนาด/งบ\n\n"
            "ตัวอย่าง:\n"
            "เคสรีโนเวทบ้าน 2 ชั้น 200 ตร.ม. ที่นนทบุรี งบ 2 ล้าน · เจอปัญหา foundation crack..."
        ),
        height=220,
        key="contrib_body",
    )

    author = st.text_input(
        "ชื่อผู้ส่ง (ไม่บังคับ)",
        placeholder="ว่างไว้ได้ · จะเป็น anonymous",
        key="contrib_author",
        max_chars=60,
    )

    related = st.text_input(
        "หน้า wiki ที่เกี่ยวข้อง (ไม่บังคับ)",
        placeholder="เช่น · wiki/concepts/ระยะร่น, wiki/concepts/FAR-OSR-ข้อกำหนดผังเมือง (comma-separated)",
        key="contrib_related",
    )
    related_list = [r.strip() for r in related.split(",") if r.strip()]

    can_submit = bool(title.strip()) and bool(body.strip())

    if st.button(
        "📤 ส่งเข้ากล่องรอเข้า",
        type="primary", use_container_width=True, disabled=not can_submit,
    ):
        entry = add(c_type, category, title, body, author, related_list)
        st.success(f"✅ บันทึกแล้ว · id `{entry['id']}` · สถานะ: pending")
        # Reset form
        for k in ["contrib_title", "contrib_body", "contrib_author", "contrib_related"]:
            if k in st.session_state:
                st.session_state[k] = ""
        st.rerun()

    if not can_submit:
        st.caption("กรอก **หัวเรื่อง** และ **รายละเอียด** ให้ครบก่อนส่ง")


def _render_browse():
    """Browse existing contributions with category filter"""
    entries = get_all()
    if not entries:
        st.info("📦 กล่องยังว่าง · ช่วยเติมเรื่องแรกดูสิ")
        return

    # Category filter
    cat_counts = {}
    for e in entries:
        cat_counts[e["category"]] = cat_counts.get(e["category"], 0) + 1

    col_t, col_f = st.columns([2, 2])
    col_t.markdown(f"### 📦 กล่องรอเข้า · {len(entries)} รายการ")

    options = ["ทั้งหมด"] + sorted(cat_counts.keys(), key=lambda k: -cat_counts[k])
    selected = col_f.selectbox(
        "กรองหัวข้อ",
        options=options,
        format_func=lambda k: (
            "🗂 ทั้งหมด" if k == "ทั้งหมด"
            else f"{CATEGORIES[k][0]} {CATEGORIES[k][1]} ({cat_counts[k]})"
        ),
        key="contrib_filter",
    )

    filtered = entries if selected == "ทั้งหมด" else [e for e in entries if e["category"] == selected]

    # Group by category
    groups: dict = {}
    for e in filtered:
        groups.setdefault(e["category"], []).append(e)

    # Render per-group
    for cat_key, items in sorted(groups.items()):
        emoji, name, _ = CATEGORIES.get(cat_key, ("", cat_key, ""))
        st.markdown(f"#### {emoji} {name} · {len(items)}")
        for entry in items:
            t_emoji, t_label, _ = TYPES.get(entry["type"], ("", entry["type"], ""))
            ts = entry["timestamp"][:16].replace("T", " ")
            header = f"{t_emoji} **{entry['title']}** · {ts}"
            if entry.get("author"):
                header += f" · _by {entry['author']}_"

            with st.expander(header):
                st.caption(f"id `{entry['id']}` · type: {t_label} · status: {entry['status']}")
                st.markdown(entry["body"])
                if entry.get("related_pages"):
                    st.caption("เกี่ยวข้อง: " + ", ".join(entry["related_pages"]))

                cc1, cc2, cc3 = st.columns(3)
                cc1.download_button(
                    "📥 .json",
                    data=json.dumps(entry, ensure_ascii=False, indent=2),
                    file_name=f"{entry['category']}-{entry['id']}.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"dl_json_{entry['id']}",
                )
                cc2.download_button(
                    "📄 .md (wiki-ready)",
                    data=to_markdown(entry),
                    file_name=f"{entry['category']}-{entry['id']}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"dl_md_{entry['id']}",
                )
                if cc3.button("🗑 ลบ", use_container_width=True, key=f"del_{entry['id']}"):
                    delete(entry["id"])
                    st.rerun()


def _render_bulk_download():
    """Bulk-export all contributions as a single JSON"""
    entries = get_all()
    if not entries:
        return
    st.divider()
    bulk = {
        "exported_at": datetime.now().isoformat(),
        "count": len(entries),
        "contributions": entries,
    }
    col_dl, col_clear = st.columns([3, 1])
    col_dl.download_button(
        f"📦 Download ทั้งหมด ({len(entries)} รายการ) · .json",
        data=json.dumps(bulk, ensure_ascii=False, indent=2),
        file_name=f"contributions-{datetime.now().strftime('%Y%m%d-%H%M')}.json",
        mime="application/json",
        use_container_width=True,
        key="contrib_bulk_dl",
    )
    if col_clear.button("🗑 ล้างทั้งหมด", use_container_width=True, key="contrib_clear_all"):
        clear()
        st.rerun()


def render_panel():
    """Main entry · call from a tab"""
    tab_new, tab_browse = st.tabs(["✍ เขียนเรื่องใหม่", "📦 เรื่องที่เขียนแล้ว"])
    with tab_new:
        _render_new_form()
    with tab_browse:
        _render_browse()
        _render_bulk_download()
