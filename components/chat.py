"""Chat follow-up · ถาม AI เพิ่มเติมเกี่ยวกับผลวิเคราะห์

Each chat is scoped to a specific history entry (analysis).
Messages stored in session_state: chat_msgs_{entry_id} = [{role, content, ts}]

System prompt includes:
- base system prompt
- full project_data
- the original analysis (structured or raw)
- full_knowledge + kg (for citations)
"""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from components import history, llm


# ============================================================================
# Message storage
# ============================================================================

def _msg_key(entry_id: str) -> str:
    return f"chat_msgs_{entry_id}"


def get_messages(entry_id: str) -> list:
    key = _msg_key(entry_id)
    return st.session_state.setdefault(key, [])


def add_message(entry_id: str, role: str, content: str):
    get_messages(entry_id).append({
        "role": role,
        "content": content,
        "ts": datetime.now().isoformat(),
    })


def clear_messages(entry_id: str):
    st.session_state[_msg_key(entry_id)] = []


# ============================================================================
# Prompt
# ============================================================================

def _load_kg() -> str:
    p = Path(__file__).parent.parent / "kg-compact.json"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _load_full_knowledge() -> str:
    p = Path(__file__).parent.parent / "full-knowledge.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _load_base_prompt() -> str:
    p = Path(__file__).parent.parent / "system-prompt.md"
    return p.read_text(encoding="utf-8") if p.exists() else (
        "You are an architect's assistant specialized in Thai residential architecture."
    )


def _format_prior_analysis(entry: dict) -> str:
    """Prefer structured result (markdown summary) over raw text"""
    if entry.get("result"):
        from components import analysis
        return analysis.to_markdown(entry["result"])
    return entry.get("raw_text", "") or "(no prior analysis)"


def build_chat_system_prompt(entry: dict) -> str:
    """System prompt tailored to one analysis · includes knowledge base for citations"""
    pd = entry.get("project_data") or {}
    prior = _format_prior_analysis(entry)

    return f"""{_load_base_prompt()}

## 🗣 บริบทการสนทนา

ผู้ใช้ถามต่อเกี่ยวกับโครงการที่คุณวิเคราะห์ไปแล้ว · ตอบสั้น · กระชับ · อ้างอิงข้อมูลด้านล่าง + KG

### ข้อมูลโครงการ
```json
{json.dumps(pd, ensure_ascii=False, indent=2)}
```

### ผลวิเคราะห์เดิม
{prior}

---

## ⭐ FULL KNOWLEDGE (cite ตัวเลขกฎหมาย)
{_load_full_knowledge()}

---

## Knowledge Graph Map
{_load_kg()}

---

## ⚠ กฎการตอบ
- สั้น กระชับ ตอบตรงคำถาม
- Cite ตัวเลขกฎหมายจาก FULL KNOWLEDGE เท่านั้น · ห้ามสร้างเอง
- ถ้าไม่แน่ใจ · บอก "ต้องตรวจเพิ่ม" แทนการเดา
- ตอบเป็นไทย (ศัพท์เทคนิคอังกฤษได้)
- ไม่ต้องเขียน JSON · ตอบเป็นข้อความธรรมดาได้
"""


def _format_convo(messages: list) -> str:
    """Convert message history into a flat text conversation for LLM"""
    lines = []
    for m in messages:
        prefix = "ผู้ใช้" if m["role"] == "user" else "AI"
        lines.append(f"{prefix}: {m['content']}")
    return "\n\n".join(lines)


def _call_llm(messages: list, entry: dict, api_key: str, provider: str, model: str) -> str:
    """Send conversation to LLM · returns reply text"""
    system = build_chat_system_prompt(entry)
    user_text = _format_convo(messages)
    if provider == "gemini":
        return llm.call_gemini(api_key, system, user_text, model=model)
    return llm.call_claude(api_key, system, user_text)


# ============================================================================
# UI
# ============================================================================

SUGGESTED_QUESTIONS = [
    "FAR ของเขตนี้เท่าไหร่ · ใช้ได้เต็มไหม?",
    "ถ้าเพิ่มห้องพระ · ควรวางทิศไหน?",
    "ระยะร่นขั้นต่ำจากที่ดินข้างเคียงกี่เมตร?",
    "ประเด็นฮวงจุ้ยที่ต้องระวังใน layout นี้?",
    "ค่าก่อสร้างประมาณกี่ล้าน · grade ไหน?",
    "ถ้างบลด 30% · ควรตัดอะไรก่อน?",
]


def render_panel(api_key: str, provider: str, model: str = "gemini-2.5-flash"):
    """Full chat tab · pick analysis → chat window + input"""
    st.markdown("### 💬 ถามเพิ่มเติม (follow-up chat)")
    st.caption(
        "เลือกโครงการที่เคยวิเคราะห์ · ถามรายละเอียด · AI ตอบโดยอ้างผลเดิม + Knowledge Graph"
    )

    entries = history.get_all()
    if not entries:
        st.info("ยังไม่มีผลวิเคราะห์ · วิเคราะห์โปรเจคก่อนเพื่อเปิดใช้ chat")
        return

    if not api_key:
        st.warning("⚠ ใส่ API Key ที่ sidebar ก่อน")
        return

    # Entry picker
    options = {
        e["id"]: f"{e['name']} · {e['province']} · {_short_ts(e['ts'])}"
        for e in entries
    }
    selected_id = st.selectbox(
        "โครงการ",
        options=list(options.keys()),
        format_func=lambda k: options[k],
        key="chat_entry_pick",
    )
    entry = next(e for e in entries if e["id"] == selected_id)
    messages = get_messages(selected_id)

    # Clear button
    col_info, col_clear = st.columns([4, 1])
    col_info.caption(f"🧠 บริบท: brief + ผลวิเคราะห์ + KG 104 nodes")
    if col_clear.button("🗑 ล้างแชท", use_container_width=True, key=f"chat_clear_{selected_id}"):
        clear_messages(selected_id)
        st.rerun()

    # Render history
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested questions (only when empty)
    if not messages:
        st.markdown("**💡 คำถามตัวอย่าง:**")
        cols = st.columns(3)
        for i, sug in enumerate(SUGGESTED_QUESTIONS[:3]):
            with cols[i]:
                if st.button(sug, use_container_width=True, key=f"chat_sug_top_{i}"):
                    _handle_user_message(selected_id, sug, entry, api_key, provider, model)
                    st.rerun()
        cols = st.columns(3)
        for i, sug in enumerate(SUGGESTED_QUESTIONS[3:6]):
            with cols[i]:
                if st.button(sug, use_container_width=True, key=f"chat_sug_bot_{i}"):
                    _handle_user_message(selected_id, sug, entry, api_key, provider, model)
                    st.rerun()

    # Input bar
    user_input = st.chat_input("ถามอะไรก็ได้เกี่ยวกับโครงการนี้...")
    if user_input:
        _handle_user_message(selected_id, user_input, entry, api_key, provider, model)
        st.rerun()


def _handle_user_message(entry_id: str, user_text: str, entry: dict,
                         api_key: str, provider: str, model: str):
    add_message(entry_id, "user", user_text)
    try:
        with st.spinner("🧠 กำลังคิด..."):
            reply = _call_llm(get_messages(entry_id), entry, api_key, provider, model)
    except Exception as e:
        reply = f"❌ Error: {e}"
    add_message(entry_id, "assistant", reply)


def _short_ts(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%m-%d %H:%M")
    except Exception:
        return ts[:16]
