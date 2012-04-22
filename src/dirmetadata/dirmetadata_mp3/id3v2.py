import re
from dirmetadata.dirmetadata_mp3.id3v1 import decode_genre


def ignore(data):
#    print "IGNORED", data
    return None

STRING_ENCODINGS = {0: 'iso-8859-1', 1: 'utf-16', 2: 'utf-16be', 3: 'utf-8'}
BOM_LITTLE_ENDIAN = b'\xff\xfe'
BOM_BIG_ENDIAN = b'\xfe\xff'
BOMS = (BOM_LITTLE_ENDIAN, BOM_BIG_ENDIAN)

def _decode_typed_string(strng, stringtype, nullreplace=u'\n'):
    encoding = STRING_ENCODINGS[stringtype]
    if stringtype == 1:
        # This is a safekeeping code. Under normal circumstances, it shouldn't
        # happen to have a \0 or a second BOM or no BOM in a type 1 string
        bom = strng[:2]
        if bom in BOMS:
            therest = strng[2:].replace(BOM_BIG_ENDIAN, b'').replace(BOM_LITTLE_ENDIAN, b'')
            strng = bom + therest
        else:
            strng = BOM_LITTLE_ENDIAN + strng
            
    try:
        result = unicode(strng, encoding)
        
    except UnicodeDecodeError:
        try:
            result = unicode(strng + b'\0', encoding)

        except UnicodeDecodeError:
            return u''
            
    if nullreplace is None:
        return result
    
    return result.replace(u'\0', nullreplace)


def _read_id3_string(data, nullreplace=u'\n'):
    return _decode_typed_string(data[1:], ord(data[0]), nullreplace)


def named_text(name):
    def text(data):
#        print name, repr(data)
        return name, _read_id3_string(data)
    return text



re_genre = re.compile(r'\((\(|(?P<ref>\d+)\))')
re_genre2 = re.compile(r'^\d+$')


def _genre_sub(mobj):
    ref = mobj.group('ref')
    if ref is None:
        return "("
    num = int(ref)
    return decode_genre(num)


def genre(data):
    raw = _read_id3_string(data).strip()
    
    mobj = re_genre2.match(raw)
    if mobj:
        value = decode_genre(int(mobj.group(0)))
    
    else:
        value = re_genre.sub(_genre_sub, raw)
    
    return "genre", value


def named_text_list(name):
    def text(data):
        return name, _read_id3_string(data).split(u'/')
    return text


def string_int(name): 
    def text(data):
        try:
            return name, int(_read_id3_string(data))
        
        except ValueError:
            return name, None
        
    return text

def string_ms_as_s(name): 
    def text(data):
        try:
            return name, float(_read_id3_string(data)) / 1000.0
        
        except ValueError:
            return name, None
        
    return text



def trunc_at_0(lang):
    null_byte = lang.find(b'\0')
    if null_byte == -1:
        return lang
    
    return lang[:null_byte]


def comment(data):
    stringtype  = ord(data[0])
    lang = unicode(trunc_at_0(data[1:4]), 'ISO-8859-1', 'replace')
    
    full = _decode_typed_string(data[4:], stringtype)
    lst = full.split(u'\n', 1)
    
    return 'comment', (lst[0], lang, lst[1])


def _valid_int_or_none(value):
    try:
        return int(value)
    
    except ValueError:
        return None



def _decode_track(track):
    #The track field can either contain a track number or a string in the
    #format <trackno>/<trackcount> (Example: 3/14)
    
    if '/' in track: 
        num, maxnum = track.split('/', 1)
        return _valid_int_or_none(num), _valid_int_or_none(maxnum)
        
    return (_valid_int_or_none(track), None)

        


