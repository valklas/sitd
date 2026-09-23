from sitd.filesystem import inspect_dir
from pathlib import Path

source_path = Path("~/.local/share/sitd/storage/").expanduser()
result = inspect_dir(source_path)
assert isinstance(result, list)
