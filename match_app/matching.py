import pandas as pd
import recordlinkage
from rapidfuzz import distance, fuzz
from dataclasses import dataclass
import re
from typing import Dict, Any, List

# Helper functions

def parse_date(value: str):
    """Parse a date string into a datetime object."""
    if value is None or value == "":
        return pd.NaT
    return pd.to_datetime(value, errors="coerce")

def standardize_phone(phone: Any) -> str:
    """Keep only digits for phone numbers."""
    if phone is None:
        return ""
    return re.sub(r"\D", "", str(phone))

def jw_similarity(a: Any, b: Any) -> float:
    """Jaro-Winkler similarity between two strings (0-1)."""
    if pd.isna(a) or pd.isna(b):
        return 0.0
    return distance.JaroWinkler.normalized_similarity(str(a), str(b))

def phone_similarity(a: Any, b: Any) -> float:
    """Similarity based on partial match of digits."""
    a_std, b_std = standardize_phone(a), standardize_phone(b)
    if not a_std or not b_std:
        return 0.0
    if a_std in b_std or b_std in a_std:
        return 1.0
    return fuzz.partial_ratio(a_std, b_std) / 100.0

def exact_match(a: Any, b: Any) -> float:
    return 1.0 if str(a).lower() == str(b).lower() and a != "" and b != "" else 0.0

@dataclass
class MatchConfig:
    thresholds: Dict[str, float]
    weights: Dict[str, float]
    top_n: int = 5


def prepare_database(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    if 'dob' in df.columns:
        df['dob'] = pd.to_datetime(df['dob'], errors='coerce')
    # combine phone numbers for easier comparison
    phone_cols = [col for col in df.columns if col.startswith('phonenumber')]
    if phone_cols:
        df['phone_combined'] = df[phone_cols].fillna('').apply(lambda x: ' '.join(x), axis=1)
    else:
        df['phone_combined'] = ''
    df['phone_combined'] = df['phone_combined'].apply(standardize_phone)
    return df

def build_compare(config: MatchConfig) -> recordlinkage.Compare:
    compare = recordlinkage.Compare()
    compare.add(recordlinkage.CompareFunction(jw_similarity, 'mom_first_name', 'mom_first_name', label='mom_first_name'))
    compare.add(recordlinkage.CompareFunction(jw_similarity, 'mom_last_name', 'mom_last_name', label='mom_last_name'))
    compare.add(recordlinkage.CompareFunction(jw_similarity, 'address', 'address', label='address'))
    compare.add(recordlinkage.CompareFunction(exact_match, 'sex', 'sex', label='sex'))
    compare.add(recordlinkage.CompareFunction(lambda x, y: 1.0 if parse_date(x) == parse_date(y) else 0.0, 'dob', 'dob', label='dob'))
    compare.add(recordlinkage.CompareFunction(phone_similarity, 'phone_combined', 'phone_combined', label='phone'))
    compare.add(recordlinkage.CompareFunction(exact_match, 'cluster', 'cluster', label='cluster'))
    return compare

def match_records(mits_record: Dict[str, Any], db: pd.DataFrame, config: MatchConfig) -> pd.DataFrame:
    mits_df = pd.DataFrame([mits_record])
    mits_df['dob'] = mits_df.get('dob').apply(parse_date)
    mits_df['phone_combined'] = ' '.join([standardize_phone(mits_record.get('phonenumber')), standardize_phone(mits_record.get('phonenumber2'))]).strip()

    indexer = recordlinkage.Index()
    indexer.full()
    candidate_links = indexer.index(mits_df, db)

    compare = build_compare(config)
    features = compare.compute(candidate_links, mits_df, db)

    # features has MultiIndex (left, right)
    features.reset_index(inplace=True)
    results = features.merge(db, left_on='right', right_index=True, how='left', suffixes=('', '_db'))

    # calculate binary scores and composite score
    for field, threshold in config.thresholds.items():
        score_col = field
        match_col = f"{field}_match"
        results[match_col] = (results[score_col] >= threshold).astype(int)

    results['composite_score'] = sum(
        results[f"{field}_match"] * config.weights.get(field, 1.0)
        for field in config.thresholds
    )

    results.sort_values('composite_score', ascending=False, inplace=True)
    return results.head(config.top_n)
