from dirmetadata.dirmetadata_mp3.main import Mp3DirmetadataProvider
import os
import unittest

test_data_directory = r'D:\Hg\hsaudiotag\hsaudiotag\tests\testdata\id3v1'


class TestCase(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        

    def process_file(self, filename):
        with open(os.path.join(test_data_directory, filename), 'rb') as inp:
            file_data = inp.read()
        
        prov = Mp3DirmetadataProvider()
        readers = prov.data_generator(file_data)
        
        for r in readers:
            r(file_data)
        
        for r in readers:
            r('')
        
        return prov.data()


    def assert_tags(self, filename, **expected):
        tags = self.process_file(filename)
        
        self.assertTrue('id3v1' in tags)
        id3v1 = tags['id3v1']
        
        for key, expected_value in expected.items():
            self.assertEqual(expected_value, id3v1[key])
        
        self.assertSetEqual(set(expected.keys()), set(id3v1.keys()))



    def expect_no_id3v1(self, filename):
        tags = self.process_file(filename)
        self.assertFalse('id3v1' in tags)
    
    
    def test001(self):
        self.assert_tags("id3v1_001_basic.mp3", title="Title", artist="Artist", album="Album", year=2003, genre="Hip-Hop", comment="Comment")


    def test002(self):
        self.assert_tags("id3v1_002_basic.mp3", title="Title", artist="Artist", album="Album", year=2003, genre="Hip-Hop", comment="Comment", track=12)

            
    def test003(self):
        self.expect_no_id3v1("id3v1_003_basic_F.mp3")


    def test004(self):
        self.assert_tags("id3v1_004_basic.mp3", year=2003, genre="Blues")

    
    def test005(self):
        self.assert_tags("id3v1_005_basic.mp3", 
                         title="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaA",
                         artist="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbB",
                         album="cccccccccccccccccccccccccccccC",
                         year=2003,
                         genre="Blues",
                         comment="dddddddddddddddddddddddddddddD")
        
    
    def test006(self):
        self.assert_tags("id3v1_006_basic.mp3", 
                        title=  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaA",
                        artist= "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbB",
                        album=  "cccccccccccccccccccccccccccccC",
                        year=   2003,
                        genre=  "Blues",
                        comment="dddddddddddddddddddddddddddD",
                        track=  1)


    def test007(self):
        self.assert_tags("id3v1_007_basic_W.mp3",
                        title=  "12345",
                        artist= "12345",
                        album=  "12345",
                        year=   2003,
                        genre=  "Blues",
                        comment="12345")
    
    
    def test008(self):
        self.assert_tags("id3v1_008_basic_W.mp3",
                        title=  "12345",
                        artist= "12345",
                        album=  "12345",
                        year=   2003,
                        genre=  "Blues",
                        comment="12345",
                        track=1)
    
    
    def test009(self):
        # The original test assumed that the track number would be maxed at 99. I honestly can find no good reason for that
        self.assert_tags("id3v1_009_basic.mp3",
                          track=255,
                          year=2003,
                          genre="Blues")
    
    
    def test010(self):
        self.assert_tags("id3v1_010_year.mp3", year=0, genre="Blues")
    
    
    def test011(self):
        self.assert_tags("id3v1_011_year.mp3", year=9999, genre="Blues")


    def test012(self):
        self.assert_tags("id3v1_012_year_F.mp3", year=3, genre="Blues")
    
    
    def test013(self):
        self.assert_tags("id3v1_013_year_F.mp3", year=112, genre="Blues")
    
    
    def test014(self):
        self.assert_tags("id3v1_014_year_F.mp3", genre="Blues")


    def testgenres(self):
        for i in range(15, 95):
            tags = self.process_file("id3v1_%03d_genre.mp3" % i)['id3v1']
            self.assertTrue('genre' in tags, "No 'genre' at %d" % i)
            self.assertTrue('title' in tags, "No 'TITLE' at %d" % i)
            self.assertEqual(tags['title'], tags['genre'], "Failure at %d" % i)
            
        for i in range(95, 163):
            tags = self.process_file("id3v1_%03d_genre_W.mp3" % i)['id3v1']
            self.assertTrue('genre' in tags, "No 'genre' at %d" % i)
            self.assertTrue('title' in tags, "No 'TITLE' at %d" % i)
            self.assertEqual(tags['title'], tags['genre'], "Failure at %d" % i)
            
        for i in range(163, 271):
            tags = self.process_file("id3v1_%03d_genre_F.mp3" % i)['id3v1']
            self.assertTrue('genre' in tags, "No 'genre' at %d" % i)
            self.assertTrue('title' in tags, "No 'TITLE' at %d" % i)
            self.assertEqual(tags['title'], tags['genre'], "Failure at %d" % i)


    def testzero(self):
        #test that id3v1 handle invalid files gracefully
        self.expect_no_id3v1('../zerofile')
        self.expect_no_id3v1('../randomfile')


    def test_non_ascii(self):
        self.assert_tags('id3v1_non_ascii.mp3', 
                         title=u'Title\u00c8',
                         album='Album',
                         genre='Hip-Hop',
                         artist='Artist',
                         comment='Comment',
                         year=2003)


    def test_crlf(self):
        self.assert_tags('id3v1_newlines.mp3',
                        title='foo bar baz',
                        artist='foo bar baz',
                        album='foo bar baz',
                        comment='foo bar baz',
                        year=None, # Year will be illegal
                        genre='Hip-Hop')
    

if __name__ == '__main__':
    unittest.main()

