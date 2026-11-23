from decimal import Decimal
import pytest
from app.domain import ObservationCriteria, ObservationListItem, Option
from app.models import Sex
from app.services.observation_service import ObservationService


def _item(year: int) -> ObservationListItem:
    return ObservationListItem(
        country_name="Romania",
        country_iso3="ROU",
        region="Europe & Central Asia",
        indicator_code="WHOSIS_000001",
        indicator_name="Life expectancy at birth",
        unit="years",
        year=year,
        sex=Sex.BOTH,
        value=Decimal("74.00"),
    )


class FakeRepository:
    def __init__(self, total_items: int) -> None:
        self.items = [_item(2000 + i) for i in range(total_items)]
        self.find_calls: list[tuple[ObservationCriteria, int, int]] = []

    def find(self, criteria: ObservationCriteria, *, limit: int, offset: int) -> list[ObservationListItem]:
        self.find_calls.append((criteria, limit, offset))
        return self.items[offset : offset + limit]

    def count(self, criteria: ObservationCriteria) -> int:
        return len(self.items)

    def list_countries(self) -> list[Option]:
        return [Option("ROU", "Romania (ROU)")]

    def list_indicators(self) -> list[Option]:
        return [Option("WHOSIS_000001", "Life expectancy at birth (WHOSIS_000001)")]

    def list_regions(self) -> list[Option]:
        return [Option("Europe & Central Asia", "Europe & Central Asia")]


@pytest.mark.parametrize(
    ("number", "expected_offset", "expected_len", "has_prev", "has_next"),
    [
        (1, 0, 4, False, True),
        (2, 4, 4, True, True),
        (3, 8, 1, True, False),
    ],
)
def test_get_page_pagination(number, expected_offset, expected_len, has_prev, has_next) -> None:
    repo = FakeRepository(total_items=9)
    service = ObservationService(repo, page_size=4)
    criteria = ObservationCriteria(country_iso3="ROU")

    page = service.get_page(criteria, number)

    assert repo.find_calls == [(criteria, 4, expected_offset)]
    assert len(page.items) == expected_len
    assert page.total_pages == 3
    assert page.has_previous is has_prev
    assert page.has_next is has_next


def test_empty_result_has_one_page() -> None:
    service = ObservationService(FakeRepository(total_items=0), page_size=4)
    page = service.get_page(ObservationCriteria(), 1)
    assert page.total_pages == 1
    assert page.has_previous is False
    assert page.has_next is False


def test_invalid_page_size_or_number_raises() -> None:
    with pytest.raises(ValueError):
        ObservationService(FakeRepository(total_items=1), page_size=0)
    service = ObservationService(FakeRepository(total_items=1), page_size=4)
    with pytest.raises(ValueError):
        service.get_page(ObservationCriteria(), 0)


def test_get_filter_options() -> None:
    service = ObservationService(FakeRepository(total_items=1), page_size=4)
    opts = service.get_filter_options()
    assert opts.countries == [Option("ROU", "Romania (ROU)")]
    assert len(opts.indicators) == 1
    assert len(opts.regions) == 1


def test_get_page_passes_sex_and_options_include_sexes() -> None:
    repo = FakeRepository(total_items=2)
    service = ObservationService(repo, page_size=4)
    criteria = ObservationCriteria(sex=Sex.MALE)
    service.get_page(criteria, 1)
    assert repo.find_calls == [(criteria, 4, 0)]
    assert [o.value for o in service.get_filter_options().sexes] == ["BTSX", "MLE", "FMLE"]
