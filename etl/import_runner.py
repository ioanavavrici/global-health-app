from dataclasses import dataclass
import logging
from pathlib import Path
import sys
from typing import Callable, Sequence
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Country
from etl.clean import clean_observations
from etl.load import (
    get_or_create_indicator,
    get_or_create_source,
    log_import,
    upsert_observations,
)
from etl.step_result import StepResult

logger = logging.getLogger(__name__)

RAW_ROOT = Path("data/raw")


@dataclass(frozen=True)
class SourceSpec:
    name: str
    url: str
    raw_dir: Path


@dataclass(frozen=True)
class IndicatorSpec:
    code: str
    remote_id: str
    name: str
    unit: str
    raw_filename: str


def import_indicators_with_session(
    session: Session,
    source: SourceSpec,
    indicators: Sequence[IndicatorSpec],
    transform_fn: Callable[[Path, str], pd.DataFrame],
    valid_iso3: set[str],
) -> list[StepResult]:
    results: list[StepResult] = []
    source_id = get_or_create_source(session, source.name, source.url)
    session.commit()

    for spec in indicators:
        path = source.raw_dir / spec.raw_filename
        if not path.exists():
            results.append(
                StepResult.from_error(
                    source.name, spec.code, FileNotFoundError(f"Missing raw file: {path}")
                )
            )
            continue

        try:
            raw_df = transform_fn(path, spec.code)
            cleaned_df = clean_observations(raw_df, valid_iso3)
            ind_id = get_or_create_indicator(
                session, spec.code, spec.name, spec.unit, source_id
            )
            loaded = upsert_observations(session, cleaned_df, ind_id)
            log_import(session, source.name, spec.code, str(path), loaded)
            session.commit()
            results.append(
                StepResult.ok(
                    source.name,
                    spec.code,
                    f"raw={len(raw_df)}, clean={len(cleaned_df)}, loaded={loaded}",
                )
            )
        except (ValueError, OSError, SQLAlchemyError) as error:
            session.rollback()
            logger.exception("%s %s: import failed", source.name, spec.code)
            results.append(StepResult.from_error(source.name, spec.code, error))

    return results


def import_for_loaded_countries(
    source: SourceSpec,
    indicators: Sequence[IndicatorSpec],
    transform_fn: Callable[[Path, str], pd.DataFrame],
) -> list[StepResult]:
    session = SessionLocal()
    try:
        valid_iso3 = set(session.execute(select(Country.iso3)).scalars().all())
        if not valid_iso3:
            err = RuntimeError("Country table is empty. Run World Bank import first.")
            return [StepResult.from_error(source.name, "countries", err)]
        return import_indicators_with_session(
            session, source, indicators, transform_fn, valid_iso3
        )
    finally:
        session.close()


def report_and_exit_on_failure(results: Sequence[StepResult]) -> None:
    failed = False
    for r in results:
        print(f"[{r.status.value.upper():<6}] {r.source:<18} {r.item:<20} {r.detail}")
        if not r.is_ok:
            failed = True
    if failed:
        sys.exit(1)
