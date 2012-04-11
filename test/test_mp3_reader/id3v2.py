from dirmetadata.dirmetadata_mp3.main import Mp3DirmetadataProvider
import os
import unittest

test_data_directory = r'D:\Hg\hsaudiotag\hsaudiotag\tests\testdata\id3v2'


class Test(unittest.TestCase):
    def process_file(self, filename):
        with open(os.path.join(test_data_directory, filename), 'rb') as inp:
            file_data = inp.read()
        
        prov = Mp3DirmetadataProvider()
        readers = prov.data_generator(file_data)
        
        for r in readers:
            r(file_data)
        
        for r in readers:
            r('')
        
        tags = prov.data()
        return tags
    



    def expect_equal_dicts(self, expected, result):
        for key, expected_value in expected.items():
            print repr(expected_value)
            print repr(result[key])
            self.assertEqual(expected_value, result[key], "Fail at {0}".format(key))
        
        self.assertSetEqual(set(expected.keys()), set(result.keys()))


    def assert_tags(self, filename, **expected):
        tags = self.process_file(filename)
        
        self.assertTrue('id3v2' in tags, "No id3v2 tags")
        id3v2 = tags['id3v2']
        
        self.expect_equal_dicts(expected, id3v2)



    def testNormal(self):
        self.assert_tags('normal.mp3',
                        title=u'La Primavera',
                        artists=[u'Manu Chao'],
                        album=u'Proxima Estacion Esperanza (AD',
                        year=2001,
                        genre=u'Latin',
                        comment={u'': {'eng': u'http://www.EliteMP3.ws'}},
                    )


    def test_no_tag(self):
        tags = self.process_file('notag.mp3')
        self.assertFalse('id3v2' in tags, "Shouldn't have an id3v2 tags")


    def test_that_spot(self):
        expected_comment = u"""THAT SPOT RIGHT THERE (14 second demo clip)

This 14 second demo clip was recorded at CD-Quality using the standard MusicMatch Jukebox
software program.  If you like this track, you can click the "Buy CD" button in your MusicMatch
Jukebox "Track Info" window, and you'll be connected to a recommended online music retailer.


Enjoy your copy of MusicMatch Jukebox!"""
        
        tags = self.process_file('thatspot.tag')
        inner = tags['id3v2']
        inner['comment'] = inner['comment'][u''][u'eng'].replace('\r','')
        
        self.maxDiff = None
        
        self.expect_equal_dicts(dict(
                            title=u'That Spot Right There',
                            artists=[u'Carey Bell'],
                            album=u'Mellow Down Easy',
                            genre=u'Blues',
                            comment=expected_comment
                        ),
                        tags['id3v2'])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()