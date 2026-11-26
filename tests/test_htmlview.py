import unittest
from forklift.htmlview import bars, page
from forklift.render import table
class HTMLViewTests(unittest.TestCase):
    def test_native_labels(self):
        path='long/'*100+'<file>&.tex'
        html=page('Test',bars('Size',[(path,0),('other',10)],'Bytes')+table('Numbers',['Value'],[(10,),(2,)]))
        self.assertIn('long/'*100+'&lt;file&gt;&amp;.tex',html)
        self.assertIn('width:0.0000%',html)
        self.assertIn('width:100.0000%',html)
        self.assertIn('data-number="10"',html)
        self.assertNotIn('<svg',html)
