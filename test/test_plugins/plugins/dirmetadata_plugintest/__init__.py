from dirmetadata import DirMetaDataProvider, register_provider

class DummyDirmetadataProvider(DirMetaDataProvider):
    
    category_name = "dummy"
    
    def readers(self):
        return []
    
    def data(self):
        return {}

register_provider(DummyDirmetadataProvider)