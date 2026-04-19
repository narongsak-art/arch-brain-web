"""Tier system · Free vs Pro · quota + feature gating

No real payment integration yet. Pro tier activation is via sidebar dev
toggle (Phase-0 placeholder). The value is in having the mechanism
wired up so we can plug in Stripe/PromptPay later.

Free:
  · 5 analyses / session
  · Markdown + JSON export
  · History · Contribute · Compare · Booking · Chat
  · Share link (self-hosted gzip · no cost to us)
  · Structured output
  · Basic CS support

Pro:
  · Unlimited analyses
  · All Free features +
  · PDF export (native Sarabun · ready to brand)
  · Image generation (uses own Gemini key · quota is user's)
  · Save/Load project JSON
  · Priority queue (placeholder)
  · Consultation discount 20% on booking
"""

import streamlit as st


TIERS = {
    "free": {
        "name": "ฟรี (Free)",
        "emoji": "🆓",
        "price_label": "0 บาท/เดือน",
        "limits": {
            "analyses_per_session": 5,
            "image_gen": False,
            "save_load": False,
            "pdf_export": False,
            "consultation_discount_pct": 0,
        },
        "features": [
            "✅ วิเคราะห์ 5 ครั้ง/session",
            "✅ อัปโหลดแปลน (ถ้ามี)",
            "✅ Markdown + JSON + Raw export",
            "✅ Share link (read-only URL)",
            "✅ Chat follow-up",
            "✅ เปรียบเทียบ 2 projects",
            "✅ ช่วยเติมเนื้อหา + AI organize",
            "✅ จองปรึกษา",
            "❌ PDF ระดับโปร (Sarabun)",
            "❌ Image generation (mockup)",
            "❌ Save/Load project JSON",
            "❌ ส่วนลด consultation",
        ],
    },
    "pro": {
        "name": "โปร (Pro)",
        "emoji": "💎",
        "price_label": "490 บาท/เดือน",
        "limits": {
            "analyses_per_session": None,
            "image_gen": True,
            "save_load": True,
            "pdf_export": True,
            "consultation_discount_pct": 20,
        },
        "features": [
            "✅ วิเคราะห์ **ไม่จำกัด**",
            "✅ ทุก feature ของ Free",
            "✅ **PDF ระดับโปร** (Sarabun font)",
            "✅ **Image generation** (mockup bird's-eye/perspective/plan/interior)",
            "✅ **Save/Load project JSON**",
            "✅ **ส่วนลด consultation 20%**",
            "✅ Priority support",
        ],
    },
}


# ============================================================================
# State
# ============================================================================

def _init():
    st.session_state.setdefault("tier", "free")
    st.session_state.setdefault("analyses_used", 0)


def get_tier() -> str:
    _init()
    return st.session_state["tier"]


def set_tier(tier: str):
    if tier in TIERS:
        st.session_state["tier"] = tier


def current_config() -> dict:
    return TIERS[get_tier()]


# ============================================================================
# Quota
# ============================================================================

def get_used() -> int:
    _init()
    return st.session_state["analyses_used"]


def increment_analysis():
    _init()
    st.session_state["analyses_used"] += 1


def reset_quota():
    st.session_state["analyses_used"] = 0


def get_remaining() -> int | None:
    """None = unlimited"""
    _init()
    limit = current_config()["limits"]["analyses_per_session"]
    if limit is None:
        return None
    return max(0, limit - get_used())


def check_quota() -> tuple[bool, str | None]:
    """Returns (can_analyze, error_message_if_blocked)"""
    remaining = get_remaining()
    if remaining is None:
        return True, None
    if remaining <= 0:
        limit = current_config()["limits"]["analyses_per_session"]
        return False, (
            f"ใช้ครบโควต้า {limit} ครั้งใน session นี้ · "
            "อัพเกรดเป็น Pro เพื่อวิเคราะห์ไม่จำกัด (ปุ่มในแท็บ Pricing)"
        )
    return True, None


# ============================================================================
# Feature gating
# ============================================================================

def can_use(feature_key: str) -> bool:
    return bool(current_config()["limits"].get(feature_key, False))


def feature_gate(feature_key: str, feature_name: str) -> bool:
    """True if user can use · else shows upgrade prompt and returns False"""
    if can_use(feature_key):
        return True
    st.warning(
        f"🔒 **{feature_name}** เป็น feature Pro · "
        "ดูแพ็กเกจและอัพเกรดที่แท็บ **💼 Pricing**"
    )
    return False


