"""
สมองจำลองของสถาปนิก · v5-beta
Thai Architect's Studio · drafted.ai-inspired minimal rebuild

3 views only: Create · My Studio · Explore
No tabs madness · no feature sprawl · focused flow.
"""

import streamlit as st

from core import theme, llm
from views import create, studio, explore


# =============================================================================
# Page config
# =============================================================================

st.set_page_config(
    page_title="สมองจำลอง · Thai Architect's Studio",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Sidebar (minimal · brand + AI config + view switcher)
# =============================================================================

def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div style="padding: 6px 0 14px 0;">'
            '<div class="eyebrow">THAI STUDIO</div>'
            '<div style="font-family: var(--font-display); font-size: 1.25em; '
            'font-weight: 700; color: var(--ink);">สมองจำลอง</div>'
            '<div style="font-size: 0.8em; color: var(--muted);">ของสถาปนิก · v5</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        # View switcher (replaces tabs)
        view = st.radio(
            "View",
            options=["create", "studio", "explore"],
            format_func=lambda v: {
                "create":  "🎨 Create",
                "studio":  "📚 My Studio",
                "explore": "🌐 Explore",
            }[v],
            label_visibility="collapsed",
            key="_view",
        )

        st.divider()

        # AI settings
        st.caption("**AI**")
        provider = st.radio(
            "Provider",
            options=["gemini", "claude"],
            format_func=lambda x: {"gemini": "🆓 Gemini (ฟรี)",
                                    "claude": "💎 Claude"}[x],
            horizontal=True,
            label_visibility="collapsed",
            key="_provider",
        )

        if provider == "gemini":
            api_key = st.text_input(
                "Gemini API Key", type="password",
                placeholder="AIza...", key="_gemini_key",
            )
            st.caption("📎 [รับ Gemini ฟรี](https://aistudio.google.com/apikey)")
            model = st.selectbox(
                "Model",
                options=list(llm.GEMINI_MODELS.keys()),
                format_func=lambda x: llm.GEMINI_MODELS[x],
                key="_gemini_model",
            )
        else:
            api_key = st.text_input(
                "Claude API Key", type="password",
                placeholder="sk-ant-...", key="_claude_key",
            )
            st.caption("📎 [สมัคร Claude](https://console.anthropic.com)")
            model = "claude-sonnet-4-6"

        st.divider()

        # Stats footer
        hist_count = len(st.session_state.get("history", []))
        st.caption(f"📚 ประวัติ session: **{hist_count}** รายการ")
        st.caption(
            "⚠ ผลเบื้องต้น · ไม่แทนสถาปนิก/วิศวกรใบอนุญาต\n\n"
            "[ADMIN.md](https://github.com/narongsak-art/arch-brain-web/blob/v5-beta/ADMIN.md)"
        )

    return view, provider, api_key, model


# =============================================================================
# Main
# =============================================================================

def main():
    theme.inject()
    view, provider, api_key, model = render_sidebar()

    if view == "create":
        create.render(provider, api_key, model)
    elif view == "studio":
        studio.render()
    elif view == "explore":
        explore.render()


if __name__ == "__main__":
    main()
