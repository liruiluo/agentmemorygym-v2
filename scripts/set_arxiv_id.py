#!/usr/bin/env python3
"""Set an author-confirmed arXiv ID, then regenerate the site and editable deck.

No commit, push or public deployment is performed. The PDF is rebuilt separately
because its renderer needs the documented local fonts.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('arxiv_id', help='author-confirmed identifier, e.g. 2612.01234')
    ap.add_argument('--root', type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = ap.parse_args()
    aid = args.arxiv_id.strip()
    if not re.fullmatch(r'\d{2}(?:0[1-9]|1[0-2])\.\d{4,5}(?:v[1-9]\d*)?', aid):
        ap.error('expected a numeric arXiv identifier, not a URL or placeholder')
    root = args.root.resolve()
    path = root / 'data/research.json'
    data = json.loads(path.read_text())
    data['arxiv_id'] = aid
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)
    subprocess.run([sys.executable, str(root/'scripts/build_website.py')], check=True)
    subprocess.run([sys.executable, str(root/'scripts/build_slides.py')], check=True)
    print('Updated the site, citation and PPTX hyperlinks. No publication performed.')
    print('Next: rebuild the PDF and validate before committing:')
    print('  python3 scripts/render_slides_pdf.py assets/slides/campii-slides.pptx assets/slides/campii-slides.pdf')
    print('  python3 scripts/validate_artifacts.py')

if __name__ == '__main__':
    main()
