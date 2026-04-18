"""Draw plan · blank canvas for sketching a floor plan · send to AI

User can sketch a rough floor plan directly in the browser,
then the sketch (as PNG) is sent to AI alongside the project data.

Uses streamlit-drawable-canvas.
"""

import io
import streamlit as st
from PIL import Image, ImageDraw


# Preset plot sizes (ratio preserved for canvas)
PLOT_PRESETS = {
    "4x16": ("ทาวน์เฮาส์ 4×16 ม.", 4, 16),
    "8x12": ("เล็ก กทม. 8×12 ม.", 8, 12),
    "10x20": ("บ้านเดี่ยวเล็ก 10×20 ม.", 10, 20),
    "15x20": ("บ้านเดี่ยว 15×20 ม.", 15, 20),
    "20x30": ("บ้านใหญ่ 20×30 ม.", 20, 30),
    "25x40": ("บ้านหรู 25×40 ม.", 25, 40),
}


def _build_grid_bg(plot_w_m: float, plot_d_m: float, px_per_m: int = 30) -> Image.Image:
    """Create a white canvas with 1m grid + dimension labels"""
    w = int(plot_w_m * px_per_m)
    h = int(plot_d_m * px_per_m)
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)

    # Grid lines every 1m (light gray), every 5m (darker)
    for i in range(0, int(plot_w_m) + 1):
        x = i * px_per_m
        color = "#cbd5e1" if i % 5 == 0 else "#e2e8f0"
        draw.line([(x, 0), (x, h)], fill=color, width=1 if i % 5 else 2)
    for j in range(0, int(plot_d_m) + 1):
        y = j * px_per_m
        color = "#cbd5e1" if j % 5 == 0 else "#e2e8f0"
        draw.line([(0, y), (w, y)], fill=color, width=1 if j % 5 else 2)

    # Border
    draw.rectangle([(0, 0), (w - 1, h - 1)], outline="#64748b", width=3)

    return img


def render_draw_plan_widget(plot_w_m: float = 15.0, plot_d_m: float = 20.0):
    """Render the drawable canvas.

    Returns: annotated image bytes (PNG) or None if nothing drawn / lib missing.
    """
    try:
        from streamlit_drawable_canvas import st_canvas
    except ImportError:
        st.info(
            "💡 ต้องติดตั้ง `streamlit-drawable-canvas` ก่อน · `pip install streamlit-drawable-canvas`"
        )
        return None

    st.markdown(
        "🖊 วาดแปลนในกรอบด้านล่าง · แต่ละช่อง = **1 ตร.ม.** · "
        "ช่องใหญ่ (เส้นเข้ม) = 5 ม. · วาดเสร็จแล้วคลิก **\"ใช้ภาพนี้วิเคราะห์\"**"
    )

    # Canvas controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        tool = st.selectbox(
            "เครื่องมือ",
            ["freedraw", "line", "rect", "transform"],
            format_func=lambda x: {
                "freedraw": "✏ วาดมือเปล่า",
                "line": "📏 เส้นตรง",
                "rect": "⬜ ห้อง (สี่เหลี่ยม)",
                "transform": "👆 เลือก/ย้าย",
            }[x],
            key="dp_tool",
        )
    with col2:
        color = st.color_picker("สี", "#1e40af", key="dp_color")
    with col3:
        stroke_width = st.slider("เส้น", 1, 8, 3, key="dp_width")
    with col4:
        st.write("")
        reset = st.button("🔄 รีเซ็ต", use_container_width=True, key="dp_reset")

    if reset:
        st.session_state["dp_canvas_v"] = st.session_state.get("dp_canvas_v", 0) + 1

    version = st.session_state.get("dp_canvas_v", 0)

    # Build grid background
    px_per_m = 30
    bg_img = _build_grid_bg(plot_w_m, plot_d_m, px_per_m)
    cw, ch = bg_img.size

    canvas_result = st_canvas(
        fill_color="rgba(59, 130, 246, 0.15)",
        stroke_width=stroke_width,
        stroke_color=color,
        background_image=bg_img,
        update_streamlit=True,
        height=ch,
        width=cw,
        drawing_mode=tool,
        key=f"dp_canvas_{version}",
    )

    # Compose output
    if canvas_result.image_data is not None:
        try:
            overlay = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
            composed = bg_img.convert("RGBA")
            composed.alpha_composite(overlay)
            composed_rgb = composed.convert("RGB")
            buf = io.BytesIO()
            composed_rgb.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as e:
            st.caption(f"_(compose failed: {e})_")

    return None


def _on_preset_change():
    """Callback fires before widgets re-instantiate → safe to mutate state"""
    preset_key = st.session_state.get("dp_preset", "custom")
    if preset_key != "custom" and preset_key in PLOT_PRESETS:
        _, pw, pd = PLOT_PRESETS[preset_key]
        st.session_state["dp_plot_w"] = float(pw)
        st.session_state["dp_plot_d"] = float(pd)


def render_draw_tab(project_data: dict):
    """Render the full draw-plan tab (preset picker + canvas + use button)"""
    st.markdown("### 🖊 วาดแปลนด้วยตัวเอง")
    st.caption(
        "วาดเค้าโครงคร่าวๆ โดยไม่ต้อง upload รูป · "
        "เหมาะสำหรับ brainstorming · ส่งภาพที่วาดให้ AI วิเคราะห์พร้อมข้อมูลโครงการ"
    )

    # Initialize session defaults BEFORE instantiating widgets (so preset
    # callback can mutate them without StreamlitAPIException).
    default_w = float(project_data.get("land_w", 15))
    default_d = float(project_data.get("land_d", 20))
    st.session_state.setdefault("dp_plot_w", default_w)
    st.session_state.setdefault("dp_plot_d", default_d)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        plot_w = st.number_input(
            "กว้างที่ดิน (ม.)",
            min_value=3.0, max_value=50.0,
            step=0.5,
            key="dp_plot_w",
        )
    with col2:
        plot_d = st.number_input(
            "ลึกที่ดิน (ม.)",
            min_value=3.0, max_value=80.0,
            step=0.5,
            key="dp_plot_d",
        )
    with col3:
        st.selectbox(
            "หรือเลือก preset",
            options=["custom"] + list(PLOT_PRESETS.keys()),
            format_func=lambda k: "-- ไม่เปลี่ยน --" if k == "custom" else PLOT_PRESETS[k][0],
            key="dp_preset",
            on_change=_on_preset_change,
        )

    st.markdown("---")

    plan_bytes = render_draw_plan_widget(plot_w, plot_d)

    if plan_bytes:
        st.markdown("---")
        col_save, col_dl = st.columns(2)
        with col_save:
            if st.button(
                "✅ ใช้ภาพนี้วิเคราะห์ (ส่งไปแท็บ 'วิเคราะห์ใหม่')",
                type="primary", use_container_width=True, key="dp_use",
            ):
                st.session_state["_drawn_plan_bytes"] = plan_bytes
                st.success("✅ บันทึกแล้ว · ไปแท็บ 'วิเคราะห์ใหม่' เพื่อวิเคราะห์")
        with col_dl:
            st.download_button(
                "📥 ดาวน์โหลด .png",
                data=plan_bytes,
                file_name=f"drawn-plan-{project_data.get('name','untitled')}.png",
                mime="image/png",
                use_container_width=True,
                key="dp_download",
            )
