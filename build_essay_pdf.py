"""Build the essay PDF: markdown -> styled HTML -> headless Chrome print.

Same pipeline as paper/build_pdf.py (needs the `markdown` package, e.g. the
~/emergence-lab/.venv interpreter, and Google Chrome). Writes
emergent-resolution-the-gradient.pdf next to the source; the intermediate
_essay_build.html is removed on success.

    ~/emergence-lab/.venv/bin/python build_essay_pdf.py
"""

import subprocess
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC = HERE / "emergent-resolution-the-gradient.md"
PDF = HERE / "emergent-resolution-the-gradient.pdf"

CSS = """
@page { size: letter; margin: 22mm 20mm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt;
       line-height: 1.45; color: #111; max-width: 100%; margin: 0; }
h1 { font-size: 19pt; line-height: 1.25; margin: 0 0 6pt; }
h2 { font-size: 13pt; font-weight: normal; font-style: italic;
     margin: 0 0 14pt; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 16pt 0 6pt; page-break-after: avoid; }
p { margin: 0 0 8pt; text-align: justify; hyphens: auto; }
li { margin-bottom: 4pt; }
code { font-family: Menlo, monospace; font-size: 9pt; }
img { max-width: 100%; height: auto; display: block; margin: 12pt auto 4pt; page-break-inside: avoid; }
hr { border: 0; border-top: 0.5pt solid #aaa; margin: 16pt 0; }
"""

body = markdown.markdown(SRC.read_text(), extensions=["smarty"])
html = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<title>The 4-Bit Image in a 32-Bit World</title>"
        f"<style>{CSS}</style></head><body>{body}</body></html>")
build = HERE / "_essay_build.html"
build.write_text(html)
subprocess.run([CHROME, "--headless", "--disable-gpu",
                "--no-pdf-header-footer", f"--print-to-pdf={PDF}",
                f"file://{build}"], check=True, capture_output=True)
build.unlink()
print(f"wrote {PDF} ({PDF.stat().st_size:,} bytes)")
