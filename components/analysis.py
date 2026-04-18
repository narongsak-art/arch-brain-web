"""Structured analysis: prompt builder + JSON parser + renderer"""

import json
import re

import streamlit as st


OUTPUT_INSTRUCTION = """

## Output Format — ตอบเป็น JSON ล้วน

เริ่มด้วย `{` จบด้วย `}` · ห้ามใส่ markdown · ห้ามใส่ ```json``` หุ้ม

```
{
  "summary": {
    "feasibility": "green|yellow|red",
    "note": "1-2 ประโยค สรุปความเป็นไปได้",
    "score": 0-100,
    "concern": "ประเด็นหลัก 1 ข้อ",
    "strength": "จุดเด่น 1 ข้อ"
  },
  "metrics": {
    "land_area_sqm": number,
    "buildable_area_sqm": number,
    "far_allowed": number,
    "far_estimated": number,
    "osr_required_pct": number,
    "setback_front_m": number,
    "setback_side_m": number,
    "setback_back_m": number,
    "max_height_m": number,
    "floor_area_sqm": number,
    "cost_mbaht": number
  },
  "layers": {
    "law": {"status":"pass|warning|fail", "score":0-100, "findings":[{"severity":"critical|warning|info","title":"...","detail":"...","citation":"..."}]},
    "eng": {...}, "design": {...}, "thai": {...}, "fengshui": {...}
  },
  "rooms": [
    {"name":"ห้องนอนใหญ่","type":"bedroom","size_min":12,"size_max":20,"orientation":"ทิศที่ดี","thai_note":null,"fengshui_note":null,"points":["..."],"issues":[]}
  ],
  "issues": [{"rank":1,"severity":"high|medium|low","title":"...","detail":"...","action":"..."}],
  "strengths": [{"rank":1,"title":"...","detail":"..."}],
  "actions": [{"step":1,"action":"...","who":"สถาปนิก|วิศวกร|เจ้าของ","when":"ก่อนออกแบบ|ก่อนก่อสร้าง|หลัง"}],
  "confidence": "high|medium|low",
  "caveats": ["ข้อจำกัด/สมมติ"]
}
```

### กฎ
- `rooms`: ใส่อย่างน้อย 6 ห้อง (จาก brief) · เรียงตามความสำคัญ
- `issues` + `strengths`: อย่างน้อย 3 ต่ออัน
- ตัวเลขกฎหมาย: cite จาก FULL KNOWLEDGE เท่านั้น · ถ้าไม่แน่ใจใส่ null
- `feasibility`: green=ทำได้เลย · yellow=ระวัง · red=ต้องปรับ
"""


def build_prompt(base_prompt: str, full_knowledge: str, kg: str) -> str:
    return f"""{base_prompt}

## ⭐ FULL KNOWLEDGE (ใช้ cite ตัวเลขกฎหมาย)

{full_knowledge}

---

## Knowledge Graph Map

{kg}

---

⚠ Cite ตัวเลขกฎหมายจาก FULL KNOWLEDGE เท่านั้น · ห้ามสร้างเอง
{OUTPUT_INSTRUCTION}
"""


def extract_json(text: str) -> dict | None:
    """Extract JSON object from LLM text. Handles fenced ```json``` blocks, leading commentary, etc."""
    if not text:
        return None
    # Direct
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    # Fenced
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Brace-match first object
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except Exception:
                    return None
    return None


# ============================================================================
# Renderers
# ============================================================================

FEAS = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
STATUS = {"pass": "✅", "warning": "⚠", "fail": "❌"}
SEV = {"critical": "🚨", "high": "🔴", "warning": "⚠", "medium": "🟡", "low": "🟢", "info": "ℹ"}
LAYERS = [
    ("law", "🏛", "กฎหมาย"),
    ("eng", "🔧", "วิศวกรรม"),
    ("design", "🎨", "ออกแบบ"),
    ("thai", "🪷", "วัฒนธรรมไทย"),
    ("fengshui", "☯", "ฮวงจุ้ย"),
]


def render(data: dict):
    _render_summary(data.get("summary", {}))
    st.divider()
    _render_metrics(data.get("metrics", {}))
    st.divider()
    _render_layers(data.get("layers", {}))
    st.divider()
    _render_rooms(data.get("rooms", []))
    st.divider()
    _render_issues_strengths(data.get("issues", []), data.get("strengths", []))
    if data.get("actions"):
        st.divider()
        _render_actions(data["actions"])
    if data.get("caveats"):
        st.divider()
        _render_caveats(data["caveats"], data.get("confidence", "medium"))


