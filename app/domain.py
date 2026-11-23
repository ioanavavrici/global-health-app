from dataclasses import dataclass
from decimal import Decimal
from app.models import Sex


@dataclass(frozen=True)
class ObservationCriteria:
    """Filters for observations; ``None`` means do not filter on this."""

    country_iso3: str | None = None
    indicator_code: str | None = None
    region: str | None = None
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
