# สมองจำลองของสถาปนิก · v6

> Thai Architect's Studio · AI-powered residential analysis
> Minimal sidebar-first rebuild · 2 Python files · ~1000 lines total

**Live:** https://arch-brain-narongsak.streamlit.app
**Repo:** https://github.com/narongsak-art/arch-brain-web

---

## What it does

Input a Thai home brief (land · family · budget · requirements) → AI analyzes through
**5 layers** (กฎหมาย · วิศวกรรม · ออกแบบ · วัฒนธรรมไทย · ฮวงจุ้ย) → structured result
with metrics · 5-layer scores · per-room breakdown · top issues · next actions.

## Layout

**Sidebar (left):** inputs — AI config + project form + analyze button
**Main (right):** output — welcome / analysis result / gallery / knowledge browser

**3 views** via sidebar radio:
- 🎨 **Create** · form → analyze → result + downloads
- 📚 **My Studio** · gallery of past analyses
- 🌐 **Explore** · browse 104 Knowledge Graph pages with related links

## Code

2 files:
- `app.py` — UI + flow + sidebar + 3 views
- `brain.py` — AI clients + prompt + parser + renderer + markdown export

Plus data (unchanged):
- `kg-compact.json` · 104 nodes · 425 edges
- `full-knowledge.md` · 291 KB curated bundle
- `system-prompt.md` · AI system prompt

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Get a free Gemini API key at https://aistudio.google.com/apikey (1,500 requests/day).

## Branches

- `main` · this (v6 · current)
- `v5-beta` · earlier rebuild · 3 views + core/ + views/ · preserved
- `legacy-v2` · v2 feature-complete (19 components) · preserved for reference

---

Built with ❤ for Thai architects and homeowners
