from pathlib import Path

def human_readable(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    units_index = 0
    units_length = len(units) - 1

    while size >= 1024 and units_index < units_length:
        size /= 1024
        units_index += 1

    return f"{size:.2f} {units[units_index]}"

def inspect_dir(path):
    entries = []

    for item in path.iterdir():
        name = item.name

        if item.is_file():
            file_size_in_bytes = item.stat().st_size
            readable_size = human_readable(file_size_in_bytes)

            file_entry = {
                "name": name,
                "type": "file",
                "file_size": readable_size
            }
            entries.append(file_entry)

        elif item.is_dir():
            dir_entry = {
                "name": name,
                "type": "directory"
            }
            children = inspect_dir(item)
            dir_entry["children"] = children
            entries.append(dir_entry)

        else:
            print(f"Invalid file or folder {item}")

    return entries
