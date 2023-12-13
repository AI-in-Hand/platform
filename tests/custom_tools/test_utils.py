import pytest

from nalgonda.custom_tools.utils import check_directory_traversal


@pytest.mark.parametrize("path", ["..", "/", "/sbin"])
def test_check_directory_traversal_raises_for_attempts(path):
    with pytest.raises(ValueError) as e:
        check_directory_traversal(path)
    assert e.errisinstance(ValueError)
    assert "Directory traversal is not allowed." in str(e.value)
