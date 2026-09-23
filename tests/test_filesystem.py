from sitd.filesystem import inspect_dir
from pathlib import Path

source_path = Path("~/.local/share/sitd/storage").expanduser()

result = inspect_dir(source_path)

assert isinstance(result, list)
assert len(result) >= 0


def check_entries(entries):
    for item in entries:
        assert isinstance(item, dict)

        assert "name" in item
        assert "type" in item
        assert item["type"] in ["file", "directory"]

        if item["type"] == "file":
            assert "file_size" in item

        elif item["type"] == "directory":
            assert "children" in item
            assert isinstance(item["children"], list)

            check_entries(item["children"])


check_entries(result)
