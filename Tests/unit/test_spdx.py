import unittest

import kss.license.spdx as spdx

class SPDXTestCase(unittest.TestCase):
    def test_get_entry(self):
        s = spdx.SPDX()
        self.assertTrue(s.get_entry('0BSD') is not None)
        self.assertEqual(s.get_entry('0BSD')['licenseId'], '0BSD')
        self.assertTrue(s.get_entry('notthere') is None)

    def test_search(self):
        s = spdx.SPDX()
        bsd3 = s.get_entry('BSD-3-Clause')
        self.assertTrue(bsd3 is not None)
        self.assertEqual(s.search('BSD-3-Clause'), bsd3)
        self.assertEqual(s.search('BSD 3-Clause "New" or "Revised" License'), bsd3)
        self.assertEqual(s.search('spdxBSD3'), bsd3)
        self.assertTrue(s.search('notthere') is None)
