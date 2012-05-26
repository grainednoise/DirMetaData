# -*- coding: utf-8 -*-

import unittest
import os.path

from dirmetadata.readers import FileSystemDirectoryReader
import datetime


class Test(unittest.TestCase):


    def setUp(self):
        self.test_directory = os.path.abspath(os.path.join(__file__, '..', '..', 'testdata'))
        assert os.path.isdir(self.test_directory)
        self.reader = FileSystemDirectoryReader('test', None, self.test_directory)


    def tearDown(self):
        pass


    def test_not_empty_files(self):
        expected = set(['Lyrical Ballads 1798.txt', 'pg19033-images.epub'])
        self.assertEqual(expected, set(self.reader.files()))


    def test_attributes(self):
        result = self.reader.get_file_info('Lyrical Ballads 1798.txt')
        print result
        self.assertEqual(151549, result['size'])
        self.assertEqual(0o100666, result['mode'])
        # 8 January 2012 12:27:56
        self.assertEqual(datetime.datetime(2012, 1, 8, 12, 27, 56), datetime.datetime.fromtimestamp(result['created']).replace(microsecond=0))
        # ‎26 ‎May ‎2012, ‏‎10:42:27
        self.assertEqual(datetime.datetime(2012, 5, 26, 10, 42, 27), datetime.datetime.fromtimestamp(result['modified']).replace(microsecond=0))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
