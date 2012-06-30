import dirmetadata
import pytest


@pytest.mark.skipif("'mp3' in dirmetadata.main.dirmetadata_providers")
def test_discovery():
    import dirmetadata.dirmetadata_mp3 as dirmetadata_mp3 #@UnusedImport

    print dirmetadata.main.dirmetadata_providers

    assert "mp3" in dirmetadata.main.dirmetadata_providers



if __name__ == "__main__":
    pytest.main()
