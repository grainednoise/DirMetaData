
from dirmetadata import DirMetaDataProvider, register_provider


class Mp3DirmetadataProvider(DirMetaDataProvider):
    
    category_name = "mp3"
    
    def readers(self):
        return []
    
    def data(self):
        return {}

register_provider(Mp3DirmetadataProvider)
