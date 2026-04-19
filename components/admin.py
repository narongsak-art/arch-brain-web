"""Admin moderation · review queue for contributions pushed to GitHub

Access: open app with `?admin=<token>` where token matches
`st.secrets["admin"]["token"]`. Token is checked constant-time.

What admins can do:
- List all contributions from GitHub's contributions/ folder
- View each entry's content + AI suggestions + metadata
- ✅ Approve (status → approved · reason optional)
- ❌ Reject (status → rejected · reason REQUIRED)
- ✏ Edit title/body/category inline before approving

Approved entries stay in contributions/ with updated status. A separate
ingest step (Phase 5) reads approved entries and writes .md files into
wiki/ on the Obsidian vault.

Setup in .streamlit/secrets.toml:
  [admin]
  token = "pick-a-long-random-string-32chars-plus"

Then open: https://your-app.streamlit.app/?admin=<token>
"""

import base64
import hmac
import json
from datetime import datetime

import requests
import streamlit as st

from components import github_sync


# ============================================================================
# Auth
# ============================================================================

def _get_admin_token() -> str | None:
    try:
        return st.secrets.get("admin", {}).get("token")
    except Exception:
        return None


def is_admin_mode() -> bool:
    """True if ?admin=... matches secrets · False otherwise (incl. no secrets set)"""
    try:
        provided = st.query_params.get("admin")
    except Exception:
        return False
    if not provided:
        return False
    expected = _get_admin_token()
    if not expected:
        return False
    # constant-time compare to avoid timing leaks
    return hmac.compare_digest(str(provided), str(expected))


# ============================================================================
# GitHub reads
# ============================================================================

_FOLDERS = ["corrections", "proposals", "cases", "questions"]


def _list_files(folder: str, cfg: dict) -> list[dict]:
    """GET /repos/{owner}/{repo}/contents/contributions/{folder}"""
    url = f"{github_sync.GITHUB_API}/repos/{cfg['repo']}/contents/contributions/{folder}"
    headers = {
        "Authorization": f"token {cfg['token']}",
        "Accept": "application/vnd.github+json",
    }
    try:
        r = requests.get(url, headers=headers, params={"ref": cfg["branch"]}, timeout=30)
    except requests.RequestException:
        return []
    if r.status_code == 404:
        return []  # folder doesn't exist yet
    if r.status_code != 200:
        return []
    return [item for item in r.json() if item.get("type") == "file"]


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_file_content(path: str, repo: str, branch: str, token: str) -> tuple[str | None, str | None]:
    """GET content + sha of a file. Returns (json_content, sha) or (None, None)"""
    url = f"{github_sync.GITHUB_API}/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    try:
        r = requests.get(url, headers=headers, params={"ref": branch}, timeout=30)
    except requests.RequestException:
        return None, None
    if r.status_code != 200:
        return None, None
    data = r.json()
    sha = data.get("sha")
    try:
        raw = base64.b64decode(data["content"]).decode("utf-8")
    except Exception:
        return None, sha
    return raw, sha


