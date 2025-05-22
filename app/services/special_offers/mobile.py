import random

from fastapi import HTTPException, status
from firebase_admin import firestore  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.collection_names import CollectionNames
from app.models.special_offer import SpecialOffer
from app.models.user import User
from app.services.restaurants.shared import check_restaurant_existence


def get_restaurant_special_offers(restaurant_id: str, db_ref: firestore.Client) -> list[dict]:
    restaurant_ref = check_restaurant_existence(restaurant_id, db_ref)
    restaurant_doc = restaurant_ref.get()

    if not restaurant_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Restaurant with id {restaurant_id} not found"
        )

    restaurant_data = restaurant_doc.to_dict()
    special_offer_refs = restaurant_data.get("special_offers", [])

    if not special_offer_refs:
        return []

    special_offers_docs = db_ref.get_all(special_offer_refs)
    result = []

    for doc in special_offers_docs:
        if not doc.exists:
            continue

        offer_data = doc.to_dict()
        dish_ref = offer_data.get("dish_id")
        dish_doc = dish_ref.get()

        if not dish_doc.exists:
            continue

        dish_data = dish_doc.to_dict()

        result.append(
            {
                "id": doc.id,
                "name": offer_data.get("name"),
                "dish_id": dish_ref.id,
                "dish_name": dish_data.get("name"),
                "dish_description": dish_data.get("description"),
                "original_price": dish_data.get("price"),
                "special_price": offer_data.get("special_price"),
            }
        )

    return result


def get_user_special_offers(user: User, db_ref: firestore.Client) -> list[dict]:
    if not user.special_offers:
        return []

    special_offers_docs = db_ref.get_all(user.special_offers)
    result = []

    for doc in special_offers_docs:
        if not doc.exists:
            continue

        offer_data = doc.to_dict()
        dish_ref = offer_data.get("dish_id")
        dish_doc = dish_ref.get()

        if not dish_doc.exists:
            continue

        dish_data = dish_doc.to_dict()

        result.append(
            {
                "id": doc.id,
                "dish_id": dish_ref.id,
                "dish_name": dish_data.get("name"),
                "dish_description": dish_data.get("description"),
                "original_price": dish_data.get("price"),
                "special_price": offer_data.get("special_price"),
            }
        )

    return result


def generate_special_offer_for_user(user: User, restaurant_id: str, db_ref: firestore.Client) -> dict:
    restaurant_ref = check_restaurant_existence(restaurant_id, db_ref)

    # Using only one db filter to avoid the composite index requirement
    restaurant_dishes = (
        db_ref.collection(CollectionNames.RESTAURANT_DISHES)
        .where(filter=FieldFilter("restaurant_id", "==", restaurant_ref))
        .stream()
    )

    dish_refs = []
    for dish_doc in restaurant_dishes:
        dish_data = dish_doc.to_dict()
        if dish_data.get("is_available", False) and dish_data.get("stock_count", 0) > 0:
            dish_refs.append(dish_data.get("dish_id"))

    if not dish_refs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No available dishes found for restaurant with id {restaurant_id}",
        )

    selected_dish_ref = random.choice(dish_refs)
    dish_doc = selected_dish_ref.get()

    if not dish_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selected dish not found")

    dish_data = dish_doc.to_dict()
    original_price = dish_data.get("base_price")

    if original_price is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Dish data is missing base_price field"
        )

    special_price = round(original_price * (1 - random.uniform(0.1, 0.9)), 2)

    _, special_offer_ref = db_ref.collection(CollectionNames.SPECIAL_OFFERS).add(
        SpecialOffer(dish_id=selected_dish_ref, special_price=special_price).model_dump()
    )

    user_special_offers = user.special_offers.copy() if user.special_offers else []
    user_special_offers.append(special_offer_ref)

    db_ref.collection(CollectionNames.USERS).document(user.id).update({"special_offers": user_special_offers})

    return {
        "id": special_offer_ref.id,
        "dish_id": selected_dish_ref.id,
        "dish_name": dish_data.get("name"),
        "dish_description": dish_data.get("description"),
        "original_price": original_price,
        "special_price": special_price,
    }
