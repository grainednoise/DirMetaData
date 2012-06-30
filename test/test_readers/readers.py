# -*- coding: utf-8 -*-

from dirmetadata.readers import FileSystemDirectoryReader
import datetime
import os.path
from functools import wraps


test_directory = os.path.abspath(os.path.join(__file__, '..', '..', 'testdata'))

def reader():
    return FileSystemDirectoryReader('test', None, test_directory)


def test_not_empty_files():
    expected = set(['Lyrical Ballads 1798.txt', 'pg19033-images.epub'])
    assert expected == set(reader().files())



def test_attributes():
    result = reader().get_file_info('Lyrical Ballads 1798.txt')
    print result
    assert 151549 == result['size']
    assert 0o100666 == result['mode']

    # 8 January 2012 12:27:56
    assert datetime.datetime(2012, 1, 8, 12, 27, 56) == datetime.datetime.fromtimestamp(result['created']).replace(microsecond=0)

    # ‎26 ‎May ‎2012, ‏‎10:42:27
    assert datetime.datetime(2012, 5, 26, 10, 42, 27) == datetime.datetime.fromtimestamp(result['modified']).replace(microsecond=0)



def pytest_generate_tests(metafunc):
    if "topdesk_version" in metafunc.funcargnames:
        metafunc.parametrize("topdesk_version", ["4.4sp2", "5.0"])




def xxx(func):
    @wraps(func)
    def rv(topdesk_version):
        func(topdesk_version)

    return rv

@xxx
def test_versions(topdesk_version):
    print topdesk_version
    assert topdesk_version < "5"
if __name__ == "__main__":

    import nose
    nose.runmodule()

