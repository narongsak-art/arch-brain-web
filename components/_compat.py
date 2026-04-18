"""Compatibility shims for third-party Streamlit libs

streamlit-drawable-canvas (as of 0.9.x) relies on
`streamlit.elements.image.image_to_url()` which was removed in Streamlit 1.32+.

Import this module BEFORE importing `streamlit_drawable_canvas` anywhere.
"""

import base64
import io

try:
    from streamlit.elements import image as _st_image_module
except Exception:
    _st_image_module = None


def _image_to_url_shim(image, width=-1, clamp=False, channels="RGB",
                      output_format="auto", image_id="", allow_emoji=False,
                      mime_type=None):
    """Data-URL fallback for PIL Image / bytes / numpy array"""
    # Bytes → use as-is
    if isinstance(image, (bytes, bytearray)):
        raw = bytes(image)
        mime = mime_type or "image/png"
        b64 = base64.b64encode(raw).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    # PIL Image
    try:
        from PIL import Image
        if isinstance(image, Image.Image):
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Exception:
        pass

    # numpy array
    try:
        import numpy as np
        if isinstance(image, np.ndarray):
            from PIL import Image
            img = Image.fromarray(image.astype("uint8"))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Exception:
        pass

    # String: assume already a URL / file path
    if isinstance(image, str):
        return image

    # Last-resort empty 1x1 transparent PNG
    return (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )


if _st_image_module is not None and not hasattr(_st_image_module, "image_to_url"):
    _st_image_module.image_to_url = _image_to_url_shim
