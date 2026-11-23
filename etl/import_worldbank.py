import logging
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from etl.extract_worldbank import (
    download_worldbank_countries,
    download_worldbank_indicator,
)
from etl.transform_worldbank import (
    transform_worldbank_countries,
    transform_worldbank_file,
)
from etl.clean import clean_observations
from etl.load import (
    get_or_create_source,
    upsert_countries,
    get_or_create_indicator,
    upsert_observations,
    log_import,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("import_worldbank")

SOURCE_NAME = "World Bank"
SOURCE_URL = "https://data.worldbank.org/"

INDICATORS = [
    ("SH.XPD.CHEX.GD.ZS", "Current health expenditure (% of GDP)", "% of GDP"),
    ("SH.IMM.MEAS", "Measles immunization", "% of children ages 12-23 months"),
    ("SP.DYN.IMRT.IN", "Infant mortality rate", "per 1,000 live births"),
    ("NY.GDP.PCAP.CD", "GDP per capita", "current US$"),
]

def main() -> None:
    print("Starting World Bank import...")
    session = SessionLocal()
    failed = []
    try:
        source_id = get_or_create_source(session, SOURCE_NAME, SOURCE_URL)

        # 1. Countries
        c_path = download_worldbank_countries()
        df_c = transform_worldbank_countries(c_path)
        upsert_countries(session, df_c)
        session.commit()
        print(f"Upserted {len(df_c)} countries into database.")

        valid_iso3 = set(df_c["iso3"])

        # 2. Indicators
        for code, name, unit in INDICATORS:
            try:
                path = download_worldbank_indicator(code, year_from=2000, year_to=2024)
                raw_df = transform_worldbank_file(path, code)
                cleaned_df = clean_observations(raw_df, valid_iso3)
                ind_id = get_or_create_indicator(session, code, name, unit, source_id)
                loaded = upsert_observations(session, cleaned_df, ind_id)
                log_import(session, SOURCE_NAME, code, f"https://api.worldbank.org/v2/country/all/indicator/{code}", loaded)
                session.commit()
                print(f"{code:<22} raw={len(raw_df):>6} clean={len(cleaned_df):>6} loaded={loaded:>6}")
            except (ValueError, OSError, SQLAlchemyError) as e:
                session.rollback()
                logger.exception("%s: import failed: %s", code, e)
                failed.append(code)

        if failed:
            print(f"Failed indicators: {failed}")
        else:
            print("World Bank import completed successfully!")
    finally:
        session.close()

if __name__ == "__main__":
    main()
