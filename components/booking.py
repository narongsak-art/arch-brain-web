"""
Consultation booking system

Flow:
1. User fills form (name · email · project · datetime)
2. Save to session (in-memory log)
3. Build mailto: link · user can trigger email
4. Show confirmation + calendar export (.ics)

No backend DB · uses urllib mailto + session.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime, date, time, timedelta
from typing import Optional
from urllib.parse import quote
import streamlit as st

from components import tiers


CONSULTANT_EMAIL = "narongsak.bimtts2004@gmail.com"
CONSULTANT_LINE = "@your-line-id"  # เปลี่ยนเป็น LINE ID จริง
BASE_PRICE = 2500  # baht per 1-hour consultation


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
        "price": BASE_PRICE * 1.5,
    },
    "full": {
        "label": "Full project consult (2 ชั่วโมง)",
        "duration_min": 120,
        "price": BASE_PRICE * 2,
    },
}


@dataclass
class Booking:
    name: str
    email: str
    phone: str
    service: str
    preferred_date: date
    preferred_time: str
    project_info: str
    tier: str = "free"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def discount_pct(self) -> int:
        cfg = tiers.tier_config(self.tier)
        return cfg["limits"].get("consultation_discount", 0)

    @property
    def base_price(self) -> float:
        return SERVICE_TYPES[self.service]["price"]

    @property
    def final_price(self) -> float:
        return self.base_price * (1 - self.discount_pct / 100)

    @property
    def service_label(self) -> str:
        return SERVICE_TYPES[self.service]["label"]

    @property
    def duration_min(self) -> int:
        return SERVICE_TYPES[self.service]["duration_min"]


# ============================================================================
# Session state
# ============================================================================

def _init_state():
    if "bookings" not in st.session_state:
        st.session_state["bookings"] = []


def save_booking(booking: Booking):
    _init_state()
    st.session_state["bookings"].append(asdict(booking))


def get_bookings() -> list:
    _init_state()
    return st.session_state["bookings"]


# ============================================================================
# Email + Calendar generation
# ============================================================================

def build_mailto_link(booking: Booking) -> str:
    """Generate mailto: link that pre-fills an email to consultant"""
    subject = f"[สมองจำลองสถาปนิก] จองปรึกษา · {booking.name}"

    body = f"""สวัสดีครับ

ผมขอจองปรึกษาผ่าน สมองจำลองของสถาปนิก

── ข้อมูลผู้จอง ──
ชื่อ: {booking.name}
อีเมล: {booking.email}
โทร: {booking.phone}

── บริการที่เลือก ──
{booking.service_label}
วันที่ต้องการ: {booking.preferred_date}
เวลา: {booking.preferred_time}
ระยะเวลา: {booking.duration_min} นาที
ราคา: {booking.final_price:,.0f} บาท{' (ส่วนลด Pro ' + str(booking.discount_pct) + '%)' if booking.discount_pct else ''}

── รายละเอียดโปรเจค ──
{booking.project_info}

── ต้องการให้ติดต่อกลับ ──
กรุณาตอบเมลยืนยันวัน/เวลา

ขอบคุณครับ
"""

    mailto = f"mailto:{CONSULTANT_EMAIL}?subject={quote(subject)}&body={quote(body)}"
    return mailto


def build_ics_file(booking: Booking) -> bytes:
    """Generate .ics calendar file for download"""
    try:
        # Parse time
        hour, minute = map(int, booking.preferred_time.split(":"))
        start_dt = datetime.combine(booking.preferred_date, time(hour, minute))
    except Exception:
        start_dt = datetime.combine(booking.preferred_date, time(10, 0))

    end_dt = start_dt + timedelta(minutes=booking.duration_min)

    fmt = "%Y%m%dT%H%M%S"

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//สมองจำลองสถาปนิก//consult//TH
BEGIN:VEVENT
UID:{booking.created_at}@arch-brain
DTSTAMP:{datetime.now().strftime(fmt)}
DTSTART:{start_dt.strftime(fmt)}
DTEND:{end_dt.strftime(fmt)}
SUMMARY:สถาปนิก Consultation · {booking.service_label}
DESCRIPTION:ผู้จอง {booking.name}\\n{booking.project_info}
LOCATION:Online / Office TBC
ORGANIZER;CN=Architect:MAILTO:{CONSULTANT_EMAIL}
ATTENDEE;CN={booking.name};RSVP=TRUE:MAILTO:{booking.email}
STATUS:TENTATIVE
END:VEVENT
END:VCALENDAR
"""
    return ics.encode("utf-8")


# ============================================================================
# UI Components
# ============================================================================

