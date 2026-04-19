"""Ingest approved contributions → wiki/ markdown pages

Reads all contribution JSONs in contributions/ folder, finds ones with
status=approved, and writes them as .md pages into the Obsidian vault's
wiki/ folder (pre-configured path). Also regenerates kg-compact.json +
full-knowledge.md.

Runs locally (not in Streamlit app) — operates on filesystem directly.

Usage:
  python scripts/ingest_contributions.py [--vault PATH] [--dry-run]

Default vault: ../NarongsakBIM (sibling of this repo).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
DEFAULT_VAULT = REPO_ROOT.parent / "NarongsakBIM"
CONTRIBS_DIR = REPO_ROOT / "contributions"

# Map contribution type → wiki subfolder
TYPE_TO_WIKI = {
    "correction": "concepts",    # corrections often live as concept updates
    "proposal": "concepts",      # new concept page
    "case": "syntheses",         # real-world case = synthesis
    "question": "syntheses",     # questions become Q&A syntheses
}


def slugify(title: str, max_len: int = 60) -> str:
    s = title.strip().lower()
    s = re.sub(r"[\s]+", "-", s)
    s = re.sub(r"[^\u0E00-\u0E7F\w\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:max_len] or "untitled"


def entry_to_markdown(entry: dict) -> str:
    """Convert contribution JSON → wiki-compatible .md with frontmatter"""
    date = (entry.get("timestamp") or datetime.now().isoformat())[:10]
    ai = entry.get("ai_suggestions") or {}
    layers = ai.get("layers") or []
    related_ai = [r["id"] for r in ai.get("related_pages", []) if isinstance(r, dict) and r.get("id")]
    related_all = list(dict.fromkeys((entry.get("related_pages") or []) + related_ai))
    keywords = ai.get("keywords") or []

    tags = [entry.get("category", ""), entry.get("type", ""), "community"]
    tags += keywords
    tags_str = ", ".join(t for t in tags if t)

    fm_lines = [
        "---",
        f'title: "{entry.get("title", "untitled")}"',
        "type: contribution",
        f"created: {date}",
        f"updated: {datetime.now().strftime('%Y-%m-%d')}",
        f"tags: [{tags_str}]",
    ]
    if layers:
        fm_lines.append(f"layers: [{', '.join(layers)}]")
    fm_lines.extend([
        f'author: "{entry.get("author") or "anonymous"}"',
        "source_status: community-approved",
        "status: approved",
        f'approved_at: "{entry.get("approved_at", "")}"',
    ])
    if related_all:
        fm_lines.append("related:")
        for r in related_all:
            fm_lines.append(f'  - "[[{r}]]"')
    fm_lines.append("---")
    fm = "\n".join(fm_lines) + "\n"

    body_parts = ["", entry.get("body", "")]
    if ai.get("short_summary"):
        body_parts += ["", f"> AI summary: {ai['short_summary']}"]
    if entry.get("approval_note"):
        body_parts += ["", f"> Admin note: {entry['approval_note']}"]
    if entry.get("edited_by_admin"):
        body_parts += ["", "_(edited by admin before approval)_"]
    if related_all:
        body_parts += ["", "## เกี่ยวข้องกับ", ""]
        body_parts += [f"- [[{r}]]" for r in related_all]

    return fm + "\n".join(body_parts) + "\n"


def find_approved_contributions() -> list[dict]:
    """Scan contributions/ for approved entries"""
    results = []
    if not CONTRIBS_DIR.exists():
        print(f"⚠ contributions dir not found: {CONTRIBS_DIR}")
        return results
    for p in CONTRIBS_DIR.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  skip {p.name}: {e}")
            continue
        if data.get("status") == "approved":
            results.append({"path": p, "entry": data})
    return results


def write_to_vault(entry: dict, vault: Path, dry_run: bool = False) -> Path | None:
    type_key = entry.get("type", "proposal")
    subfolder = TYPE_TO_WIKI.get(type_key, "concepts")
    title = entry.get("title", "untitled")
    eid = entry.get("id", "xxxxxxxx")
    filename = f"community-{slugify(title)}-{eid}.md"
    dest = vault / "wiki" / subfolder / filename
    content = entry_to_markdown(entry)

    if dry_run:
        print(f"  [dry-run] would write {dest}")
        print(f"  [dry-run] content preview: {content[:200]}...")
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    print(f"  ✓ wrote {dest}")
    return dest


def regen_kg(dry_run: bool = False):
    """Run build_kg.py to refresh kg-compact.json + full-knowledge.md"""
    build_script = REPO_ROOT / "scripts" / "build_kg.py"
    if not build_script.exists():
        print(f"⚠ build_kg.py not found · skipping KG regeneration")
        return
    if dry_run:
        print(f"  [dry-run] would run: python {build_script}")
        return
    print(f"🔨 running {build_script.name}...")
    try:
        subprocess.run([sys.executable, str(build_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"✗ build_kg failed: {e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vault", type=Path, default=DEFAULT_VAULT,
                   help=f"path to Obsidian vault (default: {DEFAULT_VAULT})")
    p.add_argument("--dry-run", action="store_true",
                   help="show what would be done without writing files")
    p.add_argument("--no-kg-regen", action="store_true",
                   help="skip kg-compact.json regeneration")
    args = p.parse_args()

    if not args.vault.exists():
        print(f"✗ vault not found: {args.vault}")
        print(f"  usage: {sys.argv[0]} --vault <path>")
        sys.exit(1)

    approved = find_approved_contributions()
    print(f"📥 found {len(approved)} approved contribution(s)")

    if not approved:
        print("nothing to ingest · done")
        return

    written = []
    for item in approved:
        entry = item["entry"]
        print(f"\n→ {entry.get('id', '?')} · {entry.get('type', '?')} · {entry.get('title', '')[:60]}")
        dest = write_to_vault(entry, args.vault, dry_run=args.dry_run)
        if dest:
            written.append(dest)

    print(f"\n✅ wrote {len(written)} file(s) to vault")

    if not args.no_kg_regen:
        print()
        regen_kg(dry_run=args.dry_run)

    if args.dry_run:
        print("\n(dry-run · nothing was actually written)")


if __name__ == "__main__":
    main()
