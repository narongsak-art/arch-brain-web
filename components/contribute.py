"""Contribute · ให้คนอื่นช่วยเติมเนื้อหาลงใน wiki

Phase 0: เก็บ contributions ใน session · download เป็น .json
Phase 1: Auto-save analysis → case contribution with heuristic category
Phase 2: AI-assisted organizing · suggest layers / related pages / keywords

Schema per contribution:
{
  id, timestamp, type, category, title, body, author,
  related_pages: [], status: pending,
  ai_suggestions: { layers[], related_pages[], keywords[], model, generated_at }
}
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

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


def _auto_classify(project_data: dict, result: dict | None) -> str:
    """Heuristic: pick the most relevant category for an auto-saved analysis.
    Defaults to 'design' when nothing stands out.
    """
    special = (project_data.get("special") or "").lower()
    fs = project_data.get("fengshui", "")

    rules = [
        ("fengshui", fs == "มาก"),
        ("thai-culture", "ห้องพระ" in special or "ศาลภูมิ" in special or "บ้านไทย" in special),
        ("renovation", "รีโนเวท" in special or "ต่อเติม" in special or "renovate" in special),
        ("sustainability", "solar" in special or "ประหยัดพลังงาน" in special or "edge" in special or "leed" in special),
        ("landscape", "สระ" in special or "pool" in special or "สวน" in special or "pergola" in special),
        ("smart-home", "iot" in special or "smart" in special or "automation" in special),
        ("cost", (project_data.get("budget") or 0) >= 20),
    ]
    for cat, cond in rules:
        if cond:
            return cat
    # Elderly → accessibility falls under design layer
    if project_data.get("has_elderly") == "ใช่":
        return "design"
    return "design"


def save_analysis_as_case(project_data: dict, result: dict | None, provider: str) -> dict:
    """Promote an analysis into a community case study automatically"""
    name = project_data.get("name", "ไม่ระบุ")
    zone = project_data.get("zone", "-")
    area = project_data.get("land_area", 0)
    floors = project_data.get("floors", "-")
    bedrooms = project_data.get("bedrooms", "-")
    budget = project_data.get("budget", 0)

    title = f"{name} · {zone} · {area:.0f} ตร.ม. · {floors} ชั้น · {bedrooms} BR"

    parts = ["**Brief โครงการ**", ""]
    parts.append(f"- ที่ดิน: {project_data.get('land_w')}×{project_data.get('land_d')} ม. = {area:.0f} ตร.ม.")
    parts.append(f"- จังหวัด: {project_data.get('province')} · เขต: {zone}")
    parts.append(f"- ครอบครัว: {project_data.get('family_size')} คน · ผู้สูงอายุ: {project_data.get('has_elderly')}")
    parts.append(f"- ชั้น: {floors} · ห้องนอน: {bedrooms}")
    parts.append(f"- งบ: {budget} ลบ. · ฮวงจุ้ย: {project_data.get('fengshui')}")
    if project_data.get("special"):
        parts.append(f"- พิเศษ: {project_data['special']}")

    if result:
        s = result.get("summary", {})
        parts.append("")
        parts.append(f"**AI Analysis (by {provider})**")
        parts.append("")
        parts.append(f"- Feasibility: {s.get('feasibility', '-')} · Score: {s.get('score', '-')}/100")
        if s.get("concern"):
            parts.append(f"- ⚠ ประเด็น: {s['concern']}")
        if s.get("strength"):
            parts.append(f"- ⭐ จุดเด่น: {s['strength']}")
        # Issues
        issues = result.get("issues") or []
        if issues:
            parts.append("")
            parts.append("**Top Issues:**")
            for it in issues[:3]:
                parts.append(f"- {it.get('title', '-')} — {it.get('detail', '')}")

    body = "\n".join(parts)
    category = _auto_classify(project_data, result)
    return add("case", category, title, body, author="", related_pages=[])


# ============================================================================
# Phase 2: AI-assisted organizing
# ============================================================================

LAYER_LABELS = {
    "law": "🏛 กฎหมาย",
    "eng": "🔧 วิศวกรรม",
    "design": "🎨 ออกแบบ",
    "thai": "🪷 วัฒนธรรมไทย",
    "fengshui": "☯ ฮวงจุ้ย",
}


def _load_kg_index() -> list[dict]:
    """Load the KG node list (id + title + layers) for grounding AI suggestions"""
    kg_path = Path(__file__).parent.parent / "kg-compact.json"
    if not kg_path.exists():
        return []
    try:
        data = json.loads(kg_path.read_text(encoding="utf-8"))
        return [
            {"id": n["id"], "title": n.get("title", n["id"]),
             "layers": n.get("layers", []), "type": n.get("type", "concept")}
            for n in data.get("nodes", [])
        ]
    except Exception:
        return []


def _build_organize_prompt(entry: dict, kg_nodes: list[dict]) -> tuple[str, str]:
    """Return (system, user) prompts for AI organizing task"""
    # Keep only id + title for context (minimize tokens)
    index_lines = "\n".join(
        f"- {n['id']} · {n['title']}" for n in kg_nodes[:160]
    )
    cat_meta = CATEGORIES.get(entry["category"], ("", entry["category"], ""))
    type_meta = TYPES.get(entry["type"], ("", entry["type"], ""))

    system = """คุณคือบรรณารักษ์ของ wiki สถาปัตยกรรมไทย · หน้าที่: จัดระเบียบ contribution ใหม่เข้ากับฐานข้อมูลเดิม

