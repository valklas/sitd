from pathlib import Path
from fastapi import FastAPI

from .filesystem import inspect_dir

app = FastAPI()

storage_path = Path("~/.local/share/sitd/storage").expanduser()


@app.get("/")
def home():
    return {"message": "Hello from SITD!"}


@app.get("/api/files")
def files():
    result = inspect_dir(storage_path, storage_path)
    return result


@app.get("/api/files/{path:path}")
def files(path: str):
    sub_path = storage_path / path

    if sub_path.is_dir():
        result = inspect_dir(sub_path, storage_path)
        return result

    elif sub_path.is_file():
        file_entry = {
            "name": sub_path.name,
            "type": "file",
            "path": str(sub_path.relative_to(storage_path)),
            "file_size": sub_path.stat().st_size
        }
        return file_entry
