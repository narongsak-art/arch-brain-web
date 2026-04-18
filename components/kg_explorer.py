"""KG Explorer · visual graph of 104 nodes / 425 edges"""

import json
import streamlit as st
from pathlib import Path

KG_FILE = Path(__file__).parent.parent / "kg-compact.json"

LAYER_COLORS = {
    "law": "#ef4444",
    "eng": "#3b82f6",
    "design": "#10b981",
    "thai": "#f59e0b",
    "fengshui": "#a855f7",
}
LAYER_LABELS = {
    "law": "🏛 กฎหมาย",
    "eng": "🔧 วิศวกรรม",
    "design": "🎨 ออกแบบ",
    "thai": "🪷 วัฒนธรรมไทย",
    "fengshui": "☯ ฮวงจุ้ย",
}
TYPE_SHAPE = {
    "concept": "dot",
    "summary": "square",
    "synthesis": "diamond",
    "entity": "triangle",
}


@st.cache_data
def _load_kg():
    if not KG_FILE.exists():
        return None
    with open(KG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _short_label(title: str, max_len: int = 30) -> str:
    return title if len(title) <= max_len else title[:max_len].rstrip() + "…"


def _primary_layer(layers: list) -> str:
    if not layers:
        return "design"
    priority = ["law", "eng", "design", "thai", "fengshui"]
    for p in priority:
        if p in layers:
            return p
    return layers[0]


def render_kg_explorer():
    """Render the KG Explorer tab"""
    kg = _load_kg()
    if kg is None:
        st.error("❌ ไม่พบ kg-compact.json")
        return

    meta = kg.get("meta", {})
    nodes = kg.get("nodes", [])
    edges = kg.get("edges", [])

    st.markdown(f"### 🕸 Knowledge Graph Explorer")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nodes", meta.get("node_count", len(nodes)))
    col2.metric("Edges", meta.get("edge_count", len(edges)))
    col3.metric("Layers", len(meta.get("layers", [])))
    verified = sum(1 for n in nodes if n.get("source_status") == "verified")
    col4.metric("Verified", verified)

    st.markdown("---")

    with st.expander("🎛 ตัวกรอง (filter)", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            selected_layers = st.multiselect(
                "ชั้นความรู้ (เลือกได้หลายชั้น)",
                options=list(LAYER_LABELS.keys()),
                default=list(LAYER_LABELS.keys()),
                format_func=lambda x: LAYER_LABELS[x],
            )
        with col_b:
            types = sorted(set(n.get("type", "concept") for n in nodes))
            selected_types = st.multiselect(
                "ประเภท node",
                options=types,
                default=types,
            )

        search = st.text_input("🔎 ค้นหาชื่อ (title contains)", value="")

    # Filter nodes
    def _keep(n):
        layers = n.get("layers", [])
        if not any(l in selected_layers for l in layers):
            return False
        if n.get("type", "concept") not in selected_types:
            return False
        if search and search.lower() not in n.get("title", "").lower():
            return False
        return True

    filtered_nodes = [n for n in nodes if _keep(n)]
    node_ids = {n["id"] for n in filtered_nodes}
    filtered_edges = [e for e in edges if e.get("from") in node_ids and e.get("to") in node_ids]

    st.caption(f"แสดง **{len(filtered_nodes)}** nodes · **{len(filtered_edges)}** edges")

    # Render graph
    try:
        from streamlit_agraph import agraph, Node, Edge, Config

        agraph_nodes = []
        for n in filtered_nodes:
            primary = _primary_layer(n.get("layers", []))
            agraph_nodes.append(Node(
                id=n["id"],
                label=_short_label(n.get("title", n["id"])),
                size=14 if n.get("type") == "concept" else 10,
                color=LAYER_COLORS.get(primary, "#888"),
                shape=TYPE_SHAPE.get(n.get("type", "concept"), "dot"),
                title=f"{n.get('title','')}\n\n{n.get('summary','')}",
            ))

        agraph_edges = [
            Edge(source=e["from"], target=e["to"], type="CURVE_SMOOTH")
            for e in filtered_edges
        ]

        config = Config(
            width="100%",
            height=620,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            collapsible=False,
        )
        agraph(nodes=agraph_nodes, edges=agraph_edges, config=config)

    except ImportError:
        st.warning(
            "⚠ ยังไม่ได้ติดตั้ง `streamlit-agraph` · แสดงเป็นรายการแทน\n\n"
            "ติดตั้ง: `pip install streamlit-agraph`"
        )
        _render_list_fallback(filtered_nodes)

    st.markdown("---")
    st.markdown("### 🎨 รหัสสี")
    legend_cols = st.columns(len(LAYER_COLORS))
    for i, (layer, color) in enumerate(LAYER_COLORS.items()):
        with legend_cols[i]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'<span style="width:14px;height:14px;border-radius:50%;background:{color};display:inline-block;"></span>'
                f"<span>{LAYER_LABELS[layer]}</span></div>",
                unsafe_allow_html=True,
            )


def _render_list_fallback(nodes: list):
    """Fallback list view if streamlit-agraph unavailable"""
    for n in nodes[:50]:
        layers_badges = " ".join(
            f'<span style="background:{LAYER_COLORS.get(l,"#888")};color:#fff;padding:2px 8px;border-radius:10px;font-size:0.75em;">{LAYER_LABELS.get(l,l)}</span>'
            for l in n.get("layers", [])
        )
        st.markdown(
            f"**{n.get('title', n['id'])}** {layers_badges}  \n"
            f"<span style='color:#888;font-size:0.88em;'>{n.get('summary','')[:180]}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
    if len(nodes) > 50:
        st.caption(f"...และอีก {len(nodes)-50} node")
