"""
brain.py · everything AI + analysis-rendering lives here

Contents (in order):
  - Knowledge base loaders (kg, full-knowledge, system-prompt)
  - LLM clients (Gemini · Claude · unified dispatch)
  - Prompt builder (includes structured JSON schema)
  - JSON extraction (handles pure / fenced / embedded)
  - Structured result renderer (6 sections)
  - Markdown exporter
"""

import base64
import json
import re
from pathlib import Path

import requests
import streamlit as st


ROOT = Path(__file__).parent
KG_FILE = ROOT / "kg-compact.json"
FULL_FILE = ROOT / "full-knowledge.md"
PROMPT_FILE = ROOT / "system-prompt.md"

GEMINI_MODELS = {
    "gemini-2.5-flash": "🚀 Gemini 2.5 Flash",
    "gemini-2.0-flash": "⚡ Gemini 2.0 Flash",
    "gemini-1.5-flash": "📦 Gemini 1.5 Flash",
}
CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8000


# ============================================================================
# Knowledge loaders (cached · load once per session)
# ============================================================================

@st.cache_data
def load_kg() -> str:
    return KG_FILE.read_text(encoding="utf-8") if KG_FILE.exists() else ""


@st.cache_data
def load_full_knowledge() -> str:
    return FULL_FILE.read_text(encoding="utf-8") if FULL_FILE.exists() else ""


@st.cache_data
def load_base_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    return "You are an architect's assistant for Thai residential design."


@st.cache_data
def load_kg_parsed() -> dict:
    """KG JSON parsed for use by Explore view"""
    try:
        return json.loads(load_kg()) if load_kg() else {}
    except Exception:
        return {}


# ============================================================================
# LLM clients
# ============================================================================

def _call_gemini(api_key: str, system: str, user_prompt: str,
                image_bytes: bytes | None, model: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    combined = f"{system}\n\n---\n\n{user_prompt}"
    parts = [{"text": combined}]
    if image_bytes:
        parts.insert(0, {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
            }
        })
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"maxOutputTokens": MAX_TOKENS, "temperature": 0.3},
    }
    r = requests.post(url, json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"No response from Gemini: {data}")
    return candidates[0]["content"]["parts"][0]["text"]


def _call_claude(api_key: str, system: str, user_prompt: str,
                image_bytes: bytes | None) -> str:
    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError("anthropic package not installed") from e
    client = anthropic.Anthropic(api_key=api_key)
    content: list = [{"type": "text", "text": user_prompt}]
    if image_bytes:
        content.insert(0, {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
            },
        })
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    return resp.content[0].text


def run_ai(provider: str, api_key: str, system: str, user_text: str,
           image_bytes: bytes | None = None,
           model: str = "gemini-2.5-flash") -> str:
    """Unified dispatch · never crashes callers (raises RuntimeError on fail)"""
    if provider == "gemini":
        return _call_gemini(api_key, system, user_text, image_bytes, model)
    return _call_claude(api_key, system, user_text, image_bytes)


# ============================================================================
# Prompt construction
# ============================================================================

