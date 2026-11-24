from decimal import Decimal
import pytest
from app.domain import (
    IndicatorInfo,
    InvalidQueryError,
    PeriodAverage,
    PeriodAverageQuery,
    UnknownIndicatorError,
)
from app.models import Sex
from app.services.period_average_service import PeriodAverageService


class FakeAvgRepository:
    def __init__(self, indicator_exists: bool = True) -> None:
        self.indicator_exists = indicator_exists
        self.calls: list[tuple[PeriodAverageQuery, Sex]] = []

    def find_country_names(self, iso3s: tuple[str, ...]) -> dict[str, str]:
        return {iso3: f"Country {iso3}" for iso3 in iso3s}

    def find_indicator(self, code: str) -> IndicatorInfo | None:
        if not self.indicator_exists:
            return None
        return IndicatorInfo(code=code, name="Life expectancy at birth", unit="years")

    def average_by_period(self, query: PeriodAverageQuery, sex: Sex = Sex.BOTH) -> list[PeriodAverage]:
        self.calls.append((query, sex))
        return [
            PeriodAverage("ROU", "Romania", 2000, Decimal("71.304"), 5),
            PeriodAverage("ROU", "Romania", 2005, Decimal("72.801"), 5),
            PeriodAverage("FRA", "France", 2000, Decimal("79.222"), 5),
        ]


def test_periods_generation_and_rounding() -> None:
    repo = FakeAvgRepository()
    svc = PeriodAverageService(repo)
    query = PeriodAverageQuery(
        indicator_code="WHOSIS_000001",
        country_iso3s=("ROU", "FRA"),
        first_year=2000,
        last_year=2009,
        period_years=5,
    )
    report = svc.get_report(query)

    assert [p.label for p in report.periods] == ["2000-2004", "2005-2009"]
    assert len(report.series) == 2
    rou = next(s for s in report.series if s.country_iso3 == "ROU")
    assert rou.averages == [Decimal("71.30"), Decimal("72.80")]
    fra = next(s for s in report.series if s.country_iso3 == "FRA")
    # In 2005-2009 FRA nu are inregistrari in repo -> None
    assert fra.averages == [Decimal("79.22"), None]


def test_unknown_indicator_raises() -> None:
    svc = PeriodAverageService(FakeAvgRepository(indicator_exists=False))
    query = PeriodAverageQuery("UNKNOWN", ("ROU",), 2000, 2020, 5)
    with pytest.raises(UnknownIndicatorError):
        svc.get_report(query)


@pytest.mark.parametrize(
    "query",
    [
        PeriodAverageQuery("WHOSIS_000001", ("ROU",), 2000, 2020, 0),  # period_years < 1
        PeriodAverageQuery("WHOSIS_000001", ("ROU",), 2020, 2010, 5),  # first_year > last_year
        PeriodAverageQuery("WHOSIS_000001", tuple(f"C{i:02d}" for i in range(21)), 2000, 2020, 5),  # > 20 tari
    ],
)
def test_invalid_query_validation(query) -> None:
    svc = PeriodAverageService(FakeAvgRepository())
    with pytest.raises(InvalidQueryError):
        svc.get_report(query)


def test_country_without_observations_gets_none_series() -> None:
    svc = PeriodAverageService(FakeAvgRepository())
    query = PeriodAverageQuery("WHOSIS_000001", ("ROU", "GIB"), 2000, 2009, 5)
    report = svc.get_report(query)
    gib = next(s for s in report.series if s.country_iso3 == "GIB")
    assert gib.country_name == "Country GIB"
    assert gib.averages == [None, None]
