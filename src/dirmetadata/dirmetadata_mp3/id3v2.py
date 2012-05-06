from dirmetadata.dirmetadata_mp3.id3v1 import decode_genre
import base64
import logging
import re

log = logging.getLogger("dirmetadata_mp3.id3v2")


def ignore(data):
    return None


class StringDecodeError(Exception):
    pass


STRING_ENCODINGS = {0: 'iso-8859-1', 1: 'utf-16', 2: 'utf-16be', 3: 'utf-8'}
BOM_LITTLE_ENDIAN = b'\xff\xfe'
BOM_BIG_ENDIAN = b'\xfe\xff'
BOMS = (BOM_LITTLE_ENDIAN, BOM_BIG_ENDIAN)

def _decode_typed_string(strng, stringtype):
    encoding = STRING_ENCODINGS.get(stringtype)
    if encoding is None:
        raise StringDecodeError()
    
    
    if stringtype == 1:
        if strng[:2] in BOMS:
            encoding = 'utf-16'
        
        else:
            encoding = 'utf-16lE'
    
    else:
        encoding = STRING_ENCODINGS[stringtype]
        
    try:
        result = unicode(strng, encoding)
        
    except UnicodeDecodeError:
        try:
            result = unicode(strng + b'\0', encoding)

        except UnicodeDecodeError:
            return u''
    
    return result.replace(u"\ufeff", u"").replace(u"\ufffe", u"")   # Get rid of any spurious BOMs
    


def sanitize_unicode_string(strng, nullreplace=u' '):
    if strng and strng[-1] == u'\0':
        strng = strng[:-1]

    return strng.replace(u'\0', nullreplace)


def _read_id3_string(data):
    return _decode_typed_string(data[1:], ord(data[0]))


re_permissive_newline = re.compile(r'\n\r?|\r\n?')

def _read_id3_string_replace_newlines(data):
    raw =  _decode_typed_string(data[1:], ord(data[0]))
    return re_permissive_newline.sub(u" ", sanitize_unicode_string(raw))
    

def named_text(name):
    def text(data):
#        print name, repr(data)
        return name, _read_id3_string_replace_newlines(data)
    return text


def named_text_with_newlines(name):
    def text(data):
        try:
            return name, sanitize_unicode_string(_read_id3_string(data), u'\n')
        
        except StringDecodeError:
            return name, None
        
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
    raw = _read_id3_string_replace_newlines(data).strip()
    
    mobj = re_genre2.match(raw)
    if mobj:
        value = decode_genre(int(mobj.group(0)))
    
    else:
        value = re_genre.sub(_genre_sub, raw)
    
    return "genre", value


def named_text_list(name):
    def text(data):
        return name, [v.strip() for v in _read_id3_string_replace_newlines(data).split(u'/')]
    return text


def string_int(name): 
    def text(data):
        try:
            return name, int(sanitize_unicode_string(_read_id3_string(data)).strip())
        
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
    
    try:
        full = _decode_typed_string(data[4:], stringtype)
        lst = full.split(u'\0', 1)
        
        if len(lst) < 2:
            return 'comment', (u'', lang, sanitize_unicode_string(full, u'\n'))
    
    except StringDecodeError:
        return None, None
    
    return 'comment', (sanitize_unicode_string(lst[0], u'\n'), lang, sanitize_unicode_string(lst[1], u'\n'))


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


def _split_null(data, offset, string_type):
    if string_type in (0, 3):
        split_point = data.find(b'\0', offset)
        assert split_point != -1
        string_data = data[offset:split_point]
        rest = data[split_point + 1:]

    else:
        assert string_type in (1, 2)
        
        current = offset
        while current < len(data) - 2:
            if data[current:current + 2] == b'\0\0':
                string_data = data[offset:current]
                rest = data[current + 2:]
            
            current += 2
        
        else:
            raise AssertionError()
    
    
    strng = sanitize_unicode_string(_decode_typed_string(string_data, string_type))
    
    return strng, rest
    
    

def decode_pic(data):
    string_type = ord(data[0])
    
    null = data.find(b'\0', 1)
    if null != -1:
        mime_type = unicode(data[1:null], 'ISO-8859-1', 'replace')
    else:
        mime_type = u""
    
    picture_type = ord(data[null + 1])
    
    description, rest = _split_null(data, null + 2, string_type)
    
    return "picture", (mime_type, picture_type, description, rest)


frames_3 = dict(
        BUF=ignore,
        CNT=ignore,
        COM=comment,
        CRA=ignore,
        CRM=ignore,
        ETC=ignore,
        EQU=ignore,
        GEO=ignore,
        IPL=ignore,
        LNK=ignore,
        MCI=ignore,
        MLL=ignore,
        PIC=decode_pic,
        POP=ignore,
        REV=ignore,
        RVA=ignore,
        SLT=ignore,
        STC=ignore,
        TAL=named_text('album'),
        TBP=ignore,
        TCM=named_text_list('composers'),
        TCO=genre,
        TCR=ignore,
        TDA=ignore,
        TDY=ignore,
        TEN=ignore,
        TFT=ignore,
        TIM=ignore,
        TKE=ignore,
        TLA=ignore,
        TLE=string_ms_as_s('duration'),
        TMT=ignore,
        TOA=ignore,
        TOF=ignore,
        TOL=ignore,
        TOR=ignore,
        TOT=ignore,
        TP1=named_text_list('artists'),
        TP2=ignore,
        TP3=ignore,
        TP4=ignore,
        TPA=ignore,
        TPB=ignore,
        TRC=ignore,
        TRD=ignore,
        TRK=named_text('track_raw'),
        TSI=ignore,
        TSS=ignore,
        TT1=named_text('content_group'),
        TT2=named_text('title'),
        TT3=named_text('subtitle'),
        TXT=ignore,
        TXX=ignore,
        TYE=string_int('year'),
        UFI=ignore,
        ULT=ignore,
        WAF=ignore,
        WAR=ignore,
        WAS=ignore,
        WCM=ignore,
        WCP=ignore,
        WPB=ignore,
        WXX=ignore,
    )


