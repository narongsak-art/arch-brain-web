"""Follow-up chat · Q&A about a selected analysis · retains project context"""

import streamlit as st
from datetime import datetime

from components import history


def _chat_state_key(entry_id: str) -> str:
    return f"chat_msgs_{entry_id}"


def _init_chat(entry_id: str):
    key = _chat_state_key(entry_id)
    if key not in st.session_state:
        st.session_state[key] = []


def add_message(entry_id: str, role: str, content: str):
    _init_chat(entry_id)
    st.session_state[_chat_state_key(entry_id)].append({
        "role": role,
        "content": content,
        "ts": datetime.now().isoformat(),
    })


def get_messages(entry_id: str):
    _init_chat(entry_id)
    return st.session_state[_chat_state_key(entry_id)]


def build_chat_system_prompt(entry: dict, base_prompt: str, full_knowledge: str, kg: str) -> str:
    """System prompt for chat mode — includes project + previous analysis"""
    import json
    return f"""{base_prompt}

## บริบทการสนทนา

ผู้ใช้ถามต่อเกี่ยวกับโครงการที่วิเคราะห์ไปแล้ว · ตอบโดยอ้างอิงข้อมูลด้านล่างและ Knowledge Graph

### ข้อมูลโครงการ (JSON)
```json
{json.dumps(entry['project_data'], ensure_ascii=False, indent=2)}
```

### ผลวิเคราะห์เดิม
{entry['analysis']}

---

## ⭐ FULL KNOWLEDGE
{full_knowledge}

---

## Knowledge Graph Map
{kg}

---

⚠ คำตอบต้อง: (1) สั้น กระชับ ตอบตรงคำถาม (2) cite ตัวเลขกฎหมายจาก FULL KNOWLEDGE เท่านั้น (3) ถ้าไม่แน่ใจ บอก "ต้องตรวจเพิ่ม" แทนการเดา
"""


def render_chat_panel(call_llm_fn, provider: str, api_key: str, base_prompt: str, full_knowledge: str, kg: str):
    """Render chat UI. call_llm_fn(provider, api_key, system, user_text) → str"""
    entries = history.get_history()
    if not entries:
        st.info("💬 ยังไม่มีผลวิเคราะห์ · วิเคราะห์โครงการก่อนเพื่อถามเพิ่มเติม")
        return

    if not api_key:
        st.warning("⚠ ต้องใส่ API Key ที่ sidebar ก่อน")
        return

    st.markdown("### 💬 ถาม-ตอบต่อเนื่อง (Follow-up chat)")
    st.caption("เลือกโครงการ · ถามเพิ่มเติม · AI ตอบโดยอ้างผลวิเคราะห์เดิม + Knowledge Graph")

    # Pick an entry
    options = {e["id"]: f"{e['name']} · {e['province']} · {datetime.fromisoformat(e['timestamp']).strftime('%m-%d %H:%M')}" for e in entries}
    selected = st.selectbox(
        "เลือกโครงการ",
        options=list(options.keys()),
        format_func=lambda x: options[x],
        key="chat_entry",
    )

    entry = next(e for e in entries if e["id"] == selected)
    messages = get_messages(selected)

    # Controls
    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("🗑 ล้างแชท", use_container_width=True, key=f"chat_clear_{selected}"):
            st.session_state[_chat_state_key(selected)] = []
            st.rerun()

    # Render message history
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggested prompts if empty
    if not messages:
        st.markdown("**💡 คำถามตัวอย่าง:**")
        cols = st.columns(3)
        suggestions = [
            "FAR ของที่ดินนี้เท่าไหร่?",
            "ถ้าเพิ่มห้องพระ ต้องวางทิศไหน?",
            "ระยะร่นขั้นต่ำกี่เมตร?",
        ]
        for i, sug in enumerate(suggestions):
            with cols[i]:
                if st.button(sug, use_container_width=True, key=f"sug_{i}"):
                    _handle_user_message(selected, sug, entry, call_llm_fn, provider, api_key, base_prompt, full_knowledge, kg)
                    st.rerun()

    # Chat input
    user_input = st.chat_input("ถามอะไรก็ได้เกี่ยวกับโครงการนี้...")
    if user_input:
        _handle_user_message(selected, user_input, entry, call_llm_fn, provider, api_key, base_prompt, full_knowledge, kg)
        st.rerun()


def _handle_user_message(entry_id, user_text, entry, call_llm_fn, provider, api_key, base_prompt, full_knowledge, kg):
    add_message(entry_id, "user", user_text)

    # Build conversation context
    system = build_chat_system_prompt(entry, base_prompt, full_knowledge, kg)
    history_msgs = get_messages(entry_id)
    convo = "\n\n".join(
        f"{'ผู้ใช้' if m['role']=='user' else 'AI'}: {m['content']}"
        for m in history_msgs
    )

    try:
        with st.spinner("🧠 กำลังคิด..."):
            reply = call_llm_fn(provider, api_key, system, convo)
        add_message(entry_id, "assistant", reply)
    except Exception as e:
        add_message(entry_id, "assistant", f"❌ Error: {e}")
