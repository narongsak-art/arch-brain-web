"""Build kg-compact.json + full-knowledge.md from the Obsidian wiki vault.

Source priority:
  1. ENV var `WIKI_VAULT` (if set)
  2. Sibling folder `../NarongsakBIM` (local dev default)
  3. Repo-local `wiki/` folder (for GitHub Actions · no vault present)
  4. Hard-coded E:/Narongsakb/NarongsakBIM (legacy fallback)

Writes (always into this repo):
  - kg-compact.json
  - full-knowledge.md

Usage:
  python scripts/build_kg.py                          # auto-detect
  WIKI_VAULT=/path/to/vault python scripts/build_kg.py
"""

import json
import os
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent


def _resolve_vault() -> Path:
    """Pick the first existing vault from the priority list"""
    env_val = os.getenv("WIKI_VAULT")
    if env_val:
        p = Path(env_val)
        if p.exists():
            return p
    candidates = [
        REPO_ROOT.parent / "NarongsakBIM",           # sibling folder
        REPO_ROOT / "wiki-mirror",                    # repo-local mirror
        Path("E:/Narongsakb/NarongsakBIM"),           # legacy hardcoded
    ]
    for c in candidates:
        if c.exists() and (c / "wiki").exists():
            return c
    # Last resort: maybe the repo itself IS the vault (has wiki/ directly)
    if (REPO_ROOT / "wiki").exists():
        return REPO_ROOT
    return candidates[0]  # return first candidate even if missing (for error message)


VAULT = _resolve_vault()
OUT_KG = REPO_ROOT / "kg-compact.json"
OUT_FULL = REPO_ROOT / "full-knowledge.md"

SUBFOLDERS = ["concepts", "syntheses", "summaries", "entities"]
SUBFOLDER_TO_TYPE = {
    "concepts": "concept",
    "syntheses": "synthesis",
    "summaries": "summary",
    "entities": "entity",
}

# Pages to include in full-knowledge.md (bundled full content for AI context)
# We'll auto-pick by: highest edge degree + specific must-haves
MUST_HAVE_IN_BUNDLE = {
    "concepts/ระยะร่น",
    "concepts/FAR-OSR-ข้อกำหนดผังเมือง",
    "concepts/ขนาดห้องตามกฎหมาย",
    "concepts/ที่จอดรถ",
    "concepts/บันไดและทางหนีไฟ",
    "concepts/พื้นที่ว่างรอบบ้าน",
    "concepts/ระยะห่างระหว่างตึกในที่ดินเดียวกัน",
    "concepts/การวางทิศบ้าน",
    "concepts/ขนาดเฟอร์นิเจอร์มาตรฐาน",
    "syntheses/แนวทางการออกแบบบ้าน",
}


def parse_frontmatter(text: str):
    """Parse YAML frontmatter block; returns (meta_dict, body)"""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5:]

    meta = {}
    current_list_key = None
    for raw_line in fm_text.split("\n"):
        line = raw_line.rstrip()
        if not line:
            current_list_key = None
            continue
        # Nested list item
        if line.startswith("  - ") or line.startswith("- "):
            val = line.split("- ", 1)[1].strip().strip('"').strip("'")
            if current_list_key:
                meta.setdefault(current_list_key, []).append(val)
            continue
        # Top-level key
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            if val == "" or val == "[]":
                meta[key] = [] if val == "[]" else []
                current_list_key = key if val == "" else None
                continue
            # Inline list
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1]
                items = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
                meta[key] = items
            else:
                meta[key] = val.strip('"').strip("'")
            current_list_key = None
    return meta, body


def extract_summary(body: str, max_len: int = 200) -> str:
    """Pull first meaningful paragraph from body (skip headings/frontmatter residue)"""
    for chunk in body.split("\n\n"):
        text = chunk.strip()
        if not text:
            continue
        # Skip headings
        if text.startswith("#"):
            continue
        # Skip code fences
        if text.startswith("```"):
            continue
        # Strip markdown links/emphasis for cleaner summary
        text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", text)
        text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # Flatten newlines
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 20:
            continue
        if len(text) <= max_len:
            return text
        return text[:max_len].rstrip() + "…"
    return ""


def extract_wikilinks(body: str):
    """Yield canonical wikilink targets (without display text / anchors)"""
    for m in re.finditer(r"\[\[([^\]]+)\]\]", body):
        target = m.group(1).split("|")[0].split("#")[0].strip()
        yield target


