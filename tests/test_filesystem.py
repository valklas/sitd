from pathlib import Path
from sitd.filesystem import inspect_dir
from tempfile import TemporaryDirectory


def create_test_tree(current_dir, depth):
        files = ["1.txt", "2.txt", "3.txt"]
    
        for file_name in files:
            new_file = current_dir / file_name
            new_file.write_text(f"This is the {file_name} file.")
            print(new_file)
        
        if depth == 0:
            return
    
        new_dir = current_dir / f"{depth}_dir"
        new_dir.mkdir()
        print(new_dir)

        create_test_tree(new_dir , depth - 1)


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


with TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)

    create_test_tree(root_dir, 5)
    print(list(root_dir.iterdir()))

    result = inspect_dir(root_dir)
    
    assert isinstance(result, list)
    assert len(result) == 4

    check_entries(result)

    print(result)