def _render_summary(s: dict):
    st.subheader("📊 สรุปผลวิเคราะห์")
    feas = s.get("feasibility", "yellow")
    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("ความเป็นไปได้", f"{FEAS.get(feas, '❔')} {feas}")
    c2.metric("คะแนน", f"{s.get('score', 0)}/100")
    c3.info(f"**หมายเหตุ:** {s.get('note', '-')}")
    c4, c5 = st.columns(2)
    if s.get("concern"):
        c4.error(f"**⚠ ประเด็น:** {s['concern']}")
    if s.get("strength"):
        c5.success(f"**⭐ จุดเด่น:** {s['strength']}")


def _num(v, unit="", dec=1):
    if v is None:
        return "–"
    try:
        if isinstance(v, (int, float)):
            if dec == 0 or v == int(v):
                return f"{int(v):,}{unit}"
            return f"{v:,.{dec}f}{unit}"
    except Exception:
        pass
    return str(v)


def _render_metrics(m: dict):
    st.subheader("📐 ตัวเลขโครงการ")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("พื้นที่ดิน", _num(m.get("land_area_sqm"), " ตร.ม.", 0))
    c2.metric("พื้นที่สร้างได้", _num(m.get("buildable_area_sqm"), " ตร.ม.", 0))
    c3.metric("FAR allowed", _num(m.get("far_allowed"), "", 2))
    c4.metric("FAR ใช้จริง", _num(m.get("far_estimated"), "", 2))
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("OSR required", _num(m.get("osr_required_pct"), "%", 0))
    c6.metric("ระยะร่นหน้า", _num(m.get("setback_front_m"), " ม.", 1))
    c7.metric("ระยะร่นข้าง", _num(m.get("setback_side_m"), " ม.", 1))
    c8.metric("สูงสุด", _num(m.get("max_height_m"), " ม.", 1))
    if m.get("floor_area_sqm") or m.get("cost_mbaht"):
        c9, c10 = st.columns(2)
        if m.get("floor_area_sqm"):
            c9.metric("พื้นที่ใช้สอย", _num(m["floor_area_sqm"], " ตร.ม.", 0))
        if m.get("cost_mbaht"):
            c10.metric("ค่าก่อสร้างประมาณ", _num(m["cost_mbaht"], " ลบ.", 1))


def _render_layers(layers: dict):
    st.subheader("🧩 5-Layer Analysis")
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
        st.table([{"ชั้น": n, "score": layers.get(k, {}).get("score", 0)} for k, _, n in LAYERS])

    for key, emoji, name in LAYERS:
        l = layers.get(key, {})
        findings = l.get("findings", [])
        if not findings:
            continue
        with st.expander(f"{emoji} {name} · {STATUS.get(l.get('status', 'warning'), '❔')} {l.get('status', '-')} · {len(findings)} findings"):
            for f in findings:
                sev = f.get("severity", "info")
                st.markdown(f"**{SEV.get(sev, 'ℹ')} {f.get('title', '-')}**")
                st.markdown(f.get("detail", ""))
                if f.get("citation"):
                    st.caption(f"📚 {f['citation']}")
                st.write("")


