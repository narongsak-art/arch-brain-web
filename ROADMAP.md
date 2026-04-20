# Roadmap · แผนพัฒนาเว็ปไซต์

> แผนการพัฒนาต่อจาก v6 · เรียงตาม **impact × urgency** · ทำตามลำดับจะได้ค่าสูงสุด
>
> **Updated:** 2026-04-20

---

## 🎯 North Star

> เป็นเครื่องมือที่สถาปนิกไทยใช้ทุกวัน · จากรับงานจนส่งมอบ

**Measure of success:**
- สถาปนิก 1 คนใช้ครบ 1 โปรเจค (brief → analyze → portfolio → invoice)
- เว็ปไม่มีข้อมูลหาย · ไม่มี blocker สำคัญ
- Loyal users 10+ คนใน 3 เดือน

---

## 📊 Priority framework

แต่ละ phase ให้คะแนน 3 มิติ:

| มิติ | ความหมาย |
|---|---|
| **Impact** | ผู้ใช้ได้ค่าแค่ไหน · 🟢 สูง · 🟡 กลาง · 🔴 ต่ำ |
| **Effort** | ทำยากแค่ไหน · S (1 session) · M (2-3) · L (4+) |
| **Blocker** | ถ้าไม่มี จะทำ phase ถัดไปได้ไหม |

---

## 🚀 Phase 7 · Persistence Foundation

**Goal:** ข้อมูลไม่หายเมื่อ refresh · สถาปนิกใช้เป็นประจำวันได้

| Feature | Impact | Effort | Why |
|---|---|---|---|
| Auto-save ทุก analysis ลง `localStorage` | 🟢 | S | แก้ session-loss problem |
| Import/Export project bundle (.json) | 🟢 | S | backup + share · ยัง port ไปเว็ปอื่นได้ |
| Session restore banner ("มี 5 งานเก่า · โหลดคืน?") | 🟡 | S | UX smoothness |
| Recent projects quick-switcher (sidebar) | 🟡 | S | เปิดงานเก่ารวดเร็ว |
| Loading skeleton ตอน AI thinking | 🟡 | S | perceived perf |
| Mobile responsive tuning | 🟡 | M | ใช้บนมือถือได้จริง |

**Success metric:** ลองเปิด-ปิด-refresh 10 รอบ · **0 ข้อมูลหาย**
**Est:** 3-5 commits · 1-2 sessions
**Blocks:** Phase 11 (monetize · ต้อง stable ก่อน)

---

## 💼 Phase 8 · Professional Deliverables

**Goal:** สถาปนิกใช้ตัวเลข + เอกสารจากเว็ปไปส่งลูกค้าได้เลย

| Feature | Impact | Effort | Why |
|---|---|---|---|
| **Fee calculator** · Thai architect standard fee (% × construction value) | 🟢 | M | ปัญหา pain point · ทุกสถาปนิกต้อง quote |
| **BOQ estimate** · คร่าวๆ · 30-40 รายการหลัก | 🟢 | M | รายละเอียดกว่า "ค่าก่อสร้าง 10 ลบ." |
| **TOR / Contract template** download | 🟢 | M | ลูกค้าร้องขอทุกครั้ง |
| **Client brief template** (.docx หรือ interactive) | 🟡 | M | ก่อนเริ่มงาน · เก็บข้อมูลจากลูกค้า |
| **Phase timeline Gantt** · SVG · ดึงจาก phases data | 🟡 | S | visualize timeline |
| **Compliance PDF checklist** · download เฉพาะ section | 🟡 | S | สำหรับ submission |

**Success metric:** 1 สถาปนิกทำได้ end-to-end (brief → BOQ → contract → portfolio)
**Est:** 5-7 commits · 2-3 sessions
**Blocks:** Phase 11 (ต้องมี deliverable ให้ขาย)

---

## 🎨 Phase 9 · Visual Intelligence

**Goal:** visual outputs แบบสถาปนิกดูแล้วเข้าใจทันที

