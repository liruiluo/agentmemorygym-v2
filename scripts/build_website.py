#!/usr/bin/env python3
"""Render the static site from its template and the shared paper-data snapshot."""
import html
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
esc = html.escape

def bars(rows, maximum=80, highlight=None, classes=''):
    result = []
    for label, value in rows:
        cls = ' ours' if label == highlight else ''
        result.append(f'<div class="hbar{cls} {classes}"><span class="hbar-name">{esc(label)}</span><div class="hbar-track" aria-hidden="true"><i style="width:{value/maximum*100:.5f}%"></i></div><strong>{value:.1f}</strong></div>')
    return '\n'.join(result)

def table(headers, rows, caption):
    return '<table><caption>'+esc(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr'+(' class="highlight"' if str(r[0]).startswith('CAMP-II') else '')+'><th scope="row">'+esc(str(r[0]))+'</th>'+''.join('<td>'+esc(f'{c:.1f}' if isinstance(c,(float,int)) else str(c))+'</td>' for c in r[1:])+'</tr>' for r in rows)+'</tbody></table>'

def main():
    d=json.loads((ROOT/'data/research.json').read_text())
    main=d['main_results']; by={r['name']:r for r in main}
    display=[by[n] for n in ['CAMP-II','CAMP-I','MemOPD (w/ SFT)','HELM (single-model)','Hy-Memory','CompactOPD','Frozen 4B','ACM','HELM','MemOPD']]
    domain=[]
    for i,name in enumerate(d['domains']):
        a=by['CAMP-I']['scores'][i]; b=by['CAMP-II']['scores'][i]
        domain.append(f'<div class="domain"><h4>{name}</h4><div class="paired-bars"><div><span>{a:.1f}</span><i style="height:{a*1.45}px" class="camp1"></i></div><div><span>{b:.1f}</span><i style="height:{b*1.45}px" class="camp2"></i></div></div><p class="delta {"negative" if b<a else ""}">{b-a:+.1f} pts</p></div>')
    paths={
      'bag':'<path d="M8 12h24l3 25H5zM14 14V9a6 6 0 0 1 12 0v5"/>',
      'code':'<rect x="3" y="6" width="34" height="28" rx="2"/><path d="m14 16-5 5 5 5m12-10 5 5-5 5m-4-13-4 16"/>',
      'plot':'<path d="M5 4v31h32M11 27l7-10 8 4 9-13"/><circle cx="18" cy="17" r="2"/>',
      'doc':'<path d="M8 3h17l8 8v26H8zM25 3v9h8M14 19h13M14 25h13M14 31h8"/>',
      'web':'<rect x="3" y="5" width="34" height="30" rx="2"/><path d="M3 13h34M9 9h1m4 0h1m4 0h1M9 19h11v10H9zm17 0h5m-5 6h5"/>'}
    env=''.join(f'<article class="environment"><svg viewBox="0 0 40 40" aria-hidden="true">{paths[e["icon"]]}</svg><div><h3>{esc(e["name"])}</h3><span>{esc(e["origin"])}</span></div><p>{esc(e["task"])}</p><p class="env-memory">{esc(e["memory"])}</p></article>' for e in d['environments'])
    ext={r['name']:r for r in d['external']}; transfer=[]
    for key,heading in [('tb','Terminal-Bench 2.1'),('swe','SWE-Bench Pro V2')]:
        rows=[]
        for scale in ['4B','9B']:
            a=ext['Qwen3.5-'+scale][key]; b=ext['CAMP-II-'+scale][key]
            rows.append(f'<div class="transfer-pair"><span class="model-scale">{scale}</span><div>'+bars([('Initial model',a),('CAMP-II',b)],50,'CAMP-II')+'</div></div>')
        transfer.append(f'<figure><figcaption>{heading}<span>Success rate (%) · axis 0–50</span></figcaption>'+''.join(rows)+'</figure>')
    citation='@article{luo2026campii,\n  title = {'+d['title']+'},\n  author = {'+' and '.join(d['authors'])+'},\n  year = {'+str(d['year'])+'}'
    if d['arxiv_id']:
        citation+=',\n  eprint = {'+d['arxiv_id']+'},\n  archivePrefix = {arXiv}'
    citation+='\n}'
    paper='https://arxiv.org/abs/'+d['arxiv_id'] if d['arxiv_id'] else d['paper_url']
    vals={
      'TITLE':esc(d['title']), 'PROJECT':d['project_url'],'PAPER':paper,'CODE':esc(d['code_url']),
      'PAPER_LABEL':'Paper on arXiv' if d['arxiv_id'] else 'Paper PDF',
      'AUTHORS':' · '.join(esc(n) for n in d['authors']), 'AFFILIATIONS':' · '.join(esc(n) for n in d['affiliations']),
      'MAIN_CHART':bars([(r['name'],r['avg']) for r in display],80,'CAMP-II'),
      'MAIN_TABLE':table(['Policy']+d['domains']+['Average'],[[r['name']]+r['scores']+[r['avg']] for r in main],'Paper Table 1 · CAMG-II scores (0–100). Frozen 4B/9B are Qwen3.5; frozen teacher is Qwen3.8-27B.'),
      'DOMAIN_CHART':'\n'.join(domain),
      'COVERAGE':bars([(r['name'],r['action_share']) for r in d['interfaces']],25,'Files / Bash'),
      'PREFERENCE':bars([(r['name'],r['preference']) for r in d['interfaces']],100,'Files / Bash'),
      'ABLATIONS':bars([(r['name'],r['value']) for r in d['ablations']],80,'CAMP-II'),
      'ENVIRONMENTS':env,'TRANSFER':''.join(transfer),
      'EXTERNAL_TABLE':table(['Policy','Terminal-Bench 2.1','SWE-Bench Pro V2','Average'],[[r['name'],r['tb'],r['swe'],r['avg']] for r in d['external']],'Paper Table 2 · external transfer success rates (%)'),
      'CITATION':esc(citation),'RELEASE':('arXiv:'+esc(d['arxiv_id']) if d['arxiv_id'] else 'Submitted to arXiv; identifier pending announcement')
    }
    page=(ROOT/'scripts/site.template.html').read_text()
    for k,v in vals.items(): page=page.replace('{{'+k+'}}',v)
    assert '{{' not in page, 'Unresolved template slot'
    (ROOT/'index.html').write_text(page)
    print('Built index.html from data/research.json and scripts/site.template.html')
if __name__=='__main__':main()
