from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.controllers.api.schemas import CountryResponse, IndicatorDetailResponse, IndicatorResponse
from app.dependencies import get_observation_service, get_period_average_service
from app.services.observation_service import ObservationService
from app.services.period_average_service import PeriodAverageService

router = APIRouter(prefix="/api", tags=["reference data"])
ObsServiceDep = Annotated[ObservationService, Depends(get_observation_service)]
AvgServiceDep = Annotated[PeriodAverageService, Depends(get_period_average_service)]


@router.get("/regions")
def list_regions(service: ObsServiceDep) -> list[str]:
    return [opt.value for opt in service.list_regions()]


@router.get("/countries")
def list_countries(
    service: ObsServiceDep, region: str | None = None
) -> list[CountryResponse]:
    return [CountryResponse.from_option(c) for c in service.list_countries(region)]


@router.get("/indicators")
def list_indicators(service: ObsServiceDep) -> list[IndicatorResponse]:
    return [IndicatorResponse.from_option(i) for i in service.list_indicators()]


@router.get("/indicators/{indicator_code}")
def get_indicator(
    indicator_code: str, service: AvgServiceDep
) -> IndicatorDetailResponse:
    info = service.find_indicator(indicator_code)
    if info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"unknown indicator {indicator_code!r}",
        )
    return IndicatorDetailResponse.from_domain(info)