OUTPUT_SCHEMA = """
ตอบเป็น JSON ล้วน · เริ่มด้วย { จบด้วย } · ห้าม markdown

{
  "summary": {
    "feasibility": "green|yellow|red",
    "note": "1-2 ประโยค",
    "score": 0-100,
    "concern": "ประเด็นหลัก",
    "strength": "จุดเด่น"
  },
  "metrics": {
    "land_area_sqm": number, "buildable_area_sqm": number,
    "far_allowed": number, "far_estimated": number,
    "osr_required_pct": number,
    "setback_front_m": number, "setback_side_m": number, "setback_back_m": number,
    "max_height_m": number, "floor_area_sqm": number, "cost_mbaht": number
  },
  "layers": {
    "law":      {"status":"pass|warning|fail", "score":0-100, "findings":[{"severity":"critical|warning|info","title":"","detail":"","citation":""}]},
    "eng":      {...},
    "design":   {...},
    "thai":     {...},
    "fengshui": {...}
  },
  "rooms": [{"name":"","type":"bedroom|kitchen|bathroom|living|prayer|other",
             "size_min":0,"size_max":0,"orientation":"","thai_note":null,"fengshui_note":null,
             "points":["..."],"issues":[]}],
  "issues":    [{"rank":1,"severity":"high|medium|low","title":"","detail":"","action":""}],
  "strengths": [{"rank":1,"title":"","detail":""}],
  "actions":   [{"step":1,"action":"","who":"สถาปนิก|วิศวกร|เจ้าของ","when":"ก่อนออกแบบ|ก่อนก่อสร้าง|หลัง"}],
  "phases": {
    "SD": {"label": "Schematic Design", "tasks": ["...", "..."], "deliverables": ["..."], "duration_weeks": 4},
    "DD": {"label": "Design Development", "tasks": [...], "deliverables": [...], "duration_weeks": 6},
    "CD": {"label": "Construction Documents", "tasks": [...], "deliverables": [...], "duration_weeks": 8},
    "CA": {"label": "Construction Administration", "tasks": [...], "deliverables": [...], "duration_weeks": 26}
  },
  "compliance": {
    "building_code":    {"status": "pass|warning|fail", "note": "..."},
    "zoning":           {"status": "...", "note": "..."},
    "parking":          {"status": "...", "note": "..."},
    "fire_egress":      {"status": "...", "note": "..."},
    "accessibility":    {"status": "...", "note": "..."},
    "energy":           {"status": "...", "note": "..."}
  },
  "confidence": "high|medium|low",
  "caveats":   ["..."]
}

กฎ:
- rooms อย่างน้อย 6
- issues + strengths อย่างน้อย 3 ต่ออัน
- phases: 4 phases (SD · DD · CD · CA) · 3-5 tasks ต่อ phase · 2-3 deliverables · duration realistic
- compliance: 6 หมวดหลัก · status + note 1 บรรทัด (cite มาตรา ถ้าทำได้)
- ตัวเลขกฎหมาย: cite จาก FULL KNOWLEDGE · ถ้าไม่แน่ใจใส่ null
- ใช้ข้อมูล orientation/topography/priority เพื่อปรับคำแนะนำให้ตรงโจทย์
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


def build_user_prompt(pd: dict) -> str:
    priority_str = ", ".join(pd.get("priority") or []) or "-"
    pro_lines = []
    if pd.get("orientation"):
        pro_lines.append(f"- ทิศที่ดิน (ด้านยาวหัน): {pd['orientation']}")
    if pd.get("topography"):
        pro_lines.append(f"- ภูมิประเทศ: {pd['topography']}")
    if pd.get("adjacent"):
        pro_lines.append(f"- บริบทรอบที่ดิน: {pd['adjacent']}")
    if priority_str != "-":
        pro_lines.append(f"- ลำดับความสำคัญ: {priority_str}")
    if pd.get("grade"):
        pro_lines.append(f"- Grade ก่อสร้าง: {pd['grade']}")
    if pd.get("timeline"):
        pro_lines.append(f"- Timeline: {pd['timeline']}")
    pro_block = ("\n".join(pro_lines) + "\n") if pro_lines else ""

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
{pro_block}
วิเคราะห์เป็น structured JSON ตาม schema · อย่าลืมใช้ข้อมูลทิศ/ภูมิประเทศ/priority เพื่อ tailor advice
"""


# ============================================================================
# JSON parser · robust across 4 input shapes
# ============================================================================

def extract_json(text: str) -> dict | None:
    if not text:
        return None
    # pure
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    # fenced ```json
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # brace-match embedded
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
# Rendering
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
    """Full structured analysis display · architect-focused"""
    _summary(data.get("summary", {}))
    st.divider()
    _metrics(data.get("metrics", {}))
    compliance = data.get("compliance") or {}
    if compliance:
        st.divider()
        _compliance(compliance)
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
    phases = data.get("phases") or {}
    if phases:
        st.divider()
        _phases(phases)
    actions = data.get("actions", [])
    if actions:
        st.divider()
        _actions(actions)
    caveats = data.get("caveats", [])
    if caveats:
        st.divider()
        _caveats(caveats, data.get("confidence", "medium"))


# ----- new sections for architect use -----

