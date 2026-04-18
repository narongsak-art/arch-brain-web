"""
สมองจำลองของสถาปนิก — Streamlit Web App
Thai Residential Architecture Analysis · 5-Layer Knowledge Graph

Supports: Google Gemini (free) and Anthropic Claude (paid)
Default: Gemini (no credit card required)

Run locally:  streamlit run app.py
Deploy:       streamlit.io (free tier)
"""

import base64
import json
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

from components import (
    theme,
    wizard,
    history,
    kg_explorer,
    compare,
    chat,
    presets,
    annotate,
    project_io,
    export_pdf,
    tiers,
    booking,
    structured_analysis,
    share,
    image_gen,
    draw_plan,
)
from components.progress import AnalysisProgress

# =============================================================================
# Configuration
# =============================================================================

st.set_page_config(
    page_title="สมองจำลองของสถาปนิก",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "สมองจำลองของสถาปนิก · AI + 5-Layer Knowledge Graph · Thai Residential Architecture"
    },
)

GEMINI_MODELS = {
    "gemini-2.5-flash": "🚀 Gemini 2.5 Flash (ล่าสุด · เร็ว)",
    "gemini-2.0-flash": "⚡ Gemini 2.0 Flash (stable · 1,500/วัน)",
    "gemini-1.5-flash": "📦 Gemini 1.5 Flash (legacy · backup)",
}
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8000

KG_FILE = Path(__file__).parent / "kg-compact.json"
SYSTEM_PROMPT_FILE = Path(__file__).parent / "system-prompt.md"
FULL_KNOWLEDGE_FILE = Path(__file__).parent / "full-knowledge.md"


# =============================================================================
# Knowledge base loaders
# =============================================================================

@st.cache_data
def load_knowledge_graph():
    if KG_FILE.exists():
        return KG_FILE.read_text(encoding="utf-8")
    return ""


@st.cache_data
def load_system_prompt():
    if SYSTEM_PROMPT_FILE.exists():
        return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    return "You are an architect's assistant."


@st.cache_data
def load_full_knowledge():
    if FULL_KNOWLEDGE_FILE.exists():
        return FULL_KNOWLEDGE_FILE.read_text(encoding="utf-8")
    return ""


# =============================================================================
# LLM Calls
# =============================================================================

def call_gemini(api_key, system, user_prompt, image_bytes=None, model=None):
    if model is None:
        model = st.session_state.get("gemini_model", DEFAULT_GEMINI_MODEL)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    combined = f"{system}\n\n---\n\n{user_prompt}"
    parts = [{"text": combined}]
    if image_bytes:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        parts.insert(0, {
            "inline_data": {"mime_type": "image/jpeg", "data": image_b64}
        })

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"maxOutputTokens": MAX_TOKENS, "temperature": 0.3},
    }
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    if "candidates" not in data or not data["candidates"]:
        raise Exception(f"No response from Gemini: {data}")
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_claude(api_key, system, user_prompt, image_bytes=None):
    try:
        import anthropic
    except ImportError:
        raise Exception("Anthropic library not installed. Install: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    content = [{"type": "text", "text": user_prompt}]
    if image_bytes:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        content.insert(0, {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64},
        })
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text


