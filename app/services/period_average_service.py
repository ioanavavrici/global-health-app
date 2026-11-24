from decimal import Decimal, ROUND_HALF_UP
from app.domain import (
    CountrySeries,
    IndicatorInfo,
    InvalidQueryError,
    PeriodAverage,
    PeriodAverageQuery,
    PeriodAverageReport,
    PeriodInfo,
    UnknownIndicatorError,
)
from app.models import Sex
from app.repositories.period_average_repository import PeriodAverageRepository

DEFAULT_FIRST_YEAR = 2000
DEFAULT_LAST_YEAR = 2023
DEFAULT_PERIOD_YEARS = 5
MAX_QUERY_COUNTRIES = 20
AVERAGED_SEX = Sex.BOTH


def _round_half_up(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _validate(query: PeriodAverageQuery) -> None:
    if query.period_years < 1:
        raise InvalidQueryError(f"period_years must be at least 1, got {query.period_years}")
    if query.first_year > query.last_year:
        raise InvalidQueryError(
            f"first_year {query.first_year} is after last_year {query.last_year}"
        )
    if len(query.country_iso3s) > MAX_QUERY_COUNTRIES:
        raise InvalidQueryError(
            f"at most {MAX_QUERY_COUNTRIES} countries, got {len(query.country_iso3s)}"
        )


def _periods(query: PeriodAverageQuery) -> list[PeriodInfo]:
    periods: list[PeriodInfo] = []
    start = query.first_year
    while start <= query.last_year:
        end = min(start + query.period_years - 1, query.last_year)
        label = f"{start}" if start == end else f"{start}-{end}"
        periods.append(PeriodInfo(start=start, end=end, label=label))
        start += query.period_years
    return periods


def _series(
    country_iso3s: tuple[str, ...],
    periods: list[PeriodInfo],
    averages: list[PeriodAverage],
    country_names: dict[str, str],
) -> list[CountrySeries]:
    # Harta rapida: (iso3, period_start) -> average
    avg_map: dict[tuple[str, int], Decimal | None] = {}
    for a in averages:
        avg_map[(a.country_iso3, a.period_start)] = a.average

    result: list[CountrySeries] = []
    for iso3 in country_iso3s:
        c_name = country_names.get(iso3, iso3)
        c_averages = [
            _round_half_up(avg_map.get((iso3, p.start)))
            for p in periods
        ]
        result.append(
            CountrySeries(
                country_iso3=iso3,
                country_name=c_name,
                averages=c_averages,
            )
        )
    return result


class PeriodAverageService:
    """Business logic for period averaging, validation, and series formatting."""

    def __init__(self, repository: PeriodAverageRepository) -> None:
        self._repository = repository

    def find_indicator(self, code: str) -> IndicatorInfo | None:
        return self._repository.find_indicator(code)

    def get_report(self, query: PeriodAverageQuery) -> PeriodAverageReport:
        _validate(query)
        indicator = self._repository.find_indicator(query.indicator_code)
        if indicator is None:
            raise UnknownIndicatorError(f"unknown indicator {query.indicator_code!r}")

        periods = _periods(query)
        sex = query.sex if query.sex is not None else AVERAGED_SEX
        averages = self._repository.average_by_period(query, sex=sex)

        country_names = {a.country_iso3: a.country_name for a in averages}
        missing_names = tuple(
            iso3 for iso3 in query.country_iso3s if iso3 not in country_names
        )
        if missing_names:
            country_names.update(self._repository.find_country_names(missing_names))

        series = _series(query.country_iso3s, periods, averages, country_names)
        return PeriodAverageReport(indicator=indicator, periods=periods, series=series)