def _compliance(comp: dict):
    st.markdown(
        '<div class="eyebrow">COMPLIANCE</div>'
        '<h2 style="margin-top:0;">Compliance checklist</h2>',
        unsafe_allow_html=True,
    )
    label_map = {
        "building_code": ("🏛", "พรบ.ควบคุมอาคาร"),
        "zoning": ("📋", "ผังเมือง · FAR/OSR"),
        "parking": ("🚗", "ที่จอดรถ"),
        "fire_egress": ("🔥", "บันไดหนีไฟ"),
        "accessibility": ("♿", "ผู้สูงอายุ · ผู้พิการ"),
        "energy": ("🌱", "ประหยัดพลังงาน"),
    }
    try:
        import pandas as pd
        rows = []
        for key, (emoji, label) in label_map.items():
            c = comp.get(key) or {}
            status = c.get("status", "-")
            note = c.get("note", "")
            rows.append({
                "หมวด": f"{emoji} {label}",
                "สถานะ": f"{STATUS.get(status, '❔')} {status}",
                "หมายเหตุ": note[:80] + ("…" if len(note) > 80 else ""),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except Exception:
        for key, (emoji, label) in label_map.items():
            c = comp.get(key) or {}
            st.markdown(f"**{emoji} {label}** · {STATUS.get(c.get('status', 'warning'), '❔')} {c.get('status', '-')}")
            if c.get("note"):
                st.caption(c["note"])


PHASE_ORDER = [
    ("SD", "🧭", "Schematic Design"),
    ("DD", "📐", "Design Development"),
    ("CD", "📑", "Construction Documents"),
    ("CA", "🔨", "Construction Administration"),
]


def _phases(phases: dict):
    st.markdown(
        '<div class="eyebrow">DESIGN PHASES</div>'
        '<h2 style="margin-top:0;">Phases ของโครงการ</h2>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(PHASE_ORDER))
    total_weeks = 0
    for i, (key, emoji, label) in enumerate(PHASE_ORDER):
        p = phases.get(key) or {}
        weeks = p.get("duration_weeks") or 0
        total_weeks += weeks
        with cols[i]:
            st.markdown(
                f'<div style="background: var(--white); border: 1px solid var(--border); '
                f'border-radius: var(--radius); padding: 14px;">'
                f'<div style="font-size:0.7em; letter-spacing:0.1em; '
                f'color:var(--teak); font-weight:600; text-transform:uppercase;">{key}</div>'
                f'<div style="font-family:var(--font-display); font-weight:700; '
                f'font-size:1.05em; margin:4px 0 6px 0;">{emoji} {label}</div>'
                f'<div style="color:var(--muted); font-size:0.8em;">'
                f'⏱ <b>{weeks} สัปดาห์</b></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    if total_weeks:
        months = total_weeks / 4.33
        st.caption(f"รวมประมาณ **{total_weeks} สัปดาห์** (~{months:.1f} เดือน)")

    # Detail expanders · 1 per phase
    for key, emoji, label in PHASE_ORDER:
        p = phases.get(key) or {}
        tasks = p.get("tasks") or []
        delivs = p.get("deliverables") or []
        if not tasks and not delivs:
            continue
        weeks = p.get("duration_weeks") or 0
        with st.expander(f"{emoji} **{key} · {label}** · {weeks} สัปดาห์"):
            if tasks:
                st.markdown("**📋 Tasks:**")
                for t in tasks:
                    st.markdown(f"- {t}")
            if delivs:
                st.markdown("**📦 Deliverables:**")
                for d in delivs:
                    st.markdown(f"- {d}")


def _num(v, unit="", dec=1):
    if v is None:
        return "–"
    if isinstance(v, (int, float)):
        if dec == 0 or v == int(v):
            return f"{int(v):,}{unit}"
        return f"{v:,.{dec}f}{unit}"
    return str(v)


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


def _metrics(m: dict):
    st.markdown(
        '<div class="eyebrow">NUMBERS</div>'
        '<h2 style="margin-top:0;">ตัวเลขโครงการ</h2>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("พื้นที่ดิน", _num(m.get("land_area_sqm"), " ตร.ม.", 0))
    c2.metric("สร้างได้", _num(m.get("buildable_area_sqm"), " ตร.ม.", 0))
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
            c9.metric("ใช้สอย", _num(m["floor_area_sqm"], " ตร.ม.", 0))
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
        rows = [{
            "ชั้น": f"{e} {n}",
            "สถานะ": f"{STATUS.get(layers.get(k, {}).get('status', 'warning'), '❔')} {layers.get(k, {}).get('status', '-')}",
            "คะแนน": layers.get(k, {}).get("score", 0),
        } for k, e, n in LAYERS]
        st.dataframe(
            pd.DataFrame(rows), use_container_width=True, hide_index=True,
            column_config={"คะแนน": st.column_config.ProgressColumn(
                "คะแนน", min_value=0, max_value=100, format="%d")},
        )
    except Exception:
        pass
    for k, e, n in LAYERS:
        l = layers.get(k, {})
        findings = l.get("findings", [])
        if not findings:
            continue
        status_emoji = STATUS.get(l.get("status", "warning"), "❔")
        with st.expander(f"{e} {n} · {status_emoji} · {len(findings)} finding(s)"):
            for f in findings:
                sev = f.get("severity", "info")
                st.markdown(f"**{SEV.get(sev, 'ℹ')} {f.get('title', '-')}**")
                st.markdown(f.get("detail", ""))
                if f.get("citation"):
                    st.caption(f"📚 {f['citation']}")


def _rooms(rooms: list):
    st.markdown(
        f'<div class="eyebrow">ROOMS · {len(rooms)}</div>'
        '<h2 style="margin-top:0;">วิเคราะห์ห้อง</h2>',
        unsafe_allow_html=True,
    )
    try:
        import pandas as pd
        table = []
        for r in rooms:
            mn, mx = r.get("size_min"), r.get("size_max")
            size = f"{mn}-{mx} ตร.ม." if (mn and mx) else "–"
            table.append({
                "ห้อง": r.get("name", "-"),
                "ประเภท": r.get("type", "-"),
                "ขนาด": size,
                "ทิศ": r.get("orientation", "-") or "-",
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
        st.markdown(f"### 🚨 ประเด็น · {len(issues)}")
        for i in issues:
            sev = i.get("severity", "medium")
            st.markdown(f"**{i.get('rank', '-')}. {SEV.get(sev, '🟡')} {i.get('title', '-')}**")
            st.markdown(i.get("detail", ""))
            if i.get("action"):
                st.info(f"💡 {i['action']}")
            st.write("")
    with c2:
        st.markdown(f"### ⭐ จุดเด่น · {len(strengths)}")
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
# Markdown export (for downloads)
# ============================================================================

def to_markdown(data: dict) -> str:
    out = []
    s = data.get("summary", {})
    feas = s.get("feasibility", "-")
    out.append("## 📊 สรุป\n")
    out.append(f"- ความเป็นไปได้: {FEAS.get(feas, '❔')} {feas}")
    out.append(f"- คะแนน: {s.get('score', '-')}/100")
    if s.get("note"): out.append(f"- หมายเหตุ: {s['note']}")
    if s.get("concern"): out.append(f"- ⚠ ประเด็น: {s['concern']}")
    if s.get("strength"): out.append(f"- ⭐ จุดเด่น: {s['strength']}")
    out.append("")

    m = data.get("metrics", {})
    if m:
        out.append("## 📐 ตัวเลข\n| รายการ | ค่า |\n|---|---|")
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
    for k, e, n in LAYERS:
        l = data.get("layers", {}).get(k, {})
        if not l:
            continue
        out.append(f"### {e} {n} · {l.get('status', '-')} · {l.get('score', 0)}/100\n")
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

    comp = data.get("compliance") or {}
    if comp:
        out.append("## 📋 Compliance\n")
        labels = {
            "building_code": "พรบ.ควบคุมอาคาร",
            "zoning": "ผังเมือง",
            "parking": "ที่จอดรถ",
            "fire_egress": "บันไดหนีไฟ",
            "accessibility": "Universal design",
            "energy": "ประหยัดพลังงาน",
        }
        for k, lab in labels.items():
            c = comp.get(k) or {}
            if c:
                out.append(f"- **{lab}** · {c.get('status', '-')} · {c.get('note', '')}")
        out.append("")

    phases = data.get("phases") or {}
    if phases:
        out.append("## 🧭 Design Phases\n")
        for key in ["SD", "DD", "CD", "CA"]:
            p = phases.get(key) or {}
            if not p:
                continue
            out.append(f"### {key} · {p.get('label', key)} · {p.get('duration_weeks', 0)} สัปดาห์\n")
            for t in p.get("tasks", []):
                out.append(f"- {t}")
            if p.get("deliverables"):
                out.append("\n**Deliverables:**")
                for d in p["deliverables"]:
                    out.append(f"- {d}")
            out.append("")

    actions = data.get("actions", [])
    if actions:
        out.append("## 🎯 Next Actions\n| # | Action | โดย | เมื่อ |\n|---|---|---|---|")
        for a in actions:
            out.append(f"| {a.get('step', '-')} | {a.get('action', '-')} | {a.get('who', '-')} | {a.get('when', '-')} |")
        out.append("")

    return "\n".join(out)
