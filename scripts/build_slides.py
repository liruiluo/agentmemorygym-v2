#!/usr/bin/env python3
"""Build the public paper talk using the author's CRG/SPHERE academic layout.

Native text, diagrams, and tables stay editable. Plots use public arXiv v1 values;
generated assets and draft decks belong outside the website repository.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

SW, SH = 10.0, 5.625
FONT, CODE = "Arial", "Menlo"
INK, MID, LIGHT, LINE = "111111", "555555", "888888", "CCD2D8"
BLUE, PALE, RED, GREEN, WHITE = "285F91", "EAF1F8", "C8192E", "19806A", "FFFFFF"
PROJECT = "https://liruiluo.github.io/agentmemorygym-v2/"
PAPER = "https://arxiv.org/abs/2609.34422"


def rgb(value):
    return RGBColor.from_string(value)


def text(slide, content, x, y, w, h, size=18, color=INK, bold=False,
         align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, font=FONT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = valign
    for i, row in enumerate(str(content).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = row or " "
        p.alignment = align
        p.line_spacing = 1.08
        p.space_after = Pt(0)
        for r in p.runs:
            r.font.name = font
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = rgb(color)
    return box


def rich(slide, spans, x, y, w, h, size=17, align=PP_ALIGN.LEFT):
    box = text(slide, "", x, y, w, h, size, align=align)
    p = box.text_frame.paragraphs[0]
    p.clear()
    for spec in spans:
        if isinstance(spec, str):
            spec = (spec, INK, False)
        r = p.add_run()
        r.text = spec[0]
        r.font.name = FONT
        r.font.size = Pt(size)
        r.font.color.rgb = rgb(spec[1] if len(spec) > 1 else INK)
        r.font.bold = spec[2] if len(spec) > 2 else False
    return box


def rect(slide, x, y, w, h, fill=WHITE, stroke=INK, width=1.1, oval=False):
    kind = MSO_SHAPE.OVAL if oval else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    s.line.color.rgb = rgb(stroke)
    s.line.width = Pt(width)
    return s


def line(slide, x1, y1, x2, y2, color=LINE, width=1.1, arrow=False, dash=False):
    s = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                  Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    s.line.color.rgb = rgb(color)
    s.line.width = Pt(width)
    if dash:
        s.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if arrow:
        tail = OxmlElement("a:tailEnd")
        tail.set("type", "triangle")
        tail.set("w", "med")
        tail.set("len", "med")
        s.line._get_or_add_ln().append(tail)
    return s


def image(slide, path, x, y, w, h):
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    ww, hh = iw * scale, ih * scale
    return slide.shapes.add_picture(str(path), Inches(x+(w-ww)/2),
                                   Inches(y+(h-hh)/2), Inches(ww), Inches(hh))


def title(slide, heading):
    size = 21.5 if len(heading) < 50 else 20.2
    text(slide, heading, .13, .06, 8.94, .52, size=size,
         valign=MSO_ANCHOR.MIDDLE)
    text(slide, "JD.com", 9.16, .19, .68, .24, size=12, bold=True,
         color=RED, align=PP_ALIGN.RIGHT)


def conclusion(slide, spans, y=4.91, size=17):
    return rich(slide, spans, .42, y, 9.16, .55, size, PP_ALIGN.CENTER)


def source(slide, copy):
    text(slide, copy, .46, 5.42, 9.1, .15, size=8, color=LIGHT,
         align=PP_ALIGN.CENTER)


def metric(slide, value, label, y, color=RED, x=7.18, w=2.42):
    text(slide, value, x, y, w, .49, size=29, color=color, bold=True,
         align=PP_ALIGN.CENTER)
    text(slide, label, x, y+.55, w, .48, size=12.5, color=MID,
         align=PP_ALIGN.CENTER)


def node(slide, label, x, y, w, h=.67, color=BLUE, fill=WHITE, size=17):
    rect(slide, x, y, w, h, fill, color)
    text(slide, label, x+.06, y+.04, w-.12, h-.08, size=size, bold=True,
         color=color, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def terminal(slide, label, rows, x, y, w, h, size=14, accent=BLUE):
    rect(slide, x, y, w, h, WHITE, accent)
    rect(slide, x, y, w, .36, PALE, accent, .6)
    text(slide, label, x+.13, y+.065, w-.26, .23, size=12.5, color=accent, bold=True)
    text(slide, rows, x+.17, y+.57, w-.34, h-.69, size=size, font=CODE)


def links(slide, y, size=11):
    box = rich(slide, [("Project: ", INK, True),
                       ("liruiluo.github.io/agentmemorygym-v2", BLUE)],
               .55, y, 5.0, .25, size)
    box.text_frame.paragraphs[0].runs[1].hyperlink.address = PROJECT
    box = rich(slide, [("Paper: ", INK, True), ("PDF", BLUE)],
               6.15, y, 3.25, .25, size)
    box.text_frame.paragraphs[0].runs[1].hyperlink.address = PROJECT + "assets/paper.pdf"


def charts(out):
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "Arial", "font.size": 13,
                         "axes.labelsize": 14, "xtick.labelsize": 12,
                         "ytick.labelsize": 12, "text.color": "#111111",
                         "axes.labelcolor": "#555555", "axes.edgecolor": "#A8AFB6",
                         "xtick.color": "#555555", "ytick.color": "#555555"})
    blue, grey, pale, red = "#"+BLUE, "#BAC2CB", "#8FB4E3", "#"+RED

    def base(width=6.6, height=3.95):
        f, a = plt.subplots(figsize=(width, height), dpi=220)
        a.spines[["top", "right"]].set_visible(False)
        a.set_axisbelow(True)
        a.tick_params(length=0, pad=7)
        return f, a

    def save(fig, name):
        fig.savefig(out/name, facecolor="white")
        plt.close(fig)

    # Average success across the five domains, other memory interfaces as context.
    f, a = base()
    names = ["Frozen 4B", "MemOPD (SFT)", "CompactOPD", "CAMP-I", "CAMP-II"]
    vals = [45.3, 51.8, 48.2, 54.2, 64.6]
    bars = a.barh(np.arange(5), vals, color=[grey, grey, grey, grey, blue], height=.62)
    a.set_yticks(np.arange(5), names)
    a.invert_yaxis()
    a.set_xlim(0, 76)
    a.set_xticks([0, 20, 40, 60])
    a.set_xlabel("Average task success (%)", labelpad=10)
    a.grid(axis="x", color="#E5E8EB", linewidth=.7)
    a.spines["left"].set_visible(False)
    for b, v in zip(bars, vals):
        a.text(v+1.3, b.get_y()+b.get_height()/2, f"{v:.1f}", va="center", size=14,
               color=blue if v == 64.6 else "#444444", weight="bold" if v == 64.6 else "normal")
    f.subplots_adjust(left=.26, right=.97, bottom=.18, top=.98)
    save(f, "average.png")

    # Five domains, CAMP-II against CAMP-I.
    f, a = base(width=7.4)
    x = np.arange(5)
    camp2 = [100.0, 37.5, 64.1, 81.2, 40.2]
    camp1 = [85.2, 32.0, 38.3, 68.8, 46.5]
    for dx, values, color, lab in [(-.19, camp1, grey, "CAMP-I"), (.19, camp2, blue, "CAMP-II")]:
        bs = a.bar(x+dx, values, .36, color=color, label=lab)
        for b, v in zip(bs, values):
            a.text(b.get_x()+b.get_width()/2, v+2, f"{v:.1f}", ha="center", size=11)
    a.set_xticks(x, ["Shop", "Coding", "Auto\nResearch", "General", "Visual"])
    a.set_ylim(0, 112)
    a.set_yticks([0, 25, 50, 75, 100])
    a.set_ylabel("Task success (%)")
    a.grid(axis="y", color="#E5E8EB", linewidth=.7)
    a.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(.5, 1.16), fontsize=12)
    f.subplots_adjust(left=.105, right=.98, bottom=.18, top=.85)
    save(f, "domains.png")

    # Ablation: what each substitution costs.
    f, a = base()
    names = ["CAMP-II", "compaction", "memory tools", "gradient masked", "budget-matched"]
    vals = [64.6, 48.2, 48.2, 47.3, 63.3]
    colors = [blue, grey, grey, grey, pale]
    bars = a.barh(np.arange(5), vals, color=colors, height=.62)
    a.set_yticks(np.arange(5), names)
    a.invert_yaxis()
    a.set_xlim(0, 76)
    a.set_xticks([0, 20, 40, 60])
    a.set_xlabel("Average task success (%)", labelpad=10)
    a.grid(axis="x", color="#E5E8EB", linewidth=.7)
    a.spines["left"].set_visible(False)
    for b, v in zip(bars, vals):
        a.text(v+1.3, b.get_y()+b.get_height()/2, f"{v:.1f}", va="center", size=14,
               color="#444444", weight="bold" if v == 64.6 else "normal")
    f.subplots_adjust(left=.30, right=.97, bottom=.18, top=.98)
    save(f, "ablation.png")

    # Teacher preference over the same memory content, three interfaces.
    f, a = base(width=6.2, height=3.4)
    names = ["File", "Compaction", "Memory tools"]
    vals = [76.5, 70.0, 63.8]
    bars = a.bar(np.arange(3), vals, .5, color=[blue, grey, grey])
    for b, v in zip(bars, vals):
        a.text(b.get_x()+b.get_width()/2, v+1.4, f"{v:.1f}", ha="center", size=13)
    a.set_xticks(np.arange(3), names)
    a.set_ylim(50, 84)
    a.set_ylabel("Preferred the correct write (%)")
    a.axhline(50, color=red, linewidth=1.1, linestyle="--")
    a.text(2.42, 50.9, "chance", color=red, size=10, ha="right")
    a.grid(axis="y", color="#E5E8EB", linewidth=.7)
    f.subplots_adjust(left=.13, right=.98, bottom=.17, top=.96)
    save(f, "preference.png")


def build(out_pptx: Path, site_root: Path):
    work = out_pptx.parent/"generated"
    charts(work)
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)
    blank = prs.slide_layouts[6]

    def new(heading=None, note=None):
        s = prs.slides.add_slide(blank)
        if heading:
            title(s, heading)
        if note:
            s.notes_slide.notes_text_frame.text = note
        return s

    # 1 - Cover
    s = new(note="CAMP-II: distilling file-based memory through the interface both models already know.")
    text(s, "JD.com", .26, .22, 1.35, .36, size=23, color=RED, bold=True)
    text(s, "Coding Agent Memory Post-Training II", .48, 1.12, 9.04, .56, size=26, bold=True,
         align=PP_ALIGN.CENTER)
    text(s, "Unlocking the Memory Potential of Pre-trained File Operations\nfor Long-Horizon Tasks via On-Policy Distillation",
         .48, 1.80, 9.04, .75, size=19, bold=True, align=PP_ALIGN.CENTER)
    text(s, "Lirui Luo · Kelong Mao · Heming Xia · Rongqing Li · Xinwei Yang · Luyu Chen\nKieran Wong · Yudong Guo · Xinrui Wang · Jiayin Zhu · Simiu Gu · Sulong Xu · Cong Fang",
         .55, 2.98, 8.9, .56, size=11.4, color=MID, align=PP_ALIGN.CENTER)
    text(s, "JD.com", .6, 3.68, 8.8, .28, size=13, bold=True, align=PP_ALIGN.CENTER)
    links(s, 4.24, 10.4)
    line(s, .65, 4.72, 9.35, 4.72)
    conclusion(s, [("An interface teaches", BLUE, True),
                   (" only what both models already speak.", INK, False)], 4.95, 16.5)

    # 2 - Two questions
    s = new("Distillation asks two questions, not one")
    node(s, "Task-reward training", .62, 1.02, 3.5, .62, MID)
    node(s, "On-policy distillation", 5.55, 1.02, 3.5, .62, BLUE)
    rect(s, .62, 1.82, 3.5, 1.05, WHITE, LINE)
    text(s, "Can the student reach the\nbehaviour by exploring?", .74, 1.98, 3.26, .8, size=15, color=MID)
    rect(s, 5.55, 1.82, 3.5, 1.05, PALE, BLUE)
    text(s, "Does the student emit the\naction, and can the teacher\nscore what it wrote?", 5.67, 1.92, 3.3, .95,
         size=14.5, color=BLUE, bold=True)
    text(s, "One prior is enough", 1.28, 3.05, 2.2, .3, size=12, color=MID, align=PP_ALIGN.CENTER)
    text(s, "Two priors must meet", 6.06, 3.05, 2.5, .3, size=12, color=BLUE, align=PP_ALIGN.CENTER)
    conclusion(s, [("Coverage and supervision", BLUE, True),
                   (" are the two sides of the same design choice.", INK, False)])
    source(s, "Section 1 · framing of the paper")

    # 3 - What the interface must provide
    s = new("The interface has to satisfy both sides")
    text(s, "Student side", .72, .92, 3.6, .3, size=16, bold=True, color=BLUE)
    terminal(s, "rollout", "cat > notes.md\nconfirmed: velvet", .68, 1.32, 3.9, 1.12, 12.5)
    text(s, "The action must appear in the sample,\nor there is nothing to supervise.", .72, 2.5, 3.9, .6,
         size=13.5, color=MID)
    text(s, "Teacher side", 5.42, .92, 3.6, .3, size=16, bold=True, color=RED)
    terminal(s, "frozen teacher", "p(note | context) = 0.91", 5.38, 1.32, 3.9, 1.12, 12.5, accent=RED)
    text(s, "The teacher must recognise the content\nit is asked to score.", 5.42, 2.5, 3.9, .6,
         size=13.5, color=MID)
    node(s, "A shared file interface", 2.9, 3.42, 4.2, .62, BLUE)
    line(s, 2.63, 1.78, 2.9, 3.42, color=BLUE, arrow=True)
    line(s, 7.35, 1.78, 7.1, 3.42, color=RED, arrow=True)
    conclusion(s, [("One interface", BLUE, True),
                   (" raises coverage and supervision at the same time.", INK, False)])
    source(s, "Section 3 · Figure 3; Appendix B")

    # 4 - The prior is already there
    s = new("The file interface is already familiar to both")
    metric(s, "1/3", "of the teacher's cost on compaction", 1.02, color=BLUE, x=.7, w=3.1)
    metric(s, "21.6%", "of actions are memory on files,\nagainst 7.8% and 5.9%", 1.02, color=BLUE, x=4.06, w=2.9)
    metric(s, "2.97x", "gain over the best OPD baseline", 1.02, color=RED, x=7.16, w=2.4)
    text(s, "Files cost the teacher a third of what compaction costs it, and the student a fifth.\nOn the file interface the student writes and reads memory far more often than on the\ninterfaces that need a protocol.", .72, 2.55, 8.6, .95, size=15, color=MID)
    conclusion(s, [("Nothing about the interface", BLUE, True),
                   (" has to be taught before training starts.", INK, False)])
    source(s, "Section 6 · Figure 3a,b")

    # 5 - CAMG-II
    s = new("CAMG-II: five environments, one memory substrate")
    rows = [("Shop", "six sessions, one purchase chain"),
            ("Coding", "repository repair across the horizon"),
            ("AutoResearch", "experiment, read, revise"),
            ("General", "long office tasks over a tool surface"),
            ("Visual", "build, inspect the render, revise")]
    for i, (name, desc) in enumerate(rows):
        y = .92 + i*.82
        node(s, name, .72, y, 2.25, .58, BLUE)
        text(s, desc, 3.2, y+.14, 6.4, .34, size=15, color=MID)
        line(s, .72, y+.7, 9.3, y+.7, color=LINE)
    text(s, "Every environment keeps its native task and shares ordinary shell access with an\nepisode-persistent workspace.", .72, 4.4, 8.5, .55, size=14, color=INK)
    source(s, "Section 4 · Appendix A")

    # 6 - Method
    s = new("Distil on what the student actually writes")
    node(s, "Student samples", .6, 1.0, 2.35, .62, BLUE)
    node(s, "Teacher scores every token", 3.28, 1.0, 3.0, .62, RED)
    node(s, "Learner follows the gap", 6.62, 1.0, 2.6, .62, BLUE)
    line(s, 2.95, 1.31, 3.28, 1.31, arrow=True)
    line(s, 6.28, 1.31, 6.62, 1.31, arrow=True)
    terminal(s, "what the trainee wrote", "page: css-only, no html body markup\nplan: rewrite dist/index.html\nnext: rebuild and check", .6, 1.9, 4.2, 1.25, 12.5)
    terminal(s, "what the teacher returns", "p(token | context) for every\ntoken of the write", 5.0, 1.9, 4.2, 1.25, 12.5, accent=RED)
    text(s, "Rollouts keep arriving from published weights while the learner catches up, so an\nepisode can enter a minibatch several weight publications after it was sampled.", .62, 3.35, 8.7, .7, size=14, color=MID)
    conclusion(s, [("Supervision reaches", BLUE, True),
                   (" exactly the tokens the policy chose to write.", INK, False)])
    source(s, "Section 5 · Appendix C")

    # 7 - Main result
    s = new("CAMP-II reaches 64.6% average task success")
    image(s, work/"average.png", .32, .82, 6.1, 3.75)
    metric(s, "64.6%", "average over five domains", 1.12, color=BLUE, x=6.85, w=2.9)
    metric(s, "+10.4", "points over CAMP-I", 2.02, color=RED, x=6.85, w=2.9)
    metric(s, "+16.4", "points over the frozen student", 2.92, color=MID, x=6.85, w=2.9)
    conclusion(s, [("Same schedule, same budget", BLUE, True),
                   (" - a different interface.", INK, False)])
    source(s, "Table 1 · five held-out panels, 128 tasks each")

    # 8 - Per domain
    s = new("The gain lands where the interface carries the most")
    image(s, work/"domains.png", .55, .82, 7.1, 3.8)
    metric(s, "+25.8", "AutoResearch", 1.15, color=BLUE, x=7.9, w=1.95)
    metric(s, "+12.4", "General", 2.05, color=BLUE, x=7.9, w=1.95)
    metric(s, "-6.3", "Visual", 2.95, color=MID, x=7.9, w=1.95)
    conclusion(s, [("Shop saturates and Visual stays bounded by the judge", BLUE, True),
                   ("; the long horizons open up.", INK, False)])
    source(s, "Table 1")

    # 9 - Ablation
    s = new("Every variant that touches memory supervision loses the gain")
    image(s, work/"ablation.png", .55, .82, 6.4, 3.8)
    text(s, "Swapping the interface for compaction or for the dedicated memory tools costs\n16 to 17 points. Masking the loss on the tokens the policy writes costs 17.\nMasking the same number of tokens at random costs 1.3.", 7.25, 1.06, 2.6, 2.6, size=13, color=MID)
    conclusion(s, [("The gain is", BLUE, True), (" the supervision on memory content,", INK, False),
                   (" not the budget.", BLUE, True)])
    source(s, "Figure 6 · Section 6.2")

    # 10 - Teacher preference
    s = new("The teacher prefers the write that keeps the task")
    image(s, work/"preference.png", .5, .9, 6.0, 3.55)
    text(s, "Two hundred note pairs per interface, each scored in both orders under the\nsame visible context. The teacher ranks the write that carries the prefix's own\ntask above a foreign one.", 6.72, 1.06, 3.1, 1.55, size=13.5, color=MID)
    metric(s, "0.918", "on Shop, with three distinct values", 2.75, color=RED, x=6.72, w=3.1)
    conclusion(s, [("A familiar interface", BLUE, True),
                   (" gives the teacher something to compare.", INK, False)])
    source(s, "Appendix D.3 · Figure 13")

    # 11 - Memory content intervention
    s = new("What the note says decides what the next context can do")
    image(s, site_root/"assets/case-study.png", .45, .95, 9.1, 3.3)
    conclusion(s, [("Change the saved content", BLUE, True),
                   (" and the episode that follows it changes with it.", INK, False)])
    source(s, "Figure 5 · intervention on the stored note")

    # 12 - Seeds
    s = new("The result does not rest on one draw")
    metric(s, "64.9", "mean over five seeds", 1.05, color=BLUE, x=1.0, w=2.5)
    metric(s, "0.5", "standard deviation, points", 1.05, color=BLUE, x=3.9, w=2.5)
    metric(s, "0.9", "largest domain deviation", 1.05, color=MID, x=6.8, w=2.3)
    terminal(s, "seed / average", "1 64.6   2 65.5   3 64.4\n4 65.0   5 65.2", 1.0, 2.3, 4.2, 1.25, 12.5)
    text(s, "Shop stays at 100.0 in every seed. Coding, AutoResearch, General and Visual each\nmove by about a point, and the ordering of the domains is stable.", 5.6, 2.42, 4.2, 1.05, size=13.5, color=MID)
    conclusion(s, [("The comparison in the paper", BLUE, True),
                   (" holds across training runs.", INK, False)])
    source(s, "Appendix C.3 · Table 8")

    # 13 - Transfer
    s = new("Trained memory carries outside the gym")
    rows = [("Qwen3.5-4B", "23.1", "11.2", "17.1"),
            ("Qwen3.5-9B", "23.1", "23.1", "23.1"),
            ("Qwen3.5-35B-A3B", "33.8", "27.4", "30.6"),
            ("CAMP-II-4B", "30.0", "18.1", "24.1"),
            ("CAMP-II-9B", "38.0", "30.1", "34.1")]
    heads = ["Policy", "Terminal-Bench 2.1", "SWE-Bench Pro V2", "Average"]
    xs = [.72, 3.9, 6.1, 8.35]
    ws = [3.1, 2.1, 2.2, 1.5]
    for x, w, h in zip(xs, ws, heads):
        text(s, h, x, 1.02, w, .3, size=11.5, color=MID)
    line(s, .72, 1.38, 9.3, 1.38)
    for i, row in enumerate(rows):
        y = 1.50 + i*.66
        hl = row[0].startswith("CAMP-II")
        for x, w, cell in zip(xs, ws, row):
            text(s, cell, x, y, w, .34, size=15 if not hl else 15.5,
                 bold=hl, color=BLUE if hl else INK)
        line(s, .72, y+.48, 9.3, y+.48, color=LINE)
    text(s, "Both trained policies improve on the weights they started from. The 9B policy averages\nabove a 35B model at a quarter of its parameters.", .72, 4.92, 8.6, .5,
         size=12.5, color=MID)
    source(s, "Table 2 · same suites, decoding budgets and graders across rows")

    # 14 - Cost model
    s = new("Why the interface decides the cost")
    rich(s, [("Rare-action regime of the mean-field cost model:", INK, True)], .78, 1.0, 8.4, .35, 15)
    text(s, "N  ~  1 / (2\u03bb Q\u2080 u\u2080)", 3.0, 1.6, 4.2, .45, size=22, color=BLUE, bold=True, align=PP_ALIGN.CENTER)
    text(s, "Q0   how rarely the student emits the action", .9, 2.35, 4.2, .3, size=13.5, color=MID)
    text(s, "u0   how far the student starts from the teacher", 5.1, 2.35, 4.2, .3, size=13.5, color=MID)
    text(s, "The exact mean-field integral has two limits. Rare action gives the form above; a policy\nalready close to the teacher loses u0 entirely and the cost falls to log(1/rho) over\n2*lambda*Q(1-Q). The law is a limit, not a universal law, and the paper says which regime\nit applies to.", .78, 2.95, 8.5, 1.35, size=13.5, color=INK)
    conclusion(s, [("An interface", BLUE, True),
                   (" moves Q0 and u0 at the same time.", INK, False)])
    source(s, "Appendix B · Theorem 1")

    # 15 - Conclusion
    s = new("What this paper establishes")
    items = [("A shared interface prior", "sets what memory distillation can teach."),
             ("CAMP-II", "reaches 64.6% average over five task worlds without a memory-specific teacher."),
             ("The behavior", "survives five seeds and transfers to two external suites.")]
    for i, (head, body) in enumerate(items):
        y = 1.05 + i*1.0
        text(s, head, .78, y, 3.2, .38, size=17, bold=True, color=BLUE)
        text(s, body, 4.05, y, 5.2, .62, size=14.5, color=INK)
    line(s, .78, 4.3, 9.25, 4.3)
    text(s, "Code and weights: withheld during review.", .78, 4.45, 5.4, .3, size=12, color=MID)
    text(s, "liruiluo.github.io/agentmemorygym-v2", 5.9, 4.45, 3.4, .3, size=12, color=BLUE, align=PP_ALIGN.RIGHT)

    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_pptx)
    return len(prs.slides.__iter__.__self__._sldIdLst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--site", default=str(Path(__file__).resolve().parents[1]))
    args = ap.parse_args()
    out = Path(args.out)
    n = build(out, Path(args.site))
    print(f"{out} ({n} slides)")


if __name__ == "__main__":
    main()
