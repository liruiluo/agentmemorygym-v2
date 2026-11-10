#!/usr/bin/env python3
"""Build the editable 15-minute CAMP-II talk from the same data as the website.

All charts, typography and explanatory diagrams are native PowerPoint shapes.
Only the observed Visual case uses a frozen paper image. No GUI is launched.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

ROOT=Path(__file__).resolve().parents[1]
W,H=13.333333,7.5
INK,MUTED,LIGHT,LINE='17232D','596772','75818D','DCE2E9'
BLUE,PALE,GREY,RED,WHITE='235EC8','EAF1FF','AEBDCE','AA3B36','FFFFFF'
WASH='F5F7FA'
FONT='Arial'

def rgb(c):return RGBColor.from_string(c)

def text(s,content,x,y,w,h,size=22,color=INK,bold=False,align=PP_ALIGN.LEFT,font=FONT,valign=MSO_ANCHOR.TOP):
    b=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=b.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    tf.vertical_anchor=valign
    for i,row in enumerate(str(content).split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=row or ' ';p.alignment=align;p.line_spacing=1.12;p.space_after=Pt(0)
        for r in p.runs:r.font.name=font;r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=rgb(color)
    return b

def rect(s,x,y,w,h,fill=WHITE,stroke=LINE,width=.8,oval=False):
    r=s.shapes.add_shape(MSO_SHAPE.OVAL if oval else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    r.fill.solid();r.fill.fore_color.rgb=rgb(fill);r.line.color.rgb=rgb(stroke);r.line.width=Pt(width)
    return r

def line(s,x,y,x2,y2,color=LINE,width=1,arrow=False,dash=False):
    r=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(y),Inches(x2),Inches(y2))
    r.line.color.rgb=rgb(color);r.line.width=Pt(width)
    if arrow:
        a=OxmlElement('a:tailEnd');a.set('type','triangle');a.set('w','med');a.set('len','med');r.line._get_or_add_ln().append(a)
    if dash:
        a=OxmlElement('a:prstDash');a.set('val','dash');r.line._get_or_add_ln().append(a)
    return r

def image(s,p,x,y,w,h):
    iw,ih=Image.open(p).size;scale=min(w/iw,h/ih);ww,hh=iw*scale,ih*scale
    return s.shapes.add_picture(str(p),Inches(x+(w-ww)/2),Inches(y+(h-hh)/2),Inches(ww),Inches(hh))

def note(s,body,source=''):
    s.notes_slide.notes_text_frame.text=body+('\n\n来源与口径：'+source if source else '')

def heading(s,title,n,source='',subtitle=None):
    text(s,title,.58,.43,11.6,.62,size=30,bold=True)
    text(s,'CAMP–II',12.02,.28,.74,.24,size=11,color=BLUE,bold=True,align=PP_ALIGN.RIGHT)
    line(s,.6,1.20,12.73,1.20)
    if subtitle:text(s,subtitle,.63,1.41,12.0,.52,size=17,color=MUTED)
    text(s,source,.62,7.16,11.4,.18,size=9,color=LIGHT)
    text(s,f'{n:02d} / 15',12.0,7.13,.72,.22,size=10,color=LIGHT,align=PP_ALIGN.RIGHT)

def conclusion(s,copy,y=6.47,size=24):
    line(s,.64,y-.22,12.68,y-.22,color=LINE)
    text(s,copy,.67,y,12,.62,size=size,color=BLUE,bold=True)

def file(s,x,y,w,h,title='notes.md',lines=None):
    rect(s,x,y,w,h,WHITE,'B4C8EB');rect(s,x,y,.055,h,BLUE,BLUE)
    text(s,title,x+.22,y+.17,w-.43,.3,size=16,color=BLUE,bold=True,font='Menlo')
    line(s,x+.05,y+.64,x+w,y+.64)
    if lines:text(s,lines,x+.22,y+.88,w-.44,h-.97,size=17,color=INK)

def barplot(s,rows,x,y,w,h,maxv=80,labelw=2.8,highlight=None,size=17,axis=True,colors=None):
    # Native geometry and data labels; axis begins at zero.
    n=len(rows);step=(h-.45)/n;plotw=w-labelw-.95;plotx=x+labelw
    if axis:
        ticks=[0,20,40,60,80] if maxv==80 else ([0,25,50,75,100] if maxv==100 else ([0,25,50] if maxv==50 else [0,5,10,15,20,25]))
        for tick in ticks:
            xx=plotx+plotw*tick/maxv;line(s,xx,y-.02,xx,y+step*n-.05,width=.5)
            text(s,str(tick),xx-.16,y+step*n+.06,.38,.2,size=10,color=LIGHT,align=PP_ALIGN.CENTER)
    for i,(lab,val) in enumerate(rows):
        yy=y+i*step
        col=(colors[i] if colors else BLUE if lab==highlight else GREY)
        text(s,lab,x,yy+.015,labelw-.15,step-.02,size=size,color=BLUE if lab==highlight else INK,bold=lab==highlight,valign=MSO_ANCHOR.MIDDLE)
        bh=min(.32,step*.65)
        if val:rect(s,plotx,yy+(step-bh)/2,plotw*val/maxv,bh,col,col,width=.1)
        text(s,f'{val:.1f}',plotx+plotw*val/maxv+.10,yy+.015,.86,step-.02,size=size,color=BLUE if lab==highlight else MUTED,bold=lab==highlight,valign=MSO_ANCHOR.MIDDLE)

def build(out,site_root):
    d=json.loads((site_root/'data/research.json').read_text());by={r['name']:r for r in d['main_results']}
    prs=Presentation();prs.slide_width=Inches(W);prs.slide_height=Inches(H)
    prs.core_properties.title=d['title'];prs.core_properties.author='Lirui Luo and coauthors';prs.core_properties.subject='CAMP-II: shared file-operation priors for on-policy memory distillation'
    def slide(title=None,source='',subtitle=None):
        s=prs.slides.add_slide(prs.slide_layouts[6])
        if title:heading(s,title,len(prs.slides),source,subtitle)
        return s
    # 1: one visual idea, complete publication identity.
    s=slide()
    text(s,'CAMP–II',.68,.42,3,.38,size=18,color=BLUE,bold=True)
    text(s,'Coding Agent Memory\nPost-Training II',.68,1.10,8.3,1.47,size=42,bold=True)
    text(s,'Unlocking the Memory Potential of Pre-trained File Operations\nfor Long-Horizon Tasks via On-Policy Distillation',.72,2.80,11.7,.8,size=22,color=MUTED)
    file(s,9.75,1.08,2.73,1.43,'memory.md','write → read')
    text(s,'Context 1',8.82,.70,1.45,.25,size=11,color=MUTED)
    text(s,'Context 2',11.20,.70,1.45,.25,size=11,color=MUTED)
    line(s,9.27,.95,11.85,.95,BLUE,1.1,arrow=True)
    text(s,' · '.join(d['authors'][:6])+'\n'+' · '.join(d['authors'][6:]),.74,4.11,11.88,.66,size=14,color=INK)
    text(s,' · '.join(d['affiliations'][:3])+'\n'+' · '.join(d['affiliations'][3:]),.74,4.96,11.85,.60,size=11,color=MUTED)
    line(s,.74,5.85,12.55,5.85)
    text(s,'Teaching agents to remember through files.',.74,6.13,10.5,.53,size=26,color=BLUE,bold=True)
    p=text(s,d['project_url'].replace('https://',''),.76,6.93,9.5,.2,size=10,color=MUTED)
    p.text_frame.paragraphs[0].runs[0].hyperlink.address=d['project_url']
    p=text(s,'Paper',11.25,6.90,1.23,.25,size=11,color=BLUE,align=PP_ALIGN.RIGHT)
    p.text_frame.paragraphs[0].runs[0].hyperlink.address=('https://arxiv.org/abs/'+d['arxiv_id'] if d['arxiv_id'] else d['paper_url'] if d['paper_url'].startswith('https://') else d['project_url']+d['paper_url'])
    note(s,'这篇工作讨论一个具体问题：长程 agent 的任务还没有结束，但上下文已经装不下了。我们用师生都熟悉的文件操作来蒸馏记忆。先看任务中的问题，再看为什么选择这个接口。','论文完整标题与现有网站作者/单位列表。约 30 秒。')
    # 2: concrete task before abstract priors.
    s=slide('The context ends. The task does not.','Visual case · explanatory schematic; actual trace on slide 12','Task: build a fitness-product showcase with products, collections, picks and comparisons.')
    text(s,'Before the boundary',.74,2.19,3.8,.38,size=22,bold=True)
    text(s,'Styles are present.\nThe HTML body is missing.',.74,2.91,3.5,1.60,size=22,color=MUTED)
    line(s,4.05,3.41,4.88,3.41,BLUE,1.3,arrow=True)
    file(s,5.03,2.22,3.19,2.59,'CONTR.txt','CSS only. No HTML body.\n\nRewrite all four sections.')
    line(s,8.38,3.41,9.12,3.41,BLUE,1.3,arrow=True)
    text(s,'After the boundary',9.37,2.19,3.2,.38,size=22,bold=True)
    text(s,'The history is gone.\nRead the plan and continue.',9.37,2.91,3.08,1.13,size=22,color=MUTED)
    text(s,'Context is replaced',4.91,5.18,3.52,.3,size=16,color=RED,align=PP_ALIGN.CENTER)
    text(s,'The file persists',4.91,5.61,3.52,.35,size=20,color=BLUE,bold=True,align=PP_ALIGN.CENTER)
    conclusion(s,'The memory must preserve what the next context needs.')
    note(s,'用真实 Visual 案例串起动机：模型发现页面只有 CSS、没有 HTML body，但此时需要换上下文。笔记保存问题和重写计划。换完后再读回来，任务才能连上。这里先画解释性示意，后面会展示原始轨迹；不把示意当新实验。','Figure 5。约 60 秒。')
    # 3: the two-sided bottleneck, no exaggerated impossibility claim.
    s=slide('A strong teacher still needs a usable memory interface','Introduction; Figure 3','On-policy distillation learns from actions the student actually samples.')
    for x,label,title,body in [(.75,'Student side','Sample a meaningful\nmemory action.','If a write never appears,\nit receives no supervision.'),(7.12,'Teacher side','Give useful feedback\non that same action.','A strong task model may still be\nunfamiliar with the memory protocol.')]:
        line(s,x,2.24,x+5.30,2.24,color=BLUE,width=2)
        text(s,label,x,2.49,5.2,.27,size=15,color=BLUE,bold=True)
        text(s,title,x,3.06,5.25,1.10,size=30,bold=True)
        text(s,body,x,4.46,5.20,.94,size=21,color=MUTED)
    conclusion(s,'Memory learning depends on both action coverage and teacher feedback.')
    note(s,'现在才引入双边接口问题。OPD 教的是学生真实采出的动作，所以学生得愿意用这个接口，老师也得能够评分。一个模型很会解任务，不代表它熟悉任意新造的记忆协议。不要说陌生接口绝对无法工作；论文比较的是不同接口的学习条件和效果。','约 60 秒。')
    # 4: method choice in ordinary language.
    s=slide('Use the file operations both models already know','CAMG-II interface; CAMP-II method','A shared Bash interface, an episode-persistent workspace, one task-acting policy.')
    ops=[('Create / revise','Save requirements, findings\nand a plan.'),('Search / read','Recover relevant state\nwhen it is needed.'),('Continue','Use that state for the\nnext task decision.')]
    for i,(name,body) in enumerate(ops):
        x=.8+i*4.17
        text(s,name,x,2.32,3.6,.44,size=26,bold=True,color=BLUE)
        text(s,body,x,3.08,3.57,1.15,size=21,color=MUTED)
        if i<2:line(s,x+3.55,2.56,x+4.0,2.56,BLUE,1.1,arrow=True)
    file(s,2.84,4.54,7.65,1.21,'Episode-persistent workspace',None)
    text(s,'notes.md     evidence/     CONTINUATION.md',3.08,5.29,7.0,.27,size=16,color=MUTED,font='Menlo',align=PP_ALIGN.CENTER)
    conclusion(s,'Familiar operations provide the channel. Training teaches the memory.')
    note(s,'采用普通文件，不是发明一组专用记忆 API。模型本来就会 bash 和文件操作；这些已有能力提供了可用的通道。训练要学的是保留什么、怎样组织、何时读取。普通记忆文件和有界 continuation 文件都在这个框架里。上下文重置后只给路径，不自动注入笔记内容。','文件名为接口示意，不是新增工具。约 60 秒。')
    # 5: show the actual learning relation, no advisor role.
    s=slide('The student acts. The frozen teacher scores.','Method · detached token-level OPD signal with clipped importance correction','The teacher sees the student’s recorded context and scores the response it sampled.')
    xvals=[.75,5.00,9.16]
    for i,(name,body) in enumerate([('Sample','Task actions and file writes\ncome from the student.'),('Score','Scores the same tokens\nin the same context.'),('Update','Train the student on both\ntask and memory tokens.')]):
        text(s,f'0{i+1}',xvals[i],2.28,1,.25,size=14,color=BLUE)
        text(s,name,xvals[i],2.78,3.38,.48,size=29,bold=True)
        text(s,body,xvals[i],3.50,3.40,.98,size=19,color=MUTED)
        if i<2:line(s,xvals[i]+3.47,3.04,xvals[i]+4.00,3.04,BLUE,1.3,arrow=True)
    rect(s,.78,5.01,11.79,.91,WASH,WASH)
    text(s,'Token feedback  =  teacher log-probability  −  student log-probability',1.10,5.28,11.15,.38,size=21,color=BLUE,align=PP_ALIGN.CENTER)
    conclusion(s,'Learn from the teacher during training. Act without it at inference.',size=23)
    note(s,'OPD 的顺序是学生先采样，教师再对同一个输出的每个 token 评分。教师与学生共享可见上下文，没有替学生执行动作，也不是给学生另一份答案。更新以 teacher 和 student 的 log probability 差构成 detached signal，并做 clipped importance correction；异步 rollout 的版本校正在实现中处理。监督覆盖任务与记忆输出，题面、观测和 padding 不训。','Method 方程。约 75 秒。')
    # 6: five distinct tasks, no pointless UI cards.
    s=slide('One policy learns across five task worlds','CAMG-II · five long-horizon environments','Native task semantics stay intact. The file-memory interface is shared.')
    descriptions=[('Shop','Six linked\npurchases','Product evidence'),('Coding','Repository\nrepair','Diagnosis + tests'),('AutoResearch','ML experiment\niteration','Results + next trial'),('General','Multi-tool\nknowledge work','Requirements + outputs'),('Visual','Website\ndevelopment','Visual findings + plan')]
    for i,(name,task,mem) in enumerate(descriptions):
        x=.72+i*2.54
        text(s,name,x,2.41,2.30,.37,size=22,bold=True,color=BLUE)
        line(s,x,3.04,x+2.18,3.04)
        text(s,task,x,3.31,2.29,.88,size=21)
        text(s,mem,x,4.53,2.29,.62,size=15,color=MUTED)
        line(s,x+1.05,5.14,x+1.05,5.45,color=BLUE)
    rect(s,.78,5.45,11.78,.67,PALE,PALE)
    text(s,'One joint policy  ·  ordinary Bash  ·  persistent workspace',1.03,5.62,11.3,.35,size=22,color=BLUE,align=PP_ALIGN.CENTER)
    note(s,'这是环境贡献 CAMG-II，不要和方法 CAMP-II 混为一个名字。五种任务分别需要保存购物约束、代码诊断、实验结果、知识工作中间输出和视觉开发计划。一个 policy 联合训练。Coding agent 指用文件管理记忆的形式，不是所有任务都写代码。','约 50 秒。')
    # 7: all primary baseline variants visible.
    s=slide('File-based OPD gives the largest average gain','Table 1 · five-domain mean: four success rates + Visual panel-mean judge score','The full 4B comparison set. CAMP-I uses task RL; the memory baselines use OPD adaptations.')
    names=['CAMP-II','CAMP-I','MemOPD (w/ SFT)','HELM (single-model)','Hy-Memory','CompactOPD','Frozen 4B','ACM','HELM','MemOPD']
    barplot(s,[(n,by[n]['avg']) for n in names],.74,2.11,8.30,4.48,labelw=2.79,highlight='CAMP-II',size=16)
    text(s,'+12.8',9.45,2.55,2.9,.72,size=46,color=BLUE,bold=True)
    text(s,'points over the strongest\nmemory OPD baseline',9.49,3.43,2.9,.85,size=18,color=MUTED)
    line(s,9.49,4.56,12.47,4.56)
    text(s,'2.97× the gain',9.49,4.88,2.95,.40,size=24,bold=True,color=BLUE)
    text(s,'From the same initial 4B:\n+19.3 vs +6.5 points.',9.49,5.48,2.95,.70,size=17,color=MUTED)
    note(s,'先给完整主比较，不只挑一个弱基线。CAMP-II 为 64.6，最强 OPD 记忆基线 MemOPD 加 SFT 冷启动为 51.8，显示差 12.8 点。初始 4B 为 45.3，因此两个增量是 19.3 和 6.5，比例约 2.97。它不是最终分数高三倍。CAMP-I 是同文件记忆的 task-RL 参照。MemOPD 零分是无 SFT 冷启动的版本，不能拿它替代原始 recipe。','Table 1，差额为展示值算术。约 75 秒。')
    # 8: native domain bars retain the negative domain.
    s=slide('The average improves; Visual remains a trade-off','Table 1 · Visual is a panel-mean judge score; other domains use task success','CAMP-II versus the file-memory task-RL reference, CAMP-I.')
    plotx=.93;ploty=2.38;ploth=2.83;basey=ploty+ploth
    for t in [0,50,100]:
        yy=basey-ploth*t/100;line(s,plotx,yy,12.45,yy,color=LINE,width=.5)
        text(s,str(t),.38,yy-.1,.36,.2,size=11,color=LIGHT,align=PP_ALIGN.RIGHT)
    for i,name in enumerate(d['domains']):
        x=1.38+i*2.29;a=by['CAMP-I']['scores'][i];b=by['CAMP-II']['scores'][i]
        for dx,val,col in [(0,a,GREY),(.54,b,BLUE)]:
            hh=ploth*val/100;rect(s,x+dx,basey-hh,.43,hh,col,col,.1)
            text(s,f'{val:.1f}',x+dx-.09,basey-hh-.32,.61,.23,size=13,color=MUTED,align=PP_ALIGN.CENTER)
        text(s,name,x-.26,5.45,1.58,.4,size=16,align=PP_ALIGN.CENTER)
        text(s,f'{b-a:+.1f} pts',x-.26,5.94,1.58,.3,size=17,color=BLUE if b>=a else RED,bold=True,align=PP_ALIGN.CENTER)
    rect(s,9.14,1.50,.18,.18,GREY,GREY);text(s,'CAMP-I',9.44,1.47,1.15,.3,size=13,color=MUTED)
    rect(s,10.82,1.50,.18,.18,BLUE,BLUE);text(s,'CAMP-II',11.12,1.47,1.25,.3,size=13,color=MUTED)
    conclusion(s,'The largest gain over CAMP-I is in AutoResearch: +25.8 points.',size=23)
    note(s,'平均更好不等于每个域都胜过 CAMP-I。最大差在 AutoResearch，General 也明显增加。Visual 40.2 对 CAMP-I 46.5，负 6.3 点，保留这个反例。Visual 的值是平均判分，不要当成功题数。这里的差额同样是表格显示值相减。','约 55 秒。')
    # 9: both sides grounded, with two complementary exhibits.
    s=slide('Files expose more memory actions to learning','Figure 3 · action share and frozen-model surprisal','The file interface is familiar to both models and used more by the student.')
    text(s,'Memory actions / all actions (%)',.78,2.20,7.4,.35,size=20,bold=True)
    barplot(s,[(r['name'],r['action_share']) for r in d['interfaces']],.79,2.92,7.50,2.70,maxv=25,labelw=2.15,highlight='Files / Bash',size=20)
    text(s,'Lower surprisal',9.08,2.20,3.7,.35,size=22,color=BLUE,bold=True)
    text(s,'Nats per token · lower is more familiar',9.08,2.75,3.55,.5,size=13,color=MUTED)
    text(s,'Teacher',10.27,3.38,1.0,.3,size=13,color=MUTED,align=PP_ALIGN.CENTER)
    text(s,'Student',11.54,3.38,1.0,.3,size=13,color=MUTED,align=PP_ALIGN.CENTER)
    for i,r in enumerate(d['interfaces']):
        yy=3.90+i*.57
        text(s,['Files','Tools','Compact'][i],8.86,yy,1.3,.32,size=16,color=BLUE if i==0 else MUTED)
        for xx,key in [(10.27,'teacher_nll'),(11.54,'student_nll')]:
            text(s,f'{r[key]:.2f}',xx,yy,1.0,.3,size=16,color=BLUE if i==0 else MUTED,bold=i==0,align=PP_ALIGN.CENTER)
    conclusion(s,'A familiar channel gives OPD more memory actions to supervise.')
    note(s,'先看覆盖率：文件接口中记忆动作占 21.6%，工具为 7.8%，压缩为 5.9%。右边是冻结教师和初始学生对动作的 surprisal，以每 token 的 NLL 表示，越低越熟悉。不要把 NLL 说成实际美元费用，也不要把文件能力说成无需训练就已会最优记忆。','约 60 秒。')
    # 10: preference diagnostic, no score/return confusion.
    s=slide('The teacher better recognizes task-matched notes','Appendix D.3 · same-task versus foreign-task memory preference','Does the teacher prefer a note from this task over a note from another task?')
    barplot(s,[(r['name'],r['preference']) for r in d['interfaces']],1.00,2.62,9.8,3.00,maxv=100,labelw=2.70,highlight='Files / Bash',size=24)
    line(s,3.7+(9.8-2.7-.95)*.5,2.51,3.7+(9.8-2.7-.95)*.5,5.13,RED,1,dash=True)
    text(s,'50% chance',6.03,5.72,1.7,.3,size=13,color=RED)
    text(s,'76.5%',10.78,2.81,1.9,.54,size=32,color=BLUE,bold=True)
    text(s,'on files',10.86,3.43,1.7,.4,size=18,color=MUTED)
    conclusion(s,'This tests task relevance. Next: isolate what the student learns.',size=23)
    note(s,'这页把“老师能不能评分”变成一个具体辨别问题：同一任务笔记和外来笔记，老师偏好哪一个。文件 76.5%，压缩 70.0%，专用工具 63.8%。只报告点估计，不声称显著；更不把老师的似然偏好直接等同于这条笔记能提高任务成功率。真正针对学习作用的控制在下一页。','约 55 秒。')
    # 11: concise, matched ablation story.
    s=slide('Learning what to write carries the gain','Figure 6 · controlled interface and loss-masking ablations','Mask memory-content supervision, or mask the same token budget at random.')
    barplot(s,[(r['name'],r['value']) for r in d['ablations']],.77,2.27,9.30,3.77,maxv=80,labelw=4.20,highlight='CAMP-II',size=19,colors=[BLUE,GREY,GREY,RED,'7D9FDD'])
    text(s,'−17.3',10.49,2.82,2.1,.58,size=37,color=RED,bold=True)
    text(s,'memory-content\nloss masked',10.53,3.55,2.14,.73,size=18,color=MUTED)
    text(s,'−1.3',10.49,4.63,2.1,.58,size=37,color=BLUE,bold=True)
    text(s,'same budget\nmasked at random',10.53,5.35,2.14,.73,size=18,color=MUTED)
    conclusion(s,'Which tokens are taught matters—not only how many.',size=25)
    note(s,'遮掉记忆内容 token 的蒸馏损失，平均分从 64.6 掉到 47.3。随机遮掉同样多 token 仍有 63.3。这比只展示文件读写频次更直接：收益依赖对记忆内容的训练。更换记忆接口也会掉到 48.2。不要把这些不同干预混成一个单变量实验；每行的干预对象要说清楚。','约 75 秒。')
    # 12: full source exhibit; labels are large enough at full slide scale.
    s=slide('The agent resumes from a plan it wrote','Paper Figure 5 · observed Visual training episode; not a causal intervention')
    image(s,site_root/'assets/case-study.png',1.45,1.45,10.45,5.12)
    text(s,'Write → replace context → read → continue',.74,6.65,11.9,.35,size=21,color=BLUE,bold=True,align=PP_ALIGN.CENTER)
    note(s,'回到开场的真实例子。第 32 回合写 CONTR.txt，记录 CSS-only 和缺少 body 的问题，还列了四个待补板块。第 33 回合上下文被替换，35 回合 ls，36 回合 cat，后续继续重写页面。这里给观众看的是原图和原有轨迹，不是人为补造的成功演示，也不是“换笔记”的因果实验。','约 60 秒。')
    # 13: native points, labelled spread not confidence interval.
    s=slide('The result repeats across five training seeds','Appendix C.3 · sample standard deviation across training seeds','Same CAMP-II recipe. Five independent training runs.')
    text(s,f'{d["seed_mean"]:.1f} ± {d["seed_sd"]:.1f}',.84,2.40,5.20,.94,size=52,color=BLUE,bold=True)
    text(s,'Five-domain mean ± sample SD',.88,3.52,5.30,.40,size=20,color=MUTED)
    x0,y0,pw=7.08,5.27,5.15
    for tick in [64,65,66]:
        xx=x0+(tick-64)*pw/2;line(s,xx,2.65,xx,y0,color=LINE,width=.6)
        text(s,str(tick),xx-.2,y0+.17,.4,.3,size=13,color=MUTED,align=PP_ALIGN.CENTER)
    for i,v in enumerate(d['seed_avgs']):
        yy=2.87+i*.48;xx=x0+(v-64)*pw/2
        text(s,f'Run {i+1}',5.77,yy-.08,1.1,.25,size=14,color=MUTED)
        rect(s,xx-.055,yy-.055,.11,.11,BLUE,BLUE,.1,oval=True)
        text(s,f'{v:.1f}',xx+.15,yy-.10,.6,.26,size=14,color=BLUE)
    text(s,'CAMG-II average score · expanded axis 64–66',6.92,5.89,5.5,.32,size=13,color=MUTED)
    conclusion(s,'The five reported averages range from 64.4 to 65.5.',size=25)
    note(s,'均值 64.9、样本标准差 0.5，是训练种子间的波动，不是标准误或置信区间。右侧用点图和显式 64 到 66 的局部坐标展示全部五点，避免用截断柱图夸大差异。不要据此声称每个对照也有五 seed 的配对显著性。','约 45 秒。')
    # 14: paired benchmark improvements; larger MoE reference named exactly.
    s=slide('The learned policy improves on two external benchmarks','Table 2 · success rates (%); larger reference is Qwen3.5-35B-A3B','Both model sizes improve over the checkpoints they start from.')
    ext={r['name']:r for r in d['external']}
    for k,(key,label) in enumerate([('tb','Terminal-Bench 2.1'),('swe','SWE-Bench Pro V2')]):
        x=.85+k*6.45;text(s,label,x,2.16,5.7,.45,size=25,bold=True)
        rows=[]
        for scale in ['4B','9B']:
            rows.extend([(f'{scale} initial',ext['Qwen3.5-'+scale][key]),(f'{scale} CAMP-II',ext['CAMP-II-'+scale][key])])
        barplot(s,rows,x,3.07,5.62,2.79,maxv=50,labelw=1.73,highlight=None,size=17,axis=True,colors=[GREY,BLUE,GREY,BLUE])
        text(s,f'35B-A3B reference: {ext["Qwen3.5-35B-A3B"][key]:.1f}',x,5.98,5.65,.36,size=15,color=MUTED)
    conclusion(s,'Memory learned in the gym carries into new task benchmarks.',size=24)
    note(s,'两个外部评测都要报名称，别只给一个平均。4B 从 23.1/11.2 到 30.0/18.1，9B 从 23.1/23.1 到 38.0/30.1。下方保留当前表的 Qwen3.5-35B-A3B 33.8/27.4 参照，不替换成更新的中间回执。它是 MoE，不能说四分之一参数就等于四分之一推理成本。','约 70 秒。')
    # 15: one claim and three contributions, usable during Q&A.
    s=slide('Familiar operations make better teaching channels','CAMP-II · Coding Agent Memory Post-Training II')
    text(s,'Teach memory through files.',.80,1.91,11.7,.83,size=40,color=BLUE,bold=True)
    items=[('The principle','Match the memory interface to both the student and the teacher.'),('The method','Distill the task policy’s own file actions with token-level feedback.'),('The evidence','Higher average scores, memory-specific ablations and external transfer.')]
    for i,(a,b) in enumerate(items):
        yy=3.22+i*.91;text(s,a,.86,yy,2.46,.4,size=21,bold=True)
        text(s,b,3.39,yy,8.98,.65,size=21,color=MUTED)
    line(s,.86,6.25,12.48,6.25)
    text(s,'One shared file-memory interface. Five long-horizon task worlds.',.86,6.53,11.6,.43,size=22,color=BLUE)
    note(s,'最后留一句话：接口不只是工程包装，它决定学生会产出什么动作，以及老师能提供什么监督。CAMP-II 用熟悉的文件操作把两边连起来；CAMG-II 提供五个长程任务世界。停在这页进入问答，理论和实现细节按问题解释。','约 30 秒。')
    assert len(prs.slides)==15
    out.parent.mkdir(parents=True,exist_ok=True);prs.save(out)
    notes=['# CAMP-II 演讲备注\n\n15 页，约 15 分钟。由 build_slides.py 与 PPTX 同源生成。\n']
    for i,s in enumerate(prs.slides,1):
        notes.append(f'## {i:02d}\n\n'+s.notes_slide.notes_text_frame.text+'\n')
    (site_root/'slides').mkdir(parents=True,exist_ok=True)
    (site_root/'slides/speaker-notes.md').write_text('\n'.join(notes))
    print(json.dumps({'slides':len(prs.slides),'output':str(out),'native_charts':True,'source':str(site_root/'data/research.json')}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'assets/slides/campii-slides.pptx');ap.add_argument('--site-root',type=Path,default=ROOT);a=ap.parse_args();build(a.out,a.site_root)
