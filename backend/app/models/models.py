from __future__ import annotations

from datetime import UTC, datetime, time
from typing import Any, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String as SQLString
from sqlalchemy.types import TypeDecorator
from typing_extensions import Annotated

int_pk = Annotated[int, mapped_column(primary_key=True, index=True)]
person_fk = Annotated[int, mapped_column(ForeignKey("people.id"))]


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Person(Base):
    """
    A base class containing contact info and other common fields.
    """

    __tablename__ = "people"

    id: Mapped[int_pk]
    name: Mapped[str]
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(unique=True)

    def __repr__(self) -> str:
        return f"<Person id={self.id} name={self.name}>"


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


class Doctor(Person):
    """
    A doctor who can have appointments with patients.
    """

    __tablename__ = "doctors"

    id: Mapped[person_fk] = mapped_column(primary_key=True)
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospitals.id"))
    specialty: Mapped[Optional[str]]  # Consider Enum for specialties

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")
    # Currently a doctor works only at one hospital
    hospital: Mapped["Hospital"] = relationship(back_populates="doctors")

    def __repr__(self) -> str:
        return f"<Doctor id={self.id} name={self.name}>"


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


class Patient(Person):
    """
    A patient that requires and appointment with a doctor.
    """

    __tablename__ = "patients"

    id: Mapped[person_fk] = mapped_column(primary_key=True)

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")

    def __repr__(self) -> str:
        return f"<Patient id={self.id} name={self.name}>"


class Staff(Person):
    """
    Medical staff at a hospital, including doctors and other personnel.
    """

    __tablename__ = "staff"

    id: Mapped[person_fk] = mapped_column(primary_key=True)
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospitals.id"))

    # Currently a staff member works only at one hospital32
    hospital = relationship("Hospital", back_populates="staff")

    def __repr__(self) -> str:
        return f"<Staff id={self.id} name={self.name} hospital_id={self.hospital_id}>"


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
    person_id: Mapped[Optional[int]] = mapped_column(ForeignKey("people.id"))

    person: Mapped[Optional["Person"]] = relationship()

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} username={self.username} is_active={self.is_active}>"
        )
