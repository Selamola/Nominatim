"""Helpers for Streamlit frontend to talk to API."""
from __future__ import annotations

import os
import requests
from typing import Optional

API_URL = os.getenv("API_URL", "http://api:8000")


def api_request(path: str, method: str = "get", token: Optional[str] = None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.request(method, f"{API_URL}{path}", headers=headers, **kwargs)


def login(email: str, password: str):
    return api_request("/auth/login", method="post", data={"username": email, "password": password})


def register(email: str, password: str, name: str):
    return api_request("/auth/register", method="post", json={"email": email, "password": password, "name": name})


def current_user(token: str):
    return api_request("/auth/me", token=token)


def search(token: str, payload: dict):
    return api_request("/match/search", method="post", token=token, json=payload)


def sync_redcap(token: str):
    return api_request("/data/sync-redcap", method="post", token=token)
