# CAMP-II project website

Static project page for **Coding Agent Memory Post-Training II: Unlocking the Memory Potential of
Pre-trained File Operations for Long-Horizon Tasks via On-Policy Distillation**.

Run locally:

```bash
cd agentmemorygym-website-v2
python3 -m http.server 4180 --bind 127.0.0.1
```

Open <http://127.0.0.1:4180>.

## Contents

- `index.html`, `styles.css`, `script.js` — the page. The environment strip carries five tabs,
  one per CAMG-II environment.
- `assets/` — figure exports from the paper, the paper PDF, and the slides (PDF and editable PPTX).
- `scripts/set_arxiv_id.py` — points the page, the deck and the citation at the arXiv identifier once
  it exists.
- `slides/outline.md` — the talk outline, one row per slide with its source.
- `scripts/build_slides.py` — builds the editable deck with `python-pptx`.
- `scripts/render_slides_pdf.py` — renders the deck to PDF with macOS Keynote or LibreOffice.

## Numbers on the page

All of them come from the paper. Task success on the CAMG-II held-out panels for CAMP-II is
100.0 / 37.5 / 64.1 / 81.2 / 40.2, an average of 64.6, against 54.2 for CAMP-I. Visual is the mean
judge score over the whole panel, with an episode that ends without a submission counting as zero.
External transfer reads 30.0 and 18.1 for CAMP-II-4B and 38.0 and 30.1 for CAMP-II-9B.

The code is not linked and not published from here.
