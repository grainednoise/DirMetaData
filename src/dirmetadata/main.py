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



try:
    _valid_provider_id_types = (str, unicode)  # @UndefinedVariable

except:
    _valid_provider_id_types = (str, bytes)  # @UndefinedVariable



def register_provider(clss):
    """This function should be called during import of a plugin to register
     a subclass of DirMetaDataProvider. It may be called only once for any
     particular class, and the clss.category_name must be globally unique.
    """
    assert isinstance(clss.category_name, _valid_provider_id_types)
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

    print(plugin_names)




class DirMetaDataProvider(object):
    """Base class for all metadata plugin classes.
    All derived classes must supply a unique category name.
    """

    category_name = None


    def __init__(self, previously_stored_data=None):
        """
        @param previously_stored_data: a data structure containing serializable data
            as returned from the call to self.data() a previous occasion. Should be used
            when not all data can be parsed from the file (i.e. is input by the user) or
            when historical data should be kept (versioning).
        """


    def data_generator(self, first_block_of_data, first_block_is_entire_file=False):
        """Must return a list of readers (which may be empty).

        @param first_block_of_data: to determine whether or not you have readers for this type of data.
            The size of the block will be at least 64K, assuming of course the file is that long.
            There is be no set upper limit.

        @param first_block_is_entire_file: when True, ``first_block_of_data`` is guaranteed to  contain
            all data in the file, and the entire processing may be done in this method. In that case,
            ``[]`` should be returned.
            Please note that this is an optimization, and there may be circumstances in
            which this parameter is not set to True when the entire contents of the file actually
            *is* in ``first_block_of_data``.

        @return: a list of readers
            A reader is a callable which can be called multiple times with as its sole parameter a block
            of binary data from the file. All blocks will have a size >= 1, except the last one, which
            will have a size of 0. Please make sure you do *not* store any references to the data blocks
            as they will generally be as large as practical, and having more than one of these blocks may
            cause the program to run out of memory.

        """
        return []


    def data(self):
        """
        Will only be called after the data_generator() is called, and all readers returned will
        have been fed all the file data.
        """
        raise NotImplementedError()
