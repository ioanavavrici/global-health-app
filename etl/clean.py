import logging
from typing import NamedTuple
import pandas as pd
from app.models import Sex

logger = logging.getLogger(__name__)

class _Bounds(NamedTuple):
    low: float
    high: float
    low_inclusive: bool = True
    high_inclusive: bool = True

_INDICATOR_BOUNDS = {
    "SH.XPD.CHEX.GD.ZS": _Bounds(0.0, 100.0),
    "SH.IMM.MEAS": _Bounds(0.0, 100.0),
    "SP.DYN.IMRT.IN": _Bounds(0.0, 500.0),
    "NY.GDP.PCAP.CD": _Bounds(0.0, 500_000.0, low_inclusive=False),
    "WHOSIS_000001": _Bounds(0.0, 120.0, low_inclusive=False),
    "MDG_0000000025": _Bounds(0.0, 100.0),
    "maternal-mortality-rate": _Bounds(0.0, 10_000.0),
}

_SEX_MAP = {"SEX_BTSX": "BTSX", "SEX_MLE": "MLE", "SEX_FMLE": "FMLE"}
_VALID_SEX = {"BTSX", "MLE", "FMLE"}
_KEY_COLUMNS = ["country_iso3", "indicator_code", "year", "sex"]

def _drop(cleaned: pd.DataFrame, mask: pd.Series, reason: str) -> pd.DataFrame:
    dropped = int(mask.sum())
    if dropped:
        logger.info("dropped %d observation rows: %s", dropped, reason)
    return cleaned[~mask]

def _out_of_bounds(df: pd.DataFrame) -> pd.Series:
    out = pd.Series(False, index=df.index)
    for code, b in _INDICATOR_BOUNDS.items():
        subset = df["indicator_code"] == code
        if not subset.any():
            continue
        vals = df.loc[subset, "value"]
        bad = pd.Series(False, index=vals.index)
        if b.low_inclusive:
            bad |= vals < b.low
        else:
            bad |= vals <= b.low
        if b.high_inclusive:
            bad |= vals > b.high
        else:
            bad |= vals >= b.high
        out.loc[subset] = bad
    return out

def clean_observations(df: pd.DataFrame, valid_iso3: set[str]) -> pd.DataFrame:
    cleaned = df.copy()

    # 1. Standardize country codes
    cleaned["country_iso3"] = cleaned["country_iso3"].astype(str).str.strip().str.upper()
    cleaned = _drop(cleaned, ~cleaned["country_iso3"].isin(valid_iso3), "invalid or missing country iso3")

    # 2. Type conversion for year and value
    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce")
    cleaned["value"] = pd.to_numeric(cleaned["value"], errors="coerce")
    cleaned = _drop(cleaned, cleaned["year"].isna() | cleaned["value"].isna(), "missing or non-numeric year/value")

    # 3. Whole years only
    cleaned = _drop(cleaned, cleaned["year"] % 1 != 0, "year is not a whole number")
    cleaned["year"] = cleaned["year"].astype(int)

    # 4. Harmonize sex codes
    cleaned["sex"] = cleaned["sex"].fillna(Sex.BOTH.value).replace(_SEX_MAP)
    cleaned = _drop(cleaned, ~cleaned["sex"].isin(_VALID_SEX), "unknown sex code")

    # 5. Range checks
    cleaned = _drop(cleaned, _out_of_bounds(cleaned), "value outside plausible bounds")

    # 6. Year window (2000 to 2024)
    cleaned = _drop(cleaned, ~cleaned["year"].between(2000, 2024), "year outside study window")

    # 7. Deduplication (keep last)
    cleaned = _drop(cleaned, cleaned.duplicated(subset=_KEY_COLUMNS, keep="last"), "duplicate observations")

    # 8. Task 2.2: IQR Outlier Flag (Flag instead of drop)
    cleaned["is_outlier"] = False
    for code in cleaned["indicator_code"].unique():
        sub_idx = cleaned["indicator_code"] == code
        vals = cleaned.loc[sub_idx, "value"]
        if len(vals) > 5:
            q1 = vals.quantile(0.25)
            q3 = vals.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outlier_mask = (vals < lower) | (vals > upper)
            cleaned.loc[sub_idx & cleaned.index.isin(vals[outlier_mask].index), "is_outlier"] = True

    return cleaned
