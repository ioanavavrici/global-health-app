import json
import logging
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw/worldbank")
RAW_DIR.mkdir(parents=True, exist_ok=True)

class WorldBankApiError(Exception):
    pass

def _get_all_pages(url: str, params: dict) -> list[dict]:
    records = []
    page = 1
    params = params.copy()
    params["format"] = "json"
    params["per_page"] = 400

    while True:
        params["page"] = page
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        body = response.json()

        if not (isinstance(body, list) and len(body) == 2):
            raise WorldBankApiError(f"{url}: unexpected response {body!r}")

        meta, data = body
        if not isinstance(meta, dict) or "pages" not in meta:
            raise WorldBankApiError(f"{url}: missing page metadata in {meta!r}")

        records.extend(data or [])
        if page >= int(meta["pages"]):
            return records
        page += 1

def download_worldbank_countries() -> Path:
    url = "https://api.worldbank.org/v2/country"
    data = _get_all_pages(url, {})
    path = RAW_DIR / "countries.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved %d World Bank countries to %s", len(data), path)
    return path

def download_worldbank_indicator(code: str, year_from: int = 2000, year_to: int = 2024) -> Path:
    url = f"https://api.worldbank.org/v2/country/all/indicator/{code}"
    params = {"date": f"{year_from}:{year_to}"}
    data = _get_all_pages(url, params)
    filename = f"{code}_from{year_from}.json"
    path = RAW_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved %d records for %s to %s", len(data), code, path)
    return path
