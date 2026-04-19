# คู่มือใช้งาน · สมองจำลองของสถาปนิก

คู่มือสำหรับ**ผู้ใช้ทั่วไป** (เจ้าของบ้าน · สถาปนิก · นักเรียน) · ฉบับปรับปรุง 2026-04-20

> 🌐 เว็ปไซต์: https://arch-brain-narongsak.streamlit.app

---

## 🚀 เริ่มต้นใน 3 ขั้นตอน

### 1️⃣ รับ API key (ฟรี)
- เปิด https://aistudio.google.com/apikey
- Login ด้วย Google account
- กด **"Create API key"** → copy key
- **ไม่ต้องใส่ credit card** · ได้ 1,500 ครั้ง/วัน

### 2️⃣ ใส่ key ที่ sidebar (ซ้ายของเว็ป)
- Paste key ในช่อง **"Gemini API Key"**
- เลือก Model (แนะนำ **Gemini 2.5 Flash**)

### 3️⃣ กรอกข้อมูลโปรเจค → วิเคราะห์
- กดปุ่ม preset เร็วๆ: 🏘 ทาวน์เฮาส์ / 🏠 บ้านเดี่ยวเล็ก / 🏡 บ้านเดี่ยวใหญ่ / 🏛 บ้านหรู / 🏙 บ้านเล็ก กทม.
- หรือกรอกเอง (กว้าง · ลึก · จังหวัด · เขต · ครอบครัว · งบ · ฮวงจุ้ย · รายละเอียด)
- Upload แปลน (optional)
- กด **🔍 วิเคราะห์โครงการ** · รอ ~30-60 วิ

---

## 📊 อ่านผลวิเคราะห์

AI ตอบเป็น **structured output** · แบ่งเป็น section:

### 1. 📊 สรุปผลวิเคราะห์
- **Feasibility:** 🟢 ทำได้เลย · 🟡 ระวัง · 🔴 ต้องปรับ
- **คะแนน:** 0-100
- **ประเด็นหลัก** + **จุดเด่น** (1 ข้อแต่ละอัน)

### 2. 📐 ตัวเลขโครงการ (8-10 metrics)
FAR (allowed vs ใช้จริง) · OSR % · ระยะร่น · ความสูง · พื้นที่ใช้สอย · ค่าก่อสร้างประมาณ

### 3. 🧩 5-Layer Analysis
**Progress bars** ต่อชั้น:
- 🏛 กฎหมาย · 🔧 วิศวกรรม · 🎨 ออกแบบ · 🪷 วัฒนธรรมไทย · ☯ ฮวงจุ้ย
- Expander แต่ละชั้น → ดู findings (severity + citation ที่มา)

### 4. 🚪 วิเคราะห์ห้อง (6-10 ห้อง)
แต่ละห้อง:
- ขนาดแนะนำ (min-max ตร.ม.)
- ทิศที่ดีที่สุด (+เหตุผล)
- หมายเหตุวัฒนธรรมไทย + ฮวงจุ้ย
- Key points + ปัญหาเฉพาะ

### 5. 🚨 Top Issues · ⭐ Top Strengths
ประเด็นสำคัญ 3 ข้อต่ออัน · พร้อม action แนะนำ

### 6. 🎯 Next Actions
ตาราง Step / Action / โดย / เมื่อ

---

## 🛠 8 tabs ที่ใช้ประโยชน์ได้

### 📚 ประวัติ (N)
- ทุกการวิเคราะห์ใน session นี้ถูกเก็บ
- ปุ่มต่อ entry: 🔄 ใช้เป็นผลปัจจุบัน · 📥 .md · 🗑 ลบ
- 🗑 ล้างทั้งหมด
- **เตือน:** refresh page = ประวัติหาย · ใช้ **💾 Save/Load** เพื่อเก็บเป็น .json

### 💬 Chat
- เลือก analysis จากประวัติ → chat ต่อ
- **6 คำถามตัวอย่าง** กดเร็วได้ (FAR · ห้องพระ · ระยะร่น · ฮวงจุ้ย · ค่าก่อสร้าง · ตัดงบ)
- AI ตอบโดยอ้างอิงผลเดิม + Knowledge Graph 104 nodes
- ถามต่อได้ไม่จำกัด (Pro) · 5 ต่อ session (Free)

### 🔀 เปรียบเทียบ
- เลือก 2 projects → side-by-side
- **Brief diff table** · ช่องไหนต่างขึ้น ⚠
- **5-Layer bars** เทียบคะแนน
- Full analysis scrollable 2 columns

### 💡 ช่วยเติม
- **Tab 1 "เขียนเรื่องใหม่":**
  - เลือก **4 ประเภท:** 📝 แก้ไข · 💡 เสนอ · 🏗 เคสจริง · ❓ คำถาม
  - เลือก **12 หัวข้อ:** กฎหมาย · โครงสร้าง · MEP · ออกแบบ · ไทย · ฮวงจุ้ย · สวน · ยั่งยืน · รีโนเวท · ต้นทุน · สมาร์ทโฮม · BIM
  - เขียน title + body + (optional) ชื่อ + pages ที่เกี่ยว
- **Tab 2 "เรื่องที่เขียนแล้ว":**
  - Filter ตามหัวข้อ · เห็น count ต่อหมวด
  - ✨ **AI ช่วยจัดระเบียบ** → แนะนำ layers · related pages · keywords · หน้าใหม่
  - Download ต่อ entry: `.json` หรือ `.md` (wiki-ready)
  - 🚀 **ส่งขึ้น GitHub** (ต้อง admin set secrets ก่อน)

