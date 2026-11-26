import unittest
from xml.etree import ElementTree as ET
from forklift.visuals import svg, heatmap

class ReadabilityTest(unittest.TestCase):
    def test_chart_palette(self):
        ns={'s':'http://www.w3.org/2000/svg'}
        for chart in [svg('Test',[('path',1)],'Commits'),heatmap({'incidence':{'A':1},'coupling':[]})]:
            root=ET.fromstring(chart)
            self.assertEqual(root.find('s:rect',ns).get('fill'),'#ffffff')
            self.assertEqual(root.find('s:g',ns).get('fill'),'#000000')
            for label in root.findall('.//s:text',ns):
                self.assertGreaterEqual(int(label.get('font-size')),16)