def _update_file(path: str, new_content: dict, sha: str, cfg: dict, commit_msg: str) -> tuple[bool, str]:
    """PUT an updated file back · returns (ok, msg_or_url)"""
    url = f"{github_sync.GITHUB_API}/repos/{cfg['repo']}/contents/{path}"
    headers = {
        "Authorization": f"token {cfg['token']}",
        "Accept": "application/vnd.github+json",
    }
    content_b64 = base64.b64encode(
        json.dumps(new_content, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("ascii")
    body = {
        "message": commit_msg,
        "content": content_b64,
        "sha": sha,
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
        commit_url = r.json().get("commit", {}).get("html_url", "")
        return True, commit_url
    try:
        msg = r.json().get("message", r.text)
    except Exception:
        msg = r.text
    return False, f"API {r.status_code}: {msg}"


# ============================================================================
# Operations
# ============================================================================

def fetch_all_pending(cfg: dict) -> list[dict]:
    """Return list of {path, sha, entry} for all contributions in repo"""
    out: list[dict] = []
    for folder in _FOLDERS:
        for item in _list_files(folder, cfg):
            path = item.get("path")
            if not path or not path.endswith(".json"):
                continue
            raw, sha = _fetch_file_content(path, cfg["repo"], cfg["branch"], cfg["token"])
            if raw is None:
                continue
            try:
                entry = json.loads(raw)
            except Exception:
                continue
            out.append({"path": path, "sha": sha, "entry": entry})
    # Sort: pending first, then submitted, then approved/rejected. Within group, newest first.
    status_order = {"pending": 0, "submitted": 1, "approved": 2, "rejected": 3}
    out.sort(key=lambda x: (
        status_order.get(x["entry"].get("status", "pending"), 99),
        -int(datetime.fromisoformat(
            x["entry"].get("timestamp", "2000-01-01T00:00:00")
        ).timestamp()),
    ))
    return out


def approve(entry: dict, path: str, sha: str, cfg: dict, reason: str = "") -> tuple[bool, str]:
    updated = dict(entry)
    updated["status"] = "approved"
    updated["approved_at"] = datetime.now().isoformat()
    if reason:
        updated["approval_note"] = reason
    msg = f"moderate: approve {entry.get('id', '')} · {entry.get('title', '')[:50]}"
    return _update_file(path, updated, sha, cfg, msg)


def reject(entry: dict, path: str, sha: str, cfg: dict, reason: str) -> tuple[bool, str]:
    updated = dict(entry)
    updated["status"] = "rejected"
    updated["rejected_at"] = datetime.now().isoformat()
    updated["rejection_reason"] = reason or "(no reason given)"
    msg = f"moderate: reject {entry.get('id', '')} · {reason[:40]}"
    return _update_file(path, updated, sha, cfg, msg)


def edit_and_approve(
    entry: dict, path: str, sha: str, cfg: dict,
    new_title: str, new_body: str, new_category: str, reason: str = ""
) -> tuple[bool, str]:
    updated = dict(entry)
    updated["title"] = new_title.strip() or entry.get("title", "")
    updated["body"] = new_body.strip() or entry.get("body", "")
    updated["category"] = new_category or entry.get("category", "")
    updated["status"] = "approved"
    updated["approved_at"] = datetime.now().isoformat()
    updated["edited_by_admin"] = True
    if reason:
        updated["approval_note"] = reason
    msg = f"moderate: edit+approve {entry.get('id', '')} · {updated['title'][:50]}"
    return _update_file(path, updated, sha, cfg, msg)


# ============================================================================
# UI
# ============================================================================

STATUS_BADGES = {
    "pending": "🟡 pending",
    "submitted": "🟠 submitted",
    "approved": "🟢 approved",
    "rejected": "🔴 rejected",
}

# Re-use category + type metadata from contribute module
try:
    from components.contribute import CATEGORIES, TYPES
except Exception:
    CATEGORIES, TYPES = {}, {}


def render_panel():
    """Full-page admin review view · replaces normal app when in admin mode"""
    st.markdown(
        """
        <div class="ab-hero" style="background: linear-gradient(135deg, #ef4444, #f59e0b);">
          <h1>👮 Admin Moderation</h1>
          <p>ตรวจ contributions จาก GitHub · approve / reject / edit</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cfg = github_sync.get_config()
    if not cfg:
        st.error("❌ GitHub sync ยังไม่ได้ตั้งค่า · ตั้ง `[github]` ใน secrets.toml ก่อน")
        return

    # Refresh button (bust cache)
    c_head, c_refresh = st.columns([4, 1])
    c_head.caption(f"Repo: `{cfg['repo']}` · Branch: `{cfg['branch']}`")
    if c_refresh.button("🔄 Refresh", use_container_width=True, key="admin_refresh"):
        _fetch_file_content.clear()
        st.rerun()

    # Fetch all
    with st.spinner("🌐 โหลด contributions..."):
        items = fetch_all_pending(cfg)

    if not items:
        st.info("📭 ยังไม่มี contributions ใน GitHub · กลับมาใหม่เมื่อมีผู้ส่ง")
        _render_exit_button()
        return

    # Summary metrics
    by_status = {"pending": 0, "submitted": 0, "approved": 0, "rejected": 0}
    for it in items:
        s = it["entry"].get("status", "pending")
        by_status[s] = by_status.get(s, 0) + 1

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric("รวม", len(items))
    mc2.metric("🟡 pending", by_status.get("pending", 0))
    mc3.metric("🟠 submitted", by_status.get("submitted", 0))
    mc4.metric("🟢 approved", by_status.get("approved", 0))
    mc5.metric("🔴 rejected", by_status.get("rejected", 0))

    # Filter
    status_filter = st.multiselect(
        "กรองตาม status",
        options=["pending", "submitted", "approved", "rejected"],
        default=["pending", "submitted"],
        format_func=lambda s: STATUS_BADGES.get(s, s),
        key="admin_status_filter",
    )

    filtered = [it for it in items if it["entry"].get("status", "pending") in status_filter]
    st.markdown(f"### 📋 Queue · {len(filtered)}/{len(items)} รายการ")

    for it in filtered:
        _render_entry(it, cfg)

    st.divider()
    _render_exit_button()


def _render_entry(item: dict, cfg: dict):
    entry = item["entry"]
    path = item["path"]
    sha = item["sha"]

    status = entry.get("status", "pending")
    type_key = entry.get("type", "proposal")
    cat_key = entry.get("category", "")
    t_emoji, t_label, _ = TYPES.get(type_key, ("❓", type_key, ""))
    c_emoji, c_label, _ = CATEGORIES.get(cat_key, ("", cat_key, ""))

    header = (
        f"{STATUS_BADGES.get(status, status)} · {t_emoji} · "
        f"{c_emoji} · **{entry.get('title', '-')}** · _{entry.get('author', 'anonymous')}_"
    )

    with st.expander(header, expanded=(status in ("pending", "submitted"))):
        # Metadata row
        meta_a, meta_b, meta_c = st.columns(3)
        meta_a.caption(f"id `{entry.get('id', '')}`")
        meta_b.caption(f"type: {t_label}")
        meta_c.caption(f"category: {c_label}")
        st.caption(f"path: `{path}`")

        # Content preview
        st.markdown("**เนื้อหา:**")
        st.markdown(entry.get("body", "(empty)"))

        # AI suggestions if present
        ai = entry.get("ai_suggestions") or {}
        if ai:
            with st.expander("🧠 AI suggestions"):
                if ai.get("layers"):
                    st.caption(f"Layers: {', '.join(ai['layers'])}")
                if ai.get("keywords"):
                    st.caption(f"Keywords: {', '.join(ai['keywords'])}")
                if ai.get("short_summary"):
                    st.info(ai["short_summary"])

        # Current admin notes (if any)
        if entry.get("approval_note"):
            st.success(f"🟢 Approved note: {entry['approval_note']}")
        if entry.get("rejection_reason"):
            st.error(f"🔴 Rejected: {entry['rejection_reason']}")

        # Actions (only show for actionable statuses)
        if status in ("pending", "submitted"):
            st.divider()
            _render_action_tabs(entry, path, sha, cfg)


def _render_action_tabs(entry: dict, path: str, sha: str, cfg: dict):
    tab_approve, tab_reject, tab_edit = st.tabs(["✅ Approve", "❌ Reject", "✏ Edit + Approve"])

    with tab_approve:
        note = st.text_input(
            "Note (optional)", key=f"approve_note_{entry['id']}",
            placeholder="เช่น: ข้อมูลครบ · link ถูก · merge ได้เลย",
        )
        if st.button("✅ Approve", type="primary", use_container_width=True, key=f"btn_approve_{entry['id']}"):
            with st.spinner("committing..."):
                ok, msg = approve(entry, path, sha, cfg, note)
            if ok:
                st.success(f"✅ approved · [commit]({msg})")
                _fetch_file_content.clear()
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    with tab_reject:
        reason = st.text_area(
            "เหตุผล (required)", key=f"reject_reason_{entry['id']}",
            placeholder="เช่น: ข้อมูลไม่ cite · contradicts พรบ. · duplicate ของหน้า X",
            height=80,
        )
        if st.button(
            "❌ Reject", use_container_width=True, key=f"btn_reject_{entry['id']}",
            disabled=not reason.strip(),
        ):
            with st.spinner("committing..."):
                ok, msg = reject(entry, path, sha, cfg, reason.strip())
            if ok:
                st.success(f"🔴 rejected · [commit]({msg})")
                _fetch_file_content.clear()
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    with tab_edit:
        new_title = st.text_input(
            "Title", value=entry.get("title", ""), key=f"edit_title_{entry['id']}",
            max_chars=120,
        )
        new_body = st.text_area(
            "Body", value=entry.get("body", ""), key=f"edit_body_{entry['id']}",
            height=220,
        )
        # Category picker (same set as contribute module)
        cat_keys = list(CATEGORIES.keys()) if CATEGORIES else [entry.get("category", "design")]
        try:
            cat_index = cat_keys.index(entry.get("category", "design"))
        except ValueError:
            cat_index = 0
        new_cat = st.selectbox(
            "Category", options=cat_keys,
            format_func=lambda k: f"{CATEGORIES[k][0]} {CATEGORIES[k][1]}" if k in CATEGORIES else k,
            index=cat_index, key=f"edit_cat_{entry['id']}",
        )
        edit_note = st.text_input(
            "Note", key=f"edit_note_{entry['id']}",
            placeholder="เช่น: แก้ typo + เพิ่ม citation",
        )
        if st.button(
            "✏ Save + Approve", type="primary",
            use_container_width=True, key=f"btn_edit_{entry['id']}",
        ):
            with st.spinner("committing..."):
                ok, msg = edit_and_approve(
                    entry, path, sha, cfg,
                    new_title, new_body, new_cat, edit_note,
                )
            if ok:
                st.success(f"✅ edited + approved · [commit]({msg})")
                _fetch_file_content.clear()
                st.rerun()
            else:
                st.error(f"❌ {msg}")


def _render_exit_button():
    if st.button("🚪 Exit admin mode", use_container_width=True, key="admin_exit"):
        st.query_params.clear()
        st.rerun()
