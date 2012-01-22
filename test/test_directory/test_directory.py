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
        dd = directory.read_directory(self.path)
        print(dd)
        print(dd._data)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()