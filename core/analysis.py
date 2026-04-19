"""Structured analysis · prompt builder + JSON parser + renderer + md export"""

import json
import re
from pathlib import Path

import streamlit as st


REPO = Path(__file__).parent.parent


# ============================================================================
# Knowledge loaders
# ============================================================================

@st.cache_data
def load_kg() -> str:
    p = REPO / "kg-compact.json"
    return p.read_text(encoding="utf-8") if p.exists() else ""


@st.cache_data
def load_full_knowledge() -> str:
    p = REPO / "full-knowledge.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


@st.cache_data
def load_base_prompt() -> str:
    p = REPO / "system-prompt.md"
    return p.read_text(encoding="utf-8") if p.exists() else (
        "You are an architect's assistant for Thai residential design."
    )


# ============================================================================
# Prompt
# ============================================================================

OUTPUT_SCHEMA = """
ตอบเป็น JSON ล้วน · เริ่มด้วย { จบด้วย } · ห้าม markdown

{
  "summary": {
    "feasibility": "green|yellow|red",
    "note": "1-2 ประโยค",
    "score": 0-100,
    "concern": "ประเด็นหลัก 1 ข้อ",
    "strength": "จุดเด่น 1 ข้อ"
  },
  "metrics": {
    "land_area_sqm": number, "buildable_area_sqm": number,
    "far_allowed": number, "far_estimated": number,
    "osr_required_pct": number,
    "setback_front_m": number, "setback_side_m": number, "setback_back_m": number,
    "max_height_m": number, "floor_area_sqm": number, "cost_mbaht": number
  },
  "layers": {
    "law": {"status":"pass|warning|fail", "score":0-100, "findings":[{"severity":"critical|warning|info","title":"","detail":"","citation":""}]},
    "eng": {...}, "design": {...}, "thai": {...}, "fengshui": {...}
  },
  "rooms": [{"name":"","type":"bedroom|kitchen|bathroom|living|prayer|other",
             "size_min":0,"size_max":0,"orientation":"","thai_note":null,"fengshui_note":null,
             "points":["..."],"issues":[]}],
  "issues":[{"rank":1,"severity":"high|medium|low","title":"","detail":"","action":""}],
  "strengths":[{"rank":1,"title":"","detail":""}],
  "actions":[{"step":1,"action":"","who":"สถาปนิก|วิศวกร|เจ้าของ","when":"ก่อนออกแบบ|ก่อนก่อสร้าง|หลัง"}],
  "confidence":"high|medium|low",
  "caveats":["..."]
}

กฎ:
- rooms อย่างน้อย 6 ห้อง
- issues + strengths อย่างน้อย 3 ต่ออัน
- ตัวเลขกฎหมาย: cite จาก FULL KNOWLEDGE · ถ้าไม่แน่ใจใส่ null
"""


def build_system_prompt() -> str:
    return f"""{load_base_prompt()}

## ⭐ FULL KNOWLEDGE
{load_full_knowledge()}

---

## Knowledge Graph
{load_kg()}

---

⚠ Cite ตัวเลขกฎหมายจาก FULL KNOWLEDGE เท่านั้น

{OUTPUT_SCHEMA}
"""


def build_user_prompt(project_data: dict) -> str:
    pd = project_data
    return f"""ข้อมูลโครงการ:
- ชื่อ: {pd.get('name', '-')}
- ที่ดิน: {pd.get('land_w', '-')} × {pd.get('land_d', '-')} ม. ({pd.get('land_area', 0):.0f} ตร.ม.)
- เขต: {pd.get('zone', '-')} · จังหวัด: {pd.get('province', '-')}
- ถนนติด: {pd.get('street_w', '-')} ม.
- ครอบครัว: {pd.get('family_size', '-')} คน · ผู้สูงอายุ: {pd.get('has_elderly', '-')}
- ชั้น: {pd.get('floors', '-')} · ห้องนอน: {pd.get('bedrooms', '-')}
- งบ: {pd.get('budget', '-')} ล้านบาท
- ฮวงจุ้ย: {pd.get('fengshui', '-')}
- ข้อพิเศษ: {pd.get('special', '-')}

วิเคราะห์เป็น structured JSON ตาม schema ด้านบน
"""


