from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from google.cloud.firestore import Transaction

from app.models.firestore_ref import FirestoreRef
from app.models.order import PersistedOrder
from app.services.orders.shared import finalize_order_stock


@pytest.fixture
def mock_db_ref():
    return MagicMock()


@pytest.fixture
def mock_order():
    return PersistedOrder(
        order_items={"dish1": 2, "dish2": 1},
        restaurant_id=MagicMock(spec=FirestoreRef),
        user_id="user1",
        total_price=0.0,
        total_price_including_special_offers=0.0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def make_restaurant_dish_doc(doc_id, dish_id, stock_count):
    doc = MagicMock()
    doc.id = doc_id
    doc.to_dict.return_value = {
        "dish_id": MagicMock(id=dish_id),
        "restaurant_id": MagicMock(),
        "stock_count": stock_count,
        "is_available": True,
    }
    return doc


@patch("app.services.orders.shared.firestore.transactional", lambda f: f)  # skip transactional decorator logic
def test_finalize_order_success(mock_order, mock_db_ref):
    mock_transaction = MagicMock(spec=Transaction)
    mock_db_ref.transaction.return_value = mock_transaction

    dish1_doc = make_restaurant_dish_doc("rd1", "dish1", stock_count=5)
    dish2_doc = make_restaurant_dish_doc("rd2", "dish2", stock_count=2)

    mock_db_ref.collection.return_value.where.return_value.where.return_value = MagicMock()
    mock_transaction.get.return_value = [dish1_doc, dish2_doc]

    result = finalize_order_stock(mock_order, "order1", mock_db_ref)

    assert result is True
    assert mock_transaction.update.call_count == 2
    mock_transaction.update.assert_any_call(mock_db_ref.collection().document("rd1"), {"stock_count": 3})
    mock_transaction.update.assert_any_call(mock_db_ref.collection().document("rd2"), {"stock_count": 1})


@patch("app.services.orders.shared.firestore.transactional", lambda f: f)
def test_finalize_order_insufficient_stock(mock_order, mock_db_ref):
    mock_transaction = MagicMock(spec=Transaction)
    mock_db_ref.transaction.return_value = mock_transaction

    dish1_doc = make_restaurant_dish_doc("rd1", "dish1", stock_count=1)  # Not enough for quantity=2
    dish2_doc = make_restaurant_dish_doc("rd2", "dish2", stock_count=5)

    mock_db_ref.collection.return_value.where.return_value.where.return_value = MagicMock()
    mock_transaction.get.return_value = [dish1_doc, dish2_doc]

    with pytest.raises(HTTPException) as exc_info:
        finalize_order_stock(mock_order, "order2", mock_db_ref)

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "exceeds current restaurant stock" in exc_info.value.detail
    mock_transaction.update.assert_not_called()
