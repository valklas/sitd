from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .filesystem import inspect_dir


app = FastAPI()

app.mount("/static", StaticFiles(directory="sitd/static"), name="static")


storage_path = Path("~/.local/share/sitd/storage").expanduser()


def validate_path_exists(path):
    if not path.exists():
        raise HTTPException(status_code=404, detail="You sure this is the correct path...")

def get_target_path(path):
    root = storage_path.resolve()
    target_path = (storage_path / path).resolve()

    if not target_path.is_relative_to(root):
        raise HTTPException(status_code=404, detail="Naughty you...")
    
    return target_path


@app.get("/")
def home():
    return RedirectResponse("/files")


@app.get("/api/files")
def api_files():
    result = inspect_dir(storage_path, storage_path)
    return result


@app.get("/api/files/{path:path}")
def api_sub_files(path: str):

    target_path = get_target_path(path)

    validate_path_exists(target_path)

    if target_path.is_dir():
        result = inspect_dir(target_path, storage_path)
        return result

    elif target_path.is_file():
        file_entry = {
            "name": target_path.name,
            "type": "file",
            "path": str(target_path.relative_to(storage_path)),
            "file_size": target_path.stat().st_size
        }
        return file_entry


@app.get("/files/{path:path}")
def serve_sub_files(path: str):
    target_path = get_target_path(path)

    validate_path_exists(target_path)

    if target_path.is_file():
        return FileResponse(target_path)

    elif target_path.is_dir():
            return FileResponse("sitd/static/index.html")
