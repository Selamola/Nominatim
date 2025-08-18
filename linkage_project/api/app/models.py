"""Database models."""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List

from sqlmodel import SQLModel, Field, Column, JSON, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    password_hash: str
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    logs: List["AuditLog"] = Relationship(back_populates="user")


class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    champs_id_ps: Optional[str] = Field(default=None, index=True)
    mom_first_name: Optional[str] = Field(default=None, index=True)
    mom_last_name: Optional[str] = Field(default=None, index=True)
    address: Optional[str] = Field(default=None)
    cluster: Optional[str] = Field(default=None)
    sex: Optional[str] = Field(default=None)
    dob: Optional[date] = Field(default=None)
    phones: List[str] = Field(sa_column=Column(JSON), default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    action: str
    payload: dict = Field(sa_column=Column(JSON), default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="logs")
