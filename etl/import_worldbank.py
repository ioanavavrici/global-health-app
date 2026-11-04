import logging
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOURCE_NAME = "World Bank"
SOURCE_URL = "https://data.worldbank.org/"

INDICATORS = [
    ("SH.STA.MMRT", "Maternal mortality ratio", "per 100,000 live births"),
    ("SH.STA.BRTC.ZS", "Births attended by skilled health staff", "% of total births"),
    ("SH.XPD.CHEX.GD.ZS", "Current health expenditure", "% of GDP"),
    ("NY.GDP.PCAP.CD", "GDP per capita", "current US$"),
]

def main() -> None:
    logger.info("Starting World Bank import...")
    session = SessionLocal()
    try:
        source_id = get_or_create_source(session, SOURCE_NAME, SOURCE_URL)

        # 1. Countries
        c_path = download_worldbank_countries()
        df_c = transform_worldbank_countries(c_path)
        upsert_countries(session, df_c)
        session.commit()
        logger.info("Upserted %d countries.", len(df_c))

        # Valid ISO3 set
        valid_iso3 = set(df_c["iso3"])

        # 2. Indicators
        for code, name, unit in INDICATORS:
            path = download_worldbank_indicator(code, year_from=2000, year_to=2024)
            raw_df = transform_worldbank_file(path, code)
            cleaned_df = clean_observations(raw_df, valid_iso3)
            ind_id = get_or_create_indicator(session, code, name, unit, source_id)
            loaded = upsert_observations(session, cleaned_df, ind_id)
            log_import(session, SOURCE_NAME, code, f"https://api.worldbank.org/v2/country/all/indicator/{code}", loaded)
            session.commit()
            logger.info("Imported %s: loaded %d rows.", code, loaded)

        logger.info("World Bank import complete successfully.")
    except Exception as e:
        session.rollback()
        logger.exception("World Bank import failed: %s", e)
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
