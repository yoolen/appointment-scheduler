from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, int_pk, person_fk
from .people import Person


class User(Base):
    """
    A user of the system, for authentication and authorization purposes.

    In a production system, authentication would be through some enterprise
    identity provider (e.g., OAuth, SAML, etc.) and we would not store passwords.
    """

    __tablename__ = "users"

    id: Mapped[int_pk]
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    person_id: Mapped[Optional[person_fk]]

    person: Mapped[Optional["Person"]] = relationship()

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} username={self.username} is_active={self.is_active}>"
        )
