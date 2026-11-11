# CAMP-II website and research talk

**Coding Agent Memory Post-Training II** — a static research website and a
15-slide editable talk, organized around the same story:

> A task outlives its context → both sides need a usable memory interface →
> student file actions receive frozen-teacher feedback → comparisons and
> memory-specific ablations → recovery example and external transfer.

## Preview

Open `index.html` directly. No server, external font, library CDN or API is
required. Alternatively, use a **loopback-only** preview:

```bash
python3 -m http.server 4180 --bind 127.0.0.1
```

Open <http://127.0.0.1:4180>. The write/reset/resume illustration supports arrow
keys and Home/End. With JavaScript disabled, all three stages remain readable.
Chart values also appear as text; the two full results tables are expandable.

- Website: `index.html`
- Slides: `assets/slides/campii-slides.pdf`
- Editable source: `assets/slides/campii-slides.pptx`
- Story and per-slide sources: `slides/outline.md`
- Chinese speaker notes: embedded in every PPTX slide, and in `slides/speaker-notes.md`

## Regenerate and check

Python dependencies: `python-pptx`, `Pillow`, `reportlab`, `PyMuPDF`.
Browser QA additionally uses `playwright` and installed Chrome. `pdffonts`
(Poppler) is used to check embedded fonts.

```bash
python3 scripts/build_website.py
python3 scripts/build_slides.py
python3 scripts/render_slides_pdf.py assets/slides/campii-slides.pptx assets/slides/campii-slides.pdf
python3 scripts/validate_artifacts.py
python3 scripts/test_build.py
python3 scripts/check_browser.py --out /tmp/campii-browser-check
```

The PPTX contains native text, diagrams and charts; only the original paper's
Visual case is an embedded image. The PDF is a **headless ReportLab rendition of
those native PPTX elements**, not a PowerPoint/Keynote export. Its renderer
currently expects macOS Arial and Menlo font files. It checks text overflow and
embeds TrueType fonts. A native PowerPoint application reflow has not been tested.

Edit these sources rather than generated outputs:

| Surface | Source |
|---|---|
| Numbers, authors, paper identity | `data/research.json` |
| Website content and structure | `scripts/site.template.html` |
| Website appearance and interaction | `styles.css`, `script.js` |
| Native deck and speaker notes | `scripts/build_slides.py` |
| PDF rendering | `scripts/render_slides_pdf.py` |

`build_website.py` regenerates `index.html`. `build_slides.py` regenerates the
PPTX and the readable speaker-notes file. Both use the same research snapshot.

## Evidence boundaries

Results are transcribed from the **current paper**, not refreshed from experimental
receipts. Table 1, Table 2, Figures 3/5/6 and Appendices C.3/D.3 are the source
locations. The original main-paper PDF and figure files are retained unchanged.

- The five-domain average combines four task success rates and the Visual
  panel-mean judge score. Unsubmitted Visual episodes count as zero.
- CAMP-II 64.6 vs initial 4B 45.3 is **+19.3**; vs MemOPD with SFT 51.8 is
  **+12.8**. The 2.97× value compares gains, not final scores.
- CAMP-I remains ahead in Visual (46.5 vs 40.2).
- Teacher preference is same-task versus foreign-task note discrimination;
  the Visual trace is an observed example. Neither is a causal outcome test.
- Standard deviation across five training runs is not a confidence interval.
  Validate it from the per-run five-domain means before rounding the mean cells;
  the already-rounded average column loses enough precision to change the SD.
- External Table 2 retains the published 35B-A3B row 33.8 / 27.4 / 30.6.
  A MoE parameter count is not an inference-cost measurement.

The complete title and all 12 authors are retained in the website citation.
The code is neither linked nor published from this repository.

## Paper identifier and deployment

Until an author-confirmed identifier is available, paper links point to the
included PDF. Once it exists:

```bash
python3 scripts/set_arxiv_id.py 2612.01234   # example only; replace it
```

This updates the shared data, site, citation and PPTX link. Rebuild the PDF and
run the checks afterward. The helper never pushes or deploys.

GitHub Pages publishes **`main`** at
<https://liruiluo.github.io/agentmemorygym-v2/>. Website and slides updates are
complete only after the verified revision reaches `main`, the Pages build
succeeds for that commit, and the live page and PDF/PPTX downloads are checked.
Use a review-only branch only when preview-only delivery is explicitly requested.
Keep the previous commit and deployment verification as rollback evidence.
