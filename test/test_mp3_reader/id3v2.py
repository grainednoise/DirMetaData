from dirmetadata.dirmetadata_mp3.main import Mp3DirmetadataProvider
import os
import unittest
from dirmetadata.dirmetadata_mp3 import id3v2
from dirmetadata.dirmetadata_mp3.id3v2 import named_text, _decode_track
import contextlib



test_data_directory = r'D:\Hg\hsaudiotag\hsaudiotag\tests\testdata\id3v2'

class IGNORE:
    pass


@contextlib.contextmanager
def allow_text_tag(**override):
    oldvals = {}
    for key, value in override.iteritems():
        oldvals[key] = id3v2.frames_4.get(key, IGNORE)
        id3v2.frames_4[key] = named_text(value)
    
    try:
        yield
    
    finally:
        for key, value in oldvals.iteritems():
            if value is IGNORE:
                del id3v2.frames_4[key]
            else:
                id3v2.frames_4[key] = value

        
    
class Id3V2Test(unittest.TestCase):
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
            if expected_value is not IGNORE:
                print repr(expected_value)
                print repr(result[key])
                self.assertEqual(expected_value, result[key], "Fail at {0}: expected {1!r}, got {2!r}".format(key, expected_value, result[key]))
        
        self.assertSetEqual(set(expected.keys()), set(result.keys()))


    def assert_tags(self, filename, **expected):
        tags = self.process_file(filename)
        
        self.assertTrue('id3v2' in tags, "No id3v2 tags")
        id3v2 = tags['id3v2']
        
        self.expect_equal_dicts(expected, id3v2)



    def test_normal(self):
        self.assert_tags('normal.mp3',
                        title=u'La Primavera',
                        artists=[u'Manu Chao'],
                        album=u'Proxima Estacion Esperanza (AD',
                        year=2001,
                        genre=u'Latin',
                        comment={'eng': u'http://www.EliteMP3.ws'},
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
        inner['comment'] = inner['comment'][u'eng'].replace('\r','')
        self.maxDiff = None
        
        self.expect_equal_dicts(dict(
                            title=u'That Spot Right There',
                            artists=[u'Carey Bell'],
                            album=u'Mellow Down Easy',
                            genre=u'Blues',
                            comment=expected_comment,
                            comment_ids=IGNORE,
                            duration=15.0,
                            track=0,
                        ),
                        inner)


    def test_ozzy(self):
        self.assert_tags('ozzy.tag',
                        title=u'Bark At The Moon',
                        artists=[u'Ozzy Osbourne'],
                        album=u'Bark At The Moon',
                        year=1983,
                        genre=u'Metal',
                        comment_ids=IGNORE,
                        duration=257.358,
                        track=1,
                    )


    def test_unicode(self):
        with allow_text_tag(TXXX='experimental'):
            self.assert_tags('230-unicode.tag',
                        experimental=u'example text frame\nThis text and the description should be in Unicode.'
                    )


    def test_with_footer(self):
        self.assert_tags('with_footer.mp3',
                         artists=[u'AFI'],
                         album=u'Shut Your Mouth And Open Your',
                         title=u'06 - Third Season',
                         genre='Metal',
                         comment_ids=IGNORE,
                    )


    def test_non_ascii_non_unicode(self):
        self.assert_tags('ozzy_non_ascii.tag',
                          album=u'Bark At The \u00c8\u00c9\u00ca\u00cb',
                          title=u'Bark At The \u00c8\u00c9\u00ca\u00cb',
                          artists=[u'Ozzy Osbourne'],
                          genre='Metal',
                          year=1983,
                          comment_ids=IGNORE,
                          duration=257.358,
                          track=1,
                    )


    def test_numeric_genre(self):
        #A file with a genre field containing (<number>)
        self.assert_tags('numeric_genre.tag',
                        genre=u'Metal',
                        title=u'Die For Your Government', 
                        artists=[u'Antiflag'],
                    )
    
    
    def test_numeric_genre2(self):
        #A file with a genre field containing (<number>)
        self.assert_tags('numeric_genre2.tag',
                        genre=u'Rock',
                        album=u'Greatest Hits, Disc 1',
                        artists=[u'Queen'],
                        title=u'Seven Seas of Rhye',
                        comment=IGNORE,
                        comment_ids=IGNORE,
                        track=15,
                    )
    
    
    def test_numeric_genre3(self):
        #like numeric_genre, but the number is not between ()
        self.assert_tags('numeric_genre3.tag',
                        genre=u'Rock',
                        album=u'Greatest Hits, Disc 1',
                        artists=[u'Queen'],
                        title=u'Seven Seas of Rhye',
                        comment=IGNORE,
                        comment_ids=IGNORE,
                        track=15,
                    )


    def test_unicode_truncated(self):
        with allow_text_tag(TXXX='experimental'):
            self.assert_tags('230-unicode_truncated.tag',
                        experimental=u'example text frame\nThis text and the description should be in Unicode.'
                    )


    def test_unicode_invalid_surrogate(self):
        with allow_text_tag(TXXX='experimental'):
            self.assert_tags('230-unicode_surregate.tag',
                        experimental=u''
                    )
            
    def test_unicode_comment(self):
        self.assert_tags('230-unicode_comment.tag',
                         comment_ids={u'example text frame': {u'': u'This text and the description should be in Unicode.'}}
                    )

    def test_tlen(self):
        self.assert_tags('../mpeg/test8.mp3',
                duration=299.284,
                album=u'461 Ocean Boulevard',
                composers=[u'Eric Clapton'],
                title=u'Let It Grow',
                artists=[u'Eric Clapton'],
                year=1974,
                genre=u'Blues',
                track=8,
            )


    def test_track_decoding(self):
        self.assertEqual((42, None), _decode_track(u'42'))
        self.assertEqual((None, None), _decode_track(u''))
        self.assertEqual((12, 24), _decode_track(u'12/24'))
        self.assertEqual((None, None), _decode_track(u' '))
        self.assertEqual((None, None), _decode_track(u'/'))
        self.assertEqual((None, 12), _decode_track(u'foo/12'))
        self.assertEqual((None, 24), _decode_track(u'/24'))
        self.assertEqual((8, None), _decode_track(u'8/'))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()