def analyze_project(provider, api_key, project_data, plan_image_bytes=None, progress=None, structured=True):
    """Orchestrate analysis with chosen provider + report stage progress.

    If structured=True, instruct LLM to return JSON; otherwise markdown.
    Returns: raw text (caller parses).
    """
    if progress:
        progress.advance("load_kb")
    kg = load_knowledge_graph()
    full_knowledge = load_full_knowledge()
    base_prompt = load_system_prompt()

    if progress:
        progress.advance("build_prompt", f"{len(kg):,} chars KG · {len(full_knowledge):,} chars knowledge")

    if structured:
        system = structured_analysis.build_structured_prompt(base_prompt, full_knowledge, kg)
    else:
        system = f"""{base_prompt}

## ⭐ FULL KNOWLEDGE (เนื้อหาเต็มหน้า wiki สำคัญ · ใช้อ้างอิงตัวเลขจริง)

{full_knowledge}

---

## Knowledge Graph Map (ภาพรวม 63 หน้า)

{kg}

---

⚠ สำคัญ: Cite ตัวเลขกฎหมายจาก FULL KNOWLEDGE ด้านบนเท่านั้น · ห้ามสร้างตัวเลขเองจากความจำของคุณ"""

    user_text = f"""ข้อมูลโครงการ:
- ชื่อ: {project_data['name']}
- ที่ดิน: {project_data['land_w']} × {project_data['land_d']} ม. ({project_data['land_area']:.0f} ตร.ม.)
- เขต: {project_data['zone']} · จังหวัด: {project_data['province']}
- ถนนติด: กว้าง {project_data['street_w']} ม.
- ครอบครัว: {project_data['family_size']} คน · ผู้สูงอายุ: {project_data['has_elderly']}
- ชั้น: {project_data['floors']} · ห้องนอน: {project_data['bedrooms']}
- งบ: {project_data['budget']} ล้านบาท
- ฮวงจุ้ย: {project_data['fengshui']}
- ความต้องการพิเศษ: {project_data['special']}

กรุณาวิเคราะห์:
1. **Feasibility** — FAR/OSR check · buildable area
2. **5-Layer Analysis** (กฎหมาย · วิศวกรรม · ออกแบบ · วัฒนธรรมไทย · ฮวงจุ้ย)
3. **Top 3 Issues** ที่ต้องแก้
4. **Top 3 Strengths** / โอกาส
5. **Next Actions** steps ที่แนะนำ
"""

    if progress:
        progress.advance("call_llm", f"{provider.title()} · ~30-60 วิ")

    if provider == "gemini":
        result = call_gemini(api_key, system, user_text, plan_image_bytes)
    elif provider == "claude":
        result = call_claude(api_key, system, user_text, plan_image_bytes)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    if progress:
        progress.advance("parse", f"{len(result):,} chars response")

    return result


# =============================================================================
# UI
# =============================================================================

def render_sidebar_tier_section():
    """Add tier badge + nav links to sidebar"""
    tiers.sidebar_tier_badge()
    st.sidebar.markdown("---")

    # Quick nav
    st.sidebar.markdown("### 🧭 Quick Nav")
    col1, col2 = st.sidebar.columns(2)
    if col1.button("💼 Pricing", use_container_width=True, key="nav_pricing"):
        st.switch_page("pages/1_💼_Pricing.py")
    if col2.button("📅 จองนัด", use_container_width=True, key="nav_book"):
        st.switch_page("pages/2_📅_Book_Consultation.py")

    col3, col4 = st.sidebar.columns(2)
    if col3.button("📊 ประวัติ", use_container_width=True, key="nav_history"):
        st.switch_page("pages/3_📊_History.py")
    if col4.button("🗺 KG", use_container_width=True, key="nav_kg"):
        st.switch_page("pages/4_🗺_KG_Explorer.py")

    st.sidebar.markdown("---")


