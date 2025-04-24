from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models.order import PersistedOrder
from app.models.user import User, UserRole
from app.services.orders.shared import calculate_order_prices


@pytest.fixture
def mock_db_ref():
    return MagicMock()


@pytest.fixture
def mock_order():
    mock_restaurant_ref = MagicMock()
    mock_restaurant_ref.get.return_value.to_dict.return_value = {"special_offers": []}

    return PersistedOrder(
        order_items={"dish1": 2, "dish2": 1},
        restaurant_id=mock_restaurant_ref,
        user_id="user1",
        total_price=0.0,
        total_price_including_special_offers=0.0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_user():
    return User(id="user1", email="test@test.com", role=UserRole.CUSTOMER)


def test_calculate_order_prices_without_special_offers(mock_db_ref, mock_order, mock_user):
    mock_dish_docs = [
        MagicMock(id="dish1", to_dict=lambda: {"base_price": 10.0}),
        MagicMock(id="dish2", to_dict=lambda: {"base_price": 20.0}),
    ]
    mock_db_ref.get_all.side_effect = [mock_dish_docs, [], []]
    mock_db_ref.collection.return_value.document.return_value = None

    order_total, total_including_discounts = calculate_order_prices(mock_order, mock_user, mock_db_ref)

    assert order_total == 40.0
    assert total_including_discounts == 40.0


def test_calculate_order_prices_with_special_offers(mock_db_ref, mock_order, mock_user):
    mock_dish_docs = [
        MagicMock(id="dish1", to_dict=lambda: {"base_price": 10.0}),
        MagicMock(id="dish2", to_dict=lambda: {"base_price": 20.0}),
    ]

    mock_user.special_offers = [MagicMock()]
    restaurant_special_offers = [MagicMock()]

    dish_1_id = MagicMock()
    dish_1_id.id = "dish1"

    dish_2_id = MagicMock()
    dish_2_id.id = "dish2"

    mock_user.special_offers[0].to_dict.return_value = {"dish_id": dish_1_id, "special_price": 5.0}
    restaurant_special_offers[0].to_dict.return_value = {"dish_id": dish_2_id, "special_price": 15.0}

    mock_db_ref.get_all.side_effect = [mock_dish_docs, mock_user.special_offers, restaurant_special_offers]

    order_total, total_including_discounts = calculate_order_prices(mock_order, mock_user, mock_db_ref)

    assert order_total == 40.0  # 2 * 10 + 1 * 20
    assert total_including_discounts == 25.0  # 2 * 5 + 1 * 15
