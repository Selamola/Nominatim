"""Pydantic schemas for requests and responses."""
from __future__ import annotations

from datetime import date
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, constr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str


class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Login(BaseModel):
    email: EmailStr
    password: str


class Record(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sex: Optional[str] = None
    dob: Optional[date] = None
    address: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    cluster: Optional[str] = None


class Thresholds(BaseModel):
    composite_threshold: float = 0.0
    fuzzy_last_block: float = 0.85
    fuzzy_first_block: float = 0.85
    fuzzy_addr_block: float = 0.70
    fuzzy_cluster_block: float = 0.70
    enable_phone_block: bool = True
    dob_block_days: int = 0


class Weights(BaseModel):
    last_name_sim: float = 0.35
    first_name_sim: float = 0.30
    dob_match: float = 0.20
    sex_match: float = 0.05
    address_sim: float = 0.05
    phone_match: float = 0.05


class MatchRequest(BaseModel):
    record: Record
    thresholds: Thresholds = Thresholds()
    weights: Weights = Weights()
    top_n: int = 1000


class Candidate(BaseModel):
    id: int
    champs_id_ps: Optional[str]
    mom_first_name: Optional[str]
    mom_last_name: Optional[str]
    address: Optional[str]
    cluster: Optional[str]
    sex: Optional[str]
    dob: Optional[date]
    phones: List[str] = []
    last_name_sim: float
    first_name_sim: float
    address_sim: float
    cluster_sim: float
    sex_match: int
    dob_match: int
    phone_match: int
    composite_score: float

    class Config:
        orm_mode = True
