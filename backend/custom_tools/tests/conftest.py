import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir_path:
        # Create a subdirectory inside the temporary directory
        sub_dir = os.path.join(temp_dir_path, "sub")
        os.mkdir(sub_dir)

        # Create test files in the subdirectory
        with open(os.path.join(sub_dir, "test.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(sub_dir, "test.txt"), "w") as f:
            f.write("hello world")

        yield Path(temp_dir_path)
