# PRD · สมองจำลองของสถาปนิก

> **Status:** v6 production · branch `v6` · ระบบ production-ready
>
> **Owner:** Narongsak Buttumpan · narongsak.bimtts2004@gmail.com
> **Repo:** https://github.com/narongsak-art/arch-brain-web
> **Live:** https://arch-brain-narongsak.streamlit.app
> **Last updated:** 2026-04-20

---

## 1. Vision

เครื่องมือ **AI-powered design analysis** สำหรับสถาปนิกและเจ้าของบ้านไทย · ใส่ brief → วิเคราะห์ผ่าน 5 ชั้นความรู้ (กฎหมาย · วิศวกรรม · ออกแบบ · วัฒนธรรมไทย · ฮวงจุ้ย) → ได้ผล structured + portfolio ส่งลูกค้าได้ใน 60 วินาที

**Core loop:**
```
Brief (sidebar) → AI analysis → Structured result (main) → Portfolio HTML → ลูกค้า
```

**Thai identity:** editorial aesthetic · warm palette (ครีม · ไม้สัก · ทอง) · Bai Jamjuree serif · ที่มาจริงจาก Thai building codes · วัฒนธรรมไทย · tropical climate design

---

## 2. Target Users

### 👤 A. สถาปนิกมืออาชีพ (primary)
- **ต้องการ:** second opinion · cross-check · client-ready deliverable
- **Input:** project brief · orientation · grade · priority · notes
- **Output:** compliance checklist · 5-layer score · design phases · portfolio

### 🏠 B. เจ้าของบ้าน
- **ต้องการ:** ประเมินโปรเจคเบื้องต้น · รู้ปัญหาก่อนจ้างสถาปนิก
- **Input:** brief ขั้นต้น · บางฟิลด์ใช้ preset ได้
- **Output:** feasibility · metrics · issues · actions

### 🎓 C. นักเรียนสถาปัตย์
- **ต้องการ:** ดู reference · เข้าใจกฎหมายไทย · case studies
- **Input:** thesis project
- **Output:** 5-layer analysis · citations · phases · Explore ความรู้

---

## 3. Current State · v6 (2026-04-20)

### ✅ Features

**📝 Inputs (sidebar · 4 tabs)**
| Tab | Fields |
|---|---|
| 📝 Basic | name · W × D · province · zone · street · family · elderly · floors · BR · budget · fengshui · special |
| 🧭 Pro | 8-way orientation + visual compass · topography · adjacent context · priority (multi) · grade · timeline |
| 🏷 Meta | client · tags · notes |
| 📎 Plan | upload JPG/PNG |

Plus 8 preset tiles in welcome gallery: ทาวน์เฮาส์ · บ้านเดี่ยวเล็ก/ใหญ่ · บ้านหรู · บ้านเล็ก กทม. · ห้องแถว · รีสอร์ทวิลลา · บ้านผู้สูงอายุ

**📊 Outputs (main · result area)**
1. **Summary hero** · feasibility + score + concern/strength
2. **Site SVG** · plot + buildable area + north arrow (rotates to orientation) + dimensions
3. **Usage bars** · FAR · OSR · budget vs cost (color-coded sage/gold/terra)
4. **Metrics grid** · 8-10 key values
5. **📋 Compliance** · 6 categories (code · zoning · parking · fire · accessibility · energy)
6. **🧩 5-Layer** · scored bars + findings per layer
7. **🚪 Rooms** · 6+ rooms · size/orientation/cultural/fengshui
8. **🚨/⭐ Issues + Strengths** · ranked · with actions
9. **🧭 Design Phases** · SD/DD/CD/CA · tasks + deliverables + weeks
10. **🎯 Next Actions** · table with owner + timing

**💾 Exports**
- `.md` Markdown · `.json` structured · `.txt` raw AI
- **📑 Portfolio HTML** · client-ready · 9 sections · print-to-PDF ready

**📚 My Studio**
- Gallery cards with feasibility + score + metadata
- 📌 Pin favorites (separate section at top)
- 4-filter toolbar · search · feasibility · tag · client
- Actions per card: open · pin/unpin · delete

**🌐 Explore**
- 104-node Knowledge Graph browser
- Layer filter + text search
- Click card → detail view with related-pages graph navigation

### 🏗 Code structure

```
arch-brain-web/
├── app.py                   ~1,400 lines · UI · CSS · sidebar · 3 views · routing
├── brain.py                 ~1,100 lines · AI + prompts + parsing + rendering + portfolio
├── kg-compact.json          104 nodes · 425 edges · AI context
├── full-knowledge.md        291 KB · curated page bundle
├── system-prompt.md         base AI persona
├── requirements.txt         5 packages
├── scripts/
│   ├── build_kg.py          regen KG from Obsidian vault
│   └── selftest.py          10-check diagnostic (run before release)
├── contributions/           staging folder (for future community UI)
└── fonts/                   (optional) Sarabun TTF for native PDF
```

