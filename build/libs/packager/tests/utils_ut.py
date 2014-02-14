#!/usr/bin/env python
""" Unit tests for utils module """

import os
import sys
import unittest

sys.path.append(os.path.dirname(os.getcwd()))
import utils

class UtilsTests(unittest.TestCase):
    """ Unit tests for Utils class """
    def setUp(self):
        self.utils_obj = utils.Utils()

    def test_check_package_md5_empty_location(self):
        """ Test with empty value for location key """
        pkginfo = {'test-pkg' : {'location': ''}}
        self.assertRaises(RuntimeError, self.utils_obj.check_package_md5,
                         (pkginfo))

    def test_check_package_md5_file_not_found(self):
        """ Test get md5 for non existent file """
        pkginfo = {'test-pkg' : {'location': '/cs-shared/builder/cache/',
                                 'file': 'not-found-pkg'}}
        self.assertRaises(RuntimeError, self.utils_obj.check_package_md5,
                          (pkginfo))

    def test_check_package_md5_file_found(self):
        """ Test get md5 for existing file """
        pkginfo = {'test-pkg' : {'md5': '8375adaa4a86788091f6cd29a3b212bc',
                     'location': '/cs-shared/builder/cache/ubuntu1204/havana/',
                     'file': 'libsslcommon2_0.14-2_amd64.deb'}}
        self.assertEqual(None, self.utils_obj.check_package_md5(pkginfo))



if __name__ == "__main__":
    unittest.main()
