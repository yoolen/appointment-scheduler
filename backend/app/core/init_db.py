"""
Database initialization script.
Creates all tables defined in models.
"""

import random
from datetime import time
from typing import cast

from faker import Faker
from sqlalchemy.orm import sessionmaker

from ..models import Base, Doctor, Hospital, Patient, Staff, User
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
                open_time=time(random.randint(6, 9), 0),  # Open between 6 AM and 9 AM
                close_time=time(
                    random.randint(17, 22), 0
                ),  # Close between 5 PM and 10 PM
            )
            for _ in range(10)
        ]
        session.bulk_save_objects(hospitals)
        session.commit()
        hospital_ids = [
            cast(int, hospital.id) for hospital in session.query(Hospital).all()
        ]

        # Create staff (doctors and other staff)
        staff = []
        doctors = []
        for hospital_id in hospital_ids:
            for _ in range(10):  # 10 doctors
                staff.append(
                    Staff(
                        name=fake.name(),
                        hospital_id=hospital_id,
                    )
                )
            for _ in range(20):  # 20 other staff
                doctors.append(
                    Doctor(
                        name=fake.name(),
                        hospital_id=hospital_id,
                    )
                )
        session.bulk_save_objects(staff)
        session.bulk_save_objects(doctors)

        # Create patients
        patients = [Patient(name=fake.name()) for _ in range(200)]
        session.bulk_save_objects(patients)

        # Commit all changes
        session.commit()

        # Get some actual staff and doctor IDs for demo users
        some_doctors = session.query(Doctor).limit(2).all()
        some_staff = session.query(Staff).limit(2).all()

        # Create some demo users
        demo_users = [
            # Admin user (you)
            User(
                email="admin@test.com",
                hashed_password="$2b$12$iWuf7ugkm/PWdvTsJKcPPOh0yL1.LEonWxdhM5GvI0fo0S0FuHqre",  # salted and hashed "password"  # pylint: disable=line-too-long
                person_id=None,
                is_superuser=True,
            ),
            # A few doctors who can log in
            User(
                email="doctor1@test.com",
                hashed_password="$2b$12$qlbB/ZtKyNlXLKMl8KX8v.v/N1bHF8ZxMPkwy7nElEkxviYVjaW3G",  # salted and hashed "docpass"  # pylint: disable=line-too-long
                person_id=some_doctors[0].id,
                is_superuser=False,
            ),
            User(
                email="doctor2@test.com",
                hashed_password="$2b$12$Xdi38fXZfsbNc50qMxNxfu46SC4nIAD8E77WjWA8Qeb7ad53aObbC",  # salted and hashed "docpass"  # pylint: disable=line-too-long
                person_id=some_doctors[1].id,
                is_superuser=False,
            ),
            # A few staff members who can log in
            User(
                email="staff1@test.com",
                hashed_password="$2b$12$Hmg3w7fkX6rfK0RUbxdzx.AjzztP7ed8UJCu5rfBkkBMyfFqsq/W6",  # salted and hashed "staffpass"  # pylint: disable=line-too-long
                person_id=some_staff[0].id,
                is_superuser=False,
            ),
            User(
                email="staff2@test.com",
                hashed_password="$2b$12$bn8fZQ5Eww8emE.MvOY9iu4uEKvA/0Dkgn23n.Yd7N88JizdoB6X2",  # salted and hashed "staffpass"  # pylint: disable=line-too-long
                person_id=some_staff[1].id,
                is_superuser=False,
            ),
        ]
        session.bulk_save_objects(demo_users)
        session.commit()

    print("Database populated with stub data successfully!")


if __name__ == "__main__":
    create_tables()
    populate_tables()
