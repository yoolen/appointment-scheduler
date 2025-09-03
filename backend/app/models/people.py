from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, int_pk, person_fk

if TYPE_CHECKING:
    from .appointments import Appointment
    from .facilities import Hospital


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
