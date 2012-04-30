from os.path import dirname, join, exists
import dirmetadata.directory as directory
import os
import unittest



class Test(unittest.TestCase):

    def setUp(self):
        self.path = join(dirname(__file__), 'testdata')
        self.metadata_path = join(self.path, '.dirmetadata')
        self.delete_metadata()

    
    def tearDown(self):
        self.delete_metadata()
    
    
    def delete_metadata(self):
        if exists(self.metadata_path):
            os.remove(self.metadata_path)
    
        

    def test_read_write(self):
        self.assertFalse(exists(self.metadata_path ))
        
        dd = directory.read_directory(self.path)
        original_names =  dd.names()
        original_data = {}
        
        for name in original_names:
            data = dd[name]
            self.assertTrue(data['file']['updated'])
            del data['file']['updated']
            
            self.assertTrue('updated' in dd[name]['file'])  # Should not affect internal data
            
            original_data[name] = data
        
        
        dd.write_if_updated()
        
        self.assertTrue(exists(join(self.path, '.dirmetadata')))
        
        
        dd2 = directory.read_directory(self.path) 
        
        self.assertEqual(original_names, dd2.names())
        
        for name in original_names:
            data = dd2[name]
            self.assertFalse(data['file']['updated'])
            del data['file']['updated']
            self.assertEqual(original_data[name], data)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()