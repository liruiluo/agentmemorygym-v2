#!/usr/bin/env python3
"""Point the page, the deck and the citation at the published arXiv identifier.

Usage: python3 scripts/set_arxiv_id.py 2612.01234
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ABSTRACT_URL = "https://arxiv.org/abs/{id}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("arxiv_id", help="the identifier as it appears in the URL, e.g. 2612.01234")
    args = ap.parse_args()
    aid = args.arxiv_id.strip()
    url = ABSTRACT_URL.format(id=aid)

    page = ROOT / "index.html"
    html = page.read_text()
    html = re.sub(r'<a class="topbar-cta" href="[^"]*">\s*<span>[^<]*</span>',
                  f'<a class="topbar-cta" href="{url}" target="_blank" rel="noreferrer">\n          <span>arXiv:{aid}</span>',
                  html, count=1)
    page.write_text(html)

    deck = ROOT / "scripts" / "build_slides.py"
    src = deck.read_text()
    src = re.sub(r'PAPER = "https://arxiv.org/abs/[^"]*"', f'PAPER = "{url}"', src)
    deck.write_text(src)

    readme = ROOT / "README.md"
    text = readme.read_text()
    if "arXiv:" not in text:
        text += f"\nPaper: <{url}>\n"
    readme.write_text(text)
    print(f"pointed the page and the deck at {url}")
    print("now rebuild the deck and push:")
    print("  python3 scripts/build_slides.py --out assets/slides/campii-slides.pptx")
    print("  python3 scripts/render_slides_pdf.py assets/slides/campii-slides.pptx assets/slides/campii-slides.pdf")
    print("  git commit -am 'Point the page at the arXiv identifier' && git push")


if __name__ == "__main__":
    main()