# ============================================================================
# Parser
# ============================================================================

def extract_json(text: str) -> dict | None:
    if not text:
        return None
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except Exception:
                    return None
    return None


# ============================================================================
# Renderer
# ============================================================================

FEAS = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
STATUS = {"pass": "✅", "warning": "⚠", "fail": "❌"}
SEV = {"critical": "🚨", "high": "🔴", "warning": "⚠", "medium": "🟡",
       "low": "🟢", "info": "ℹ"}
LAYERS = [
    ("law", "🏛", "กฎหมาย"),
    ("eng", "🔧", "วิศวกรรม"),
    ("design", "🎨", "ออกแบบ"),
    ("thai", "🪷", "วัฒนธรรมไทย"),
    ("fengshui", "☯", "ฮวงจุ้ย"),
]


def render(data: dict):
    _summary(data.get("summary", {}))
    st.divider()
    _metrics(data.get("metrics", {}))
    st.divider()
    _layers(data.get("layers", {}))
    rooms = data.get("rooms", [])
    if rooms:
        st.divider()
        _rooms(rooms)
    issues = data.get("issues", [])
    strengths = data.get("strengths", [])
    if issues or strengths:
        st.divider()
        _issues_strengths(issues, strengths)
    actions = data.get("actions", [])
    if actions:
        st.divider()
        _actions(actions)
    caveats = data.get("caveats", [])
    if caveats:
        st.divider()
        _caveats(caveats, data.get("confidence", "medium"))


def _summary(s: dict):
    st.markdown(
        '<div class="eyebrow">SUMMARY</div>'
        '<h2 style="margin-top:0;">สรุปผลวิเคราะห์</h2>',
        unsafe_allow_html=True,
    )
    feas = s.get("feasibility") or "yellow"
    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("ความเป็นไปได้", f"{FEAS.get(feas, '❔')} {feas}")
    c2.metric("คะแนน", f"{s.get('score', '—')} / 100")
    c3.info(f"**สรุป:** {s.get('note', '-')}")
    if s.get("concern"):
        st.error(f"**⚠ ประเด็น:** {s['concern']}")
    if s.get("strength"):
        st.success(f"**⭐ จุดเด่น:** {s['strength']}")


def _num(v, unit="", dec=1):
    if v is None:
        return "–"
    if isinstance(v, (int, float)):
        if dec == 0 or v == int(v):
            return f"{int(v):,}{unit}"
        return f"{v:,.{dec}f}{unit}"
    return str(v)


def _metrics(m: dict):
    st.markdown(
        '<div class="eyebrow">NUMBERS</div>'
        '<h2 style="margin-top:0;">ตัวเลขโครงการ</h2>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("พื้นที่ดิน", _num(m.get("land_area_sqm"), " ตร.ม.", 0))
    c2.metric("พื้นที่สร้างได้", _num(m.get("buildable_area_sqm"), " ตร.ม.", 0))
    c3.metric("FAR allowed", _num(m.get("far_allowed"), "", 2))
    c4.metric("FAR ใช้", _num(m.get("far_estimated"), "", 2))
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("OSR %", _num(m.get("osr_required_pct"), "%", 0))
    c6.metric("ร่นหน้า", _num(m.get("setback_front_m"), " ม.", 1))
    c7.metric("ร่นข้าง", _num(m.get("setback_side_m"), " ม.", 1))
    c8.metric("สูงสุด", _num(m.get("max_height_m"), " ม.", 1))
    if m.get("floor_area_sqm") or m.get("cost_mbaht"):
        c9, c10 = st.columns(2)
        if m.get("floor_area_sqm"):
            c9.metric("พื้นที่ใช้สอย", _num(m["floor_area_sqm"], " ตร.ม.", 0))
        if m.get("cost_mbaht"):
            c10.metric("ค่าก่อสร้าง", _num(m["cost_mbaht"], " ลบ.", 1))


def _layers(layers: dict):
    st.markdown(
        '<div class="eyebrow">5-LAYER ANALYSIS</div>'
        '<h2 style="margin-top:0;">5 ชั้นความรู้</h2>',
        unsafe_allow_html=True,
    )
    try:
        import pandas as pd
        rows = []
        for key, emoji, name in LAYERS:
            l = layers.get(key, {})
            rows.append({
                "ชั้น": f"{emoji} {name}",
                "สถานะ": f"{STATUS.get(l.get('status', 'warning'), '❔')} {l.get('status', '-')}",
                "คะแนน": l.get("score", 0),
            })
        df = pd.DataFrame(rows)
        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={"คะแนน": st.column_config.ProgressColumn(
                "คะแนน", min_value=0, max_value=100, format="%d")},
        )
    except Exception:
        pass

    for key, emoji, name in LAYERS:
        l = layers.get(key, {})
        findings = l.get("findings", [])
        if not findings:
            continue
        with st.expander(f"{emoji} {name} · {STATUS.get(l.get('status', 'warning'), '❔')} · {len(findings)} finding(s)"):
            for f in findings:
                sev = f.get("severity", "info")
                st.markdown(f"**{SEV.get(sev, 'ℹ')} {f.get('title', '-')}**")
                st.markdown(f.get("detail", ""))
                if f.get("citation"):
                    st.caption(f"📚 {f['citation']}")


