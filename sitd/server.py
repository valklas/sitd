from pathlib import Path
from fastapi import FastAPI, HTTPException

from .filesystem import inspect_dir

app = FastAPI()

storage_path = Path("~/.local/share/sitd/storage").expanduser()


def path_not_found(path):
    if not path.exists():
        raise HTTPException(status_code=404, detail="You sure this is the correct path...")

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

    path_not_found(sub_path)

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
