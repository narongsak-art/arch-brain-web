"""Booking · จองนัดปรึกษากับสถาปนิกตัวจริง

Flow:
1. User กรอกฟอร์ม (ชื่อ email โทร บริการ วันเวลา รายละเอียด)
2. save เข้า session (log)
3. สร้าง mailto: link · user กดแล้ว email app เปิดพร้อมข้อความ
4. สร้าง .ics calendar file ให้ download ไปใส่ Google/Apple Calendar

No backend · no database. Everything happens client-side via
mailto: + .ics download.
"""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime, time, timedelta
from urllib.parse import quote

import streamlit as st


# ============================================================================
# Configuration
# ============================================================================

CONSULTANT_EMAIL = "narongsak.bimtts2004@gmail.com"
CONSULTANT_LINE = "@your-line-id"  # เปลี่ยนเป็น LINE ID จริง
BASE_PRICE = 2500  # บาท/ชั่วโมง

SERVICE_TYPES = {
    "intro": {
        "label": "Introductory call (30 นาที · ฟรี)",
        "duration_min": 30,
        "price": 0,
    },
    "review": {
        "label": "Plan review (60 นาที)",
        "duration_min": 60,
        "price": BASE_PRICE,
    },
    "consultation": {
        "label": "Design consultation (90 นาที)",
        "duration_min": 90,
        "price": int(BASE_PRICE * 1.5),
    },
    "full": {
        "label": "Full project consult (2 ชั่วโมง)",
        "duration_min": 120,
        "price": BASE_PRICE * 2,
    },
}

