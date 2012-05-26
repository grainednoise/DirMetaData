from .core import AbstractDirectoryReader, NotFound, SEPARATOR
import os
import stat

try:
    import pwd

    def name_from_uid(uid):
        try:
            pwd.getpwuid(uid).pw_name
        except:
            return None

except ImportError:
    def name_from_uid(uid):
        return None

try:
    import grp

    def name_from_gid(gid):
        try:
            grp.getgrgid(gid).gr_name
        except:
            return None

except ImportError:
    def name_from_gid(gid):
        return None







class FileSystemDirectoryReader(AbstractDirectoryReader):
    def __init__(self, name, parent=None, full_path=None):
        super(FileSystemDirectoryReader, self).__init__(name, parent)
        self._current_files = None
        self._directories = None
        if parent is None:
            if full_path is None:
                raise ValueError("Must have parent or full_path")

            self._full_path = full_path

        else:
            if full_path is not None:
                raise ValueError("Must have either parent or full_path, not both")


            self._full_path = SEPARATOR.join([parent.full_path, name])



    def _ensure_file_data(self):
        if self._current_files is None:
            self._read_all()


    def files(self):
        self._ensure_file_data()

        return self._current_files.iterkeys()



    def subdirectories(self):
        self._ensure_file_data()

        return self._directories.iterkeys()


    def get_subdirectory_reader(self, subdirectory):
        raise NotImplementedError()



    def get_file_info(self, filename):
        self._ensure_file_data()
        full_file_name = self.full_name(filename)

        data = self._current_files.get(filename)
        if data is None:
            raise NotFound(full_file_name)


        return data




    def get_file_reader(self, filename):
        raise NotFound(self.full_name(filename))


    def _read_all(self):
        base_dir = self.full_path
        current_files = {}
        current_directories = {}

        for name in os.listdir(base_dir):
            full = os.path.join(base_dir, name)
            st = os.stat(full)

            mode = st.st_mode
            if stat.S_ISDIR(mode):
                current_directories[name] = st

            elif stat.S_ISREG:
                current_files[name] = st


        self._current_files, self._current_directories = self._process_stat_data(current_files, current_directories)


    def _process_stat_data(self, current_files, current_directories):

        for name, st in current_files.iteritems():
            result = dict(
                    size=st.st_size,
                    created=st.st_ctime,
                    modified=st.st_mtime,
                    mode=st.st_mode,
                )


            user_name = name_from_uid(st.st_uid)
            if user_name is not None:
                result['owner'] = user_name

            user_name = name_from_gid(st.st_gid)
            if user_name is not None:
                result['group'] = user_name

#            print oct(st.st_mode)
#            print st.st_birthtime

            current_files[name] = result


        return current_files, current_directories
