import unittest
import os

import kss.license.util as util


class SPDXTestCase(unittest.TestCase):
    def test_get_entry(self):
        s = util.SPDX()
        self.assertTrue(s.get_entry('0BSD') is not None)
        self.assertEqual(s.get_entry('0BSD')['licenseId'], '0BSD')
        self.assertTrue(s.get_entry('notthere') is None)

    def test_search(self):
        s = util.SPDX()
        bsd3 = s.get_entry('BSD-3-Clause')
        self.assertTrue(bsd3 is not None)
        self.assertEqual(s.search('BSD-3-Clause'), bsd3)
        self.assertEqual(s.search('BSD 3-Clause "New" or "Revised" License'), bsd3)
        self.assertEqual(s.search('BSD3'), bsd3)
        self.assertTrue(s.search('notthere') is None)


class OtherUtilTestCase(unittest.TestCase):
    def test_find_all(self):
        all = util.find_all('file1.dat')
        self.assertEqual(len(all), 4)
        self.assertTrue("Tests/unit/TestData/dir1/dir11/file1.dat" in all)
        self.assertTrue("Tests/unit/TestData/dir1/file1.dat" in all)
        self.assertTrue("Tests/unit/TestData/dir2/dir21/file1.dat" in all)
        self.assertTrue("Tests/unit/TestData/dir2/dir22/file1.dat" in all)

        all = util.find_all('file1.dat', skipprefix='Tests/')
        self.assertEqual(len(all), 0)

        all = util.find_all('file1.dat', directory='Tests/unit/TestData')
        self.assertEqual(len(all), 4)
        self.assertTrue("dir1/dir11/file1.dat" in all)
        self.assertTrue("dir1/file1.dat" in all)
        self.assertTrue("dir2/dir21/file1.dat" in all)
        self.assertTrue("dir2/dir22/file1.dat" in all)

        all = util.find_all('file1.dat', directory='Tests/unit/TestData', skipprefix='Tests/')
        self.assertEqual(len(all), 4)
        self.assertTrue("dir1/dir11/file1.dat" in all)
        self.assertTrue("dir1/file1.dat" in all)
        self.assertTrue("dir2/dir21/file1.dat" in all)
        self.assertTrue("dir2/dir22/file1.dat" in all)

        all = util.find_all('testdir', isdir=True)
        self.assertEqual(len(all), 2)
        self.assertTrue("Tests/unit/TestData/dir1/testdir" in all)
        self.assertTrue("Tests/unit/TestData/dir2/dir21/testdir" in all)

        all = util.find_all('testdir', directory='Tests/unit/TestData', isdir=True)
        self.assertEqual(len(all), 2)
        self.assertTrue("dir1/testdir" in all)
        self.assertTrue("dir2/dir21/testdir" in all)
