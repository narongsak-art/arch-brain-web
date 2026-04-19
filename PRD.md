# PRD · สมองจำลองของสถาปนิก (Architect's Second Brain)

> **Status:** v3.0 deployed · พัฒนาแบบ incremental · ระบบกลายเป็น community knowledge hub
>
> **Owner:** Narongsak Buttumpan · narongsak.bimtts2004@gmail.com
> **Repo:** https://github.com/narongsak-art/arch-brain-web · **Deploy:** https://arch-brain-narongsak.streamlit.app
> **Last updated:** 2026-04-18

---

## 1. Vision / เป้าหมาย

สร้างเครื่องมือ AI ที่ช่วยวิเคราะห์บ้านพักอาศัยไทย โดยใช้ฐานความรู้ **5 ชั้น** · และให้ระบบ**โตตามการใช้งาน**:

```
                  คนใช้
                    ↓
             AI วิเคราะห์
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
 ได้ผล         บันทึก            ช่วยเติม
              (กล่องรอเข้า)        (community)
                    ↓
              admin ตรวจ
                    ↓
              สมุดใหญ่ (wiki)
                    ↓
             AI ฉลาดขึ้น ← loop กลับ
```

**หลักการ:** "ยิ่งคนใช้ · AI ยิ่งเก่ง"

---

## 2. User Personas

### 👤 A. เจ้าของบ้าน (Owner-builder)
- **ต้องการ:** ประเมินบ้านของตัวเองก่อนจ้างสถาปนิก · ถามเรื่องพื้นฐาน (ห้อง · ทิศ · ฮวงจุ้ย)
- **Input:** ข้อมูลที่ดิน · ครอบครัว · งบ · optional upload แปลน
- **ต้องการ output:** feasibility · ประเด็นต้องระวัง · คำแนะนำเบื้องต้น · next steps

### 🏛 B. สถาปนิก (Professional)
- **ต้องการ:** second opinion · cross-check กฎหมาย · structured brief ให้ลูกค้า
- **Input:** brief ลูกค้า · plan images · case history
- **ต้องการ output:** cite source · checklists · exportable reports · client share link

### 🎓 C. นักเรียน / อาจารย์สถาปัตย์
- **ต้องการ:** reference case · ข้อมูลเชิงโครงสร้าง · material costs · design patterns
- **Input:** โปรเจคเรียน · thesis
- **ต้องการ output:** explainable analysis · citable sources · KG browser

---

## 3. Current State (v3.0 · 2026-04-18)

### ✅ Features ที่ใช้งานได้

| # | Feature | Module | Commit |
|---|---------|--------|--------|
| 1 | **Form wizard** (land/family/special) | app.py | - |
| 2 | **5 preset chips** (ทาวน์เฮาส์ → บ้านหรู) | presets.py | `3d6bf2a` |
| 3 | **Upload plan** (image · optional) | app.py | - |
| 4 | **Gemini / Claude analysis** (structured JSON) | llm.py, analysis.py | - |
| 5 | **Structured result renderer** (metrics · 5-layer · rooms · issues · actions) | analysis.py | - |
| 6 | **Download** .md / .json / .txt | app.py | - |
| 7 | **Session history** (load / download / delete / clear-all) | history.py | `9c17593` |
| 8 | **Theme system** (light/dark toggle · CSS tokens) | theme.py | `de64f95` |
| 9 | **Contribute Hub** (12 หมวด × 4 ประเภท · browse + filter) | contribute.py | `e8a201f` |
| 10 | **Auto-save to Hub** (1-click case study · heuristic categorize) | contribute.py | `196ae61` |
| 11 | **AI-assisted organizing** (layers · related · keywords · proposed pages) | contribute.py | `3f6e004` |
| 12 | **Project Save/Load JSON** (schema-validated · form populate) | project_io.py | `8898cf6` |
| 13 | **HTML + PDF export** (print-ready · Sarabun font optional) | export_pdf.py | `c1c466a` |
| 14 | **Share link** (gzip+base64 URL · read-only view · demo mode) | share.py | `e25aec9` |
| 15 | **Image generation** (Gemini Flash Image · 4 view types · gallery) | image_gen.py | `cf28e3b` |
| 16 | **Chat follow-up** (per-analysis · 6 suggestions · KG-grounded) | chat.py | `24c72b4` |
| 17 | **Compare 2 analyses** (diff table · layer bars · side-by-side) | compare.py | `812d13d` |
| 18 | **Booking** (4 tiers · mailto + .ics · session history) | booking.py | `aa7db64` |
| 19 | **Tier Free/Pro** (quota · feature gate · pricing tab) | tiers.py | `6e04db2` |
| 20 | **GitHub push** (Phase 3 · PAT-auth · per-entry commit) | github_sync.py | `ac39c59` |
| 21 | **Admin moderation** (Phase 4 · review queue · approve/reject/edit) | admin.py | `e321770` |
| 22 | **Auto-rebuild pipeline** (Phase 5 · 2 GH Actions · flexible vault) | .github/workflows/ | `3ca80ea` |

