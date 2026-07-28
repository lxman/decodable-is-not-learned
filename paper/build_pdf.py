"""Build the paper PDF: markdown -> styled HTML -> headless Chrome print.

Needs the `markdown` package (any location, e.g.
`pip install --target <dir> markdown` + PYTHONPATH=<dir>) and Google
Chrome. Writes decodable-is-not-learned.pdf next to the source; the
intermediate _build.html is removed on success.

    python paper/build_pdf.py
"""

import subprocess
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: letter; margin: 22mm 20mm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt;
       line-height: 1.45; color: #111; max-width: 100%; margin: 0; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 6pt; }
h2 { font-size: 13pt; margin: 18pt 0 6pt; page-break-after: avoid; }
h3 { font-size: 11pt; margin: 14pt 0 5pt; page-break-after: avoid; }
p { margin: 0 0 7pt; text-align: justify; hyphens: auto; }
li { margin-bottom: 3pt; }
code { font-family: Menlo, monospace; font-size: 9pt; }
img { max-width: 100%; page-break-inside: avoid; margin: 6pt 0 2pt; }
table { border-collapse: collapse; font-size: 7.3pt; width: 100%;
        margin: 6pt 0 10pt; page-break-inside: auto;
        font-family: Helvetica, Arial, sans-serif; }
th, td { border: 0.5pt solid #aaa; padding: 2.5pt 4pt; text-align: left;
         vertical-align: top; }
th { background: #f2f1ee; font-weight: 600; }
tr { page-break-inside: avoid; }
"""

md = (HERE / "decodable-is-not-learned.md").read_text()
body = markdown.markdown(md, extensions=["tables", "smarty"])
html = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>Decodable Is Not Learned</title>"
        f"<style>{CSS}</style></head><body>{body}</body></html>")
build = HERE / "_build.html"
build.write_text(html)

pdf = HERE / "decodable-is-not-learned.pdf"
subprocess.run([CHROME, "--headless", "--disable-gpu",
                "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                f"file://{build}"], check=True, capture_output=True)
build.unlink()
print(f"wrote {pdf} ({pdf.stat().st_size:,} bytes)")
