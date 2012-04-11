
from dirmetadata import DirMetaDataProvider, register_provider
from dirmetadata.blockreaderutils import (
    reader_from_file_like_object_accepting_function,
    reader_from_trailing_block_accepting_function)
from dirmetadata.dirmetadata_mp3.mp3framereader import (classify_header, 
    read_frames)
from dirmetadata.dirmetadata_mp3.id3v1 import id3v1tagreader
from dirmetadata.dirmetadata_mp3.id3v2 import process_id3v2_frame




class Mp3DirmetadataProvider(DirMetaDataProvider):
    
    category_name = "mp3"
    
    def __init__(self, previously_stored_data=None):
        DirMetaDataProvider.__init__(self, previously_stored_data)
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
    
    
    def data(self):
        result = {}
        
        if self.id3v1data is not None:
            result['id3v1'] = self.id3v1data

        if self.id3v2data is not None:
            result['id3v2'] = self.id3v2data
            
        return result
    
    
    def _mp3_data_processor(self, reader):
        for frame in read_frames(reader):
            if frame.classification == "ID3":
                self._id3_frame_processor(frame)
            
    
    def _id3v1tagreader(self, block):
        self.id3v1data = id3v1tagreader(block)


    def _id3_frame_processor(self, frame):
        self.id3v2data = process_id3v2_frame(frame)
        
        
        
        
        
            
        

    
register_provider(Mp3DirmetadataProvider)
