import StringIO
import base64
import contextlib
import os

from PIL import Image

from dirmetadata.dirmetadata_mp3 import id3v2
from dirmetadata.dirmetadata_mp3.id3v2 import (_decode_track, 
    named_text_with_newlines)
from dirmetadata.dirmetadata_mp3.main import Mp3DirmetadataProvider


test_data_directory = r'D:\Hg\hsaudiotag\hsaudiotag\tests\testdata\id3v2'

class IGNORE:
    pass


@contextlib.contextmanager
def allow_text_tag(**override):
    oldvals = {}
    for key, value in override.iteritems():
        oldvals[key] = id3v2.frames_4.get(key, IGNORE)
        id3v2.frames_4[key] = named_text_with_newlines(value)
    
    try:
        yield
    
    finally:
        for key, value in oldvals.iteritems():
            if value is IGNORE:
                del id3v2.frames_4[key]
            else:
                id3v2.frames_4[key] = value

        

def process_file(filename, offset=0):
    if os.path.isfile(filename):
        full_name = filename
    
    else:
        full_name = os.path.join(test_data_directory, filename)
    
    with open(full_name, 'rb') as inp:
        file_data = inp.read()
    
    if offset:
        file_data = file_data[offset:]
    
    prov = Mp3DirmetadataProvider()
    readers = prov.data_generator(file_data)
    
    for r in readers:
        r(file_data)
    
    for r in readers:
        r('')
    
    tags = prov.data()
    return tags



def picture(size=None, mime_type=None, picture_type=None):

    def get_image_from_data(data):
        image_data = base64.b64decode(data)
        buf = StringIO.StringIO(image_data)
        image = Image.open(buf)
        return image


    def test(picture_data_list):
        assert 1 == len(picture_data_list)
        picture_data = picture_data_list[0]
        
        image = get_image_from_data(picture_data['image_data'])
        assert image is not None
        
        if mime_type is not None:
            assert mime_type == picture_data['mime_type']
        
        if size is not None:
            assert size == image.size
    
    return test


def expect_equal_dicts(expected, result):
    for key, expected_value in expected.items():
        if hasattr(expected_value, '__call__'):
            expected_value(result[key])
             
        elif expected_value is not IGNORE:
            assert expected_value == result[key], "Fail at {0}: expected {1!r}, got {2!r}".format(key, expected_value, result[key])
    
    assert set(expected.keys()) == set(result.keys())


def assert_tags(filename, **expected):
    tags = process_file(filename)
    
    assert 'id3v2' in tags, "No id3v2 tags"
    id3v2 = tags['id3v2']
    
    expect_equal_dicts(expected, id3v2)


def assert_tags_offset(filename, offset, **expected):
    tags = process_file(filename, offset)
    
    assert 'id3v2' in tags, "No id3v2 tags"
    id3v2 = tags['id3v2']
    
    expect_equal_dicts(expected, id3v2)



def test_normal():
    assert_tags('normal.mp3',
                    title=u'La Primavera',
                    artists=[u'Manu Chao'],
                    album=u'Proxima Estacion Esperanza (AD',
                    year=2001,
                    genre=u'Latin',
                    comments=[dict(language='eng', value=u'http://www.EliteMP3.ws')],
                )


def test_no_tag():
    tags = process_file('notag.mp3')
    assert tags is None or 'id3v2' not in tags, "Shouldn't have an id3v2 tags"


def test_that_spot():
    expected_comment = u"""THAT SPOT RIGHT THERE (14 second demo clip)

This 14 second demo clip was recorded at CD-Quality using the standard MusicMatch Jukebox
software program.  If you like this track, you can click the "Buy CD" button in your MusicMatch
Jukebox "Track Info" window, and you'll be connected to a recommended online music retailer.


Enjoy your copy of MusicMatch Jukebox!"""
        
    tags = process_file('thatspot.tag')
    inner = tags['id3v2']
    
    expect_equal_dicts(dict(
                        title=u'That Spot Right There',
                        artists=[u'Carey Bell'],
                        album=u'Mellow Down Easy',
                        genre=u'Blues',
                        comments=IGNORE,
                        duration=15.0,
                        track=0,
                        pictures=picture(size=(236, 238), picture_type=u'Other')
                    ),
                    inner)
    
    for comment in inner['comments']:
        if 'id' in comment and comment['language'] == u'eng':
                assert expected_comment == comment['value'].replace('\r','')


def test_ozzy():
    assert_tags('ozzy.tag',
                title=u'Bark At The Moon',
                artists=[u'Ozzy Osbourne'],
                album=u'Bark At The Moon',
                year=1983,
                genre=u'Metal',
                comments=IGNORE,
                duration=257.358,
                track=1,
                pictures=IGNORE, # APIC tag doesn't seem to contain valid image data
            )


def test_unicode():
    with allow_text_tag(TXXX='experimental'):
        assert_tags('230-unicode.tag',
                    experimental=u'example text frame\nThis text and the description should be in Unicode.'
                )


def test_with_footer():
    assert_tags_offset('with_footer.mp3', 25902,
                     artists=[u'AFI'],
                     album=u'Shut Your Mouth And Open Your',
                     title=u'06 - Third Season',
                     genre='Metal',
                     comments=IGNORE,
                )


