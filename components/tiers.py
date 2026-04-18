"""
Tiered access system · Free vs Pro

Free tier:
- 5 analyses per session
- Basic Markdown export
- Essential features

Pro tier (future paid):
- Unlimited analyses
- PDF export with branding
- Project save/load
- Priority support
- Consultation discount

No real payment yet · Pro is waitlist via booking form.
"""

from datetime import datetime
import streamlit as st


# ============================================================================
# Tier limits
# ============================================================================

TIERS = {
    "free": {
        "name": "ฟรี (Free)",
        "emoji": "🆓",
        "price": "0 บาท/เดือน",
        "limits": {
            "analyses_per_session": 5,
            "image_upload": True,
            "md_export": True,
            "pdf_export": False,
            "project_save": False,
            "history_count": 10,
            "annotation": True,
            "kg_explorer": True,
            "comparison": False,
            "chat": False,
            "consultation_discount": 0,
        },
        "features": [
            "✅ วิเคราะห์ 5 ครั้ง/session",
            "✅ อัปโหลดแปลน",
            "✅ ดาวน์โหลด Markdown",
            "✅ KG Explorer",
            "✅ Annotation drawer",
            "❌ PDF ระดับโปร",
            "❌ Save project",
            "❌ เปรียบเทียบ 2 แปลน",
            "❌ Chat follow-up",
        ],
    },
    "pro": {
        "name": "โปร (Pro)",
        "emoji": "💎",
        "price": "490 บาท/เดือน",
        "limits": {
            "analyses_per_session": None,  # unlimited
            "image_upload": True,
            "md_export": True,
            "pdf_export": True,
            "project_save": True,
            "history_count": 100,
            "annotation": True,
            "kg_explorer": True,
            "comparison": True,
            "chat": True,
            "consultation_discount": 20,  # 20%
        },
        "features": [
            "✅ วิเคราะห์ไม่จำกัด",
            "✅ PDF ระดับโปร · brandable",
            "✅ Save/Load projects (.json)",
            "✅ History 100 รายการ",
            "✅ Annotation + measure tools",
            "✅ KG Explorer full",
            "✅ เปรียบเทียบ 2+ แปลน",
            "✅ Chat follow-up Q&A",
            "✅ ส่วนลด consultation 20%",
            "✅ Priority support",
        ],
    },
}


# ============================================================================
# Session state helpers
# ============================================================================

def _init_state():
    if "user_tier" not in st.session_state:
        st.session_state["user_tier"] = "free"
    if "analysis_count" not in st.session_state:
        st.session_state["analysis_count"] = 0


def get_tier():
    _init_state()
    return st.session_state["user_tier"]


def set_tier(tier_id: str):
    if tier_id not in TIERS:
        return
    st.session_state["user_tier"] = tier_id


def tier_config(tier_id: str | None = None):
    _init_state()
    tier_id = tier_id or get_tier()
    return TIERS.get(tier_id, TIERS["free"])


def can_use(feature: str) -> bool:
    """Check if current tier allows feature"""
    cfg = tier_config()
    return cfg["limits"].get(feature, False)


def increment_analysis():
    _init_state()
    st.session_state["analysis_count"] += 1


def get_remaining_analyses() -> int | None:
    """Return remaining analyses this session · None = unlimited"""
    _init_state()
    cfg = tier_config()
    limit = cfg["limits"]["analyses_per_session"]
    if limit is None:
        return None
    used = st.session_state.get("analysis_count", 0)
    return max(0, limit - used)


def is_over_limit() -> bool:
    remaining = get_remaining_analyses()
    if remaining is None:
        return False
    return remaining == 0


# ============================================================================
# UI Components
# ============================================================================

def sidebar_tier_badge(container=None):
    """Show current tier + usage in sidebar"""
    c = container or st.sidebar
    _init_state()
    cfg = tier_config()

    c.markdown(f"### {cfg['emoji']} Tier: **{cfg['name']}**")

    remaining = get_remaining_analyses()
    if remaining is None:
        c.caption("✨ การวิเคราะห์ไม่จำกัด")
    else:
        used = st.session_state.get("analysis_count", 0)
        total = used + remaining
        c.caption(f"วันนี้: {used}/{total} · เหลือ **{remaining}** ครั้ง")
        c.progress(min(1.0, used / max(1, total)))

    if get_tier() == "free":
        c.caption("👉 [ดูแพ็กเกจ Pro](/Pricing)")


def upgrade_prompt(feature_name: str, container=None):
    """Show upgrade prompt when free user hits Pro feature"""
    c = container or st
    c.warning(
        f"🔒 **{feature_name}** เป็น feature Pro · "
        f"[อัพเกรดเลย](/Pricing) เพื่อปลดล็อก"
    )


def feature_gate(feature: str, feature_name: str, container=None):
    """Gate UI element · show upgrade if not allowed.

    Returns:
        bool · True if user can use feature
    """
    if can_use(feature):
        return True
    upgrade_prompt(feature_name, container=container)
    return False


def check_analysis_quota() -> tuple[bool, str | None]:
    """Returns (can_analyze, error_message)"""
    if is_over_limit():
        cfg = tier_config()
        limit = cfg["limits"]["analyses_per_session"]
        return (
            False,
            f"คุณใช้ครบโควต้าวันนี้ ({limit} ครั้ง) · "
            f"อัปเกรด Pro ไม่จำกัด · [ดูแพ็กเกจ](/Pricing)",
        )
    return (True, None)


def render_tier_comparison():
    """Render Free vs Pro comparison table"""
    col1, col2 = st.columns(2)

    free = TIERS["free"]
    pro = TIERS["pro"]

    with col1:
        st.markdown(f"### {free['emoji']} {free['name']}")
        st.markdown(f"**{free['price']}**")
        st.markdown("---")
        for f in free["features"]:
            st.markdown(f)

        if get_tier() == "free":
            st.success("✓ ตอนนี้คุณใช้ tier นี้")

    with col2:
        st.markdown(f"### {pro['emoji']} {pro['name']}")
        st.markdown(f"**{pro['price']}**")
        st.markdown("---")
        for f in pro["features"]:
            st.markdown(f)

        if get_tier() == "pro":
            st.success("✓ ตอนนี้คุณใช้ tier นี้")
        else:
            if st.button("🚀 อัพเกรดเป็น Pro", type="primary", use_container_width=True, key="upgrade_btn"):
                st.info(
                    "เรียน · ขณะนี้ Pro เปิดเป็น **waitlist** · "
                    "กรอก [Booking form](/Book_Consultation) · "
                    "ทีมจะติดต่อเพื่อ activate"
                )


# ============================================================================
# Dev helpers (for testing)
# ============================================================================

def _dev_toggle(container=None):
    """For development only · toggle tier manually"""
    c = container or st.sidebar
    with c.expander("🛠 Dev toggle tier", expanded=False):
        current = get_tier()
        new_tier = c.radio(
            "Test tier",
            options=["free", "pro"],
            index=0 if current == "free" else 1,
            horizontal=True,
            label_visibility="collapsed",
        )
        if new_tier != current:
            set_tier(new_tier)
            st.rerun()
