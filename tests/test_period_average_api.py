from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from app.dependencies import get_period_average_service
from app.domain import (
    CountrySeries,
    IndicatorInfo,
    InvalidQueryError,
    PeriodAverageQuery,
    PeriodAverageReport,
    PeriodInfo,
    UnknownIndicatorError,
)
from app.main import app
from app.models import Sex


class FakePeriodAverageService:
    def __init__(self, report_or_error) -> None:
        self.target = report_or_error
        self.calls: list[PeriodAverageQuery] = []

    def get_report(self, query: PeriodAverageQuery) -> PeriodAverageReport:
        self.calls.append(query)
        if isinstance(self.target, Exception):
            raise self.target
        return self.target


def test_period_averages_api_returns_json_numbers() -> None:
    sample_report = PeriodAverageReport(
        indicator=IndicatorInfo("WHOSIS_000001", "Life expectancy", "years"),
        periods=[PeriodInfo(2000, 2004, "2000-2004")],
        series=[CountrySeries("ROU", "Romania", [Decimal("71.30")])],
    )
    fake = FakePeriodAverageService(sample_report)
    app.dependency_overrides[get_period_average_service] = lambda: fake
    try:
        client = TestClient(app)
        resp = client.get("/api/indicators/WHOSIS_000001/period-averages?country=ROU&country=FRA&sex=MLE")
        assert resp.status_code == 200
        data = resp.json()

        val = data["series"][0]["averages"][0]
        assert isinstance(val, (int, float))
        assert val == 71.3
        assert fake.calls[0].country_iso3s == ("ROU", "FRA")
        assert fake.calls[0].sex == Sex.MALE
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (UnknownIndicatorError("unknown indicator 'X'"), 404),
        (InvalidQueryError("period_years must be at least 1"), 422),
    ],
)
def test_service_errors_become_http_status_codes(error, expected_status) -> None:
    fake = FakePeriodAverageService(error)
    app.dependency_overrides[get_period_average_service] = lambda: fake
    try:
        client = TestClient(app)
        resp = client.get("/api/indicators/WHOSIS_000001/period-averages?country=ROU")
        assert resp.status_code == expected_status
        assert resp.json() == {"detail": str(error)}
    finally:
        app.dependency_overrides.clear()
