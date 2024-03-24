from pathlib import Path

import pytest

from backend.custom_skills.utils import check_directory_traversal


@pytest.mark.parametrize("path", [".", "tests", "tests/custom_skills"])
def test_check_directory_traversal_does_not_raise_for_valid_paths(path):
    check_directory_traversal(Path(path))


@pytest.mark.parametrize("path", ["..", "/", "/sbin"])
def test_check_directory_traversal_raises_for_attempts(path):
    with pytest.raises(ValueError) as e:
        check_directory_traversal(Path(path))
    assert e.errisinstance(ValueError)
    assert "Directory traversal is not allowed." in str(e.value)
