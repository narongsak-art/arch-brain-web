"""Materials palette · วัสดุไทยสำหรับบ้านเขตร้อนชื้น

Thai-specific material library. Used to pick a palette for a project
and have AI consider it when recommending / rendering.

Not tied to real product catalogs · descriptive only · AI reads the
palette keys to ground its suggestions and image-gen prompts.
"""

import streamlit as st


# ============================================================================
# Material library · grouped by application
# ============================================================================

MATERIALS = {
    "roof": {
        "label": "หลังคา",
        "emoji": "🏠",
        "items": {
            "tile-clay": ("กระเบื้องดินเผา", "#a0522d", "classic Thai · รถระบายน้ำดี · เกราะกันความร้อน"),
            "tile-concrete": ("กระเบื้องคอนกรีต", "#808080", "ราคากลาง · แข็งแรง · น้ำหนักเยอะ"),
            "metal-coated": ("เมทัลชีทเคลือบ", "#4a4a4a", "ติดตั้งเร็ว · น้ำหนักเบา · กันร้อน"),
            "wood-shingle": ("กระเบื้องไม้", "#8b4513", "vernacular · บ้านไทยพื้นถิ่น · ต้องการ maintenance"),
            "thatch": ("หญ้าคา · จาก", "#d4a574", "เย็น · ทรอปิคอล · vernacular · rerolled ทุก 3-5 ปี"),
        },
    },
    "wall": {
        "label": "ผนัง",
        "emoji": "🧱",
        "items": {
            "brick-red": ("อิฐแดง", "#8b4513", "ดูดซับความร้อนต่ำ · โชว์ลาย · Thai architecture"),
            "concrete-smooth": ("ปูนเรียบ", "#e5e1d8", "modern · ทาสีได้ · ราคากลาง"),
            "wood-teak": ("ไม้สัก", "#c9875a", "heritage · บ้านไทยเดิม · ราคาสูง · อายุยาว 80+ ปี"),
            "wood-reclaimed": ("ไม้เก่าสัก", "#9c6b3f", "vintage · eco · ลดต้นทุน · มีเสน่ห์"),
            "fiber-cement": ("ไฟเบอร์ซีเมนต์", "#b8b0a2", "แพร่หลาย · ราคาถูก · ดูแลง่าย"),
            "stucco": ("ปูนปั้น", "#ede4d3", "งานฝีมือ · texture · luxury Thai vernacular"),
        },
    },
    "floor": {
        "label": "พื้น",
        "emoji": "👣",
        "items": {
            "tile-granite": ("หินแกรนิต", "#4a4a4a", "ทนทาน · luxury · เย็น"),
            "tile-travertine": ("หินทราเวอร์ทีน", "#d2b48c", "upscale · warm · edges อาจต้องเคลือบ"),
            "wood-teak-plank": ("พื้นไม้สัก", "#b8854f", "Thai heritage · หายาก · ราคาสูงมาก"),
            "wood-engineered": ("พื้นไม้เอ็นจิเนียร์", "#a87a51", "สวย · ราคากลาง · ดูแลง่าย"),
            "concrete-polished": ("ขัดมัน", "#7a7a7a", "modern Thai · ประหยัด · cool to touch"),
            "tile-ceramic": ("กระเบื้องเซรามิก", "#e8e4dc", "ทั่วไป · ราคาถูก · ดูแลง่าย"),
            "terrazzo": ("หินอ่อนผสม", "#d4c5a8", "มิกซ์ยุค · pattern · กลางบ้านไทย 60s-70s revival"),
        },
    },
    "door-window": {
        "label": "ประตู-หน้าต่าง",
        "emoji": "🚪",
        "items": {
            "wood-louver": ("ไม้ซี่เกล็ด · louver", "#9c6b3f", "classic Thai · privacy + airflow"),
            "wood-panel": ("ไม้แผ่นบาน", "#b8854f", "warmth · heritage · ไม้สัก/ไม้เต็ง"),
            "aluminum-modern": ("อลูมิเนียมโมเดิร์น", "#a0a0a0", "slim profile · modern · large openings"),
            "steel-dark": ("เหล็กสีเข้ม", "#2f2f2f", "industrial · strong lines · modern loft"),
            "glass-sliding": ("บานเลื่อนกระจก", "#c0d7e0", "panoramic · garden view · indoor-outdoor"),
        },
    },
    "accent": {
        "label": "สีเสริม · accent",
        "emoji": "🎨",
        "items": {
            "indigo-thai": ("คราม (Thai indigo)", "#2e4057", "heritage · subtle · refined"),
            "gold-royal": ("ทอง royal", "#c9a961", "luxury · auspicious · พระ"),
            "lotus-pink": ("ชมพูกลีบบัว", "#e8a5b0", "feminine · soft · temple reminiscent"),
            "teak-deep": ("น้ำตาลสัก", "#8b5a2b", "warm · grounding · Thai wood"),
            "sage-herb": ("เขียวใบข่า", "#7a8b6e", "natural · calming · garden-adjacent"),
            "terracotta": ("ดินเผา", "#c97864", "earthy · tropical · tile color"),
            "cream-paper": ("ครีมกระดาษ", "#faf7f0", "editorial · neutral backdrop"),
        },
    },
}