### 💾 Save/Load
- **Export** current project เป็น .json (brief + result + raw)
- **Export** ประวัติทั้งหมด 1 ไฟล์
- **Import** ไฟล์ .json ของโปรเจคเก่า → โหลดเข้าฟอร์ม (และผลถ้าอยากดู)
- ใช้เก็บงานข้ามวัน · แชร์กับทีม · backup

### 🎨 ภาพ mockup
- (Pro only · ใช้ Gemini Image quota ของคุณ)
- 4 มุมมอง: 🦅 Bird's-eye · 🏠 Perspective · 📐 Floor plan · 🛋 Interior
- **เพิ่มคำแนะนำเสริม** (style · material · mood) ก่อนสร้าง
- Gallery เก็บ 6 ภาพล่าสุด · download เป็น .png

### 📅 จองปรึกษา
4 แพ็กเกจ:
| | Duration | Price |
|---|---|---|
| Introductory call | 30 นาที | **ฟรี** |
| Plan review | 60 นาที | 2,500 บาท |
| Design consultation | 90 นาที | 3,750 บาท |
| Full project consult | 2 ชม. | 5,000 บาท |

หลังกรอก → 2 ขั้นต่อ:
- 📤 **เปิดแอพอีเมล** (mailto: พร้อมข้อความ)
- 📥 **Download .ics** (บันทึกใน Google/Apple Calendar)

**Pro tier ลด 20%**

### 💼 Pricing
เทียบ Free vs Pro · FAQ · dev toggle (สำหรับทดสอบ)

---

## 🔗 แชร์ผลให้ลูกค้า

หลังวิเคราะห์เสร็จ · scroll ลง → panel **"🔗 แชร์ลิงก์ให้ลูกค้า"**
- Copy URL จาก text area
- ส่งให้ลูกค้าผ่าน email/LINE
- ลูกค้ากดเปิด → เห็นผลเต็ม · ไม่ต้อง login · read-only
- ถ้า URL ยาวเกิน → download `.json` แทน · ลูกค้า upload ในเว็ป

---

## 📥 5 Download formats

| Format | ใช้ตอนไหน |
|---|---|
| `.md` Markdown | ใส่ Obsidian · Notion · GitHub |
| `.json` | Backup · import กลับมาในเว็ป · data exchange |
| `.txt` Raw AI | Debug · เห็น output AI ก่อน parse |
| `.html` | เปิด browser · Ctrl+P → Save as PDF (ทำงาน 100% + ฟอนต์ไทย) |
| `.pdf` (Pro) | Native PDF ด้วย Sarabun font (ต้อง ship font ก่อน) |

---

## 💡 Tips ใช้ให้ได้ผลดีที่สุด

### Prompt tricks
- ใส่ **ข้อมูลเฉพาะ** ใน "รายละเอียดพิเศษ" · AI จะคิดครบ
- ตัวอย่างดี: "ห้องพระต้องหันทิศตะวันออก · ผู้สูงอายุใช้ wheelchair · สระ 4×10"
- ตัวอย่างแย่: "สวยๆ ใหญ่ๆ"

### หลายโมเดลเทียบ
- เช็คใน sidebar เปลี่ยน **Gemini model**: 2.5-flash (เร็ว) · 2.0-flash (เสถียร) · 1.5-flash (backup)
- ใช้ Claude ถ้าต้อง quality สูง (เสียเงิน)

### Quota
- Free: 5 ครั้ง/session · refresh page = รีเซ็ต
- ใช้ **ช่วยเติม + Chat** เพื่อถามต่อโดยไม่เปลืองโควต้า analysis

### ผลแปลกๆ
- **Rate limit 429:** รอ 1 นาที · หรือเปลี่ยน model
- **AI ไม่ตอบ JSON:** แสดงเป็น markdown แทน · ข้อมูลยังครบ
- **ตัวเลขกฎหมาย null:** AI ไม่แน่ใจ · ปรึกษาสถาปนิกจริง

---

## ❓ FAQ

**Q: ข้อมูลของผมถูกเก็บไหม?**
A: ไม่ · session-based · ปิด tab = หายหมด · ไม่ใช้ train AI (privacy guarantee)

**Q: ผลวิเคราะห์ใช้แทนสถาปนิกได้ไหม?**
A: **ไม่ได้** · เป็นการประเมินเบื้องต้น · พรบ.ควบคุมอาคาร 2522 มาตรา 49 ทวิ ต้องมีลายเซ็นผู้ประกอบวิชาชีพ

**Q: ถ้าผมเจอข้อมูลผิด?**
A: ใช้ tab **💡 ช่วยเติม** → ประเภท "📝 แก้ไข" → เขียนให้ admin ตรวจ

**Q: Pro tier ซื้อยังไง?**
A: ยังเป็น waitlist · กรอก booking form · ทีมจะติดต่อ

**Q: API key หาย?**
A: ใส่ใหม่ทุกครั้งที่เข้าเว็ป · ไม่ถูกเก็บ (privacy)

---

## 🐛 ถ้าเจอปัญหา

1. **Refresh page** (Ctrl+R) · บางทีก็แก้ได้
2. **เปลี่ยน AI model** ที่ sidebar
3. **ส่ง feedback** ผ่าน tab **💡 ช่วยเติม** → ประเภท "🐛 คำถาม"
4. **ติดต่อ:** narongsak.bimtts2004@gmail.com

---

**Built with ❤ for Thai architects and homeowners**
