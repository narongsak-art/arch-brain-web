# 🚀 Deploy to Streamlit Cloud (ฟรี)

คู่มือ deploy step-by-step · **15-20 นาที** · ได้เว็บออนไลน์จริง

## ✅ ผลลัพธ์

- URL: `https://arch-brain-[yourname].streamlit.app`
- ใช้งานได้ทันที · share ลูกค้า/ทีมได้
- **ฟรี 100%** · Streamlit Cloud + Gemini API

---

## Phase 1 · Prerequisites (3 นาที)

### 1.1 สมัคร GitHub (ถ้ายังไม่มี)
- https://github.com/signup
- Free account พอ

### 1.2 สมัคร Streamlit Cloud
- https://streamlit.io/cloud
- Sign in **ด้วย GitHub**
- Free tier: unlimited public apps

### 1.3 Install Git (ถ้ายังไม่มี)
Windows: https://git-scm.com/download/win

ทดสอบ: `git --version` ใน terminal

---

## Phase 2 · Push to GitHub (5 นาที)

### 2.1 สร้าง repo บน GitHub
1. เข้า https://github.com/new
2. Repository name: **`arch-brain-web`**
3. **Public** (Streamlit Cloud free tier ต้อง public)
4. **ไม่ต้อง** Add README, .gitignore (เรามีแล้ว)
5. Create repository
6. Copy URL ที่แสดง เช่น `https://github.com/YOURNAME/arch-brain-web.git`

### 2.2 Push code จากเครื่องคุณ

เปิด terminal · รัน:

```bash
cd /d E:\Narongsakb\arch-brain-web
git init
git add .
git commit -m "Initial commit: สมองจำลองของสถาปนิก"
git branch -M main
git remote add origin https://github.com/YOURNAME/arch-brain-web.git
git push -u origin main
```

> แทน `YOURNAME` ด้วย GitHub username ของคุณ

### 2.3 Verify
ไปที่ `https://github.com/YOURNAME/arch-brain-web` · ควรเห็นไฟล์ทั้งหมด

---

## Phase 3 · Deploy to Streamlit Cloud (5 นาที)

### 3.1 เชื่อม GitHub

1. เข้า https://share.streamlit.io
2. คลิก **"New app"**
3. Authorize GitHub (ถ้ายังไม่ได้)
4. เลือก:
   - **Repository:** `YOURNAME/arch-brain-web`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. **App URL:** กำหนดเองได้ เช่น `arch-brain-narongsak`
6. **Deploy!**

### 3.2 รอ build (2-5 นาที)

Streamlit จะ:
1. Clone repo
2. Install `requirements.txt`
3. Start app

ดู progress log ระหว่างรอ

### 3.3 Live!

App URL: `https://arch-brain-narongsak.streamlit.app` (หรือตามที่ตั้ง)

---

## Phase 4 · รับ Gemini API Key (5 นาที)

### 4.1 สร้าง Gemini API Key
1. เปิด https://aistudio.google.com/apikey
2. Login ด้วย Google account
3. **Create API key**
4. เลือก project · Copy key (ขึ้นต้น `AIza...`)
5. **ไม่ต้องใส่ credit card!**

### 4.2 ทดสอบแอพ

1. เปิด URL แอพของคุณ (เช่น arch-brain-narongsak.streamlit.app)
2. Sidebar ซ้าย → Paste Gemini API key
3. กรอกข้อมูลทดสอบ (default ok)
4. กด "🔍 วิเคราะห์โครงการ"
5. รอ 30-60 วินาที
6. ดูผลวิเคราะห์

---

## Phase 5 · Custom domain (optional · ถ้ามี)

ถ้าต้องการ URL ของตัวเอง เช่น `tools.yourdomain.com`:

1. Streamlit Cloud: App settings → General → Custom subdomain (พรีเมียม)
2. หรือ ใช้ domain provider · CNAME redirect
3. หรือ ใช้ Cloudflare redirect (ฟรี)

