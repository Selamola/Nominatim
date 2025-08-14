"""Input/output utilities for the pipeline."""
from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path
from typing import Tuple

import pandas as pd
import pyodbc
import requests

from .config import Settings
from . import synthetic_data

LOGGER = logging.getLogger(__name__)


def extract_real_data(settings: Settings, out_dir: Path = Path("data/inputs")) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Extract df1 and df2 from SQL Server and REDCap."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # df1 from SQL Server
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={settings.sql_server};"
        f"DATABASE={settings.sql_database};UID={settings.sql_username};PWD={settings.sql_password}"
    )
    query = "SELECT * FROM [Neonads_Database].[DBO].[neonads];"
    df_neo = pd.read_sql(query, conn)
    conn.close()

    df_neo['outcome'] = df_neo['outcome'].astype('Int64').astype(str)
    df_neo = df_neo[df_neo['outcome'] == '5']

    df1 = df_neo[[
        "REC_CODE", "first_name", "first_name2", "surname", "surname2",
        "mom_name", "mom_name2", "dob", "dob2", "date_disc", "date_disc2",
        "gender", "gender2", "hospital_number", "hospital_number_mom", "hospital_number_mom2"
    ]].copy()
    df1["gender"] = df1["gender"].fillna(df1["gender2"])
    df1["gender"] = df1["gender"].replace({1.0: "M", 2.0: "F"})
    df1.drop("gender2", axis=1, inplace=True)

    def date_columns_processing(df: pd.DataFrame, cols):
        for col in cols:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    df1 = date_columns_processing(df1, ["dob", "dob2", "date_disc", "date_disc2"])

    def fill_and_drop_columns(df: pd.DataFrame, primary_col: str, secondary_col: str) -> pd.DataFrame:
        df[primary_col] = df[primary_col].where(df[primary_col].notna(), df[secondary_col])
        return df.drop(columns=[secondary_col])

    df1 = fill_and_drop_columns(df1, "dob", "dob2")
    df1 = fill_and_drop_columns(df1, "date_disc", "date_disc2")
    df1.rename(columns={"surname": "last_name", "date_disc": "dod"}, inplace=True)
    df1 = df1.apply(lambda x: x.str.strip().str.upper() if x.dtype == "object" else x)
    honorific_pattern = r"\b(MR|MISS|MS|DR|BT)\s+"
    for col in ["first_name", "first_name2", "mom_name", "mom_name2"]:
        df1[col] = df1[col].str.replace(honorific_pattern, "", case=False, regex=True)
    df1["year"] = df1["dod"].dt.year
    df1["first_name_original_missing"] = df1["first_name"].isna() | (df1["first_name"] == "")
    df1["first_name_filled_with_mom"] = df1["first_name_original_missing"] & df1["mom_name"].notna()
    df1["first_name"] = df1["first_name"].replace("", pd.NA)
    df1["first_name"] = df1["first_name"].fillna(df1["mom_name"])
    df1["hospital_number"] = df1["hospital_number"].astype(str).str.strip().str.upper()
    df1["hospital_number_mom"] = df1["hospital_number_mom"].astype(str).str.strip().str.upper()
    df1["hospital_number_mom2"] = df1["hospital_number_mom2"].astype(str).str.strip().str.upper()

    df1 = df1.reset_index(drop=True)
    df1.index = pd.Index(df1.index, name="df1_index")

    # df2 from REDCap
    data = {
        "token": settings.redcap_token,
        "content": "record",
        "action": "export",
        "format": "csv",
        "type": "flat",
        "csvDelimiter": "",
        "rawOrLabel": "label",
        "rawOrLabelHeaders": "raw",
        "exportCheckboxLabel": "false",
        "exportSurveyFields": "false",
        "exportDataAccessGroups": "true",
        "returnFormat": "json",
    }
    response = requests.post("https://redcap.core.wits.ac.za/redcap/api/", data=data, timeout=60)
    df = pd.read_csv(StringIO(response.text), low_memory=False)

    datetime_columns_df2 = ["report_death_dt", "report_note_dt", "report_dob"]

    def process_date_cols(df: pd.DataFrame, cols):
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    df = process_date_cols(df, datetime_columns_df2)
    df2 = df[[
        "report_id", "report_child_firstname", "report_child_surname",
        "report_caretaker_firstname", "report_caretaker_firstname",
        "report_dob", "report_death_dt", "report_note_dt", "report_sex",
        "report_age_class", "report_stillbirth", "hospital_number", "mom_hospital_number"
    ]].copy()
    df2 = df2.loc[:, ~df2.columns.duplicated()]
    gender_mapping = {"Male": "M", "Female": "F", "Unknown": "U", "Indeterminate": "I", pd.NA: "U"}
    df2["report_sex"] = df2["report_sex"].map(gender_mapping)
    for col in ["report_child_firstname", "report_caretaker_firstname"]:
        df2[col] = df2[col].str.replace(honorific_pattern, "", case=False, regex=True)
    df2["child_firstname_original_missing"] = df2["report_child_firstname"].isna() | (df2["report_child_firstname"] == "")
    df2["child_firstname_filled_caretaker"] = df2["child_firstname_original_missing"] & df2["report_caretaker_firstname"].notna()
    df2["report_child_firstname"] = df2["report_child_firstname"].replace("", pd.NA)
    df2["report_child_firstname"] = df2["report_child_firstname"].fillna(df2["report_caretaker_firstname"])
    df2["report_death_dt"] = df2["report_death_dt"].where(df2["report_death_dt"].notna(), df2["report_note_dt"])
    df2.rename(columns={
        "report_child_firstname": "first_name",
        "report_child_surname": "last_name",
        "report_dob": "dob",
        "report_death_dt": "dod",
        "report_sex": "gender",
    }, inplace=True)
    df2 = df2.apply(lambda x: x.str.strip().str.upper() if x.dtype == "object" else x)
    df2["hospital_number"] = df2["hospital_number"].astype(str).str.strip().str.upper()
    df2["mom_hospital_number"] = df2["mom_hospital_number"].astype(str).str.strip().str.upper()

    df2 = df2.reset_index(drop=True)
    df2.index = pd.Index(df2.index, name="df2_index")

    df1.to_csv(out_dir / "df1.csv", index=False)
    df2.to_csv(out_dir / "df2.csv", index=False)
    LOGGER.info("Extracted df1 and df2 to %s", out_dir)
    return df1, df2


def load_inputs(mock: bool, settings: Settings) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return df1 and df2 either from synthetic data or extracted files."""
    in_dir = Path("data/inputs")
    if mock:
        LOGGER.info("Generating synthetic data")
        return synthetic_data.generate_demo(in_dir)
    if not (in_dir / "df1.csv").exists() or not (in_dir / "df2.csv").exists():
        LOGGER.info("Input files not found. Extracting real data.")
        return extract_real_data(settings, in_dir)
    return (
        pd.read_csv(in_dir / "df1.csv"),
        pd.read_csv(in_dir / "df2.csv"),
    )