# ============================================================================
# Session storage · pick per project
# ============================================================================

def _init():
    st.session_state.setdefault("materials_palette", {})


def set_pick(group: str, item_key: str):
    _init()
    st.session_state["materials_palette"][group] = item_key


def clear_pick(group: str):
    _init()
    st.session_state["materials_palette"].pop(group, None)


def get_palette() -> dict:
    _init()
    return st.session_state["materials_palette"]


def palette_summary() -> str:
    """Flat text for AI prompt inclusion"""
    p = get_palette()
    if not p:
        return ""
    parts = []
    for group, item_key in p.items():
        group_meta = MATERIALS.get(group, {})
        items = group_meta.get("items", {})
        if item_key in items:
            name, _, desc = items[item_key]
            parts.append(f"{group_meta.get('label', group)}: {name} ({desc})")
    return " · ".join(parts)


# ============================================================================
# UI
# ============================================================================

SWATCH_CSS = """
<style>
  .swatch-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 6px 0;
  }
  .swatch-card {
    width: 108px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: all 0.15s ease;
  }
  .swatch-card:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow-sm);
  }
  .swatch-card.selected {
    border-color: var(--primary);
    border-width: 2px;
    box-shadow: var(--shadow-md);
  }
  .swatch-color {
    height: 64px;
    width: 100%;
    position: relative;
  }
  .swatch-color::after {
    content: attr(data-hex);
    position: absolute;
    bottom: 4px;
    right: 6px;
    font-size: 0.68em;
    font-weight: 500;
    color: rgba(255,255,255,0.8);
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
    font-family: monospace;
  }
  .swatch-card .swatch-label {
    padding: 6px 8px;
    font-size: 0.82em;
    color: var(--text);
    font-weight: 500;
    line-height: 1.2;
    min-height: 30px;
  }
</style>
"""


def _render_group(group_key: str):
    group = MATERIALS[group_key]
    selected_item = get_palette().get(group_key)

    st.markdown(f"##### {group['emoji']} {group['label']}")

    # Flat columns grid (st.columns handles responsive wrap on mobile)
    items = list(group["items"].items())
    cols = st.columns(min(len(items), 4))
    for i, (item_key, (name, hex_color, desc)) in enumerate(items):
        col = cols[i % len(cols)]
        is_selected = selected_item == item_key

        # Show swatch as HTML (has color + hex)
        border = "2px solid var(--primary)" if is_selected else "1px solid var(--border)"
        col.markdown(
            f'<div style="border: {border}; border-radius: 10px; overflow: hidden; margin-bottom: 6px;">'
            f'<div style="background: {hex_color}; height: 56px; display: flex; align-items: flex-end; justify-content: flex-end; padding: 4px 6px;">'
            f'<span style="font-size: 0.68em; font-family: monospace; color: rgba(255,255,255,0.85); text-shadow: 0 1px 2px rgba(0,0,0,0.4);">{hex_color}</span>'
            f'</div>'
            f'<div style="padding: 6px 8px; font-size: 0.82em; min-height: 30px;">{name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        col.caption(desc)
        btn_label = "✓ Selected" if is_selected else "เลือก"
        if col.button(
            btn_label,
            key=f"mat_pick_{group_key}_{item_key}",
            use_container_width=True,
            type="primary" if is_selected else "secondary",
        ):
            if is_selected:
                clear_pick(group_key)
            else:
                set_pick(group_key, item_key)
            st.rerun()


def render_panel():
    """Full materials picker tab · inject CSS + render 5 groups"""
    st.markdown(SWATCH_CSS, unsafe_allow_html=True)

    st.markdown(
        '<div class="ab-eyebrow">THAI MATERIALS PALETTE</div>'
        '<h2 style="margin-top: 4px; margin-bottom: 6px;">วัสดุไทย · สำหรับบ้านเขตร้อนชื้น</h2>'
        '<p style="color: var(--text-muted); margin-bottom: 14px;">'
        'เลือกวัสดุแต่ละหมวด · AI จะใช้ palette นี้ประกอบการวิเคราะห์และสร้างภาพ mockup'
        '</p>',
        unsafe_allow_html=True,
    )

    palette = get_palette()
    if palette:
        summary = palette_summary()
        st.info(f"🎨 **Palette ปัจจุบัน:** {summary}")
        if st.button("🧹 รีเซ็ตทั้งหมด", key="mat_reset_all"):
            st.session_state["materials_palette"] = {}
            st.rerun()

    # Render each group
    for group_key in MATERIALS.keys():
        st.divider()
        _render_group(group_key)

    # Download palette as JSON
    if palette:
        st.divider()
        import json
        export = {
            "palette": {
                group_key: {
                    "key": item_key,
                    "name": MATERIALS[group_key]["items"][item_key][0],
                    "hex": MATERIALS[group_key]["items"][item_key][1],
                    "note": MATERIALS[group_key]["items"][item_key][2],
                }
                for group_key, item_key in palette.items()
                if item_key in MATERIALS.get(group_key, {}).get("items", {})
            },
            "summary": palette_summary(),
        }
        st.download_button(
            "📥 Download palette .json",
            data=json.dumps(export, ensure_ascii=False, indent=2),
            file_name="palette.json",
            mime="application/json",
            use_container_width=True,
        )
