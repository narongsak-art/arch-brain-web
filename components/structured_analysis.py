"""Structured analysis output · JSON schema + renderer

Flow:
1. Build a prompt that asks LLM for JSON output (plus markdown narrative)
2. Parse JSON blob out of response
3. Render as tables/metrics/charts in Streamlit
4. Fall back to plain markdown if JSON parse fails

Schema (v1):
{
  summary: {feasibility, overall_score, key_concern, key_strength, ...},
  metrics: {far_allowed, far_used, osr_*, setback_*, ...},
  layers: {law|eng|design|thai|fengshui: {status, findings[]}},
  rooms: [{name, type, size_range, orientation, notes, ...}],
  issues: [{rank, severity, title, detail, action}],
  strengths: [{rank, title, detail}],
  next_actions: [{step, action, who, when}],
  confidence, caveats
}
"""

import json
import re
from typing import Optional

import streamlit as st


SCHEMA_VERSION = "1.0"


# ============================================================================
# Prompt builder
# ============================================================================

STRUCTURED_OUTPUT_INSTRUCTION = """

## ⭐ Output Format — Structured JSON (IMPORTANT)

ตอบเป็น **JSON ล้วนๆ** ในรูปแบบด้านล่าง · ห้ามใส่ markdown · ห้ามใส่ ```json ``` หุ้ม · เริ่มด้วย `{` จบด้วย `}` เท่านั้น

```
{
  "summary": {
    "feasibility": "green|yellow|red",
    "feasibility_note": "1-2 ประโยค · สรุปความเป็นไปได้",
    "overall_score": 0-100,
    "key_concern": "ปัญหาหลักที่สุด 1 ข้อ",
    "key_strength": "จุดเด่นหลัก 1 ข้อ"
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
    "estimated_floor_area_sqm": number,
    "estimated_cost_mbaht": number
  },
  "layers": {
    "law": {
      "status": "pass|warning|fail",
      "score": 0-100,
      "findings": [
        {"severity": "critical|warning|info", "title": "...", "detail": "...", "citation": "กฎกระทรวง 55 ข้อ 50"}
      ]
    },
    "eng": { "status": "...", "score": 0-100, "findings": [...] },
    "design": { "status": "...", "score": 0-100, "findings": [...] },
    "thai": { "status": "...", "score": 0-100, "findings": [...] },
    "fengshui": { "status": "...", "score": 0-100, "findings": [...] }
  },
  "rooms": [
    {
      "name": "ห้องนอนใหญ่",
      "type": "bedroom|kitchen|bathroom|living|dining|prayer|office|utility|other",
      "recommended_size_min_sqm": number,
      "recommended_size_max_sqm": number,
      "orientation_best": "ทิศที่ดีที่สุด (+เหตุผล)",
      "fengshui_note": "ข้อควรระวังฮวงจุ้ย (หรือ null)",
      "thai_culture_note": "ข้อวัฒนธรรมไทย (หรือ null)",
      "key_points": ["bullet 1", "bullet 2", "bullet 3"],
      "issues": ["ปัญหาเฉพาะห้อง (หรือ array ว่าง)"]
    }
  ],
  "issues": [
    {"rank": 1, "severity": "high|medium|low", "title": "...", "detail": "...", "action": "ควรทำอะไร"}
  ],
  "strengths": [
    {"rank": 1, "title": "...", "detail": "..."}
  ],
  "next_actions": [
    {"step": 1, "action": "...", "who": "สถาปนิก|วิศวกร|เจ้าของ|ซินแส", "when": "ก่อนออกแบบ|ก่อนก่อสร้าง|หลังก่อสร้าง"}
  ],
  "confidence": "high|medium|low",
  "caveats": ["ข้อจำกัด/สมมติที่ใช้"]
}
```

### กฎการเขียน
- `feasibility: green` = ทำได้เลย · `yellow` = ทำได้แต่ต้องระวัง · `red` = ทำไม่ได้/ต้องปรับสาระสำคัญ
- `rooms:` ใส่**ทุกห้องที่ครอบครัวน่าจะต้องการ** (จากจำนวนห้องนอนใน brief + ห้องมาตรฐาน) · อย่างน้อย 6-10 ห้อง
- `issues` + `strengths` ต้องมีอย่างน้อย **3** รายการต่ออัน · เรียงตามความสำคัญ
- ตัวเลขกฎหมาย · cite จาก FULL KNOWLEDGE เท่านั้น · ถ้าไม่มีให้ใส่ `null`
- ประโยคไทย กระชับ · ไม่ต้อง over-explain
"""


