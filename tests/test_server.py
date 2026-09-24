from fastapi.testclient import TestClient
from pathlib import Path

from sitd.server import app
import sitd.server

from tempfile import TemporaryDirectory


client = TestClient(app)


def create_test_tree(root_dir):
    (root_dir / "1.txt").write_text("This is 1.txt")
    (root_dir / "2.txt").write_text("This is 2.txt")

    some_dir = root_dir / "some_dir"
    some_dir.mkdir()

    (some_dir / "3.txt").write_text("This is 3.txt")


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from SITD!"}


def test_api_files():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)
        create_test_tree(root_dir)

        old_storage_path = sitd.server.storage_path
        sitd.server.storage_path = root_dir

        try:
            response = client.get("/api/files")

            assert response.status_code == 200

            data = response.json()

            assert isinstance(data, list)
            assert len(data) == 3

        finally:
            sitd.server.storage_path = old_storage_path


def test_api_files_directory():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)
        create_test_tree(root_dir)

        old_storage_path = sitd.server.storage_path
        sitd.server.storage_path = root_dir

        try:
            response = client.get("/api/files/some_dir")

            assert response.status_code == 200

            data = response.json()

            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["name"] == "3.txt"
            assert data[0]["type"] == "file"

        finally:
            sitd.server.storage_path = old_storage_path


def test_api_files_file():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)
        create_test_tree(root_dir)

        old_storage_path = sitd.server.storage_path
        sitd.server.storage_path = root_dir

        try:
            response = client.get("/api/files/1.txt")

            assert response.status_code == 200

            data = response.json()

            assert data["name"] == "1.txt"
            assert data["type"] == "file"
            assert data["file_size"] == (root_dir / "1.txt").stat().st_size

        finally:
            sitd.server.storage_path = old_storage_path


def test_api_files_not_found():
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir)

        old_storage_path = sitd.server.storage_path
        sitd.server.storage_path = root_dir

        try:
            response = client.get("/api/files/does-not-exist")

            assert response.status_code == 404

        finally:
            sitd.server.storage_path = old_storage_path
