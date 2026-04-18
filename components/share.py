"""Share · generate read-only share links for analyses

Encoding strategy: gzip + base64url on the JSON payload.
No backend required — receiver's browser reconstructs the analysis from the URL.

Payload format:
{
  "v": "1.0",
  "project_data": {...},
  "structured": {...},
  "analysis": "raw markdown (optional fallback)",
  "provider": "gemini|claude",
  "timestamp": "..."
}
"""

import base64
import gzip
import json
from datetime import datetime

import streamlit as st


SCHEMA_VERSION = "1.0"

# Streamlit Cloud hosts under this pattern; local uses localhost
DEFAULT_BASE_URL = "https://arch-brain-narongsak.streamlit.app"


# ============================================================================
# Encode / Decode
# ============================================================================

def encode_payload(project_data: dict, structured: dict | None, raw_analysis: str, provider: str) -> str:
    """Compress + encode analysis payload to URL-safe base64"""
    payload = {
        "v": SCHEMA_VERSION,
        "project_data": project_data,
        "structured": structured,
        "analysis": raw_analysis if not structured else None,  # Skip raw if we have structured
        "provider": provider,
        "timestamp": datetime.now().isoformat(),
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def decode_payload(encoded: str) -> dict | None:
    """Decode URL-safe base64 + gzip back to payload dict"""
    try:
        # Restore padding
        pad = "=" * (4 - len(encoded) % 4) if len(encoded) % 4 else ""
        compressed = base64.urlsafe_b64decode(encoded + pad)
        raw = gzip.decompress(compressed)
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


# ============================================================================
# UI helpers
# ============================================================================

def build_share_url(payload_b64: str, base_url: str | None = None) -> str:
    base = base_url or st.session_state.get("share_base_url", DEFAULT_BASE_URL)
    return f"{base}/View?data={payload_b64}"


def render_share_button(project_data: dict, structured: dict | None, analysis: str, provider: str):
    """Render a compact 'Create share link' UI panel"""
    with st.expander("🔗 สร้างลิงก์แชร์ (read-only)", expanded=False):
        st.caption(
            "สร้าง URL ที่ฝังผลวิเคราะห์ทั้งหมด · แชร์ให้ลูกค้าดูผ่านเบราว์เซอร์ได้เลย "
            "(ไม่ต้อง login · ไม่มี backend)"
        )

        try:
            encoded = encode_payload(project_data, structured, analysis, provider)
        except Exception as e:
            st.error(f"สร้างลิงก์ไม่สำเร็จ: {e}")
            return

        url = build_share_url(encoded)
        size_kb = len(encoded) / 1024

        if size_kb > 6:
            st.warning(
                f"⚠ ลิงก์ใหญ่มาก ({size_kb:.1f} KB · {len(url):,} chars) · "
                "บางเบราว์เซอร์จำกัด URL ที่ ~2,000-8,000 chars · "
                "ใช้ `ดาวน์โหลด .json` แทนได้ (ผู้รับเปิดไฟล์แล้ว drag เข้า View page)"
            )
        elif size_kb > 2:
            st.caption(f"📏 ลิงก์: {size_kb:.1f} KB · {len(url):,} chars")

        st.text_area("🔗 Share URL", value=url, height=80, key="share_url_display")

        col1, col2 = st.columns(2)
        with col1:
            st.code(url, language=None)
        with col2:
            # Downloadable JSON as fallback for oversized URLs
            json_payload = {
                "v": SCHEMA_VERSION,
                "project_data": project_data,
                "structured": structured,
                "analysis": analysis,
                "provider": provider,
                "timestamp": datetime.now().isoformat(),
            }
            st.download_button(
                "📥 ดาวน์โหลด .json (fallback)",
                data=json.dumps(json_payload, ensure_ascii=False, indent=2),
                file_name=f"share-{project_data.get('name','untitled')}.json",
                mime="application/json",
                use_container_width=True,
            )


def upload_share_file():
    """Allow users to load a share payload from a .json file (when URL too big)"""
    uploaded = st.file_uploader(
        "หรือ upload ไฟล์ .json ที่ได้รับ",
        type=["json"],
        key="share_upload",
    )
    if uploaded is not None:
        try:
            data = json.loads(uploaded.read().decode("utf-8"))
            return data
        except Exception as e:
            st.error(f"อ่านไฟล์ไม่สำเร็จ: {e}")
    return None
