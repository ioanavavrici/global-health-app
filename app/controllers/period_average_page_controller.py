from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.controllers.api import API_DOCS_URL
from app.services.period_average_service import (
    DEFAULT_FIRST_YEAR,
    DEFAULT_LAST_YEAR,
)

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)
MAX_CHART_COUNTRIES = 8


@router.get("/period-averages", response_class=HTMLResponse)
def show_period_averages(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "period_averages.html",
        {
            "first_year": DEFAULT_FIRST_YEAR,
            "last_year": DEFAULT_LAST_YEAR,
            "max_countries": MAX_CHART_COUNTRIES,
            "api_docs_url": API_DOCS_URL,
        },
    )