### 📊 Knowledge Graph

- **104 nodes** (wiki pages) · **425 edges** (wikilinks)
- **291 KB** full-knowledge.md · bundled 32 curated pages
- **4 new tracks:** Smart Home · Cost Estimation · BIM · Tropical Design (16 pages · +5,821 บรรทัด)

### 🏗 Architecture (v3 complete · 14 components · 1 entry · 2 scripts · 2 workflows)

```
arch-brain-web/
├── app.py                                    # main · sidebar + form + result + tabs
├── components/
│   ├── theme.py                              # CSS tokens + light/dark + hero helper
│   ├── llm.py                                # Gemini + Claude clients
│   ├── analysis.py                           # structured JSON prompt / parser / renderer
│   ├── presets.py                            # 5 home-type templates
│   ├── history.py                            # session history + per-item ops
│   ├── contribute.py                         # 12-category hub + AI organizer + auto-save
│   ├── project_io.py                         # Save/Load JSON
│   ├── export_pdf.py                         # markdown → HTML + reportlab PDF
│   ├── share.py                              # gzip+base64 URL + view mode
│   ├── image_gen.py                          # Gemini Flash Image · 4 views · gallery
│   ├── chat.py                               # per-analysis chat · 6 suggestions
│   ├── compare.py                            # 2-project side-by-side + diff
│   ├── booking.py                            # 4-tier service · mailto + .ics
│   ├── tiers.py                              # Free/Pro · quota · feature gate
│   ├── github_sync.py                        # PAT-auth contribution push
│   └── admin.py                              # Phase 4 moderation view
├── scripts/
│   ├── build_kg.py                           # wiki → kg-compact.json (flexible vault)
│   └── ingest_contributions.py               # approved JSON → .md files
├── .github/workflows/
│   ├── rebuild-kg.yml                        # auto-regen KG on wiki change
│   └── promote-approved.yml                  # auto-promote approved → wiki-mirror
├── kg-compact.json                           # 104 nodes · 425 edges
├── full-knowledge.md                         # 291 KB curated bundle
├── system-prompt.md                          # AI system prompt
├── fonts/README.md                           # Sarabun TTF instructions
├── contributions/                            # Tier 2 staging (GitHub push lands here)
│   └── README.md                             # schema + 12 categories doc
├── wiki-mirror/                              # (created by GH Action when first approval)
├── PRD.md                                    # this file
├── ADMIN.md                                  # admin workflow guide
├── README.md · DEPLOY.md
└── requirements.txt                          # streamlit · requests · anthropic · Pillow · pandas · reportlab
```

### 🖥 UI surface (8 tabs)

```
📝 form (main flow)  →  🔍 analyze  →  📊 result
                                        ├─ 📤 Save to Hub
                                        ├─ 🔗 Share link
                                        └─ 📥 Downloads (5 formats)

secondary tabs:
  📚 ประวัติ · 💬 Chat · 🔀 เปรียบเทียบ · 💡 ช่วยเติม
  💾 Save/Load · 🎨 ภาพ mockup · 📅 จองปรึกษา · 💼 Pricing
```

### 🚫 ลบถาวรเพราะ lib ไม่เสถียร

- `streamlit-drawable-canvas` → draw-plan tool · annotate (Streamlit 1.32+ แตก)
- `streamlit-agraph` → KG graph viz
- Multi-page (`pages/` folder) → complexity เยอะ · ทำให้ CSS inject ยุ่ง
- Compat shims · version pinning

**Backup:** branch `legacy-v2` บน GitHub เก็บ v2 ไว้สำหรับ revival

---

## 4. Data Model

### 3-Tier Storage

