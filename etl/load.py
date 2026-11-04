import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import select, insert, func
from sqlalchemy.orm import Session
from app.models import Source, Country, Indicator, Observation, ImportLog

logger = logging.getLogger(__name__)

def get_or_create_source(session: Session, name: str, url: str) -> int:
    stmt = select(Source.source_id).where(Source.name == name)
    res = session.execute(stmt).scalar_one_or_none()
    if res is not None:
        return res
    stmt = insert(Source).values(name=name, url=url).returning(Source.source_id)
    return session.execute(stmt).scalar_one()

def upsert_countries(session: Session, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    records = df.to_dict(orient="records")
    for chunk_start in range(0, len(records), 500):
        chunk = records[chunk_start : chunk_start + 500]
        for r in chunk:
            session.merge(Country(**r))
    session.flush()
    return len(records)

def get_or_create_indicator(session: Session, code: str, name: str, unit: str, source_id: int) -> int:
    stmt = select(Indicator.indicator_id).where(Indicator.code == code)
    res = session.execute(stmt).scalar_one_or_none()
    if res is not None:
        return res
    stmt = insert(Indicator).values(
        code=code, name=name, unit=unit, source_id=source_id
    ).returning(Indicator.indicator_id)
    return session.execute(stmt).scalar_one()

def upsert_observations(session: Session, df: pd.DataFrame, indicator_id: int) -> int:
    if df.empty:
        return 0
    
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "country_iso3": r["country_iso3"],
            "indicator_id": indicator_id,
            "year": int(r["year"]),
            "sex": r["sex"],
            "value": float(r["value"]) if pd.notna(r["value"]) else None,
            "is_outlier": bool(r.get("is_outlier", False)),
        })

    chunk_size = 1000
    total_loaded = 0
    for start in range(0, len(rows), chunk_size):
        chunk = rows[start : start + chunk_size]
        stmt = insert(Observation).values(chunk)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_observation",
            set_={
                "value": stmt.excluded.value,
                "is_outlier": stmt.excluded.is_outlier,
                "imported_at": func.now(),
            },
        )
        session.execute(stmt)
        total_loaded += len(chunk)
    session.flush()
    return total_loaded

def log_import(session: Session, source_name: str, indicator_code: str, url: str, rows_loaded: int) -> None:
    session.add(ImportLog(
        source_name=source_name,
        indicator_code=indicator_code,
        url=url,
        rows_loaded=rows_loaded
    ))
    session.flush()
