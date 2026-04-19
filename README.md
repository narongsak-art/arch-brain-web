# 🏠 สมองจำลองของสถาปนิก

> Web app for analyzing Thai residential architecture using AI + a community-curated **5-Layer Knowledge Graph**.
> Architect's second brain · สำหรับเจ้าของบ้าน · สถาปนิก · นักเรียนสถาปัตย์

**Live:** https://arch-brain-narongsak.streamlit.app
**Code:** https://github.com/narongsak-art/arch-brain-web

---

## ✨ What it does

ใส่ข้อมูลโปรเจค → AI วิเคราะห์ผ่าน **5 ชั้นความรู้** (กฎหมาย · วิศวกรรม · ออกแบบ · วัฒนธรรมไทย · ฮวงจุ้ย) → ได้ผลใน 60 วินาที

- **📐 Metrics** · FAR · OSR · setback · buildable area · cost estimate
- **🧩 5-Layer Scoring** · คะแนน 0-100 ต่อชั้น + top findings
- **🚪 Room-by-room** · ขนาดแนะนำ · ทิศ · ข้อควรระวัง
- **🚨 Issues · ⭐ Strengths · 🎯 Next actions**

## 🛠 Features (22 · v3.19)

### Studio experience (drafted.ai-inspired · Thai editorial)
- 🎨 **Studio** · gallery of saved designs · pinnable · click-to-open
- 🌐 **Explore** · community + 104 KG seed entries · click card → detail view with related pages graph
- 🧵 **วัสดุ** · Thai materials palette (ไม้สัก · ดินเผา · ครีม · etc · 5 groups × 25+ items)
  - palette auto-fed into AI analysis + mockup generation prompts

### วิเคราะห์
- ฟอร์มแบบ structured + 5 preset templates (ทาวน์เฮาส์ → บ้านหรู)
- Gemini 2.5 Flash (ฟรี) หรือ Claude Sonnet 4.6
- Image upload สำหรับแปลนที่มี
- Output เป็น JSON + renderer สวย · หรือ markdown fallback

### ผลลัพธ์
- 📥 Download: .md · .json · .txt · .html · .pdf
- 📑 **Portfolio export** · all-in-one Thai editorial HTML (cover + brief + palette + images + analysis) · client-ready
- 🔗 Share link (URL ฝังผลไว้ · ไม่ต้อง backend)
- 🖼 Image mockup (Gemini Flash Image · 4 มุมมอง)
- 💬 Chat follow-up (ถามต่อได้ · grounded ใน 104-node KG)
- 🔀 Compare 2 projects (side-by-side + diff table)
- 💾 Save/Load project JSON

### Community Hub
- 💡 **Contribute** · 12 หัวข้อ × 4 ประเภท (แก้ไข · เสนอ · case · คำถาม)
- ✨ AI organizer (suggest layers · related pages · keywords · new pages)
- 🚀 **Push ขึ้น GitHub** ผ่าน API (opt-in · PAT auth)
- 👮 **Admin moderation** ที่ `?admin=<token>` · review queue · approve/reject/edit
- 🤖 **Auto-rebuild:** approve → GH Action → wiki-mirror → KG regen → redeploy

### Business
- 🆓/💎 Tier system (Free quota · Pro unlimited + premium features)
- 📅 Booking (4 service tiers · mailto + .ics)
- 💼 Pricing page + FAQ

## 📊 Knowledge base

- **104 wiki pages** · 5 layers · 12 topic subgroups
- **425 wikilink edges** · cross-referenced
- **291 KB** full-knowledge.md bundled with every AI call
- Topics covered: กฎหมาย · MEP · passive design · tropical climate · cost estimation · smart home · BIM · renovation · cultural (ห้องพระ · ศาลภูมิ · บ้านไทย) · fengshui

## 🚀 Quick Start

```bash
# local dev
pip install -r requirements.txt
streamlit run app.py

# open http://localhost:8501
# ใส่ Gemini API key (ฟรีที่ aistudio.google.com/apikey)
```

## 📚 Documentation

| Doc | Audience | Purpose |
|-----|----------|---------|
| [`USER_GUIDE.md`](USER_GUIDE.md) | 👤 end users | How to use each tab · FAQ · tips |
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | 🛠 devs | Recipes · testing · maintenance · emergencies |
| [`ADMIN.md`](ADMIN.md) | 👮 admin | Moderation workflow · secrets setup |
| [`PRD.md`](PRD.md) | 🎯 PM/future-you | Architecture · roadmap · changelog |
| [`DEPLOY.md`](DEPLOY.md) | 🚀 devops | Deploy to Streamlit Cloud |
| [`contributions/README.md`](contributions/README.md) | 📦 contributors | Contribution schema · GitHub push setup |
| [`fonts/README.md`](fonts/README.md) | 🔤 Pro users | Enable native PDF via Sarabun font |

## 🧱 Tech stack

- **Python 3.11** · Streamlit (latest) · no pinning
- **AI:** Google Gemini 2.5 Flash (free tier) · Anthropic Claude (optional)
- **Storage:** session_state (client) · GitHub repo (community contributions) · Obsidian vault (wiki source)
- **No backend DB** · No user accounts · No third-party UI libs that break

## 🌱 Philosophy

```
ยิ่งคนใช้ · AI ยิ่งเก่ง
```

ระบบออกแบบให้**โตตามการใช้งาน**: ทุก analysis ถูกเก็บ · ทุก contribution ผ่านการตรวจ ·
approved → ไป wiki → AI ใช้อ้างอิงในครั้งถัดไป · loop ปิด

## 📝 License

Private · educational use only
สำหรับสถาปนิกและเจ้าของบ้านในประเทศไทย
