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
PROJECT = "https://liruiluo.github.io/agentmemorygym/"
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
                       ("liruiluo.github.io/agentmemorygym", BLUE)],
               .55, y, 5.0, .25, size)
    box.text_frame.paragraphs[0].runs[1].hyperlink.address = PROJECT
    box = rich(slide, [("Paper: ", INK, True), ("arXiv:2609.34422", BLUE)],
               6.15, y, 3.25, .25, size)
    box.text_frame.paragraphs[0].runs[1].hyperlink.address = PAPER


def charts(out):
    out.mkdir(parents=True, exist_ok=True)
    # Set sizes for their physical slide dimensions, not a page-sized figure.
    plt.rcParams.update({"font.family": "Arial", "font.size": 13,
                         "axes.labelsize": 14, "xtick.labelsize": 12,
                         "ytick.labelsize": 12, "text.color": "#111111",
                         "axes.labelcolor": "#555555", "axes.edgecolor": "#A8AFB6",
                         "xtick.color": "#555555", "ytick.color": "#555555"})
    blue, grey, red = "#"+BLUE, "#BAC2CB", "#"+RED

    def base(width=6.6, height=3.95):
        f, a = plt.subplots(figsize=(width, height), dpi=220)
        a.spines[["top", "right"]].set_visible(False)
        a.set_axisbelow(True)
        a.tick_params(length=0, pad=7)
        return f, a

    def save(fig, name):
        fig.savefig(out/name, facecolor="white")
        plt.close(fig)

    f, a = base()
    names = ["Qwen3.5-4B", "Mem0", "Letta Code", "CompactionRL", "AgeMem", "CAMG-RL"]
    vals = [17.4, 19.7, 17.8, 48.0, 25.3, 54.4]
    bars = a.barh(np.arange(6), vals, color=[grey]*5+[blue], height=.62)
    a.set_yticks(np.arange(6), names)
    a.invert_yaxis()
    a.set_xlim(0, 64)
    a.set_xticks([0, 20, 40, 60])
    a.set_xlabel("Average task success (%)", labelpad=10)
    a.grid(axis="x", color="#E5E8EB", linewidth=.7)
    a.spines["left"].set_visible(False)
    for b, v in zip(bars, vals):
        a.text(v+1.3, b.get_y()+b.get_height()/2, f"{v:.1f}", va="center", size=14,
               color=blue if v==54.4 else "#444444", weight="bold" if v==54.4 else "normal")
    f.subplots_adjust(left=.25, right=.97, bottom=.18, top=.98)
    save(f, "main.png")

    f, a = base()
    x = np.arange(4)
    camg = [97.1, 26.6, 55.5, 38.3]
    compact = [97.5, 19.5, 50.8, 24.2]
    for dx, values, color, lab in [(-.19, compact, grey, "CompactionRL"),
                                   (.19, camg, blue, "CAMG-RL")]:
        bs = a.bar(x+dx, values, .36, color=color, label=lab)
        for b, v in zip(bs, values):
            a.text(b.get_x()+b.get_width()/2, v+2, f"{v:.1f}", ha="center", size=11)
    a.set_xticks(x, ["Shop", "Coding", "Deep\nResearch", "Auto\nResearch"])
    a.set_ylim(0, 112)
    a.set_yticks([0, 25, 50, 75, 100])
    a.set_ylabel("Task success (%)")
    a.grid(axis="y", color="#E5E8EB", linewidth=.7)
    a.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(.5, 1.17), fontsize=12)
    f.subplots_adjust(left=.115, right=.98, bottom=.18, top=.84)
    save(f, "domains.png")

    f, a = base()
    x = np.arange(4)
    # Rounded point estimates shown in the original Fig. 3a. No reconstructed error bars.
    files = [1.19, .08, .25, .27]
    tools = [1.40, .47, .27, .33]
    for i, (v1, v2) in enumerate(zip(files, tools)):
        a.plot([i-.11, i+.11], [v1, v2], color="#CBD3DB", lw=2, zorder=1)
    a.scatter(x-.11, files, s=100, color=blue, label="Filesystem actions", zorder=3)
    a.scatter(x+.11, tools, s=100, color=grey, edgecolor="#6F7F8C", label="Dedicated tools", zorder=3)
    for i, (v1, v2) in enumerate(zip(files, tools)):
        a.annotate(f"{v1:.2f}", (i-.11, v1), xytext=(-8,-19), textcoords="offset points",
                   ha="center", size=12, color=blue, weight="bold")
        a.annotate(f"{v2:.2f}", (i+.11, v2), xytext=(8,11), textcoords="offset points",
                   ha="center", size=12, color="#666666")
    a.set_xticks(x, ["Store", "Retrieve", "Revise", "Remove"])
    a.set_xlim(-.5, 3.5)
    a.set_ylim(-.10, 1.68)
    a.set_yticks([0, .5, 1.0, 1.5])
    a.set_ylabel("NLL (nats / action token)")
    a.grid(axis="y", color="#E5E8EB", linewidth=.7)
    a.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(.5, 1.17), fontsize=12)
    f.subplots_adjust(left=.15, right=.98, bottom=.15, top=.85)
    save(f, "prior.png")

    f, a = base()
    x = np.arange(2)
    for dx, vals, color, lab in [(-.17, [8.0,20.9],blue,"CAMG-RL"),
                                (.17,[0,0],grey,"AgeMem")]:
        bs=a.bar(x+dx, vals, .31, color=color, label=lab)
        for b,v in zip(bs,vals):
            a.text(b.get_x()+b.get_width()/2,v+.8,f"{v:.1f}%",ha="center",size=16,
                   color=color if color==blue else "#666666",weight="bold")
    a.set_ylim(0,27)
    a.set_yticks([0,5,10,15,20,25])
    a.set_xticks(x, ["First quarter\nupdates 1–50", "Final quarter\nupdates 151–200"])
    a.set_ylabel("Episodes with a complete chain (%)")
    a.grid(axis="y",color="#E5E8EB",linewidth=.7)
    a.legend(frameon=False,ncol=2,loc="upper center",bbox_to_anchor=(.5,1.15))
    f.subplots_adjust(left=.14,right=.98,bottom=.19,top=.85)
    save(f,"chains.png")

    f,a=base()
    vals=[54.4,21.1,41.8,28.1]
    labels=["Full\nCAMG-RL", "No memory\ngradients", "Continuation\nonly: retrain", "Continuation\nonly: eval"]
    colors=[blue,"#8FAECC","#ACC4D9",grey]
    bs=a.bar(np.arange(4),vals,color=colors,width=.62)
    a.set_ylim(0,65)
    a.set_xticks(np.arange(4),labels)
    a.set_yticks([0,20,40,60])
    a.set_ylabel("Average task success (%)")
    a.grid(axis="y",color="#E5E8EB",linewidth=.7)
    for b,v in zip(bs,vals):
        a.text(b.get_x()+b.get_width()/2,v+1.3,f"{v:.1f}",ha="center",size=16,weight="bold")
    a.axvline(2.5,color="#CCD2D8",lw=1,ls="--")
    f.subplots_adjust(left=.12,right=.98,bottom=.20,top=.96)
    save(f,"ablation.png")

    f,a=base()
    y=np.arange(4)
    for dy,values,c,lab in [(-.18,[-29.4,-13.8,-4.8,-8.3],red,"Blank"),
                            (.18,[-14.4,-6.5,-16.7,-8.3],blue,"Shuffled")]:
        bs=a.barh(y+dy,values,.33,color=c,label=lab)
        for b,v in zip(bs,values):
            a.text(v-.7,b.get_y()+b.get_height()/2,f"{v:.1f}",ha="right",va="center",size=12,color=c)
    a.set_yticks(y,["Shop", "Coding", "DeepResearch", "AutoResearch"])
    a.invert_yaxis()
    a.set_xlim(-37,1)
    a.set_xticks([-30,-20,-10,0])
    a.set_xlabel("Success change vs. intact memory (pp)",labelpad=10)
    a.grid(axis="x",color="#E5E8EB",linewidth=.7)
    a.axvline(0,color="#9AA4AD",lw=1)
    a.spines[["left","top","right"]].set_visible(False)
    a.legend(frameon=False,ncol=2,loc="upper center",bbox_to_anchor=(.5,1.15))
    f.subplots_adjust(left=.235,right=.98,bottom=.18,top=.86)
    save(f,"intervention.png")


