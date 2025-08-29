from datetime import UTC, datetime
from typing import Any, List, cast
from zoneinfo import ZoneInfo

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String as SQLString
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase):
    pass


class ZoneInfoType(TypeDecorator):  # pylint: disable=abstract-method
    """
    Custom SQLAlchemy type for storing ZoneInfo objects as strings in the database.
    """

    impl = SQLString
    cache_ok = True

    def process_bind_param(self, value: ZoneInfo | None, dialect: Any) -> str | None:
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect: Any) -> ZoneInfo | None:
        if value is not None:
            return ZoneInfo(value)
        return value


class Hospital(Base):
    """
    The location a doctor works out of.
    """

    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    timezone: Mapped[ZoneInfo] = mapped_column(ZoneInfoType(50), nullable=False)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)

    staff = relationship("Staff", back_populates="hospital")

    def __repr__(self) -> str:
        return f"<Hospital id={self.id} name={self.name}>"

    @property
    def doctors(self) -> List["Staff"]:
        """Return all staff members who are doctors."""
        return [member for member in self.staff if member.is_doctor]


class Staff(Base):
    """
    Medical staff at a hospital, including doctors and other personnel.
    """

    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    is_doctor = Column(Boolean, default=False)

    # Relationships
    hospital = relationship("Hospital", back_populates="staff")
    appointments = relationship("Appointment", back_populates="doctor")

    def __repr__(self) -> str:
        role = "Doctor" if self.is_doctor else "Staff"
        return f"<{role} id={self.id} name={self.name} hospital_id={self.hospital_id}>"

    @classmethod
    def create_doctor(cls, name: str, hospital_id: int, **kwargs: Any) -> "Staff":
        """Create and return a new doctor."""
        return Staff(name=name, hospital_id=hospital_id, is_doctor=True, **kwargs)

    @classmethod
    def create_staff(cls, name: str, hospital_id: int, **kwargs: Any) -> "Staff":
        """Create and return a new staff member."""
        return Staff(name=name, hospital_id=hospital_id, is_doctor=False, **kwargs)

    @classmethod
    def doctors(cls, session) -> List["Staff"]:
        """Return all staff members who are doctors."""
        return cast(List["Staff"], session.query(cls).filter_by(is_doctor=True).all())


class Patient(Base):
    """
    A patient that requires and appointment with a doctor.
    """

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    # Relationships
    appointments = relationship("Appointment", back_populates="patient")

    def __repr__(self) -> str:
        return f"<Patient id={self.id} name={self.name}>"


class Appointment(Base):
    """
    An appointment between a patient and a doctor at a specific time.
    """

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    doctor = relationship("Staff", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")

    __table_args__ = (
        # Prevent double bookings - unique constraint on doctor + time
        Index(
            "idx_unique_doctor_timeslot", "doctor_id", "appointment_time", unique=True
        ),
        # Ensure only doctors can be assigned to appointments
        CheckConstraint(
            "doctor_id IN (SELECT id FROM staff WHERE is_doctor = true)",
            name="check_doctor_is_actually_doctor",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Appointment id={self.id} doctor_id={self.doctor_id} "
            f"patient_id={self.patient_id} time={self.appointment_time.isoformat()}>"
        )
