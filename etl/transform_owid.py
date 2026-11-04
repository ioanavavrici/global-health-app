from pathlib import Path
import pandas as pd

def transform_owid_file(path: Path, indicator_code: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    
    # OWID uses 'Code' for ISO3 country code; drop rows with missing codes (like 'World', 'Africa')
    df = df.dropna(subset=["Code"])
    df = df[df["Code"].str.len() == 3]

    # Find the value column (which is not Entity, Code, or Year)
    value_cols = [c for c in df.columns if c not in ("Entity", "Code", "Year")]
    if not value_cols:
        raise ValueError(f"No value column found in {path}")
    val_col = value_cols[0]

    return pd.DataFrame({
        "country_iso3": df["Code"].astype(str).str.strip().str.upper(),
        "indicator_code": indicator_code,
        "year": pd.to_numeric(df["Year"], errors="coerce"),
        "sex": "BTSX",
        "value": pd.to_numeric(df[val_col], errors="coerce"),
    })
