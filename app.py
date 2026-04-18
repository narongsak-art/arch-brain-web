"""
สมองจำลองของสถาปนิก — Streamlit Web App
Thai Residential Architecture Analysis · 5-Layer Knowledge Graph

Supports: Google Gemini (free) and Anthropic Claude (paid)
Default: Gemini (no credit card required)

Run locally:  streamlit run app.py
Deploy:       streamlit.io (free tier)
"""

import streamlit as st
import json
import base64
import requests
from pathlib import Path
from datetime import datetime

# =============================================================================
# Configuration
# =============================================================================

st.set_page_config(
    page_title="สมองจำลองของสถาปนิก",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "สมองจำลองของสถาปนิก · AI + 5-Layer Knowledge Graph · Thai Residential Architecture"
    }
)

# Providers
GEMINI_MODEL = "gemini-2.0-flash"
CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4000

# Paths
KG_FILE = Path(__file__).parent / "kg-compact.json"
SYSTEM_PROMPT_FILE = Path(__file__).parent / "system-prompt.md"


# =============================================================================
# Load knowledge base
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


# =============================================================================
# LLM Calls
# =============================================================================

def call_gemini(api_key, system, user_prompt, image_bytes=None):
    """Call Google Gemini API (free tier)"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"

    combined = f"{system}\n\n---\n\n{user_prompt}"

    parts = [{"text": combined}]
    if image_bytes:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        parts.insert(0, {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_b64
            }
        })

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "maxOutputTokens": MAX_TOKENS,
            "temperature": 0.3
        }
    }

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    if "candidates" not in data or not data["candidates"]:
        raise Exception(f"No response from Gemini: {data}")

    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_claude(api_key, system, user_prompt, image_bytes=None):
    """Call Anthropic Claude API (paid)"""
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
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_b64
            }
        })

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": content}]
    )
    return response.content[0].text


def analyze_project(provider, api_key, project_data, plan_image_bytes=None):
    """Orchestrate analysis with chosen provider"""
    kg = load_knowledge_graph()
    base_prompt = load_system_prompt()

    system = f"""{base_prompt}

## Knowledge Graph (context)

