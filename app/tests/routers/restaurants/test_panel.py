from unittest.mock import MagicMock

from fastapi import status
from google.auth.credentials import AnonymousCredentials  # type: ignore
from google.cloud import firestore  # type: ignore

BASE_URL = "/restaurant/panel"


def test_get_restaurant_by_id_success(
    mock_authorized_client,
):

    response = mock_authorized_client.get(
        f"{BASE_URL}/get_restaurant_by_id/1",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Pizza Place"


def test_get_restaurant_by_id_not_found(
    mock_authorized_client,
    mock_db_ref,
):
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db_ref.collection.return_value.document.return_value.get.return_value = mock_doc

    response = mock_authorized_client.get(
        f"{BASE_URL}/get_restaurant_by_id/resXYZ",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Restaurant not found"


def test_add_restaurant(
    mock_authorized_client,
):
    restaurant_data = {
        "id": None,
        "name": "Test Bistro",
        "city": "Breslau",
        "address": "Watykanska 12",
        "opening_hours": "9 AM - 10 PM",
        "special_offers": [],
    }

    response = mock_authorized_client.post(
        f"{BASE_URL}/add_restaurant",
        json=restaurant_data,
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == restaurant_data


def test_update_restaurant(
    mock_authorized_client,
):
    restaurant_data = {
        "id": "1",
        "name": "Test Bistro",
        "city": "Breslau",
        "address": "Watykanska 12",
        "opening_hours": "9 AM - 10 PM",
        "special_offers": [],
    }

    response = mock_authorized_client.put(
        f"{BASE_URL}/update_restaurant/res789",
        json=restaurant_data,
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == restaurant_data


def test_delete_restaurant(
    mock_authorized_client,
):
    response = mock_authorized_client.delete(
        f"{BASE_URL}/delete_restaurant/res999",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Restaurant deleted successfully"


def test_update_special_offers(
    mock_authorized_client,
):
    special_offers = ["offer1", "offer2"]

    response = mock_authorized_client.put(
        f"{BASE_URL}/update_special_offers/res123",
        json=special_offers,
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Special offers updated successfully"


def test_update_menu(mock_authorized_client, mock_db_ref):

    def create_fake_doc_ref(collection="restaurants", doc_id="test_id"):
        client = firestore.Client(project="test-project", credentials=AnonymousCredentials())
        return client.collection(collection).document(doc_id)

    mock_doc_ref = create_fake_doc_ref("test", "test")

    mock_db_ref.collection.return_value.document.return_value = mock_doc_ref
    mock_db_ref.collection.return_value.add.return_value = True

    response = mock_authorized_client.put(
        f"{BASE_URL}/update_menu/res123?dish_id=dish456",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Restaurant menu updated successfully"
