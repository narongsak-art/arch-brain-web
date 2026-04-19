"""
สมองจำลองของสถาปนิก · Thai Residential Architecture AI
Lean v3.0 — single-page app, no third-party UI libs beyond Streamlit.

Flow: form → (optional upload) → AI analysis → structured display + download
"""

import json
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from components import theme, llm, analysis, presets, history, contribute, project_io, export_pdf, share, image_gen, chat, compare, booking, tiers, admin, studio, materials


# =============================================================================
# Config
# =============================================================================

st.set_page_config(
    page_title="สมองจำลองของสถาปนิก",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
KG_FILE = ROOT / "kg-compact.json"
FULL_FILE = ROOT / "full-knowledge.md"
PROMPT_FILE = ROOT / "system-prompt.md"


@st.cache_data
def load_kg() -> str:
    return KG_FILE.read_text(encoding="utf-8") if KG_FILE.exists() else ""


@st.cache_data
def load_full() -> str:
    return FULL_FILE.read_text(encoding="utf-8") if FULL_FILE.exists() else ""


@st.cache_data
def load_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8") if PROMPT_FILE.exists() else "You are an architect's assistant."


# =============================================================================
# Session state
# =============================================================================

for key, default in [
    ("history", []),
    ("result", None),
    ("raw_text", None),
    ("project_data", None),
    ("last_provider", None),
]:
    st.session_state.setdefault(key, default)


# =============================================================================
# Sidebar
# =============================================================================

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🏠 สมองจำลองของสถาปนิก")
        st.caption("Architect's Brain · v3.0")
        theme.toggle_widget(container=st.sidebar)
        st.divider()

        # Tier badge
        tiers.render_sidebar_badge()
        st.divider()

        provider = st.radio(
            "AI Provider",
            options=["gemini", "claude"],
            format_func=lambda x: {"gemini": "🆓 Gemini (ฟรี)", "claude": "💎 Claude"}[x],
            horizontal=True,
            key="sb_provider",
        )

        if provider == "gemini":
            api_key = st.text_input(
                "Gemini API Key", type="password",
                placeholder="AIza...", key="sb_gemini_key",
                help="ฟรี · รับได้ที่ aistudio.google.com/apikey",
            )
            st.caption("📎 [รับ Gemini ฟรี](https://aistudio.google.com/apikey)")
            model = st.selectbox(
                "Model",
                options=list(llm.GEMINI_MODELS.keys()),
                format_func=lambda x: llm.GEMINI_MODELS[x],
                key="sb_model",
            )
        else:
            api_key = st.text_input(
                "Claude API Key", type="password",
                placeholder="sk-ant-...", key="sb_claude_key",
            )
            st.caption("📎 [สมัคร Claude](https://console.anthropic.com)")
            model = "claude-sonnet-4-6"

        st.divider()

        # KG info
        try:
            kg_data = json.loads(load_kg())
            meta = kg_data.get("meta", {})
            c1, c2 = st.columns(2)
            c1.metric("Nodes", meta.get("node_count", 0))
            c2.metric("Edges", meta.get("edge_count", 0))
        except Exception:
            st.caption("KG not loaded")

        hist_n = len(st.session_state["history"])
        st.caption(f"📚 ประวัติ session: {hist_n}")

        st.divider()
        st.caption(
            "**5 ชั้นความรู้**\n\n"
            "🏛 กฎหมาย · 🔧 วิศวกรรม · 🎨 ออกแบบ · 🪷 วัฒนธรรมไทย · ☯ ฮวงจุ้ย\n\n"
            "⚠ ผลเบื้องต้น · ไม่แทนสถาปนิก/วิศวกรใบอนุญาต"
        )

    return provider, api_key, model


# =============================================================================
# Main UI
# =============================================================================

def render_hero():
    theme.hero(
        "สมองจำลองของสถาปนิก",
        "วิเคราะห์แปลนบ้านไทยด้วย AI + Knowledge Graph 5 ชั้น · ผลใน ~60 วินาที",
        eyebrow="Thai Architect's Studio · since 2026",
    )


def render_welcome_onboarding():
    """Shown above form when user has NO api_key yet · makes first impression useful"""
    st.markdown("""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 10px 0 18px 0;">
  <div class="ab-card">
    <div style="font-size: 1.8em;">📐</div>
    <strong>Structured metrics</strong>
    <div style="color: var(--text-muted); font-size: 0.9em;">FAR · OSR · setback · buildable area · cost estimate</div>
  </div>
  <div class="ab-card">
    <div style="font-size: 1.8em;">🧩</div>
    <strong>5-Layer scoring</strong>
    <div style="color: var(--text-muted); font-size: 0.9em;">กฎหมาย · วิศวกรรม · ออกแบบ · วัฒนธรรมไทย · ฮวงจุ้ย</div>
  </div>
  <div class="ab-card">
    <div style="font-size: 1.8em;">🚪</div>
    <strong>Room-by-room</strong>
    <div style="color: var(--text-muted); font-size: 0.9em;">ขนาดแนะนำ · ทิศที่ดี · ข้อควรระวัง · ฮวงจุ้ย</div>
  </div>
  <div class="ab-card">
    <div style="font-size: 1.8em;">🎨</div>
    <strong>Image mockup</strong>
    <div style="color: var(--text-muted); font-size: 0.9em;">AI สร้างภาพ bird's-eye · perspective · floor plan</div>
  </div>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 1️⃣ รับ API key (ฟรี)")
        st.markdown("ใช้ **[Gemini API](https://aistudio.google.com/apikey)** · ไม่ต้องใส่ credit card · ได้ 1,500 ครั้ง/วัน")
    with c2:
        st.markdown("### 2️⃣ ใส่ที่ sidebar")
        st.markdown("👈 Sidebar ซ้าย · กรอก key แล้วเลือก model ได้เลย")
    with c3:
        st.markdown("### 3️⃣ กรอกข้อมูล → วิเคราะห์")
        st.markdown("เลือก preset ได้เพื่อความเร็ว · หรือกรอกเองทั้งหมด · ผล 60 วินาที")

    st.info(
        "💡 **Privacy:** API key ของคุณ + ข้อมูลโปรเจค ไม่ถูกเก็บ · "
        "ไม่ถูกใช้ train AI · ทุกอย่างอยู่ใน browser session · ปิด tab = หายหมด"
    )


def render_form() -> dict:
    """Project brief form. Returns project_data dict."""
    st.subheader("📝 ข้อมูลโครงการ")

    presets.render_chips()

    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อโปรเจค", value="บ้าน-A", key="form_name")
        land_w = st.number_input("กว้างที่ดิน (ม.)", 3.0, 100.0, 15.0, 0.5, key="form_land_w")
        land_d = st.number_input("ลึกที่ดิน (ม.)", 3.0, 100.0, 20.0, 0.5, key="form_land_d")
        province = st.selectbox(
            "จังหวัด",
            options=["กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี", "สมุทรปราการ",
                     "นครปฐม", "เชียงใหม่", "ภูเก็ต", "อื่นๆ"],
            key="form_province",
        )
        zone = st.selectbox(
            "สีผังเมือง",
            options=["ย.1", "ย.2", "ย.3", "ย.4", "ย.5", "ย.6", "ย.7",
                     "ย.8", "ย.9", "ย.10", "พ.1", "พ.2", "ไม่ทราบ"],
            index=2,
            help="ย. = ที่อยู่อาศัย · พ. = พาณิชย์",
            key="form_zone",
        )
        street_w = st.number_input("ถนนติดกว้าง (ม.)", 1.0, 50.0, 6.0, 0.5, key="form_street")

    with c2:
        family_size = st.slider("สมาชิกครอบครัว", 1, 15, 4, key="form_family")
        has_elderly = st.radio("มีผู้สูงอายุ", ["ไม่มี", "มี"], horizontal=True, key="form_elderly")
        floors = st.selectbox("จำนวนชั้น", ["1", "2", "3", "4+"], index=1, key="form_floors")
        bedrooms = st.selectbox("ห้องนอน", ["1", "2", "3", "4", "5+"], index=2, key="form_bedrooms")
        budget = st.number_input("งบ (ล้านบาท)", 0.5, 200.0, 8.0, 0.5, key="form_budget")
        fengshui = st.selectbox("สนใจฮวงจุ้ย", ["มาก", "ปานกลาง", "น้อย", "ไม่สน"], index=1, key="form_fs")

    special = st.text_area(
        "ความต้องการพิเศษ",
        placeholder="เช่น ห้องพระ · สระว่ายน้ำ · walk-in · home office · ผู้สูงอายุใช้ wheelchair",
        height=100,
        key="form_special",
    )

    return {
        "name": name,
        "land_w": land_w,
        "land_d": land_d,
        "land_area": land_w * land_d,
        "province": province,
        "zone": zone,
        "street_w": street_w,
        "family_size": family_size,
        "has_elderly": "ใช่" if has_elderly == "มี" else "ไม่",
        "floors": floors,
        "bedrooms": bedrooms,
        "budget": budget,
        "fengshui": fengshui,
        "special": special,
    }


def build_user_message(pd: dict) -> str:
    palette = materials.palette_summary()
    palette_line = f"- วัสดุที่เลือก (palette): {palette}\n" if palette else ""
    return f"""ข้อมูลโครงการ:
- ชื่อ: {pd['name']}
- ที่ดิน: {pd['land_w']} × {pd['land_d']} ม. ({pd['land_area']:.0f} ตร.ม.)
- เขต: {pd['zone']} · จังหวัด: {pd['province']}
- ถนนติด: {pd['street_w']} ม.
- ครอบครัว: {pd['family_size']} คน · ผู้สูงอายุ: {pd['has_elderly']}
- ชั้น: {pd['floors']} · ห้องนอน: {pd['bedrooms']}
- งบ: {pd['budget']} ล้านบาท
- ฮวงจุ้ย: {pd['fengshui']}
- ความต้องการพิเศษ: {pd['special']}
{palette_line}
วิเคราะห์โครงการนี้ตาม JSON schema ด้านบน (structured output · ห้ามใส่ markdown)
"""


def run_analysis(provider: str, api_key: str, model: str,
                 project_data: dict, image_bytes: bytes | None):
    system = analysis.build_prompt(load_prompt(), load_full(), load_kg())
    user_text = build_user_message(project_data)

    progress = st.status(f"🧠 วิเคราะห์ด้วย {provider.title()}...", expanded=True)
    progress.update(label="📚 โหลด Knowledge Graph")
    time.sleep(0.1)

    try:
        progress.update(label=f"🧠 เรียก AI · ~30-60 วินาที")
        t0 = time.time()
        if provider == "gemini":
            raw = llm.call_gemini(api_key, system, user_text, image_bytes, model)
        else:
            raw = llm.call_claude(api_key, system, user_text, image_bytes)
        elapsed = time.time() - t0

        progress.update(label=f"📊 parse · {len(raw):,} chars")
        parsed = analysis.extract_json(raw)
        progress.update(
            label=f"✅ เสร็จใน {elapsed:.1f} วิ" + (" (JSON)" if parsed else " (markdown fallback)"),
            state="complete", expanded=False,
        )

        # Save to session + history + bump quota
        st.session_state["result"] = parsed
        st.session_state["raw_text"] = raw
        st.session_state["project_data"] = project_data
        st.session_state["last_provider"] = provider
        history.add(project_data, raw, parsed, provider)
        tiers.increment_analysis()
        st.rerun()

    except Exception as e:
        progress.update(label=f"❌ ล้มเหลว: {e}", state="error", expanded=True)
        st.error(str(e))


def render_result():
    """Render the current analysis result"""
    data = st.session_state["result"]
    raw = st.session_state["raw_text"]
    pd = st.session_state["project_data"]
    provider = st.session_state["last_provider"]

    if not pd:
        return

    st.divider()
    st.header(f"📊 ผลวิเคราะห์ — {pd['name']}")
    st.caption(f"Provider: {provider.title()} · {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    if data:
        analysis.render(data)
    else:
        st.warning("⚠ AI ไม่ตอบเป็น JSON · แสดง markdown แทน")
        st.markdown(raw)

    # Save to Hub (Phase 1 · auto-save as case study)
    st.divider()
    _render_save_to_hub(pd, data, provider)

    # Share link (read-only URL for clients)
    st.divider()
    share.render_share_panel(pd, data, raw, provider)

    # Downloads
    st.divider()
    st.subheader("📥 ดาวน์โหลด")

    md_content = analysis.to_markdown(data) if data else (raw or "")
    full_md = f"""# ผลวิเคราะห์ — {pd['name']}

**วันที่:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Provider:** {provider.title()}

## ข้อมูลโครงการ

```json
{json.dumps(pd, ensure_ascii=False, indent=2)}
```

## ผลวิเคราะห์

{md_content}

---

*สร้างโดย สมองจำลองของสถาปนิก · ผลเบื้องต้น ไม่แทนสถาปนิก/วิศวกรใบอนุญาต*
"""

    ts = datetime.now().strftime("%Y%m%d-%H%M")
    c1, c2, c3 = st.columns(3)
    c1.download_button(
        "📥 Markdown (.md)", full_md,
        file_name=f"{pd['name']}-{ts}.md", mime="text/markdown",
        use_container_width=True,
    )
    if data:
        c2.download_button(
            "📋 JSON (.json)", json.dumps({
                "project_data": pd, "result": data, "provider": provider,
                "timestamp": datetime.now().isoformat(),
            }, ensure_ascii=False, indent=2),
            file_name=f"{pd['name']}-{ts}.json", mime="application/json",
            use_container_width=True,
        )
    c3.download_button(
        "📝 Raw AI output (.txt)", raw or "",
        file_name=f"{pd['name']}-{ts}-raw.txt", mime="text/plain",
        use_container_width=True,
    )

    # Print-ready exports (row 2)
    c4, c5 = st.columns(2)
    html_doc = export_pdf.build_print_html(pd, md_content, provider)
    c4.download_button(
        "🖨 HTML (พิมพ์ → PDF)", data=html_doc,
        file_name=f"{pd['name']}-{ts}.html", mime="text/html",
        use_container_width=True,
        help="เปิดใน browser แล้วกด Ctrl+P → Save as PDF (รองรับฟอนต์ไทย)",
    )
    if not tiers.can_use("pdf_export"):
        c5.button(
            "📄 PDF (🔒 Pro)", disabled=True, use_container_width=True,
            help="PDF export เป็น feature Pro · ดูแพ็กเกจที่แท็บ 💼 Pricing",
        )
    else:
        pdf_bytes, pdf_err = export_pdf.try_build_pdf_bytes(pd, md_content, provider)
        if pdf_bytes:
            c5.download_button(
                "📄 PDF (Sarabun)", data=pdf_bytes,
                file_name=f"{pd['name']}-{ts}.pdf", mime="application/pdf",
                use_container_width=True,
                help="Native PDF · ใช้ฟอนต์ Sarabun จากไฟล์ที่ shipped",
            )
        else:
            c5.button(
                "📄 PDF (ไม่พร้อม)", disabled=True, use_container_width=True,
                help=pdf_err or "PDF export ยังไม่พร้อม · ใช้ HTML แทน",
            )


def _render_save_to_hub(project_data: dict, result: dict | None, provider: str):
    """Phase 1: one-click save current analysis as a case contribution.

    Tracks which analyses have been sent via session_state to prevent duplicates
    on reruns. Auto-classifies category using heuristics in contribute._auto_classify.
    """
    # Build a stable key for this analysis (name + timestamp of the form submission)
    # Fall back to object id(project_data) if no timestamp available
    sig_parts = [
        project_data.get("name", ""),
        str(project_data.get("land_area", "")),
        str(project_data.get("budget", "")),
        (project_data.get("special") or "")[:40],
    ]
    sig = "|".join(sig_parts)
    saved_ids: dict = st.session_state.setdefault("_hub_saved", {})

    st.subheader("📤 ส่งเข้า Hub ของชุมชน")
    st.caption(
        "บันทึกเคสนี้ลง **กล่องรอเข้า** → ช่วยให้ AI ฉลาดขึ้นเมื่อรายงานผ่านการตรวจ · "
        "แก้ไข/ลบได้ที่แท็บ **💡 ช่วยเติม**"
    )

    if sig in saved_ids:
        entry_id = saved_ids[sig]
        st.success(f"✅ เคสนี้ส่งแล้ว · id `{entry_id}` · ดูในแท็บ **💡 ช่วยเติม**")
    else:
        auto_cat = contribute._auto_classify(project_data, result)
        cat_emoji, cat_name, _ = contribute.CATEGORIES[auto_cat]
        col_a, col_b = st.columns([3, 1])
        col_a.caption(
            f"จะถูกจัดเข้าหมวด **{cat_emoji} {cat_name}** โดยอัตโนมัติ · "
            "(เปลี่ยนทีหลังได้)"
        )
        if col_b.button("💾 ส่งเข้า Hub", use_container_width=True, key="hub_save_btn"):
            entry = contribute.save_analysis_as_case(project_data, result, provider)
            saved_ids[sig] = entry["id"]
            st.rerun()


def render_tabs_section(provider: str, api_key: str, model: str):
    """Secondary content below main flow · tabs"""
    st.divider()
    hist_count = len(history.get_all())
    contrib_count = len(contribute.get_all())
    img_count = len(st.session_state.get("generated_images", []))
    bk_count = len(booking.get_all())
    palette_count = len(materials.get_palette())
    tab_studio, tab_materials, tab_hist, tab_chat, tab_cmp, tab_contrib, tab_io, tab_mockup, tab_book, tab_price = st.tabs([
        f"🎨 Studio",
        f"🧵 วัสดุ ({palette_count})",
        f"📚 ประวัติ ({hist_count})",
        f"💬 Chat",
        f"🔀 เปรียบเทียบ",
        f"💡 ช่วยเติม ({contrib_count})",
        "💾 Save/Load",
        f"🖼 Mockup ({img_count})",
        f"📅 จองปรึกษา ({bk_count})",
        "💼 Pricing",
    ])
    with tab_studio:
        studio.render_panel()
    with tab_materials:
        materials.render_panel()
    with tab_hist:
        if hist_count == 0:
            st.info("🕐 ยังไม่มีประวัติ · วิเคราะห์โปรเจคแรกเพื่อเริ่มบันทึก")
        else:
            history.render_panel()
    with tab_chat:
        chat.render_panel(api_key, provider, model)
    with tab_cmp:
        compare.render_panel()
    with tab_contrib:
        contribute.render_panel()
    with tab_io:
        # Save/Load is a Pro feature · gate it
        if tiers.feature_gate("save_load", "Save/Load project JSON"):
            project_io.render_panel()
    with tab_mockup:
        # Image generation is a Pro feature · gate it
        if tiers.feature_gate("image_gen", "Image generation"):
            pd = st.session_state.get("project_data") or project_io._build_pd_from_form()
            image_gen.render_panel(pd, api_key, provider)
    with tab_book:
        booking.render_panel()
    with tab_price:
        tiers.render_pricing_panel()


# =============================================================================
# Main
# =============================================================================

def main():
    theme.inject()

    # Admin mode: ?admin=<token> takes priority over everything
    if admin.is_admin_mode():
        admin.render_panel()
        return

    # Share mode: if ?share=... is in URL, render read-only view instead
    if share.is_share_mode():
        share.render_view()
        return

    provider, api_key, model = render_sidebar()

    render_hero()

    # Welcome/onboarding when no api_key yet
    if not api_key:
        render_welcome_onboarding()
        st.divider()

    # Form + analyze
    project_data = render_form()

    st.divider()
    uploaded = st.file_uploader(
        "📎 แปลน (ไม่บังคับ · .jpg/.png)",
        type=["jpg", "jpeg", "png"],
        help="ถ้ามีแปลน · AI จะวิเคราะห์จาก layout ด้วย",
    )
    image_bytes = uploaded.getvalue() if uploaded else None
    if image_bytes:
        st.image(image_bytes, caption="แปลนที่จะส่ง", use_container_width=True)

    st.divider()
    if not api_key:
        st.info("👈 ใส่ API Key ที่ sidebar ก่อนเริ่ม")
    else:
        can_analyze, quota_err = tiers.check_quota()
        if not can_analyze:
            st.error(quota_err)
            if st.button("💎 ดูแพ็กเกจ Pro", use_container_width=True):
                # no real nav across tabs; user can scroll down to Pricing
                st.info("เปิดแท็บ **💼 Pricing** ด้านล่างเพื่อดูรายละเอียด")
        else:
            if st.button("🔍 วิเคราะห์โครงการ", type="primary", use_container_width=True):
                run_analysis(provider, api_key, model, project_data, image_bytes)

    # Show result if one exists
    if st.session_state.get("result") or st.session_state.get("raw_text"):
        render_result()

    # Secondary tools (history + chat + contribute + save/load + mockup)
    render_tabs_section(provider, api_key, model)


if __name__ == "__main__":
    main()