def normalize_link(target: str, known_ids: set) -> str | None:
    """Resolve a wikilink target to a known node id (folder/stem form)"""
    # Strip prefix "wiki/"
    t = target
    if t.startswith("wiki/"):
        t = t[5:]
    # Direct match
    if t in known_ids:
        return t
    # Slash form — match by stem
    base = t.split("/")[-1]
    for kid in known_ids:
        if kid.endswith("/" + base):
            return kid
    return None


def main():
    if not VAULT.exists():
        print(f"❌ Vault not found: {VAULT}")
        sys.exit(1)

    nodes = []
    node_by_id = {}
    raw_bodies = {}  # id -> body text

    for sub in SUBFOLDERS:
        folder = VAULT / "wiki" / sub
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            stem = path.stem
            node_id = f"{sub}/{stem}"
            text = path.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text)
            title = meta.get("title", stem)
            layers = meta.get("layers", []) or []
            if isinstance(layers, str):
                layers = [layers]
            sources = meta.get("sources", []) or []
            if isinstance(sources, str):
                sources = [sources]

            node = {
                "id": node_id,
                "title": title,
                "type": meta.get("type", SUBFOLDER_TO_TYPE[sub]),
                "layers": layers,
                "jurisdiction": meta.get("jurisdiction", "universal"),
                "source_status": meta.get("source_status", "synthesis"),
                "summary": extract_summary(body),
            }
            if sources:
                node["sources"] = sources
            nodes.append(node)
            node_by_id[node_id] = node
            raw_bodies[node_id] = body

    # Build edges from wikilinks in body + frontmatter `related:` list
    known_ids = set(node_by_id.keys())
    edges_set = set()

    # We need full raw text (including frontmatter) to parse `related:`
    for sub in SUBFOLDERS:
        folder = VAULT / "wiki" / sub
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            stem = path.stem
            node_id = f"{sub}/{stem}"
            text = path.read_text(encoding="utf-8")
            # Wikilinks anywhere (body + related:)
            for link in extract_wikilinks(text):
                target = normalize_link(link, known_ids)
                if target and target != node_id:
                    edges_set.add((node_id, target))

    edges = [{"from": a, "to": b} for a, b in sorted(edges_set)]

    # ---------- kg-compact.json ----------
    kg = {
        "meta": {
            "version": "2.0",
            "domain": "Thai Residential Architecture",
            "layers": ["law", "eng", "design", "thai", "fengshui"],
            "node_count": len(nodes),
            "edge_count": len(edges),
            "usage": "Pass alongside project data / plan image to any AI for 5-layer analysis.",
        },
        "nodes": nodes,
        "edges": edges,
    }
    OUT_KG.write_text(json.dumps(kg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {OUT_KG.name}: {len(nodes)} nodes, {len(edges)} edges, {OUT_KG.stat().st_size // 1024} KB")

    # ---------- full-knowledge.md ----------
    # Pick pages: must-haves + top pages by edge degree (incoming + outgoing)
    in_degree = {}
    for e in edges:
        in_degree[e["to"]] = in_degree.get(e["to"], 0) + 1
        in_degree[e["from"]] = in_degree.get(e["from"], 0) + 1

    ranked = sorted(node_by_id.keys(), key=lambda x: (-in_degree.get(x, 0), x))
    picked = list(MUST_HAVE_IN_BUNDLE)
    for nid in ranked:
        if nid in picked:
            continue
        if len(picked) >= 32:
            break
        picked.append(nid)
    # Only keep nodes that actually exist
    picked = [p for p in picked if p in node_by_id]

    bundle = ["# สมองจำลองของสถาปนิก · Full Knowledge Bundle",
              f"\n_Auto-generated from wiki vault · {len(picked)} pages_\n\n---\n"]
    for nid in picked:
        node = node_by_id[nid]
        bundle.append(f"\n## {node['title']}")
        bundle.append(f"\n_id: `{nid}` · type: {node['type']} · layers: {', '.join(node['layers']) or '-'}_\n")
        bundle.append(raw_bodies[nid])
        bundle.append("\n\n---\n")
    OUT_FULL.write_text("\n".join(bundle), encoding="utf-8")
    print(f"✅ {OUT_FULL.name}: {len(picked)} pages bundled, {OUT_FULL.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
