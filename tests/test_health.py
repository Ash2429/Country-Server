import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from app.main import app
from app.settings import settings


def _mongo_is_reachable() -> bool:
    client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=500)
    try:
        client.admin.command("ping")
        return True
    except ServerSelectionTimeoutError:
        return False
    finally:
        client.close()


@pytest.mark.skipif(
    not _mongo_is_reachable(),
    reason="requires a running Mongo instance (docker compose up -d mongo)",
)
def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
