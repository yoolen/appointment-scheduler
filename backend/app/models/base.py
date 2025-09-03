from __future__ import annotations

from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.types import String as SQLString
from sqlalchemy.types import TypeDecorator
from typing_extensions import Annotated

int_pk = Annotated[int, mapped_column(primary_key=True, index=True)]
uuid_pk = Annotated[
    str,
    mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())),
]
person_fk = Annotated[int, mapped_column(ForeignKey("people.id"))]


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class ZoneInfoType(TypeDecorator):  # pylint: disable=abstract-method
    """
    Custom SQLAlchemy type for storing ZoneInfo objects as strings in the database.
    """

    impl = SQLString
    cache_ok = True

    def process_bind_param(self, value: ZoneInfo | None, dialect: Any) -> str | None:
        return str(value) if value is not None else None

    def process_result_value(self, value, dialect: Any) -> ZoneInfo | None:
        return ZoneInfo(value) if value is not None else None
