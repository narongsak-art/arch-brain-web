"""
สมองจำลองของสถาปนิก · v5-beta
Thai Architect's Studio · sidebar-for-inputs · main-for-outputs

Navigation:
- Sidebar · view switcher + all inputs (AI config + project form)
- Main area · only renders the current view's OUTPUT
"""

import streamlit as st

from core import theme, llm
from views import create, studio, explore


st.set_page_config(
    page_title="สมองจำลอง · Thai Architect's Studio",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Sidebar shell · brand · view switcher · AI config
# =============================================================================

def render_sidebar_shell():
    """Top of sidebar · brand + view switcher + AI settings
    Returns (view, provider, api_key, model)
    """
    with st.sidebar:
        # Brand
        st.markdown(
            '<div style="padding: 6px 0 14px 0;">'
            '<div class="eyebrow">THAI STUDIO</div>'
            '<div style="font-family: var(--font-display); font-size: 1.25em; '
            'font-weight: 700; color: var(--ink);">สมองจำลอง</div>'
            '<div style="font-size: 0.8em; color: var(--muted);">ของสถาปนิก · v5</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # View switcher
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

        # AI section · open only if key missing (onboarding hint)
        key_present = bool(st.session_state.get("_gemini_key") or st.session_state.get("_claude_key"))
        with st.expander("⚙ AI Settings", expanded=not key_present):
            provider = st.radio(
                "Provider",
                options=["gemini", "claude"],
                format_func=lambda x: {"gemini": "🆓 Gemini (ฟรี)",
                                        "claude": "💎 Claude"}[x],
                horizontal=True,
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

    return view, provider, api_key, model


def render_sidebar_footer():
    """Bottom of sidebar · stats + disclaimer"""
    with st.sidebar:
        st.divider()
        hist_count = len(st.session_state.get("history", []))
        st.caption(f"📚 ประวัติ session: **{hist_count}** รายการ")
        st.caption(
            "⚠ ผลเบื้องต้น · ไม่แทนสถาปนิก/วิศวกรใบอนุญาต"
        )


# =============================================================================
# Main
# =============================================================================

def main():
    theme.inject()
    view, provider, api_key, model = render_sidebar_shell()

    if view == "create":
        # Form lives inside sidebar · main area is output-only
        project_data, image_bytes = create.render_sidebar_form(provider, api_key, model)
        render_sidebar_footer()
        create.render_main(provider, api_key, model, project_data, image_bytes)

    elif view == "studio":
        render_sidebar_footer()
        studio.render()

    elif view == "explore":
        render_sidebar_footer()
        explore.render()


if __name__ == "__main__":
    main()
