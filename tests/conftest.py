import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["APP_DATABASE_URL"] = "sqlite:///./test.db"
os.environ["APP_LOG_FILE"] = "./test_logs/app.log"

from app.main import app


@pytest.fixture(scope="session", autouse=True)
def clean_test_artifacts() -> None:
    """Ensure test db/log files do not leak state across runs."""

    db_file = Path("test.db")
    log_dir = Path("test_logs")

    if db_file.exists():
        db_file.unlink()

    if log_dir.exists():
        for item in log_dir.glob("*"):
            if item.is_file():
                item.unlink()


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
