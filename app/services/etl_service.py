from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Callable, Sequence
import requests
from sqlalchemy.exc import SQLAlchemyError
from etl import import_owid, import_who, import_worldbank
from etl.extract_owid import download_owid_chart
from etl.extract_who import WhoApiError, download_who_indicator
from etl.extract_worldbank import (
    WorldBankApiError,
    download_worldbank_countries,
    download_worldbank_indicator,
)
from etl.step_result import StepResult

logger = logging.getLogger(__name__)

EXTRACT_ERRORS = (
    OSError,
    ValueError,
    requests.RequestException,
    WorldBankApiError,
    WhoApiError,
)
IMPORT_ERRORS = (OSError, ValueError, SQLAlchemyError)


@dataclass(frozen=True)
class ExtractJob:
    source: str
    item: str
    download: Callable[[], Path | tuple[Path, str]]


@dataclass(frozen=True)
class ImportJob:
    source: str
    run: Callable[[], list[StepResult]]


def _default_extract_jobs() -> tuple[ExtractJob, ...]:
    jobs: list[ExtractJob] = [
        ExtractJob("World Bank", "countries", download_worldbank_countries)
    ]
    for spec in import_worldbank.INDICATORS:
        jobs.append(
            ExtractJob(
                "World Bank",
                spec.code,
                lambda code=spec.remote_id: download_worldbank_indicator(code),
            )
        )
    for spec in import_who.INDICATORS:
        jobs.append(
            ExtractJob(
                "WHO",
                spec.code,
                lambda code=spec.remote_id: download_who_indicator(code),
            )
        )
    for spec in import_owid.INDICATORS:
        jobs.append(
            ExtractJob(
                "Our World in Data",
                spec.code,
                lambda slug=spec.remote_id: download_owid_chart(slug),
            )
        )
    return tuple(jobs)


DEFAULT_IMPORT_JOBS: tuple[ImportJob, ...] = (
    ImportJob("World Bank", import_worldbank.import_all),
    ImportJob("WHO", import_who.import_all),
    ImportJob("Our World in Data", import_owid.import_all),
)


def _run_extract(job: ExtractJob) -> StepResult:
    try:
        res = job.download()
        path = res[0] if isinstance(res, tuple) else res
        size = path.stat().st_size
        return StepResult.ok(job.source, job.item, f"{path.name} ({size:,} bytes)")
    except EXTRACT_ERRORS as error:
        logger.exception("%s %s: extract failed", job.source, job.item)
        return StepResult.from_error(job.source, job.item, error)


def _run_import(job: ImportJob) -> list[StepResult]:
    try:
        return job.run()
    except IMPORT_ERRORS as error:
        logger.exception("%s: import failed", job.source)
        return [StepResult.from_error(job.source, "all", error)]


class EtlService:
    """Orchestrates raw extraction and database transform & load jobs."""

    def __init__(
        self,
        extract_jobs: Sequence[ExtractJob] | None = None,
        import_jobs: Sequence[ImportJob] = DEFAULT_IMPORT_JOBS,
    ) -> None:
        self._extract_jobs = (
            _default_extract_jobs() if extract_jobs is None else tuple(extract_jobs)
        )
        self._import_jobs = tuple(import_jobs)

    def extract_all(self) -> list[StepResult]:
        """Download every source into data/raw/; one result per file."""
        return [_run_extract(job) for job in self._extract_jobs]

    def transform_and_load_all(self) -> list[StepResult]:
        """Transform, clean and load the raw files of every source."""
        return [
            result for job in self._import_jobs for result in _run_import(job)
        ]
