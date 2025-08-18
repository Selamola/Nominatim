"""Seeding helpers for database."""
from __future__ import annotations

from datetime import date
import os
from sqlmodel import Session, select

from .models import User, Person
from .auth import get_password_hash
from .utils import dedupe


MOCK_DATA = [
    {
        "champs_id_ps": "001",
        "mom_first_name": "Alice",
        "mom_last_name": "Smith",
        "address": "123 Main St",
        "cluster": "A1",
        "sex": "F",
        "dob": date(2020, 1, 1),
        "phones": ["0831234567"],
    },
    {
        "champs_id_ps": "002",
        "mom_first_name": "Bob",
        "mom_last_name": "Jones",
        "address": "456 Side Rd",
        "cluster": "B2",
        "sex": "M",
        "dob": date(2020, 5, 20),
        "phones": ["0847654321"],
    },
]


def create_admin_if_needed(session: Session) -> None:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    name = os.getenv("ADMIN_NAME", "Admin")
    if not email or not password:
        return
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        return
    admin = User(email=email, name=name, role="admin", password_hash=get_password_hash(password))
    session.add(admin)
    session.commit()


def seed_mock_data(session: Session) -> None:
    for item in MOCK_DATA:
        exists = session.exec(select(Person).where(Person.champs_id_ps == item["champs_id_ps"])) .first()
        if exists:
            continue
        person = Person(**item)
        session.add(person)
    session.commit()
