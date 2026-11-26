import unittest,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
from forklift.visuals import metrics,figures

class VisualTests(unittest.TestCase):
    def test_metrics_and_svg(self):
        d={'files':[{'path':'src/a<&.py','size':12},{'path':'README','size':4}], 'commits':[{'date':'2026-01-01','changes':[{'path':'src/a<&.py','added':3,'deleted':2},{'path':'image','added':None,'deleted':None}]}], 'contributors':[{'name':'A & B','commits':1}], 'months':{'2026-01':1},'incidence':{'A':1,'B':1},'coupling':[{'a':'A','b':'B','count':1}]}
        m=metrics(d); self.assertEqual(m['directories'],{'src':12,'(root)':4}); self.assertEqual(m['monthly_churn']['2026-01'],[3,2,1]); self.assertEqual(m['churn']['src/a<&.py'],[3,2,0])
        with tempfile.TemporaryDirectory() as tmp:
            charts=figures(d,Path(tmp)); self.assertEqual(len(charts),6)
            for p in Path(tmp).glob('*.svg'): ET.parse(p)
