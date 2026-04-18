"""Compatibility shims for third-party Streamlit libs

streamlit-drawable-canvas (as of 0.9.x) calls
`streamlit.elements.image.image_to_url(image, width, clamp, channels,
output_format, image_id)` which was moved to
`streamlit.elements.lib.image_utils` with a new signature in Streamlit
1.32+. The new signature takes a `LayoutConfig` object instead of a
raw `width: int`. We wrap the new function with the old positional
calling convention.

Import this module BEFORE importing `streamlit_drawable_canvas` anywhere.
"""

try:
    from streamlit.elements import image as _st_image_module
except Exception:
    _st_image_module = None

try:
    from streamlit.elements.lib.image_utils import image_to_url as _modern_image_to_url
    from streamlit.elements.lib.image_utils import LayoutConfig as _LayoutConfig
except Exception:
    _modern_image_to_url = None
    _LayoutConfig = None


def _image_to_url_shim(image, width=-1, clamp=False, channels="RGB",
                      output_format="auto", image_id="", *args, **kwargs):
    """Adapter: old-style positional call → modern image_to_url.

    The old signature is (image, width, clamp, channels, output_format, image_id).
    The new one takes (image, layout_config, clamp, channels, output_format, image_id).
    """
    if _modern_image_to_url is not None and _LayoutConfig is not None:
        try:
            layout = _LayoutConfig(width=width) if width and width > 0 else _LayoutConfig()
            return _modern_image_to_url(
                image, layout, clamp, channels, output_format, image_id or ""
            )
        except Exception:
            pass  # fall through to data-URL fallback below

    # Last-resort data-URL fallback (works even with baseUrlPath because
    # libraries commonly test `if url.startswith('data:')` before prepending)
    import base64, io
    try:
        from PIL import Image as _PIL
        if isinstance(image, _PIL.Image):
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Exception:
        pass
    if isinstance(image, (bytes, bytearray)):
        b64 = base64.b64encode(bytes(image)).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    return ""


if _st_image_module is not None and not hasattr(_st_image_module, "image_to_url"):
    _st_image_module.image_to_url = _image_to_url_shim