ตอบเป็น JSON ล้วน ห้ามใส่ markdown · เริ่มด้วย { จบด้วย }

Schema:
{
  "layers": ["law"|"eng"|"design"|"thai"|"fengshui"],
  "related_pages": [
    {"id": "concepts/xxx", "relevance": "direct|adjacent|background"}
  ],
  "keywords": ["คำสำคัญ 3-8 คำ"],
  "proposed_new_pages": [
    {"slug": "english-kebab-case", "title": "ชื่อเรื่อง", "reason": "ทำไมน่าสร้าง"}
  ],
  "short_summary": "สรุป 1-2 ประโยค"
}

- `layers`: เลือก 1-3 ชั้นที่เกี่ยวข้องมากที่สุด
- `related_pages`: ต้องเป็น id ที่อยู่ในรายการด้านล่างเท่านั้น · อย่าสร้างใหม่
- `proposed_new_pages`: เสนอเฉพาะกรณีที่ contribution นี้พูดถึงเรื่องที่ยังไม่มีหน้า · ว่างเปล่าถ้าไม่จำเป็น
"""

    user = f"""## Contribution

- ประเภท: {type_meta[0]} {type_meta[1]}
- หมวดหมู่: {cat_meta[0]} {cat_meta[1]}
- หัวเรื่อง: {entry['title']}
- เนื้อหา:

{entry['body']}

## รายการหน้า wiki ปัจจุบัน (id · title)

{index_lines}

---

