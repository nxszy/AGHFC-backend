from firebase_admin import firestore  # type: ignore


def get_database_ref() -> firestore.Client:
    """Get a reference to the Firestore database.

    Returns:
        firestore.Client: A Firestore client instance.
    """
    return firestore.client()
