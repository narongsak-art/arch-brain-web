"""Image generation · Gemini 2.5 Flash Image (bird's-eye mockup from brief)

Uses Google's image-capable Gemini model to generate:
- Bird's-eye mockup from project brief
- Concept sketch (perspective)
- Floor plan sketch (top-down)

Note: Image gen requires a Gemini API key with image-generation enabled.
Model: `gemini-2.5-flash-image-preview` (may change · check ai.google.dev)
"""

import base64
import io
from typing import Literal

import requests
import streamlit as st


IMAGE_MODELS = {
    "gemini-2.5-flash-image": "🖼 Gemini 2.5 Flash Image (ล่าสุด)",
    "gemini-2.5-flash-image-preview": "🧪 Gemini 2.5 Flash Image (preview)",
    "gemini-2.0-flash-preview-image-generation": "📦 Gemini 2.0 Flash Image (backup)",
}
DEFAULT_IMAGE_MODEL = "gemini-2.5-flash-image"


# ============================================================================
# Prompt templates
# ============================================================================

VIEW_TYPES = {
    "birdseye": {
        "label": "🦅 Bird's-eye view",
        "desc": "มุมสูง · เห็นทั้งบ้าน + สวน + ที่ดิน",
        "prompt_style": (
            "Architectural bird's-eye rendering, isometric 45-degree angle, "
            "showing the full plot with house, landscape, driveway, garden. "
            "Professional architectural visualization, soft natural daylight, "
            "photorealistic materials, clean modern style."
        ),
    },
    "perspective": {
        "label": "🏠 Perspective view (3/4)",
        "desc": "มุม 3/4 · เห็น facade + ทางเข้า",
        "prompt_style": (
            "Architectural 3/4 perspective rendering at eye level, "
            "showing the main facade and entrance, with landscape in foreground. "
            "Professional photorealistic style, warm daylight, clear sky."
        ),
    },
    "floorplan": {
        "label": "📐 Floor plan sketch",
        "desc": "แปลนสไตล์วาดมือ · top-down",
        "prompt_style": (
            "Architectural floor plan sketch, top-down view, hand-drawn style, "
            "clean linework with room labels in Thai, dimensional annotations, "
            "north arrow, scale bar, minimal color."
        ),
    },
    "interior": {
        "label": "🛋 Interior mood",
        "desc": "บรรยากาศภายใน (ห้องหลัก)",
        "prompt_style": (
            "Interior architectural rendering of the main living space, "
            "natural daylight through large windows, warm modern Thai tropical style, "
            "photorealistic, soft ambient lighting."
        ),
    },
}


def build_mockup_prompt(
    project_data: dict,
    view_type: Literal["birdseye", "perspective", "floorplan", "interior"] = "birdseye",
    extra_notes: str = "",
) -> str:
    """Build a natural-language prompt for image generation from the project brief"""
    vt = VIEW_TYPES.get(view_type, VIEW_TYPES["birdseye"])

    # Build a concise project description
    parts = []
    parts.append(f"A {project_data.get('floors', '2')}-story Thai residential house.")
    parts.append(
        f"Plot size: {project_data.get('land_w', 15)}×{project_data.get('land_d', 20)} meters "
        f"({project_data.get('land_area', 300):.0f} sqm)."
    )
    parts.append(
        f"{project_data.get('bedrooms', '3')} bedrooms, "
        f"for a family of {project_data.get('family_size', 4)}."
    )
    parts.append(
        f"Located in {project_data.get('province', 'Bangkok')}, "
        f"zoning {project_data.get('zone', 'residential')}."
    )

    if project_data.get("has_elderly") == "ใช่":
        parts.append("Accessible design for elderly residents (ground-floor bedroom, ramps).")

    if project_data.get("fengshui") in ("มาก", "ปานกลาง"):
        parts.append("Incorporates Thai cultural elements (prayer room, auspicious orientation).")

    special = project_data.get("special", "").strip()
    if special:
        parts.append(f"Special requirements: {special}.")

    # Tropical climate context
    parts.append(
        "Tropical climate design: wide eaves, ventilated openings, "
        "shaded veranda, appropriate for Thailand's hot-humid climate."
    )

    brief = " ".join(parts)
    if extra_notes.strip():
        brief += f" Additional notes: {extra_notes.strip()}."

    return f"{vt['prompt_style']}\n\nProject brief:\n{brief}"


# ============================================================================
# Gemini Image API
# ============================================================================

