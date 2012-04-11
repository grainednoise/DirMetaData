

def ignore(data):
    print "IGNORED", data
    return None

STRING_ENCODINGS = {0: 'iso-8859-1', 1: 'utf-16', 2: 'utf-16be', 3: 'utf-8'}
BOM_LITTLE_ENDIAN = b'\xff\xfe'
BOM_BIG_ENDIAN = b'\xfe\xff'
BOMS = (BOM_LITTLE_ENDIAN, BOM_BIG_ENDIAN)

def _read_id3_string(strng, stringtype, nullreplace=None):
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



def named_text(name):
    def text(data):
        print name, repr(data)
        return name, _read_id3_string(data[1:], ord(data[0]))
    return text


def genre(data):
    return "genre", _read_id3_string(data[1:], ord(data[0]))


def named_text_list(name):
    def text(data):
        return name, _read_id3_string(data[1:], ord(data[0])).split(u'/')
    return text


def string_int(name): 
    def text(data):
        try:
            return name, int(_read_id3_string(data[1:], ord(data[0])))
        
        except ValueError:
            return name, None
        
    return text


def comment(data):
    stringtype  = ord(data[0])
    lang = unicode(data[1:4], 'ISO-8859-1', 'replace')
    full = _read_id3_string(data[4:], stringtype)
    lst = full.split(u'\0', 1)
    assert len(lst) == 2
    
    
    return 'comment', (lst[0], lang, lst[1])



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
        TLEN=ignore,
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
        TRCK=ignore,
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
            print result
    
    
    
    result = {}
    
    for name, data in results_list:
        if name == 'comment':
            comment = result.setdefault('comment', {})
            commentid, lang, value = data
            per_id = comment.setdefault(commentid, {})
            if lang in per_id:
                print "Duplicate id, lang:", commentid, lang
            else:
                per_id[lang] = value
            
        
        else:
            if name in result:
                print "Duplicate name:", name
            
            else:
                result[name] = data
    
    
    print result
    return result