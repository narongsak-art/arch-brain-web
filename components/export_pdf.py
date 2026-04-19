"""PDF / HTML export · print-ready reports with Thai font support

Three paths:
1. HTML export (PRIMARY, works everywhere):
   - Self-contained .html with Sarabun via Google Fonts <link>
   - User opens in browser → Ctrl+P → Save as PDF
   - Zero dependencies beyond stdlib

2. Native PDF via reportlab (BONUS, if Sarabun TTF shipped):
   - fonts/Sarabun-Regular.ttf (optional)
   - Falls back gracefully to HTML-only if reportlab or font missing

3. Portfolio HTML (comprehensive client deliverable):
   - Cover + brief + analysis + palette + images · all one file
   - Thai editorial styling · ready to present/print
"""

import base64
import io
import json
import re
from datetime import datetime
from pathlib import Path


# ============================================================================
# Minimal markdown → HTML (enough for our analysis output)
# ============================================================================

def _escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline_md(text: str) -> str:
    text = _escape_html(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(md: str) -> str:
    """Very small MD subset: headings, lists, code fences, paragraphs, tables"""
    lines = md.split("\n")
    out: list[str] = []
    in_list = False
    in_code = False
    in_table = False
    table_buf: list[str] = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def close_code():
        nonlocal in_code
        if in_code:
            out.append("</pre>")
            in_code = False

    def flush_table():
        nonlocal in_table, table_buf
        if not in_table:
            return
        if len(table_buf) >= 2:
            header = table_buf[0]
            # rows = table_buf[2:]  # skip separator row
            hcells = [c.strip() for c in header.strip("|").split("|")]
            out.append("<table>")
            out.append("<thead><tr>" + "".join(f"<th>{_inline_md(c)}</th>" for c in hcells) + "</tr></thead>")
            out.append("<tbody>")
            for row in table_buf[2:]:
                cells = [c.strip() for c in row.strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{_inline_md(c)}</td>" for c in cells) + "</tr>")
            out.append("</tbody></table>")
        in_table = False
        table_buf = []

    for raw in lines:
        line = raw.rstrip()

        # Fenced code
        if line.startswith("```"):
            close_list()
            flush_table()
            if in_code:
                close_code()
            else:
                out.append('<pre class="code">')
                in_code = True
            continue
        if in_code:
            out.append(_escape_html(line))
            continue

        # Table
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                close_list()
                in_table = True
                table_buf = []
            table_buf.append(line)
            continue
        else:
            flush_table()

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_list()
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline_md(m.group(2))}</h{level}>")
            continue

        # Lists
        if re.match(r"^\s*[-*•]\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = re.sub(r"^\s*[-*•]\s+", "", line)
            out.append(f"<li>{_inline_md(item)}</li>")
            continue

        # Horizontal rule
        if line.strip() == "---":
            close_list()
            out.append("<hr/>")
            continue

        # Blank line
        if line.strip() == "":
            close_list()
            continue

        # Paragraph
        out.append(f"<p>{_inline_md(line)}</p>")

    close_list()
    close_code()
    flush_table()
    return "\n".join(out)


# ============================================================================
# HTML export (primary)
# ============================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>ผลวิเคราะห์ — {title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: 'Sarabun', 'Tahoma', sans-serif;
    line-height: 1.6;
    color: #222;
    max-width: 820px;
    margin: 20px auto;
    padding: 20px;
    background: #fff;
  }}
  .header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 24px;
  }}
  .header h1 {{ margin: 0 0 8px 0; font-weight: 700; color: #fff; }}
  .meta {{ font-size: 0.92em; opacity: 0.95; }}
  .data-box {{
    background: #f6f8fb;
    border: 1px solid #e0e4ea;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 16px 0;
  }}
  pre.code {{
    background: #f3f4f6;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 0.88em;
    white-space: pre-wrap;
    font-family: 'Consolas', 'Menlo', monospace;
  }}
  h1, h2, h3, h4 {{ color: #1e293b; margin-top: 1.2em; }}
  h2 {{ border-bottom: 2px solid #667eea; padding-bottom: 4px; }}
  ul {{ padding-left: 1.4em; }}
  li {{ margin: 4px 0; }}
  code {{ background: #f3f4f6; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 0.92em; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; }}
  thead th {{ background: #eef2ff; }}
  .disclaimer {{
    margin-top: 40px;
    padding: 14px;
    background: #fff8e6;
    border-left: 4px solid #f59e0b;
    border-radius: 6px;
    font-size: 0.88em;
    color: #6b5b1e;
  }}
  .footer {{
    margin-top: 20px;
    text-align: center;
    color: #888;
    font-size: 0.82em;
  }}
  @media print {{
    body {{ margin: 0; padding: 14mm; max-width: none; }}
    .header {{ break-inside: avoid; }}
    .no-print {{ display: none !important; }}
  }}
  .print-btn {{
    position: fixed; top: 14px; right: 14px;
    background: #667eea; color: #fff; padding: 10px 18px;
    border: none; border-radius: 8px; cursor: pointer;
    font-family: inherit; font-weight: 600;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  }}
</style>
</head>
<body>
  <button class="print-btn no-print" onclick="window.print()">🖨 พิมพ์ / Save as PDF</button>

  <div class="header">
    <h1>🏠 ผลวิเคราะห์ — {title}</h1>
    <div class="meta">
      <div>วันที่: {timestamp}</div>
      <div>Provider: {provider}</div>
    </div>
  </div>

  <h2>📋 ข้อมูลโครงการ</h2>
  <div class="data-box">
    <pre class="code">{project_json}</pre>
  </div>

  <h2>📊 ผลวิเคราะห์</h2>
  {analysis_html}

  <div class="disclaimer">
    <strong>⚠ Disclaimer:</strong>
    ผลเป็นการวิเคราะห์เบื้องต้น · ไม่แทนสถาปนิก/วิศวกรใบอนุญาต ·
    การขออนุญาตก่อสร้างต้องมีลายเซ็นผู้ประกอบวิชาชีพ (พรบ.ควบคุมอาคาร 2522 มาตรา 49 ทวิ)
  </div>
  <div class="footer">
    สร้างโดย สมองจำลองของสถาปนิก · Thai Residential Architecture Analysis
  </div>
</body>
</html>
"""


def build_print_html(project_data: dict, analysis_md: str, provider: str) -> str:
    """Self-contained HTML → user opens in browser → Ctrl+P to save as PDF"""
    title = _escape_html(project_data.get("name", ""))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    project_json = _escape_html(json.dumps(project_data, ensure_ascii=False, indent=2))
    analysis_html = markdown_to_html(analysis_md)
    return HTML_TEMPLATE.format(
        title=title, timestamp=ts, provider=provider.title(),
        project_json=project_json, analysis_html=analysis_html,
    )


# ============================================================================
# Native PDF via reportlab (bonus if font available)
# ============================================================================

PORTFOLIO_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>Portfolio — {title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@500;600;700&family=Sarabun:wght@300;400;500;600;700&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --cream: #faf7f0; --sand: #f4efe3; --border: #e5dfcf;
    --teak: #8b5a2b; --gold: #c9a961; --terra: #c97864;
    --ink: #2d1f15; --muted: #6b5842;
    --font-display: 'Bai Jamjuree', 'Playfair Display', 'Sarabun', serif;
    --font-body: 'Sarabun', sans-serif;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: var(--font-body);
    background: var(--cream);
    color: var(--ink);
    margin: 0;
    line-height: 1.6;
  }}
  .page {{
    max-width: 860px;
    margin: 0 auto;
    padding: 40px 48px;
  }}

  /* COVER PAGE */
  .cover {{
    min-height: 70vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 60px 48px;
    background: linear-gradient(135deg, var(--teak) 0%, var(--gold) 55%, var(--terra) 100%);
    color: #fff;
    margin-bottom: 0;
    page-break-after: always;
    position: relative;
    overflow: hidden;
  }}
  .cover::after {{
    content: "";
    position: absolute; inset: 0;
    background: radial-gradient(circle at 15% 20%, rgba(255,255,255,0.12) 0%, transparent 45%),
                radial-gradient(circle at 85% 80%, rgba(255,255,255,0.08) 0%, transparent 45%);
    pointer-events: none;
  }}
  .cover-eyebrow {{
    font-family: var(--font-display);
    font-size: 0.9em;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    opacity: 0.9;
    margin-bottom: 12px;
    position: relative;
  }}
  .cover h1 {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 3.5em;
    line-height: 1.1;
    margin: 0 0 14px 0;
    letter-spacing: -0.02em;
    position: relative;
  }}
  .cover .subtitle {{
    font-size: 1.3em;
    opacity: 0.95;
    max-width: 620px;
    margin: 0 0 32px 0;
    position: relative;
  }}
  .cover-meta {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 18px;
    padding-top: 24px;
    border-top: 1px solid rgba(255,255,255,0.25);
    position: relative;
    max-width: 720px;
  }}
  .cover-meta .m-label {{
    font-size: 0.72em;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.8;
    margin-bottom: 4px;
  }}
  .cover-meta .m-value {{
    font-family: var(--font-display);
    font-size: 1.15em;
    font-weight: 600;
  }}

  /* SECTIONS */
  .section {{
    padding: 50px 48px;
    border-bottom: 1px solid var(--border);
  }}
  .section:last-child {{ border-bottom: none; }}
  .section .eyebrow {{
    font-family: var(--font-display);
    color: var(--teak);
    font-size: 0.85em;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .section h2 {{
    font-family: var(--font-display);
    font-size: 2em;
    font-weight: 700;
    margin: 0 0 24px 0;
    color: var(--ink);
    letter-spacing: -0.015em;
  }}
  .section h3 {{
    font-family: var(--font-display);
    font-size: 1.35em;
    font-weight: 600;
    margin: 22px 0 10px 0;
    color: var(--ink);
  }}

  /* brief box */
  .brief {{
    background: var(--sand);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 22px 26px;
    font-size: 0.98em;
  }}
  .brief-row {{ display: grid; grid-template-columns: 140px 1fr; gap: 8px 20px; margin: 4px 0; }}
  .brief-row .label {{ color: var(--muted); font-weight: 600; }}

  /* palette */
  .palette-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-top: 14px;
  }}
  .palette-card {{
    background: #fff;
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
  }}
  .palette-swatch {{ height: 74px; position: relative; }}
  .palette-swatch .hex {{
    position: absolute; bottom: 6px; right: 8px;
    font-family: monospace; font-size: 0.78em; color: rgba(255,255,255,0.9);
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
  }}
  .palette-card .body {{
    padding: 10px 12px;
  }}
  .palette-card .group {{ font-size: 0.72em; letter-spacing: 0.1em; text-transform: uppercase; color: var(--teak); }}
  .palette-card .name {{ font-family: var(--font-display); font-weight: 600; margin-top: 2px; }}
  .palette-card .note {{ font-size: 0.82em; color: var(--muted); margin-top: 4px; line-height: 1.4; }}

  /* images */
  .gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
    margin-top: 14px;
  }}
  .gallery img {{
    width: 100%;
    border-radius: 10px;
    border: 1px solid var(--border);
  }}
  .gallery .caption {{
    font-size: 0.78em;
    color: var(--muted);
    margin-top: 4px;
  }}

  /* analysis body · from markdown_to_html */
  .analysis-body h2, .analysis-body h3, .analysis-body h4 {{ font-family: var(--font-display); color: var(--ink); }}
  .analysis-body h2 {{ font-size: 1.6em; border-bottom: 2px solid var(--teak); padding-bottom: 4px; margin-top: 28px; }}
  .analysis-body h3 {{ font-size: 1.2em; margin-top: 20px; }}
  .analysis-body table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.92em; }}
  .analysis-body th, .analysis-body td {{ border: 1px solid var(--border); padding: 6px 10px; text-align: left; }}
  .analysis-body thead th {{ background: var(--sand); }}
  .analysis-body code {{ background: var(--sand); padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }}
  .analysis-body ul {{ padding-left: 1.4em; }}
  .analysis-body li {{ margin: 4px 0; }}

  /* disclaimer */
  .disclaimer {{
    background: #fff8e6;
    border-left: 4px solid var(--gold);
    border-radius: 6px;
    padding: 16px 20px;
    font-size: 0.88em;
    color: #6b5b1e;
    margin: 20px 0;
  }}

  /* footer */
  .footer {{
    padding: 30px 48px;
    text-align: center;
    color: var(--muted);
    font-size: 0.85em;
    border-top: 1px solid var(--border);
  }}

  /* print */
  @media print {{
    body {{ background: #fff; }}
    .cover {{ page-break-after: always; min-height: 95vh; }}
    .section {{ page-break-inside: avoid; }}
    .no-print {{ display: none; }}
  }}
  .print-btn {{
    position: fixed; top: 16px; right: 16px;
    background: var(--teak); color: #fff; padding: 10px 20px;
    border: none; border-radius: 8px; cursor: pointer;
    font-family: var(--font-display); font-weight: 600;
    box-shadow: 0 2px 10px rgba(0,0,0,0.18);
    z-index: 99;
  }}
</style>
</head>
<body>
  <button class="print-btn no-print" onclick="window.print()">🖨 พิมพ์ / Save PDF</button>

  <!-- COVER -->
  <div class="cover">
    <div class="cover-eyebrow">THAI RESIDENTIAL PORTFOLIO</div>
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    <div class="cover-meta">
      <div><div class="m-label">ที่ดิน</div><div class="m-value">{land_dim}</div></div>
      <div><div class="m-label">เขต</div><div class="m-value">{zone}</div></div>
      <div><div class="m-label">งบ</div><div class="m-value">{budget}</div></div>
      <div><div class="m-label">วันที่</div><div class="m-value">{date}</div></div>
    </div>
  </div>

  <!-- BRIEF -->
  <div class="section">
    <div class="eyebrow">01 · Project Brief</div>
    <h2>ข้อมูลโครงการ</h2>
    <div class="brief">{brief_rows}</div>
  </div>

  <!-- PALETTE -->
  {palette_section}

  <!-- IMAGES -->
  {images_section}

  <!-- ANALYSIS -->
  <div class="section">
    <div class="eyebrow">04 · AI Analysis</div>
    <h2>ผลวิเคราะห์ 5 ชั้นความรู้</h2>
    <div class="analysis-body">{analysis_html}</div>
  </div>

  <!-- DISCLAIMER -->
  <div class="section">
    <div class="disclaimer">
      <strong>⚠ Disclaimer</strong><br>
      ผลเป็นการวิเคราะห์เบื้องต้นโดย AI · <b>ไม่แทนที่</b>สถาปนิก/วิศวกรใบอนุญาต ·
      การขออนุญาตก่อสร้างต้องมีลายเซ็นผู้ประกอบวิชาชีพ (พรบ.ควบคุมอาคาร 2522 ม. 49 ทวิ)
    </div>
  </div>

  <div class="footer">
    Generated by สมองจำลองของสถาปนิก · Thai Architect's Studio · {date}
  </div>
</body>
</html>
"""


def build_portfolio_html(
    project_data: dict,
    analysis_md: str,
    provider: str,
    palette: dict | None = None,
    images: list[dict] | None = None,
) -> str:
    """Build the full portfolio HTML · editorial Thai style

    palette: {group_key: {name, hex, note, group_label}}
    images: [{"bytes": b"...", "view_type": "...", "model": "..."}]
    """
    pd = project_data
    title = _escape_html(pd.get("name", "Untitled"))
    subtitle_parts = []
    subtitle_parts.append(f"{pd.get('floors', '-')} ชั้น · {pd.get('bedrooms', '-')} ห้องนอน · ครอบครัว {pd.get('family_size', '-')} คน")
    if pd.get("special"):
        subtitle_parts.append(str(pd["special"])[:100])
    subtitle = _escape_html(" · ".join(subtitle_parts))

    land_dim = f"{pd.get('land_w', '-')}×{pd.get('land_d', '-')} ม. · {pd.get('land_area', 0):.0f} ตร.ม."
    zone = _escape_html(pd.get("zone", "-"))
    budget = f"{pd.get('budget', '-')} ลบ."
    date = datetime.now().strftime("%Y-%m-%d")

    # Brief rows
    brief_items = [
        ("จังหวัด", pd.get("province", "-")),
        ("สีผังเมือง", pd.get("zone", "-")),
        ("ถนนติด", f"{pd.get('street_w', '-')} ม."),
        ("ครอบครัว", f"{pd.get('family_size', '-')} คน"),
        ("ผู้สูงอายุ", pd.get("has_elderly", "-")),
        ("ชั้น", pd.get("floors", "-")),
        ("ห้องนอน", pd.get("bedrooms", "-")),
        ("งบประมาณ", f"{pd.get('budget', '-')} ล้านบาท"),
        ("ฮวงจุ้ย", pd.get("fengshui", "-")),
        ("ข้อกำหนดพิเศษ", pd.get("special", "-")),
    ]
    brief_rows = "".join(
        f'<div class="brief-row"><div class="label">{_escape_html(k)}</div><div>{_escape_html(str(v))}</div></div>'
        for k, v in brief_items
    )

    # Palette section
    if palette:
        cards = []
        for group_key, data in palette.items():
            cards.append(
                f'<div class="palette-card">'
                f'<div class="palette-swatch" style="background: {data["hex"]};"><span class="hex">{data["hex"]}</span></div>'
                f'<div class="body">'
                f'<div class="group">{_escape_html(data.get("group_label", group_key))}</div>'
                f'<div class="name">{_escape_html(data["name"])}</div>'
                f'<div class="note">{_escape_html(data.get("note", ""))}</div>'
                f'</div></div>'
            )
        palette_section = (
            '<div class="section">'
            '<div class="eyebrow">02 · Materials Palette</div>'
            '<h2>วัสดุไทย · Tropical palette</h2>'
            '<div class="palette-grid">'
            + "".join(cards)
            + '</div></div>'
        )
    else:
        palette_section = ""

    # Images gallery
    if images:
        img_cards = []
        for img in images[:6]:
            img_b64 = base64.b64encode(img["bytes"]).decode("ascii")
            caption = f"{img.get('view_type', 'mockup')} · {img.get('model', 'ai')}"
            img_cards.append(
                f'<div><img src="data:image/png;base64,{img_b64}" alt="mockup"/>'
                f'<div class="caption">{_escape_html(caption)}</div></div>'
            )
        images_section = (
            '<div class="section">'
            '<div class="eyebrow">03 · Visual Mockups</div>'
            '<h2>ภาพ render</h2>'
            '<div class="gallery">'
            + "".join(img_cards)
            + '</div></div>'
        )
    else:
        images_section = ""

    analysis_html = markdown_to_html(analysis_md)

    return PORTFOLIO_TEMPLATE.format(
        title=title,
        subtitle=subtitle,
        land_dim=land_dim,
        zone=zone,
        budget=budget,
        date=date,
        brief_rows=brief_rows,
        palette_section=palette_section,
        images_section=images_section,
        analysis_html=analysis_html,
    )


def try_build_pdf_bytes(project_data: dict, analysis_md: str, provider: str) -> tuple[bytes | None, str | None]:
    """Returns (bytes, None) if success · (None, reason) if skipped/failed"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    except ImportError:
        return None, "reportlab ไม่ติดตั้ง · ใช้ .html export แทน"

    font_dir = Path(__file__).parent.parent / "fonts"
    font_path = font_dir / "Sarabun-Regular.ttf"
    if not font_path.exists():
        return None, (
            f"ไม่พบฟอนต์ไทย · วางไฟล์ `Sarabun-Regular.ttf` ที่ `fonts/` "
            "(ดาวน์โหลดฟรีจาก Google Fonts) · ระหว่างนี้ใช้ .html export แทน"
        )

    try:
        pdfmetrics.registerFont(TTFont("Sarabun", str(font_path)))
        bold_path = font_dir / "Sarabun-Bold.ttf"
        if bold_path.exists():
            pdfmetrics.registerFont(TTFont("Sarabun-Bold", str(bold_path)))

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=18 * mm, rightMargin=18 * mm,
            topMargin=18 * mm, bottomMargin=18 * mm,
        )
        styles = getSampleStyleSheet()
        body = ParagraphStyle("body", parent=styles["Normal"], fontName="Sarabun", fontSize=11, leading=16)
        h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName="Sarabun", fontSize=18, leading=22, textColor="#764ba2")
        h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Sarabun", fontSize=14, leading=18, textColor="#667eea")
        pre_style = ParagraphStyle("pre", parent=body, fontName="Sarabun", fontSize=9, leading=12)

        story: list = []
        story.append(Paragraph(f"🏠 ผลวิเคราะห์ — {project_data.get('name', '')}", h1))
        story.append(Paragraph(
            f"วันที่: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Provider: {provider.title()}",
            body,
        ))
        story.append(Spacer(1, 8))
        story.append(Paragraph("ข้อมูลโครงการ", h2))
        story.append(Preformatted(
            json.dumps(project_data, ensure_ascii=False, indent=2),
            pre_style,
        ))
        story.append(Spacer(1, 8))
        story.append(Paragraph("ผลวิเคราะห์", h2))

        # Convert markdown paragraphs to reportlab Paragraphs (very simple)
        for para in analysis_md.split("\n\n"):
            text = para.strip()
            if not text:
                continue
            # Strip markdown markup that reportlab doesn't understand natively
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            text = text.replace("\n", "<br/>")
            story.append(Paragraph(text, body))
            story.append(Spacer(1, 4))

        doc.build(story)
        return buf.getvalue(), None
    except Exception as e:
        return None, f"สร้าง PDF ล้มเหลว: {e}"
