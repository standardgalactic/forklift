import tempfile,subprocess,unittest
from pathlib import Path
from forklift.analysis import analyze
from forklift.render import write_report

class TestAnalysis(unittest.TestCase):
    def test_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            def g(*args): return subprocess.check_output(['git','-C',tmp,*args])
            g('init','-q'); g('config','user.name','Fixture'); g('config','user.email','fixture@example.org')
            (p/'README.md').write_text('one\n'); g('add','.'); g('commit','-qm','root'); base=g('rev-parse','HEAD').decode().strip()
            (p/'README.md').write_text('one\ntwo\n'); (p/'package.json').write_text('{}\n'); g('add','.'); g('commit','-qm','second')
            before=g('status','--porcelain'); data=analyze(p)
            self.assertEqual(data['summary']['commits'],int(g('rev-list','--count','HEAD')))
            self.assertEqual(data['summary']['files'],2); self.assertEqual(data['summary']['bytes'],11)
            self.assertEqual(data['incidence'],{'Dependencies and packaging':1,'Documentation':2})
            self.assertEqual(data['coupling'][0]['count'],1)
            self.assertEqual(analyze(p,base=base)['summary']['commits'],1)
            self.assertEqual(g('status','--porcelain'),before)
            write_report(data,p/'report'); self.assertTrue((p/'report/index.html').exists())

            html=(p/'report/index.html').read_text()
            self.assertNotIn('<svg',html)
            self.assertIn('class="bar-fill"',html)
            self.assertIn('color-scheme:light dark',html)
            self.assertIn('File coupling (retained pairs)',html)
            self.assertTrue((p/'report/images/activity.svg').exists())