def _render_rooms(rooms: list):
    if not rooms:
        return
    st.subheader(f"🚪 วิเคราะห์ห้อง ({len(rooms)})")
    try:
        import pandas as pd
        rows = []
        for r in rooms:
            size_min = r.get("size_min")
            size_max = r.get("size_max")
            size = "–"
            if size_min and size_max:
                size = f"{size_min}-{size_max} ตร.ม."
            rows.append({
                "ห้อง": r.get("name", "-"),
                "ประเภท": r.get("type", "-"),
                "ขนาด": size,
                "ทิศ": r.get("orientation", "-") or "-",
                "⚠": len(r.get("issues", [])),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except Exception:
        pass

    for r in rooms:
        with st.expander(f"🚪 **{r.get('name', '-')}** · _{r.get('type', '-')}_"):
            c1, c2 = st.columns(2)
            with c1:
                if r.get("size_min") and r.get("size_max"):
                    st.metric("ขนาดแนะนำ", f"{r['size_min']}-{r['size_max']} ตร.ม.")
                if r.get("orientation"):
                    st.markdown(f"**🧭 ทิศ:** {r['orientation']}")
            with c2:
                if r.get("thai_note"):
                    st.markdown(f"**🪷 วัฒนธรรมไทย:** {r['thai_note']}")
                if r.get("fengshui_note"):
                    st.markdown(f"**☯ ฮวงจุ้ย:** {r['fengshui_note']}")
            if r.get("points"):
                st.markdown("**📌 ข้อแนะนำ:**")
                for p in r["points"]:
                    st.markdown(f"- {p}")
            if r.get("issues"):
                for iss in r["issues"]:
                    st.warning(f"⚠ {iss}")


def _render_issues_strengths(issues: list, strengths: list):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 🚨 Top {len(issues)} Issues")
        for i in issues:
            sev = i.get("severity", "medium")
            st.markdown(f"**{i.get('rank', '-')}. {SEV.get(sev, '🟡')} {i.get('title', '-')}**")
            st.markdown(i.get("detail", ""))
            if i.get("action"):
                st.info(f"💡 **ทำ:** {i['action']}")
            st.write("")
    with c2:
        st.markdown(f"### ⭐ Top {len(strengths)} Strengths")
        for s in strengths:
            st.markdown(f"**{s.get('rank', '-')}. {s.get('title', '-')}**")
            st.markdown(s.get("detail", ""))
            st.write("")


def _render_actions(actions: list):
    st.markdown("### 🎯 Next Actions")
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
            st.markdown(f"**{a.get('step', '-')}.** {a.get('action', '-')} _(โดย {a.get('who', '-')} · {a.get('when', '-')})_")


def _render_caveats(caveats: list, confidence: str):
    emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence, "🟡")
    st.markdown(f"### ⚠ ข้อจำกัด · Confidence {emoji} {confidence}")
    for c in caveats:
        st.caption(f"• {c}")


# ============================================================================
# Export to markdown
# ============================================================================

def to_markdown(data: dict) -> str:
    """Convert parsed data to readable markdown for downloads"""
    out = []
    s = data.get("summary", {})
    feas = s.get("feasibility", "-")
    out.append(f"## 📊 สรุปผลวิเคราะห์\n")
    out.append(f"- **ความเป็นไปได้:** {FEAS.get(feas, '❔')} {feas}")
    out.append(f"- **คะแนน:** {s.get('score', '-')}/100")
    if s.get("note"):
        out.append(f"- **หมายเหตุ:** {s['note']}")
    if s.get("concern"):
        out.append(f"- **⚠ ประเด็น:** {s['concern']}")
    if s.get("strength"):
        out.append(f"- **⭐ จุดเด่น:** {s['strength']}")
    out.append("")

    m = data.get("metrics", {})
    if m:
        out.append("## 📐 ตัวเลข\n")
        out.append("| รายการ | ค่า |")
        out.append("|---|---|")
        for key, label, unit in [
            ("land_area_sqm", "พื้นที่ดิน", "ตร.ม."),
            ("buildable_area_sqm", "พื้นที่สร้างได้", "ตร.ม."),
            ("far_allowed", "FAR allowed", ""),
            ("far_estimated", "FAR ใช้จริง", ""),
            ("osr_required_pct", "OSR required", "%"),
            ("setback_front_m", "ระยะร่นหน้า", "ม."),
            ("setback_side_m", "ระยะร่นข้าง", "ม."),
            ("setback_back_m", "ระยะร่นหลัง", "ม."),
            ("max_height_m", "สูงสุด", "ม."),
            ("floor_area_sqm", "ใช้สอย", "ตร.ม."),
            ("cost_mbaht", "ค่าก่อสร้าง", "ลบ."),
        ]:
            v = m.get(key)
            if v is not None:
                out.append(f"| {label} | {v} {unit} |")
        out.append("")

    out.append("## 🧩 5-Layer\n")
    for key, emoji, name in LAYERS:
        l = data.get("layers", {}).get(key, {})
        if not l:
            continue
        out.append(f"### {emoji} {name} · {l.get('status', '-')} · {l.get('score', 0)}/100\n")
        for f in l.get("findings", []):
            out.append(f"- **{SEV.get(f.get('severity', 'info'), 'ℹ')} {f.get('title', '-')}** — {f.get('detail', '')}")
            if f.get("citation"):
                out.append(f"  _📚 {f['citation']}_")
        out.append("")

    rooms = data.get("rooms", [])
    if rooms:
        out.append(f"## 🚪 วิเคราะห์ห้อง ({len(rooms)})\n")
        for r in rooms:
            out.append(f"### {r.get('name', '-')} · _{r.get('type', '-')}_")
            if r.get("size_min") and r.get("size_max"):
                out.append(f"- **ขนาด:** {r['size_min']}-{r['size_max']} ตร.ม.")
            if r.get("orientation"):
                out.append(f"- **ทิศ:** {r['orientation']}")
            if r.get("thai_note"):
                out.append(f"- **🪷 วัฒนธรรมไทย:** {r['thai_note']}")
            if r.get("fengshui_note"):
                out.append(f"- **☯ ฮวงจุ้ย:** {r['fengshui_note']}")
            for p in r.get("points", []):
                out.append(f"- {p}")
            for iss in r.get("issues", []):
                out.append(f"- **⚠:** {iss}")
            out.append("")

    for label, key, prefix in [("🚨 Issues", "issues", ""), ("⭐ Strengths", "strengths", "")]:
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

    if data.get("caveats"):
        out.append(f"## ⚠ ข้อจำกัด · {data.get('confidence', 'medium')}\n")
        for c in data["caveats"]:
            out.append(f"- {c}")

    return "\n".join(out)