จัดระเบียบ contribution นี้ตาม JSON schema ด้านบน
"""
    return system, user


def _extract_json(text: str) -> dict | None:
    """Lift JSON object from LLM response"""
    if not text:
        return None
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # brace-match
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except Exception:
                    return None
    return None


def ai_organize(entry_id: str, api_key: str, provider: str, model: str = "gemini-2.5-flash") -> dict | None:
    """Run AI organizer on a contribution by id · returns suggestions dict or None on failure"""
    from components import llm  # lazy to avoid circular at import time

    entry = next((e for e in get_all() if e["id"] == entry_id), None)
    if not entry:
        return None

    kg = _load_kg_index()
    system, user_text = _build_organize_prompt(entry, kg)

    try:
        if provider == "gemini":
            raw = llm.call_gemini(api_key, system, user_text, model=model)
        else:
            raw = llm.call_claude(api_key, system, user_text)
    except Exception as e:
        return {"error": str(e)}

    parsed = _extract_json(raw)
    if not parsed:
        return {"error": "AI ไม่ตอบเป็น JSON ที่ใช้ได้", "raw": raw[:500]}

    # Validate related_pages against known KG ids
    known_ids = {n["id"] for n in kg}
    if isinstance(parsed.get("related_pages"), list):
        parsed["related_pages"] = [
            r for r in parsed["related_pages"]
            if isinstance(r, dict) and r.get("id") in known_ids
        ]
    parsed["model"] = model
    parsed["generated_at"] = datetime.now().isoformat()

    # Persist into the contribution
    for e in st.session_state.get("contributions", []):
        if e["id"] == entry_id:
            e["ai_suggestions"] = parsed
            break

    return parsed


# ============================================================================
# Wiki-ready markdown export
# ============================================================================

def to_markdown(entry: dict) -> str:
    """Convert a contribution into the wiki page format (for eventual ingestion)"""
    cat_meta = CATEGORIES.get(entry["category"], ("", entry["category"], ""))
    type_meta = TYPES.get(entry["type"], ("", entry["type"], ""))
    ts = entry["timestamp"][:10]  # date only
    ai = entry.get("ai_suggestions") or {}

    # Merge AI-suggested layers + related with user-provided ones
    layers = ai.get("layers") or []
    related_ai = [r["id"] for r in ai.get("related_pages", []) if r.get("id")]
    related_all = list(dict.fromkeys((entry.get("related_pages") or []) + related_ai))
    keywords = ai.get("keywords") or []

    fm_lines = [
        '---',
        f'title: "{entry["title"]}"',
        'type: contribution',
        f'created: {ts}',
        f'updated: {ts}',
        f'tags: [{entry["category"]}, {entry["type"]}, community' +
        (', ' + ', '.join(keywords) if keywords else '') + ']',
    ]
    if layers:
        fm_lines.append(f'layers: [{", ".join(layers)}]')
    fm_lines.extend([
        f'author: "{entry["author"] or "anonymous"}"',
        'source_status: unverified',
        f'status: {entry["status"]}',
    ])
    if related_all:
        fm_lines.append("related:")
        for r in related_all:
            fm_lines.append(f'  - "[[{r}]]"')
    fm_lines.append('---')
    fm = "\n".join(fm_lines) + "\n"

    body_parts = [
        "",
        f"_{type_meta[0]} {type_meta[1]} · {cat_meta[0]} {cat_meta[1]}_",
        "",
        entry["body"],
    ]
    if ai.get("short_summary"):
        body_parts += ["", "> AI summary: " + ai["short_summary"]]
    if ai.get("proposed_new_pages"):
        body_parts += ["", "## 💡 AI เสนอหน้าใหม่ที่ยังไม่มี", ""]
        for p in ai["proposed_new_pages"]:
            body_parts.append(f"- **{p.get('title', '-')}** (`{p.get('slug', '-')}`) — {p.get('reason', '')}")
    if related_all:
        body_parts += ["", "## เกี่ยวข้องกับ", ""]
        body_parts += [f"- [[{r}]]" for r in related_all]

    return fm + "\n".join(body_parts) + "\n"


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

                _render_ai_panel(entry)

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


def _render_ai_panel(entry: dict):
    """Show AI-suggested metadata for a contribution, with a 'run AI' button"""
    ai = entry.get("ai_suggestions") or {}

    if ai:
        if ai.get("error"):
            st.warning(f"⚠ AI จัดระเบียบไม่สำเร็จ: {ai['error']}")
        else:
            # Display suggestions
            if ai.get("short_summary"):
                st.info(f"🧠 **AI summary:** {ai['short_summary']}")

            cols = st.columns([1, 1])
            with cols[0]:
                if ai.get("layers"):
                    st.caption("**ชั้นความรู้:**")
                    badges = " ".join(
                        f'`{LAYER_LABELS.get(l, l)}`' for l in ai["layers"]
                    )
                    st.markdown(badges)
                if ai.get("keywords"):
                    st.caption("**คำสำคัญ:**")
                    st.markdown(" ".join(f"`{k}`" for k in ai["keywords"]))
            with cols[1]:
                if ai.get("related_pages"):
                    st.caption("**หน้าที่เกี่ยวข้อง (AI):**")
                    for r in ai["related_pages"][:6]:
                        rel = r.get("relevance", "")
                        st.markdown(f"- `{r['id']}` _{rel}_")

            if ai.get("proposed_new_pages"):
                st.caption("**AI เสนอหน้าใหม่:**")
                for p in ai["proposed_new_pages"]:
                    st.markdown(f"- 💡 **{p.get('title', '-')}** — {p.get('reason', '')}")

            st.caption(
                f"_by {ai.get('model', 'ai')} · {ai.get('generated_at', '')[:16].replace('T', ' ')}_"
            )

    # Button to run (or re-run) AI
    api_key = (
        st.session_state.get("gemini_key")
        if st.session_state.get("provider", "gemini") == "gemini"
        else st.session_state.get("claude_key")
    )
    provider = st.session_state.get("provider", "gemini")
    model = st.session_state.get("sb_model", "gemini-2.5-flash")

    label = "✨ AI ช่วยจัดระเบียบ" if not ai else "🔄 รัน AI ใหม่"
    btn_cols = st.columns([3, 1])
    if btn_cols[1].button(
        label, key=f"ai_org_{entry['id']}", use_container_width=True, disabled=not api_key
    ):
        with st.spinner("AI กำลังจัดระเบียบ... ~15-30 วิ"):
            ai_organize(entry["id"], api_key, provider, model)
        st.rerun()
    if not api_key:
        btn_cols[0].caption("_ใส่ API Key ที่ sidebar ก่อนเพื่อเปิดใช้ AI organizer_")


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