def render_sidebar():
    st.sidebar.markdown(
        '<div style="padding:8px 0 16px 0;">'
        '<div style="font-size:1.2em;font-weight:800;letter-spacing:-0.01em;">🏠 สมองจำลอง</div>'
        '<div style="font-size:0.82em;color:var(--text-muted);margin-top:2px;">Architect\'s Brain · v2.0</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # Tier + Navigation
    render_sidebar_tier_section()

    st.sidebar.markdown("##### 🎨 ธีม")
    theme.theme_toggle(container=st.sidebar)
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### ⚙ การตั้งค่า AI")

    # Provider selector
    provider = st.sidebar.radio(
        "เลือก AI Provider",
        options=["gemini", "claude"],
        format_func=lambda x: {"gemini": "🆓 Google Gemini (ฟรี)", "claude": "💎 Claude (เสียเงิน)"}[x],
        index=0,
        help="Gemini ฟรี 1,500 ครั้ง/วัน · Claude คุณภาพสูงกว่า แต่เสียเงิน",
    )
    st.session_state["provider"] = provider

    if provider == "gemini":
        api_key = st.sidebar.text_input(
            "Gemini API Key",
            type="password",
            help="ฟรี · ไม่ต้องใส่ credit card · รับได้ที่ aistudio.google.com/apikey",
            value=st.session_state.get("gemini_key", ""),
            placeholder="AIza...",
        )
        st.session_state["gemini_key"] = api_key
        st.sidebar.caption("📎 [รับ Gemini API Key ฟรี](https://aistudio.google.com/apikey)")

        gemini_model = st.sidebar.selectbox(
            "Gemini Model",
            options=list(GEMINI_MODELS.keys()),
            format_func=lambda x: GEMINI_MODELS[x],
            index=0,
            help="ถ้าตัวใดเจอ rate limit · ลองเปลี่ยน",
        )
        st.session_state["gemini_model"] = gemini_model
    else:
        api_key = st.sidebar.text_input(
            "Claude API Key",
            type="password",
            help="ต้องเติม credit · $0.02-0.05/ครั้ง",
            value=st.session_state.get("claude_key", ""),
            placeholder="sk-ant-...",
        )
        st.session_state["claude_key"] = api_key
        st.sidebar.caption("📎 [สมัคร Claude API](https://console.anthropic.com)")

    st.sidebar.markdown("---")

    # Output format toggle
    st.sidebar.markdown("##### 📋 รูปแบบผลวิเคราะห์")
    structured_mode = st.sidebar.toggle(
        "✨ Structured output (ตาราง · charts)",
        value=st.session_state.get("structured_mode", True),
        help="เปิด: AI ตอบเป็น JSON → แสดงเป็นตาราง/charts/metrics · ปิด: markdown ธรรมดา",
        key="structured_mode_toggle",
    )
    st.session_state["structured_mode"] = structured_mode

    st.sidebar.markdown("---")

    # KG stats
    st.sidebar.markdown("### 📊 Knowledge Graph")
    try:
        kg_data = json.loads(load_knowledge_graph())
        meta = kg_data.get("meta", {})
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Nodes", meta.get("node_count", 0))
        col2.metric("Edges", meta.get("edge_count", 0))
    except Exception:
        st.sidebar.warning("KG not loaded")

    # History count
    hist_count = len(history.get_history())
    st.sidebar.caption(f"📚 ประวัติ: {hist_count} รายการ")

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
### 📖 5 ชั้นความรู้
- 🏛 **กฎหมาย** (พรบ 2522, กฎกระทรวง 55)
- 🔧 **วิศวกรรม** (MEP, โครงสร้าง)
- 🎨 **ออกแบบ** (passive, ergonomics)
- 🪷 **วัฒนธรรมไทย** (พระ, ศาลภูมิ)
- ☯ **ฮวงจุ้ย** (ทิศ, ประตู, เตียง)

⚠ ผลเป็นการวิเคราะห์เบื้องต้น · ไม่แทนสถาปนิก/วิศวกรใบอนุญาต

---
Built with ❤ for Thai architects
    """)
    return provider, api_key


def render_hero():
    st.markdown(
        """
        <div class="ab-hero">
            <div class="ab-hero-badge">✨ AI + Knowledge Graph</div>
            <h1>สมองจำลองของสถาปนิก</h1>
            <p class="tagline">วิเคราะห์แปลนบ้านไทยด้วย AI · รู้ลึก 5 มิติ · ใน 60 วินาที</p>
            <div class="subtagline">
                <span>🏛 กฎหมาย</span>
                <span>🔧 วิศวกรรม</span>
                <span>🎨 ออกแบบ</span>
                <span>🪷 วัฒนธรรมไทย</span>
                <span>☯ ฮวงจุ้ย</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_features():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="ab-card">'
            '<div class="ab-card-icon">🎯</div>'
            "<h4>ครอบคลุม · 5 ชั้นความรู้</h4>"
            "<p>32 concepts · 14 summaries · กฎหมายจริงทั้ง พรบ 2522 + กฎกระทรวง 55</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="ab-card">'
            '<div class="ab-card-icon">⚡</div>'
            "<h4>เร็ว · ได้ผลใน 60 วิ</h4>"
            "<p>Top 3 issues + strengths + next actions · ไม่ต้องรอสถาปนิกตอบ</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="ab-card">'
            '<div class="ab-card-icon">🔬</div>'
            "<h4>น่าเชื่อถือ · cite ทุกข้อ</h4>"
            "<p>ไม่สร้างตัวเลขเอง · verified จากต้นฉบับ 21 ไฟล์ · ตรวจที่มาย้อนกลับได้</p>"
            "</div>",
            unsafe_allow_html=True,
        )


