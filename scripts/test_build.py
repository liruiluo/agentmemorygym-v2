#!/usr/bin/env python3
"""Isolated regressions for generation, publication wiring and visual fail-safes."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from pptx import Presentation
from pptx.util import Inches
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validate_artifacts',ROOT/'scripts/validate_artifacts.py')
validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='campii-build-test-')
        self.root=Path(self.tmp.name)/'site'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('.git','__pycache__'))
    def tearDown(self):self.tmp.cleanup()
    def call(self,script,*args):
        return subprocess.run([sys.executable,str(self.root/'scripts'/script),*args],cwd=self.root,capture_output=True,text=True)
    def test_static_site_is_reproducible(self):
        old=(self.root/'index.html').read_bytes()
        self.assertEqual(self.call('build_website.py').returncode,0)
        self.assertEqual(old,(self.root/'index.html').read_bytes())
    def test_bad_identifier_never_modifies_data(self):
        old=(self.root/'data/research.json').read_bytes()
        for aid in ['TBD','https://arxiv.org/abs/2612.01234','2613.01234','2612.01234<script>','2612.01234v0']:
            with self.subTest(aid=aid):
                self.assertNotEqual(self.call('set_arxiv_id.py',aid).returncode,0)
                self.assertEqual(old,(self.root/'data/research.json').read_bytes())
    def test_identifier_reaches_all_current_surfaces(self):
        p=self.call('set_arxiv_id.py','2612.01234v2');self.assertEqual(p.returncode,0,p.stderr)
        html=(self.root/'index.html').read_text()
        self.assertEqual(html.count('https://arxiv.org/abs/2612.01234v2'),3)
        self.assertIn('eprint = {2612.01234v2}',html);self.assertIn('Paper on arXiv',html)
        ppt=Presentation(self.root/'assets/slides/campii-slides.pptx')
        links=[r.hyperlink.address for s in ppt.slides for b in s.shapes if b.has_text_frame for p in b.text_frame.paragraphs for r in p.runs]
        self.assertIn('https://arxiv.org/abs/2612.01234v2',links)
    def test_table_tampering_is_rejected(self):
        self.assertTrue(validator.check(self.root)['passed'], 'Positive control must pass before tampering')
        p=self.root/'index.html';s=p.read_text();self.assertIn('<td>64.6</td>',s)
        p.write_text(s.replace('<td>64.6</td>','<td>66.4</td>',1))
        result=validator.check(self.root)
        self.assertFalse(result['passed'])
        self.assertTrue(any('table cell' in c['check'] and not c['pass'] for c in result['checks']))
    def test_wrapped_numeric_label_is_rejected(self):
        self.assertTrue(validator.check(self.root)['passed'], 'Positive control must pass before narrowing')
        path=self.root/'assets/slides/campii-slides.pptx';ppt=Presentation(path)
        values=[b for b in ppt.slides[9].shapes if b.has_text_frame and b.text=='76.5']
        self.assertEqual(len(values),1);values[0].width=Inches(.40);ppt.save(path)
        p=self.call('render_slides_pdf.py','assets/slides/campii-slides.pptx','assets/slides/campii-slides.pdf')
        self.assertIn('"pages": 15',p.stdout,p.stderr)
        result=validator.check(self.root)
        self.assertFalse(result['passed']);self.assertTrue(result['numeric_wraps'])

if __name__=='__main__':unittest.main(verbosity=2)