def _rooms(rooms: list):
    st.markdown(
        f'<div class="eyebrow">ROOMS ({len(rooms)})</div>'
        '<h2 style="margin-top:0;">วิเคราะห์ห้อง</h2>',
        unsafe_allow_html=True,
    )
    try:
        import pandas as pd
        table = []
        for r in rooms:
            size_min = r.get("size_min")
            size_max = r.get("size_max")
            size = f"{size_min}-{size_max} ตร.ม." if (size_min and size_max) else "–"
            table.append({
                "ห้อง": r.get("name", "-"),
                "ประเภท": r.get("type", "-"),
                "ขนาดแนะนำ": size,
                "ทิศที่ดี": r.get("orientation", "-") or "-",
                "⚠": len(r.get("issues", [])),
            })
        st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
    except Exception:
        pass

    for r in rooms:
        with st.expander(f"🚪 **{r.get('name', '-')}** · _{r.get('type', '-')}_"):
            c1, c2 = st.columns(2)
            if r.get("size_min") and r.get("size_max"):
                c1.metric("ขนาด", f"{r['size_min']}-{r['size_max']} ตร.ม.")
            if r.get("orientation"):
                c1.markdown(f"**🧭 ทิศ:** {r['orientation']}")
            if r.get("thai_note"):
                c2.markdown(f"**🪷 ไทย:** {r['thai_note']}")
            if r.get("fengshui_note"):
                c2.markdown(f"**☯ ฮวงจุ้ย:** {r['fengshui_note']}")
            for p in r.get("points", []):
                st.markdown(f"- {p}")
            for iss in r.get("issues", []):
                st.warning(f"⚠ {iss}")


def _issues_strengths(issues: list, strengths: list):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 🚨 ประเด็น ({len(issues)})")
        for i in issues:
            sev = i.get("severity", "medium")
            st.markdown(f"**{i.get('rank', '-')}. {SEV.get(sev, '🟡')} {i.get('title', '-')}**")
            st.markdown(i.get("detail", ""))
            if i.get("action"):
                st.info(f"💡 {i['action']}")
            st.write("")
    with c2:
        st.markdown(f"### ⭐ จุดเด่น ({len(strengths)})")
        for s in strengths:
            st.markdown(f"**{s.get('rank', '-')}. {s.get('title', '-')}**")
            st.markdown(s.get("detail", ""))
            st.write("")


def _actions(actions: list):
    st.markdown(
        '<div class="eyebrow">NEXT STEPS</div>'
        '<h2 style="margin-top:0;">Action list</h2>',
        unsafe_allow_html=True,
    )
    try:
        import pandas as pd
        rows = [{
            "#": a.get("step", "-"),
            "Action": a.get("action", "-"),
            "โดย": a.get("who", "-"),
            "เมื่อ": a.get("when", "-"),
        } for a in actions]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except Exception:
        for a in actions:
            st.markdown(f"**{a.get('step', '-')}.** {a.get('action', '-')}")


