from dirmetadata.dirmetadata_mp3.main import Mp3DirmetadataProvider
import os

test_data_directory = r'D:\Hg\hsaudiotag\hsaudiotag\tests\testdata\id3v1'


def process_file(filename):
    with open(os.path.join(test_data_directory, filename), 'rb') as inp:
        file_data = inp.read()
    
    prov = Mp3DirmetadataProvider()
    readers = prov.data_generator(file_data)
    
    for r in readers:
        r(file_data)
    
    for r in readers:
        r('')
    
    return prov.data()


def assert_tags(filename, **expected):
    tags = process_file(filename)
    
    assert 'id3v1' in tags
    id3v1 = tags['id3v1']
    
    for key, expected_value in expected.items():
        assert expected_value == id3v1[key]
    
    assert set(expected.keys()) == set(id3v1.keys())



def expect_no_id3v1(filename):
    tags = process_file(filename)
    assert 'id3v1' not in tags
    
    
def test_001():
    assert_tags("id3v1_001_basic.mp3", title="Title", artist="Artist", album="Album", year=2003, genre="Hip-Hop", comment="Comment")


def test_002():
    assert_tags("id3v1_002_basic.mp3", title="Title", artist="Artist", album="Album", year=2003, genre="Hip-Hop", comment="Comment", track=12)

        
def test_003():
    expect_no_id3v1("id3v1_003_basic_F.mp3")


def test_004():
    assert_tags("id3v1_004_basic.mp3", year=2003, genre="Blues")


def test_005():
    assert_tags("id3v1_005_basic.mp3", 
                 title="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaA",
                 artist="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbB",
                 album="cccccccccccccccccccccccccccccC",
                 year=2003,
                 genre="Blues",
                 comment="dddddddddddddddddddddddddddddD")
    

def test_006():
    assert_tags("id3v1_006_basic.mp3", 
                title="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaA",
                artist="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbB",
                album="cccccccccccccccccccccccccccccC",
                year=2003,
                genre="Blues",
                comment="dddddddddddddddddddddddddddD",
                track=1)


def test_007():
    assert_tags("id3v1_007_basic_W.mp3",
                title="12345",
                artist="12345",
                album="12345",
                year=2003,
                genre="Blues",
                comment="12345")


def test_008():
    assert_tags("id3v1_008_basic_W.mp3",
                title="12345",
                artist="12345",
                album="12345",
                year=2003,
                genre="Blues",
                comment="12345",
                track=1)


def test_009():
    # The original test assumed that the track number would be maxed at 99. I honestly can find no good reason for that
    assert_tags("id3v1_009_basic.mp3",
                  track=255,
                  year=2003,
                  genre="Blues")


def test_010():
    assert_tags("id3v1_010_year.mp3", year=0, genre="Blues")


def test_011():
    assert_tags("id3v1_011_year.mp3", year=9999, genre="Blues")


def test_012():
    assert_tags("id3v1_012_year_F.mp3", year=3, genre="Blues")


def test_013():
    assert_tags("id3v1_013_year_F.mp3", year=112, genre="Blues")


def test_014():
    assert_tags("id3v1_014_year_F.mp3", genre="Blues")


def test_genres():
    for i in range(15, 95):
        tags = process_file("id3v1_%03d_genre.mp3" % i)['id3v1']
        assert 'genre' in tags, "No 'genre' at %d" % i
        assert 'title' in tags, "No 'TITLE' at %d" % i
        assert tags['title'] == tags['genre'], "Failure at %d" % i
        
    for i in range(95, 163):
        tags = process_file("id3v1_%03d_genre_W.mp3" % i)['id3v1']
        assert 'genre' in tags, "No 'genre' at %d" % i
        assert 'title' in tags, "No 'TITLE' at %d" % i
        assert tags['title'] == tags['genre'], "Failure at %d" % i
        
    for i in range(163, 271):
        tags = process_file("id3v1_%03d_genre_F.mp3" % i)['id3v1']
        assert 'genre' in tags, "No 'genre' at %d" % i
        assert 'title' in tags, "No 'TITLE' at %d" % i
        assert tags['title'] == tags['genre'], "Failure at %d" % i


def test_zero():
    #test that id3v1 handle invalid files gracefully
    assert process_file('../zerofile') is None
    assert process_file('../randomfile') is None


def test_non_ascii():
    assert_tags('id3v1_non_ascii.mp3', 
                 title=u'Title\u00c8',
                 album='Album',
                 genre='Hip-Hop',
                 artist='Artist',
                 comment='Comment',
                 year=2003)


def test_crlf():
    assert_tags('id3v1_newlines.mp3',
                title='foo bar baz',
                artist='foo bar baz',
                album='foo bar baz',
                comment='foo bar baz',
                year=None, # Year will be illegal
                genre='Hip-Hop')