```
┌──────────────────────────────────────────────┐
│ TIER 1 · TRANSIENT (st.session_state)        │
│   · form · result · history · contributions  │
│   · lost on refresh                          │
└──────────────────────────────────────────────┘
                   ↓ (Phase 3: GitHub API push)
┌──────────────────────────────────────────────┐
│ TIER 2 · STAGING (contributions/ in repo)    │
│   · unmoderated · public audit trail         │
│   · 4 subfolders: corrections/ proposals/    │
│     cases/ questions/                        │
└──────────────────────────────────────────────┘
                   ↓ (Phase 5: admin approve)
┌──────────────────────────────────────────────┐
│ TIER 3 · PRODUCTION (wiki/ · Obsidian vault) │
│   · curated knowledge                        │
│   · rebuild kg-compact.json + full-knowledge │
└──────────────────────────────────────────────┘
```

### Core Schemas

**Project Brief** (form)
```json
{
  "name": "string",
  "land_w": "float (m)", "land_d": "float (m)", "land_area": "computed",
  "province": "string", "zone": "string", "street_w": "float",
  "family_size": "int", "has_elderly": "ใช่|ไม่",
  "floors": "1|2|3|4+", "bedrooms": "1|2|3|4|5+",
  "budget": "float (MB)", "fengshui": "มาก|ปานกลาง|น้อย|ไม่สน",
  "special": "string"
}
```

**Analysis Result** (structured JSON from AI)
```json
{
  "summary": {"feasibility":"green|yellow|red","score":0-100,"concern":"...","strength":"..."},
  "metrics": {"land_area_sqm": 0, "far_allowed": 0, ...},
  "layers": {"law":{"status":"...","score":0-100,"findings":[...]}, ...},
  "rooms": [{"name":"...","type":"...","size_min":0,...}],
  "issues": [{"rank":1,"severity":"high|medium|low",...}],
  "strengths": [...],
  "actions": [{"step":1,"action":"...","who":"...","when":"..."}],
  "confidence":"high|medium|low","caveats":[...]
}
```

**Contribution** (staging)
```json
{
  "id": "uuid8",
  "timestamp": "ISO8601",
  "type": "correction|proposal|case|question",
  "category": "law-zoning|structure|mep|design|thai-culture|fengshui|landscape|sustainability|renovation|cost|smart-home|bim-tools",
  "title": "string",
  "body": "markdown",
  "author": "string (optional)",
  "related_pages": ["wiki/concepts/xxx", ...],
  "status": "pending|approved|rejected",
  "ai_suggestions": {
    "layers": ["..."], "related_pages": [{"id":"...","relevance":"..."}],
    "keywords": [...], "proposed_new_pages": [{"slug":"...","title":"...","reason":"..."}],
    "short_summary": "...", "model": "...", "generated_at": "..."
  }
}
```

---

## 5. Roadmap (phased)

### ✅ Completed

**Foundation · v3 lean rebuild**
- v3.0 core · presets · history · theme

**Hub (community knowledge) · Phase 0-2**
- 12-category contribution system (session-scoped)
- Auto-save every analysis as case (heuristic categorize)
- AI organizer (layers · related pages · keywords · proposed new)

**Backlog · ALL 7 re-additions done** ✨
- Project Save/Load JSON
- HTML + PDF export (Sarabun)
- Share link (gzip+base64 URL · view mode)
- Image generation (Gemini Flash Image · 4 views)
- Chat follow-up (per-analysis · 6 suggestions)
- Compare 2 analyses (diff + layer bars)
- Booking (4 services · mailto + .ics)
- Tier Free/Pro (quota + feature gate + pricing)

### ✅ Hub Phase 3-5 · ALL DONE

**Phase 3 · GitHub push** (`ac39c59`)
- `components/github_sync.py` · PAT auth via Streamlit secrets
- Per-entry 🚀 ส่งขึ้น GitHub button
- Graceful 401/403/404/422 error handling with Thai messages
- Path convention: `contributions/{type}/{date}_{slug}_{id}.json`

**Phase 4 · Admin moderation** (`e321770`)
- `?admin=<token>` constant-time auth
- `components/admin.py` · review queue with status filter
- 3 actions per entry: ✅ approve · ❌ reject (reason required) · ✏ edit+approve
- GitHub API writes (PUT contents) with commit trail

**Phase 5 · Auto-rebuild pipeline** (`3ca80ea`)
- `scripts/ingest_contributions.py` · local CLI or GH Actions
- `.github/workflows/promote-approved.yml` · approved JSON → .md
- `.github/workflows/rebuild-kg.yml` · wiki change → regen KG + commit
- Flexible vault resolution (env var / sibling / mirror / legacy)
- Daily 03:15 UTC cron as safety net

