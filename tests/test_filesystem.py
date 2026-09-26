from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from sitd.filesystem import get_mime_type, inspect_dir
from tests.helpers import assert_entries_valid, create_test_tree


@pytest.fixture
def test_storage():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        yield root_dir


def test_files(test_storage):
    (test_storage / "1.txt").write_text("hello")
    (test_storage / "2.txt").write_text("hello world")
    (test_storage / "3.txt").write_text("hello world!")

    result = inspect_dir(test_storage, test_storage)

    assert isinstance(result, list)
    assert len(result) == 3

    assert_entries_valid(result, test_storage)


def test_single_file(test_storage):
    file = test_storage / "hello.txt"
    file.write_text("Hello, world!")

    result = inspect_dir(test_storage, test_storage)

    assert isinstance(result, list)
    assert len(result) == 1

    item = result[0]

    assert item["name"] == "hello.txt"
    assert item["type"] == "file"
    assert item["path"] == "hello.txt"
    assert item["file_size"] == file.stat().st_size
    assert item["mime_type"] == "text/plain"

    assert_entries_valid(result, test_storage)


def test_empty_directory(test_storage):
    result = inspect_dir(test_storage, test_storage)

    assert isinstance(result, list)
    assert result == []


def test_nested_directories(test_storage):
    create_test_tree(test_storage, 5)

    result = inspect_dir(test_storage, test_storage)

    assert isinstance(result, list)
    assert len(result) == 4

    assert_entries_valid(result, test_storage)


def test_empty_nested_directory(test_storage):
    empty_dir = test_storage / "empty"
    empty_dir.mkdir()

    result = inspect_dir(test_storage, test_storage)

    assert isinstance(result, list)
    assert len(result) == 1

    item = result[0]

    assert item["name"] == "empty"
    assert item["type"] == "directory"
    assert item["path"] == "empty"
    assert item["children"] == []

    assert_entries_valid(result, test_storage)


def test_get_mime_type(test_storage):
    path = test_storage / "1.txt"
    path.write_text("Hello")

    result = get_mime_type(path)

    assert result == "text/plain"


def test_get_mime_type_unknown(test_storage):
    path = test_storage / "something.sitdtest"
    path.write_text("Hello")

    result = get_mime_type(path)

    assert result is None
