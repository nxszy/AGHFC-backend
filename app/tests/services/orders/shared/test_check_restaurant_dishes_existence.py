from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status
from google.cloud import firestore

from app.models.order import CreateOrderPayload
from app.services.orders.shared import check_restaurant_dishes_existence


@pytest.fixture
def mock_db_ref():
    return MagicMock(spec=firestore.Client)


@pytest.fixture
def mock_order_payload():
    return CreateOrderPayload(restaurant_id="restaurant123", order_items={"dish1": 1, "dish2": 2})


def test_valid_dishes_exist(mock_order_payload, mock_db_ref):
    dish_refs = [MagicMock() for _ in mock_order_payload.order_items]
    for ref, dish_id in zip(dish_refs, mock_order_payload.order_items.keys()):
        ref.id = dish_id

    mock_db_ref.collection.return_value.document.side_effect = lambda id: next(
        (ref for ref in dish_refs if ref.id == id), MagicMock(id=id)
    )

    def fake_doc(dish_id):
        doc = MagicMock()
        doc.to_dict.return_value = {"dish_id": MagicMock(id=dish_id)}
        return doc

    mock_stream = [fake_doc("dish1"), fake_doc("dish2")]

    restaurant_dishes_collection = MagicMock()
    mock_db_ref.collection.return_value = restaurant_dishes_collection
    restaurant_dishes_collection.where.return_value.where.return_value.stream.return_value = mock_stream

    check_restaurant_dishes_existence(mock_order_payload, mock_db_ref)


def test_invalid_dishes_raise_exception(mock_order_payload, mock_db_ref):
    dish_refs = [MagicMock() for _ in mock_order_payload.order_items]
    for ref, dish_id in zip(dish_refs, mock_order_payload.order_items.keys()):
        ref.id = dish_id

    mock_db_ref.collection.return_value.document.side_effect = lambda id: next(
        (ref for ref in dish_refs if ref.id == id), MagicMock(id=id)
    )

    def fake_doc(dish_id):
        doc = MagicMock()
        doc.to_dict.return_value = {"dish_id": MagicMock(id=dish_id)}
        return doc

    mock_stream = [fake_doc("dish1")]

    restaurant_dishes_collection = MagicMock()
    mock_db_ref.collection.return_value = restaurant_dishes_collection
    restaurant_dishes_collection.where.return_value.where.return_value.stream.return_value = mock_stream

    with pytest.raises(HTTPException) as exc_info:
        check_restaurant_dishes_existence(mock_order_payload, mock_db_ref)

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "dish2" in exc_info.value.detail


def test_empty_order_items_does_nothing(mock_db_ref):
    empty_order = CreateOrderPayload(restaurant_id="restaurant123", order_items={})
    check_restaurant_dishes_existence(empty_order, mock_db_ref)
