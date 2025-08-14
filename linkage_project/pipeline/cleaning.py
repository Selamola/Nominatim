from __future__ import annotations

import logging
from typing import Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)
HONORIFICS = r"\b(MR|MRS|MS|DR|MISS|MADAM|SIR)\s+"


def _clean_names(df: pd.DataFrame, columns) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = (df[col].astype(str).str.strip().str.upper()
                        .str.replace(HONORIFICS, "", regex=True)
                        .str.replace(r"\s+", " ", regex=True))
    return df


def clean_df1(df1: pd.DataFrame) -> pd.DataFrame:
    df1 = _clean_names(df1, ["first_name", "first_name2", "last_name", "surname2", "mom_name", "mom_name2"])
    gender_map = {"MALE": "M", "FEMALE": "F", "UNKNOWN": "U", "INDETERMINATE": "I"}
    df1["gender"] = df1.get("gender", "").astype(str).str.upper().map(gender_map).fillna("U")
    for col in ["dob", "dod"]:
        df1[f"{col}_raw"] = df1[col]
        df1[f"{col}_clean"] = pd.to_datetime(df1[col], errors="coerce")
    df1["dob_year"] = df1["dob_clean"].dt.year
    first_parts = [c for c in ["first_name", "first_name2", "mom_name", "mom_name2"] if c in df1.columns]
    df1["first_name_clean"] = (df1[first_parts]
                                .fillna("")
                                .agg(lambda x: " ".join(sorted(set(" ".join(x).split()))).strip(), axis=1))
    last_parts = [c for c in ["last_name", "surname2"] if c in df1.columns]
    df1["last_name_clean"] = (df1[last_parts]
                               .fillna("")
                               .agg(lambda x: " ".join(sorted(set(" ".join(x).split()))).strip(), axis=1))
    for col in ["hospital_number", "hospital_number_mom"]:
        if col in df1.columns:
            df1[col] = df1[col].astype(str).str.replace(r"\W", "", regex=True)
            df1[f"has_{col}"] = df1[col].ne("")
        else:
            logger.warning("Missing column %s", col)
            df1[col] = ""
            df1[f"has_{col}"] = False
    return df1


def clean_df2(df2: pd.DataFrame) -> pd.DataFrame:
    df2 = _clean_names(df2, ["first_name", "last_name", "report_caretaker_firstname"])
    gender_map = {"MALE": "M", "FEMALE": "F", "UNKNOWN": "U", "INDETERMINATE": "I"}
    df2["gender"] = df2.get("gender", "").astype(str).str.upper().map(gender_map).fillna("U")
    for col in ["dob", "dod", "report_note_dt"]:
        if col in df2.columns:
            df2[f"{col}_raw"] = df2[col]
            df2[f"{col}_clean"] = pd.to_datetime(df2[col], errors="coerce")
    df2["dob_year"] = df2["dob_clean"].dt.year
    first_parts = [c for c in ["first_name", "report_caretaker_firstname"] if c in df2.columns]
    df2["first_name_clean"] = (df2[first_parts]
                                .fillna("")
                                .agg(lambda x: " ".join(sorted(set(" ".join(x).split()))).strip(), axis=1))
    last_parts = ["last_name"]
    df2["last_name_clean"] = (df2[last_parts]
                               .fillna("")
                               .agg(lambda x: " ".join(sorted(set(" ".join(x).split()))).strip(), axis=1))
    for col in ["hospital_number", "mom_hospital_number"]:
        if col in df2.columns:
            df2[col] = df2[col].astype(str).str.replace(r"\W", "", regex=True)
            df2[f"has_{col}"] = df2[col].ne("")
        else:
            logger.warning("Missing column %s", col)
            df2[col] = ""
            df2[f"has_{col}"] = False
    return df2


def clean_data(df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    return clean_df1(df1.copy()), clean_df2(df2.copy())

