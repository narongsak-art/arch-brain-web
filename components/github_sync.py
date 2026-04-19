"""GitHub sync · push contributions to the repo via GitHub API

Auth: app-level Personal Access Token stored in Streamlit secrets.
Users don't need their own GitHub account — the app itself is the
committer.

Setup (see contributions/README.md for a longer guide):
  .streamlit/secrets.toml:
    [github]
    token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxx"
    repo = "narongsak-art/arch-brain-web"  # owner/name
    branch = "main"                         # or "staging"
    committer_name = "arch-brain bot"       # optional
    committer_email = "bot@arch-brain.local" # optional

The PAT needs the `repo` (or just `public_repo` if repo is public)
scope. Create at: https://github.com/settings/tokens

Endpoint used: PUT /repos/{owner}/{repo}/contents/{path}
Docs: https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents
"""

import base64
import json
import re
from datetime import datetime

import requests
import streamlit as st


GITHUB_API = "https://api.github.com"


# ============================================================================
# Configuration helpers
# ============================================================================

def get_config() -> dict | None:
    """Read GitHub config from Streamlit secrets. Returns None if not configured."""
    try:
        cfg = st.secrets.get("github", None)
        if not cfg:
            return None
        # Minimal validation
        if not cfg.get("token") or not cfg.get("repo"):
            return None
        return {
            "token": cfg.get("token"),
            "repo": cfg.get("repo"),  # "owner/name"
            "branch": cfg.get("branch", "main"),
            "committer_name": cfg.get("committer_name", "arch-brain contributor"),
            "committer_email": cfg.get("committer_email", "bot@arch-brain.local"),
        }
    except Exception:
        return None


def is_configured() -> bool:
    return get_config() is not None


# ============================================================================
# Slug / path
# ============================================================================

def slugify(title: str, max_len: int = 50) -> str:
    """Thai-safe slug: keep alphanumerics + Thai · replace space+punctuation with hyphen"""
    s = title.strip().lower()
    s = re.sub(r"[\s]+", "-", s)
    # Keep Thai + ASCII alphanumerics + hyphens · drop other punctuation
    s = re.sub(r"[^\u0E00-\u0E7F\w\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:max_len] or "untitled"


def build_path(entry: dict) -> str:
    """Build contributions/{type}/{YYYY-MM-DD}_{slug}.json"""
    type_key = entry.get("type", "proposal")
    # Map type key → folder
    folder = {
        "correction": "corrections",
        "proposal": "proposals",
        "case": "cases",
        "question": "questions",
    }.get(type_key, "misc")
    date = entry.get("timestamp", datetime.now().isoformat())[:10]
    slug = slugify(entry.get("title", "untitled"))
    return f"contributions/{folder}/{date}_{slug}_{entry['id']}.json"


# ============================================================================
# API
# ============================================================================

def push_contribution(entry: dict, cfg: dict | None = None) -> tuple[bool, str]:
    """Create a commit with one contribution file.

    Returns (success, message). `message` is a human-readable success URL
    or the API error body.
    """
    cfg = cfg or get_config()
    if not cfg:
        return False, "ยังไม่ได้ตั้งค่า GitHub secrets · ดู contributions/README.md"

    path = build_path(entry)
    content_bytes = json.dumps(entry, ensure_ascii=False, indent=2).encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("ascii")

    url = f"{GITHUB_API}/repos/{cfg['repo']}/contents/{path}"
    headers = {
        "Authorization": f"token {cfg['token']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    author = entry.get("author") or "anonymous"
    type_meta = entry.get("type", "contribution")
    commit_message = f"community: {type_meta} · {entry.get('title', '')[:60]} (by {author})"

    body = {
        "message": commit_message,
        "content": content_b64,
        "branch": cfg["branch"],
        "committer": {
            "name": cfg["committer_name"],
            "email": cfg["committer_email"],
        },
    }

    try:
        r = requests.put(url, headers=headers, json=body, timeout=30)
    except requests.RequestException as e:
        return False, f"Network error: {e}"

    if r.status_code in (200, 201):
        data = r.json()
        commit_url = data.get("commit", {}).get("html_url", "")
        content_url = data.get("content", {}).get("html_url", "")
        return True, content_url or commit_url or "ok"

    # Handle common errors
    try:
        err_body = r.json()
        msg = err_body.get("message") or r.text
    except Exception:
        msg = r.text

    if r.status_code == 401:
        return False, "PAT ไม่ถูกต้อง หรือหมดอายุ · เช็คที่ github.com/settings/tokens"
    if r.status_code == 403:
        return False, f"PAT ไม่มีสิทธิ์เขียน repo นี้ · ต้องมี scope `repo` · {msg}"
    if r.status_code == 404:
        return False, f"ไม่พบ repo `{cfg['repo']}` หรือ branch · {msg}"
    if r.status_code == 422:
        return False, f"ไฟล์มีอยู่แล้ว หรือข้อมูลไม่ถูกต้อง · {msg}"

    return False, f"API {r.status_code}: {msg}"


# ============================================================================
# UI helpers
# ============================================================================

def render_setup_hint():
    """Shown when secrets aren't configured"""
    st.caption(
        "🔧 **GitHub push ยังไม่เปิด** · เพิ่ม secrets.toml:\n\n"
        "```toml\n[github]\ntoken = \"ghp_...\"\nrepo = \"owner/repo\"\nbranch = \"main\"\n```\n\n"
        "ดูรายละเอียดที่ `contributions/README.md`"
    )
