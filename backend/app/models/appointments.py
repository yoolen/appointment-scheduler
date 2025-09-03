from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, int_pk, person_fk

if TYPE_CHECKING:
    from .people import Doctor, Patient, Person


class Appointment(Base):
    """
    An appointment between a patient and a doctor at a specific time.
    """

    __tablename__ = "appointments"

    id: Mapped[int_pk]
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"))
    patient_id: Mapped[Optional[int]] = mapped_column(ForeignKey("patients.id"))
    appointment_time: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    created_by: Mapped[person_fk]

    creator: Mapped["Person"] = relationship()
    doctor: Mapped["Doctor"] = relationship(
        back_populates="appointments", foreign_keys=[doctor_id]
    )
    patient: Mapped["Patient"] = relationship(
        back_populates="appointments", foreign_keys=[patient_id]
    )

    __table_args__ = (
        # Prevent double bookings - unique constraint on doctor + time
        Index(
            "idx_unique_doctor_timeslot", "doctor_id", "appointment_time", unique=True
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Appointment id={self.id} doctor_id={self.doctor_id} "
            f"patient_id={self.patient_id} time={self.appointment_time.isoformat()}>"
        )
