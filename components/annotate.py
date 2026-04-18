"""Image annotations · draw/mark on uploaded plan using streamlit-drawable-canvas"""

import io
import streamlit as st
from PIL import Image


def render_annotate_widget(uploaded_file):
    """
    Show a drawable canvas over the uploaded plan.
    Returns the annotated image bytes (PNG) or the original bytes if no annotation drawn.
    """
    if uploaded_file is None:
        return None

    try:
        from streamlit_drawable_canvas import st_canvas
    except ImportError:
        st.info(
            "💡 ถ้าต้องการวาด/มาร์คบนแปลนก่อนส่ง AI · ติดตั้ง `streamlit-drawable-canvas`\n\n"
            "`pip install streamlit-drawable-canvas`"
        )
        st.image(uploaded_file, caption="แปลนที่อัปโหลด (ไม่มี annotate)", use_container_width=True)
        return uploaded_file.getvalue()

    # Load image
    img = Image.open(uploaded_file).convert("RGB")
    orig_w, orig_h = img.size

    # Downscale for canvas if too big
    max_w = 900
    scale = min(1.0, max_w / orig_w)
    cw = int(orig_w * scale)
    ch = int(orig_h * scale)
    bg_img = img.resize((cw, ch)) if scale < 1.0 else img

    st.markdown("##### 🖊 มาร์ค/วาดบนแปลน (ไม่บังคับ)")
    col_tool, col_color, col_width, col_reset = st.columns([2, 1, 1, 1])
    with col_tool:
        tool = st.selectbox(
            "เครื่องมือ",
            ["freedraw", "line", "rect", "circle", "transform"],
            format_func=lambda x: {
                "freedraw": "✏ วาดมือเปล่า",
                "line": "📏 เส้นตรง",
                "rect": "⬜ สี่เหลี่ยม",
                "circle": "⭕ วงกลม",
                "transform": "👆 เลือก/ย้าย",
            }[x],
            key="annot_tool",
        )
    with col_color:
        color = st.color_picker("สี", "#ef4444", key="annot_color")
    with col_width:
        stroke_width = st.slider("เส้น", 1, 10, 3, key="annot_width")
    with col_reset:
        st.write("")
        reset = st.button("🔄 รีเซ็ต", key="annot_reset", use_container_width=True)

    canvas_key = "plan_canvas"
    if reset:
        # Changing the key resets the canvas
        st.session_state["annot_canvas_v"] = st.session_state.get("annot_canvas_v", 0) + 1
    version = st.session_state.get("annot_canvas_v", 0)

    canvas_result = st_canvas(
        fill_color="rgba(239, 68, 68, 0.15)",
        stroke_width=stroke_width,
        stroke_color=color,
        background_image=bg_img,
        update_streamlit=True,
        height=ch,
        width=cw,
        drawing_mode=tool,
        key=f"{canvas_key}_{version}",
    )

    # Compose output: flatten canvas strokes onto image
    if canvas_result.image_data is not None:
        try:
            # image_data is RGBA array of canvas strokes (bg removed)
            from PIL import Image as _PIL
            overlay = _PIL.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
            # Resize back to original size
            if scale < 1.0:
                overlay = overlay.resize((orig_w, orig_h))
            composed = img.convert("RGBA")
            composed.alpha_composite(overlay)
            composed_rgb = composed.convert("RGB")
            buf = io.BytesIO()
            composed_rgb.save(buf, format="JPEG", quality=88)
            return buf.getvalue()
        except Exception as e:
            st.caption(f"_(annot compose failed: {e} · ส่งภาพต้นฉบับแทน)_")

    return uploaded_file.getvalue()
