from os.path import join, dirname
import dirmetadata
import pytest


@pytest.mark.skipif("'dummy' in dirmetadata.main.dirmetadata_providers")
def test_discovery(monkeypatch):

    additional_plugin_path = join(dirname(__file__), 'plugins')

    monkeypatch.syspath_prepend(additional_plugin_path)

    assert "dummy" not in dirmetadata.main.dirmetadata_providers
    try:
        dirmetadata.main.enable_plugin_paths([additional_plugin_path])

        print dirmetadata.main.dirmetadata_providers

        assert "dummy" in dirmetadata.main.dirmetadata_providers


    finally:
        if "dummy" in dirmetadata.main.dirmetadata_providers:
            del dirmetadata.main.dirmetadata_providers["dummy"]




if __name__ == "__main__":
    pytest.main()
