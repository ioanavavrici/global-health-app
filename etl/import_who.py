import logging
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Country
from etl.extract_who import download_who_indicator
from etl.transform_who import transform_who_file
from etl.clean import clean_observations
from etl.load import (
    get_or_create_source,
    get_or_create_indicator,
    upsert_observations,
    log_import,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOURCE_NAME = "WHO"
SOURCE_URL = "https://www.who.int/data/gho"

INDICATORS = [
    ("MDG_0000000025", "Births attended by skilled health personnel", "%"),
]

def main() -> None:
    logger.info("Starting WHO import...")
    session = SessionLocal()
    try:
        source_id = get_or_create_source(session, SOURCE_NAME, SOURCE_URL)

        # Get valid countries from DB loaded by World Bank import
        valid_iso3 = set(session.execute(select(Country.iso3)).scalars().all())
        if not valid_iso3:
            logger.error("Country table is empty! Run python -m etl.import_worldbank first.")
            return

        for code, name, unit in INDICATORS:
            path, url = download_who_indicator(code, year_from=2000)
            raw_df = transform_who_file(path, code)
            cleaned_df = clean_observations(raw_df, valid_iso3)
            ind_id = get_or_create_indicator(session, code, name, unit, source_id)
            loaded = upsert_observations(session, cleaned_df, ind_id)
            log_import(session, SOURCE_NAME, code, url, loaded)
            session.commit()
            logger.info("Imported %s: loaded %d rows.", code, loaded)

        logger.info("WHO import complete successfully.")
    except Exception as e:
        session.rollback()
        logger.exception("WHO import failed: %s", e)
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
