from pathlib import Path
import pandas as pd
from etl.json_types import read_json_records

_SEX_DIMENSION = "SEX"

def transform_who_file(path: Path, indicator_code: str) -> pd.DataFrame:
    records = read_json_records(path)
    if not records:
        return pd.DataFrame(columns=["country_iso3", "indicator_code", "year", "sex", "value"])

    raw = pd.DataFrame(records)

    if "SpatialDimType" in raw.columns:
        raw = raw[raw["SpatialDimType"] == "COUNTRY"]

    sex = "BTSX"
    if "Dim1" in raw.columns and "Dim1Type" in raw.columns:
        dim1_type = raw["Dim1Type"]
        raw = raw[dim1_type.isna() | (dim1_type == _SEX_DIMENSION)]
        raw_sex = raw["Dim1"].where(raw["Dim1Type"] == _SEX_DIMENSION)
        sex = raw_sex.fillna("BTSX")
    elif "Dim1" in raw.columns:
        sex = raw["Dim1"].fillna("BTSX")

    return pd.DataFrame({
        "country_iso3": raw["SpatialDim"].astype(str).str.strip().str.upper(),
        "indicator_code": indicator_code,
        "year": pd.to_numeric(raw["TimeDim"], errors="coerce"),
        "sex": sex,
        "value": pd.to_numeric(raw["NumericValue"], errors="coerce"),
    })
