import string


GENRE_NAMES = (
        u"Blues",
        u"Classic Rock",
        u"Country",
        u"Dance",
        u"Disco",
        u"Funk",
        u"Grunge",
        u"Hip-Hop",
        u"Jazz",
        u"Metal",
        u"New Age",
        u"Oldies",
        u"Other",
        u"Pop",
        u"R&B",
        u"Rap",
        u"Reggae",
        u"Rock",
        u"Techno",
        u"Industrial",
        u"Alternative",
        u"Ska",
        u"Death Metal",
        u"Pranks",
        u"Soundtrack",
        u"Euro-Techno",
        u"Ambient",
        u"Trip-Hop",
        u"Vocal",
        u"Jazz+Funk",
        u"Fusion",
        u"Trance",
        u"Classical",
        u"Instrumental",
        u"Acid",
        u"House",
        u"Game",
        u"Sound Clip",
        u"Gospel",
        u"Noise",
        u"AlternRock",
        u"Bass",
        u"Soul",
        u"Punk",
        u"Space",
        u"Meditative",
        u"Instrumental Pop",
        u"Instrumental Rock",
        u"Ethnic",
        u"Gothic",
        u"Darkwave",
        u"Techno-Industrial",
        u"Electronic",
        u"Pop-Folk",
        u"Eurodance",
        u"Dream",
        u"Southern Rock",
        u"Comedy",
        u"Cult",
        u"Gangsta",
        u"Top 40",
        u"Christian Rap",
        u"Pop/Funk",
        u"Jungle",
        u"Native American",
        u"Cabaret",
        u"New Wave",
        u"Psychadelic",
        u"Rave",
        u"Showtunes",
        u"Trailer",
        u"Lo-Fi",
        u"Tribal",
        u"Acid Punk",
        u"Acid Jazz",
        u"Polka",
        u"Retro",
        u"Musical",
        u"Rock & Roll",
        u"Hard Rock",

        # Winamp additions 
        u"Folk",
        u"Folk-Rock",
        u"National Folk",
        u"Swing",
        u"Fast Fusion",
        u"Bebob",
        u"Latin",
        u"Revival",
        u"Celtic",
        u"Bluegrass",
        u"Avantgarde",
        u"Gothic Rock",
        u"Progressive Rock",
        u"Psychedelic Rock",
        u"Symphonic Rock",
        u"Slow Rock",
        u"Big Band",
        u"Chorus",
        u"Easy Listening",
        u"Acoustic",
        u"Humour",
        u"Speech",
        u"Chanson",
        u"Opera",
        u"Chamber Music",
        u"Sonata",
        u"Symphony",
        u"Booty Bass",
        u"Primus",
        u"Porn Groove",
        u"Satire",
        u"Slow Jam",
        u"Club",
        u"Tango",
        u"Samba",
        u"Folklore",
        u"Ballad",
        u"Power Ballad",
        u"Rhythmic Soul",
        u"Freestyle",
        u"Duet",
        u"Punk Rock",
        u"Drum Solo",
        u"A capella",
        u"Euro-House",
        u"Dance Hall",

        # Later additions
        u"Goa",
        u"Drum & Bass",
        u"Club-House",
        u"Hardcore",
        u"Terror",
        u"Indie",
        u"BritPop",
        u"Negerpunk",
        u"Polsk Punk",
        u"Beat",
        u"Christian",
        u"Heavy Metal",
        u"Black Metal",
        u"Crossover",
        u"Contemporary",
        u"Christian Rock",
        u"Merengue",
        u"Salsa",
        u"Thrash Metal",
        u"Anime",
        u"JPop",
        u"Synthpop"
    )


translation_table = string.maketrans(''.join([chr(n) for n in range(32)]), ' ' * 32)


def truncate_id3v1(strng):
    null_idx = strng.find('\0')
    
    if null_idx == -1:
        return strng
    
    return strng[:null_idx]


def get_string(block, result, name):
    raw_string = truncate_id3v1(block).translate(translation_table).strip()
    
#    if raw_string.translate(translation_table) != raw_string:
#        print "ORG", raw_string
#        print "XLATE", raw_string.translate(translation_table)
#    
    if not raw_string:
        return
    
    result[name] = unicode(raw_string, 'ISO-8859-1', 'replace')


def id3v1tagreader(block):
    if len(block) != 128 or block[:3] != "TAG":
        return None
    
    result = {}
    
#    print "ID3v1:", block
    
    get_string(block[3:33], result, "title")
    get_string(block[33:63], result, "artist")
    get_string(block[63:93], result, "album")
    get_string(block[97:127], result, "comment")
    
    
    year_string = truncate_id3v1(block[93:97]).strip()
    if year_string:
        try:
            year = int(year_string)
        except ValueError:
            year = None

        result['year'] = year
        
    
    genre_code = ord(block[127])
    
    if genre_code < len(GENRE_NAMES):
        result['genre'] = GENRE_NAMES[genre_code]
        
    else:
        result['genre'] = u"Unknown/{0}".format(genre_code)
        
    
    track_num = ord(block[126])
    before_track_num = ord(block[125])
    
    if track_num != 0:
        if before_track_num == 0 or (before_track_num == 32 and track_num != 32):
            result['track'] = track_num 
    
    
    return result
