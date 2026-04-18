# Fonts

Optional. For **native PDF export** (Sarabun Thai font).

## To enable PDF export

1. Download Sarabun TTF from Google Fonts: https://fonts.google.com/specimen/Sarabun
2. Extract the zip
3. Copy these files into this folder:
   - `Sarabun-Regular.ttf` (required)
   - `Sarabun-Bold.ttf` (optional, improves bold rendering)
4. Commit + push → Streamlit Cloud redeploys → PDF export button enables

## Without these files

The **HTML export** (🖨 HTML) still works perfectly — just uses Google Fonts via `<link>`
and lets the browser handle the font. Users print from browser (Ctrl+P → Save as PDF).

The PDF button will stay disabled with a helpful message.

## License

Sarabun is licensed under SIL Open Font License — free for commercial use, can be bundled.
