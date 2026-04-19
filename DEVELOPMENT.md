# Development Guide · แนวทางพัฒนาต่อ

คู่มือสำหรับคุณ (Narongsak) หรือ dev ที่มาทำต่อในอนาคต · 2026-04-20

---

## 🎯 หลักการพัฒนา (learned · อย่าลืม)

### 🟢 Do
- **ใช้ [data-testid="..."]** ใน CSS selector เท่านั้น · stable across Streamlit versions
- **1 feature ต่อ 1 commit** · syntax + behavioral test ทุกครั้งก่อน push
- **Session state หลีกเลี่ยง mutate after widget instantiation** · ใช้ `on_click`/`on_change` callback แทน
- **Graceful fallback** ทุก API call · ห้าม crash
- **Docs updated** · stat numbers match (104 nodes · ใช้ selftest เช็ค)

### 🔴 Don't
- ❌ target Streamlit internal class `.css-xyz` · `class*="st-"` · `.element-container`
- ❌ hide parent container (`visibility: hidden` or `display: none`) ถ้ามี child ที่ต้องการให้เห็น (เช่น sidebar toggle อยู่ใน stToolbar)
- ❌ เพิ่ม third-party lib ที่ไม่ได้ update ล่าสุด (streamlit-drawable-canvas · streamlit-agraph ตายแล้ว)
- ❌ Pin Streamlit version · ให้ track latest · ถ้าเจอ breaking change · แก้ด้วย CSS fallback
- ❌ ใช้ multi-page (`pages/` folder) · ทำให้ CSS inject ยุ่ง · ใช้ tabs แทน

---

## 🏗 Architecture at a glance

```
app.py (~520 บรรทัด)
  ├─ main() · entry
  ├─ Special modes (checked first):
  │   · admin.is_admin_mode() → admin.render_panel()
  │   · share.is_share_mode() → share.render_view()
  ├─ render_sidebar() · theme toggle + tier badge + AI config + 📖 5 layers info
  ├─ render_hero() · gradient banner via theme.hero()
  ├─ render_welcome_onboarding() · if no api_key yet
  ├─ render_form() · project brief (+ preset chips)
  ├─ File uploader · optional plan image
  ├─ Analyze button (gated by tiers.check_quota)
  ├─ render_result() · if result exists
  │   ├─ analysis.render() · structured display
  │   ├─ _render_save_to_hub() · auto-categorize case
  │   ├─ share.render_share_panel() · URL + fallback json
  │   └─ Downloads (5 formats · PDF gated for Pro)
  └─ render_tabs_section() · 8 tabs for secondary tools
```

### Import graph

```
theme    · zero deps · everyone imports
llm      · Gemini + Claude clients · used by: analysis-runner, chat, image_gen
analysis · prompt/parse/render/md · used by: app, history, chat, compare, share
presets  · form-fill callback · used by: app
history  · session list · used by: app, chat, compare, contribute, share-encode
contribute · 12-cat hub · imports: analysis, llm, github_sync
github_sync · PAT auth + API · used by: contribute, admin
admin    · moderation · imports: github_sync, contribute (for CATEGORIES/TYPES)
project_io · Save/Load · used by: app (+ has _build_pd_from_form helper)
export_pdf · HTML + reportlab · used by: app
share    · gzip+base64 URL · used by: app
image_gen · Gemini Flash Image · used by: app
chat     · follow-up Q&A · imports: history, llm
compare  · side-by-side · imports: history, analysis
booking  · consultation · used by: app
tiers    · quota + feature gate · used by: app
```

---

## 🔧 Recipe: เพิ่ม feature ใหม่

### 1. ตัดสินใจ scope
- **Tab?** → เพิ่มใน `render_tabs_section` · ต้องมี session state
- **ปุ่มใน result?** → เพิ่มใน `render_result` · ใช้ current analysis
- **Page mode?** (เหมือน admin/share) → ใส่ check บน `main()` · render เอง
- **Component ย่อย?** → new file ใน `components/`

### 2. สร้าง component
```python
# components/my_feature.py
"""My Feature · 1-line description of what it does"""

import streamlit as st

def render_panel():
    """Main entry · call from app.py or a tab"""
    st.markdown("### ✨ My Feature")
    # ...
```

### 3. Syntax check
```bash
python -c "import ast; ast.parse(open('components/my_feature.py').read())"
```

### 4. Behavioral test (mocked Streamlit)
```python
# Stub minimal st.* functions → exercise core logic
# See scripts/selftest.py for reference mocking
```

