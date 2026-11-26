import tempfile, unittest, subprocess, json
from pathlib import Path
from xml.etree import ElementTree
from forklift.collection import discover, collection
from forklift.artifacts import artifacts, treemap
class CollectionTest(unittest.TestCase):
    def test_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('a','b'):
                p=root/name; p.mkdir()
                def g(*args): return subprocess.check_output(['git','-C',str(p),*args])
                g('init','-q'); g('config','user.name','Test'); g('config','user.email','test@example.org'); (p/'a.tex').write_text('abc'); g('add','.'); g('commit','-qm','root')
            self.assertEqual(len(discover(root,1)),2); self.assertEqual(discover(root,0),[])
            rows,errors=collection(discover(root),root/'out',True)
            self.assertFalse(errors); self.assertEqual(sum(r['bytes'] for r in rows),6)
            self.assertTrue(all((root/'out'/r['report']).exists() for r in rows))
            self.assertEqual(len(json.loads((root/'out/collection.json').read_text())['repositories']),2)
            html=(root/'out/index.html').read_text()
            self.assertNotIn('<svg',html)
            self.assertIn('class="bar-fill"',html)
            self.assertTrue((root/'out/images/commits.svg').exists())
    def test_artifacts(self):
        files=[{'path':'a&b/x.tex','size':10},{'path':'x.aux','size':5},{'path':'empty','size':0}]
        self.assertEqual(sum(v['bytes'] for v in artifacts(files).values()),15)
        self.assertEqual(artifacts(files)['Likely generated']['bytes'],5)
        ElementTree.fromstring(treemap(files)); ElementTree.fromstring(treemap([]))
