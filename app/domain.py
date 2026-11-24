from dataclasses import dataclass
from decimal import Decimal
from app.models import Sex


@dataclass(frozen=True)
class ObservationCriteria:
    """Filters for observations; ``None`` means do not filter on this."""

    country_iso3: str | None = None
    indicator_code: str | None = None
    region: str | None = None
    sex: Sex | None = None
    year_from: int | None = None
    year_to: int | None = None


@dataclass(frozen=True)
class ObservationListItem:
    """One entry of the observations list joined with country and indicator details."""

    country_name: str
    country_iso3: str
    region: str | None
    indicator_code: str
    indicator_name: str
    unit: str | None
    year: int
    sex: Sex
    value: Decimal | None


@dataclass(frozen=True)
class Option:
    """One choice of a filter drop-down list."""

    value: str
    label: str


@dataclass(frozen=True)
class FilterOptions:
    """All drop-down lists needed by the filter form."""

    countries: list[Option]
    indicators: list[Option]
    regions: list[Option]
    sexes: list[Option]


class DomainError(Exception):
    """Base for domain-level business errors."""


class UnknownIndicatorError(DomainError):
    """Raised when an indicator code is not found in the database."""


class InvalidQueryError(DomainError):
    """Raised when query parameters violate business rules."""


@dataclass(frozen=True)
class IndicatorInfo:
    code: str
    name: str
    unit: str | None


@dataclass(frozen=True)
class PeriodInfo:
    start: int
    end: int
    label: str


@dataclass(frozen=True)
class PeriodAverage:
    country_iso3: str
    country_name: str
    period_start: int
    average: Decimal | None
    observation_count: int


@dataclass(frozen=True)
class CountrySeries:
    country_iso3: str
    country_name: str
    averages: list[Decimal | None]


@dataclass(frozen=True)
class PeriodAverageQuery:
    indicator_code: str
    country_iso3s: tuple[str, ...]
    first_year: int
    last_year: int
    period_years: int
    sex: Sex = Sex.BOTH


@dataclass(frozen=True)
class PeriodAverageReport:
    indicator: IndicatorInfo
    periods: list[PeriodInfo]
    series: list[CountrySeries]
