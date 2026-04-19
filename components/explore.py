"""Explore · community gallery of approved contributions

Reads approved `.md` files from `wiki-mirror/wiki/` (populated by the
promote-approved GH Action) and renders them as editorial cards.
Users can browse by category or type.

If wiki-mirror doesn't exist yet (no approved contributions), shows a
curated "seed examples" gallery from the Knowledge Graph so the tab
is never empty.
"""

import json
import re
from pathlib import Path

import streamlit as st

from components.contribute import CATEGORIES, TYPES


REPO_ROOT = Path(__file__).parent.parent
WIKI_MIRROR = REPO_ROOT / "wiki-mirror" / "wiki"
KG_FILE = REPO_ROOT / "kg-compact.json"


EXPLORE_CSS = """
<style>
  .explore-hero {
    padding: 32px 28px;
    background: var(--surface-alt);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    margin-bottom: 20px;
  }
  .explore-hero h2 {
    font-family: var(--font-display);
    margin: 0 0 8px 0;
    font-size: 1.8em;
  }
  .explore-hero p {
    color: var(--text-muted);
    margin: 0;
  }

  .explore-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px;
    transition: all 0.15s ease;
    height: 100%;
  }
  .explore-card:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow-sm);
  }
  .explore-card .explore-type {
    font-size: 0.75em;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--primary);
    font-weight: 600;
  }
  .explore-card .explore-title {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.1em;
    margin: 4px 0 6px 0;
    line-height: 1.3;
  }
  .explore-card .explore-preview {
    color: var(--text-muted);
    font-size: 0.88em;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .explore-card .explore-meta {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    font-size: 0.78em;
    color: var(--text-subtle);
  }
</style>
"""


