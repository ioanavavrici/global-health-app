import json
import logging
from pathlib import Path
import time
import requests

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw/worldbank")
RAW_DIR.mkdir(parents=True, exist_ok=True)


class WorldBankApiError(Exception):
    pass


def _get_all_pages(url: str, params: dict, label: str = "") -> list[dict]:
    records = []
    page = 1
    params = params.copy()
    params["format"] = "json"
    params["per_page"] = 1000
    headers = {"User-Agent": "GlobalHealthPlatform/1.0", "Accept": "application/json"}

    while True:
        params["page"] = page
        retries = 5
        body = None
        last_err = None
        while retries > 0:
            try:
                response = requests.get(url, params=params, headers=headers, timeout=90)
                response.raise_for_status()
                body = response.json()
                break
            except Exception as e:
                last_err = e
                retries -= 1
                if retries == 0:
                    raise WorldBankApiError(f"{url} page {page} failed: {e}") from e
                time.sleep(3)

        if not (isinstance(body, list) and len(body) == 2):
            raise WorldBankApiError(f"{url}: unexpected response {body!r}")

        meta, data = body
        if not isinstance(meta, dict) or "pages" not in meta:
            raise WorldBankApiError(f"{url}: missing page metadata in {meta!r}")

        records.extend(data or [])
        total_pages = int(meta.get("pages", 1))
        print(f"  [{label}] Descarcat pagina {page}/{total_pages} (total {len(records)} inregistrari)")

        if page >= total_pages or total_pages == 0:
            return records
        page += 1
        time.sleep(0.5)


def download_worldbank_countries() -> Path:
    path = RAW_DIR / "countries.json"
    if path.exists() and path.stat().st_size > 1000:
        return path
    url = "https://api.worldbank.org/v2/country"
    data = _get_all_pages(url, {}, label="Countries")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def download_worldbank_indicator(code: str, year_from: int = 2000, year_to: int = 2024) -> Path:
    filename = f"{code}_from{year_from}.json"
    path = RAW_DIR / filename
    if path.exists() and path.stat().st_size > 5000:
        print(f"{filename} exista deja, folosim cache-ul.")
        return path

    url = f"https://api.worldbank.org/v2/country/all/indicator/{code}"
    params = {"date": f"{year_from}:{year_to}"}
    print(f"\nDescarcare {code} de la World Bank...")
    data = _get_all_pages(url, params, label=code)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Salvat {len(data)} inregistrari in {filename}")
    return path