def call_gemini_image(api_key: str, prompt: str, model: str | None = None) -> tuple[bytes | None, str | None]:
    """Call Gemini image-generation API. Returns (image_bytes, error_msg)."""
    model = model or st.session_state.get("image_model", DEFAULT_IMAGE_MODEL)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
    except requests.RequestException as e:
        return None, f"Network error: {e}"

    if response.status_code != 200:
        return None, f"API {response.status_code}: {response.text[:300]}"

    try:
        data = response.json()
    except Exception as e:
        return None, f"Invalid JSON: {e}"

    candidates = data.get("candidates", [])
    if not candidates:
        return None, f"No candidates: {data}"

    for part in candidates[0].get("content", {}).get("parts", []):
        inline = part.get("inline_data") or part.get("inlineData")
        if inline and inline.get("data"):
            try:
                img_bytes = base64.b64decode(inline["data"])
                return img_bytes, None
            except Exception as e:
                return None, f"decode error: {e}"

    return None, "No image in response (model may have refused or returned text only)"


# ============================================================================
# UI
# ============================================================================

def render_image_gen_panel(project_data: dict, api_key: str):
    """Render image generation UI inside the analysis tab"""
    st.markdown("### 🎨 สร้างภาพ mockup จาก brief")
    st.caption(
        "ให้ AI ช่วยสร้างภาพ visualization จากข้อมูลโครงการ · "
        "ใช้ Gemini Image model (ใช้ quota Gemini ของคุณเอง)"
    )

    if not api_key:
        st.info("ใส่ Gemini API Key ที่ sidebar ก่อน (ใช้ key เดียวกับวิเคราะห์)")
        return

    col_type, col_model = st.columns([2, 1])
    with col_type:
        view_type = st.radio(
            "มุมมอง",
            options=list(VIEW_TYPES.keys()),
            format_func=lambda k: f"{VIEW_TYPES[k]['label']} · {VIEW_TYPES[k]['desc']}",
            horizontal=False,
            key="imgen_view_type",
        )
    with col_model:
        model = st.selectbox(
            "Image model",
            options=list(IMAGE_MODELS.keys()),
            format_func=lambda k: IMAGE_MODELS[k],
            key="imgen_model",
        )
        st.session_state["image_model"] = model

    extra = st.text_area(
        "คำแนะนำเพิ่มเติม (optional)",
        placeholder="เช่น: modern Thai contemporary style, wooden louvers, tropical garden, sunset lighting",
        height=80,
        key="imgen_extra",
    )

    prompt = build_mockup_prompt(project_data, view_type, extra)
    with st.expander("👁 ดู prompt ที่ส่งให้ AI"):
        st.code(prompt, language=None)

    if st.button("🎨 สร้างภาพ", type="primary", use_container_width=True, key="imgen_go"):
        with st.spinner("🖼 กำลังสร้างภาพ · ~10-30 วินาที"):
            img_bytes, err = call_gemini_image(api_key, prompt, model)

        if err:
            st.error(f"❌ {err}")
            if "not found" in err.lower() or "404" in err:
                st.warning(
                    "Image model อาจไม่เปิดใน region หรือ API key นี้ · "
                    "ลองเปลี่ยน model หรือดูที่ [ai.google.dev](https://ai.google.dev/gemini-api/docs/image-generation)"
                )
            return

        # Store in session so user can regenerate / download multiple views
        images = st.session_state.setdefault("generated_images", [])
        images.insert(0, {
            "bytes": img_bytes,
            "view_type": view_type,
            "model": model,
            "prompt": prompt,
        })

    _render_image_gallery(project_data)


def _render_image_gallery(project_data: dict):
    images = st.session_state.get("generated_images", [])
    if not images:
        return

    st.markdown("---")
    st.markdown(f"### 🖼 ภาพที่สร้างแล้ว ({len(images)})")
    for i, img in enumerate(images[:6]):  # Show latest 6
        with st.expander(
            f"🖼 #{len(images) - i} · {VIEW_TYPES.get(img['view_type'], {}).get('label', img['view_type'])} · {img['model']}",
            expanded=(i == 0),
        ):
            st.image(img["bytes"], use_container_width=True)
            name = project_data.get("name", "project")
            st.download_button(
                f"📥 ดาวน์โหลด .png",
                data=img["bytes"],
                file_name=f"mockup-{name}-{img['view_type']}-{i}.png",
                mime="image/png",
                use_container_width=True,
                key=f"imgen_dl_{i}",
            )