**Dependencies:** streamlit · requests · anthropic · Pillow · pandas

### 🎨 Design language

**Palette** (softer · editorial):
- Cream bg `#fbf9f3`
- Teak primary `#7a4e24`
- Gold `#b89755` · Terra `#b16a57` · Sage `#6b7f64`
- Ink text `#241a11` · muted `#6e5d48` · subtle `#a89879`

**Fonts:** Bai Jamjuree (display · Thai serif-sans) + Sarabun (body) via Google Fonts

**Spacing:** 8/12/16/20 radius scale · 180ms cubic-bezier transitions · fadeInUp on card load

---

## 4. Branches (evolution history)

| Branch | State | Purpose |
|---|---|---|
| **`v6`** | ✅ current production | 2-file · sidebar tabs · architect edition |
| `v5-beta` | preserved | 9-file split · core/ + views/ (intermediate) |
| `main` | legacy v3.0/v4.5.1 | 19 components · 11 tabs (over-engineered) |
| `legacy-v2` | preserved | v2 feature-complete snapshot · oldest |

### 📜 v6 commit history (10 commits)

| Commit | Summary |
|---|---|
| `4a43ad0` | Initial rebuild · 2 files · 1,282 lines |
| `9de390f` | Refined aesthetic · softer palette · better cards |
| `e65591f` | Gallery-first welcome · 5 big preset tiles |
| `285ad15` | Architect edition · compass · priority · phases · compliance |
| `4a9d91d` | Visual diagrams · site SVG · FAR/OSR bars |
| `23b833f` | Portfolio HTML export · 9 sections · print-ready |
| `c8eedb8` | Tags + notes + client · Studio pin + filter |
| `49b7866` | +3 presets (shophouse · resort · accessible) · 8 total |
| `a8111ea` | Selftest 10-check · README refresh |
| `364d379` | **Sidebar form as 4 tabs · compact layout** |

---

## 5. Principles (learned · เรียนรู้มาแล้ว)

### ✅ DO
- **1 commit = 1 feature** · test + selftest ก่อน push
- **Target `[data-testid=...]` only** ใน CSS · ห้ามใช้ `.css-*` ที่เปลี่ยนระหว่าง Streamlit version
- **Session state defaults BEFORE widgets** · ใช้ `on_change` callback เวลา mutate
- **Graceful fallback** ทุก API call · ห้าม crash
- **Preserve data:** KG + full-knowledge + system-prompt ไม่แตะ (source of truth)

### ❌ DON'T
- ❌ เพิ่ม third-party UI lib ที่ไม่ได้ maintain (streamlit-drawable-canvas, agraph ตายแล้ว)
- ❌ Pin Streamlit version (track latest · แก้ด้วย CSS fallback)
- ❌ Multi-page `pages/` folder (CSS inject พัง · ใช้ views + radio switcher แทน)
- ❌ เก็บทุก feature เก่าตลอด · กล้าลบที่ไม่จำเป็น (v6 ลบ 15+ features จาก v4 โดยยังทำงานครบ core)

---

## 6. Roadmap

### 🟢 Done (v6.x)
- Sidebar tabs (compact form)
- Portfolio HTML export
- Architect fields + compass
- Visual site diagram
- Studio pin/filter
- 8 preset templates
- Explore KG detail view
- Selftest CI gate

### 🟡 Next candidates
Pick based on user feedback:

**A · Visual upgrades**
- PDF export via browser print better UX (show print-to-PDF tutorial)
- Image mockup generation (Gemini Flash Image · 4 views)
- More detailed site diagram (sun path · wind rose · shadow study)

**B · Data integration**
- Google Sheets backend (save analyses across sessions)
- GitHub community contributions (users submit case studies)
- Project version tracking (v1 · v2 · v3 of same project)

**C · Professional features**
- BOQ generator from AI (Bill of Quantities sample)
- Fee calculator (standard Thai architect fee structure)
- Client brief template download (.docx)
- TOR template generator

**D · Polish**
- Mobile responsive tuning
- Loading skeleton while AI thinks
- Toast notifications
- Keyboard shortcuts

**E · Content**
- More wiki pages (smart home · cost · BIM · tropical design)
- Real case studies from your practice
- Video tutorials
- Thai architecture glossary

