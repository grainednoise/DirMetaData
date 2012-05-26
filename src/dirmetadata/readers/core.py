
from abc import ABCMeta, abstractmethod

SEPARATOR = u'/'


class NotFound(Exception):
    pass


class AbstractDirectoryReader(object):
    __metaclass__ = ABCMeta

    def __init__(self, name=None, parent=None):
        self._name = name
        self._parent = parent
        self._full_path = None


    @property
    def name(self):
        return


    @property
    def full_path(self):
        return self._full_path



    def full_name(self, filename):
        return SEPARATOR.join([self._full_path, filename])


    @abstractmethod
    def files(self):
        raise NotImplementedError()


    @abstractmethod
    def subdirectories(self):
        raise NotImplementedError()


    @abstractmethod
    def get_subdirectory_reader(self, subdirectory):
        raise NotImplementedError()


    @abstractmethod
    def get_file_info(self, filename):
        raise NotFound()


    @abstractmethod
    def get_file_reader(self, filename):
        raise NotFound()
