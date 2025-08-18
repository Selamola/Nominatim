"""Database utilities."""
from __future__ import annotations

import os
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Iterator

from .models import Person
from .seed import create_admin_if_needed, seed_mock_data
from .utils import get_env_bool

DB_URL = os.getenv("DB_URL", "sqlite:///./data/app.db")
engine = create_engine(DB_URL, echo=False, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})


def init_db() -> None:
    """Create tables and seed data."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        create_admin_if_needed(session)
        has_person = session.exec(select(Person).limit(1)).first() is not None
        if not has_person:
            if get_env_bool("REDCAP_ENABLED", False):
                # if REDCap enabled but no data yet, seed mock data so UI works
                seed_mock_data(session)
            else:
                seed_mock_data(session)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