### 🔵 Long-term
- Real payment (Stripe · PromptPay QR) for Pro tier
- OAuth + persistent accounts (Supabase)
- Team workspace
- Multi-language (English for international Thai architects)
- Export to CAD (DWG · IFC · SketchUp)

---

## 7. Tech decisions (recorded · don't relitigate)

| Decision | Rationale |
|---|---|
| **Streamlit** (not Next.js) | solo dev · Python-first · free hosting · suits this product |
| **2 files** (not 19) | maintainability · easy to hold in head · less indirection |
| **Session state** (not DB) | no infra · privacy-first · rebuild on every refresh |
| **Knowledge in repo** (not API) | version-controlled · diffable · offline-capable |
| **Structured JSON output** (not markdown) | consistent rendering · better exports |
| **Sidebar-first layout** | drafted.ai pattern · clean main work area |
| **Thai editorial aesthetic** | differentiation from generic startup look |
| **No canvas/drawable** libs | abandoned libs · break on Streamlit updates · site SVG is enough |

---

## 8. Testing

### Selftest (10 checks · run before release)
```bash
python scripts/selftest.py
```

1. All .py files parse
2. Core imports (brain + app · mocked st)
3. JSON parser (4 input shapes)
4. 8 presets valid
5. Site SVG generation
6. Portfolio HTML generation
7. Prompts construction
8. KG integrity (meta matches arrays)
9. CSS has no fragile selectors
10. All 3 views render without crash

### Manual smoke test
1. Load app · see welcome gallery (8 tiles)
2. Click preset → ribbon shows "พร้อมวิเคราะห์"
3. Sidebar tabs visible · all 4 (Basic/Pro/Meta/Plan) accessible
4. Compass rotates when orientation changes
5. Analyze → progress status → result appears
6. Site SVG renders with correct dimensions + rotation
7. Compliance table shows 6 rows
8. 5-Layer dataframe shows progress bars
9. Phases show 4 cards (SD/DD/CD/CA)
10. Download `.md` + `.json` + portfolio `.html`
11. Switch to Studio → see card with pin/open/delete
12. Click Pin → appears in PINNED section
13. Switch to Explore → 104 cards · filter works · detail view opens
14. Click related page → detail recurses · back button works

---

## 9. Known limitations

- **Session-only persistence** (refresh = lose history · until we add backend)
- **No user auth** (private per-device)
- **AI rate limit** (Gemini free 15 req/min · 1,500/day · ใช้ Claude เสียเงิน)
- **Thai font** in native PDF requires ship Sarabun TTF (HTML export works always)
- **No real-time collab** (single-user design tool)

---

## 10. Maintenance

### Weekly (5 นาที)
- [ ] `git pull` · ดู GH Actions status
- [ ] `python scripts/selftest.py` · ต้อง 10/10

### Monthly (15 นาที)
- [ ] ลอง deployed URL · test 5-step flow จริง
- [ ] Streamlit changelog · มี breaking change?
- [ ] review contributions/ ถ้ามี

### Quarterly (1 ชม.)
- [ ] Update PRD changelog + version
- [ ] Backup Obsidian vault
- [ ] Review legacy branches · revive anything?

---

## 11. Deliverables for this session

**Code (on branch `v6`):**
- app.py · 1,400 lines · all UI + CSS + routing
- brain.py · 1,100 lines · AI + rendering + portfolio
- scripts/selftest.py · 10-check diagnostic
- scripts/build_kg.py · KG regenerator

**Documentation:**
- README.md · user-facing overview
- PRD.md (this file) · product + architecture + roadmap

**Data preserved:**
- kg-compact.json · 104 nodes (ยังใช้ต่อ)
- full-knowledge.md · 291 KB (ยังใช้ต่อ)
- system-prompt.md (ยังใช้ต่อ)
- contributions/ scaffold (ยังใช้ต่อสำหรับ feature ในอนาคต)
- fonts/ scaffold (สำหรับ ship Sarabun เมื่อพร้อม)

---

## 12. Next session checklist

เมื่อกลับมาทำต่อ:

1. [ ] `git checkout v6 && git pull`
2. [ ] `python scripts/selftest.py` · ต้อง 10/10
3. [ ] เปิด deployed URL · test flow 5 นาที
4. [ ] อ่าน PRD นี้ (this file) · Roadmap section
5. [ ] เลือก 1 feature จาก Roadmap § 6
6. [ ] ทำ · 1 commit · test · push
7. [ ] อัปเดต changelog table § 4 ของ PRD นี้

---

*ระบบนี้โตขึ้นเรื่อยๆ ตามการใช้งาน · keep it simple · keep it honest · keep it growing 🌱*
