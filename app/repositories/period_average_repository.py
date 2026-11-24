from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.domain import IndicatorInfo, PeriodAverage, PeriodAverageQuery
from app.models import Country, Indicator, Observation, Sex


class PeriodAverageRepository:
    """Computes period averages directly inside PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_country_names(self, iso3s: tuple[str, ...]) -> dict[str, str]:
        if not iso3s:
            return {}
        stmt = select(Country.iso3, Country.name).where(Country.iso3.in_(iso3s))
        return {row.iso3: row.name for row in self._session.execute(stmt)}

    def find_indicator(self, code: str) -> IndicatorInfo | None:
        stmt = select(Indicator.code, Indicator.name, Indicator.unit).where(
            Indicator.code == code
        )
        row = self._session.execute(stmt).first()
        if row is None:
            return None
        return IndicatorInfo(code=row.code, name=row.name, unit=row.unit)

    def average_by_period(
        self, query: PeriodAverageQuery, sex: Sex = Sex.BOTH
    ) -> list[PeriodAverage]:
        if not query.country_iso3s:
            return []

        # Calculul matematic al inceputului de perioada (bucket)
        period_start = (
            query.first_year
            + (Observation.year - query.first_year)
            // query.period_years
            * query.period_years
        )

        bucketed = (
            select(
                Observation.country_iso3,
                period_start.label("period_start"),
                Observation.value,
            )
            .join(Indicator, Observation.indicator_id == Indicator.indicator_id)
            .where(
                Indicator.code == query.indicator_code,
                Observation.country_iso3.in_(query.country_iso3s),
                Observation.year.between(query.first_year, query.last_year),
                Observation.sex == (sex.value if isinstance(sex, Sex) else sex),
                Observation.value.is_not(None),
            )
            .subquery()
        )

        averages_stmt = (
            select(
                Country.iso3.label("country_iso3"),
                Country.name.label("country_name"),
                bucketed.c.period_start,
                func.avg(bucketed.c.value).label("average"),
                func.count().label("observation_count"),
            )
            .join(Country, Country.iso3 == bucketed.c.country_iso3)
            .group_by(Country.iso3, Country.name, bucketed.c.period_start)
            .order_by(Country.name, bucketed.c.period_start)
        )

        rows = self._session.execute(averages_stmt).all()
        return [
            PeriodAverage(
                country_iso3=r.country_iso3,
                country_name=r.country_name,
                period_start=int(r.period_start),
                average=Decimal(str(r.average)) if r.average is not None else None,
                observation_count=int(r.observation_count),
            )
            for r in rows
        ]
