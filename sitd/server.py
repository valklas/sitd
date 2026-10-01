import html, hashlib
from pathlib import Path

from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
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


def get_file_etag(path):
    stat = path.stat()
    value = f"{stat.st_mtime_ns}-{stat.st_size}".encode()
    return f'"{hashlib.sha256(value).hexdigest()}"'


def get_last_modified(path):
    modified_time = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

    return modified_time.replace(microsecond=0)


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
        return JSONResponse(
            content=file_entry,
            headers={
                "Cache-Control": "private, max-age=10"
            }
        )


@app.get("/api/content/{path:path}")
def get_file_content(path: str, if_none_match: str | None = Header(default=None), if_modified_since: str | None = Header(default=None)):
    target_path = get_target_path(path)
    validate_path_exists(target_path)

    if not target_path.is_file():
        raise HTTPException(status_code=404, detail="Not a file")

    etag = get_file_etag(target_path)
    last_modified = get_last_modified(target_path)

    headers = {
        "Cache-Control": "private, max-age=60", "ETag": etag, "Last-Modified": format_datetime(last_modified, usegmt=True)
    }

    if if_none_match == etag:
        return Response(status_code=304, headers=headers)
    
    if if_modified_since:
        modified_since = parsedate_to_datetime(if_modified_since)
    
        last_modified = datetime.fromtimestamp(target_path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0)
    
        if last_modified <= modified_since:
            return Response(status_code=304, headers=headers)

    mime_type = get_mime_type(target_path)

    if mime_type is None:
        return FileResponse(target_path, filename=target_path.name, content_disposition_type="attachment", headers=headers)

    return FileResponse(target_path, media_type=mime_type, headers=headers)


@app.get("/files/{path:path}")
def serve_sub_files(path: str):
    target_path = get_target_path(path)

    validate_path_exists(target_path)

    if target_path:
        return FileResponse("sitd/static/index.html")
