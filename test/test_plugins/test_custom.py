from os.path import join, dirname
import dirmetadata
import unittest


class PluginTest1(unittest.TestCase):


    def test_discovery(self):
        if dirmetadata.main.dirmetadata_providers:
            raise Exception("System is already initialised, can't run test")
        
        dirmetadata.main.enable_plugin_paths([join(dirname(__file__), 'plugins')])
        
        print dirmetadata.main.dirmetadata_providers
        
        self.assertTrue("dummy" in dirmetadata.main.dirmetadata_providers)
        
    
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_discovery']
    unittest.main()