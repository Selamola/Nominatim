"""Data cleaning and normalization functions."""
from __future__ import annotations

import logging
import re
from typing import Iterable

import pandas as pd

LOGGER = logging.getLogger(__name__)
HONORIFIC_PATTERN = re.compile(r"^(MR|MRS|MS|DR|MISS|MADAM|SIR)\s+", re.I)
NAME_FIELDS_LEFT = ["first_name", "first_name2", "mom_name", "mom_name2"]
NAME_FIELDS_RIGHT = ["first_name", "report_caretaker_firstname"]
SURNAME_FIELDS_LEFT = ["last_name", "surname2"]
SURNAME_FIELDS_RIGHT = ["last_name"]


def _ensure_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    for col in columns:
        if col not in df.columns:
            LOGGER.warning("Missing column %s added as empty", col)
            df[col] = pd.NA


def _clean_text(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
        .str.replace(HONORIFIC_PATTERN, "", regex=True)
    )


def _map_gender(s: pd.Series) -> pd.Series:
    mapping = {"MALE": "M", "FEMALE": "F", "UNKNOWN": "U", "INDETERMINATE": "I"}
    return s.astype(str).str.upper().map(mapping).fillna("U")


def _parse_dates(df: pd.DataFrame, cols: Iterable[str]) -> None:
    for col in cols:
        if col in df.columns:
            df[col + "_clean"] = pd.to_datetime(df[col], errors="coerce")
    if "dob_clean" in df:
        df["dob_year"] = df["dob_clean"].dt.year


def _build_name_variations(df: pd.DataFrame, fields: Iterable[str], out_col: str) -> None:
    names = []
    for field in fields:
        if field in df.columns:
            names.append(df[field].fillna(""))
    if names:
        tokens = (
            pd.concat(names, axis=1)
            .apply(lambda x: " ".join(pd.unique(" ".join(x).lower().split())), axis=1)
        )
        df[out_col] = tokens.str.upper()
    else:
        df[out_col] = ""


def clean_df(df: pd.DataFrame, side: str) -> pd.DataFrame:
    """Clean df1 or df2 according to the specification."""
    df = df.copy()
    if side == "left":
        name_fields = NAME_FIELDS_LEFT
        surname_fields = SURNAME_FIELDS_LEFT
        hosp_cols = ["hospital_number", "hospital_number_mom", "hospital_number_mom2"]
    else:
        name_fields = NAME_FIELDS_RIGHT
        surname_fields = SURNAME_FIELDS_RIGHT
        hosp_cols = ["hospital_number", "mom_hospital_number"]

    _ensure_columns(df, name_fields + surname_fields + hosp_cols + ["gender", "dob", "dod"])

    for col in name_fields + surname_fields:
        df[col] = _clean_text(df[col])
    df["gender"] = _map_gender(df["gender"])
    _parse_dates(df, ["dob", "dod"])
    _build_name_variations(df, name_fields, "first_name_clean")
    _build_name_variations(df, surname_fields, "last_name_clean")

    for col in hosp_cols:
        df[col] = df[col].astype(str).str.replace(r"[^A-Z0-9]", "", regex=True)
    df["has_hosp_num"] = df[hosp_cols].apply(lambda x: x.notna() & (x != "")).any(axis=1)
    df["is_name_missing"] = df["first_name_clean"].eq("") | df["last_name_clean"].eq("")
    return df