# ============================================================================
# UI · sidebar badge + pricing tab
# ============================================================================

def render_sidebar_badge():
    """Compact badge shown in sidebar"""
    cfg = current_config()
    remaining = get_remaining()
    used = get_used()

    st.markdown(f"**{cfg['emoji']} Tier: {cfg['name']}**")
    if remaining is None:
        st.caption("✨ การวิเคราะห์ไม่จำกัด")
    else:
        total = used + remaining
        st.caption(f"Session: **{used}/{total}** ครั้ง · เหลือ **{remaining}**")
        if total > 0:
            st.progress(min(1.0, used / total))

    if get_tier() == "free":
        st.caption("[ดูแพ็กเกจ Pro →](#pricing)")


def render_pricing_panel():
    """Full pricing comparison · used inside a tab"""
    st.markdown("### 💼 แพ็กเกจและราคา")
    st.caption("เลือกแพ็กเกจที่เหมาะกับการใช้งาน · ยกเลิกได้ทุกเมื่อ")

    free = TIERS["free"]
    pro = TIERS["pro"]
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"#### {free['emoji']} {free['name']}")
        st.markdown(f"**{free['price_label']}**")
        st.divider()
        for f in free["features"]:
            st.markdown(f)
        if get_tier() == "free":
            st.success("✓ คุณใช้ tier นี้อยู่")

    with c2:
        st.markdown(f"#### {pro['emoji']} {pro['name']}")
        st.markdown(f"**{pro['price_label']}**")
        st.divider()
        for f in pro["features"]:
            st.markdown(f)
        if get_tier() == "pro":
            st.success("✓ คุณใช้ tier นี้อยู่")
        else:
            if st.button(
                "🚀 อัพเกรดเป็น Pro (waitlist)",
                type="primary", use_container_width=True,
                key="tier_upgrade_cta",
            ):
                st.info(
                    "Pro tier กำลังเปิดเป็น **waitlist** · "
                    "กรอก booking form ที่แท็บ **📅 จองปรึกษา** "
                    "· ทีมจะติดต่อเพื่อ activate"
                )

    st.divider()
    _render_dev_toggle()

    # FAQ
    st.divider()
    st.markdown("### 🤔 คำถามที่พบบ่อย")
    with st.expander("Pro ต่างจาก Free ยังไง?"):
        st.markdown("""
- **Free** = ทดลองใช้ · เจ้าของบ้านทั่วไป
- **Pro** = ใช้งานจริง · สถาปนิก/developer ที่ทำหลายโปรเจค
  - Image generation ช่วย present ลูกค้า
  - PDF ระดับโปร ส่งให้ลูกค้าได้เลย
  - Save/Load เก็บโปรเจคไว้เปิดต่อ
  - ส่วนลด consultation 20%
""")
    with st.expander("ต้องมี Gemini API key เองอยู่แล้วไหม?"):
        st.markdown("""
**ใช่** · ทุก tier · คุณใช้ API key ของคุณเอง · quota ของคุณ · ไม่ผ่านเรา

ทำไม: privacy + cost transparency · คุณควบคุมค่าใช้จ่ายเอง
""")
    with st.expander("ยกเลิก Pro ได้ไหม?"):
        st.markdown("ได้ทุกเมื่อ · ไม่มี lock-in · กลับไปใช้ Free ทันที")


def _render_dev_toggle():
    """Dev-only: manually switch tier (removed before production real payment)"""
    with st.expander("🛠 Dev: toggle tier (ชั่วคราว)"):
        current = get_tier()
        new = st.radio(
            "Test tier",
            options=["free", "pro"],
            index=0 if current == "free" else 1,
            horizontal=True,
            key="tier_dev_toggle",
        )
        if new != current:
            set_tier(new)
            st.rerun()
        if st.button("🔄 Reset quota", key="tier_reset_quota"):
            reset_quota()
            st.rerun()


def apply_discount(amount: int) -> tuple[int, int]:
    """Returns (discount_pct, final_amount)"""
    pct = current_config()["limits"]["consultation_discount_pct"]
    if pct <= 0:
        return 0, amount
    discount = amount * pct // 100
    return pct, amount - discount
