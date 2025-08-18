"""Matching and record linkage utilities."""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Iterable

from sqlmodel import Session, select
from difflib import SequenceMatcher

try:  # optional rapidfuzz
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover
    fuzz = None

from .models import Person
from .schema import MatchRequest, Candidate
from .utils import dedupe


def jaro_winkler(a: str, b: str) -> float:
    if fuzz:
        return fuzz.WRatio(a or "", b or "") / 100.0
    return SequenceMatcher(None, a or "", b or "").ratio()


def normalize_phone(phone: str) -> Optional[str]:
    """Normalize South African phone numbers."""
    if phone is None:
        return None
    s = str(phone)
    if s.endswith(".0"):
        s = s[:-2]
    digits = ''.join(ch for ch in s if ch.isdigit())
    if len(digits) == 10 and digits.startswith('0'):
        norm = digits
    else:
        if len(digits) < 9:
            return None
        digits = digits[-9:]
        norm = '0' + digits if not digits.startswith('0') else digits
    if len(norm) != 10:
        return None
    return norm


def normalize_phone_list(phones: Iterable[str]) -> List[str]:
    cleaned = [normalize_phone(p) for p in phones]
    cleaned = [p for p in cleaned if p]
    return dedupe(cleaned)


def apply_composite_score(df, weights: dict) -> None:
    """Add composite_score column to DataFrame."""
    df['composite_score'] = (
        df['last_name_sim'] * weights['last_name_sim'] +
        df['first_name_sim'] * weights['first_name_sim'] +
        df['dob_match'] * weights['dob_match'] +
        df['sex_match'] * weights['sex_match'] +
        df['address_sim'] * weights['address_sim'] +
        df['phone_match'] * weights['phone_match']
    )


def search(req: MatchRequest, session: Session) -> List[Candidate]:
    persons = session.exec(select(Person)).all()
    record = req.record
    thresholds = req.thresholds
    weights = req.weights
    query_phones = normalize_phone_list([record.phone1, record.phone2])
    results = []
    for p in persons:
        candidate_phones = normalize_phone_list(p.phones or [])
        if thresholds.enable_phone_block and query_phones:
            if not any(q[-7:] in c for q in query_phones for c in candidate_phones):
                continue
        last_sim = jaro_winkler(record.last_name or "", p.mom_last_name or "")
        if last_sim < thresholds.fuzzy_last_block:
            continue
        first_sim = jaro_winkler(record.first_name or "", p.mom_first_name or "")
        if first_sim < thresholds.fuzzy_first_block:
            continue
        address_sim = jaro_winkler(record.address or "", p.address or "")
        if address_sim < thresholds.fuzzy_addr_block:
            continue
        cluster_sim = jaro_winkler(record.cluster or "", p.cluster or "")
        if cluster_sim < thresholds.fuzzy_cluster_block:
            continue
        sex_match = 1 if record.sex and p.sex and record.sex == p.sex else 0
        dob_match = 1 if record.dob and p.dob and record.dob == p.dob else 0
        phone_match = 1 if any(q == c for q in query_phones for c in candidate_phones) else 0
        comp = (
            last_sim * weights.last_name_sim +
            first_sim * weights.first_name_sim +
            dob_match * weights.dob_match +
            sex_match * weights.sex_match +
            address_sim * weights.address_sim +
            phone_match * weights.phone_match
        )
        if comp >= thresholds.composite_threshold:
            results.append(Candidate(
                id=p.id,
                champs_id_ps=p.champs_id_ps,
                mom_first_name=p.mom_first_name,
                mom_last_name=p.mom_last_name,
                address=p.address,
                cluster=p.cluster,
                sex=p.sex,
                dob=p.dob,
                phones=candidate_phones,
                last_name_sim=last_sim,
                first_name_sim=first_sim,
                address_sim=address_sim,
                cluster_sim=cluster_sim,
                sex_match=sex_match,
                dob_match=dob_match,
                phone_match=phone_match,
                composite_score=comp,
            ))
    results.sort(key=lambda c: c.composite_score, reverse=True)
    return results[: req.top_n]