def render_booking_form():
    """Render full booking form"""
    st.header("📅 จองปรึกษาสถาปนิก")

    user_tier = tiers.tier_config()
    discount = user_tier["limits"].get("consultation_discount", 0)

    if discount > 0:
        st.success(f"🎉 คุณเป็น **{user_tier['name']}** · ได้ส่วนลด **{discount}%**")

    # Service selection
    st.subheader("1️⃣ เลือกบริการ")
    def _service_label(k):
        cfg = SERVICE_TYPES[k]
        price_str = "ฟรี" if cfg["price"] == 0 else f"{cfg['price']:,.0f} บาท"
        return f"{cfg['label']} · {price_str}"

    service_key = st.radio(
        "ประเภทการปรึกษา",
        options=list(SERVICE_TYPES.keys()),
        format_func=_service_label,
        key="booking_service",
    )

    base_price = SERVICE_TYPES[service_key]["price"]
    final_price = base_price * (1 - discount / 100)
    duration = SERVICE_TYPES[service_key]["duration_min"]

    col1, col2, col3 = st.columns(3)
    col1.metric("ราคาปกติ", f"{base_price:,.0f} บาท")
    if discount > 0:
        col2.metric("ส่วนลด Pro", f"-{discount}%", delta=f"-{base_price * discount / 100:,.0f} บาท")
    col3.metric("ราคาสุทธิ", f"{final_price:,.0f} บาท")

    st.markdown(f"⏱ ระยะเวลา: **{duration} นาที**")

    # Contact info
    st.subheader("2️⃣ ข้อมูลติดต่อ")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("ชื่อ-สกุล *", key="booking_name")
        phone = st.text_input("เบอร์โทร *", key="booking_phone")
    with col2:
        email = st.text_input("อีเมล *", key="booking_email", placeholder="you@example.com")

    # Schedule
    st.subheader("3️⃣ วัน-เวลาที่สะดวก")
    col1, col2 = st.columns(2)
    with col1:
        min_date = date.today() + timedelta(days=1)
        max_date = date.today() + timedelta(days=30)
        preferred_date = st.date_input(
            "วันที่ต้องการ",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="booking_date",
        )
    with col2:
        time_slots = [
            "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00",
        ]
        preferred_time = st.selectbox("ช่วงเวลา", options=time_slots, key="booking_time")

    # Project info
    st.subheader("4️⃣ เกี่ยวกับโปรเจค")
    project_info = st.text_area(
        "อธิบายโปรเจคโดยย่อ",
        placeholder="เช่น บ้านเดี่ยว 2 ชั้น 200 ตร.ม. · ที่ดิน ย.3 · งบ 8 ล้าน · สนใจ passive design",
        height=120,
        key="booking_project",
    )

    st.markdown("---")

    # Submit
    can_submit = all([name, email, phone, project_info])

    if st.button(
        "📤 ส่งคำขอ + สร้าง email ให้",
        type="primary",
        use_container_width=True,
        disabled=not can_submit,
    ):
        booking = Booking(
            name=name,
            email=email,
            phone=phone,
            service=service_key,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            project_info=project_info,
            tier=tiers.get_tier(),
        )
        save_booking(booking)
        st.session_state["_last_booking"] = booking
        st.rerun()

    if not can_submit:
        st.caption("กรอกข้อมูลให้ครบก่อนส่ง (ช่องที่มี *)")

    # Show confirmation if just submitted
    if st.session_state.get("_last_booking"):
        _render_confirmation(st.session_state["_last_booking"])


def _render_confirmation(booking: Booking):
    """Confirmation panel after booking"""
    st.markdown("---")
    st.success("✅ บันทึกคำขอเรียบร้อย · ทำขั้นต่อไปได้เลย")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📧 Step 1: ส่ง email ยืนยัน")
        mailto = build_mailto_link(booking)
        st.markdown(f"""
<a href="{mailto}" target="_blank">
  <button style="
    background: #4285f4; color: white; padding: 12px 24px;
    border: none; border-radius: 8px; font-size: 16px; cursor: pointer;
    width: 100%;">
    📤 เปิดแอพอีเมล · ส่ง booking
  </button>
</a>
""", unsafe_allow_html=True)
        st.caption("กดแล้วจะเปิดแอพอีเมลพร้อมข้อความที่เตรียมไว้")

    with col2:
        st.markdown("### 📆 Step 2: บันทึกลงปฏิทิน")
        ics_bytes = build_ics_file(booking)
        st.download_button(
            "📥 ดาวน์โหลด .ics (Google/Apple Calendar)",
            data=ics_bytes,
            file_name=f"consultation-{booking.preferred_date}.ics",
            mime="text/calendar",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("### หรือ · ติดต่อช่องทางอื่น")

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"📧 [Email โดยตรง](mailto:{CONSULTANT_EMAIL})")
    col2.markdown(f"📱 [LINE Official]({CONSULTANT_LINE})")
    col3.markdown("📞 โทร: 0XX-XXX-XXXX")


def render_bookings_history():
    """Show bookings in this session"""
    bookings = get_bookings()
    if not bookings:
        st.info("ยังไม่มีการจอง")
        return

    st.markdown(f"### 📋 คำขอของคุณ (session นี้ · {len(bookings)} รายการ)")
    for b in reversed(bookings):
        with st.expander(f"{b['preferred_date']} · {b['service']} · {b['name']}"):
            st.json(b)