def build_structured_prompt(base_prompt: str, full_knowledge: str, kg: str) -> str:
    """Wrap base prompt with JSON schema instruction"""
    return f"""{base_prompt}

## ⭐ FULL KNOWLEDGE (เนื้อหาเต็มหน้า wiki · ใช้อ้างอิงตัวเลขจริง)

{full_knowledge}

---

## Knowledge Graph Map

{kg}

---

⚠ Cite ตัวเลขกฎหมายจาก FULL KNOWLEDGE เท่านั้น · ห้ามสร้างตัวเลขจากความจำ
{STRUCTURED_OUTPUT_INSTRUCTION}
"""


# ============================================================================
# Parser
# ============================================================================

def extract_json_blob(text: str) -> Optional[dict]:
    """Extract and parse the first JSON object from LLM text.
    Handles:
      - Pure JSON
      - JSON wrapped in ```json ... ``` blocks
      - JSON with leading commentary
    Returns None if parse fails.
    """
    if not text:
        return None

    # Try direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try fenced ```json ... ``` block
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Try brace-matching from first `{`
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
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None


# ============================================================================
# Renderer
# ============================================================================

STATUS_META = {
    "green": ("🟢", "ทำได้เลย", "success"),
    "yellow": ("🟡", "ทำได้ · ต้องระวัง", "warning"),
    "red": ("🔴", "ต้องปรับก่อน", "error"),
    "pass": ("✅", "ผ่าน", "success"),
    "warning": ("⚠", "ระวัง", "warning"),
    "fail": ("❌", "ไม่ผ่าน", "error"),
    "critical": ("🚨", "สำคัญมาก", "error"),
    "info": ("ℹ", "ข้อมูล", "info"),
    "high": ("🔴", "สูง", "error"),
    "medium": ("🟡", "กลาง", "warning"),
    "low": ("🟢", "ต่ำ", "success"),
}

LAYER_META = {
    "law": ("🏛", "กฎหมาย", "#ef4444"),
    "eng": ("🔧", "วิศวกรรม", "#3b82f6"),
    "design": ("🎨", "ออกแบบ", "#10b981"),
    "thai": ("🪷", "วัฒนธรรมไทย", "#f59e0b"),
    "fengshui": ("☯", "ฮวงจุ้ย", "#a855f7"),
}


def render_analysis(data: dict):
    """Render the full structured analysis"""
    _render_summary(data.get("summary", {}))
    st.markdown("---")
    _render_metrics(data.get("metrics", {}))
    st.markdown("---")
    _render_layers(data.get("layers", {}))
    st.markdown("---")
    _render_rooms(data.get("rooms", []))
    st.markdown("---")
    _render_issues_strengths(
        data.get("issues", []),
        data.get("strengths", []),
    )
    st.markdown("---")
    _render_next_actions(data.get("next_actions", []))
    if data.get("caveats"):
        st.markdown("---")
        _render_caveats(data.get("caveats", []), data.get("confidence", "medium"))


def _render_summary(summary: dict):
    st.markdown("## 📊 สรุปผลวิเคราะห์")
    feas = summary.get("feasibility", "yellow")
    emoji, label, _ = STATUS_META.get(feas, STATUS_META["yellow"])
    score = summary.get("overall_score", 0)

    col1, col2, col3 = st.columns([1, 1, 2])
    col1.metric("ความเป็นไปได้", f"{emoji} {label}")
    col2.metric("คะแนนรวม", f"{score}/100")
    col3.markdown(f"**หมายเหตุ:** {summary.get('feasibility_note', '-')}")

    col_a, col_b = st.columns(2)
    if summary.get("key_concern"):
        col_a.error(f"**⚠ ประเด็นหลัก:** {summary['key_concern']}")
    if summary.get("key_strength"):
        col_b.success(f"**⭐ จุดเด่น:** {summary['key_strength']}")


