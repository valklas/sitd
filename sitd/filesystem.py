from pathlib import Path


def inspect_dir(path):
    entries = []

    for item in path.iterdir():
        name = item.name

        if item.is_file():
            file_size_in_bytes = item.stat().st_size

            file_entry = {"name": name, "type": "file", "path": str(item), "file_size": file_size_in_bytes}
            entries.append(file_entry)

        elif item.is_dir():
            dir_entry = {"name": name, "type": "directory", "path": str(item)}
            children = inspect_dir(item)
            dir_entry["children"] = children
            entries.append(dir_entry)

        else:
            print(f"Invalid file or folder {item}")

    return entries
