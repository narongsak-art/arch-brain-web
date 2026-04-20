# สมองจำลองของสถาปนิก · v6

> Thai Architect's Studio · AI-powered residential design analysis
> Minimal 2-file rebuild · sidebar-first · gallery-led · professional

**Live:** https://arch-brain-narongsak.streamlit.app
**Repo:** https://github.com/narongsak-art/arch-brain-web
**Branch:** `v6` (this) · legacy branches: `main` · `v5-beta` · `legacy-v2`

---

## What it does

กรอก brief บ้าน (ที่ดิน · ครอบครัว · งบ · ทิศ · priority) → AI วิเคราะห์
ผ่าน **5 ชั้นความรู้** (กฎหมาย · วิศวกรรม · ออกแบบ · วัฒนธรรมไทย · ฮวงจุ้ย)
→ structured result พร้อม client-ready portfolio export

## Screenshots

**Create (Welcome)** · big gallery of 8 visual preset tiles · click to fill form
**Create (Result)** · summary hero + site SVG + metrics + compliance + 5-layer + rooms + issues/strengths + design phases + next actions
**Studio** · card grid with pins · tag filter · client filter · feasibility filter · search
**Explore** · 104-node Knowledge Graph browser with detail view + related pages

## Features (v6 · architect edition)

### 📝 Inputs (all in sidebar)
- **8 preset templates** · ทาวน์เฮาส์ · บ้านเดี่ยวเล็ก/ใหญ่ · บ้านหรู · บ้านเล็ก กทม. · ห้องแถว · รีสอร์ทวิลลา · บ้านผู้สูงอายุ · each with unique gradient
- **Core brief** · ชื่อ · ขนาดที่ดิน · จังหวัด · เขต · ถนน · ครอบครัว · ชั้น · BR · งบ · ฮวงจุ้ย · ข้อพิเศษ
- **🧭 Architect detail** · 8-way orientation (visual compass) · topography · adjacent context · priority · grade · timeline
- **🏷 Tags + Notes** · client name · comma-separated tags · free-form notes
- **📎 Plan upload** · optional JPG/PNG

### 📊 Outputs
- **Summary hero** · feasibility emoji + score + concern/strength callouts
- **Site SVG** · inline diagram of plot + buildable area + north arrow rotated to orientation
- **FAR/OSR/budget bars** · color-coded (sage/gold/terra) progress bars
- **Metrics** · 8-10 key values in card grid
- **📋 Compliance** · 6 Thai building-code categories with pass/warning/fail + notes
- **🧩 5-Layer analysis** · score bar + findings per layer (expandable)
- **🚪 Rooms** · 6+ rooms with size/orientation/cultural/fengshui notes
- **🚨 Issues & ⭐ Strengths** · Top-ranked with actions
- **🧭 Design Phases** · SD/DD/CD/CA cards with tasks + deliverables + week-count
- **🎯 Next Actions** · table of steps with owner + timing

### 💾 Exports
- `.md` · Markdown report
- `.json` · structured data
- `.txt` · raw AI output
- **📑 Portfolio HTML** · full editorial layout · cover page · all sections · ready to print-to-PDF · ~20KB self-contained

### 📚 Studio
- Cards grid with feasibility badge + score + metadata
- 📌 Pin favorites to top section
- 🔎 Search · feasibility filter · tag filter · client filter
- Quick actions: Open (load back into Create) · Pin · Delete

### 🌐 Explore
- 104 Knowledge Graph nodes as cards
- Layer filter (กฎหมาย · วิศวกรรม · ออกแบบ · ไทย · ฮวงจุ้ย)
- Text search over title + summary
- Click card → detail view with **related pages graph** (from KG edges)

## Code structure

```
app.py              · all UI · CSS · sidebar · 3 views · routing  (~1400 lines)
brain.py            · AI + prompts + parsing + rendering + portfolio  (~1000 lines)
scripts/
  build_kg.py       · regenerate kg-compact.json from wiki vault
  selftest.py       · 10 diagnostic checks (run before release)
kg-compact.json     · 104 nodes · 425 edges (AI context)
full-knowledge.md   · 291 KB curated bundle (for cited numbers)
system-prompt.md    · base AI persona
contributions/      · staging folder for future community contributions
fonts/              · (optional) Sarabun TTF for native PDF
```

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Free Gemini API key: https://aistudio.google.com/apikey (1,500 req/day)

## Tests

```bash
python scripts/selftest.py
```

Runs 10 checks: syntax · imports · JSON parser · 8 presets · site SVG ·
portfolio HTML · prompts · KG integrity · CSS fragility · view rendering.

## Tech

- **Python 3.11** · Streamlit
- **Google Gemini 2.5 Flash** (free) or **Claude Sonnet 4.6** (paid)
- **No backend** · session state + repo-committed knowledge
- **No 3rd-party UI libs** beyond Streamlit core

## Design language

- Palette · ครีม (`#fbf9f3`) · ไม้สัก (`#7a4e24`) · ทอง (`#b89755`) · ดินเผา (`#b16a57`) · ใบข่า (`#6b7f64`)
- Fonts · Bai Jamjuree (display) + Sarabun (body)
- Editorial feel · generous whitespace · subtle shadows · 12-16px radius

## Built with ❤ for Thai architects and homeowners

Disclaimer: ผลวิเคราะห์เป็นการประเมินเบื้องต้น · ไม่แทนสถาปนิก/วิศวกรใบอนุญาต
