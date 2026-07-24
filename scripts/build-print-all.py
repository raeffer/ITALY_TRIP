#!/usr/bin/env python3
"""
Regenerates print-all.html by stitching together days/day1.html ... day10.html
and credits.html into one continuous, print-ready document.

Run manually:
    python3 scripts/build-print-all.py

Requires: beautifulsoup4, lxml (pip install beautifulsoup4 lxml --break-system-packages)

This is also run automatically:
  - locally, by the pre-commit hook (scripts/pre-commit-hook.sh), whenever a
    day page, credits.html, or style.css is staged for commit
  - in CI, by .github/workflows/build-print-all.yml, on every push to main
    that touches those same files (as a safety net for anyone who committed
    with --no-verify or without the hook installed)
"""

import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency. Run: pip install beautifulsoup4 lxml --break-system-packages")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
DAY_FILES = [f"days/day{i}.html" for i in range(1, 11)]
ALL_FILES = DAY_FILES + ["credits.html"]
OUTPUT_FILE = REPO_ROOT / "print-all.html"


def extract_page(fpath: Path) -> str:
    with open(fpath, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")
    page_div = soup.find("div", class_="page")
    if page_div is None:
        raise ValueError(f"No <div class='page'> found in {fpath}")
    html_str = str(page_div)
    # day pages under days/ reference ../style.css and ../credits.html etc.
    # since print-all.html lives at repo root, flatten those references.
    html_str = html_str.replace('../style.css', 'style.css')
    html_str = html_str.replace('href="../', 'href="')
    html_str = html_str.replace('src="../', 'src="')
    return html_str


def build() -> str:
    blocks = []
    for idx, rel_path in enumerate(ALL_FILES):
        fpath = REPO_ROOT / rel_path
        html_str = extract_page(fpath)
        break_style = "" if idx == 0 else ' style="page-break-before: always;"'
        blocks.append(f'<div class="print-day"{break_style}>\n{html_str}\n</div>')

    combined_body = "\n\n".join(blocks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Italy Road Trip Companion — Full Printable Edition</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<style>
  /* This banner is screen-only; it hides itself when actually printing. */
  .print-banner {{
    background: #12293e;
    color: #fdf6e9;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    text-align: center;
    padding: 14px 20px;
  }}
  .print-banner a {{ color: #ffd23f; }}
  @media print {{
    .print-banner {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="print-banner">
  This is the full printable edition — all 10 days + photo credits, one continuous document.
  Press Ctrl+P (or Cmd+P) and choose "Save as PDF" with A4 paper size to export.
  <br>Individual day pages: <a href="index.html">back to site</a>
</div>

{combined_body}

</body>
</html>
"""


def main():
    content = build()
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE} ({len(content):,} chars)")


if __name__ == "__main__":
    main()
