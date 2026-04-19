"""Explore view · read-only gallery from KG + community"""

import json
import re
from pathlib import Path

import streamlit as st

from core import theme


REPO = Path(__file__).parent.parent
KG_FILE = REPO / "kg-compact.json"
WIKI_MIRROR = REPO / "wiki-mirror" / "wiki"


@st.cache_data(ttl=300)
def _load_kg() -> dict:
    if not KG_FILE.exists():
        return {}
    try:
        return json.loads(KG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _find_related(entry_id: str, limit: int = 6) -> list[dict]:
    kg = _load_kg()
    if not kg:
        return []
    nodes = {n["id"]: n for n in kg.get("nodes", [])}
    rel_ids = set()
    for e in kg.get("edges", []):
        if e.get("from") == entry_id:
            rel_ids.add(e.get("to"))
        elif e.get("to") == entry_id:
            rel_ids.add(e.get("from"))
    rel = []
    for rid in list(rel_ids)[:limit]:
        if rid in nodes:
            n = nodes[rid]
            rel.append({
                "id": rid,
                "title": n.get("title", rid),
                "summary": (n.get("summary") or "")[:140],
            })
    return rel


def _parse_fm(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    m = re.search(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    meta: dict = {}
    for line in fm_text.split("\n"):
        km = re.match(r"^([a-zA-Z_]+):\s*(.*)$", line)
        if km:
            k, v = km.group(1), km.group(2).strip()
            if v.startswith("[") and v.endswith("]"):
                meta[k] = [x.strip().strip('"').strip("'")
                           for x in v[1:-1].split(",") if x.strip()]
            else:
                meta[k] = v.strip('"').strip("'")
    return meta, body


@st.cache_data(ttl=300)
def _load_community() -> list[dict]:
    if not WIKI_MIRROR.exists():
        return []
    out = []
    for md in WIKI_MIRROR.rglob("*.md"):
        try:
            meta, body = _parse_fm(md.read_text(encoding="utf-8"))
        except Exception:
            continue
        eid = str(md.relative_to(WIKI_MIRROR).with_suffix("")).replace("\\", "/")
        out.append({
            "source": "community",
            "id": eid,
            "title": meta.get("title", md.stem),
            "author": meta.get("author", "anonymous"),
            "tags": meta.get("tags", []),
            "body": body.strip(),
        })
    return out


def _load_seed() -> list[dict]:
    kg = _load_kg()
    out = []
    for n in kg.get("nodes", [])[:80]:
        if not n.get("summary"):
            continue
        out.append({
            "source": "seed",
            "id": n["id"],
            "title": n.get("title", n["id"]),
            "author": "curated",
            "tags": n.get("layers", []),
            "body": n["summary"],
        })
    return out


EXPLORE_CSS = """
<style>
.ex-card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 18px;
  height: 100%;
  transition: all 0.15s ease;
}
.ex-card:hover {
  border-color: var(--teak);
  box-shadow: var(--shadow-sm);
}
.ex-card .type {
  font-size: 0.72em;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--teak);
  font-weight: 600;
}
.ex-card .title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.05em;
  margin: 4px 0 6px 0;
  line-height: 1.3;
}
.ex-card .preview {
  color: var(--muted);
  font-size: 0.86em;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.tag-pill {
  background: var(--teak-soft);
  color: var(--teak);
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.78em;
  font-weight: 500;
  margin-right: 6px;
  display: inline-block;
}
</style>
"""


def _card(entry: dict, idx: int):
    st.markdown(
        f'<div class="ex-card">'
        f'<div class="type">{entry["source"]}</div>'
        f'<div class="title">{entry["title"]}</div>'
        f'<div class="preview">{entry["body"][:220]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    key_sig = f"{entry.get('source', 'x')}_{idx}_{entry.get('id', '')[-16:]}"
    if st.button("📖 เปิดอ่าน", key=f"ex_open_{key_sig}", use_container_width=True):
        st.session_state["_ex_open"] = entry["id"]
        st.rerun()


def _render_detail(entry_id: str, all_entries: list):
    entry = next((e for e in all_entries if e["id"] == entry_id), None)
    if not entry:
        st.error(f"ไม่เจอ: {entry_id}")
        if st.button("← กลับ", key="ex_back_missing"):
            del st.session_state["_ex_open"]
            st.rerun()
        return

    if st.button("← กลับ Gallery", key="ex_back"):
        del st.session_state["_ex_open"]
        st.rerun()

    st.divider()
    st.markdown(
        f'<div class="eyebrow">{entry["source"].upper()}</div>'
        f'<h2 style="margin-top:4px;">{entry["title"]}</h2>',
        unsafe_allow_html=True,
    )
    if entry.get("tags"):
        st.markdown(
            "".join(f'<span class="tag-pill">{t}</span>' for t in entry["tags"][:8]),
            unsafe_allow_html=True,
        )
    st.caption(f"by {entry.get('author', 'anonymous')}")
    st.divider()
    st.markdown(entry.get("body", "(no content)"))

    related = _find_related(entry_id)
    if related:
        st.divider()
        st.markdown(
            '<div class="eyebrow">RELATED</div>'
            '<h3 style="margin-top:4px;">🕸 หน้าที่เกี่ยวข้อง</h3>',
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for i, r in enumerate(related):
            with cols[i % 2]:
                st.markdown(
                    f'<div class="ex-card" style="padding:12px;">'
                    f'<div class="title" style="font-size:1em;">{r["title"]}</div>'
                    f'<div style="color:var(--muted); font-size:0.85em; margin-top:4px;">{r["summary"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button(f"→ {r['title'][:25]}", key=f"ex_rel_{i}_{r['id']}",
                             use_container_width=True):
                    st.session_state["_ex_open"] = r["id"]
                    st.rerun()


def render():
    """Explore view · community + KG seed gallery"""
    st.markdown(EXPLORE_CSS, unsafe_allow_html=True)

    community = _load_community()
    seed = _load_seed()
    all_entries = community + seed

    # Detail mode
    if st.session_state.get("_ex_open"):
        _render_detail(st.session_state["_ex_open"], all_entries)
        return

    theme.hero(
        "Explore · สำรวจความรู้",
        f"Knowledge Graph 104 nodes · {'{0} community entries'.format(len(community)) if community else 'seed content · ยังไม่มี community'}",
        eyebrow="EXPLORE",
    )

    entries = community if community else seed

    if not entries:
        st.info("ไม่มีข้อมูล · ตรวจ kg-compact.json")
        return

    # Filter
    all_tags = sorted({t for e in entries for t in (e.get("tags") or [])})[:20]
    c_f, c_s = st.columns([1, 2])
    selected = c_f.multiselect("Filter tags", all_tags, key="ex_tags")
    search = c_s.text_input("🔎 ค้นหา", key="ex_search")

    filtered = entries
    if selected:
        filtered = [e for e in filtered if any(t in (e.get("tags") or []) for t in selected)]
    if search:
        s_lower = search.lower()
        filtered = [e for e in filtered
                    if s_lower in e["title"].lower() or s_lower in e["body"].lower()]

    st.caption(f"แสดง {len(filtered)}/{len(entries)}")

    if not filtered:
        st.info("ไม่เจอรายการ · ลองเปลี่ยน filter")
        return

    cols = st.columns(3)
    for i, e in enumerate(filtered[:30]):
        with cols[i % 3]:
            _card(e, i)
    if len(filtered) > 30:
        st.caption(f"...อีก {len(filtered) - 30} รายการ")
