"""
🗺 Knowledge Graph Explorer · ดูโครงสร้างความรู้ทั้งหมด
"""

import streamlit as st
from components import theme, tiers, kg_explorer

st.set_page_config(
    page_title="KG Explorer · สมองจำลองของสถาปนิก",
    page_icon="🗺",
    layout="wide",
)

theme.apply_theme()

st.title("🗺 Knowledge Graph Explorer")
st.caption(
    "ดูฐานความรู้ทั้งหมดที่ AI ใช้ในการวิเคราะห์ · เลือก node เพื่อดูรายละเอียด"
)

st.markdown("---")

try:
    kg_explorer.render_explorer()
except AttributeError:
    # Fallback basic explorer
    import json
    from pathlib import Path

    kg_file = Path(__file__).parent.parent / "kg-compact.json"
    if kg_file.exists():
        kg = json.loads(kg_file.read_text(encoding="utf-8"))

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nodes", kg["meta"]["node_count"])
        col2.metric("Edges", kg["meta"]["edge_count"])
        col3.metric("Layers", len(kg["meta"]["layers"]))
        col4.metric("Domain", "Thai Residential")

        st.markdown("---")

        # Filter
        layers = ["all"] + kg["meta"]["layers"]
        selected_layer = st.selectbox("Filter by layer", layers)

        types = ["all"] + sorted(set(n["type"] for n in kg["nodes"]))
        selected_type = st.selectbox("Filter by type", types)

        filtered = kg["nodes"]
        if selected_layer != "all":
            filtered = [n for n in filtered if selected_layer in (n.get("layers") or [])]
        if selected_type != "all":
            filtered = [n for n in filtered if n["type"] == selected_type]

        st.markdown(f"### 📄 {len(filtered)} nodes")
        for node in filtered:
            with st.expander(f"**{node['title']}** · {node['type']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    if node.get("summary"):
                        st.markdown(node["summary"])
                with col2:
                    st.caption("Layers:")
                    for layer in node.get("layers", []):
                        st.caption(f"• {layer}")

                if node.get("sources"):
                    st.caption("📚 Sources:")
                    for src in node["sources"]:
                        st.caption(f"- {src}")
    else:
        st.error("KG file not found")

# Sidebar
with st.sidebar:
    theme.theme_toggle()
    st.markdown("---")
    tiers.sidebar_tier_badge()
