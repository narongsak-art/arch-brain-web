"""Compare · side-by-side view of 2 analyses

Picks 2 entries from history · shows:
- Brief diff table (highlights what's different)
- Feasibility + score side by side
- Layer scores side by side
- Two scrollable containers with full structured render
"""

from datetime import datetime

import streamlit as st

from components import history, analysis


FEAS = {"green": "🟢", "yellow": "🟡", "red": "🔴"}

# Fields to show in the diff table (in order)
_DIFF_FIELDS = [
    ("land_w", "กว้าง (ม.)"),
    ("land_d", "ลึก (ม.)"),
    ("land_area", "พื้นที่ดิน (ตร.ม.)"),
    ("province", "จังหวัด"),
    ("zone", "สีผังเมือง"),
    ("street_w", "ถนนติด (ม.)"),
    ("family_size", "สมาชิก"),
    ("has_elderly", "ผู้สูงอายุ"),
    ("floors", "ชั้น"),
    ("bedrooms", "ห้องนอน"),
    ("budget", "งบ (ลบ.)"),
    ("fengshui", "ฮวงจุ้ย"),
    ("special", "ข้อกำหนดพิเศษ"),
]


def render_panel():
    entries = history.get_all()
    if len(entries) < 2:
        st.info(
            f"🔀 ต้องมีประวัติอย่างน้อย **2 รายการ** เพื่อเปรียบเทียบ "
            f"(ตอนนี้มี {len(entries)} รายการ)"
        )
        return

    st.markdown("### 🔀 เปรียบเทียบ 2 โครงการ")

    # Entry pickers
    options = {
        e["id"]: f"{e['name']} · {e['province']} · {_short_ts(e['ts'])}"
        for e in entries
    }
    ids = list(options.keys())
    c_a, c_b = st.columns(2)
    with c_a:
        id_a = st.selectbox(
            "โครงการ A", options=ids,
            format_func=lambda k: options[k],
            key="cmp_a",
        )
    with c_b:
        # Default B to the 2nd option
        default_idx = 1 if len(ids) > 1 else 0
        id_b = st.selectbox(
            "โครงการ B", options=ids,
            format_func=lambda k: options[k],
            index=default_idx,
            key="cmp_b",
        )

    if id_a == id_b:
        st.warning("⚠ เลือกคนละโครงการ")
        return

    entry_a = next(e for e in entries if e["id"] == id_a)
    entry_b = next(e for e in entries if e["id"] == id_b)

    # 1. Diff table of project data
    st.divider()
    st.markdown("#### 📋 ความต่างของ brief")
    _render_diff_table(entry_a.get("project_data") or {}, entry_b.get("project_data") or {})

    # 2. Summary side by side
    st.divider()
    st.markdown("#### 📊 สรุป + ระยะคะแนน")
    _render_summary_row(entry_a, entry_b)

    # 3. Layer scores side by side
    _render_layers_row(entry_a, entry_b)

    # 4. Full analysis side by side in scrollable containers
    st.divider()
    st.markdown("#### 📖 ผลวิเคราะห์เต็ม")
    col_aa, col_bb = st.columns(2)
    with col_aa:
        st.markdown(f"##### 🟦 {entry_a['name']}")
        st.caption(f"_{entry_a.get('provider', '-')} · {_short_ts(entry_a['ts'])}_")
        with st.container(height=700, border=True):
            if entry_a.get("result"):
                analysis.render(entry_a["result"])
            elif entry_a.get("raw_text"):
                st.markdown(entry_a["raw_text"])
            else:
                st.caption("(ไม่มีข้อมูล)")
    with col_bb:
        st.markdown(f"##### 🟥 {entry_b['name']}")
        st.caption(f"_{entry_b.get('provider', '-')} · {_short_ts(entry_b['ts'])}_")
        with st.container(height=700, border=True):
            if entry_b.get("result"):
                analysis.render(entry_b["result"])
            elif entry_b.get("raw_text"):
                st.markdown(entry_b["raw_text"])
            else:
                st.caption("(ไม่มีข้อมูล)")


# ============================================================================
# Parts
# ============================================================================

def _render_diff_table(pa: dict, pb: dict):
    try:
        import pandas as pd
    except ImportError:
        st.warning("pandas ไม่ติดตั้ง · ข้าม table")
        return

    rows = []
    diff_count = 0
    for key, label in _DIFF_FIELDS:
        va = pa.get(key)
        vb = pb.get(key)
        same = va == vb
        marker = "" if same else "⚠"
        if not same:
            diff_count += 1
        rows.append({
            "Field": label,
            f"A · {pa.get('name', '-')}": "–" if va is None else str(va),
            f"B · {pb.get('name', '-')}": "–" if vb is None else str(vb),
            "Δ": marker,
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"ต่าง **{diff_count}/{len(_DIFF_FIELDS)}** ฟิลด์")


def _render_summary_row(entry_a: dict, entry_b: dict):
    def summary(e):
        r = e.get("result") or {}
        s = r.get("summary") or {}
        return s.get("feasibility"), s.get("score"), s.get("concern"), s.get("strength")

    fa, sa, ca, st_a = summary(entry_a)
    fb, sb, cb, st_b = summary(entry_b)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"##### 🟦 {entry_a['name']}")
        cc1, cc2 = st.columns(2)
        cc1.metric("ความเป็นไปได้", f"{FEAS.get(fa, '❔')} {fa or '-'}")
        cc2.metric("คะแนน", f"{sa if sa is not None else '-'}/100")
        if ca:
            st.error(f"⚠ {ca}")
        if st_a:
            st.success(f"⭐ {st_a}")
    with c2:
        st.markdown(f"##### 🟥 {entry_b['name']}")
        cc1, cc2 = st.columns(2)
        cc1.metric("ความเป็นไปได้", f"{FEAS.get(fb, '❔')} {fb or '-'}")
        cc2.metric("คะแนน", f"{sb if sb is not None else '-'}/100")
        if cb:
            st.error(f"⚠ {cb}")
        if st_b:
            st.success(f"⭐ {st_b}")


def _render_layers_row(entry_a: dict, entry_b: dict):
    """Bar-like comparison of 5-layer scores"""
    la = (entry_a.get("result") or {}).get("layers") or {}
    lb = (entry_b.get("result") or {}).get("layers") or {}
    if not la and not lb:
        return

    st.markdown("#### 🧩 5-Layer Scores")
    try:
        import pandas as pd
        rows = []
        for key, emoji, name in [
            ("law", "🏛", "กฎหมาย"),
            ("eng", "🔧", "วิศวกรรม"),
            ("design", "🎨", "ออกแบบ"),
            ("thai", "🪷", "วัฒนธรรมไทย"),
            ("fengshui", "☯", "ฮวงจุ้ย"),
        ]:
            rows.append({
                "ชั้น": f"{emoji} {name}",
                f"A · {entry_a['name']}": la.get(key, {}).get("score", 0),
                f"B · {entry_b['name']}": lb.get(key, {}).get("score", 0),
            })
        df = pd.DataFrame(rows)
        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={
                f"A · {entry_a['name']}": st.column_config.ProgressColumn(
                    f"🟦 A", min_value=0, max_value=100, format="%d",
                ),
                f"B · {entry_b['name']}": st.column_config.ProgressColumn(
                    f"🟥 B", min_value=0, max_value=100, format="%d",
                ),
            },
        )
    except Exception:
        pass


def _short_ts(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%m-%d %H:%M")
    except Exception:
        return (ts or "")[:16]
