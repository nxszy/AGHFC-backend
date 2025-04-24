from fastapi import HTTPException, status
from firebase_admin import firestore  # type: ignore

from app.models.collection_names import CollectionNames
from app.models.special_offer import SpecialOffer
from app.services.restaurants.shared import check_restaurant_existence


def get_all_special_offers(db_ref: firestore.Client) -> list[dict]:
    special_offers_docs = db_ref.collection(CollectionNames.SPECIAL_OFFERS).stream()
    result = []

    for doc in special_offers_docs:
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
                "original_price": dish_data.get("base_price"),
                "special_price": offer_data.get("special_price"),
            }
        )

    return result


def get_special_offer_by_id(offer_id: str, db_ref: firestore.Client) -> dict:
    offer_doc = db_ref.collection(CollectionNames.SPECIAL_OFFERS).document(offer_id).get()

    if not offer_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Special offer with id {offer_id} not found")

    offer_data = offer_doc.to_dict()
    dish_ref = offer_data.get("dish_id")
    dish_doc = dish_ref.get()

    if not dish_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Dish associated with special offer {offer_id} not found"
        )

    dish_data = dish_doc.to_dict()

    return {
        "id": offer_doc.id,
        "dish_id": dish_ref.id,
        "dish_name": dish_data.get("name"),
        "dish_description": dish_data.get("description"),
        "original_price": dish_data.get("base_price"),
        "special_price": offer_data.get("special_price"),
    }


def create_special_offer(dish_id: str, special_price: float, db_ref: firestore.Client) -> dict:
    dish_ref = db_ref.collection(CollectionNames.DISHES).document(dish_id)
    dish_doc = dish_ref.get()

    if not dish_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dish with id {dish_id} not found")

    dish_data = dish_doc.to_dict()
    original_price = dish_data.get("base_price")

    if original_price is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Dish data is missing price field"
        )

    if special_price >= original_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Special price must be lower than the original price"
        )

    special_offer = SpecialOffer(dish_id=dish_ref, special_price=special_price)
    _, offer_ref = db_ref.collection(CollectionNames.SPECIAL_OFFERS).add(special_offer.model_dump())

    return {
        "id": offer_ref.id,
        "dish_id": dish_id,
        "dish_name": dish_data.get("name"),
        "dish_description": dish_data.get("description"),
        "original_price": original_price,
        "special_price": special_price,
    }


def update_special_offer(offer_id: str, special_price: float, db_ref: firestore.Client) -> dict:
    offer_doc = db_ref.collection(CollectionNames.SPECIAL_OFFERS).document(offer_id).get()

    if not offer_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Special offer with id {offer_id} not found")

    offer_data = offer_doc.to_dict()
    dish_ref = offer_data.get("dish_id")
    dish_doc = dish_ref.get()

    if not dish_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Dish associated with special offer {offer_id} not found"
        )

    dish_data = dish_doc.to_dict()
    original_price = dish_data.get("base_price")

    if original_price is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Dish data is missing price field"
        )

    if special_price >= original_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Special price must be lower than the original price"
        )

    db_ref.collection(CollectionNames.SPECIAL_OFFERS).document(offer_id).update({"special_price": special_price})

    return {
        "id": offer_id,
        "dish_id": dish_ref.id,
        "dish_name": dish_data.get("name"),
        "dish_description": dish_data.get("description"),
        "original_price": original_price,
        "special_price": special_price,
    }


def delete_special_offer(offer_id: str, db_ref: firestore.Client) -> dict:
    offer_doc = db_ref.collection(CollectionNames.SPECIAL_OFFERS).document(offer_id).get()

    if not offer_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Special offer with id {offer_id} not found")

    for restaurant_doc in (
        db_ref.collection(CollectionNames.RESTAURANTS)
        .where("special_offers", "array_contains", db_ref.collection(CollectionNames.SPECIAL_OFFERS).document(offer_id))
        .stream()
    ):
        restaurant_data = restaurant_doc.to_dict()
        special_offers = restaurant_data.get("special_offers", [])
        updated_offers = [offer for offer in special_offers if offer.id != offer_id]
        db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_doc.id).update(
            {"special_offers": updated_offers}
        )

    for user_doc in (
        db_ref.collection(CollectionNames.USERS)
        .where("special_offers", "array_contains", db_ref.collection(CollectionNames.SPECIAL_OFFERS).document(offer_id))
        .stream()
    ):
        user_data = user_doc.to_dict()
        special_offers = user_data.get("special_offers", [])
        updated_offers = [offer for offer in special_offers if offer.id != offer_id]
        db_ref.collection(CollectionNames.USERS).document(user_doc.id).update({"special_offers": updated_offers})

    db_ref.collection(CollectionNames.SPECIAL_OFFERS).document(offer_id).delete()

    return {"message": f"Special offer with id {offer_id} deleted successfully"}


def add_special_offer_to_restaurant(restaurant_id: str, offer_id: str, db_ref: firestore.Client) -> dict:
    restaurant_ref = check_restaurant_existence(restaurant_id, db_ref)
    offer_ref = db_ref.collection(CollectionNames.SPECIAL_OFFERS).document(offer_id)
    offer_doc = offer_ref.get()

    if not offer_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Special offer with id {offer_id} not found")

    restaurant_doc = restaurant_ref.get()
    restaurant_data = restaurant_doc.to_dict()
    special_offers = restaurant_data.get("special_offers", [])

    if any(offer.id == offer_id for offer in special_offers):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Special offer with id {offer_id} already added to restaurant",
        )

    special_offers.append(offer_ref)
    restaurant_ref.update({"special_offers": special_offers})

    return {"message": f"Special offer added to restaurant {restaurant_id} successfully"}


def remove_special_offer_from_restaurant(restaurant_id: str, offer_id: str, db_ref: firestore.Client) -> dict:
    restaurant_ref = check_restaurant_existence(restaurant_id, db_ref)

    restaurant_doc = restaurant_ref.get()
    restaurant_data = restaurant_doc.to_dict()
    special_offers = restaurant_data.get("special_offers", [])

    updated_offers = [offer for offer in special_offers if offer.id != offer_id]

    if len(special_offers) == len(updated_offers):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Special offer with id {offer_id} not found in restaurant {restaurant_id}",
        )

    restaurant_ref.update({"special_offers": updated_offers})

    return {"message": f"Special offer removed from restaurant {restaurant_id} successfully"}
