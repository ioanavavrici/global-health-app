from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.controllers.api.schemas import PeriodAveragesResponse
from app.controllers.form_fields import to_sex_or_none
from app.dependencies import get_period_average_service
from app.domain import InvalidQueryError, PeriodAverageQuery, UnknownIndicatorError
from app.models import Sex
from app.services.period_average_service import (
    DEFAULT_FIRST_YEAR,
    DEFAULT_LAST_YEAR,
    DEFAULT_PERIOD_YEARS,
    PeriodAverageService,
)

router = APIRouter(prefix="/api", tags=["period averages"])
AvgServiceDep = Annotated[PeriodAverageService, Depends(get_period_average_service)]


def period_average_query(
    indicator_code: str,
    country: Annotated[
        list[str] | None,
        Query(description="ISO3 code; repeat it for more countries (e.g. ?country=ROU&country=FRA)"),
    ] = None,
    first_year: int = DEFAULT_FIRST_YEAR,
    last_year: int = DEFAULT_LAST_YEAR,
    period_years: Annotated[int, Query(ge=1)] = DEFAULT_PERIOD_YEARS,
    sex: str | None = None,
) -> PeriodAverageQuery:
    parsed_sex = to_sex_or_none(sex) or Sex.BOTH
    return PeriodAverageQuery(
        indicator_code=indicator_code,
        country_iso3s=tuple(dict.fromkeys(country or ())),
        first_year=first_year,
        last_year=last_year,
        period_years=period_years,
        sex=parsed_sex,
    )


@router.get("/indicators/{indicator_code}/period-averages")
def get_period_averages(
    query: Annotated[PeriodAverageQuery, Depends(period_average_query)],
    service: AvgServiceDep,
) -> PeriodAveragesResponse:
    try:
        report = service.get_report(query)
    except UnknownIndicatorError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except InvalidQueryError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)) from error
    return PeriodAveragesResponse.from_domain(report)
