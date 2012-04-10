
"""
Loosely based on mp3cat.py by Yusuke Shinyama

"""

from struct import unpack
import logging
import sys

log = logging.getLogger('dirmetadata_mp3.mp3framereader')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

__all__ = ('JunkFrame', 'TagFrame', 'Id3Frame', 'Mp3Frame', 'read_frames')


class Frame(object):
    def __init__(self, data, classification):
        self.data = data
        self.classification = classification

class JunkFrame(Frame):
    def __init__(self, data):
        Frame.__init__(self, data, 'JUNK')

    def __repr__(self):
        return "<JunkFrame length=%d>" % len(self.data)

class TagFrame(Frame):
    def __init__(self, data):
        Frame.__init__(self, data, 'TAG')

    @staticmethod
    def create(datasource):
        data = datasource.read(128 - 3)
        return TagFrame(data)

    def __repr__(self):
        return "<TagFrame>"

class Id3Frame(Frame):
    def __init__(self, data, version_major, version_minor, flags, lengthbytes, size):
        Frame.__init__(self, data, 'ID3')
        self.version_major = version_major
        self.version_minor = version_minor
        self.flags = flags
        self.lengthbytes = lengthbytes
        self.size = size

    @staticmethod
    def create(datasource):
        version_major = datasource.read(1)
        version_minor = datasource.read(1)

        flags = datasource.read(1)

        lengthbytes = datasource.read(4)
        s = [ord(c) & 127 for c in lengthbytes]
        size = (s[0]<<21) | (s[1]<<14) | (s[2]<<7) | s[3]

        data = datasource.read(size)

        return Id3Frame(''.join((version_major, version_minor, flags, lengthbytes, data)), ord(version_major), ord(version_minor), ord(flags), lengthbytes, size)

    def __repr__(self):
        return "<Id3Frame version=%d.%d flags=%d size=%d>" % (self.version_major, self.version_minor, self.flags, self.size)


BITRATE_TABLE_V1_L1 = (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448)
BITRATE_TABLE_V1_L2 = (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384)
BITRATE_TABLE_V1_L3 = (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320)
BITRATE_TABLE_V2_L1 = (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256)           
BITRATE_TABLE_V2_5_L2L3 = (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160)              


# Currently unused
BITRATE_TABLE = {
    (1, 1): BITRATE_TABLE_V1_L1,  
    (1, 2): BITRATE_TABLE_V1_L2,  
    (1, 3): BITRATE_TABLE_V1_L3,  
    (2, 1): BITRATE_TABLE_V2_L1,
    (3, 2): BITRATE_TABLE_V2_5_L2L3,
    (3, 3): BITRATE_TABLE_V2_5_L2L3,
                       
}      
                       

SAMPLERATE1 = (44100, 48000, 32000)
SAMPLERATE2 = (22050, 24000, 16000)
SAMPLERATE25 = (11025, 12000, 8000)


