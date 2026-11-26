import unittest
from forklift.interactive import relationships, panel

class InteractiveTests(unittest.TestCase):
    def test_relationships_and_safe_payload(self):
        a='</script><script>alert(1)</script>'; b='b'; c='c'
        data={'files':[{'path':a,'size':3}], 'commits':[{'hash':'1','date':'2026-01-01','changes':[{'path':a},{'path':a},{'path':b,'old_path':c}]},{'hash':'2','date':'2026-01-02','changes':[{'path':a},{'path':b}]}]}
        r=relationships(data)
        self.assertEqual(r['edges'][0]['count'],2)
        self.assertEqual(r['edges'][0]['jaccard'],1)
        self.assertEqual(r['renames'][0]['old'],c)
        self.assertNotIn(a,panel(data,r))
        self.assertEqual(relationships(data,max_paths=1)['edges'],[])
        self.assertEqual(relationships({'commits':[]})['nodes'],[])
