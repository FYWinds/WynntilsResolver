import pytest
from wynntilsresolver.blocks import Version
from wynntilsresolver.blocks.version import SUPPORTED_VERSIONS, extract_version
from wynntilsresolver.exception import UnsupportedVersion


def test_version_decoding():
    for version in SUPPORTED_VERSIONS:
        data = [0, version, 1]
        assert Version.from_bytes(data).version == version
        assert data == [1]

    unsupported = max(SUPPORTED_VERSIONS) + 1
    with pytest.raises(UnsupportedVersion):
        Version.from_bytes([0, unsupported])


def test_extract_version():
    assert extract_version([]) == 0
    assert extract_version([Version(2)]) == 2
