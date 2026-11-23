from app.domain import ObservationCriteria
from app.models import Sex
from app.repositories.observation_repository import ObservationRepository


def _keys(items):
    return [(i.country_iso3, i.indicator_code, i.year, i.sex) for i in items]


def test_find_returns_rows_in_stable_order(db_session) -> None:
    repo = ObservationRepository(db_session)
    items = repo.find(ObservationCriteria(), limit=100, offset=0)

    assert len(items) == 9
    # Brazil first alphabetically, then France (2020 before 2015)
    assert items[0].country_iso3 == "BRA"
    assert _keys(items[1:3]) == [
        ("FRA", "WHOSIS_000001", 2020, Sex.BOTH),
        ("FRA", "NY.GDP.PCAP.CD", 2015, Sex.BOTH),
    ]


def test_filter_by_region_and_years(db_session) -> None:
    repo = ObservationRepository(db_session)
    criteria = ObservationCriteria(region="Latin America & Caribbean", year_from=2019, year_to=2021)
    assert repo.count(criteria) == 1
    items = repo.find(criteria, limit=10, offset=0)
    assert items[0].country_iso3 == "BRA"


def test_list_filter_options(db_session) -> None:
    repo = ObservationRepository(db_session)
    assert len(repo.list_countries()) == 4
    assert len(repo.list_indicators()) == 2
    assert [o.value for o in repo.list_regions()] == [
        "Europe & Central Asia",
        "Latin America & Caribbean",
    ]


def test_filter_by_sex_returns_only_that_sex(db_session) -> None:
    repo = ObservationRepository(db_session)
    criteria = ObservationCriteria(country_iso3="ROU", sex=Sex.MALE)
    items = repo.find(criteria, limit=10, offset=0)
    assert len(items) == 1
    assert items[0].sex == Sex.MALE
    assert items[0].country_iso3 == "ROU"