TIME_SLOTS = ["10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]


@dataclass
class Booking:
    name: str
    email: str
    phone: str
    service: str
    preferred_date: date
    preferred_time: str
    project_info: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def service_label(self) -> str:
        return SERVICE_TYPES[self.service]["label"]

    @property
    def duration_min(self) -> int:
        return SERVICE_TYPES[self.service]["duration_min"]

    @property
    def price(self) -> int:
        return SERVICE_TYPES[self.service]["price"]


# ============================================================================
# Storage
# ============================================================================

def _init():
    st.session_state.setdefault("bookings", [])


def save(b: Booking) -> dict:
    _init()
    # Convert to JSON-safe dict (date → string)
    d = asdict(b)
    d["preferred_date"] = b.preferred_date.isoformat()
    st.session_state["bookings"].insert(0, d)
    return d


def get_all() -> list:
    _init()
    return st.session_state["bookings"]


# ============================================================================
# mailto + .ics generation
# ============================================================================

def build_mailto(b: Booking) -> str:
    """Generate mailto: link that pre-fills an email to the consultant"""
    subject = f"[สมองจำลองสถาปนิก] จองปรึกษา · {b.name}"
    body = f"""สวัสดีครับ

ผมขอจองปรึกษาผ่านเว็ป สมองจำลองของสถาปนิก

── ข้อมูลผู้จอง ──
ชื่อ: {b.name}
อีเมล: {b.email}
โทร: {b.phone}

── บริการที่เลือก ──
{b.service_label}
วันที่ต้องการ: {b.preferred_date}
เวลา: {b.preferred_time}
ระยะเวลา: {b.duration_min} นาที
ราคา: {"ฟรี" if b.price == 0 else f"{b.price:,} บาท"}

── รายละเอียดโปรเจค ──
{b.project_info}

── ขอให้ติดต่อกลับ ──
กรุณาตอบเมลยืนยันวัน/เวลา

ขอบคุณครับ
"""
    return f"mailto:{CONSULTANT_EMAIL}?subject={quote(subject)}&body={quote(body)}"


def build_ics(b: Booking) -> bytes:
    """Generate .ics calendar file for download"""
    try:
        hour, minute = map(int, b.preferred_time.split(":"))
        start_dt = datetime.combine(b.preferred_date, time(hour, minute))
    except Exception:
        start_dt = datetime.combine(b.preferred_date, time(10, 0))

    end_dt = start_dt + timedelta(minutes=b.duration_min)
    fmt = "%Y%m%dT%H%M%S"

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//arch-brain-web//consult//TH
BEGIN:VEVENT
UID:{b.created_at}@arch-brain
DTSTAMP:{datetime.now().strftime(fmt)}
DTSTART:{start_dt.strftime(fmt)}
DTEND:{end_dt.strftime(fmt)}
SUMMARY:สถาปนิก Consultation · {b.service_label}
DESCRIPTION:ผู้จอง {b.name}\\n{b.project_info}
LOCATION:Online / Office TBC
ORGANIZER;CN=Architect:MAILTO:{CONSULTANT_EMAIL}
ATTENDEE;CN={b.name};RSVP=TRUE:MAILTO:{b.email}
STATUS:TENTATIVE
END:VEVENT
END:VCALENDAR
"""
    return ics.encode("utf-8")


# ============================================================================
# UI
# ============================================================================

def render_panel():
    """Full booking panel · form + confirmation + history"""
    st.markdown("### 📅 จองปรึกษาสถาปนิก")
    st.caption(
        "AI ช่วยวิเคราะห์เบื้องต้น · แต่บางเรื่องต้องคุยกับสถาปนิกตัวจริง · "
        "จองนัดเพื่อรับคำแนะนำเฉพาะโปรเจคคุณ"
    )

    _render_form()

    # Show confirmation if latest booking exists
    last = st.session_state.get("_last_booking")
    if last:
        st.divider()
        _render_confirmation(last)

    # History
    if get_all():
        st.divider()
        _render_history()


def _service_option_label(key: str) -> str:
    cfg = SERVICE_TYPES[key]
    price_str = "ฟรี" if cfg["price"] == 0 else f"{cfg['price']:,} บาท"
    return f"{cfg['label']} · {price_str}"


def _render_form():
    """Booking form"""
    # Service selection
    st.markdown("#### 1️⃣ เลือกบริการ")
    service_key = st.radio(
        "ประเภทการปรึกษา",
        options=list(SERVICE_TYPES.keys()),
        format_func=_service_option_label,
        key="bk_service",
    )
    cfg = SERVICE_TYPES[service_key]
    c1, c2, c3 = st.columns(3)
    c1.metric("ราคา", "ฟรี" if cfg["price"] == 0 else f"{cfg['price']:,} บาท")
    c2.metric("ระยะเวลา", f"{cfg['duration_min']} นาที")
    c3.metric("รูปแบบ", "Online / Office")

    # Contact
    st.markdown("#### 2️⃣ ข้อมูลติดต่อ")
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input("ชื่อ-สกุล *", key="bk_name")
        phone = st.text_input("เบอร์โทร *", key="bk_phone")
    with col_b:
        email = st.text_input("อีเมล *", key="bk_email", placeholder="you@example.com")

    # Schedule
    st.markdown("#### 3️⃣ วัน-เวลาที่สะดวก")
    col_d, col_t = st.columns(2)
    with col_d:
        min_date = date.today() + timedelta(days=1)
        max_date = date.today() + timedelta(days=30)
        preferred_date = st.date_input(
            "วันที่ต้องการ",
            value=min_date, min_value=min_date, max_value=max_date,
            key="bk_date",
        )
    with col_t:
        preferred_time = st.selectbox(
            "ช่วงเวลา", options=TIME_SLOTS, key="bk_time",
        )

    # Project info
    st.markdown("#### 4️⃣ เกี่ยวกับโปรเจค")
    project_info = st.text_area(
        "อธิบายโปรเจคโดยย่อ *",
        placeholder=(
            "เช่น · บ้านเดี่ยว 2 ชั้น 200 ตร.ม. · ที่ดิน ย.3 · งบ 8 ล้าน · "
            "สนใจ passive design · มีผู้สูงอายุในครอบครัว"
        ),
        height=120,
        key="bk_project",
    )

    st.divider()
    can_submit = all([name.strip(), email.strip(), phone.strip(), project_info.strip()])

    if st.button(
        "📤 ส่งคำขอจอง",
        type="primary", use_container_width=True, disabled=not can_submit,
        key="bk_submit",
    ):
        b = Booking(
            name=name.strip(), email=email.strip(), phone=phone.strip(),
            service=service_key, preferred_date=preferred_date,
            preferred_time=preferred_time, project_info=project_info.strip(),
        )
        saved = save(b)
        st.session_state["_last_booking"] = b  # dataclass for building mailto/ics
        st.rerun()

    if not can_submit:
        st.caption("กรอกข้อมูลทุกช่องที่มี * ก่อนส่ง")


def _render_confirmation(b: Booking):
    st.success("✅ บันทึกคำขอเรียบร้อย · ทำขั้นต่อไปเพื่อติดต่อ")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📧 Step 1: ส่ง email ยืนยัน")
        mailto = build_mailto(b)
        st.markdown(
            f'''<a href="{mailto}" target="_blank" style="text-decoration:none;">
<button style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white;
padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px;
cursor: pointer; width: 100%; font-weight: 600;">📤 เปิดแอพอีเมล · ส่ง booking</button>
</a>''',
            unsafe_allow_html=True,
        )
        st.caption("กดแล้วจะเปิดแอพอีเมลพร้อมข้อความที่เตรียมไว้")

    with c2:
        st.markdown("### 📆 Step 2: บันทึกลงปฏิทิน")
        ics_bytes = build_ics(b)
        st.download_button(
            "📥 ดาวน์โหลด .ics (Google/Apple Calendar)",
            data=ics_bytes,
            file_name=f"consultation-{b.preferred_date}.ics",
            mime="text/calendar",
            use_container_width=True,
            key="bk_ics_dl",
        )
        st.caption("เปิดไฟล์แล้วจะเพิ่มเข้า Calendar โดยอัตโนมัติ")

    st.markdown("---")
    st.markdown("### 💬 หรือติดต่อช่องทางอื่น")
    c3, c4, c5 = st.columns(3)
    c3.markdown(f"📧 [Email ตรง](mailto:{CONSULTANT_EMAIL})")
    c4.markdown(f"📱 [LINE Official]({CONSULTANT_LINE})")
    c5.markdown("📞 0XX-XXX-XXXX")


def _render_history():
    bookings = get_all()
    st.markdown(f"### 📋 คำขอที่ส่งไปแล้ว · {len(bookings)} รายการ")
    for b in bookings[:10]:
        title = f"{b['preferred_date']} {b['preferred_time']} · {b['name']} · {b['service']}"
        with st.expander(title):
            st.json(b)
