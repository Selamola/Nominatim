"""FastAPI application entry point."""
from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
import pandas as pd

from . import __version__
from .db import init_db, get_session
from .auth import router as auth_router, get_current_user, get_current_admin
from .models import User, Person
from .schema import MatchRequest, Candidate, UserRead
from .redcap import sync_redcap
from .matching import search

app = FastAPI(title=os.getenv("PROJECT_NAME", "Linkage Project"))

origins = [os.getenv("FRONTEND_ORIGIN", "*")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict:
    return {"version": __version__}


@app.get("/admin/users", response_model=List[UserRead])
def list_users(session: Session = Depends(get_session), _: User = Depends(get_current_admin)) -> List[User]:
    return session.exec(select(User)).all()


@app.post("/data/sync-redcap")
def sync(session: Session = Depends(get_session), _: User = Depends(get_current_admin)) -> dict:
    count = sync_redcap(session)
    return {"inserted": count}


@app.post("/match/search", response_model=List[Candidate])
def match(req: MatchRequest, session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> List[Candidate]:
    return search(req, session)


@app.post("/match/export")
def match_export(session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> Response:
    persons = session.exec(select(Person)).all()
    df = pd.DataFrame([p.dict() for p in persons])
    csv = df.to_csv(index=False)
    return Response(content=csv, media_type="text/csv")
