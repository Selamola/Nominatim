from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd
import numpy as np
import pyodbc
import requests
from io import StringIO

from .synthetic_data import generate_demo_data

logger = logging.getLogger(__name__)


def extract_data(mock: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return df1 and df2 either from synthetic generator or real sources."""
    if mock:
        logger.info("Generating synthetic data")
        return generate_demo_data(Path(__file__).resolve().parents[1] / "data" / "inputs")
    logger.info("Loading real data from SQL Server and REDCap")
    df1 = _load_df1_sql()
    df2 = _load_df2_redcap()
    return df1, df2


def _load_df1_sql() -> pd.DataFrame:
    server = '10.21.16.106'
    database = 'Neonads_Database'
    username = 'neonads_user'
    password = 'password'
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    query = "SELECT * FROM [Neonads_Database].[DBO].[neonads];"
    df_neo = pd.read_sql(query, conn)
    conn.close()

    df_neo['outcome'] = df_neo['outcome'].astype('Int64').astype(str)
    df_neo = df_neo[df_neo['outcome'] == '5']

    df1 = df_neo[["REC_CODE", "first_name", "first_name2", "surname", "surname2",
                  "mom_name", "mom_name2", "dob", "dob2", "date_disc", "date_disc2",
                  "gender", "gender2", "hospital_number", "hospital_number_mom", "hospital_number_mom2"]].copy()
    df1["gender"] = df1["gender"].fillna(df1["gender2"])
    df1["gender"] = df1["gender"].replace({1.0: "M", 2.0: "F"})
    df1.drop("gender2", axis=1, inplace=True)

    def date_columns_processing(df: pd.DataFrame, datetime_columns):
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    datetime_columns = ["dob", "dob2", "date_disc", "date_disc2"]
    df1 = date_columns_processing(df1, datetime_columns)

    def fill_and_drop_columns(df: pd.DataFrame, primary_col: str, secondary_col: str):
        df[primary_col] = np.where(df[primary_col].isna(), df[secondary_col], df[primary_col])
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
    df1["first_name"] = df1["first_name"].replace("", np.nan)
    df1["first_name"] = df1["first_name"].fillna(df1["mom_name"])
    df1["hospital_number"] = df1["hospital_number"].astype(str).str.strip().str.upper()
    df1["hospital_number_mom"] = df1["hospital_number_mom"].astype(str).str.strip().str.upper()
    df1["hospital_number_mom2"] = df1["hospital_number_mom2"].astype(str).str.strip().str.upper()
    df1 = df1.reset_index(drop=True)
    df1.index = pd.Index(df1.index, name="df1_index")
    return df1


def _load_df2_redcap() -> pd.DataFrame:
    data = {
        "token": "FE16852BB8978518EBC68F3F80404976",
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
    response = requests.post("https://redcap.core.wits.ac.za/redcap/api/", data=data)
    df = pd.read_csv(StringIO(response.text), low_memory=False)
    datetime_columns_df2 = ["report_death_dt", "report_note_dt", "report_dob"]

    def process_date_cols(df: pd.DataFrame, cols):
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    df = process_date_cols(df, datetime_columns_df2)
    df2 = df[["report_id", "report_child_firstname", "report_child_surname",
              "report_caretaker_firstname", "report_caretaker_firstname",
              "report_dob", "report_death_dt", "report_note_dt", "report_sex",
              "report_age_class", "report_stillbirth", "hospital_number", "mom_hospital_number"]].copy()
    df2 = df2.loc[:, ~df2.columns.duplicated()]
    gender_mapping = {"Male": "M", "Female": "F", "Unknown": "U", "Indeterminate": "I", np.nan: "Not specified"}
    df2["report_sex"] = df2["report_sex"].map(gender_mapping)
    honorific_pattern = r"\b(MR|MISS|MS|DR|BT)\s+"
    df2["report_child_firstname"] = df2["report_child_firstname"].str.replace(honorific_pattern, "", case=False, regex=True)
    df2["report_caretaker_firstname"] = df2["report_caretaker_firstname"].str.replace(honorific_pattern, "", case=False, regex=True)
    df2["child_firstname_original_missing"] = df2["report_child_firstname"].isna() | (df2["report_child_firstname"] == "")
    df2["child_firstname_filled_caretaker"] = df2["child_firstname_original_missing"] & df2["report_caretaker_firstname"].notna()
    df2["report_child_firstname"] = df2["report_child_firstname"].replace("", np.nan)
    df2["report_child_firstname"] = df2["report_child_firstname"].fillna(df2["report_caretaker_firstname"])
    df2["report_death_dt"] = np.where(df2["report_death_dt"].isna(), df2["report_note_dt"], df2["report_death_dt"])
    df2.rename(columns={"report_child_firstname": "first_name",
                        "report_child_surname": "last_name",
                        "report_dob": "dob",
                        "report_death_dt": "dod",
                        "report_sex": "gender"}, inplace=True)
    df2 = df2.apply(lambda x: x.str.strip().str.upper() if x.dtype == "object" else x)
    df2["hospital_number"] = df2["hospital_number"].astype(str).str.strip().str.upper()
    df2["mom_hospital_number"] = df2["mom_hospital_number"].astype(str).str.strip().str.upper()
    df2 = df2.reset_index(drop=True)
    df2.index = pd.Index(df2.index, name="df2_index")
    return df2

