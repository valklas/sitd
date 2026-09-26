import html
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .filesystem import get_mime_type, inspect_dir


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


def generate_file(path):
    with open(path, "rb") as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            yield chunk


def generate_view(path):
    file_name = html.escape(path.name)
    yield f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{file_name}</title>

        <link rel="icon" href="/static/assets/SITDWEBLOGO.svg">
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <h1>{file_name}</h1>
        
        <pre>"""

    for chunk in generate_file(path):
        yield html.escape(chunk.decode("utf-8"))

    yield """</pre>
    </body>
    </html>"""


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
            "file_size": target_path.stat().st_size,
            "mime_type": get_mime_type(target_path)
        }
        return file_entry


@app.get("/files/{path:path}")
def serve_sub_files(path: str):
    target_path = get_target_path(path)

    validate_path_exists(target_path)

    if target_path.is_file():
        mime_type = get_mime_type(target_path)

        if mime_type and mime_type.startswith("text/"):
            return RedirectResponse(f"/view/{path}")

    elif target_path.is_dir():
            return FileResponse("sitd/static/index.html")


@app.get("/view/{path:path}")
def view_file(path: str):
    target_path = get_target_path(path)
    validate_path_exists(target_path)

    if not target_path.is_file():
        raise HTTPException(status_code=404, detail="Not a file")

    mime_type = get_mime_type(target_path)
    
    if mime_type and mime_type.startswith("text/"):
        return StreamingResponse(generate_view(target_path), media_type="text/html")

    elif mime_type is None:
        return FileResponse(target_path, filename=target_path.name, content_disposition_type="attachment")
    
    else:
        return FileResponse(target_path, media_type=mime_type)
