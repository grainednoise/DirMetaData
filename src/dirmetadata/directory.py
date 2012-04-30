from os import listdir, stat
from os.path import isfile, isdir, join


from dirmetadata.main import register_provider, DirMetaDataProvider, dirmetadata_providers
import hashlib
from copy import deepcopy
import copy




class HashDataProvider(DirMetaDataProvider):
    category_name = "file"


    def __init__(self, previously_stored_data=None):
        self._data = previously_stored_data if previously_stored_data is not None else {}


    def data_generator(self, first_block_of_data, first_block_is_entire_file=False):
        self.hashgen = hashlib.sha1()

        if first_block_is_entire_file:
            self.hashgen.update(first_block_of_data)
            return []

        def updater(block):
            if block:
                self.hashgen.update(block)
                return True
            return False

        return [updater]


    def data(self):
        self._data['sha1'] = self.hashgen.hexdigest()
        return self._data



register_provider(HashDataProvider)



def read_directory(path):
    return DirectoryMetaData(path)




try:
    make_long_int = long  # @UndefinedVariable

except:
    make_long_int = int



class DirectoryMetaData(object):
    FILE_BLOCK_SIZE_LIMIT = 1024 * 1024 * 20


    def __init__(self, full_directory_path):
        assert isdir(full_directory_path)
        self._full_directory_path = full_directory_path
        self._full_metadata_path_name = join(full_directory_path, '.dirmetadata')

        if isfile(self._full_metadata_path_name):
            self._read_metadata()

        else:
            self._data = {}


        self._update_metadata()


    def __getitem__(self, name):
        """Returns a deep copy of all metadata for a file 'name' as dictionary."""
        return copy.deepcopy(self._data[name])


    def get(self, name, default=None):
        try:
            return self[name]

        except KeyError:
            return default


    def _update_metadata(self):
        directory_data = self._data

        all_files = self._all_files()

        for name in all_files:
            full_file_name = join(self._full_directory_path, name)
            st = stat(full_file_name)

            size = st.st_size
            mtime = make_long_int(round(st.st_mtime * 1000))
            ctime = make_long_int(round(st.st_ctime * 1000))

            file_data = directory_data.get(name)
            if file_data is None:
                directory_data[name] = file_data = {}
                file_data['file'] = dict(size=size, mtime=mtime, ctime=ctime, updated=True)
                self._dirty = True

            else:
                file_data_file = file_data['file']

                if size != file_data_file['size'] or mtime != file_data_file['mtime'] or ctime != file_data_file['ctime'] or file_data_file['deleted']:
                    file_data_file['size'] = size
                    file_data_file['mtime'] = mtime
                    file_data_file['ctime'] = ctime
                    file_data_file['updated'] = True
                    self._dirty = True


                else:
                    file_data_file['updated'] = False



        for name in directory_data:
            file_data = directory_data[name]
            file_data_file = file_data['file']

            if name not in all_files:
                if not file_data_file['deleted']:
                    file_data_file['deleted'] = True
                    self._dirty = True

                file_data_file.pop('updated', None)

            else:
                file_data_file.pop('deleted', None)


        for name in directory_data:
            file_data = directory_data[name]
            file_data_file = file_data['file']

            if file_data_file.get('updated'):
                self._update_file_data(name, file_data)
                del file_data_file['updated']



    def _update_file_data(self, name, file_data):
        providers = {}
        for provider_name in dirmetadata_providers:
            provider_class = dirmetadata_providers[provider_name]

            provider_data = deepcopy(file_data[provider_name]) if provider_name in file_data else {}
            providers[provider_name] = provider_class(provider_data)


        full_name = join(self._full_directory_path, name)


        with open(full_name, 'rb') as inp:
            block = inp.read(self.FILE_BLOCK_SIZE_LIMIT)
            is_complete_file = (len(block) < self.FILE_BLOCK_SIZE_LIMIT)


            readers = []
            for provider in providers.values():
                readers += provider.data_generator(block, is_complete_file)

            if is_complete_file:
                assert len(block) == file_data['file']['size']

                self._reader_feed(readers, block)
                self._reader_finish(readers)

            else:

                total = 0
                while block:
                    total += len(block)
                    self._reader_feed(readers, block)
                    block = inp.read(self.FILE_BLOCK_SIZE_LIMIT)

                self._reader_finish(readers)
                assert total == file_data['file']['size']

        for name in providers:
            file_data[name] = providers[name].data()




    def _reader_feed(self, readers, block):
        for idx in range(len(readers) - 1, -1, -1):
            reader = readers[idx]
            if not reader(block):
                del readers[idx]



    def _reader_finish(self, readers):
        self._reader_feed(readers, '')
        assert len(readers) == 0




    def _all_files(self):
        return set((name for name in listdir(self._full_directory_path) if name.lower() != '.dirmetadata'))