def render_api_key_gate(provider):
    provider_name = "Gemini" if provider == "gemini" else "Claude"
    st.info(f"👈 กรุณาใส่ **{provider_name} API Key** ที่ sidebar ก่อนเริ่ม")
    if provider == "gemini":
        st.markdown("""
        ### 🆓 วิธีรับ Gemini API Key (ฟรี · 3 นาที)

        1. เปิด **[aistudio.google.com/apikey](https://aistudio.google.com/apikey)**
        2. Login ด้วย Google account
        3. คลิก **"Create API key"**
        4. Copy key · paste ที่ sidebar ซ้าย
        5. **ไม่ต้องใส่ credit card!**

        **Free tier:** 1,500 ครั้ง/วัน · พอสำหรับงานสถาปนิก 1 เดือน
        """)
    else:
        st.markdown("""
        ### 💎 วิธีรับ Claude API Key

        1. เปิด **[console.anthropic.com](https://console.anthropic.com)**
        2. สร้าง account · ต้องเติม credit ($5+)
        3. สร้าง API key · copy
        4. Paste ที่ sidebar

        **Cost:** ~$0.02-0.05/ครั้ง
        """)


def render_analyze_tab(provider, api_key):
    """Tab 1: wizard form + analysis"""
    if not api_key:
        render_api_key_gate(provider)
        return

    # Presets on first step only
    if st.session_state.get("wizard_step", 0) == 0:
        presets.render_preset_chips(on_apply=wizard.apply_preset)
        st.markdown("---")

    st.markdown("### 📝 ข้อมูลโครงการ")
    project_data, is_ready = wizard.render_wizard()

    # Plan upload + annotation (always visible)
    st.markdown("---")
    st.markdown("### 📎 อัปโหลดแปลน (ไม่บังคับ)")

    image_bytes = None
    drawn_bytes = st.session_state.get("_drawn_plan_bytes")
    if drawn_bytes:
        st.success("✅ ใช้แปลนที่วาดในแท็บ **🖊 วาดแปลน**")
        st.image(drawn_bytes, caption="แปลนที่วาดไว้", use_container_width=True)
        image_bytes = drawn_bytes
        col_clear, _ = st.columns([1, 3])
        if col_clear.button("🗑 ล้าง · ใช้ upload แทน", key="clear_drawn"):
            del st.session_state["_drawn_plan_bytes"]
            st.rerun()
    else:
        uploaded_file = st.file_uploader(
            "ภาพแปลน · screenshot",
            type=["jpg", "jpeg", "png"],
            help="ถ้า upload แปลน · AI จะวิเคราะห์จาก layout จริง · สามารถวาดมาร์คได้ · หรือไปแท็บ **🖊 วาดแปลน** เพื่อวาดสดๆ",
        )
        if uploaded_file:
            image_bytes = annotate.render_annotate_widget(uploaded_file)

    # Analyze button (only enabled on last step)
    st.markdown("---")
    if is_ready:
        # Check tier quota
        can_analyze, error_msg = tiers.check_analysis_quota()
        if not can_analyze:
            st.error(error_msg)
            col1, col2 = st.columns(2)
            if col1.button("💎 ดูแพ็กเกจ Pro", use_container_width=True):
                st.switch_page("pages/1_💼_Pricing.py")
            if col2.button("📅 จองปรึกษา", use_container_width=True):
                st.switch_page("pages/2_📅_Book_Consultation.py")
        else:
            if st.button("🔍 วิเคราะห์โครงการ", type="primary", use_container_width=True):
                tiers.increment_analysis()
                _run_analysis(provider, api_key, project_data, image_bytes)
    else:
        st.caption("💡 กรอกข้อมูลให้ครบทุกขั้นตอนเพื่อเริ่มวิเคราะห์")


