from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

import sitd.server
from sitd.server import (
    app,
    get_target_path,
    validate_path_exists
)
from tests.helpers import assert_entries_valid, create_test_tree


client = TestClient(app)


@pytest.fixture
def test_storage():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)
        create_test_tree(root_dir, 5)

        old_storage_path = sitd.server.storage_path
        sitd.server.storage_path = root_dir

        try:
            yield root_dir
        finally:
            sitd.server.storage_path = old_storage_path


def test_api_files(test_storage):
    response = client.get("/api/files")

    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, list)
    assert len(result) == 4

    assert_entries_valid(result, test_storage)


def test_api_files_directory(test_storage):
    response = client.get("/api/files/5_dir")

    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, list)
    assert len(result) == 4

    assert_entries_valid(result, test_storage)


def test_api_files_nested_directory(test_storage):
    response = client.get("/api/files/5_dir/4_dir")

    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, list)
    assert len(result) == 4

    assert_entries_valid(result, test_storage)


def test_api_files_file(test_storage):
    response = client.get("/api/files/1.txt")

    assert response.status_code == 200

    result = response.json()

    assert result["name"] == "1.txt"
    assert result["type"] == "file"
    assert result["path"] == "1.txt"
    assert result["file_size"] == (test_storage / "1.txt").stat().st_size
    assert result["mime_type"] == "text/plain"


def test_api_files_nested_file(test_storage):
    response = client.get("/api/files/5_dir/4_dir/3_dir/1.txt")

    assert response.status_code == 200

    result = response.json()

    assert result["name"] == "1.txt"
    assert result["type"] == "file"
    assert result["path"] == "5_dir/4_dir/3_dir/1.txt"
    assert result["mime_type"] == "text/plain"


def test_api_files_not_found(test_storage):
    response = client.get("/api/files/does-not-exist.txt")

    assert response.status_code == 404


def test_api_files_path_traversal(test_storage):
    response = client.get("/api/files/%2E%2E/%2E%2E/etc/passwd")

    assert response.status_code == 404


def test_files_root(test_storage):
    response = client.get("/files")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_files_root_with_slash(test_storage):
    response = client.get("/files/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_files_directory(test_storage):
    response = client.get("/files/5_dir")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_files_nested_directory(test_storage):
    response = client.get("/files/5_dir/4_dir")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_files_file(test_storage):
    response = client.get("/files/1.txt")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>1.txt</title>" in response.text
    assert "<h1>1.txt</h1>" in response.text
    assert "This is the 1.txt file." in response.text


def test_files_nested_file(test_storage):
    response = client.get("/files/5_dir/4_dir/3_dir/1.txt")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>1.txt</title>" in response.text
    assert "<h1>1.txt</h1>" in response.text
    assert "This is the 1.txt file." in response.text


def test_files_not_found(test_storage):
    response = client.get("/files/does-not-exist.txt")

    assert response.status_code == 404


def test_files_path_traversal(test_storage):
    response = client.get("/files/%2E%2E/%2E%2E/etc/passwd")

    assert response.status_code == 404


def test_view_text_file(test_storage):
    file = test_storage / "hello.txt"
    file.write_text("Hello, world!")

    response = client.get("/view/hello.txt")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Hello, world!" in response.text


def test_view_text_file_escapes_html(test_storage):
    file = test_storage / "hello.html"
    file.write_text("<script>alert('hello')</script>")

    response = client.get("/view/hello.html")

    assert response.status_code == 200
    assert "&lt;script&gt;" in response.text
    assert "<script>" not in response.text


def test_view_text_file_utf8(test_storage):
    file = test_storage / "unicode.txt"
    file.write_text(
        "Hello — اردو — 日本語 — 😀",
        encoding="utf-8",
    )

    response = client.get("/view/unicode.txt")

    assert response.status_code == 200
    assert "Hello — اردو — 日本語 — 😀" in response.text


def test_view_nested_text_file(test_storage):
    directory = test_storage / "view_test"
    directory.mkdir()

    file = directory / "hello.txt"
    file.write_text("Hello from a nested file!")

    response = client.get("/view/view_test/hello.txt")

    assert response.status_code == 200
    assert "Hello from a nested file!" in response.text


def test_view_text_file_name(test_storage):
    file = test_storage / "hello.txt"
    file.write_text("Hello!")

    response = client.get("/view/hello.txt")

    assert response.status_code == 200
    assert "<title>hello.txt</title>" in response.text
    assert "<h1>hello.txt</h1>" in response.text


def test_view_directory(test_storage):
    directory = test_storage / "directory"
    directory.mkdir()

    response = client.get("/view/directory")

    assert response.status_code == 404


def test_view_not_found(test_storage):
    response = client.get("/view/does-not-exist.txt")

    assert response.status_code == 404


def test_view_path_traversal(test_storage):
    response = client.get("/view/%2E%2E/%2E%2E/etc/passwd")

    assert response.status_code == 404


def test_view_unknown_mime_type(test_storage):
    file = test_storage / "something.sitdtest"
    file.write_bytes(b"Some unknown file")

    response = client.get("/view/something.sitdtest")

    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]


def test_view_image(test_storage):
    file = test_storage / "image.jpg"
    file.write_bytes(b"fake image data")

    response = client.get("/view/image.jpg")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/jpeg")


def test_get_target_path(test_storage):
    result = get_target_path("1.txt")

    assert result == test_storage / "1.txt"


def test_get_target_path_nested(test_storage):
    result = get_target_path("5_dir/4_dir/1.txt")

    assert result == test_storage / "5_dir/4_dir/1.txt"


def test_get_target_path_traversal(test_storage):
    with pytest.raises(HTTPException) as error:
        get_target_path("../../etc/passwd")

    assert error.value.status_code == 404


def test_get_target_path_absolute_traversal(test_storage):
    with pytest.raises(HTTPException) as error:
        get_target_path("/etc/passwd")

    assert error.value.status_code == 404


def test_validate_path_exists(test_storage):
    path = test_storage / "1.txt"

    result = validate_path_exists(path)

    assert result is None


def test_validate_path_exists_missing(test_storage):
    path = test_storage / "does-not-exist.txt"

    with pytest.raises(HTTPException) as error:
        validate_path_exists(path)

    assert error.value.status_code == 404