# ============================================================================
# Loaders
# ============================================================================

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (meta_dict, body_text)"""
    if not text.startswith("---"):
        return {}, text
    m = re.search(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    meta: dict = {}
    current_list_key = None
    for line in fm_text.split("\n"):
        line = line.rstrip()
        if not line:
            current_list_key = None
            continue
        if line.startswith("  - ") or line.startswith("- "):
            val = line.split("- ", 1)[1].strip().strip('"').strip("'")
            if current_list_key:
                meta.setdefault(current_list_key, []).append(val)
            continue
        km = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if km:
            key = km.group(1)
            val = km.group(2).strip()
            if val == "":
                current_list_key = key
                meta[key] = []
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1]
                meta[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            else:
                meta[key] = val.strip('"').strip("'")
            current_list_key = None if val else key
    return meta, body


def _load_community_entries() -> list[dict]:
    """Load approved contributions from wiki-mirror/"""
    entries = []
    if not WIKI_MIRROR.exists():
        return entries
    for md_file in WIKI_MIRROR.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(text)
        except Exception:
            continue
        entries.append({
            "source": "community",
            "id": str(md_file.relative_to(WIKI_MIRROR).with_suffix("")).replace("\\", "/"),
            "title": meta.get("title", md_file.stem),
            "author": meta.get("author", "anonymous"),
            "tags": meta.get("tags", []),
            "body": body.strip(),  # keep full body for detail view
            "path": str(md_file.relative_to(REPO_ROOT)),
            "category": meta.get("tags", [""])[0] if meta.get("tags") else "",
            "full_body": body.strip(),
        })
    return entries


@st.cache_data(ttl=300, show_spinner=False)
def _load_kg() -> dict:
    if not KG_FILE.exists():
        return {}
    try:
        return json.loads(KG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def _load_seed_entries() -> list[dict]:
    """Fallback: pull top-level KG pages as seed content when wiki-mirror is empty"""
    kg = _load_kg()
    out = []
    for n in kg.get("nodes", [])[:60]:
        if not n.get("summary"):
            continue
        out.append({
            "source": "seed",
            "id": n["id"],
            "title": n.get("title", n["id"]),
            "author": "curated",
            "tags": n.get("layers", []),
            "body": n["summary"],
            "path": n["id"],
            "category": n.get("type", "concept"),
        })
    return out


def _find_related(entry_id: str, limit: int = 8) -> list[dict]:
    """Look up related nodes via KG edges + return list of {id, title}"""
    kg = _load_kg()
    if not kg:
        return []
    nodes_by_id = {n["id"]: n for n in kg.get("nodes", [])}
    related_ids: set = set()
    for e in kg.get("edges", []):
        if e.get("from") == entry_id:
            related_ids.add(e.get("to"))
        elif e.get("to") == entry_id:
            related_ids.add(e.get("from"))
    related = []
    for rid in list(related_ids)[:limit]:
        if rid in nodes_by_id:
            n = nodes_by_id[rid]
            related.append({
                "id": rid,
                "title": n.get("title", rid),
                "summary": (n.get("summary") or "")[:160],
                "layers": n.get("layers", []),
            })
    return related


# ============================================================================
# Rendering
# ============================================================================

def _render_card(entry: dict, idx: int):
    type_label = entry.get("source", "seed").upper()
    st.markdown(
        f'<div class="explore-card">'
        f'<div class="explore-type">{type_label}</div>'
        f'<div class="explore-title">{entry["title"]}</div>'
        f'<div class="explore-preview">{entry["body"][:220]}{"..." if len(entry["body"]) > 220 else ""}</div>'
        f'<div class="explore-meta">📁 {entry["path"][:50]}{"..." if len(entry["path"]) > 50 else ""}'
        + (f' · by {entry["author"]}' if entry.get("author") and entry["author"] != "curated" else '')
        + '</div>'
        + '</div>',
        unsafe_allow_html=True,
    )
    key_sig = f"{entry.get('source','x')}_{idx}_{entry.get('id') or entry.get('path', '')[-20:]}"
    if st.button("📖 เปิดอ่าน", key=f"explore_open_{key_sig}", use_container_width=True):
        st.session_state["_explore_open"] = entry.get("id") or entry.get("path")
        st.rerun()


def _render_detail_view(entry_id: str, all_entries: list[dict]):
    """Show full content of one entry + related pages graph · with Back button"""
    # Find the entry
    entry = next((e for e in all_entries
                  if e.get("id") == entry_id or e.get("path") == entry_id), None)
    if not entry:
        st.error(f"ไม่เจอ entry: {entry_id}")
        if st.button("← กลับ gallery", key="explore_back_missing"):
            del st.session_state["_explore_open"]
            st.rerun()
        return

    # Back button first
    c_back, c_meta = st.columns([1, 3])
    if c_back.button("← กลับ Gallery", key="explore_back", use_container_width=True):
        del st.session_state["_explore_open"]
        st.rerun()
    c_meta.caption(
        f"📁 `{entry.get('path', entry_id)}` · by {entry.get('author', 'anonymous')}"
    )

    st.divider()

    # Main content
    st.markdown(
        f'<div class="ab-eyebrow">{entry.get("source", "seed").upper()}</div>'
        f'<h2 style="margin-top:4px;">{entry["title"]}</h2>',
        unsafe_allow_html=True,
    )

    # Tags as pills
    if entry.get("tags"):
        tag_html = " ".join(
            f'<span style="background:var(--primary-soft); color:var(--primary); '
            f'padding:3px 10px; border-radius:999px; font-size:0.82em; font-weight:500;'
            f'margin-right:6px; display:inline-block;">{t}</span>'
            for t in entry["tags"][:10]
        )
        st.markdown(f'<div style="margin:8px 0 14px 0;">{tag_html}</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    # Full body
    body = entry.get("full_body") or entry.get("body") or ""
    if body:
        st.markdown(body)
    else:
        st.caption("(no body · seed entry)")

    # Related pages from KG
    related = _find_related(entry_id)
    if related:
        st.markdown("---")
        st.markdown("#### 🕸 หน้าที่เกี่ยวข้อง (จาก Knowledge Graph)")
        cols = st.columns(2)
        for i, rel in enumerate(related):
            with cols[i % 2]:
                layers_str = " · ".join(rel.get("layers", []))
                st.markdown(
                    f'<div class="explore-card" style="padding:12px;">'
                    f'<div class="explore-title" style="font-size:1em;">{rel["title"]}</div>'
                    + (f'<div style="color:var(--text-subtle); font-size:0.75em;">{layers_str}</div>' if layers_str else '')
                    + f'<div style="color:var(--text-muted); font-size:0.85em; margin-top:6px;">{rel["summary"]}</div>'
                    + '</div>',
                    unsafe_allow_html=True,
                )
                if st.button(f"→ เปิด {rel['title'][:30]}", key=f"related_{i}_{rel['id']}", use_container_width=True):
                    st.session_state["_explore_open"] = rel["id"]
                    st.rerun()


def render_panel():
    """Explore tab · community + seed gallery · with detail view"""
    st.markdown(EXPLORE_CSS, unsafe_allow_html=True)

    community = _load_community_entries()
    seed = _load_seed_entries()
    all_entries = community + seed

    # Detail view mode · if user clicked a card
    opened_id = st.session_state.get("_explore_open")
    if opened_id:
        _render_detail_view(opened_id, all_entries)
        return

    if community:
        st.markdown(
            '<div class="explore-hero">'
            '<h2>🌐 Explore · ชุมชนแบ่งปัน</h2>'
            f'<p>ผลงานและความรู้จากสมาชิก · <b>{len(community)}</b> ชิ้นที่ผ่านการตรวจ · '
            'เหมาะกับเจ้าของบ้าน · สถาปนิก · นักเรียนสถาปัตย์</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        source = community
        source_note = f"Showing {len(community)} community-approved entries"
    else:
        st.markdown(
            '<div class="explore-hero">'
            '<h2>📖 Explore · ตัวอย่างจาก Knowledge Graph</h2>'
            '<p>ยังไม่มีเนื้อหาที่ผ่านการตรวจจากชุมชน · '
            'แสดง seed content จาก Knowledge Graph (104 หน้า) ก่อน · '
            'เขียนเรื่องใหม่ที่แท็บ <b>💡 ช่วยเติม</b> แล้วรอ admin approve เพื่อให้ขึ้นที่นี่</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        source = seed
        source_note = f"Showing {len(source)} seed entries from KG"

    # Filter
    if source:
        all_tags = sorted({t for e in source for t in (e.get("tags") or [])})
        c_filter, c_search = st.columns([1, 2])
        selected_tags = c_filter.multiselect(
            "Filter by tag",
            options=all_tags[:30],
            key="explore_tags",
        )
        search = c_search.text_input("🔎 ค้นหา (title หรือ body)", key="explore_search")

        filtered = source
        if selected_tags:
            filtered = [e for e in filtered
                        if any(t in (e.get("tags") or []) for t in selected_tags)]
        if search:
            s_lower = search.lower()
            filtered = [e for e in filtered
                        if s_lower in e["title"].lower() or s_lower in e["body"].lower()]

        st.caption(f"{source_note} · showing {len(filtered)}")

        if not filtered:
            st.info("ไม่เจอรายการตาม filter · ลอง clear หรือเปลี่ยน keyword")
            return

        # 3-column grid
        cols = st.columns(3)
        for i, entry in enumerate(filtered[:30]):
            with cols[i % 3]:
                _render_card(entry, i)

        if len(filtered) > 30:
            st.caption(f"...และอีก {len(filtered) - 30} · narrow filter เพื่อหาเจอง่ายขึ้น")
    else:
        st.info("ยังไม่มีเนื้อหาทั้งในชุมชน และ seed · อาจมีปัญหาไฟล์ KG")
