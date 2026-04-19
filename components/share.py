"""Share link · encode analysis into URL for read-only sharing

Flow:
1. User clicks "🔗 Create share link" after an analysis
2. We gzip + base64url-encode the payload (project + result + raw + provider)
3. URL: https://arch-brain-narongsak.streamlit.app/?share=<encoded>
4. Recipient opens URL → app detects ?share= param → renders read-only view

No backend needed · URL is self-contained (gzipped, usually 1-3 KB).
Large payloads fall back to download-as-.json.
"""

import base64
import gzip
import json
from datetime import datetime

import streamlit as st

from components import analysis


SCHEMA_VERSION = "1.0"
DEFAULT_BASE_URL = "https://arch-brain-narongsak.streamlit.app"


# ============================================================================
# Encode / Decode
# ============================================================================

def encode_payload(project_data: dict, result: dict | None,
                   raw_text: str | None, provider: str) -> str:
    payload = {
        "v": SCHEMA_VERSION,
        "pd": project_data,
        "r": result,
        "raw": raw_text if not result else None,  # skip raw if structured result present
        "p": provider,
        "t": datetime.now().isoformat(timespec="seconds"),
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def decode_payload(encoded: str) -> dict | None:
    """Returns decoded dict or None if malformed"""
    try:
        pad = "=" * (4 - len(encoded) % 4) if len(encoded) % 4 else ""
        compressed = base64.urlsafe_b64decode(encoded + pad)
        raw = gzip.decompress(compressed)
        data = json.loads(raw.decode("utf-8"))
        # Normalize back to full field names
        return {
            "version": data.get("v", "unknown"),
            "project_data": data.get("pd", {}),
            "result": data.get("r"),
            "raw_text": data.get("raw"),
            "provider": data.get("p", "ai"),
            "timestamp": data.get("t", ""),
        }
    except Exception:
        return None


def build_url(encoded: str, base: str | None = None) -> str:
    base = base or DEFAULT_BASE_URL
    return f"{base}/?share={encoded}"


# ============================================================================
# Creator UI (shown after an analysis completes)
# ============================================================================

def render_share_panel(project_data: dict, result: dict | None,
                       raw_text: str | None, provider: str):
    """Rendered in the result area · generates + displays shareable URL"""
    st.subheader("🔗 แชร์ลิงก์ให้ลูกค้า (read-only)")
    st.caption(
        "สร้าง URL ที่ฝังผลวิเคราะห์ทั้งหมด · ผู้รับเปิดได้โดยไม่ต้อง login · "
        "ไม่มี backend · URL ใช้งานได้ตลอดไป"
    )

    try:
        encoded = encode_payload(project_data, result, raw_text, provider)
    except Exception as e:
        st.error(f"สร้างลิงก์ไม่สำเร็จ: {e}")
        return

    url = build_url(encoded)
    kb = len(encoded) / 1024
    url_len = len(url)

    # Warn if URL approaching browser limits
    if url_len > 8000:
        st.error(
            f"⚠ URL ยาวเกินขีด browser ({url_len:,} chars · max ~8,000) · "
            "ใช้ download `.json` ด้านล่างแทน · ส่งเป็นไฟล์แนบ · "
            "ผู้รับเปิดแล้ว drag เข้าเว็ปได้"
        )
    elif url_len > 4000:
        st.warning(
            f"📏 URL ค่อนข้างยาว ({url_len:,} chars · {kb:.1f} KB) · "
            "บางเบราว์เซอร์อาจตัดสั้น · ถ้าเจอปัญหาใช้ `.json` แทน"
        )
    else:
        st.caption(f"📏 URL size: {url_len:,} chars · {kb:.1f} KB")

    # The URL itself — text_area makes it easy to select+copy
    st.text_area("🔗 URL (copy ตรงนี้)", value=url, height=90, key="share_url_box")

    # Download fallback: plain .json · user attaches to email
    plain = {
        "schema": "arch-brain-share",
        "version": SCHEMA_VERSION,
        "project_data": project_data,
        "result": result,
        "raw_text": raw_text,
        "provider": provider,
        "timestamp": datetime.now().isoformat(),
    }
    name = (project_data.get("name") or "share").replace("/", "-")
    st.download_button(
        "📥 Download .json (fallback)",
        data=json.dumps(plain, ensure_ascii=False, indent=2),
        file_name=f"share-{name}.json",
        mime="application/json",
        use_container_width=True,
        key="share_json_dl",
    )


# ============================================================================
# Viewer UI (rendered when ?share= query param is present)
# ============================================================================

def is_share_mode() -> bool:
    """True when the app was opened with a ?share=... parameter"""
    try:
        return bool(st.query_params.get("share"))
    except Exception:
        return False


def render_view():
    """Full-page read-only view · replaces the normal app when ?share= is set"""
    encoded = st.query_params.get("share", "")
    payload = decode_payload(encoded) if encoded else None

    # Header band
    st.markdown(
        """
        <div class="ab-hero">
          <h1>🔗 ผลวิเคราะห์ (view-only)</h1>
          <p>วิเคราะห์ด้วย AI + Knowledge Graph 5 ชั้น · สมองจำลองของสถาปนิก</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not payload:
        st.error(
            "❌ ลิงก์เสียหายหรือไม่ถูกต้อง · ขอลิงก์ใหม่จากผู้ส่ง · "
            "หรือใช้ไฟล์ `.json` แบบ upload ด้านล่าง"
        )
        _render_upload_fallback()
        return

    pd = payload.get("project_data") or {}
    result = payload.get("result")
    raw = payload.get("raw_text")
    provider = payload.get("provider", "ai")
    ts = payload.get("timestamp", "")

    # Project summary card
    st.markdown(f"## 🏠 {pd.get('name', '-')}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ที่ดิน", f"{pd.get('land_w', '-')}×{pd.get('land_d', '-')} ม.")
    c2.metric("จังหวัด", pd.get("province", "-"))
    c3.metric("สีผังเมือง", pd.get("zone", "-"))
    c4.metric("งบประมาณ", f"{pd.get('budget', '-')} ลบ.")
    if ts:
        try:
            dt = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
        except Exception:
            dt = ts
        st.caption(f"🕐 วิเคราะห์เมื่อ: {dt} · Provider: {provider.title()}")

    st.divider()

    # Render the analysis
    if result:
        analysis.render(result)
    elif raw:
        st.markdown(raw)
    else:
        st.warning("ไม่พบเนื้อหาในลิงก์")

    # Project brief expandable
    st.divider()
    with st.expander("📋 ข้อมูลโครงการที่ใช้วิเคราะห์"):
        st.json(pd)

    # Disclaimer + CTA
    st.divider()
    st.warning(
        "**⚠ Disclaimer:** ผลเป็นการประเมินเบื้องต้น · ไม่แทนสถาปนิก/วิศวกรใบอนุญาต · "
        "การขออนุญาตก่อสร้างต้องมีลายเซ็นผู้ประกอบวิชาชีพ "
        "(พรบ.ควบคุมอาคาร 2522 มาตรา 49 ทวิ)"
    )

    if st.button("🏠 วิเคราะห์โครงการของคุณเอง", type="primary", use_container_width=True):
        # Drop the ?share= param → back to normal app
        st.query_params.clear()
        st.rerun()


def _render_upload_fallback():
    """Alt loader: user uploads a .json share file if URL was broken/too long"""
    st.markdown("---")
    st.markdown("### 📥 หรือ upload ไฟล์ .json ที่ได้รับ")
    uploaded = st.file_uploader("เลือกไฟล์ .json", type=["json"], key="share_view_upload")
    if uploaded is None:
        return
    try:
        data = json.loads(uploaded.read().decode("utf-8"))
        # Normalize
        payload = {
            "project_data": data.get("project_data") or {},
            "result": data.get("result"),
            "raw_text": data.get("raw_text"),
            "provider": data.get("provider", "ai"),
            "timestamp": data.get("timestamp", ""),
        }
        st.session_state["_share_payload_override"] = payload
        st.rerun()
    except Exception as e:
        st.error(f"อ่านไฟล์ไม่สำเร็จ: {e}")