| Feature | Impact | Effort | Why |
|---|---|---|---|
| **AI image mockup** · Gemini Flash Image · 4 views | 🟢 | M | การ present ลูกค้าใช้รูปเสมอ |
| **Sun path diagram** · SVG based on location + orientation | 🟢 | M | passive design check |
| **Wind rose** · กรุงเทพวสมี prevailing SW/NE | 🟡 | S | ventilation design |
| **Shadow study** · 9 น./เที่ยง/15 น. · 3 วัน/ปี | 🟡 | M | ใช้กับ solar + privacy |
| **Room layout sketch** · 2D schematic จาก rooms data | 🟡 | L | bubble diagram visual |
| **3D massing preview** · SVG isometric · volume only | 🔴 | L | cool แต่ไม่จำเป็น |

**Success metric:** ผลวิเคราะห์มี ≥ 4 visuals · ลูกค้าเข้าใจง่ายขึ้น (test on 3 real clients)
**Est:** 6-8 commits · 2-3 sessions

---

## 📚 Phase 10 · Knowledge Growth

**Goal:** wiki 104 → 200+ nodes · ครอบคลุมเรื่องที่สถาปนิกเจอจริง

| Content | Impact | Effort | Why |
|---|---|---|---|
| Real case studies (จากงานจริง) · 10 projects | 🟢 | L | ที่สุดของการ ground AI |
| Smart home wiki · 5 pages | 🟡 | M | trend · ลูกค้าถามบ่อย |
| Cost estimation · 10 pages · unit prices TH 2025 | 🟡 | M | update ทุกปี |
| BIM workflows · Revit/ArchiCAD/SketchUp · 8 pages | 🟡 | M | modern practice |
| Tropical design · passive · shading · 6 pages | 🟢 | M | ไทยคือ tropical |
| Thai architecture glossary · 100 terms | 🟡 | L | นักเรียน + foreigner |
| Material database · ไม้ · คอนกรีต · เหล็ก · 20 entries | 🟡 | M | BOQ support |

**Success metric:** KG 104 → **200 nodes** · full-knowledge 291 KB → 500 KB
**Est:** ต่อเนื่อง · ไม่ fix timeline · ทำพร้อมใช้งาน
**Optional dependency:** Phase 11 (community UI · users contribute · แต่ยังไม่ต้อง)

---

## 💰 Phase 11 · Monetization MVP

**Goal:** รับเงินได้จริง · sustain project

| Feature | Impact | Effort | Why |
|---|---|---|---|
| **PromptPay QR payment** · Thai bank rail · 7% fee | 🟢 | M | ง่ายที่สุดสำหรับ TH users |
| **Pro tier gates** · quota · premium exports · branded portfolio | 🟢 | S | value proposition ชัด |
| **Free quota** · 5 analyses/day (reset 00:00 GMT+7) | 🟢 | S | encourage upgrade |
| **Usage dashboard** · usage ยังเหลือเท่าไร · renewal | 🟡 | S | transparency |
| **Receipt email** · ส่งใบเสร็จอัตโนมัติ | 🟡 | M | tax compliance |
| **Coupon codes** · launch discount · referral | 🔴 | M | growth tactic |

**Success metric:** **1 paying customer** · ได้เงินจริงแม้น้อย
**Est:** 4-6 commits · 2 sessions
**Depends:** Phase 7 (stable data first · ไม่ให้ user จ่ายแล้วงานหาย)

---

## 🌱 Phase 12 · Community Contributions

**Goal:** knowledge โตจาก users · ไม่ใช่แค่ admin

| Feature | Impact | Effort | Why |
|---|---|---|---|
| **💡 Contribute tab** · 12 หัวข้อ × 4 ประเภท | 🟡 | M | fix knowledge gaps |
| **Admin review queue** · pending → approved → wiki | 🟡 | M | quality control |
| **AI organizer** · ช่วย classify contribution | 🟡 | M | reduce admin burden |
| **GitHub push** · ส่ง contribution ขึ้น repo ผ่าน API | 🟡 | M | audit trail |
| **Community leaderboard** · top contributors | 🔴 | S | gamification |

**Success metric:** **10 approved contributions** · 5 unique contributors
**Est:** 5-7 commits · 2-3 sessions
**Depends:** Phase 11 (Pro users more invested · contribute more)

---

## 🚀 Phase 13 · Scale Beyond Solo

**Goal:** ทีม · cross-device · international

