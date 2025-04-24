from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from app.models.order import OrderStatus, PersistedOrder
from app.models.user import User, UserRole
from app.services.orders.shared import check_order_validity_and_ownership


@pytest.fixture
def mock_db_ref():
    return MagicMock()


@pytest.fixture
def current_user():
    return User(id="user123", email="test@example.com", name="Test User", role=UserRole.CUSTOMER)


def make_order_doc(user_id="user123", status=OrderStatus.CHECKOUT, exists=True):
    doc = MagicMock()
    doc.exists = exists
    doc.to_dict.return_value = (
        {
            "user_id": user_id,
            "status": status,
            "order_items": {"dish1": 2},
            "restaurant_id": MagicMock(),
            "total_price": 20.0,
            "total_price_including_special_offers": 18.0,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        if exists
        else {}
    )
    return doc


def test_valid_order_and_user(mock_db_ref, current_user):
    mock_doc = make_order_doc(user_id=current_user.id, status=OrderStatus.CHECKOUT.value)
    mock_db_ref.collection.return_value.document.return_value.get.return_value = mock_doc

    order = check_order_validity_and_ownership(
        order_id="order1", expected_state=OrderStatus.CHECKOUT, current_user=current_user, db_ref=mock_db_ref
    )

    assert isinstance(order, PersistedOrder)
    assert order.user_id == current_user.id


def test_order_does_not_exist(mock_db_ref, current_user):
    mock_doc = make_order_doc(exists=False)
    mock_db_ref.collection.return_value.document.return_value.get.return_value = mock_doc

    with pytest.raises(HTTPException) as e:
        check_order_validity_and_ownership(
            order_id="order_missing", expected_state=OrderStatus.CHECKOUT, current_user=current_user, db_ref=mock_db_ref
        )

    assert e.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "No such order" in e.value.detail


def test_order_belongs_to_different_user(mock_db_ref, current_user):
    mock_doc = make_order_doc(user_id="someone_else", status=OrderStatus.CHECKOUT.value)
    mock_db_ref.collection.return_value.document.return_value.get.return_value = mock_doc

    with pytest.raises(HTTPException) as e:
        check_order_validity_and_ownership(
            order_id="order_wrong_user",
            expected_state=OrderStatus.CHECKOUT,
            current_user=current_user,
            db_ref=mock_db_ref,
        )

    assert e.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "No such order" in e.value.detail


def test_order_status_mismatch(mock_db_ref, current_user):
    mock_doc = make_order_doc(user_id=current_user.id, status=OrderStatus.COMPLETED)
    mock_db_ref.collection.return_value.document.return_value.get.return_value = mock_doc

    with pytest.raises(HTTPException) as e:
        check_order_validity_and_ownership(
            order_id="order_wrong_status",
            expected_state=OrderStatus.CHECKOUT,
            current_user=current_user,
            db_ref=mock_db_ref,
        )

    assert e.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "incorrect state" in e.value.detail


def test_no_user_check(mock_db_ref):
    mock_doc = make_order_doc(user_id="user123", status=OrderStatus.CHECKOUT)
    mock_db_ref.collection.return_value.document.return_value.get.return_value = mock_doc

    order = check_order_validity_and_ownership(
        order_id="order_no_user_check", expected_state=OrderStatus.CHECKOUT, current_user=None, db_ref=mock_db_ref
    )

    assert isinstance(order, PersistedOrder)
