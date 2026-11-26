import unittest, tempfile, subprocess, xml.etree.ElementTree as ET
from pathlib import Path
from forklift.history import snapshots
from forklift.extra import calendar, growth, distribution, explorer
class ExtraTests(unittest.TestCase):
    def test_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            def git(*args): return subprocess.check_output(['git','-C',tmp,*args],stderr=subprocess.DEVNULL)
            git('init'); git('config','user.name','Test'); git('config','user.email','test@example.org')
            for i in range(1,5):
                Path(tmp,'file').write_bytes(b'x'*i); git('add','.'); git('commit','-m',str(i))
            rows=snapshots(tmp,'HEAD',limit=2)
            self.assertEqual([r['bytes'] for r in rows],[1,4]); self.assertEqual([r['files'] for r in rows],[1,1]); ET.fromstring(growth(rows,'bytes'))
    def test_visuals(self):
        ET.fromstring(calendar({'2026-01-01':5})); self.assertIn('&lt;',explorer([{'path':'a/<b','size':3}]))
        self.assertEqual(distribution({'commits':[{'changes':[{'added':5,'deleted':6}]}]})['11–100'],1)
