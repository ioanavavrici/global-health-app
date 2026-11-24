from decimal import Decimal
from app.domain import PeriodAverageQuery
from app.models import Sex
from app.repositories.period_average_repository import PeriodAverageRepository


def test_average_by_period_computes_in_db(db_session) -> None:
    repo = PeriodAverageRepository(db_session)
    # db_session contine din Lab 3:
    # ROU WHOSIS_000001: 2021 BTSX (72.70), 2021 MLE (69.10), 2021 FMLE (76.50)
    # FRA WHOSIS_000001: 2020 BTSX (82.10)
    query = PeriodAverageQuery(
        indicator_code="WHOSIS_000001",
        country_iso3s=("ROU", "FRA"),
        first_year=2020,
        last_year=2024,
        period_years=5,
        sex=Sex.BOTH,
    )
    averages = repo.average_by_period(query, sex=Sex.BOTH)
    assert len(averages) == 2
    by_c = {a.country_iso3: a for a in averages}
    assert by_c["FRA"].period_start == 2020
    assert by_c["FRA"].average == Decimal("82.1000")
    assert by_c["ROU"].period_start == 2020
    assert by_c["ROU"].average == Decimal("72.7000")
