from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.controllers import etl_controller, observation_controller, period_average_page_controller
from app.controllers.api import API_DOCS_URL, period_average_api, reference_data_api

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Global Health Data Platform",
        openapi_url="/api/openapi.json",
        docs_url=API_DOCS_URL,
        redoc_url=None,
    )
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # API routers (apar in OpenAPI / Swagger docs)
    app.include_router(reference_data_api.router)
    app.include_router(period_average_api.router)

    # HTML page controllers (excluse din Swagger)
    app.include_router(observation_controller.router, include_in_schema=False)
    app.include_router(etl_controller.router, include_in_schema=False)
    app.include_router(period_average_page_controller.router, include_in_schema=False)
    return app


app = create_app()