def _fmt_num(v, unit="", decimals=1):
    if v is None:
        return "–"
    try:
        if isinstance(v, (int, float)):
            if decimals == 0 or v == int(v):
                return f"{int(v):,}{unit}"
            return f"{v:,.{decimals}f}{unit}"
    except Exception:
        pass
    return str(v)


def _render_metrics(metrics: dict):
    st.markdown("## 📐 ตัวเลขโครงการ")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("พื้นที่ดิน", _fmt_num(metrics.get("land_area_sqm"), " ตร.ม.", 0))
    col2.metric("พื้นที่สร้างได้", _fmt_num(metrics.get("buildable_area_sqm"), " ตร.ม.", 0))
    col3.metric("FAR allowed", _fmt_num(metrics.get("far_allowed"), "", 2))
    col4.metric("FAR ใช้จริง", _fmt_num(metrics.get("far_estimated"), "", 2))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("OSR required", _fmt_num(metrics.get("osr_required_pct"), "%", 0))
    col6.metric("ระยะร่นหน้า", _fmt_num(metrics.get("setback_front_m"), " ม.", 1))
    col7.metric("ระยะร่นข้าง", _fmt_num(metrics.get("setback_side_m"), " ม.", 1))
    col8.metric("ความสูงสูงสุด", _fmt_num(metrics.get("max_height_m"), " ม.", 1))

    col_est1, col_est2 = st.columns(2)
    if metrics.get("estimated_floor_area_sqm"):
        col_est1.metric("พื้นที่ใช้สอยประมาณ", _fmt_num(metrics["estimated_floor_area_sqm"], " ตร.ม.", 0))
    if metrics.get("estimated_cost_mbaht"):
        col_est2.metric("ค่าก่อสร้างประมาณ", _fmt_num(metrics["estimated_cost_mbaht"], " ลบ.", 1))


def _render_layers(layers: dict):
    st.markdown("## 🧩 5-Layer Analysis")

    # Score chart
    scores = []
    for key, meta in LAYER_META.items():
        layer = layers.get(key, {})
        emoji, name, color = meta
        scores.append({
            "ชั้น": f"{emoji} {name}",
            "คะแนน": layer.get("score", 0),
            "สถานะ": STATUS_META.get(layer.get("status", "warning"), STATUS_META["warning"])[0] + " " +
                      STATUS_META.get(layer.get("status", "warning"), STATUS_META["warning"])[1],
        })

    try:
        import pandas as pd
        df = pd.DataFrame(scores)
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={
                         "คะแนน": st.column_config.ProgressColumn(
                             "คะแนน", min_value=0, max_value=100, format="%d",
                         ),
                     })
    except Exception:
        st.table(scores)

    # Per-layer findings
    for key, meta in LAYER_META.items():
        layer = layers.get(key, {})
        findings = layer.get("findings", [])
        if not findings:
            continue
        emoji, name, _color = meta
        status = layer.get("status", "warning")
        st_emoji, st_label, _ = STATUS_META.get(status, STATUS_META["warning"])
        with st.expander(f"{emoji} {name} · {st_emoji} {st_label} · {len(findings)} findings"):
            for f in findings:
                sev = f.get("severity", "info")
                sev_emoji, _, _ = STATUS_META.get(sev, STATUS_META["info"])
                st.markdown(f"**{sev_emoji} {f.get('title', '-')}**")
                st.markdown(f.get("detail", ""))
                if f.get("citation"):
                    st.caption(f"📚 {f['citation']}")
                st.markdown("")