def read_tag3(data, offset):
    size_start = offset + 3
    frame_start = offset + 6
    
    identifier = data[offset:size_start]
    
    if len(data) < (frame_start + 1) or identifier == b'\0\0\0':
        return (None, None)
    
    size = (ord(data[size_start]) << 16) + (ord(data[size_start + 1]) << 8) + ord(data[size_start + 2])
    next_offset = frame_start + size
    
    return (frames_3.get(identifier, ignore)(data[frame_start: next_offset]), next_offset)


def _read_all_tag3(data):
    offset = 0
    while (offset + 7) < len(data):
        result, offset = read_tag3(data, offset)
        if offset is None:
            break
        
        if result:
            yield result



frames_4 = dict (
        AENC=ignore,
        APIC=decode_pic,
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
    size_offset = offset + 4
    frame_offset = offset + 10
    
    identifier = data[offset:size_offset]
    
    if len(data) < (frame_offset + 1) or identifier == b'\0\0\0\0':
        return (None, None)

#    flags1 = ord(data[offset + 8])
#    flags2 = ord(data[offset + 9])
    
    size = (ord(data[size_offset]) << 24) + \
        (ord(data[size_offset + 1]) << 16) + \
        (ord(data[size_offset + 2]) << 8) + \
        ord(data[size_offset + 3])
        
    next_offset = frame_offset + size
    
    return (frames_4.get(identifier, ignore)(data[frame_offset: next_offset]), next_offset)


def _read_all_tag4(data):
    offset = 0
    while (offset + 11) < len(data):
        result, offset = read_tag4(data, offset)
        if offset is None:
            break
        
        if result:
            yield result


def _add_to_result(result, key, value):
    previous = result.get(key)
    
    if previous is not None and previous != value:
        log.warn("Duplicate item '%s: previous=%s, this=%s", key, previous, value)
        return
    
    result[key] = value
    

def _process_comment(result, data):
    commentid, lang, value = data
    
    if not commentid:
        comment = result.setdefault('comment', {})
        
        if lang in comment:
            log.warn("Duplicate lang=%s",lang)
            comment[lang] += (u'\n' + value)
        else:
            comment[lang] = value
    
    else:
        comment = result.setdefault('comment_ids', {})
        per_id = comment.setdefault(commentid, {})
    
        if lang in per_id:
            log.warn("Duplicate id=%s, lang=%s", commentid, lang)
            per_id[lang] += (u'\n' + value)
        
        else:
            per_id[lang] = value



def _process_track(result, track):
    track, max_track = _decode_track(track)

    if track is not None:
        _add_to_result(result, 'track', track)

    if max_track is not None:
        _add_to_result(result, 'max_track', max_track)
        


picture_types = { 
        0: u"Other", 
        1: u"32x32 pixels 'file icon' (PNG only)",
        2: u"Other file icon",
        3: u"Cover (front)",
        4: u"Cover (back)",
        5: u"Leaflet page",
        6: u"Media (e.g. lable side of CD)",
        7: u"Lead artist/lead performer/soloist",
        8: u"Artist/performer",
        9: u"Conductor",
        0xA: u"Band/Orchestra",
        0xB: u"Composer",
        0xC: u"Lyricist/text writer",
        0xD: u"Recording Location",
        0xE: u"During recording",
        0xF: u"During performance",
        0x10: u"Movie/video screen capture",
        0x11: u"A bright coloured fish",
        0x12: u"Illustration",
        0x13: u"Band/artist logotype",
        0x14: u"Publisher/Studio logotype",
    }


def get_picture_type(number):
    picture_type = picture_types.get(number)
    if picture_type is not None:
        return picture_type
    
    return "Picture Type {0}".format(number)
     

def get_or_create_sub_list(dictionary, key):
    lst = dictionary.get(key)
    if lst is None:
        dictionary[key] = lst = []
    
    return lst


def _process_picture(result, data):
    mime_type, picture_type, description, image_data = data
    
    picture_info = dict(
                    picture_type=get_picture_type(picture_type),
                    image_data=base64.b64encode(image_data)           
                )
    
    if mime_type:
        if '/' not in mime_type:
            mime_type = 'image/' + mime_type
    
        picture_info['mime_type'] = mime_type
        
    if description:
        picture_info['description'] = description
    
    
    get_or_create_sub_list(result, 'pictures').append(picture_info)
        
    


def process_id3v2_frame(frame):
    unsync = bool(frame.flags & 0x80)
#    extended = bool(frame.flags & 0x40)
#    experimental = bool(frame.flags & 0x20)
#    print "Unsync", unsync, extended, experimental
    
    if unsync:
        raise NotImplementedError("unsync")
    
    if frame.version_major >= 3:
        reader = _read_all_tag4

    elif frame.version_major >= 2:
        reader = _read_all_tag3

    else:
        raise Exception("Undecodable version: {0}.{1}".format(frame.version_major, frame.version_minor))
    
    result = {}

    for name, data in reader(frame.data):
        if name == 'comment':
            _process_comment(result, data)
        
        elif name == 'track_raw':
            _process_track(result, data)
        
        elif name == 'picture':
            _process_picture(result, data)
        
        elif name is not None:
            _add_to_result(result, name, data)
    
    return result
