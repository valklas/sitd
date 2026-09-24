from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from .filesystem import inspect_dir


app = FastAPI()


storage_path = Path("~/.local/share/sitd/storage").expanduser()


def path_not_found(path):
    if not path.exists():
        raise HTTPException(status_code=404, detail="You sure this is the correct path...")

def get_sub_path(path):
    sub_path = storage_path / path
    return sub_path


@app.get("/")
def home():
    return {"message": "Hello from SITD!"}


@app.get("/api/files")
def api_files():
    result = inspect_dir(storage_path, storage_path)
    return result


@app.get("/api/files/{path:path}")
def api_sub_files(path: str):
    sub_path = get_sub_path(path)

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


@app.get("/files/{path:path}")
def serve_sub_files(path: str):
    sub_path = get_sub_path(path)

    path_not_found(sub_path)

    if sub_path.is_dir():
        html = ""

        if path != "":
            parent = Path(path).parent
            parent_href = f"/files/{parent}"

            html += f'<a href="{parent_href}">..</a><br>'

        for item in sub_path.iterdir():
        
            if path:
                href = f"/files/{path}/{item.name}"

            else:
                href = f"/files/{item.name}"
        
            html += f'<a href="{href}">{item.name}</a><br>'

        return HTMLResponse(html)

    elif sub_path.is_file():
        return FileResponse(sub_path)