**Full closed loop:**
```
User writes → 🚀 pushes to GitHub → Admin ✅ approves →
GH Action promotes to wiki-mirror/ → GH Action rebuilds KG →
Streamlit Cloud redeploys → AI sees new content
```

### 🟢 Nice-to-have after Hub 3-5

- **Real payment integration** (Stripe international · PromptPay QR for TH)
- **Auth:** optional Google OAuth for persistent history across devices
- **Supabase / SQLite** for server-side storage (beyond session)
- **PWA / offline mode** · service worker + offline cache of KG
- **Team plan** · shared workspace · role-based contributions
- **Analytics:** contribution rate · approval rate · popular categories

### 🔴 Permanent skip

- `streamlit-drawable-canvas` (draw-plan / annotate) — lib abandoned
- `streamlit-agraph` (KG graph viz) — lib abandoned
- **If needed later:** rewrite as pure HTML canvas or vis-network iframe
- Multi-page `pages/` folder — caused brittle CSS injection

---

## 6. Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| **Runtime** | Streamlit (latest) | Fastest Python → web · Cloud free tier |
| **Hosting** | Streamlit Community Cloud | Free · auto-deploy from GitHub |
| **AI Primary** | Google Gemini 2.5 Flash | Free 1,500/day · fast |
| **AI Secondary** | Anthropic Claude Sonnet 4.6 | Higher quality · paid |
| **Storage (now)** | `st.session_state` | No backend needed |
| **Storage (future)** | GitHub repo (via API) | Version-controlled · transparent · free |
| **Knowledge base** | JSON + markdown in repo | Portable · diffable · no DB |
| **KG format** | kg-compact.json (nodes + edges) | Feedable to any LLM |
| **Python** | 3.11 (Streamlit Cloud default) | Stability for 3rd-party libs |

### Dependencies (requirements.txt)

```
streamlit>=1.30.0
requests>=2.31.0
anthropic>=0.18.0
Pillow>=10.0.0
pandas>=2.0.0
```

**ลบ:** streamlit-drawable-canvas · streamlit-agraph · reportlab (ยังลบอยู่ · จะกลับมาใน Phase BL-PDF)

---

## 7. Key Decisions / Principles

### 🎯 Keep it stable
- **ไม่แตะ** Streamlit internal class names (`.css-xyz`) · ใช้ `[data-testid="..."]` เท่านั้น
- **Defensive** API calls · fallback ถ้า parse ไม่ได้
- **1 feature ต่อ commit** · test ก่อน push · ถ้าพังค่อย rollback ง่าย
- **Preserve** legacy-v2 branch ไว้ revive features

### 🧠 Trust through transparency
- ทุก analysis มี **source citations** จาก wiki
- AI ไม่ให้สร้างตัวเลขเอง (กฎหมาย) · ถ้าไม่มี source → ใส่ `null`
- Contribution status ชัด (pending · approved · rejected)
- Public audit trail ใน `contributions/` folder

### 🌱 Grow organically
- ไม่มี database · GitHub repo เป็น single source of truth
- Schema เป็น JSON (diffable · versionable)
- Export paths: every piece of data ดาวน์โหลดได้

### 🇹🇭 Thai-first, bilingual
- UI · content ส่วนใหญ่เป็นไทย
- ศัพท์เทคนิคอังกฤษได้ (FAR · OSR · MEP · BIM)
- Code comments / commits / schema keys เป็นอังกฤษ (maintainability)

---

## 8. Success Metrics

### 📊 Engagement
- Analyses per session · > 1.5 = ผู้ใช้ลองหลายแบบ
- Contributions / analyses · > 10% = ชุมชนเริ่ม contribute
- Repeat visitors (weekly) · > 20 = มี traction

### 🧠 Knowledge growth
- Wiki pages · 104 (now) → 200 (Q3 2026) → 500 (2027)
- Contributions approved rate · > 60% = quality control ok

### 💼 Business (if monetized)
- Booking conversions · 2-5% ของ analyses (realistic)
- Pro tier upgrade · 1-3% ของ active users

---

## 9. Open Questions

### 🔐 Auth model (Phase 3+)
- **Q:** GitHub PAT แบบไหน · shared (app-level) · หรือ per-user?
- **Recommendation:** Shared app PAT ใน Streamlit secrets · user ไม่ต้อง login
- **Concern:** rate limit GitHub API (5,000/hr per PAT · พอใช้)

