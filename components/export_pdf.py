"""PDF / HTML export · print-ready reports with Thai font support

Two paths:
1. HTML export (PRIMARY, works everywhere):
   - Self-contained .html with Sarabun via Google Fonts <link>
   - User opens in browser → Ctrl+P → Save as PDF
   - Zero dependencies beyond stdlib

2. Native PDF via reportlab (BONUS, if Sarabun TTF shipped):
   - fonts/Sarabun-Regular.ttf (optional)
   - Falls back gracefully to HTML-only if reportlab or font missing
"""

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
