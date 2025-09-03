from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, ZoneInfoType, int_pk

if TYPE_CHECKING:
    from .people import Doctor, Staff


class Hospital(Base):
    """
    The location doctors and staff work out of; where a patient goes for an appointment.
    """

    __tablename__ = "hospitals"

    id: Mapped[int_pk]
    name: Mapped[str]
    address: Mapped[str]
    timezone: Mapped[ZoneInfo] = mapped_column(ZoneInfoType(50))
    open_time: Mapped[time]
    close_time: Mapped[time]

    doctors: Mapped[list["Doctor"]] = relationship(back_populates="hospital")
    staff: Mapped[list["Staff"]] = relationship(back_populates="hospital")

    def __repr__(self) -> str:
        return f"<Hospital id={self.id} name={self.name}>"
