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

### 📊 Knowledge Graph

- **104 nodes** (wiki pages) · **425 edges** (wikilinks)
- **291 KB** full-knowledge.md · bundled 32 curated pages
- **4 new tracks:** Smart Home · Cost Estimation · BIM · Tropical Design (16 pages · +5,821 บรรทัด)

### 🏗 Architecture (clean · 9 files)

```
arch-brain-web/
├── app.py                      # main (~450 lines)
├── components/
│   ├── theme.py                # CSS tokens + light/dark
│   ├── llm.py                  # Gemini + Claude clients
│   ├── analysis.py             # structured JSON prompt/parser/renderer
│   ├── presets.py              # 5 home-type templates
│   ├── history.py              # session history + per-item ops
│   └── contribute.py           # hub + AI organizer
├── scripts/build_kg.py         # wiki → kg-compact.json
├── kg-compact.json             # 104 nodes
├── full-knowledge.md           # 291 KB curated bundle
├── system-prompt.md            # AI system prompt
└── contributions/              # Tier 2 staging (future)
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
- **Phase v3.0** · lean rebuild · stable foundation
- **Hub Phase 0** · contributions schema + UI (session-only)
- **Hub Phase 1** · auto-save analysis as case (heuristic categorize)
- **Hub Phase 2** · AI organizer (layers · related · keywords)

### 🟡 In flight / Next

**Hub Phase 3 · GitHub push**
- `scripts/submit_contribution.py` · POST ผ่าน GitHub API
- User PAT ใน `.streamlit/secrets.toml` (shared token) หรือ per-user
- สร้าง commit อัตโนมัติใน `contributions/{type}/{date}_{slug}.json`
- PR-based workflow (optional): สร้าง PR แทน direct commit

**Hub Phase 4 · Admin moderation**
- Admin mode `?admin=TOKEN` + passphrase ใน secrets
- Review queue · approve/reject/edit
- Approve → `scripts/ingest_contribution.py` เขียน `.md` ลง `wiki/` + regen KG
- Reject → note reason · ไม่ลบ (audit)

**Hub Phase 5 · Auto-rebuild pipeline**
- GitHub Action: on push to `wiki/**` → run `build_kg.py` → commit `kg-compact.json`
- Streamlit Cloud redeploy อัตโนมัติ

### 🔵 Backlog (feature re-additions)

แต่ละตัวคือ 1 commit · ค่อยๆ เติม · test ทุกครั้ง:

| Feature | เก่า (legacy-v2) | Risk | Est. |
|---------|-----------------|------|------|
| **Project save/load JSON** | project_io.py | low | 1 คอมมิต |
| **PDF export** (Sarabun font) | export_pdf.py | low (reportlab stable) | 1 คอมมิต |
| **Share link** (gzip+base64 URL) | share.py + View page | low | 1-2 คอมมิต |
| **Image generation** (Gemini Flash Image) | image_gen.py | medium (API stability) | 1 คอมมิต |
| **Chat follow-up** | chat.py | medium | 1 คอมมิต |
| **Compare 2 analyses** | compare.py | low | 1 คอมมิต |
| **Booking system** | booking.py | low | 1 คอมมิต |
| **Tier (Free/Pro)** | tiers.py | low (quota only) | 1 คอมมิต |

### 🔴 Permanent skip

- `streamlit-drawable-canvas` (draw-plan / annotate)
- `streamlit-agraph` (KG graph viz)
- **ถ้าอยากได้:** รอ lib maintainers · หรือเขียน custom HTML canvas · หรือใช้ Gradio/Dash แทน

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
├── index.md            # catalog
├── log.md              # audit trail
├── raw/                # immutable sources
└── wiki/
    ├── concepts/       # 88+ concept pages
    ├── syntheses/      # 14+ templates/analyses
    ├── entities/       # placeholders
    └── summaries/      # ingest summaries
```

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

---

## 13. Next session kickoff checklist

เมื่อกลับมาทำต่อ · ทำตามลำดับนี้:

1. [ ] `git pull` · ดู commit ล่าสุดบน main
2. [ ] Test ที่ deployed URL · screenshot ถ้าเจอบัค
3. [ ] อ่าน PRD นี้อีกครั้ง · update Roadmap section ถ้ามีการเปลี่ยน priority
4. [ ] เลือก Feature ถัดไปจาก **Hub Phase 3-5** หรือ **Backlog**
5. [ ] ทำ 1 feature · syntax check + behavioral test · commit + push
6. [ ] Update Changelog ใน PRD นี้

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
