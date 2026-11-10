#!/usr/bin/env python3
"""Offline browser acceptance: viewport layout, images, tab keyboard and fallback."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]


def run(root,out):
    out.mkdir(parents=True,exist_ok=True);checks=[];errors=[];external=[]
    def expect(ok,what):checks.append({'check':what,'pass':bool(ok)})
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True)
        for width in [1440,1024,768,390,320]:
            context=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1)
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:external.append(r.url) if r.url.startswith(('http:','https:')) else None)
            page.goto((root/'index.html').as_uri());page.wait_for_load_state('load')
            expect(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'No document overflow at {width}px')
            expect(page.locator('h1').is_visible(),f'Hero visible at {width}px')
            if width < 760:
                expect('back. Finish' in page.locator('.case-intro h2').inner_text(),f'Responsive line-break removal preserves word spacing at {width}px')
            # Screenshots must not mistake lazy-loading placeholders for failed images.
            page.locator('details.figure-details').evaluate('(e)=>e.open=true')
            for img in page.locator('img').all():
                img.scroll_into_view_if_needed();img.evaluate('(e)=>e.loading="eager"')
                page.wait_for_function('(img)=>img.complete && img.naturalWidth>0',arg=img.element_handle())
            expect(page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.complete && i.naturalWidth>0)'),f'All paper figures load at {width}px')
            page.locator('details.figure-details').evaluate('(e)=>e.open=false')
            page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
            page.screenshot(path=str(out/f'site-{width}.png'),full_page=True)
            if width==1440:
                page.screenshot(path=str(out/'site-hero.png'))
                page.locator('#story-tab-1').focus()
                for key,selected in [('ArrowRight',2),('End',3),('ArrowRight',1),('ArrowLeft',3),('Home',1)]:
                    page.keyboard.press(key)
                    expect(page.locator(f'#story-tab-{selected}').get_attribute('aria-selected')=='true',f'Tab key {key} selects stage {selected}')
                    expect(page.evaluate(f'document.activeElement.id==="story-tab-{selected}"'),f'Tab key {key} moves focus')
                    expect(page.locator('[role=tab][tabindex="0"]').count()==1,'One tab in sequential focus order')
                    expect(page.locator('[role=tabpanel]:visible').count()==1,'One visible active panel')
                for n in [2,3]:
                    page.locator(f'#story-tab-{n}').click();page.locator('.memory-scene').screenshot(path=str(out/f'story-stage-{n}.png'))
                page.locator('details.citation').evaluate('(e)=>e.open=true')
                page.evaluate('Object.defineProperty(navigator,"clipboard",{configurable:true,value:{writeText: async (t)=>{window.copied=t}}})')
                page.locator('#copy-citation').click()
                expect(page.locator('#copy-status').inner_text()=='Citation copied.' and page.evaluate('window.copied.includes("Cong Fang")'),'Clipboard success includes complete author list')
                page.evaluate('Object.defineProperty(navigator,"clipboard",{configurable:true,value:undefined})')
                page.locator('#copy-citation').click()
                expect('selected' in page.locator('#copy-status').inner_text() and page.evaluate('getSelection().toString().includes("Cong Fang")'),'Clipboard unavailable: selectable-text fallback')
            context.close()
        context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
        page=context.new_page();page.goto((root/'index.html').as_uri())
        expect(all(page.locator(f'#story-panel-{i}').is_visible() for i in [1,2,3]),'No JS: every story stage remains visible')
        expect(page.locator('#evidence .hbar').count()==10,'No JS: main results are readable')
        page.locator('.data-details').first.locator('summary').click()
        expect(page.locator('.data-details').first.locator('table').is_visible(),'No JS: native results-table expansion works')
        expect(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'No JS: no horizontal overflow')
        page.screenshot(path=str(out/'no-js-mobile.png'),full_page=True);context.close()
        context=browser.new_context(reduced_motion='reduce')
        page=context.new_page();page.goto((root/'index.html').as_uri())
        expect(page.evaluate('getComputedStyle(document.documentElement).scrollBehavior==="auto"'),'Reduced motion: no smooth scrolling')
        expect(page.locator('.memory-file').evaluate('(e)=>getComputedStyle(e).transitionDuration==="0s"'),'Reduced motion: no file animation')
        context.close();browser.close()
    expect(not errors,'No JavaScript errors');expect(not external,'No external requests needed to render')
    result={'passed':all(c['pass'] for c in checks),'checks':checks,'errors':errors,'external_requests':external}
    (out/'browser-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'checks':len(checks),'out':str(out),'failed':[c for c in checks if not c['pass']]}))
    return result['passed']

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();raise SystemExit(0 if run(a.root.resolve(),a.out.resolve()) else 1)
