import hashlib

from pathlib import Path
import pytest

import dirmetadata.directory as directory


@pytest.fixture(scope='session')
def testdata_path():
    return Path(__file__).parent.parent / 'testdata' 


@pytest.fixture(scope='module')
def hashes(testdata_path):
    values = {}

    for file_path in testdata_path.iterdir():
        with file_path.open('rb') as inp:
            values[file_path.name] = hashlib.sha1(inp.read()).hexdigest()
    
    return values


@pytest.fixture(params=[65536, 100000000, 20])
def blocksize(request):
    old_value = directory.DirectoryMetaData.FILE_BLOCK_SIZE_LIMIT
    directory.DirectoryMetaData.FILE_BLOCK_SIZE_LIMIT = request.param
    
    def fin():
        directory.DirectoryMetaData.FILE_BLOCK_SIZE_LIMIT = old_value
    request.addfinalizer(fin)

    return request.param


def test_hash(blocksize, testdata_path, hashes):
    dd = directory.read_directory(testdata_path)
    assert len(hashes) == len(dd._data)

    for name in hashes:
        assert hashes[name] == dd[name]['file']['sha1']
    

