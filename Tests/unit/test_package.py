import unittest

import kss.license


class LicensePackageTestCase(unittest.TestCase):
    def test_version(self):
        with open('REVISION', 'r') as infile:
            version = infile.read().strip()
        self.assertEqual(kss.license.__version__, version)