---

## 🔄 Update เว็บไซต์

เมื่อคุณแก้ไข code:

```bash
cd /d E:\Narongsakb\arch-brain-web
# แก้ไขไฟล์
git add .
git commit -m "Update feature X"
git push
```

Streamlit Cloud **auto-redeploy** ใน 1-2 นาที

## 🔐 ใส่ Secret (optional)

ถ้าต้องการให้ **คุณเป็นคนจ่าย API** (user ไม่ต้อง paste key):

### 5.1 เพิ่ม secrets ใน Streamlit Cloud
1. App dashboard → **Settings** → **Secrets**
2. Paste:
```toml
[gemini]
api_key = "AIza..."
```

### 5.2 แก้ `app.py`
แก้ function `render_sidebar()`:

```python
# Replace:
api_key = st.sidebar.text_input("Gemini API Key", ...)

# With:
api_key = st.secrets["gemini"]["api_key"]
st.sidebar.success("🔑 API Key from secrets")
```

### 5.3 Redeploy
```bash
git add . && git commit -m "Use secrets" && git push
```

⚠ **Warning:** คุณจะจ่าย API ทุกครั้งที่ user ใช้ · พิจารณา rate limiting

---

## 💰 Cost Breakdown

| Item | Cost |
|------|------|
| GitHub | **ฟรี** (public repo) |
| Streamlit Cloud | **ฟรี** (Community tier) |
| Gemini API | **ฟรี** (1,500 calls/day) |
| **Total** | **0 บาท/เดือน** |

**Limits ของ Streamlit free tier:**
- 1 GB RAM
- 1 CPU
- Auto-sleep หลังไม่ใช้ 7 วัน (wake up เมื่อมีคนเข้า)
- Unlimited public apps

---

## 🐛 Troubleshooting

### Build failed: ModuleNotFoundError
→ ตรวจ `requirements.txt` · version ถูกต้อง

### Build succeeded but app error
→ ดู log ใน Streamlit Cloud dashboard

### App too slow
→ Optimize `@st.cache_data` (มีแล้วใน code)
→ เปลี่ยนจาก Gemini เป็น `gemini-2.0-flash-lite` (เร็วกว่า 2x)

### 429 Rate limit
→ Gemini free tier: 15 calls/minute
→ รอ 1 นาทีแล้วลองใหม่

### API Key invalid
→ ตรวจ key ที่ aistudio.google.com
→ อาจต้อง enable billing ก็ได้ (แต่ยัง free ถ้า < limits)

---

## 📈 Next Steps

### Week 1 · Soft launch
- [ ] Deploy + test ตัวเอง
- [ ] Share URL ให้ 3-5 คนในทีมทดลอง
- [ ] เก็บ feedback

### Week 2-4 · Iterate
- [ ] แก้ UI ตาม feedback
- [ ] เพิ่ม features (เช่น save history)
- [ ] Analytics: `streamlit-analytics` package

### Month 2+ · Scale
- [ ] พิจารณา upgrade Streamlit paid ($20/mo) ถ้าจำเป็น
- [ ] หรือย้ายเป็น Next.js + Vercel (ถ้าอยากได้ UI มากกว่า)
- [ ] Monetize: Premium tier · detailed reports · priority support

---

## 🎯 Success Metrics

หลัง deploy · track:
- จำนวน unique users / สัปดาห์
- Conversion (กรอก → กดวิเคราะห์)
- Avg response time
- Error rate

**Target week 1:** 10 users · 20 analyses
**Target month 1:** 50 users · 200 analyses

---

## 📞 Support

- Streamlit docs: https://docs.streamlit.io
- Streamlit forum: https://discuss.streamlit.io
- Gemini API docs: https://ai.google.dev/gemini-api/docs

ถ้าติดขัด · กลับมาถาม Claude Code · ผม debug ให้
