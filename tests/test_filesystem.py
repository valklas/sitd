from pathlib import Path
from tempfile import TemporaryDirectory

from sitd.filesystem import inspect_dir
from tests.helpers import assert_entries_valid, create_test_tree


def test_files():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        (root_dir / "1.txt").write_text("hello")
        (root_dir / "2.txt").write_text("hello world")
        (root_dir / "3.txt").write_text("hello world!")

        result = inspect_dir(root_dir, root_dir)

        assert isinstance(result, list)
        assert len(result) == 3

        assert_entries_valid(result, root_dir)


def test_single_file():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        file = root_dir / "hello.txt"
        file.write_text("Hello, world!")

        result = inspect_dir(root_dir, root_dir)

        assert isinstance(result, list)
        assert len(result) == 1

        item = result[0]

        assert item["name"] == "hello.txt"
        assert item["type"] == "file"
        assert item["path"] == "hello.txt"
        assert item["file_size"] == file.stat().st_size

        assert_entries_valid(result, root_dir)


def test_empty_directory():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        result = inspect_dir(root_dir, root_dir)

        assert isinstance(result, list)
        assert result == []


def test_nested_directories():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        create_test_tree(root_dir, 5)

        result = inspect_dir(root_dir, root_dir)

        assert isinstance(result, list)
        assert len(result) == 4

        assert_entries_valid(result, root_dir)


def test_empty_nested_directory():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        empty_dir = root_dir / "empty"
        empty_dir.mkdir()

        result = inspect_dir(root_dir, root_dir)

        assert isinstance(result, list)
        assert len(result) == 1

        item = result[0]

        assert item["name"] == "empty"
        assert item["type"] == "directory"
        assert item["path"] == "empty"
        assert item["children"] == []

        assert_entries_valid(result, root_dir)
