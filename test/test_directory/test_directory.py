from os.path import dirname, join
import dirmetadata.directory as directory
import hashlib
import os
import unittest


class Test(unittest.TestCase):

    def setUp(self):
        self.path = join(dirname(__file__), 'testdata')
        self.sha = {}

        for name in os.listdir(self.path):
            with open(join(self.path, name), 'rb') as inp:
                self.sha[name] = hashlib.sha1(inp.read()).hexdigest()



    def test_hash_65536(self):
        directory.DirectoryMetaData.FILE_BLOCK_SIZE_LIMIT = 65536
        self._test_sha1()


    def test_hash_100000000(self):
        directory.DirectoryMetaData.FILE_BLOCK_SIZE_LIMIT = 100000000
        self._test_sha1()


    def test_hash_20(self):
        directory.DirectoryMetaData.FILE_BLOCK_SIZE_LIMIT = 20
        self._test_sha1()


    def _test_sha1(self):
        dd = directory.read_directory(self.path)
        self.assertEqual(len(self.sha), len(dd._data))
        for name in self.sha:
            self.assertEqual(self.sha[name], dd[name]['file']['sha1'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