### 5. Integrate
```python
# app.py
from components import ..., my_feature

# somewhere:
my_feature.render_panel()
```

### 6. Add to selftest
- แก้ `scripts/selftest.py` · เพิ่ม @check แต่ละ feature ใหม่
- Run: `python scripts/selftest.py` · ต้อง 14/14 (หรือ more)

### 7. Commit single feature
```
Restore/Add #N: FEATURE · 1-line summary

- bullet 1
- bullet 2

Verified: ...
```

### 8. Update docs
- `PRD.md` · feature table + changelog
- `README.md` · feature list (ถ้าเป็น user-facing)
- `USER_GUIDE.md` · how-to (ถ้าใช้ยาก)

---

## 📂 ถ้าจะเพิ่ม wiki page ใหม่

### Method 1: ผ่านเว็ปอย่างเดียว (ไม่ใช่ admin)
1. เปิด web app · tab **💡 ช่วยเติม**
2. เขียน contribution ประเภท "💡 เสนอเรื่องใหม่"
3. ✨ AI ช่วยจัดระเบียบ → AI แนะนำ layers · related pages
4. 🚀 ส่งขึ้น GitHub (ต้อง secrets ตั้งไว้)
5. Admin เปิด `?admin=<token>` → review → ✅ Approve
6. GH Action auto-promote → .md ใน wiki-mirror/ → regen KG

### Method 2: เขียนตรงในวอลต์ (สำหรับ Narongsak)
1. สร้าง `wiki/concepts/ชื่อหน้า.md` ใน NarongsakBIM vault
2. ใส่ frontmatter (title/type/layers/applies_to/etc) per CLAUDE.md schema
3. อัปเดต `index.md` · เพิ่มบรรทัดภายใต้ subsection ที่เหมาะ
4. Append เข้า `log.md` · entry `[YYYY-MM-DD] ingest | Title`
5. Run `python scripts/build_kg.py` → kg-compact.json + full-knowledge.md refresh
6. Commit web repo · push · Streamlit redeploy auto

---

## 🧪 Testing

### Local fast tests
```bash
python scripts/selftest.py        # 13 diagnostic checks · ~30 sec
python scripts/build_kg.py        # regen KG from local vault
python scripts/ingest_contributions.py --dry-run  # preview ingest
```

### CI (GitHub Actions)
- `.github/workflows/selftest.yml` · รันทุก push to main
- `.github/workflows/rebuild-kg.yml` · regen KG เมื่อ wiki เปลี่ยน
- `.github/workflows/promote-approved.yml` · ingest approved contributions

### Manual end-to-end (ที่คุณต้องทำเอง)
ดู **USER_GUIDE.md §ทดสอบ** สำหรับ checklist 20+ items

---

## 🚀 Deployment

### Streamlit Cloud (primary)
- Auto-deploy จาก main branch · 1-3 นาทีหลัง push
- Python 3.11 (lock to deployed default · ไม่ pin)
- Secrets ใน app settings (**ไม่ใส่ใน repo**)

### Required secrets (ถ้าใช้ admin/github push)
```toml
[github]
token = "ghp_..."
repo = "narongsak-art/arch-brain-web"
branch = "main"

[admin]
token = "32+ char random string"
```

### Local dev
```bash
git clone https://github.com/narongsak-art/arch-brain-web.git
cd arch-brain-web
pip install -r requirements.txt
streamlit run app.py
```

---

## 📋 Roadmap · แนวทางพัฒนาต่อ

### 🟢 Short-term (1-2 สัปดาห์)

**1. Ship Sarabun TTF**
- Download `Sarabun-Regular.ttf` + `Sarabun-Bold.ttf` from Google Fonts
- วางใน `fonts/` folder · commit
- Native PDF export ใน Pro tier จะทำงานทันที

**2. Real payment · PromptPay QR**
- เพิ่ม component `payment.py`
- PromptPay QR generation (libs: `promptpay-python`)
- Webhook จาก บก.ธปท. · verify → auto-upgrade user เป็น Pro
- Session-scoped upgrade (เพราะไม่มี backend db)

**3. Landing microsite**
- Marketing copy · hero animation
- "How it works" video placeholder
- Pricing grid · social proof slot

### 🟡 Medium-term (1 เดือน)

**4. OAuth + persistent accounts**
- Google OAuth (ง่ายสุดสำหรับ TH users)
- Supabase Auth (free tier 50K MAU)
- Persist: history · contributions · tier subscription

**5. Team plan**
- Shared workspace · role-based (owner/contributor/viewer)
- Team-level tier (ลด per-seat)
- Shared contributions queue

