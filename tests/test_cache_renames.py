import tempfile, unittest, subprocess
from pathlib import Path
from forklift.analysis import analyze
from forklift.cache import cached_analyze
from forklift.collection import collection

class CacheRenameTests(unittest.TestCase):
    def test_cache_and_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); repo=p/'repo'; repo.mkdir()
            def g(*args): return subprocess.check_output(['git','-C',str(repo),*args])
            g('init','-q'); g('config','user.name','Fixture'); g('config','user.email','fixture@example.org')
            (repo/'old.md').write_text('hello\n'); g('add','.'); g('commit','-qm','root')
            g('mv','old.md','new.py'); g('commit','-qm','rename')
            a=analyze(repo,renames=True); self.assertEqual(a['commits'][0]['changes'],[dict(path='new.py',old_path='old.md',added=0,deleted=0)])
            self.assertEqual(len(analyze(repo)['commits'][0]['changes']),2)
            db=p/'cache.sqlite'; first=cached_analyze(repo,cache=db,renames=True); second=cached_analyze(repo,cache=db,renames=True)
            self.assertFalse(first['cache_hit']); self.assertTrue(second['cache_hit']); self.assertEqual(first['commits'],second['commits'])
            self.assertFalse(cached_analyze(repo,cache=db)['cache_hit'])
            g('commit','--allow-empty','-qm','new'); self.assertFalse(cached_analyze(repo,cache=db,renames=True)['cache_hit'])
            other=p/'other'; subprocess.check_call(['git','clone','-q',str(repo),str(other)])
            rows,errors=collection([repo,other],p/'report',cache=db,jobs=2,renames=True)
            self.assertEqual(len(rows),2); self.assertFalse(errors)
            self.assertIn('color-scheme:light',(p/'report/index.html').read_text())
