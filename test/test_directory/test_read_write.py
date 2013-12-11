from pathlib import Path
import pytest

import dirmetadata.directory as directory


@pytest.fixture(scope='session')
def testdata_path():
    return Path(__file__).parent.parent / 'testdata' 


@pytest.fixture(scope='function')
def metadata_path(testdata_path, request):
    result = testdata_path / '.dirmetadata'
    def fin():
        if result.exists():
            result.unlink()
            
    request.addfinalizer(fin)
    return result
        

def test_read_write(testdata_path, metadata_path):
    """
    :type testdata_path: Path
    :type metadata_path: Path
    """
    assert not metadata_path.exists()
    
    dd = directory.read_directory(testdata_path)
    original_names =  dd.names()
    original_data = {}
    
    for name in original_names:
        data = dd[name]
        assert data['file']['updated']
        del data['file']['updated']
        
        assert 'updated' in dd[name]['file']  # Should not affect internal data
        
        original_data[name] = data
    
    
    dd.write_if_updated()
    
    assert metadata_path.exists()
    
    
    dd2 = directory.read_directory(testdata_path) 
    
    assert original_names == dd2.names()
    
    for name in original_names:
        data = dd2[name]
        assert not data['file']['updated']
        del data['file']['updated']
        assert original_data[name] == data