**6. Analytics dashboard**
- Track: analyses/day · popular presets · top categories
- Show in admin view
- Weekly email digest สำหรับคุณ

### 🔵 Long-term (3+ เดือน)

**7. PWA + offline**
- Service worker · cache KG + full-knowledge
- Offline analysis (ต้องมี local LLM หรือ cache previous results)

**8. Multi-language**
- English translation (AI-assisted)
- Support region-specific laws (Vietnam · Indonesia · Malaysia)

**9. Partner integrations**
- Export → AutoCAD · Revit · SketchUp
- Integration กับผู้ผลิตวัสดุ (BOQ auto-populate)

---

## 🧹 Maintenance rhythm

### Weekly (5 นาที)
- [ ] ดู GitHub Actions tab · ทุก workflow green?
- [ ] Admin mode · review pending contributions (ถ้ามี)
- [ ] Quick smoke test: analyze 1 preset · ทำงานปกติ?

### Monthly (15 นาที)
- [ ] `git pull` · ดูว่ามี breaking change ใน Streamlit ไหม
- [ ] Run `scripts/selftest.py` · 13/13 ทั้งหมด
- [ ] Check Streamlit Cloud quota · ยังอยู่ใน free tier?
- [ ] Review rejected contributions folder · ลบหรือ refactor

### Quarterly (1 ชม.)
- [ ] Rotate GitHub PAT (ทุก 90 วัน)
- [ ] Rotate admin token
- [ ] Review `legacy-v2` branch · ต้อง revive feature เก่าไหม?
- [ ] Update PRD changelog + version
- [ ] Backup Obsidian vault (local → external drive/cloud)

---

## 🔐 Security checklist

- [ ] `.streamlit/secrets.toml` อยู่ใน `.gitignore` ✓
- [ ] Secrets ใน Streamlit Cloud UI · ไม่ในโค้ด ✓
- [ ] GitHub PAT scope แคบสุด (`repo` only · ไม่มี admin) ✓
- [ ] Admin token ≥ 32 chars random ✓
- [ ] GH Action permissions `contents: write` เฉพาะ ✓
- [ ] ไม่ log API keys ใน error messages ✓
- [ ] User content (contributions) ผ่าน admin review ก่อนเข้า wiki ✓

---

## 🚨 Emergency procedures

### เว็ปพัง (500 error)
1. ดู Streamlit Cloud logs · หา traceback
2. `git log` · ดู commit ล่าสุด · มี syntax error ไหม?
3. ถ้าฉุกเฉิน: `git revert HEAD` · push · redeploy
4. ถ้ายังพัง: `git checkout legacy-v2` · redeploy จาก backup branch

### PAT / token leak
1. **Rotate ทันที** · github.com/settings/tokens → Delete
2. Generate PAT ใหม่ · update Streamlit secrets
3. ถ้ามี admin token ใน URL log · generate admin token ใหม่เช่นกัน
4. Audit GitHub commit history · ไม่มีการ leak ใน commits

### Knowledge graph corrupted
1. `git log kg-compact.json` · หา commit ที่ OK ก่อนหน้า
2. `git checkout <commit> -- kg-compact.json full-knowledge.md`
3. Commit · push
4. Run `scripts/selftest.py` → check integrity 13/13

### GH Actions quota ใกล้หมด (free tier 2000 min/mo)
1. Pause `rebuild-kg` daily cron (`schedule:`)
2. Keep `selftest` (runs <1 min per PR · negligible)
3. Switch `promote-approved` to manual trigger only (`workflow_dispatch`)

---

## 📚 References

- [Streamlit docs](https://docs.streamlit.io)
- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [Claude API](https://docs.anthropic.com)
- [GitHub REST API (contents)](https://docs.github.com/en/rest/repos/contents)
- [Obsidian · vault format](https://help.obsidian.md)

---

## 📝 Notes for future-you

> *"เมื่อกลับมาทำต่อหลังหยุดไปนาน · อ่านไฟล์นี้ + PRD.md ก่อน · แล้วรัน `scripts/selftest.py` · ถ้ามี FAIL ก่อนเริ่ม feature ใหม่ · fix ก่อน"*

> *"1 commit = 1 feature · ไม่มีข้อยกเว้น · ประสบการณ์เรียนรู้มาว่าถ้า bundle หลายอย่างพังแล้ว revert ยาก"*

> *"ถ้าเจอ library ที่ abandoned · อย่าพยายามพยายาม · เขียนเองดีกว่า (lesson learned from streamlit-drawable-canvas)"*

Keep it simple · keep it honest · keep it growing 🌱
