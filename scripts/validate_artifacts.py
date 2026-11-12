#!/usr/bin/env python3
"""Check generated web/deck parity, data transcription, links and PDF geometry."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import statistics
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import fitz
from pptx import Presentation

ROOT=Path(__file__).resolve().parents[1]
PAPER_SHA='f340af5b1db73e959717b918a2471299c35c0882346609e0bbac25902dfce908'

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.tables=[];self.cells=None;self.row=None;self.cell=None;self.words=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag in ('a','img','script','link'):
            link=a.get('href',a.get('src'))
            if link:self.links.append(link)
        if tag=='table':self.cells=[]
        if tag=='tr':self.row=[]
        if tag in ('th','td'):self.cell=[]
    def handle_data(self,data):
        self.words.append(data)
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('th','td') and self.cell is not None:
            self.row.append(''.join(self.cell).strip());self.cell=None
        if tag=='tr' and self.row is not None:
            self.cells.append(self.row);self.row=None
        if tag=='table' and self.cells is not None:
            self.tables.append(self.cells);self.cells=None

def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
def check(root=ROOT):
    checks=[]
    def expect(cond,name):
        checks.append({'check':name,'pass':bool(cond)})
    d=json.loads((root/'data/research.json').read_text())
    src=(root/'index.html').read_text();page=Page();page.feed(src)
    expect('{{' not in src,'No unresolved template slots')
    expect(len(page.ids)==len(set(page.ids)),'Unique document IDs')
    for href in page.links:
        u=urlparse(href)
        if u.scheme in ('https','http','mailto'):continue
        if href.startswith('#'):expect(href[1:] in page.ids,'Anchor '+href);continue
        expect((root/unquote(u.path)).is_file(),'Local asset '+href)
    expected_main=[['Policy']+d['domains']+['Average']]+[[r['name']]+[f'{n:.1f}' for n in r['scores']+[r['avg']]] for r in d['main_results']]
    expected_ext=[['Policy','Terminal-Bench 2.1','SWE-Bench Pro V2','Average']]+[[r['name']]+[f'{r[k]:.1f}' for k in ['tb','swe','avg']] for r in d['external']]
    expect(page.tables==[expected_main,expected_ext],'Every displayed table cell matches shared research snapshot')
    expect(len(d['main_results'])==13 and len(d['external'])==5,'Complete comparison roster')
    expect(len(d['authors'])==13 and all(x in src for x in d['authors']),'All 13 authors retained')
    expect('Heming Xia' not in src and '2609.34422' not in src,'No stale V1 author/identifier')
    expect(d['authors'].index('Pu Yao')+1==d['authors'].index('Gu Simiu'),'Pu Yao appears immediately before Gu Simiu')
    paper=fitz.open(root/'assets/paper.pdf');first=paper[0].get_text()
    expect('Pu Yao' in first and first.index('Pu Yao')<first.index('Gu Simiu'),'Public PDF includes Pu Yao before Gu Simiu')
    expect('JD.com' in first and d['project_url'] in first,'Public PDF includes JD.com and project website')
    expect(any(link.get('uri')==d['project_url'] for link in paper[0].get_links()),'Public PDF project link is clickable')
    expect(f'<link rel="canonical" href="{d["project_url"]}">' in src,'Current canonical URL')
    by={r['name']:r for r in d['main_results']}
    gain=by['CAMP-II']['avg']-by['Frozen 4B']['avg'];refgain=by['MemOPD (w/ SFT)']['avg']-by['Frozen 4B']['avg']
    for value in [f'{gain:.1f}',f'{refgain:.1f}',f'{gain/refgain:.2f}',f'{by["CAMP-II"]["avg"]-by["MemOPD (w/ SFT)"]["avg"]:.1f}']:
        expect(value in src,'Explanatory arithmetic '+value)
    seed_means=[statistics.mean(row) for row in d['seed_domain_scores']]
    expect([round(v,1) for v in seed_means]==d['seed_avgs'],'Seed domain rows reproduce displayed averages')
    expect(round(statistics.mean(seed_means),1)==d['seed_mean'] and round(statistics.stdev(seed_means),1)==d['seed_sd'],'Seed mean and sample SD before intermediate rounding')
    expect(hashlib.sha256((root/'assets/paper.pdf').read_bytes()).hexdigest()==PAPER_SHA,'Public paper PDF matches the current source export')
    ppt=Presentation(root/'assets/slides/campii-slides.pptx');pdf=fitz.open(root/'assets/slides/campii-slides.pdf')
    expect(len(ppt.slides)==len(pdf)==15,'PPTX and PDF both 15 slides')
    numeric_wraps=[];bounds=[];mismatches=[];overlaps=[];picture_slides=[]
    for i,(slide,p) in enumerate(zip(ppt.slides,pdf),1):
        txt=p.get_text();normalized=norm(txt)
        expect('来源与口径' in slide.notes_slide.notes_text_frame.text,f'Slide {i} source and Chinese speaker notes')
        for shape in slide.shapes:
            x,y,w,h=[v/12700 for v in [shape.left,shape.top,shape.width,shape.height]]
            if x<-.1 or y<-.1 or x+w>p.rect.width+.1 or y+h>p.rect.height+.1:
                bounds.append([i,shape.name,x,y,w,h])
            if shape.shape_type==13:picture_slides.append(i)
            if not shape.has_text_frame or not shape.text.strip():continue
            if norm(shape.text) not in normalized:mismatches.append([i,shape.text])
            if re.fullmatch(r'[+−-]?\d+\.\d+%?',shape.text):
                clipped=p.get_text('text',clip=fitz.Rect(x-1,y-3,x+w+1,y+h+3))
                if shape.text not in clipped.splitlines():numeric_wraps.append([i,shape.text,clipped])
        spans=[s for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if s['text'].strip()]
        for a in range(len(spans)):
            ra=fitz.Rect(spans[a]['bbox'])
            if not p.rect.contains(ra):bounds.append([i,spans[a]['text'],list(ra)])
            for b in range(a+1,len(spans)):
                rb=fitz.Rect(spans[b]['bbox']);inter=ra & rb
                if not inter.is_empty and inter.width>2 and inter.height>2 and inter.get_area()>min(ra.get_area(),rb.get_area())*.15:
                    overlaps.append([i,spans[a]['text'],spans[b]['text']])
    expect(not mismatches,'Every native PPTX text box survives PDF rendition')
    expect(not numeric_wraps,'Numeric data labels remain on one line')
    expect(not bounds,'No slide/text content outside the page')
    expect(not overlaps,'No material native-text overlaps')
    expect(picture_slides==[12],'Only the observed case uses a raster picture')
    fonts={f[0]:f for p in pdf for f in p.get_fonts()}
    expect(all(f[2]!='Type3' and bool(pdf.extract_font(x)[3]) for x,f in fonts.items()),'All PDF fonts embedded; zero Type 3')
    expect('19.3' in pdf[6].get_text() and '16.4' not in pdf[6].get_text(),'Correct gain over frozen 4B in deck')
    expect(all(f'{r["preference"]:.1f}' in pdf[9].get_text() for r in d['interfaces']),'Teacher preference points in deck')
    expect('27.4' in pdf[13].get_text() and '31.6' not in pdf[13].get_text(),'External reference copied from designated paper')
    expect((root/'slides/speaker-notes.md').is_file(),'Readable speaker notes generated')
    return {'passed':all(c['pass'] for c in checks),'checks':checks,'text_mismatches':mismatches,'numeric_wraps':numeric_wraps,'out_of_bounds':bounds,'text_overlaps':overlaps}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--output',type=Path);a=ap.parse_args();result=check(a.root)
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(payload+'\n')
    print(payload);raise SystemExit(0 if result['passed'] else 1)
