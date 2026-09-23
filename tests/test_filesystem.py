from pathlib import Path
from tempfile import TemporaryDirectory

from sitd.filesystem import inspect_dir


def assert_entries_valid(entries, root_dir):
    for item in entries:
        assert isinstance(item, dict)

        assert "name" in item
        assert "type" in item
        assert item["type"] in ["file", "directory"]

        assert "path" in item
        assert isinstance(item["path"], str)
        assert item["path"].endswith(item["name"])

        actual_path = root_dir / item["path"]

        assert actual_path.exists()
        assert actual_path.name == item["name"]

        if item["type"] == "file":
            assert "file_size" in item
            assert actual_path.is_file()
            assert item["file_size"] == actual_path.stat().st_size

        elif item["type"] == "directory":
            assert "children" in item
            assert isinstance(item["children"], list)
            assert actual_path.is_dir()

            assert_entries_valid(item["children"], root_dir)


def create_test_tree(current_dir, depth):
    files = ["1.txt", "2.txt", "3.txt"]

    for file_name in files:
        new_file = current_dir / file_name
        new_file.write_text(f"This is the {file_name} file.")

    if depth == 0:
        return

    new_dir = current_dir / f"{depth}_dir"
    new_dir.mkdir()

    create_test_tree(new_dir, depth - 1)


def test_empty_directory():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        result = inspect_dir(root_dir, root_dir)

        assert isinstance(result, list)
        assert result == []


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


def test_nested_directories():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        create_test_tree(root_dir, 5)

        result = inspect_dir(root_dir, root_dir)

        assert isinstance(result, list)
        assert len(result) == 4

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