def _caveats(caveats: list, confidence: str):
    emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence, "🟡")
    st.caption(f"⚠ Confidence {emoji} {confidence}")
    for c in caveats:
        st.caption(f"• {c}")


# ============================================================================
# Markdown export
# ============================================================================

def to_markdown(data: dict) -> str:
    out = []
    s = data.get("summary", {})
    feas = s.get("feasibility", "-")
    out.append("## 📊 สรุปผลวิเคราะห์\n")
    out.append(f"- ความเป็นไปได้: {FEAS.get(feas, '❔')} {feas}")
    out.append(f"- คะแนน: {s.get('score', '-')}/100")
    if s.get("note"): out.append(f"- หมายเหตุ: {s['note']}")
    if s.get("concern"): out.append(f"- ⚠ ประเด็น: {s['concern']}")
    if s.get("strength"): out.append(f"- ⭐ จุดเด่น: {s['strength']}")
    out.append("")

    m = data.get("metrics", {})
    if m:
        out.append("## 📐 ตัวเลข\n")
        out.append("| รายการ | ค่า |")
        out.append("|---|---|")
        labels = [("land_area_sqm", "พื้นที่ดิน", "ตร.ม."),
                  ("buildable_area_sqm", "สร้างได้", "ตร.ม."),
                  ("far_allowed", "FAR allowed", ""),
                  ("far_estimated", "FAR ใช้", ""),
                  ("osr_required_pct", "OSR", "%"),
                  ("setback_front_m", "ร่นหน้า", "ม."),
                  ("floor_area_sqm", "ใช้สอย", "ตร.ม."),
                  ("cost_mbaht", "ค่าก่อสร้าง", "ลบ.")]
        for k, l, u in labels:
            v = m.get(k)
            if v is not None:
                out.append(f"| {l} | {v} {u} |")
        out.append("")

    out.append("## 🧩 5-Layer\n")
    for key, emoji, name in LAYERS:
        l = data.get("layers", {}).get(key, {})
        if not l:
            continue
        out.append(f"### {emoji} {name} · {l.get('status', '-')} · {l.get('score', 0)}/100\n")
        for f in l.get("findings", []):
            out.append(f"- **{f.get('title', '-')}** — {f.get('detail', '')}")
            if f.get("citation"):
                out.append(f"  _📚 {f['citation']}_")
        out.append("")

    rooms = data.get("rooms", [])
    if rooms:
        out.append(f"## 🚪 วิเคราะห์ห้อง ({len(rooms)})\n")
        for r in rooms:
            out.append(f"### {r.get('name', '-')}")
            if r.get("size_min") and r.get("size_max"):
                out.append(f"- ขนาด: {r['size_min']}-{r['size_max']} ตร.ม.")
            if r.get("orientation"):
                out.append(f"- ทิศ: {r['orientation']}")
            for p in r.get("points", []):
                out.append(f"- {p}")
            out.append("")

    for label, key in [("🚨 ประเด็น", "issues"), ("⭐ จุดเด่น", "strengths")]:
        items = data.get(key, [])
        if items:
            out.append(f"## {label}\n")
            for it in items:
                out.append(f"**{it.get('rank', '-')}. {it.get('title', '-')}**")
                out.append(f"- {it.get('detail', '')}")
                if it.get("action"):
                    out.append(f"- 💡 {it['action']}")
                out.append("")

    actions = data.get("actions", [])
    if actions:
        out.append("## 🎯 Next Actions\n")
        out.append("| # | Action | โดย | เมื่อ |")
        out.append("|---|---|---|---|")
        for a in actions:
            out.append(f"| {a.get('step', '-')} | {a.get('action', '-')} | {a.get('who', '-')} | {a.get('when', '-')} |")
        out.append("")

    return "\n".join(out)
