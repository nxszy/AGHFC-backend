from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models.firestore_ref import FirestoreRef
from app.models.order import OrderStatus, PersistedOrder
from app.models.user import User, UserRole


@pytest.fixture
def mock_db_ref():
    return MagicMock()


@pytest.fixture
def mock_order():
    return PersistedOrder(
        user_id="user1",
        order_items={"dish1": 2},
        total_price=30.0,
        total_price_including_special_offers=25.0,
        status=OrderStatus.CHECKOUT,
        points_used=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        restaurant_id=MagicMock(spec=FirestoreRef),
    )


def user_with_specified_points(points):
    return User(id="id", email="test@test.test", role=UserRole.CUSTOMER, points=points)


def test_no_loyalty_points_used(mock_order, mock_db_ref):
    user = user_with_specified_points(100)

    mock_order.finalize_users_loyalty_points(user, 0, 0, mock_db_ref)

    assert mock_order.points_used == 0
    assert user.points == 100
    mock_db_ref.collection().document().update.assert_not_called()


def test_loyalty_points_used_within_limits(mock_order, mock_db_ref):
    user = user_with_specified_points(20)

    mock_order.finalize_users_loyalty_points(user, 15, 0, mock_db_ref)

    assert mock_order.points_used == 15
    assert user.points == 5
    mock_db_ref.collection().document.assert_called_with(user.id)
    mock_db_ref.collection().document().update.assert_called_once_with({"points": 5})


def test_loyalty_points_exceeds_user_points(mock_order, mock_db_ref):
    user = user_with_specified_points(10)

    mock_order.finalize_users_loyalty_points(user, 50, 0, mock_db_ref)

    assert mock_order.points_used == 10
    assert user.points == 0
    mock_db_ref.collection().document().update.assert_called_once_with({"points": 0})


def test_loyalty_points_exceeds_price(mock_order, mock_db_ref):
    user = user_with_specified_points(50)
    mock_order.total_price_including_special_offers = 20

    mock_order.finalize_users_loyalty_points(user, 40, 0, mock_db_ref)

    assert mock_order.points_used == 20
    assert user.points == 30
    mock_db_ref.collection().document().update.assert_called_once_with({"points": 30})
