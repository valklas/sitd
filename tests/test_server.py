from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

import sitd.server
from sitd.server import app
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


def test_api_directory(test_storage):
    response = client.get("/api/files/5_dir")

    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, list)
    assert len(result) == 4

    assert_entries_valid(result, test_storage)


def test_api_nested_directory(test_storage):
    response = client.get(
        "/api/files/5_dir/4_dir/3_dir/2_dir/1_dir"
    )

    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, list)
    assert len(result) == 3

    assert_entries_valid(result, test_storage)


def test_api_file(test_storage):
    response = client.get("/api/files/1.txt")

    assert response.status_code == 200

    result = response.json()

    assert result["name"] == "1.txt"
    assert result["type"] == "file"
    assert result["path"] == "1.txt"
    assert result["file_size"] == 23


def test_api_file_not_found(test_storage):
    response = client.get("/api/files/does-not-exist")

    assert response.status_code == 404


def test_api_files_cannot_escape_storage(test_storage):
    outside_file = test_storage.parent / "secret.txt"
    outside_file.write_text("secret")

    response = client.get("/api/files/../secret.txt")

    assert response.status_code == 404


def test_root_redirects_to_files(test_storage):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/files"


def test_serve_files_root(test_storage):
    response = client.get("/files")

    assert response.status_code == 200
    assert "<title>SITD (Serve It To Devices)</title>" in response.text


def test_serve_directory(test_storage):
    response = client.get("/files/5_dir")

    assert response.status_code == 200
    assert "<title>SITD (Serve It To Devices)</title>" in response.text


def test_serve_nested_directory(test_storage):
    response = client.get(
        "/files/5_dir/4_dir/3_dir"
    )

    assert response.status_code == 200
    assert "<title>SITD (Serve It To Devices)</title>" in response.text


def test_serve_file(test_storage):
    response = client.get("/files/1.txt")

    assert response.status_code == 200
    assert response.text == "This is the 1.txt file."


def test_serve_nested_file(test_storage):
    response = client.get(
        "/files/5_dir/4_dir/3_dir/2_dir/1_dir/1.txt"
    )

    assert response.status_code == 200
    assert response.text == "This is the 1.txt file."


def test_serve_file_not_found(test_storage):
    response = client.get("/files/does-not-exist")

    assert response.status_code == 404


def test_files_cannot_escape_storage(test_storage):
    outside_file = test_storage.parent / "secret.txt"
    outside_file.write_text("secret")

    response = client.get("/files/../secret.txt")

    assert response.status_code == 404


def test_get_target_path(test_storage):
    result = sitd.server.get_target_path("1.txt")

    assert result == test_storage / "1.txt"


def test_get_nested_target_path(test_storage):
    result = sitd.server.get_target_path(
        "5_dir/4_dir/1.txt"
    )

    assert result == test_storage / "5_dir/4_dir/1.txt"


def test_get_target_path_cannot_escape_storage(test_storage):
    with pytest.raises(HTTPException) as exc_info:
        sitd.server.get_target_path("../../sec.txt")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Naughty you..."


def test_validate_path_exists(test_storage):
    path = test_storage / "1.txt"

    sitd.server.validate_path_exists(path)


def test_validate_path_does_not_exist(test_storage):
    path = test_storage / "does-not-exist"

    with pytest.raises(HTTPException) as exc_info:
        sitd.server.validate_path_exists(path)

    assert exc_info.value.status_code == 404
