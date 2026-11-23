import io
import logging
from pathlib import Path
import pandas as pd
import requests

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw/owid")
RAW_DIR.mkdir(parents=True, exist_ok=True)
_HEADERS = {"User-Agent": "GlobalHealthPlatform/1.0"}

def download_owid_chart(slug: str) -> tuple[Path, str]:
    url = f"https://ourworldindata.org/grapher/{slug}.csv?v=1&csvType=full&useColumnShortNames=true"
    response = requests.get(url, headers=_HEADERS, timeout=60)
    response.raise_for_status()

    path = RAW_DIR / f"{slug}.csv"
    with open(path, "w", encoding="utf-8") as f:
        f.write(response.text)

    logger.info("Saved OWID chart %s to %s", slug, path)
    return path, url