### 👮 Moderation workflow (Phase 4)
- **Q:** Narongsak คนเดียว · หรือ delegate?
- **Recommendation:** คนเดียวก่อน · ถ้าเกิน 50 contributions/สัปดาห์ ค่อยคิด

### 💰 Monetization (future)
- **Q:** Free tier พอมั้ย · ทำ Pro จริงไหม?
- **Recommendation:** Free tier ก่อน · สะสม users 6 เดือน · ค่อย evaluate
- **Pro ideas:** priority support · custom branding on reports · bulk export · advanced AI models

### 🔒 Privacy
- **Q:** plan images ส่งไป AI · เก็บมั้ย?
- **Current answer:** ไม่เก็บ · ไม่ train AI · session-only
- **Future concern:** ถ้าเปิด auto-save to Hub · default off · opt-in explicit

### 🌐 Multi-user scale
- **Q:** ถ้า users โตถึง 1000/วัน · Streamlit Cloud free tier พอมั้ย?
- **Answer:** free tier มี 1 CPU + 1GB RAM · พอถึง ~100 concurrent · ถ้าเกินต้องย้าย

---

## 10. Non-goals (explicit · เพื่อไม่ให้หลงทาง)

- ❌ **ไม่ทำ full BIM tool** (ใช้ Revit/ArchiCAD/SketchUp อยู่แล้ว)
- ❌ **ไม่ทำ 3D rendering engine** (AI image generation พอ)
- ❌ **ไม่ทำ real-time collaboration** (Obsidian + GitHub พอ)
- ❌ **ไม่ทำ mobile app** (responsive web พอ · PWA ถ้าจำเป็น)
- ❌ **ไม่ replace สถาปนิกใบอนุญาต** — นี่คือ **assistant** ไม่ใช่ replacement
- ❌ **ไม่ให้คำแนะนำฮวงจุ้ยเฉพาะดวง** (ต้องซินแสตัวจริง)

---

## 11. References

### เอกสารที่เกี่ยวข้อง
- `CLAUDE.md` (ของ wiki vault) · schema ของ Obsidian wiki
- `system-prompt.md` · system prompt AI ใช้
- `scripts/build_kg.py` · KG generator
- `contributions/README.md` · contribution schema
- `README.md` · user-facing overview
- `DEPLOY.md` · deployment instructions

### Wiki structure (Obsidian vault)
```
E:/Narongsakb/NarongsakBIM/
├── CLAUDE.md           # schema
├── index.md            # catalog · 104/104 synced
├── log.md              # audit trail
├── raw/                # immutable sources (21 papers/articles)
└── wiki/               # 104 pages total
    ├── concepts/       # 69 concept pages across 5 layers + 8 subgroups
    ├── syntheses/      # 13 templates/analyses
    ├── entities/       # 8 legal/organizational
    └── summaries/      # 14 raw-source summaries
```

**Subgroup tally under `concepts/`:**
ชั้น 1 กฎหมาย 8 · ชั้น 2 วิศวกรรม 6 + smart home 3 · ชั้น 3 ออกแบบ 15 + BIM 3 + cost 3 + tropical 4 · ชั้น 4 ไทย 2 · ชั้น 5 ฮวงจุ้ย 1 · Interior 4 · Building types 4 · Specialty 3 · Theory 3 · Landscape 4 · Sustainability 2 · Renovation 2 · Business 2

### External links
- **Streamlit docs:** https://docs.streamlit.io
- **Gemini API:** https://ai.google.dev
- **Anthropic Claude:** https://docs.anthropic.com
- **Obsidian:** https://obsidian.md

---

## 12. Changelog (web app)