def test_non_ascii_non_unicode():
    assert_tags('ozzy_non_ascii.tag',
                      album=u'Bark At The \u00c8\u00c9\u00ca\u00cb',
                      title=u'Bark At The \u00c8\u00c9\u00ca\u00cb',
                      artists=[u'Ozzy Osbourne'],
                      genre='Metal',
                      year=1983,
                      comments=IGNORE,
                      duration=257.358,
                      track=1,
                      pictures=IGNORE, # APIC tag doesn't seem to contain valid image data
                )


def test_numeric_genre():
    #A file with a genre field containing (<number>)
    assert_tags('numeric_genre.tag',
                    genre=u'Metal',
                    title=u'Die For Your Government', 
                    artists=[u'Antiflag'],
                )


def test_numeric_genre2():
    #A file with a genre field containing (<number>)
    assert_tags('numeric_genre2.tag',
                    genre=u'Rock',
                    album=u'Greatest Hits, Disc 1',
                    artists=[u'Queen'],
                    title=u'Seven Seas of Rhye',
                    comments=IGNORE,
                    track=15,
                )


def test_numeric_genre3():
    #like numeric_genre, but the number is not between ()
    assert_tags('numeric_genre3.tag',
                    genre=u'Rock',
                    album=u'Greatest Hits, Disc 1',
                    artists=[u'Queen'],
                    title=u'Seven Seas of Rhye',
                    comments=IGNORE,
                    track=15,
                )


def test_unicode_truncated():
    with allow_text_tag(TXXX='experimental'):
        assert_tags('230-unicode_truncated.tag',
                    experimental=u'example text frame\nThis text and the description should be in Unicode.'
                )


def test_unicode_invalid_surrogate():
    with allow_text_tag(TXXX='experimental'):
        assert_tags('230-unicode_surregate.tag',
                    experimental=u''
                )
        
        
def test_unicode_comment():
    assert_tags('230-unicode_comment.tag',
                     comments=[dict(id=u'example text frame', value=u'This text and the description should be in Unicode.')]
                )


def test_tlen():
    assert_tags('../mpeg/test8.mp3',
            duration=299.284,
            album=u'461 Ocean Boulevard',
            composers=[u'Eric Clapton'],
            title=u'Let It Grow',
            artists=[u'Eric Clapton'],
            year=1974,
            genre=u'Blues',
            track=8,
            pictures=picture(size=(200, 198), picture_type=u'Other')
        )


def test_track_decoding():
    assert (42, None) == _decode_track(u'42')
    assert (None, None) == _decode_track(u'')
    assert (12, 24) == _decode_track(u'12/24')
    assert (None, None) == _decode_track(u' ')
    assert (None, None) == _decode_track(u'/')
    assert (None, 12) == _decode_track(u'foo/12')
    assert (None, 24) == _decode_track(u'/24')
    assert (8, None) == _decode_track(u'8/')


def test_newlines():
    #like numeric_genre, but the number is not between ()
    assert_tags('newlines.tag',
                    title=u'foo bar baz',
                    artists=[u'foo bar baz'],
                    album=u'foo bar baz',
                    genre=u'foo bar baz',
                    comments=[dict(language='en', value=u'foo\nbar\rbaz')],
                    year=None,
                )


def test_version_22():
    assert_tags('v22.tag',
                     title=u'Chanson de Nuit - Op. 15 No. 1',
                     artists=[u'Kennedy', u'Pettinger'],
                     album=u'Salut d\'Amour (Elgar)',
                     track=5,
                     max_track=10,
                     year=1984,
                     genre=u'Classical',
                     composers=[u'Edward Elgar'],
                     comments=IGNORE,
                    )


def test_v24_no_syncsafe():
    #syncsafe is only for v2.4 and up.
    assert_tags('v24_no_syncsafe.tag',
                     title=u'Boccherini / Minuet (String Quartet in E major)',
                     album=u'Smooth Classics - disk 1',
                     track=8,
                     genre=u'Classical',
                     artists=[u'Classic FM'],
                     duration=203.293,
                     comments=IGNORE,
                )


def test_invalid_text_type():
    # invalid_text_type has a 0xff stringtype
    # Don't crash on invalid string types, just ignore the text
    with allow_text_tag(TXXX='experimental'):
        assert_tags('invalid_text_type.tag',
                    experimental=None,
                )


def test_invalid_comment_type():
    # invalid_comment_type has a 0xff stringtype
    # Don't crash on invalid string types, just ignore the text
    assert_tags('invalid_comment_type.tag') # don't crash


def test_picture_data():
    def test(picture_data):
        data = picture_data[u'Cover (front)']
        assert 'image/jpg' == data['mime_type']
        
        image_data = base64.b64decode(data['image_data'])

        image = Image.open(StringIO.StringIO(image_data))
        assert (1781, 1824) == image.size
        
    
    assert_tags(r'D:\metadata-testdata\MP3\pictures\04 - Jerusalem.mp3',
                    album=u'3rd Warning',
                    pictures=picture(size=(1781, 1824)),
                    comments=[dict(language=u'eng', value=u'')],
                    title=u'Jerusalem',
                    track=4,
                    artists=[u'Miriodor'],
                    year=1991,
                    genre=u'Avant-Prog',
                )
