
from dirmetadata import DirMetaDataProvider, register_provider
from dirmetadata.blockreaderutils import (
    reader_from_file_like_object_accepting_function,
    reader_from_trailing_block_accepting_function)
from dirmetadata.dirmetadata_mp3.mp3framereader import (classify_header, 
    read_frames)
from dirmetadata.dirmetadata_mp3.id3v1 import id3v1tagreader
from dirmetadata.dirmetadata_mp3.id3v2 import process_id3v2_frame
import hashlib




class Mp3DirmetadataProvider(DirMetaDataProvider):
    
    category_name = "mp3"
    
    def __init__(self, previously_stored_data=None):
        DirMetaDataProvider.__init__(self, previously_stored_data)
        self.sound = None
        self.errors = None
        self.id3v1data = None
        self.id3v2data = None
    
    
    def data_generator(self, first_block_of_data, first_block_is_entire_file=False):
        if len(first_block_of_data) < 128:
            return []
        
        if classify_header(first_block_of_data[:3]) is None:
            return []
        
        
        return [reader_from_file_like_object_accepting_function(self._mp3_data_processor), 
                reader_from_trailing_block_accepting_function(self._id3v1tagreader, 128)
            ]


    def _build_result(self):
        result = {}
        if self.sound is not None:
            result['sound'] = self.sound
            
        if self.errors:
            result['errors'] = self.errors
        
        if self.id3v1data is not None:
            result['id3v1'] = self.id3v1data
        
        if self.id3v2data is not None:
            result['id3v2'] = self.id3v2data
        
        return result


    def data(self):
        if self.sound == None and self.errors == None and self.id3v1data == None and self.id3v2data == None:
            return None

        return self._build_result()
    
    
    def _mp3_data_processor(self, reader):
        final_tag_frame = [None]
        
        def skip_last_tag_reader(reader):
            frame_generator = read_frames(reader)
            previous_frame = frame_generator.next()
            
            for frame in frame_generator:
                yield previous_frame
                previous_frame = frame
            
            if previous_frame.classification == 'TAG':
                final_tag_frame[0] = previous_frame
            
            else:
                yield previous_frame
            
        
        spurious_tag_frames = junk_frames = junk_size = 0
        
        mp3_sha = hashlib.sha1()
        junk_sha = hashlib.sha1()
        
        samplerate = None
        inconsistent_sample_rate = False
        samples = total_frame_sizes = total_frames = 0
        declared_bitrates = {}
        
        
        for frame in skip_last_tag_reader(reader):
            classification = frame.classification
            
            if classification == 'MP3':
                if samplerate != frame.samplerate:
                    if samplerate is None:
                        samplerate = frame.samplerate
                    else:
                        inconsistent_sample_rate = True
                
                total_frames += 1
                
                if frame.bitrate not in declared_bitrates:
                    declared_bitrates[frame.bitrate] = 0
                declared_bitrates[frame.bitrate] += 1
                
                samples += frame.nsamples
                total_frame_sizes += len(frame.data)
                mp3_sha.update(frame.data)
            
            elif classification == 'JUNK':
                junk_frames += 1
                junk_size += len(frame.data)
                junk_sha.update(frame.data)
            
            elif classification == "ID3":
                self._id3_frame_processor(frame)
            
            elif classification == "TAG":
                spurious_tag_frames += 1
        
        
        errors = {}
        if inconsistent_sample_rate:
            errors['inconsistent_sample_rate'] = True
        
        if junk_frames:
            errors['junk_frames'] = junk_frames
            errors['junk_size'] = junk_size
            errors['junk_hash'] = junk_sha.hexdigest()
        
        if spurious_tag_frames:
            errors['spurious_tag_frames'] = spurious_tag_frames
        
        self.errors = errors
        
        self.sound = dict(
                samples=samples,
                total_frame_sizes=total_frame_sizes,
                sample_rate=samplerate,
                hash=mp3_sha.hexdigest(),
                declared_bitrates=declared_bitrates,
                total_frames=total_frames,
            )
        
        if samplerate is not None and not inconsistent_sample_rate:
            duration = samples / float(samplerate)
            self.sound['duration'] = duration
            self.sound['bitrate'] = int(round(8 * total_frame_sizes / duration))
            
    
    def _id3v1tagreader(self, block):
        self.id3v1data = id3v1tagreader(block)


    def _id3_frame_processor(self, frame):
        self.id3v2data = process_id3v2_frame(frame)
            
        

    
register_provider(Mp3DirmetadataProvider)
