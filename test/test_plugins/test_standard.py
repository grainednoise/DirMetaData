import dirmetadata
import unittest

print dirmetadata


class PluginTest2(unittest.TestCase):

    def test_discovery2(self):
        if dirmetadata.main.dirmetadata_providers:
            raise Exception("System is already initialised, can't run test")
        
        import dirmetadata.dirmetadata_mp3 as dirmetadata_mp3 #@UnusedImport
        
        print dirmetadata.main.dirmetadata_providers
        
        self.assertTrue("mp3" in dirmetadata.main.dirmetadata_providers)
        
    
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_discovery']
    unittest.main()