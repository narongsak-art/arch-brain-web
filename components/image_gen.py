"""Image generation · Gemini Flash Image (architectural mockups from brief)

Generates visualization images from project_data:
- 🦅 Bird's-eye: isometric 45° showing whole plot + house + landscape
- 🏠 Perspective: 3/4 facade + entrance at eye level
- 📐 Floor plan: hand-drawn top-down sketch
- 🛋 Interior mood: main living space atmosphere

Uses Google's image-capable Gemini (needs API key with image gen enabled).
Falls back gracefully if model unavailable.
"""

import base64
from typing import Literal

import requests
import streamlit as st


# ============================================================================
# Models + prompt templates
# ============================================================================

IMAGE_MODELS = {
    "gemini-2.5-flash-image": "🖼 Gemini 2.5 Flash Image (ล่าสุด)",
    "gemini-2.5-flash-image-preview": "🧪 Gemini 2.5 Flash Image (preview)",
    "gemini-2.0-flash-preview-image-generation": "📦 Gemini 2.0 Image (backup)",
}
DEFAULT_MODEL = "gemini-2.5-flash-image"

VIEW_TYPES = {
    "birdseye": {
        "label": "🦅 Bird's-eye view",
        "desc": "มุมสูง · เห็นทั้งบ้าน + สวน + ที่ดิน",
        "style": (
            "Architectural bird's-eye rendering, isometric 45-degree angle, "
            "showing the full plot with house, landscape, driveway, garden. "
            "Professional architectural visualization, soft natural daylight, "
            "photorealistic materials, clean modern style."
        ),
    },
    "perspective": {
        "label": "🏠 Perspective (3/4)",
        "desc": "มุม 3/4 · เห็น facade + ทางเข้า",
        "style": (
            "Architectural 3/4 perspective rendering at eye level, "
            "showing the main facade and entrance, with landscape in foreground. "
            "Professional photorealistic style, warm daylight, clear sky."
        ),
    },
    "floorplan": {
        "label": "📐 Floor plan sketch",
        "desc": "แปลนวาดมือ · top-down",
        "style": (
            "Architectural floor plan sketch, top-down view, hand-drawn style, "
            "clean linework with room labels, dimensional annotations, "
            "north arrow, scale bar, minimal color."
        ),
    },
    "interior": {
        "label": "🛋 Interior mood",
        "desc": "บรรยากาศภายใน",
        "style": (
            "Interior architectural rendering of the main living space, "
            "natural daylight through large windows, warm modern Thai tropical style, "
            "photorealistic, soft ambient lighting."
        ),
    },
}


def build_prompt(project_data: dict, view_type: str, extra: str = "") -> str:
    """Build a natural-language prompt for image gen from project brief"""
    vt = VIEW_TYPES.get(view_type, VIEW_TYPES["birdseye"])

    parts = []
    parts.append(f"A {project_data.get('floors', '2')}-story Thai residential house.")
    parts.append(
        f"Plot {project_data.get('land_w', 15)}×{project_data.get('land_d', 20)} meters "
        f"({project_data.get('land_area', 300):.0f} sqm)."
    )
    parts.append(
        f"{project_data.get('bedrooms', '3')} bedrooms for a family of "
        f"{project_data.get('family_size', 4)}."
    )
    parts.append(
        f"Located in {project_data.get('province', 'Bangkok')}, "
        f"zoning {project_data.get('zone', 'residential')}."
    )
    if project_data.get("has_elderly") == "ใช่":
        parts.append("Accessible design for elderly (ground-floor bedroom, ramps).")
    if project_data.get("fengshui") in ("มาก", "ปานกลาง"):
        parts.append("Incorporates Thai cultural elements (prayer room, auspicious orientation).")
    special = (project_data.get("special") or "").strip()
    if special:
        parts.append(f"Special requirements: {special}.")
    parts.append(
        "Tropical climate design: wide eaves, ventilated openings, "
        "shaded veranda, appropriate for Thailand's hot-humid climate."
    )

    brief = " ".join(parts)
    tail = f" Additional notes: {extra.strip()}." if extra.strip() else ""
    return f"{vt['style']}\n\nProject brief:\n{brief}{tail}"


# ============================================================================
# API
# ============================================================================

