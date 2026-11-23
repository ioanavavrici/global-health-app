from decimal import Decimal
from app.dependencies import get_observation_service
from app.domain import FilterOptions, ObservationCriteria, ObservationListItem, Option
from app.main import app
from app.models import Sex
from app.services.observation_service import ObservationPage


class FakeObservationService:
    def __init__(self, page: ObservationPage) -> None:
        self._page = page
        self.calls: list[tuple[ObservationCriteria, int]] = []

    def get_page(self, criteria: ObservationCriteria, number: int) -> ObservationPage:
        self.calls.append((criteria, number))
        return self._page

    def get_filter_options(self) -> FilterOptions:
        return FilterOptions(
            countries=[Option("ROU", "Romania (ROU)")],
            indicators=[Option("WHOSIS_000001", "Life expectancy (WHOSIS_000001)")],
            regions=[Option("Europe & Central Asia", "Europe & Central Asia")],
        )


def test_show_observations_parses_criteria_and_renders_html(client) -> None:
    page = ObservationPage(
        items=[
            ObservationListItem(
                country_name="Romania",
                country_iso3="ROU",
                region="Europe & Central Asia",
                indicator_code="WHOSIS_000001",
                indicator_name="Life expectancy at birth",
                unit="years",
                year=2021,
                sex=Sex.BOTH,
                value=Decimal("72.70"),
            )
        ],
        number=1,
        size=4,
        total_items=9,
    )
    fake = FakeObservationService(page)
    app.dependency_overrides[get_observation_service] = lambda: fake

    resp = client.get("/?country=ROU&year_from=abc&year_to=2022")

    assert resp.status_code == 200
    assert fake.calls == [
        (ObservationCriteria(country_iso3="ROU", year_from=None, year_to=2022), 1)
    ]
    assert "Romania (ROU)" in resp.text
    assert "72.70" in resp.text
    assert "page=2" in resp.text


def test_invalid_page_returns_422(client) -> None:
    app.dependency_overrides[get_observation_service] = lambda: FakeObservationService(
        ObservationPage(items=[], number=1, size=4, total_items=0)
    )
    assert client.get("/?page=0").status_code == 422


def test_template_escapes_html_in_values(client) -> None:
    page = ObservationPage(
        items=[
            ObservationListItem(
                country_name="<script>alert(1)</script>",
                country_iso3="ROU",
                region=None,
                indicator_code="X",
                indicator_name="Test",
                unit=None,
                year=2021,
                sex=Sex.BOTH,
                value=None,
            )
        ],
        number=1,
        size=4,
        total_items=1,
    )
    app.dependency_overrides[get_observation_service] = lambda: FakeObservationService(page)
    resp = client.get("/")
    assert "<script>alert(1)</script>" not in resp.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in resp.text
