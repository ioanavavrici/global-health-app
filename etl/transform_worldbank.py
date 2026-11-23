from pathlib import Path
import pandas as pd
from etl.json_types import read_json_records

def transform_worldbank_countries(path: Path) -> pd.DataFrame:
    records = read_json_records(path)
    rows = []
    for r in records:
        region = r.get("region", {})
        region_value = region.get("value", "") if isinstance(region, dict) else ""
        
        if region_value == "Aggregates" or not r.get("id"):
            continue
            
        income = r.get("incomeLevel", {})
        income_value = income.get("value", "") if isinstance(income, dict) else ""

        rows.append({
            "iso3": r.get("id", "").strip().upper(),
            "iso2": r.get("iso2Code", "").strip().upper() if r.get("iso2Code") else None,
            "name": r.get("name", "").strip(),
            "region": region_value if region_value else None,
            "income_group": income_value if income_value else None,
        })
    return pd.DataFrame(rows)

def transform_worldbank_file(path: Path, indicator_code: str) -> pd.DataFrame:
    records = read_json_records(path)
    rows = []
    for r in records:
        country = r.get("countryiso3code")
        if not country:
            c_dict = r.get("country", {})
            if isinstance(c_dict, dict):
                country = c_dict.get("id")

        year = r.get("date")
        val = r.get("value")

        if not country or not year:
            continue

        rows.append({
            "country_iso3": str(country).strip().upper(),
            "indicator_code": indicator_code,
            "year": int(year) if str(year).isdigit() else None,
            "sex": "BTSX",
            "value": float(val) if val is not None else None,
        })
        
    if not rows:
        return pd.DataFrame(columns=["country_iso3", "indicator_code", "year", "sex", "value"])
    return pd.DataFrame(rows)
