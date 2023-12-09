from pathlib import Path

import pytest


@pytest.fixture
def temp_dir(tmp_path: Path):
    """Create a temporary directory with some files inside it.
    The structure looks like this:
    temp_dir_path
    ├── sub
    │   ├── test.py (contains "print('hello')")
    │   └── test.txt (contains "hello world")

    Yield the path to the temporary directory.
    """
    temp_dir_path = tmp_path / "sub"
    temp_dir_path.mkdir(parents=True)
    (temp_dir_path / "test.py").write_text("print('hello')")
    (temp_dir_path / "test.txt").write_text("hello world")
    yield tmp_path
