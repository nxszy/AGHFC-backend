from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from google.cloud.firestore_v1 import DocumentReference

from app.models.order import OrderStatus, PersistedOrder
from app.services.orders.worker_panel import transition_order_status


@pytest.fixture
def mock_db_ref():
    return MagicMock()


@pytest.fixture
def mock_order():
    return PersistedOrder(
        user_id="user1",
        order_items={"dish1": 1},
        total_price=20.0,
        total_price_including_special_offers=20.0,
        status=OrderStatus.PAID,
        points_used=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        restaurant_id=MagicMock(spec=DocumentReference, id="rest1"),
    )


@pytest.mark.parametrize(
    "target_status,expected_from_status",
    [
        (OrderStatus.IN_PROGRESS, OrderStatus.PAID),
        (OrderStatus.READY, OrderStatus.IN_PROGRESS),
        (OrderStatus.COMPLETED, OrderStatus.READY),
    ],
)
@patch("app.services.orders.worker_panel.check_order_validity_and_ownership")
def test_successful_transition(mock_check_order, mock_order, mock_db_ref, target_status, expected_from_status):
    mock_check_order.return_value = mock_order
    restaurant_ref = MagicMock(spec=DocumentReference, id="rest1")

    result = transition_order_status("order123", restaurant_ref, target_status, mock_db_ref)

    assert result.status == target_status
    assert isinstance(result.updated_at, datetime)
    mock_check_order.assert_called_once_with("order123", expected_from_status, None, mock_db_ref)


def test_invalid_transition_raises_error(mock_db_ref):
    with pytest.raises(HTTPException) as e:
        transition_order_status("order123", MagicMock(spec=DocumentReference), OrderStatus.CHECKOUT, mock_db_ref)

    assert e.value.status_code == 422
    assert "Incorrect state to transition" in e.value.detail


@patch("app.services.orders.worker_panel.check_order_validity_and_ownership")
def test_wrong_restaurant_id_raises_error(mock_check_order, mock_order, mock_db_ref):
    mock_order.restaurant_id.id = "rest1"
    mock_check_order.return_value = mock_order

    wrong_restaurant_ref = MagicMock(spec=DocumentReference, id="rest999")

    with pytest.raises(HTTPException) as e:
        transition_order_status("order123", wrong_restaurant_ref, OrderStatus.IN_PROGRESS, mock_db_ref)

    assert e.value.status_code == 422
    assert "No such order with id" in e.value.detail