frames_4 = dict (
        AENC=ignore,
        APIC=ignore,
        COMM=comment,
        COMR=ignore,
        ENCR=ignore,
        EQUA=ignore,
        ETCO=ignore,
        GEOB=ignore,
        GRID=ignore,
        IPLS=ignore,
        LINK=ignore,
        MCDI=ignore,
        MLLT=ignore,
        OWNE=ignore,
        PRIV=ignore,
        PCNT=ignore,
        POPM=ignore,
        POSS=ignore,
        RBUF=ignore,
        RVAD=ignore,
        RVRB=ignore,
        SYLT=ignore,
        SYTC=ignore,
        TALB=named_text('album'),
        TBPM=ignore,
        TCOM=named_text_list('composers'),
        TCON=genre,
        TCOP=ignore,
        TDAT=ignore,
        TDLY=ignore,
        TENC=ignore,
        TEXT=ignore,
        TFLT=ignore,
        TIME=ignore,
        TIT1=named_text('content_group'),
        TIT2=named_text('title'),
        TIT3=named_text('subtitle'),
        TKEY=ignore,
        TLAN=ignore,
        TLEN=string_ms_as_s('duration'),
        TMED=ignore,
        TOAL=ignore,
        TOFN=ignore,
        TOLY=ignore,
        TOPE=ignore,
        TORY=ignore,
        TOWN=ignore,
        TPE1=named_text_list('artists'),
        TPE2=ignore,
        TPE3=ignore,
        TPE4=ignore,
        TPOS=ignore,
        TPUB=ignore,
        TRCK=named_text('track_raw'),
        TRDA=ignore,
        TRSN=ignore,
        TRSO=ignore,
        TSIZ=ignore,
        TSRC=ignore,
        TSSE=ignore,
        TYER=string_int('year'),
        TXXX=ignore,
        UFID=ignore,
        USER=ignore,
        USLT=ignore,
        WCOM=ignore,
        WCOP=ignore,
        WOAF=ignore,
        WOAR=ignore,
        WOAS=ignore,
        WORS=ignore,
        WPAY=ignore,
        WPUB=ignore,
        WXXX=ignore,
    )




def read_tag4(data, offset):
    identifier = data[offset:offset + 4]
    size_blk =  data[offset + 4:offset + 8]
    flags1 = ord(data[offset + 8])
    flags2 = ord(data[offset + 9])
    
    size = (ord(size_blk[0]) << 24) + (ord(size_blk[1]) << 16) + (ord(size_blk[2]) << 8) + ord(size_blk[3])
    print repr(identifier), size
    print repr(data[offset + 10: offset + 10 + size])
    
    if identifier == b'\0\0\0\0':
        return (None, None)
    
    return (frames_4.get(identifier, ignore)(data[offset + 10: offset + 10 + size]), offset + 10 + size)



def _add_to_result(result, key, value):
    previous = result.get(key)
    
    if previous is not None and previous != value:
        print "Duplicate item '{0}: previous={1}, this={2}".format(key, previous, value)
        return
    
    result[key] = value
    

def _process_comment(result, data):
    commentid, lang, value = data
    
    if not commentid:
        comment = result.setdefault('comment', {})
        
        if lang in comment:
            print "Duplicate lang:",lang
            comment[lang] += (u'\n' + value)
        else:
            comment[lang] = value
    
    else:
        comment = result.setdefault('comment_ids', {})
        per_id = comment.setdefault(commentid, {})
    
        if lang in per_id:
            print "Duplicate id, lang:", commentid, lang
            per_id[lang] += (u'\n' + value)
        
        else:
            per_id[lang] = value



def _process_track(result, track):
    track, max_track = _decode_track(track)
    print "TRACK", track, max_track

    if track is not None:
        _add_to_result(result, 'track', track)

    if max_track is not None:
        _add_to_result(result, 'max_track', max_track)
        


def process_id3v2_frame(frame):
    print frame
    unsync = bool(frame.flags & 0x80)
    extended = bool(frame.flags & 0x40)
    experimental = bool(frame.flags & 0x20)
    print "Unsync", unsync, extended, experimental
    
    results_list = []
    
    offset = 0
    while (offset + 11) < len(frame.data):
        result, offset = read_tag4(frame.data, offset)
        if offset is None:
            break
        
        if result:
            results_list.append(result)
#            print result
    
    result = {}
    
    for name, data in results_list:
        if name == 'comment':
            _process_comment(result, data)
        
        elif name == 'track_raw':
            _process_track(result, data)
        
        else:
            _add_to_result(result, name, data)

    
    print result
    return result