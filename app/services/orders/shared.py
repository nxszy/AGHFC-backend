from functools import reduce

from fastapi import HTTPException, status
from firebase_admin import firestore  # type: ignore
from google.cloud.firestore import Transaction  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.collection_names import CollectionNames
from app.models.order import CreateOrderPayload, OrderStatus, PersistedOrder
from app.models.restaurant_dish import RestaurantDish
from app.models.special_offer import SpecialOffer
from app.models.user import User


def calculate_order_prices(order: PersistedOrder, user: User, db_ref: firestore.Client) -> tuple[float, float]:
    order_items = order.order_items
    dish_ids = list(order_items.keys())
    dish_refs = [db_ref.collection(CollectionNames.DISHES).document(dish_id) for dish_id in dish_ids]

    dishes_docs = db_ref.get_all(dish_refs)

    order_total = 0.0
    dish_prices_including_special_offers = {}

    for dish in dishes_docs:
        order_total += float(order_items[dish.id] * dish.to_dict().get("base_price"))
        dish_prices_including_special_offers[dish.id] = dish.to_dict().get("base_price")

    restaurant_doc = order.restaurant_id.get().to_dict()

    user_special_offers = [SpecialOffer(**doc.to_dict()) for doc in db_ref.get_all(user.special_offers)]
    restaurant_special_offers = [
        SpecialOffer(**doc.to_dict()) for doc in db_ref.get_all(restaurant_doc.get("special_offers"))
    ]

    for special_offer in user_special_offers + restaurant_special_offers:
        dish_id = special_offer.dish_id.id
        current_best_price = dish_prices_including_special_offers.get(dish_id, float("inf"))

        if current_best_price > special_offer.special_price:
            dish_prices_including_special_offers[dish_id] = special_offer.special_price

    def sum_order_total_special_offers(acc: float, id: str) -> float:
        return acc + float(dish_prices_including_special_offers[id] * order_items[id])

    total_including_discounts = reduce(sum_order_total_special_offers, dish_ids, 0.0)
    return order_total, total_including_discounts


def check_restaurant_dishes_existence(order: CreateOrderPayload, db_ref: firestore.Client) -> None:
    restaurant_id = order.restaurant_id
    dish_ids = list(order.order_items.keys())

    if len(dish_ids) == 0:
        return

    dish_refs = [db_ref.collection(CollectionNames.DISHES).document(dish_id) for dish_id in dish_ids]
    restaurant_ref = db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id)

    restaurant_dishes_docs = (
        db_ref.collection(CollectionNames.RESTAURANT_DISHES)
        .where(filter=FieldFilter("dish_id", "in", dish_refs))
        .where(filter=FieldFilter("restaurant_id", "==", restaurant_ref))
        .stream()
    )

    restaurant_dishes_ids = [doc.to_dict().get("dish_id").id for doc in restaurant_dishes_docs]
    incorrect_dishes_ids = list(set(dish_ids).difference(set(restaurant_dishes_ids)))

    if len(incorrect_dishes_ids) > 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Incorrect dish ids {incorrect_dishes_ids} - did not found dishes with those ids in specified restaurant",
        )


def check_order_validity_and_ownership(
    order_id: str, expected_state: OrderStatus | None, current_user: User | None, db_ref: firestore.Client
) -> PersistedOrder:
    order_doc = db_ref.collection(CollectionNames.ORDERS).document(order_id).get()
    order_dict = order_doc.to_dict() if order_doc.exists else {}

    if not order_doc.exists or (current_user is not None and order_dict.get("user_id") != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No such order with id: {order_id}",
        )

    if expected_state is not None and order_dict.get("status") != expected_state.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot process order with id: {order_id} - incorrect state: {order_dict.get('status')}, expected state: {expected_state.value}",
        )

    return PersistedOrder(**order_dict)


def get_order_by_id(order_id: str, db_ref: firestore.Client) -> PersistedOrder:
    result = PersistedOrder(**db_ref.collection(CollectionNames.ORDERS).document(order_id).get().to_dict())
    return result


def finalize_order_stock(order: PersistedOrder, order_id: str, db_ref: firestore.Client) -> bool:
    @firestore.transactional
    def transaction_logic(transaction: Transaction) -> None:
        restaurant_ref = order.restaurant_id
        dish_ids = list(order.order_items.keys())
        dish_refs = [db_ref.collection(CollectionNames.DISHES).document(dish_id) for dish_id in dish_ids]

        restaurant_dishes_query = (
            db_ref.collection(CollectionNames.RESTAURANT_DISHES)
            .where(filter=FieldFilter("dish_id", "in", dish_refs))
            .where(filter=FieldFilter("restaurant_id", "==", restaurant_ref))
        )

        restaurant_dishes_docs = list(transaction.get(restaurant_dishes_query))

        restaurant_dishes = {doc.id: RestaurantDish(**doc.to_dict()) for doc in restaurant_dishes_docs}
        updated_state = {}

        for restaurant_dish_id, restaurant_dish in restaurant_dishes.items():
            dish_id = restaurant_dish.dish_id.id
            new_stock_state = restaurant_dish.stock_count - order.order_items[dish_id]
            if new_stock_state < 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Cannot process order with id: {order_id} - restaurant dish with id: {dish_id} exceeds current restaurant stock",
                )
            updated_state[restaurant_dish_id] = new_stock_state

        for restaurant_dish_id, stock in updated_state.items():
            doc_ref = db_ref.collection(CollectionNames.RESTAURANT_DISHES).document(restaurant_dish_id)
            transaction.update(doc_ref, {"stock_count": stock})

    transaction = db_ref.transaction()
    transaction_logic(transaction)
    return True