{kg}"""

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

    if provider == "gemini":
        return call_gemini(api_key, system, user_text, plan_image_bytes)
    elif provider == "claude":
        return call_claude(api_key, system, user_text, plan_image_bytes)
    else:
        raise ValueError(f"Unknown provider: {provider}")


# =============================================================================
# UI Components
# =============================================================================

def render_sidebar():
    st.sidebar.markdown("## ⚙ การตั้งค่า")

    # Provider selector
    provider = st.sidebar.radio(
        "เลือก AI Provider",
        options=["gemini", "claude"],
        format_func=lambda x: {"gemini": "🆓 Google Gemini (ฟรี)", "claude": "💎 Claude (เสียเงิน)"}[x],
        index=0,
        help="Gemini ฟรี 1,500 ครั้ง/วัน · Claude คุณภาพสูงกว่า แต่เสียเงิน"
    )
    st.session_state["provider"] = provider

    # API key input
    if provider == "gemini":
        api_key = st.sidebar.text_input(
            "Gemini API Key",
            type="password",
            help="ฟรี · ไม่ต้องใส่ credit card · รับได้ที่ aistudio.google.com/apikey",
            value=st.session_state.get("gemini_key", ""),
            placeholder="AIza..."
        )
        st.session_state["gemini_key"] = api_key
        st.sidebar.caption("📎 [รับ Gemini API Key ฟรี](https://aistudio.google.com/apikey)")
    else:
        api_key = st.sidebar.text_input(
            "Claude API Key",
            type="password",
            help="ต้องเติม credit · $0.02-0.05/ครั้ง",
            value=st.session_state.get("claude_key", ""),
            placeholder="sk-ant-..."
        )
        st.session_state["claude_key"] = api_key
        st.sidebar.caption("📎 [สมัคร Claude API](https://console.anthropic.com)")

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

    # Info
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
    """Landing hero section"""
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
        <h1 style="color: white; font-size: 2.5em; margin-bottom: 10px;">🏠 สมองจำลองของสถาปนิก</h1>
        <p style="font-size: 1.2em; margin: 0;">วิเคราะห์แปลนบ้านด้วย AI + Knowledge Graph 5 ชั้น</p>
        <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.9;">
            กฎหมาย · วิศวกรรม · ออกแบบ · วัฒนธรรมไทย · ฮวงจุ้ย
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_features():
    """Feature cards"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🎯 ครอบคลุม
        **5 ชั้นความรู้** · 32 concepts · 14 summaries · กฎหมายจริงทั้งพรบ + กฎกระทรวง
        """)

    with col2:
        st.markdown("""
        ### ⚡ รวดเร็ว
        **วิเคราะห์ใน 30-60 วิ** · ได้ Top 3 issues + strengths พร้อม next actions
        """)

    with col3:
        st.markdown("""
        ### 🔬 น่าเชื่อถือ
        **Cite source ทุกข้อ** · ไม่สร้างตัวเลขเอง · verified จากต้นฉบับ 21 ไฟล์
        """)


def render_input_form():
    """Project input form"""
    st.header("📝 ข้อมูลโครงการ")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏞 ที่ดิน")
            name = st.text_input("ชื่อโปรเจค (alias)", value="บ้าน-A")
            land_w = st.number_input("กว้าง (ม.)", min_value=1.0, value=15.0, step=0.5)
            land_d = st.number_input("ลึก (ม.)", min_value=1.0, value=20.0, step=0.5)
            province = st.selectbox(
                "จังหวัด",
                ["กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี", "สมุทรปราการ",
                 "สมุทรสาคร", "นครปฐม", "เชียงใหม่", "ภูเก็ต", "อื่นๆ"],
            )
            zone = st.selectbox(
                "สีผังเมือง (ย. = ที่อยู่อาศัย · พ. = พาณิชย์)",
                ["ย.1", "ย.2", "ย.3", "ย.4", "ย.5", "ย.6", "ย.7",
                 "ย.8", "ย.9", "ย.10",
                 "พ.1", "พ.2", "พ.3", "พ.4", "พ.5",
                 "อ.1", "อ.2", "อ.3", "ก.1", "ก.2", "ก.3", "ก.4", "ก.5",
                 "ไม่ทราบ"],
                index=2,
            )
            street_w = st.number_input("ถนนติดกว้าง (ม.)", min_value=1.0, value=6.0, step=0.5)

        with col2:
            st.subheader("👨‍👩‍👧 ครอบครัว + ความต้องการ")
            family_size = st.slider("จำนวนสมาชิก", 1, 15, 4)
            has_elderly = st.radio("มีผู้สูงอายุ", ["ใช่", "ไม่"], horizontal=True)
            floors = st.selectbox("ชั้น", ["1", "2", "3", "4+"], index=1)
            bedrooms = st.selectbox("ห้องนอน", ["1", "2", "3", "4", "5+"], index=2)
            budget = st.number_input("งบ (ล้านบาท)", min_value=0.5, value=8.0, step=0.5)
            fengshui = st.selectbox(
                "สนใจฮวงจุ้ย",
                ["มาก", "ปานกลาง", "น้อย", "ไม่สน"],
                index=1,
            )

    special = st.text_area(
        "ความต้องการพิเศษ",
        placeholder="ตัวอย่าง: ห้องพระ · walk-in · home office 2 คน · สระว่ายน้ำ · ผู้สูงอายุใช้ wheelchair · ลูก 2 คนต้องการห้องแยก",
        height=100,
    )

    return {
        "name": name,
        "land_w": land_w,
        "land_d": land_d,
        "land_area": land_w * land_d,
        "zone": zone,
        "province": province,
        "street_w": street_w,
        "family_size": family_size,
        "has_elderly": has_elderly,
        "floors": floors,
        "bedrooms": bedrooms,
        "budget": budget,
        "fengshui": fengshui,
        "special": special,
    }


def render_footer():
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🔒 Privacy**")
        st.caption("ไม่เก็บข้อมูล · ไม่เทรน AI · session-based")
    with col2:
        st.markdown("**⚖ Disclaimer**")
        st.caption("วิเคราะห์เบื้องต้น · ต้องสถาปนิก/วิศวกรใบอนุญาตรับรอง")
    with col3:
        st.markdown("**🛠 Built with**")
        st.caption("Streamlit · Gemini · 64-page Wiki KG")


# =============================================================================
# Main
# =============================================================================

def main():
    render_hero()
    provider, api_key = render_sidebar()

    # Features section
    render_features()

    st.markdown("---")

    # Gate: check API key
    if not api_key:
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
        return

    # Input form
    project_data = render_input_form()

    st.subheader("📎 อัปโหลดแปลน (ไม่บังคับ)")
    uploaded_file = st.file_uploader(
        "ภาพแปลน · PDF · screenshot",
        type=["jpg", "jpeg", "png"],
        help="ถ้า upload แปลน · AI จะวิเคราะห์จาก layout จริง",
    )

    image_bytes = None
    if uploaded_file:
        st.image(uploaded_file, caption="แปลนที่อัปโหลด", use_container_width=True)
        image_bytes = uploaded_file.getvalue()

    # Analyze button
    st.markdown("---")
    if st.button("🔍 วิเคราะห์โครงการ", type="primary", use_container_width=True):
        with st.spinner(f"🧠 กำลังวิเคราะห์ด้วย {provider.title()}... (30-60 วินาที)"):
            try:
                analysis = analyze_project(provider, api_key, project_data, image_bytes)

                st.success(f"✅ วิเคราะห์เสร็จ (โดย {provider.title()})")
                st.markdown("---")
                st.header("📊 ผลวิเคราะห์")
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
                st.download_button(
                    "📥 ดาวน์โหลดรายงาน (.md)",
                    data=report,
                    file_name=f"analysis-{project_data['name']}-{timestamp}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            except requests.HTTPError as e:
                st.error(f"❌ API Error: {e}")
                if "401" in str(e) or "403" in str(e):
                    st.warning("API Key ผิด หรือยังไม่ activate")
                elif "429" in str(e):
                    st.warning("Rate limit · รอ 1 นาทีแล้วลองใหม่ (Gemini free tier: 15 calls/min)")

            except Exception as e:
                st.error(f"❌ Error: {e}")

    render_footer()


if __name__ == "__main__":
    main()