def _render_rooms(rooms: list):
    if not rooms:
        return
    st.markdown(f"## 🚪 วิเคราะห์ห้อง ({len(rooms)} ห้อง)")

    # Summary table
    try:
        import pandas as pd
        rows = []
        for r in rooms:
            size_min = r.get("recommended_size_min_sqm")
            size_max = r.get("recommended_size_max_sqm")
            size = "–"
            if size_min is not None and size_max is not None:
                size = f"{size_min}-{size_max} ตร.ม."
            elif size_min is not None:
                size = f"≥{size_min} ตร.ม."
            rows.append({
                "ห้อง": r.get("name", "-"),
                "ประเภท": r.get("type", "-"),
                "ขนาดแนะนำ": size,
                "ทิศที่ดี": r.get("orientation_best", "-") or "-",
                "ปัญหา": len(r.get("issues", [])),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception:
        pass

    # Detail cards
    for r in rooms:
        with st.expander(f"🚪 **{r.get('name', '-')}** · _{r.get('type', '-')}_"):
            col1, col2 = st.columns(2)
            with col1:
                size_min = r.get("recommended_size_min_sqm")
                size_max = r.get("recommended_size_max_sqm")
                if size_min and size_max:
                    st.metric("ขนาดแนะนำ", f"{size_min}-{size_max} ตร.ม.")
                if r.get("orientation_best"):
                    st.markdown(f"**🧭 ทิศที่แนะนำ:** {r['orientation_best']}")
            with col2:
                if r.get("thai_culture_note"):
                    st.markdown(f"**🪷 วัฒนธรรมไทย:** {r['thai_culture_note']}")
                if r.get("fengshui_note"):
                    st.markdown(f"**☯ ฮวงจุ้ย:** {r['fengshui_note']}")

            if r.get("key_points"):
                st.markdown("**📌 ข้อแนะนำ:**")
                for pt in r["key_points"]:
                    st.markdown(f"- {pt}")

            if r.get("issues"):
                st.markdown("**⚠ ปัญหาเฉพาะห้อง:**")
                for iss in r["issues"]:
                    st.warning(iss)


def _render_issues_strengths(issues: list, strengths: list):
    col_iss, col_str = st.columns(2)

    with col_iss:
        st.markdown(f"### 🚨 Top {len(issues)} Issues")
        for iss in issues:
            sev = iss.get("severity", "medium")
            emoji, label, _ = STATUS_META.get(sev, STATUS_META["medium"])
            with st.container():
                st.markdown(f"**{iss.get('rank', '-')} · {emoji} {iss.get('title', '-')}**")
                st.caption(f"ระดับ: {label}")
                st.markdown(iss.get("detail", ""))
                if iss.get("action"):
                    st.info(f"💡 **ควรทำ:** {iss['action']}")
                st.markdown("")

    with col_str:
        st.markdown(f"### ⭐ Top {len(strengths)} Strengths")
        for s in strengths:
            with st.container():
                st.markdown(f"**{s.get('rank', '-')} · {s.get('title', '-')}**")
                st.markdown(s.get("detail", ""))
                st.markdown("")


def _render_next_actions(actions: list):
    if not actions:
        return
    st.markdown("### 🎯 Next Actions")
    try:
        import pandas as pd
        rows = [
            {
                "Step": a.get("step", "-"),
                "Action": a.get("action", "-"),
                "โดย": a.get("who", "-"),
                "เมื่อ": a.get("when", "-"),
            }
            for a in actions
        ]
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception:
        for a in actions:
            st.markdown(f"**{a.get('step', '-')}.** {a.get('action', '-')} _(โดย {a.get('who', '-')} · {a.get('when', '-')})_")


def _render_caveats(caveats: list, confidence: str):
    st.markdown("### ⚠ ข้อจำกัด / สมมติ")
    conf_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence, "🟡")
    st.caption(f"Confidence: {conf_emoji} {confidence}")
    for c in caveats:
        st.caption(f"• {c}")


# ============================================================================
# Markdown renderer (fallback when JSON parse fails)
# ============================================================================

def render_fallback(raw_text: str, error: str | None = None):
    """Render raw LLM output when structured parse fails"""
    if error:
        st.warning(f"⚠ ไม่สามารถแปลง JSON ได้ ({error}) · แสดงผลแบบ markdown")
    st.markdown(raw_text)
