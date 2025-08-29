"""
Database initialization script.
Creates all tables defined in models.
"""

import random

from faker import Faker
from sqlalchemy.orm import sessionmaker

from ..models import Base, Hospital, Patient, Staff
from .database import engine


def create_tables() -> None:
    """Create all tables in the database."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def populate_tables() -> None:
    """
    Initialize stub data in the database. Add the following entries:
    - 10 hospitals
    - 10 doctors and 20 staff at each hospital
    - 200 patients

    Use Faker to generate some unique data.
    """
    print("Populating database with stub data...")
    fake = Faker()

    Session = sessionmaker(bind=engine)
    with Session() as session:
        # Skip if data already exists
        if session.query(Hospital).first():
            print("Data already exists in the database. Skipping population.")
            return

        # Create hospitals
        hospitals = [
            Hospital(
                name=f"{fake.company()} Hospital",
                address=fake.address(),
                timezone=fake.timezone(),
                open_time=random.randint(6, 9),  # Open between 6 AM and 9 AM
                close_time=random.randint(17, 22),  # Close between 5 PM and 10 PM
            )
            for _ in range(10)
        ]
        session.bulk_save_objects(hospitals)
        session.commit()
        hospital_ids = [hospital.id for hospital in session.query(Hospital).all()]

        # Create staff (doctors and other staff)
        staff_members = []
        for hospital_id in hospital_ids:
            for _ in range(10):  # 10 doctors
                staff_members.append(
                    Staff.create_doctor(
                        name=fake.name(),
                        hospital_id=hospital_id,
                    )
                )
            for _ in range(20):  # 20 other staff
                staff_members.append(
                    Staff.create_staff(
                        name=fake.name(),
                        hospital_id=hospital_id,
                    )
                )
        session.bulk_save_objects(staff_members)

        # Create patients
        patients = [Patient(name=fake.name()) for _ in range(200)]
        session.bulk_save_objects(patients)

        # Commit all changes
        session.commit()

    print("Database populated with stub data successfully!")


if __name__ == "__main__":
    create_tables()
    populate_tables()