class Mp3Frame(Frame):
    def __init__(self, data, frame_number, bitrate, bitrate_bit, samplerate, version, framesize, nsamples,  pad_bit, channel, joint, copyright, original, emphasis, protected): #@ReservedAssignment
        Frame.__init__(self, data, 'MP3')

        self.frame_number = frame_number
        self.bitrate = bitrate
        self.bitrate_bit = bitrate_bit
        self.samplerate = samplerate
        self.version = version
        self.framesize = framesize
        self.nsamples = nsamples
        self.pad_bit = pad_bit
        self.bitrate = bitrate
        self.joint = joint
        self.channel = channel
        self.copyright = copyright
        self.original = original
        self.emphasis = emphasis
        self.protected = protected


    @staticmethod
    def create(datasource, frame_number, headerdata):
        h0, h1, h2 = unpack('BBB', headerdata)
        
        print hex(h0), hex(h1), hex(h2)

        version = (h1 & 0x18) >> 3
        assert version != 1
        layer = 4 - ((h1 & 0x06) >> 1)
        
        print layer
        assert layer == 3, 'Bad layer ID'

        protected = not (h0 & 0x01)

        bitrate_bit = (h2 & 0xf0) >> 4
        print bitrate_bit
        assert bitrate_bit != 0 and bitrate_bit != 15, '!Bitrate'

        pad_bit = (h2 & 0x02) >> 1

        if version == 3:                      # V1
            bitrate = BITRATE_TABLE_V1_L3[bitrate_bit]
        else:                                 # V2 or V2.5
            bitrate = BITRATE_TABLE_V2_5_L2L3[bitrate_bit]
        s = (h0 & 0x0c00) >> 10
        assert s != 3, '!SampleRate'

        if version == 3:                      # V1
            samplerate = SAMPLERATE1[s]
        elif version == 2:                    # V2
            samplerate = SAMPLERATE2[s]
        elif version == 0:                    # V2.5
            samplerate = SAMPLERATE25[s]

        nsamples = 1152
        if samplerate <= 24000:
            nsamples = 576

        headerdata2 = datasource.read(1)

        h3 = ord(headerdata2)
        channel = (h3 & 0xc0) >> 6
        joint = (h3 & 0x30) >> 4
        copyright = bool(h3 & 8) #@ReservedAssignment
        original = bool(h3 & 4)
        emphasis = h3 & 3

        if version == 3:
            framesize = 144000 * bitrate / samplerate + pad_bit
        else:
            framesize = 72000 * bitrate / samplerate + pad_bit
        
        print "Frame size ==", framesize

        data = headerdata + headerdata2 + datasource.read(framesize - 4)

        return Mp3Frame(data, frame_number, bitrate, bitrate_bit, samplerate, version, framesize, nsamples, pad_bit, channel, joint, copyright, original, emphasis, protected)


    def __repr__(self):
        return "<Mp3Frame %d: bitrate=%d; samplerate=%d; nsamples=%d; framesize=%d>" % (self.frame_number, self.bitrate, self.samplerate, self.nsamples, self.framesize)


def read_frames(datasource):
    frame_number = 0

    while True:
        headerdata, classification, junkframe = classify_and_synchronise(datasource)
        print "CLSS", classification

        if junkframe:
            frame = JunkFrame(junkframe)
            log.debug(frame)
            yield frame

        if classification == 'TAG':
            frame = TagFrame.create(datasource)

        elif classification == 'ID3':
            frame = Id3Frame.create(datasource)

        elif classification == 'MP3':
            frame_number += 1
            frame = Mp3Frame.create(datasource, frame_number, headerdata)

        else:
            break
        
        log.debug(frame)
        yield frame


def classify_and_synchronise(datasource):
    headerdata = datasource.read(3)

    if not len(headerdata) < 3:
        return None, None, headerdata
    

    classification = classify_header(headerdata)
    if classification:
        return headerdata, classification, None

    log.debug("Lost sync at %d, trying to regain",  datasource.tell())

    leftoverdata = []

    while not classification:
        leftoverdata.append(headerdata[0])
        
        headerdata = headerdata[1:] + datasource.read(1)

        if len(headerdata) < 3:
            leftoverdata += list(headerdata)
            log.debug("Sync irretrievably lost")
            break

        classification = classify_header(headerdata)
        
    else:
        log.debug("Regained sync at %d", datasource.tell())
        print headerdata

    return headerdata, classification, ''.join(leftoverdata)


def classify_header(headerdata):
    if headerdata in ('TAG', 'ID3'):
        return headerdata
    
    h1 = ord(headerdata[1])
    bitrate = (ord(headerdata[2]) & 0xf0) >> 4
    
    if ord(headerdata[0]) == 0xff and (h1 & 0xe0) == 0xe0 and (h1 & 0x06) == 2 and (h1 & 0x18) != 0 and bitrate != 0 and bitrate != 15:
        return 'MP3'

    return None


#def processId3Data(datasource, verbose):
#    # ID3 - ignored
#    version = datasource.read(2)
#    flags = ord(datasource.read(1))
#    lengthbytes = datasource.read(4)
#    s = [ ord(c) & 127 for c in lengthbytes]
#    size = (s[0]<<21) | (s[1]<<14) | (s[2]<<7) | s[3]
#
#    data = datasource.read(size)
#
#    if verbose:
#      print 'ID3 (%0xd bytes)' % size, repr(data)
#
#    return
#
#def processTagData(datasource, verbose):
#    # TAG - ignored
#    data = datasource.read(128 - 3)
#
#    if verbose:
#      print 'TAG', repr(data)


