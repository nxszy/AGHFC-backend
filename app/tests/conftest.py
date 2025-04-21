from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_database_ref
from app.main import app


@pytest.fixture
def mock_db_ref() -> MagicMock:
    mock_doc1 = MagicMock()
    mock_doc1.to_dict.return_value = {
        "id": "1",
        "name": "Pizza Place",
        "city": "Cracow",
        "address": "Krakowska 1",
        "opening_hours": "10:00-22:00",
    }

    mock_doc2 = MagicMock()
    mock_doc2.to_dict.return_value = {
        "id": "2",
        "name": "Sushi Corner",
        "city": "Warsaw",
        "address": "Warszawska 2",
        "opening_hours": "11:00-23:00",
    }

    mock_collection = MagicMock()
    mock_collection.stream.return_value = [mock_doc1, mock_doc2]
    mock_collection.document.return_value.get.return_value = mock_doc1

    mock_db = MagicMock()
    mock_db.collection.return_value = mock_collection

    return mock_db


@pytest.fixture
def mock_authorized_client(mock_db_ref) -> Any:

    with patch("app.core.middleware.verify_firebase_token") as mock_verify:
        mock_verify.return_value = {"uid": "test_user_id", "email": "test@example.com", "name": "Test User"}

        app.dependency_overrides[get_database_ref] = lambda: mock_db_ref

        with TestClient(app) as test_client:
            yield test_client

        app.dependency_overrides.clear()