| Feature | Impact | Effort | Why |
|---|---|---|---|
| **OAuth (Google)** · persist across devices | 🟢 | L | ทำงานต่อที่ไหนก็ได้ |
| **Supabase backend** · replace localStorage | 🟢 | L | multi-device + team |
| **Team workspace** · shared projects · role-based | 🟡 | L | สำนักงาน 2-10 คน |
| **Version history** · v1 · v2 · v3 · compare | 🟡 | L | design iteration |
| **English UI toggle** · international Thai architects | 🟡 | M | expand market |
| **Real-time collab** · multi-cursor | 🔴 | XL | not essential |

**Success metric:** 1 สำนักงานใช้ครอบครัว
**Est:** 20+ commits · 5-10 sessions
**Depends:** Phase 11 (revenue to justify backend cost)

---

## 🗓 Timeline sketch (realistic · solo dev + Claude)

```
Month 1 (May 2026)
  Week 1-2  · Phase 7 · Persistence foundation
  Week 3-4  · Phase 8 (start) · Fee calculator + BOQ

Month 2 (Jun 2026)
  Week 1    · Phase 8 (finish) · TOR · brief · Gantt
  Week 2-3  · Phase 9 · Visual intelligence (start)
  Week 4    · Phase 9 (finish) · mockup + sun path

Month 3 (Jul 2026)
  Week 1    · Phase 11 · Payment MVP
  Week 2    · Phase 11 · Pro gates · dashboard
  Week 3-4  · Launch + get first 3 paying customers

Month 4 · Monitor + Phase 10 (ongoing) + Phase 12 (community)
Month 5+ · Phase 13 · scale if traction
```

---

## 🎯 Minimum viable monetization path (MVMP)

ถ้าอยาก**ได้เงินเร็วที่สุด** · ทำแค่ phases นี้:

```
Phase 7 (persistence · M)
  + Phase 8 · only fee calc + BOQ (S each)
  + Phase 11 · payment + gates (M)
────────────────────────────────────────
= ~10 commits · 3-4 sessions · 2-3 weeks
= ready to charge 300-500 บาท/เดือน Pro
```

---

## 📐 Design principles (อย่าลืม)

ทุกก้าวเลือก feature · ตรวจว่า:
- ✅ ตรงกับ North Star (daily use · end-to-end)?
- ✅ 1 commit = 1 feature (อย่า bundle)?
- ✅ ทำ selftest ผ่านก่อน push?
- ✅ CSS target `[data-testid]` เท่านั้น?
- ✅ ไม่ depend on lib ที่ไม่ได้ maintain?
- ✅ Graceful fallback ทุก API?

---

## 🔻 Explicit non-goals

**อะไรที่เลือกไม่ทำ** (และทำไม):

| ไม่ทำ | เหตุผล |
|---|---|
| Full BIM tool | ซับซ้อน · ไม่ใช่ core value · ใช้ Revit/ArchiCAD อยู่แล้ว |
| Real-time 3D rendering | ค่า infra สูง · AI mockup พอเพียง |
| Mobile native app | web responsive พอ · maintenance 2×  |
| Replace architect license | พรบ.กำหนดต้องมีลายเซ็น · เราเป็น assistant |
| Facebook/IG auto-post | distraction · ไม่สร้าง retention |
| Chatbot integration | ใช้ในเว็ปดีกว่า · context ครบ |

---

## 📝 Operating rhythm

### ก่อนเริ่มทำ
```bash
git checkout v6 && git pull
python scripts/selftest.py       # ต้อง 10/10
# อ่าน ROADMAP.md · เลือก phase ถัดไป
```

### ขณะทำ
- ทำทีละ feature · commit ทีละอัน
- Selftest ก่อน commit
- ตั้งชื่อ commit ใช้ format: `Phase N · feature title`

### เมื่อ phase จบ
- Update ROADMAP.md · มาร์ค phase นั้น ✅
- Update PRD.md § 4 changelog
- Tag release · `git tag v6.N.0`

---

## 🚦 Red flags (stop & think)

- **CSS คลาด** (`.css-xyz` selectors) · STOP · ใช้ data-testid
- **Bundle 2+ features** ใน 1 commit · STOP · แยก
- **Selftest fail** ก่อน push · STOP · fix ก่อน
- **Adding new lib** ที่ไม่ได้ maintain (last update >1 year) · STOP · หา alternative
- **Breaking existing feature** · STOP · revert · redesign

---

*ทำทีละ phase · ไม่ต้องรีบ · each phase ships value*
