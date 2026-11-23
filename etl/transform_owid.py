from pathlib import Path
import pandas as pd

def transform_owid_file(path: Path, indicator_code: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    
    # Normalize column names to lowercase to prevent case issues
    df.columns = [c.strip() for c in df.columns]
    
    # Find code column ('code' or 'Code')
    code_col = None
    for c in ["code", "Code", "ISO3", "Entity"]:
        if c in df.columns:
            code_col = c
            break
            
    if not code_col:
        raise ValueError(f"Could not find country code column in {path.name}, columns are: {list(df.columns)}")

    df = df.dropna(subset=[code_col])
    df = df[df[code_col].astype(str).str.len() == 3]

    # Find year column
    year_col = "Year" if "Year" in df.columns else "year"
    
    # Find the value column (which is not code, entity, or year)
    value_cols = [c for c in df.columns if c.lower() not in ("entity", "code", "year", "iso3")]
    if not value_cols:
        raise ValueError(f"No value column found in {path}")
    val_col = value_cols[0]

    return pd.DataFrame({
        "country_iso3": df[code_col].astype(str).str.strip().str.upper(),
        "indicator_code": indicator_code,
        "year": pd.to_numeric(df[year_col], errors="coerce"),
        "sex": "BTSX",
        "value": pd.to_numeric(df[val_col], errors="coerce"),
    })