def call_api(api_key: str, prompt: str, model: str) -> tuple[bytes | None, str | None]:
    """Returns (image_bytes, error_msg). Never raises."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }
    try:
        r = requests.post(url, json=payload, timeout=180)
    except requests.RequestException as e:
        return None, f"Network error: {e}"

    if r.status_code != 200:
        return None, f"API {r.status_code}: {r.text[:300]}"

    try:
        data = r.json()
    except Exception as e:
        return None, f"Invalid JSON response: {e}"

    for cand in data.get("candidates") or []:
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inline_data") or part.get("inlineData")
            if inline and inline.get("data"):
                try:
                    return base64.b64decode(inline["data"]), None
                except Exception as e:
                    return None, f"decode error: {e}"

    return None, "No image in response (model may have refused or returned text only)"


# ============================================================================
# Session gallery
# ============================================================================

def _gallery() -> list:
    return st.session_state.setdefault("generated_images", [])


def _save(img_bytes: bytes, view_type: str, model: str, prompt: str):
    _gallery().insert(0, {
        "bytes": img_bytes,
        "view_type": view_type,
        "model": model,
        "prompt": prompt,
    })
    # Keep only last 6 to avoid session bloat
    st.session_state["generated_images"] = _gallery()[:6]


# ============================================================================
# UI panel
# ============================================================================

def render_panel(project_data: dict | None, api_key: str, provider: str):
    """Main image-gen tab · runs on user's Gemini API key"""
    st.markdown("### 🎨 สร้างภาพ mockup จาก brief")
    st.caption(
        "ใช้ AI สร้างภาพ visualization จากข้อมูลโครงการ · "
        "ใช้ quota Gemini ของคุณเอง (ภาพละ ~10-30 วินาที)"
    )

    if provider != "gemini":
        st.warning("Image generation ใช้ Gemini API เท่านั้น · สลับ provider ที่ sidebar")
        return

    if not api_key:
        st.info("👈 ใส่ Gemini API Key ที่ sidebar ก่อน")
        return

    if not project_data or not project_data.get("name"):
        st.info(
            "กรอกฟอร์มที่ด้านบนก่อน (อย่างน้อยขนาดที่ดิน + จำนวนชั้น) "
            "เพื่อให้ AI มี brief สร้างภาพ"
        )
        return

    # Controls
    c_view, c_model = st.columns([2, 1])
    with c_view:
        view_type = st.radio(
            "มุมมอง",
            options=list(VIEW_TYPES.keys()),
            format_func=lambda k: f"{VIEW_TYPES[k]['label']} · {VIEW_TYPES[k]['desc']}",
            key="imgen_view",
        )
    with c_model:
        model = st.selectbox(
            "Image model",
            options=list(IMAGE_MODELS.keys()),
            format_func=lambda k: IMAGE_MODELS[k],
            key="imgen_model",
        )

    extra = st.text_area(
        "คำแนะนำเพิ่มเติม (optional)",
        placeholder=(
            "เช่น: modern Thai contemporary · wooden louvers · "
            "tropical garden · sunset lighting"
        ),
        height=80,
        key="imgen_extra",
    )

    prompt = build_prompt(project_data, view_type, extra)
    with st.expander("👁 ดู prompt ที่ส่งให้ AI"):
        st.code(prompt, language=None)

    if st.button(
        "🎨 สร้างภาพ",
        type="primary", use_container_width=True, key="imgen_go",
    ):
        with st.spinner("🖼 กำลังสร้างภาพ · ~10-30 วินาที"):
            img_bytes, err = call_api(api_key, prompt, model)

        if err:
            st.error(f"❌ {err}")
            if "404" in err.lower() or "not found" in err.lower():
                st.warning(
                    "Model นี้อาจไม่เปิดใน region หรือ API key ของคุณ · "
                    "ลองเปลี่ยน model ด้านบน หรือดูรายการที่ [ai.google.dev/docs/image-generation]"
                    "(https://ai.google.dev/gemini-api/docs/image-generation)"
                )
            elif "429" in err:
                st.warning("Rate limit · รอ 1 นาทีแล้วลองใหม่")
            return

        _save(img_bytes, view_type, model, prompt)
        st.rerun()

    _render_gallery(project_data)


def _render_gallery(project_data: dict):
    gallery = _gallery()
    if not gallery:
        return

    st.divider()
    st.markdown(f"### 🖼 ภาพที่สร้างแล้ว ({len(gallery)})")

    name = (project_data.get("name") or "project").replace("/", "-")
    for i, img in enumerate(gallery):
        vt_meta = VIEW_TYPES.get(img["view_type"], {})
        header = (
            f"🖼 #{len(gallery) - i} · "
            f"{vt_meta.get('label', img['view_type'])} · {img['model']}"
        )
        with st.expander(header, expanded=(i == 0)):
            st.image(img["bytes"], use_container_width=True)
            c1, c2 = st.columns(2)
            c1.download_button(
                "📥 ดาวน์โหลด .png",
                data=img["bytes"],
                file_name=f"mockup-{name}-{img['view_type']}-{i}.png",
                mime="image/png",
                use_container_width=True,
                key=f"imgen_dl_{i}",
            )
            if c2.button("🗑 ลบภาพนี้", use_container_width=True, key=f"imgen_del_{i}"):
                gallery.pop(i)
                st.rerun()
