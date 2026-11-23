from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.controllers.form_fields import blank_to_none, to_int_or_none, to_sex_or_none
from app.dependencies import get_observation_service
from app.domain import ObservationCriteria
from app.services.observation_service import ObservationService

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)


def observation_criteria(
    country: str | None = None,
    indicator: str | None = None,
    region: str | None = None,
    sex: str | None = None,
    year_from: str | None = None,
    year_to: str | None = None,
) -> ObservationCriteria:
    """Build filter criteria from query parameters; ignore blank or invalid values."""
    return ObservationCriteria(
        country_iso3=blank_to_none(country),
        indicator_code=blank_to_none(indicator),
        region=blank_to_none(region),
        sex=to_sex_or_none(sex),
        year_from=to_int_or_none(year_from),
        year_to=to_int_or_none(year_to),
    )


@router.get("/", response_class=HTMLResponse)
def show_observations(
    request: Request,
    criteria: Annotated[ObservationCriteria, Depends(observation_criteria)],
    service: Annotated[ObservationService, Depends(get_observation_service)],
    page: Annotated[int, Query(ge=1)] = 1,
) -> HTMLResponse:
    observations = service.get_page(criteria, page)

    def page_url(number: int) -> str:
        return str(request.url.include_query_params(page=number))

    return templates.TemplateResponse(
        request,
        "observations.html",
        {
            "observations": observations,
            "criteria": criteria,
            "options": service.get_filter_options(),
            "previous_url": page_url(page - 1) if observations.has_previous else None,
            "next_url": page_url(page + 1) if observations.has_next else None,
        },
    )
