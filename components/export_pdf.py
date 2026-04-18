"""PDF export · generates print-ready HTML (Thai-safe) + optional reportlab PDF"""

import json
import re
from datetime import datetime


def _markdown_to_html(md: str) -> str:
    """Lightweight MD → HTML (enough for analysis output)"""
    lines = md.split("\n")
    out = []
    in_list = False
    in_code = False
    for raw in lines:
        line = raw.rstrip()

        # Code fences
        if line.startswith("```"):
            if in_code:
                out.append("</pre>")
                in_code = False
            else:
                out.append('<pre class="code">')
                in_code = True
            continue
        if in_code:
            out.append(_html_escape(line))
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(m.group(1))
            text = _inline(m.group(2))
            out.append(f"<h{level}>{text}</h{level}>")
            continue

        # List items
        if re.match(r"^\s*[-*•]\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = re.sub(r"^\s*[-*•]\s+", "", line)
            out.append(f"<li>{_inline(item)}</li>")
            continue

        if in_list and line.strip() == "":
            out.append("</ul>")
            in_list = False
            continue

        if line.strip() == "":
            out.append("<br/>")
            continue

        out.append(f"<p>{_inline(line)}</p>")

    if in_list:
        out.append("</ul>")
    if in_code:
        out.append("</pre>")
    return "\n".join(out)


def _inline(text: str) -> str:
    text = _html_escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_print_html(project_data: dict, analysis: str, provider: str) -> str:
    """Build a self-contained, print-friendly HTML document (Thai font via Google Fonts)"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    analysis_html = _markdown_to_html(analysis)
    project_json = json.dumps(project_data, ensure_ascii=False, indent=2)

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>ผลวิเคราะห์ — {_html_escape(project_data.get('name',''))}</title>
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
  .header h1 {{ margin: 0 0 8px 0; font-weight: 700; }}
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
    font-family: 'Consolas', monospace;
  }}
  h1, h2, h3, h4 {{ color: #222; margin-top: 1.2em; }}
  h2 {{ border-bottom: 2px solid #667eea; padding-bottom: 4px; }}
  ul {{ padding-left: 1.4em; }}
  li {{ margin: 4px 0; }}
  code {{ background: #f3f4f6; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }}
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
    .no-print {{ display: none; }}
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
    <h1>🏠 ผลวิเคราะห์ — {_html_escape(project_data.get('name',''))}</h1>
    <div class="meta">
      <div>วันที่: {ts}</div>
      <div>Provider: {provider.title()}</div>
      <div>Knowledge Graph: 63 nodes, 248 edges</div>
    </div>
  </div>

  <h2>📋 ข้อมูลโครงการ</h2>
  <div class="data-box">
    <pre class="code">{_html_escape(project_json)}</pre>
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


def try_build_pdf_bytes(project_data: dict, analysis: str, provider: str):
    """
    Attempt to build PDF bytes using reportlab + bundled Sarabun TTF if available.
    Returns (pdf_bytes, error_msg). If font not found or lib missing, returns (None, reason).
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    except ImportError:
        return None, "reportlab ไม่ติดตั้ง · ใช้ HTML export แทน"

    from pathlib import Path
    font_dir = Path(__file__).parent.parent / "fonts"
    font_path = font_dir / "Sarabun-Regular.ttf"
    if not font_path.exists():
        return None, f"ไม่พบฟอนต์ไทย · วางไฟล์ Sarabun-Regular.ttf ที่ {font_dir}/ เพื่อใช้ PDF export โดยตรง"

    import io
    try:
        pdfmetrics.registerFont(TTFont("Sarabun", str(font_path)))
        bold_path = font_dir / "Sarabun-Bold.ttf"
        if bold_path.exists():
            pdfmetrics.registerFont(TTFont("Sarabun-Bold", str(bold_path)))
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
        styles = getSampleStyleSheet()
        body = ParagraphStyle("body", parent=styles["Normal"], fontName="Sarabun", fontSize=11, leading=16)
        h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName="Sarabun", fontSize=18, leading=22, textColor="#764ba2")
        h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Sarabun", fontSize=14, leading=18, textColor="#667eea")

        story = []
        story.append(Paragraph(f"🏠 ผลวิเคราะห์ — {project_data.get('name','')}", h1))
        story.append(Paragraph(f"วันที่: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Provider: {provider.title()}", body))
        story.append(Spacer(1, 8))
        story.append(Paragraph("ข้อมูลโครงการ", h2))
        story.append(Preformatted(json.dumps(project_data, ensure_ascii=False, indent=2), ParagraphStyle("pre", parent=body, fontSize=9, leading=12)))
        story.append(Spacer(1, 8))
        story.append(Paragraph("ผลวิเคราะห์", h2))
        for para in analysis.split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.replace("\n", "<br/>").replace("**", ""), body))
                story.append(Spacer(1, 4))
        doc.build(story)
        return buf.getvalue(), None
    except Exception as e:
        return None, f"สร้าง PDF ล้มเหลว: {e}"