def _run_analysis(provider, api_key, project_data, image_bytes):
    try:
        # Respect the user's output-mode toggle (structured JSON by default)
        structured = st.session_state.get("structured_mode", True)
        with AnalysisProgress(provider) as prog:
            analysis = analyze_project(
                provider, api_key, project_data, image_bytes,
                progress=prog, structured=structured,
            )
            prog.done(success=True)

        st.success(f"✅ วิเคราะห์เสร็จ (โดย {provider.title()})")

        # Try to parse structured JSON if that mode was selected
        parsed_data = None
        if structured:
            parsed_data = structured_analysis.extract_json_blob(analysis)

        history.add_to_history(project_data, analysis, provider, parsed_data)
        st.markdown("---")
        st.header("📊 ผลวิเคราะห์")
        if parsed_data:
            structured_analysis.render_analysis(parsed_data)
        else:
            if structured:
                st.warning("⚠ AI ไม่ตอบในรูปแบบ JSON · แสดงเป็น markdown")
            st.markdown(analysis)

        # Download
        st.markdown("---")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        report = f"""# ผลวิเคราะห์ — {project_data['name']}

**วันที่:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Provider:** {provider.title()}
**Knowledge Graph:** 63 nodes, 248 edges

## ข้อมูลโครงการ

```json
{json.dumps(project_data, ensure_ascii=False, indent=2)}
```

## ผลวิเคราะห์

{analysis}

---

*สร้างโดย สมองจำลองของสถาปนิก · Thai Residential Architecture Analysis*
*⚠ ผลเป็นการวิเคราะห์เบื้องต้น · ไม่แทนสถาปนิก/วิศวกรใบอนุญาต*
*การขออนุญาตก่อสร้างต้องมีลายเซ็นผู้ประกอบวิชาชีพ (พรบ.ควบคุมอาคาร 2522 มาตรา 49 ทวิ)*
"""
        col_md, col_html, col_pdf = st.columns(3)
        with col_md:
            st.download_button(
                "📥 .md",
                data=report,
                file_name=f"analysis-{project_data['name']}-{timestamp}.md",
                mime="text/markdown",
                use_container_width=True,
                help="Markdown (ใช้ใน Obsidian/Notion)",
            )
        with col_html:
            html_doc = export_pdf.build_print_html(project_data, analysis, provider)
            st.download_button(
                "🖨 .html (พิมพ์ → PDF)",
                data=html_doc,
                file_name=f"analysis-{project_data['name']}-{timestamp}.html",
                mime="text/html",
                use_container_width=True,
                help="เปิดใน browser แล้ว Ctrl+P เพื่อบันทึกเป็น PDF (รองรับฟอนต์ไทย)",
            )
        with col_pdf:
            pdf_bytes, pdf_err = export_pdf.try_build_pdf_bytes(project_data, analysis, provider)
            if pdf_bytes:
                st.download_button(
                    "📄 .pdf",
                    data=pdf_bytes,
                    file_name=f"analysis-{project_data['name']}-{timestamp}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    help="PDF โดยตรง (ใช้ฟอนต์ Sarabun)",
                )
            else:
                st.button(
                    "📄 .pdf (ไม่พร้อม)",
                    disabled=True,
                    use_container_width=True,
                    help=pdf_err or "PDF export ยังไม่พร้อม · ใช้ .html แทน",
                )

        # Share link (read-only URL to give to clients)
        st.markdown("---")
        share.render_share_button(project_data, parsed_data, analysis, provider)

        st.info("💾 ผลวิเคราะห์ถูกบันทึกไว้ที่แท็บ **📚 ประวัติ** แล้ว · ถามเพิ่มได้ที่แท็บ **💬 Chat**")

    except requests.HTTPError as e:
        st.error(f"❌ API Error: {e}")
        if "401" in str(e) or "403" in str(e):
            st.warning("API Key ผิด หรือยังไม่ activate")
        elif "429" in str(e):
            st.warning("Rate limit · รอ 1 นาทีแล้วลองใหม่ (Gemini free tier: 15 calls/min)")
    except Exception as e:
        st.error(f"❌ Error: {e}")


