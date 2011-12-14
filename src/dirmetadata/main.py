import sys
from os import listdir
from os.path import join, isdir, isfile

dirmetadata_providers = {}


def _collect_plugin_paths(path):
    return [subpath for subpath in listdir(path) if subpath.startswith('dirmetadata_') and isfile(join(path, subpath, '__init__.py'))]


def _may_contain_valid_plugin_path(path):
    if not isdir(path):
        return False
    
    return bool(_collect_plugin_paths(path))



def register_provider(clss):
    """This function should be called during import of a plugin to register
     a subclass of DirMetaDataProvider. It may be called only once for any
     particular class, and the clss.category_name must be globally unique. 
    """
    assert isinstance(clss.category_name, (str, unicode))
    assert clss.category_name not in dirmetadata_providers
    dirmetadata_providers[clss.category_name] = clss
    



def enable_plugin_paths(candidate_paths):
    plugin_paths = tuple(filter(_may_contain_valid_plugin_path, candidate_paths))
    
    for path in plugin_paths:
        if path not in sys.path:
            sys.path.append(path)
    
    plugin_names = []
    for path in plugin_paths:
        plugin_names += _collect_plugin_paths(path)
    
    
    for plugin_name in plugin_names:
        __import__(plugin_name)

    print plugin_names
    



class DirMetaDataProvider(object):
    """Base class for all metadata plugin classes"""
    
    category_name = None
    
    def readers(self):
        raise NotImplementedError()

    def data(self):
        raise NotImplementedError()

    