| Date | Version | Commit | Change |
|------|---------|--------|--------|
| 2026-04-18 | v3.0 | `7f22b83` | Lean rebuild · drop broken 3rd-party libs |
| 2026-04-18 | v3.1 | `3d6bf2a` | Restore: presets |
| 2026-04-18 | v3.2 | `9c17593` | Restore: history with per-item ops |
| 2026-04-18 | v3.3 | `de64f95` | Theme foundation · tokens · light/dark |
| 2026-04-18 | v3.4 | `e8a201f` | Hub Phase 0: contributions 12 categories |
| 2026-04-18 | v3.5 | `196ae61` | Hub Phase 1: auto-save case study |
| 2026-04-18 | v3.6 | `3f6e004` | Hub Phase 2: AI organizer |
| 2026-04-18 | v3.6.1 | `6e40cf2` | Fix: selectbox help must be str |
| 2026-04-18 | v3.7 | `6f4be17` | Add PRD · pause dev · capture state |
| 2026-04-18 | v3.8 | `a7bd136` | lint: sync index.md → KG (vault repo) |
| 2026-04-19 | v3.9 | `8898cf6` | Restore: Project Save/Load JSON |
| 2026-04-19 | v3.10 | `c1c466a` | Restore: HTML + PDF export (Sarabun) |
| 2026-04-19 | v3.11 | `e25aec9` | Restore: Share link + view mode |
| 2026-04-19 | v3.12 | `cf28e3b` | Restore: Image generation (4 views) |
| 2026-04-19 | v3.13 | `24c72b4` | Restore: Chat follow-up |
| 2026-04-20 | v3.14 | `812d13d` | Restore: Compare 2 analyses |
| 2026-04-20 | v3.15 | `aa7db64` | Restore: Booking + mailto + .ics |
| 2026-04-20 | v3.16 | `6e04db2` | Restore: Tier Free/Pro · feature parity ✨ |
| 2026-04-20 | v3.16.1 | `581fcea` | Fix: sidebar toggle button hidden by header CSS |
| 2026-04-20 | v3.17 | `ac39c59` | Hub Phase 3: GitHub push (PAT · contribute button) |
| 2026-04-20 | v3.18 | `e321770` | Hub Phase 4: Admin moderation (review queue · approve/reject/edit) |
| 2026-04-20 | v3.19 | `3ca80ea` | Hub Phase 5: Auto-rebuild pipeline (2 GH Actions · ADMIN.md) ✨ |
| 2026-04-18 | v3.6.1 | `6e40cf2` | Fix: selectbox help must be str |

---

## 13. Next session kickoff checklist

**All 22 features + Hub Phases 0-5 เสร็จสมบูรณ์** · เมื่อกลับมา focus ที่:

### 🧪 End-to-end testing first
1. [ ] `git pull` · pull ADMIN.md + workflows ใหม่
2. [ ] อ่าน **ADMIN.md** (setup walkthrough)
3. [ ] Set Streamlit secrets (`[github]` + `[admin]`)
4. [ ] Smoke test: ส่ง contribution จาก web → approve ที่ `?admin=<token>` →
      ดู GH Actions ทำงาน → verify wiki-mirror/ commit + kg-compact.json refresh
5. [ ] Test hostile paths: invalid PAT · expired token · mismatched admin token

### 🟢 Business layer (next iteration)
- **Real payment:** Stripe (inter'l) + PromptPay QR (TH) · webhook → auto-upgrade tier
- **OAuth:** Google login → persistent history across devices (needs Supabase/Firestore)
- **Team plan:** shared workspace · role-based contribute permissions

### 🎨 Polish (optional small wins)
- ship `fonts/Sarabun-Regular.ttf` → enable native PDF for Pro
- Pro badge watermark on exported PDF (branding)
- "วิเคราะห์ใหม่" button on share view → clean new tab
- Landing/About microsite for first-time visitors
- Usage analytics counter (total analyses · top categories)

### 🚨 Known future-proof needs
- Rotate PAT + admin token every 90 days
- Monitor GH Actions quota (free tier: 2000 min/mo)
- Clean up contributions/rejected/ folder periodically
- Backup Obsidian vault (it's the source of truth)

### วิธีเพิ่ม feature ใหม่อย่างปลอดภัย

```bash
# 1. Peek legacy-v2 ถ้าจะ revive feature เก่า
git show legacy-v2:components/FEATURE.py | head -200

# 2. Create fresh component (ไม่ copy-paste ตรงๆ · ปรับให้เข้ากับ v3)
# 3. Syntax check
python -c "import ast; ast.parse(open('components/FEATURE.py').read())"

# 4. Behavioral check ด้วย mocked streamlit
# (ดูแบบที่ใช้ใน session · stub st.* functions)

# 5. Commit single feature · message format:
#    "Restore #N: FEATURE · 1-line summary
#    - bullet 1
#    - bullet 2
#    Verified: ..."

# 6. Push · รอ Streamlit redeploy 2 นาที · test
```

---

*สุดท้าย · ระบบนี้ไม่ใช่ทำครั้งเดียวเสร็จ · มันจะโตไปเรื่อยๆ ตามคนใช้ · คนแก้ · คนสอน*

*Keep it simple · keep it honest · keep it growing 🌱*
