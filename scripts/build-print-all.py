#!/usr/bin/env python3
"""
Regenerates print-all.html by stitching together days/day1.html ... dayN.html
(N = highest day file that currently exists) into one continuous, print-ready
document. See ALL_FILES below for the exact range currently included.

Run manually (regenerates the full 21-day print-all.html, default behavior —
used by CI and the pre-commit hook, do not change what a no-args run does):
    python3 scripts/build-print-all.py

Run for a custom day range/output (e.g. a single-stage printable edition;
this does NOT touch print-all.html and is never invoked by CI/the hook):
    python3 scripts/build-print-all.py --start 14 --end 21 \\
        --output print-stage3.html --title "Stage 3 Printable Edition"

Requires: beautifulsoup4, lxml (pip install beautifulsoup4 lxml --break-system-packages)

This is also run automatically (always with no args, full 21-day range):
  - locally, by the pre-commit hook (scripts/pre-commit-hook.sh), whenever a
    day page, credits.html, or style-editorial.css is staged for commit
  - in CI, by .github/workflows/build-print-all.yml, on every push to main
    that touches those same files (as a safety net for anyone who committed
    with --no-verify or without the hook installed)
"""

import argparse
import sys
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency. Run: pip install beautifulsoup4 lxml --break-system-packages")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_TRIP_START = 1
FULL_TRIP_END = 21  # Stage 1 (1-3) + Stage 2 (4-13) + Stage 3 (14-21) — full 21-day trip complete
OUTPUT_FILE = REPO_ROOT / "print-all.html"


def extract_page(fpath: Path) -> str:
    with open(fpath, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")
    page_div = soup.find("div", class_="page")
    if page_div is None:
        raise ValueError(f"No <div class='page'> found in {fpath}")
    for credit in page_div.select(".inline-photo-credit, .site-footer"):
        credit.decompose()
    html_str = str(page_div)
    # day pages under days/ reference ../style-editorial.css and ../credits.html etc.
    # since print-all.html lives at repo root, flatten those references.
    html_str = html_str.replace('../style-editorial.css', 'style-editorial.css')
    html_str = html_str.replace('href="../', 'href="')
    html_str = html_str.replace('src="../', 'src="')
    html_str = re.sub(r'href="(day[0-9]+\.html)', r'href="days/\1', html_str)
    return html_str


def build(day_files: list[str], title: str, banner_note: str) -> str:
    blocks = []
    for idx, rel_path in enumerate(day_files):
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
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style-editorial.css">
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
  {banner_note}
  Press Ctrl+P (or Cmd+P) and choose "Save as PDF" with A4 paper size to export.
  <br>Individual day pages: <a href="index.html">back to site</a>
</div>

{combined_body}

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", type=int, default=FULL_TRIP_START, help="First day number to include (default: 1)")
    parser.add_argument("--end", type=int, default=FULL_TRIP_END, help="Last day number to include (default: 21)")
    parser.add_argument("--output", type=str, default=None, help="Output filename, relative to repo root (default: print-all.html)")
    parser.add_argument("--title", type=str, default=None, help="Custom <title> and banner label (default: full-trip wording)")
    args = parser.parse_args()

    is_default_range = args.start == FULL_TRIP_START and args.end == FULL_TRIP_END
    day_files = [f"days/day{i}.html" for i in range(args.start, args.end + 1)]
    output_path = REPO_ROOT / (args.output if args.output else "print-all.html")

    if args.title:
        title = args.title
        banner_note = f"This is the {args.title.lower()} — {len(day_files)} days, one continuous document."
    elif is_default_range:
        title = "Italy Road Trip Companion — Full Printable Edition"
        banner_note = f"This is the full printable edition — {len(day_files)} days, one continuous document."
    else:
        title = f"Italy Road Trip Companion — Days {args.start}-{args.end} Printable Edition"
        banner_note = f"This is a partial printable edition (Days {args.start}-{args.end}) — {len(day_files)} days, one continuous document."

    content = build(day_files, title, banner_note)
    output_path.write_text(content, encoding="utf-8")
    print(f"Wrote {output_path} ({len(content):,} chars)")


if __name__ == "__main__":
    main()
