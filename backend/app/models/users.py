from __future__ import annotations

import re
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import Base, person_fk, uuid_pk
from .people import Person


class User(Base):
    """
    A user of the system, for authentication and authorization purposes.

    In a production system, authentication would be through some enterprise
    identity provider (e.g., OAuth, SAML, etc.) and we would not store passwords.
    """

    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    person_id: Mapped[Optional[person_fk]]
    refresh_token_hash: Mapped[Optional[str]] = mapped_column(default=None)

    person: Mapped[Optional["Person"]] = relationship()

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} is_active={self.is_active}>"

    @validates("email")
    def validate_email(self, address):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", address):
            raise ValueError("Invalid email address")
        return address.lower()
