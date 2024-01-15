import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from agency_swarm.util.oai import get_openai_client  # noqa: F401

from tests.unit.test_utils.mock_firestore_client import MockFirestoreClient


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield


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


@pytest.fixture(autouse=True)
def mock_firestore_client():
    firestore_client = MockFirestoreClient()
    with patch("firebase_admin.firestore.client", return_value=firestore_client):
        yield firestore_client


@pytest.fixture(autouse=True)
def mock_get_openai_client():
    with patch("agency_swarm.util.oai.get_openai_client"):
        yield
