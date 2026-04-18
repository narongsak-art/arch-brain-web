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

from components import theme, llm, analysis, presets


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
    st.markdown(
        """
        <div class="ab-hero">
          <h1>🏠 สมองจำลองของสถาปนิก</h1>
          <p>วิเคราะห์แปลนบ้านไทยด้วย AI + Knowledge Graph 5 ชั้น · ผลใน ~60 วินาที</p>
        </div>
        """,
        unsafe_allow_html=True,
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

        # Save to session
        st.session_state["result"] = parsed
        st.session_state["raw_text"] = raw
        st.session_state["project_data"] = project_data
        st.session_state["last_provider"] = provider
        # Prepend to history
        st.session_state["history"].insert(0, {
            "ts": datetime.now().isoformat(),
            "name": project_data["name"],
            "provider": provider,
            "project_data": project_data,
            "result": parsed,
            "raw_text": raw,
        })
        # Keep only 20 entries
        st.session_state["history"] = st.session_state["history"][:20]
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


def render_history():
    """Past analyses in current session"""
    hist = st.session_state["history"]
    if not hist:
        return
    st.divider()
    with st.expander(f"📚 ประวัติ session นี้ ({len(hist)})", expanded=False):
        for i, h in enumerate(hist):
            ts = datetime.fromisoformat(h["ts"]).strftime("%H:%M")
            cols = st.columns([4, 1])
            cols[0].markdown(f"**{h['name']}** · _{h['provider']}_ · {ts}")
            if cols[1].button("🔄 โหลด", key=f"hist_load_{i}", use_container_width=True):
                st.session_state["result"] = h["result"]
                st.session_state["raw_text"] = h["raw_text"]
                st.session_state["project_data"] = h["project_data"]
                st.session_state["last_provider"] = h["provider"]
                st.rerun()


# =============================================================================
# Main
# =============================================================================

def main():
    theme.inject()
    provider, api_key, model = render_sidebar()

    render_hero()

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
        if st.button("🔍 วิเคราะห์โครงการ", type="primary", use_container_width=True):
            run_analysis(provider, api_key, model, project_data, image_bytes)

    # Show result if one exists
    if st.session_state.get("result") or st.session_state.get("raw_text"):
        render_result()

    # History
    render_history()


if __name__ == "__main__":
    main()
