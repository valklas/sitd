from pathlib import Path


def create_test_tree(current_dir, depth=0):
    files = ["1.txt", "2.txt", "3.txt"]

    for file_name in files:
        new_file = current_dir / file_name
        new_file.write_text(f"This is the {file_name} file.")

    if depth == 0:
        return

    new_dir = current_dir / f"{depth}_dir"
    new_dir.mkdir()

    create_test_tree(new_dir, depth - 1)


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
            assert item["file_size"] == actual_path.stat().st_size
            assert actual_path.is_file()

        elif item["type"] == "directory":
            assert "children" in item
            assert isinstance(item["children"], list)
            assert actual_path.is_dir()

            assert_entries_valid(item["children"], root_dir)
