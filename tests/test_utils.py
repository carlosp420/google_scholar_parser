import os
import unittest

from BeautifulSoup import BeautifulSoup

from parser.scholar_cites import get_total_hits


DATA_PATH = os.path.join(os.path.dirname(__file__), "Data")


class TestUtils(unittest.TestCase):
    def test_getting_total_hits(self):
        with open(os.path.join(DATA_PATH, 'page.html'), "r") as handle:
            html = handle.read()
        soup = BeautifulSoup(html)
        expected = u'21'
        result = get_total_hits(soup)
        self.assertEqual(expected, result)
