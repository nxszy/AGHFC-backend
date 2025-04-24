from typing import Any
from unittest.mock import MagicMock

from google.cloud.firestore_v1 import DocumentReference
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class FirestoreRef:
    def __init__(self, ref: DocumentReference):
        self.ref = ref

    def __getattr__(self, name: str) -> Any:
        # Delegate everything else to the actual DocumentReference
        return getattr(self.ref, name)

    def __repr__(self) -> str:
        return f"FirestoreRef({repr(self.ref)})"

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, FirestoreRef):
            return self.ref == other.ref
        if isinstance(other, DocumentReference):
            return self.ref == other
        return False

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> "FirestoreRef":
        if isinstance(v, DocumentReference):
            return cls(v)
        if isinstance(v, cls):
            return v
        if isinstance(v, MagicMock):
            return v
        raise TypeError(f"Expected DocumentReference or FirestoreRef, got {type(v)}")
