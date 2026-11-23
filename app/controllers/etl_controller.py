from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_etl_service
from app.services.etl_service import EtlService
from etl.step_result import StepResult

router = APIRouter(prefix="/actions")
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)


def _render_step_results(
    request: Request,
    *,
    action: str,
    description: str,
    results: list[StepResult],
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "action_result.html",
        {
            "action": action,
            "description": description,
            "results": results,
        },
    )


@router.post("/extract", response_class=HTMLResponse)
def extract(
    request: Request,
    service: Annotated[EtlService, Depends(get_etl_service)],
) -> HTMLResponse:
    return _render_step_results(
        request,
        action="Extract",
        description="Downloaded raw data from external sources into data/raw/.",
        results=service.extract_all(),
    )


@router.post("/load", response_class=HTMLResponse)
def transform_and_load(
    request: Request,
    service: Annotated[EtlService, Depends(get_etl_service)],
) -> HTMLResponse:
    return _render_step_results(
        request,
        action="Transform & Load",
        description="Transformed, cleaned, and loaded cached raw files into PostgreSQL.",
        results=service.transform_and_load_all(),
    )
