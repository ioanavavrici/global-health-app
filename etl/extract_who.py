import json
import logging
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw/who")
RAW_DIR.mkdir(parents=True, exist_ok=True)

class WhoApiError(Exception):
    pass

def _download_rows(code: str, filter_str: str) -> tuple[list[dict], str]:
    base_url = f"https://ghoapi.azureedge.net/api/{code}"
    params = {"$filter": filter_str}
    rows = []
    next_url = base_url

    while next_url:
        response = requests.get(next_url, params=params, timeout=120)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, dict):
            raise WhoApiError(f"{next_url}: expected JSON object, got {payload!r}")

        value = payload.get("value", [])
        if not isinstance(value, list):
            raise WhoApiError(f"{next_url}: 'value' is not a list: {value!r}")

        rows.extend(value)
        next_link = payload.get("@odata.nextLink")
        next_url = next_link if isinstance(next_link, str) else None
        params = None

    return rows, base_url

def download_who_indicator(code: str, year_from: int = 2000) -> tuple[Path, str]:
    filter_str = f"SpatialDimType eq 'COUNTRY' and TimeDim ge {year_from}"
    rows, url = _download_rows(code, filter_str)
    filename = f"{code}_from{year_from}.json"
    path = RAW_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    logger.info("Saved %d WHO records for %s to %s", len(rows), code, path)
    return path, url