def render_footer():
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="ab-footer-card">'
            "<strong>🔒 Privacy</strong>"
            '<span style="color:var(--text-muted);font-size:0.88em;">ไม่เก็บข้อมูล · ไม่เทรน AI · session-based</span>'
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="ab-footer-card">'
            "<strong>⚖ Disclaimer</strong>"
            '<span style="color:var(--text-muted);font-size:0.88em;">วิเคราะห์เบื้องต้น · ต้องสถาปนิก/วิศวกรใบอนุญาตรับรอง</span>'
            "</div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="ab-footer-card">'
            "<strong>🛠 Built with</strong>"
            '<span style="color:var(--text-muted);font-size:0.88em;">Streamlit · Gemini · Claude · 64-page Wiki KG</span>'
            "</div>",
            unsafe_allow_html=True,
        )


# =============================================================================
# Main
# =============================================================================

def main():
    theme.inject_css()
    render_hero()

    provider, api_key = render_sidebar()

    render_features()
    st.markdown("---")

    tab_analyze, tab_draw, tab_history, tab_chat, tab_mockup, tab_compare, tab_io, tab_kg = st.tabs([
        "🔍 วิเคราะห์ใหม่",
        "🖊 วาดแปลน",
        "📚 ประวัติ",
        "💬 Chat",
        "🎨 ภาพ mockup",
        "🔀 เปรียบเทียบ",
        "💾 Save/Load",
        "🕸 KG Explorer",
    ])

    with tab_analyze:
        render_analyze_tab(provider, api_key)

    with tab_draw:
        fd = st.session_state.get("form_data", {})
        draw_plan.render_draw_tab(fd)

    with tab_history:
        history.render_history_panel()

    with tab_chat:
        # Provide a simple LLM dispatcher to chat module
        def _chat_llm(prov, key, system, user_text):
            if prov == "gemini":
                return call_gemini(key, system, user_text)
            return call_claude(key, system, user_text)

        chat.render_chat_panel(
            call_llm_fn=_chat_llm,
            provider=provider,
            api_key=api_key,
            base_prompt=load_system_prompt(),
            full_knowledge=load_full_knowledge(),
            kg=load_knowledge_graph(),
        )

    with tab_mockup:
        # Image generation uses the latest project in history (or wizard form as fallback)
        hist = history.get_history()
        if hist:
            fd = hist[0]["project_data"]
            st.caption(f"ใช้ข้อมูลจากโปรเจคล่าสุด: **{fd.get('name', '-')}**")
        else:
            fd = st.session_state.get("form_data", {})
            if fd:
                st.caption(f"ใช้ข้อมูลจากฟอร์มปัจจุบัน: **{fd.get('name', '-')}** · วิเคราะห์ก่อนจะได้ข้อมูลจริง")
            else:
                st.info("กรอกฟอร์มที่แท็บ **วิเคราะห์ใหม่** ก่อน เพื่อให้ AI มี brief สร้างภาพ")
        if fd:
            image_gen.render_image_gen_panel(fd, api_key if provider == "gemini" else "")
            if provider != "gemini":
                st.warning("Image generation ใช้ Gemini API เท่านั้น · สลับ provider ที่ sidebar")

    with tab_compare:
        compare.render_compare_panel()

    with tab_io:
        project_io.render_io_panel()

    with tab_kg:
        kg_explorer.render_kg_explorer()

    render_footer()


if __name__ == "__main__":
    main()