def build(out_pptx: Path, site_root: Path):
    work=out_pptx.parent/"generated"
    charts(work)
    prs=Presentation()
    prs.slide_width=Inches(SW)
    prs.slide_height=Inches(SH)
    blank=prs.slide_layouts[6]
    def new(heading=None, note=None):
        s=prs.slides.add_slide(blank)
        if heading: title(s,heading)
        if note: s.notes_slide.notes_text_frame.text=note
        return s

    # 1 — Full centered academic cover.
    s=new(note="Public paper: arXiv:2609.34422v1. Approximately 15 minutes.")
    text(s,"JD.com",.26,.22,1.35,.36,size=23,color=RED,bold=True)
    text(s,"Coding Agent Memory Post-training",.48,1.15,9.04,.56,size=27,bold=True,align=PP_ALIGN.CENTER)
    text(s,"Unlocking the Memory Potential of Pre-trained File Operations\nfor Long-Horizon Tasks via Reinforcement Learning",
         .48,1.85,9.04,.75,size=20,bold=True,align=PP_ALIGN.CENTER)
    text(s,"Lirui Luo · Kelong Mao · Heming Xia · Rongqing Li · Xinwei Yang · Luyu Chen\nKieran Wong · Yudong Guo · Xinrui Wang · Jiayin Zhu · Simiu Gu · Sulong Xu · Cong Fang",
         .55,3.02,8.9,.56,size=11.4,color=MID,align=PP_ALIGN.CENTER)
    text(s,"JD.com",.6,3.72,8.8,.28,size=13,bold=True,align=PP_ALIGN.CENTER)
    links(s,4.27,10.4)
    line(s,.65,4.76,9.35,4.76)
    conclusion(s,[("Files as learned memory",BLUE,True),(": 54.4% success across four task worlds.")],4.98,16.5)

    # 2 — Recompose the teaser into two legible native lanes.
    s=new("Long tasks need state that outlives context")
    text(s,"Earlier work",2.05,.94,2.6,.32,size=16,bold=True,align=PP_ALIGN.CENTER)
    text(s,"After context replacement",6.28,.94,3.05,.32,size=16,bold=True,align=PP_ALIGN.CENTER)
    line(s,5.51,1.3,5.51,4.51,color=LIGHT,dash=True)
    text(s,"Context\nonly",.42,1.72,1.12,.65,size=17,bold=True)
    terminal(s,"Active history", "plan + evidence\nintermediate results",1.84,1.49,3.1,1.18,12.5)
    line(s,4.99,2.0,6.07,2.0,color=RED,width=1.7,arrow=True)
    node(s,"Recover lost state",6.18,1.63,2.98,.75,RED,size=17)
    text(s,"Repeated work",6.18,2.59,2.98,.29,size=14,color=RED,align=PP_ALIGN.CENTER)
    text(s,"CAMG-RL",.42,3.37,1.29,.4,size=17,bold=True,color=BLUE)
    terminal(s,"Save working state", "notes.md\nCONTINUATION.md",1.84,3.12,3.1,1.11,13)
    line(s,4.99,3.66,6.07,3.66,color=BLUE,width=1.7,arrow=True)
    node(s,"Read → act → finish",6.18,3.28,2.98,.75,BLUE,size=17)
    text(s,"Files persist across the boundary",2.0,4.4,7.15,.27,size=14,color=BLUE,align=PP_ALIGN.CENTER)
    conclusion(s,[("Durable state",RED,True),(" lets the next context continue the same task.")])
    source(s,"Figure 1 · schematic of context-only and file-memory execution")

    # 3 — Familiar operations on the left, a task-driven learning cycle on the right.
    s=new("Can task reward unlock the prior in file operations?")
    text(s,"A familiar action language",.55,.91,4.2,.36,size=18,bold=True,align=PP_ALIGN.CENTER)
    terminal(s,"shell_command", "cat > notes.md       # store\ngrep -n fact notes.md # find\ncat notes.md         # read\npython revise.py     # revise",.58,1.56,4.24,1.82,13.5)
    text(s,"Available from pre-training",.62,3.66,4.12,.3,size=15,color=MID,align=PP_ALIGN.CENTER)
    text(s,"A learned memory strategy",5.48,.91,4.0,.36,size=18,bold=True,align=PP_ALIGN.CENTER)
    node(s,"Write",5.57,1.67,1.45)
    node(s,"Read",7.77,1.67,1.45)
    line(s,7.05,2.01,7.65,2.01,color=BLUE,arrow=True)
    node(s,"Task reward",6.55,3.12,2.14,.66,RED)
    line(s,8.51,2.39,8.51,3.02,color=BLUE,arrow=True)
    text(s,"use in the task",7.0,2.59,1.47,.27,size=12,color=MID,align=PP_ALIGN.CENTER)
    line(s,6.5,3.45,6.3,3.45,color=RED)
    line(s,6.3,3.45,6.3,2.42,color=RED,arrow=True)
    text(s,"learn when / what to retain",5.42,4.03,4.12,.31,size=15,color=RED,align=PP_ALIGN.CENTER)
    conclusion(s,[("CAMG-RL",RED,True),(" trains the use of ordinary files from downstream task reward.")])
    source(s,"Introduction · the commands illustrate the common executable interface")

    # 4 — Four native task vignettes, with short task objects instead of a full paper thumbnail.
    s=new("CAMG connects four long-horizon task worlds")
    cols=[.46,2.86,5.26,7.66]
    headings=["Shop","Coding","DeepResearch","AutoResearch"]
    for x,heading in zip(cols,headings):
        text(s,heading,x,.99,2.12,.35,size=18,color=BLUE,bold=True,align=PP_ALIGN.CENTER)
        line(s,x,1.43,x+2.12,1.43,color=BLUE)
    text(s,"Earlier choice",.58,1.7,1.9,.26,size=13,color=MID)
    rect(s,.62,2.15,.43,.56,"23272B","23272B")
    text(s,"Black case",1.19,2.3,1.22,.29,size=13,bold=True)
    line(s,1.49,2.89,1.49,3.3,color=BLUE,arrow=True)
    text(s,"Later purchase",.58,3.49,1.9,.26,size=13,color=MID)
    text(s,"Match the earlier\ncolor preference",.58,3.86,1.98,.55,size=14)
    terminal(s,"Repository", "items()\n → wrong order\n\npatch + tests",2.91,1.69,2.02,1.88,12.5)
    text(s,"Carry fixes and\ntest evidence",2.94,3.91,1.96,.56,size=14)
    for yy,lab in [(1.8,"Search"),(2.49,"Visit sources"),(3.18,"Answer")]:
        node(s,lab,5.46,yy,1.72,.45,size=13)
        if yy<3: line(s,6.32,yy+.47,6.32,yy+.63,color=BLUE,arrow=True)
    text(s,"Retain facts and\nsource evidence",5.35,3.91,1.96,.56,size=14)
    terminal(s,"ML workspace", "train.csv\nmodel.py\nsubmission.csv",7.71,1.69,2.03,1.88,12)
    text(s,"Reuse experiments\nand intermediate files",7.70,3.91,2.07,.56,size=14)
    conclusion(s,[("Native tasks + shell access + episode-persistent workspace",BLUE,True)],4.98,17)
    source(s,"Section 4 · task vignettes redrawn from the public examples in Appendix A")

    # 5 — System diagram with explicit flow and shared learning ownership.
    s=new("One policy learns across all four environments")
    node(s,"CAMG-RL policy",.66,1.56,2.46,1.0,BLUE,PALE,21)
    text(s,"native task + file actions",3.23,1.39,2.47,.28,size=12,color=BLUE,align=PP_ALIGN.CENTER)
    line(s,3.2,1.91,5.72,1.91,color=BLUE,width=1.7,arrow=True)
    line(s,5.72,2.26,3.2,2.26,color=MID,width=1.5,arrow=True)
    text(s,"observation + task reward",3.23,2.43,2.47,.3,size=12,color=MID,align=PP_ALIGN.CENTER)
    node(s,"Shop",5.91,1.42,1.54,.59,size=16)
    node(s,"Coding",7.74,1.42,1.73,.59,size=16)
    node(s,"DeepResearch",5.91,2.14,1.54,.59,size=12.5)
    node(s,"AutoResearch",7.74,2.14,1.73,.59,size=12.5)
    text(s,"Parallel environment episodes",5.89,.91,3.67,.28,size=16,bold=True,align=PP_ALIGN.CENTER)
    node(s,"Persistent files",.66,3.23,2.25,.65,BLUE,size=17)
    line(s,1.71,2.62,1.71,3.13,color=BLUE,arrow=True)
    line(s,2.12,3.13,2.12,2.62,color=BLUE,arrow=True)
    text(s,"write / read",.77,4.02,2.2,.27,size=13,color=MID,align=PP_ALIGN.CENTER)
    node(s,"Episode queue",5.58,3.71,2.02,.70,BLUE,size=17)
    line(s,8.64,2.82,8.64,4.06,color=BLUE)
    line(s,8.64,4.06,7.73,4.06,color=BLUE,arrow=True)
    text(s,"completed\ntrajectories",8.71,3.25,1.08,.56,size=11,color=MID)
    node(s,"Actor + critic",3.01,3.71,2.0,.70,RED,size=17)
    line(s,5.47,4.06,5.14,4.06,color=RED,arrow=True)
    line(s,4.0,3.61,4.0,3.07,color=RED)
    line(s,4.0,3.07,2.79,3.07,color=RED)
    line(s,2.79,3.07,2.79,2.63,color=RED,arrow=True)
    text(s,"publish weights",3.38,2.82,1.59,.22,size=11,color=RED)
    conclusion(s,[("Fully asynchronous PPO",RED,True),(" overlaps rollouts and learning.")])
    source(s,"Figure 2 · shared policy and learner; task semantics remain in each environment")

    # 6 — Explicit context transition with a durable file underneath.
    s=new("Context changes; the working files remain")
    text(s,"Current context",.69,.94,2.9,.31,size=17,bold=True,align=PP_ALIGN.CENTER)
    text(s,"Mechanical reset",3.61,.94,2.75,.31,size=17,color=RED,bold=True,align=PP_ALIGN.CENTER)
    text(s,"Fresh context",6.63,.94,2.7,.31,size=17,bold=True,align=PP_ALIGN.CENTER)
    terminal(s,"Policy-authored file", "CONTINUATION.md\n\nplan + evidence\nnext steps",.61,1.61,2.92,1.66,14)
    text(s,"Clear active history\nKeep task + file paths",3.85,1.94,2.30,.67,size=16,align=PP_ALIGN.CENTER)
    terminal(s,"Ordinary read action", "cd .agent_memory\ncat CONTINUATION.md",6.59,1.61,2.92,1.66,14)
    line(s,3.56,2.41,3.81,2.41,color=RED,arrow=True)
    line(s,6.19,2.41,6.50,2.41,color=RED,arrow=True)
    rect(s,1.31,3.73,7.4,.57,WHITE,BLUE)
    text(s,"Episode workspace: continuation · notes · evidence · task files",1.41,3.88,7.2,.3,size=16,color=BLUE,align=PP_ALIGN.CENTER)
    line(s,2.1,3.31,2.1,3.62,color=BLUE,arrow=True)
    line(s,8.05,3.64,8.05,3.31,color=BLUE,arrow=True)
    conclusion(s,[("The policy writes and reads.",BLUE,True),(" The reset contributes no policy action.")])
    source(s,"Section 5.1 · reset supplies paths; it does not inject saved file contents")

    # 7 — Shared response-level credit, including file operations.
    s=new("Task reward trains the entire memory-use chain")
    text(s,"One sampled action trajectory",.65,.94,8.7,.32,size=18,bold=True,align=PP_ALIGN.CENTER)
    xs=[.55,2.43,4.31,6.19,8.07]
    labels=["Task action","Write","Retrieve","Use","Outcome"]
    for i,(x,lab) in enumerate(zip(xs,labels)):
        col=RED if i==4 else BLUE
        node(s,lab,x,1.86,1.38,.81,col,PALE if i in [1,2] else WHITE,16)
        if i<4: line(s,x+1.43,2.26,x+1.78,2.26,color=BLUE,arrow=True)
    text(s,"files as policy actions",2.47,2.91,3.17,.31,size=14,color=BLUE,align=PP_ALIGN.CENTER)
    text(s,"native task\nreward",8.06,2.96,1.42,.63,size=15,color=RED,align=PP_ALIGN.CENTER)
    line(s,8.78,3.65,8.78,3.88,color=RED)
    line(s,8.78,3.88,1.25,3.88,color=RED,width=1.6,arrow=True)
    for x in xs[:-1]: line(s,x+.69,3.84,x+.69,2.83,color=RED,arrow=True)
    text(s,"GAE returns → token-level PPO",2.72,4.11,4.6,.34,size=18,color=RED,bold=True,align=PP_ALIGN.CENTER)
    conclusion(s,[("Task and memory responses share downstream credit.",INK,True)])
    source(s,"Section 5; Appendix B · no separate memory reward or reset optimizer row")

    # 8–11 — Large exhibits plus the prominent metric column used in CRG.
    s=new("CAMG-RL reaches 54.4% average task success")
    image(s,work/"main.png",.22,.84,6.62,3.97)
    metric(s,"54.4%","four-environment average",1.49,BLUE)
    line(s,7.50,2.76,9.26,2.76)
    metric(s,"+6.4 pp","over CompactionRL",3.02,RED)
    conclusion(s,[("Learning to use files",RED,True),(" outperforms the strongest memory baseline.")])
    source(s,"Table 2 · 128 test tasks per environment · paired difference 95% CI: [3.3, 9.5] pp")

    s=new("The largest gains are in Coding and AutoResearch")
    image(s,work/"domains.png",.23,.80,6.63,3.97)
    metric(s,"+7.1 pp","Coding",1.47,BLUE)
    line(s,7.50,2.76,9.26,2.76)
    metric(s,"+14.1 pp","AutoResearch",3.02,RED)
    conclusion(s,[("Shop is near saturation; "),("Coding and AutoResearch",RED,True),(" open the gap.")],size=16.5)
    source(s,"Table 2; Appendix C.1 · paired improvements significant in Coding and AutoResearch")

    s=new("The frozen base already favors filesystem actions")
    image(s,work/"prior.png",.23,.85,6.63,3.97)
    metric(s,"≤ 0.013","nats/token change\nwhen the shell tool is renamed",1.44,BLUE)
    line(s,7.50,2.96,9.26,2.96)
    text(s,"The prior extends\nbeyond the tool name.",7.18,3.34,2.42,.83,size=17,bold=True,align=PP_ALIGN.CENTER)
    conclusion(s,[("Familiar action rendering",RED,True),(" gives reinforcement learning a usable starting point.")],size=16.5)
    source(s,"Figure 3a; Appendix C.1 · frozen Qwen3.5-4B · lower NLL means more likely actions")

    s=new("RL turns familiar actions into complete memory chains")
    image(s,work/"chains.png",.23,.80,6.63,3.97)
    metric(s,"8.0 → 20.9%","episodes with a complete chain",1.44,BLUE,x=7.02,w=2.74)
    line(s,7.50,2.88,9.26,2.88)
    text(s,"Store → retrieve → use",7.02,3.16,2.74,.67,size=17,bold=True,align=PP_ALIGN.CENTER)
    text(s,"Beyond the mandatory\ncontinuation write",7.15,4.0,2.48,.51,size=13,color=MID,align=PP_ALIGN.CENTER)
    conclusion(s,[("Voluntary memory use grows",RED,True),(" while AgeMem completes no chain.")])
    source(s,"Figure 3b; Appendix C.1 · first and last quarters of the common 200-update training protocol")

    # 12 — Native readable table, deliberately selected comparisons.
    s=new("Trained competence transfers to external benchmarks")
    text(s,"Success rate (%)",.61,.95,3.4,.31,size=14,color=MID)
    text(s,"SWE-bench Verified",4.66,.95,2.27,.61,size=16,bold=True,align=PP_ALIGN.CENTER)
    text(s,"MLE-bench Lite",7.16,.95,2.13,.61,size=16,bold=True,align=PP_ALIGN.CENTER)
    line(s,.6,1.48,9.4,1.48,color=INK)
    rows=[("Qwen3.5-4B",7.6,0.0,False),
          ("CAMG-RL-4B",15.8,4.5,True),
          ("Qwen3.5-35B-A3B",15.6,4.5,False),
          ("Qwen3.5-9B",14.8,4.5,False),
          ("CAMG-RL-9B",27.6,9.1,True),
          ("Qwen3.5-122B-A10B",22.0,9.1,False)]
    for i,(lab,swe,mle,ours) in enumerate(rows):
        yy=1.65+i*.45+(0.18 if i>=3 else 0)
        if ours: rect(s,.62,yy-.06,8.77,.43,PALE,PALE,0)
        text(s,lab,.78,yy,3.9,.32,size=17,bold=ours,color=BLUE if ours else INK)
        text(s,f"{swe:.1f}",4.8,yy,2.0,.32,size=18,bold=ours,color=BLUE if ours else INK,align=PP_ALIGN.CENTER)
        text(s,f"{mle:.1f}",7.23,yy,2.0,.32,size=18,bold=ours,color=BLUE if ours else INK,align=PP_ALIGN.CENTER)
        if i==2: line(s,.63,yy+.36,9.37,yy+.36)
    line(s,.6,4.58,9.4,4.58,color=INK)
    conclusion(s,[("4B and 9B policies",RED,True),(" are competitive with much larger frozen models.")],size=16.5)
    source(s,"Selected rows from Table 3 · matched tasks, decoding, budgets and graders; all failures included")

    s=new("Memory-action credit and general files both matter")
    image(s,work/"ablation.png",.23,.83,6.63,3.97)
    metric(s,"−33.3 pp","without memory-action gradients",1.46,RED)
    line(s,7.50,2.79,9.26,2.79)
    metric(s,"−12.6 pp","retrained with\ncontinuation-only memory",3.03,BLUE)
    conclusion(s,[("Learning the file actions",RED,True),(" and using general memory files both help.")],size=16.5)
    source(s,"Figure 4 · last bar restricts the full policy only at evaluation; it is not a retrained model")

    s=new("Changing saved content reduces subsequent success")
    image(s,work/"intervention.png",.23,.81,6.63,3.97)
    metric(s,"−14.1 pp","blank memory\nequal-environment average",1.40,RED)
    line(s,7.50,2.89,9.26,2.89)
    metric(s,"−11.5 pp","task-mismatched memory\nequal-environment average",3.08,BLUE)
    conclusion(s,[("Saved content affects later decisions",RED,True),(" at the same post-reset state.")],size=16.5)
    source(s,"Appendix D.3 · eligible n = 128 / 29 / 60 / 23 · shuffled donors matched within environment and by length")

    # 15 — Large file contents and genuine commands from the public training case.
    s=new("A coding episode shows the write–read–use chain")
    text(s,"Scrapy: repair broken response logging",.53,.89,8.92,.37,size=18,bold=True)
    terminal(s,"Before reset · round 18", "objective: fix response logging\nevidence: added _mqpush\n  in scrapy/core/scheduler.py\ntested: no _mqpush error\nnext: run tests, confirm\n  logging, then submit",.53,1.56,4.24,2.51,13.2)
    text(s,".agent_memory/CONTINUATION.md",.56,4.22,4.16,.29,size=13,color=BLUE,font=CODE)
    line(s,5.04,1.54,5.04,4.52,color=RED,dash=True)
    terminal(s,"After reset · rounds 19–30", "$ cat \\\n    .agent_memory/CONTINUATION.md\n$ python test_spider.py\n$ python -m pytest \\\n    tests/test_crawl.py -v",5.32,1.56,4.15,2.08,13.2)
    text(s,"Hidden tests passed",5.51,3.86,3.73,.32,size=18,color=GREEN,bold=True)
    text(s,"Return 1.00 · submitted at step 30 / 40",5.51,4.28,3.84,.31,size=12.5,color=MID)
    conclusion(s,[("The saved fix and verification plan",RED,True),(" guide work in the fresh context.")],size=16.5)
    source(s,"Figure 5; Appendix A.4.3 · training trajectory · excerpts shortened for presentation; wrapped commands")

    # 16 — Clean closing page that can remain on screen during questions.
    s=new("Takeaways")
    rich(s,[("• CAMG ",RED,True),("makes long-horizon memory testable across four native task worlds.")],.64,1.09,8.77,.66,19)
    rich(s,[("• CAMG-RL ",RED,True),("learns to write, retrieve and reuse files from downstream task reward.")],.64,2.11,8.77,.66,19)
    rich(s,[("• Familiar file operations ",RED,True),("support learned memory chains and stronger task performance.")],.64,3.13,8.77,.70,19)
    links(s,4.43,10.7)
    line(s,.53,4.90,9.48,4.90)
    text(s,"Coding Agent Memory Post-training",.57,5.08,8.09,.29,size=15,bold=True)
    text(s,"JD.com",8.52,5.07,.93,.29,size=15,color=RED,bold=True,align=PP_ALIGN.RIGHT)

    # Grounded notes travel with the editable deck; no unpublished run state is embedded.
    for index,s in enumerate(prs.slides,1):
        tf=s.notes_slide.notes_text_frame
        if not tf.text.strip():
            tf.text=f"Slide {index}. Source: public arXiv:2609.34422v1. See slides/outline.md for provenance and speaking notes."
    out_pptx.parent.mkdir(parents=True,exist_ok=True)
    prs.core_properties.title="Coding Agent Memory Post-training"
    prs.core_properties.subject="Public paper talk · arXiv:2609.34422v1 · CRG/SPHERE academic style"
    prs.core_properties.author="Lirui Luo et al. · JD.com"
    prs.save(out_pptx)
    print(out_pptx)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--site-root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    build(a.out.resolve(),a.site_root.resolve())


if __name__=="__main__":
    main()
