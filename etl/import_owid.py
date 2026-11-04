import logging
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Country
from etl.extract_owid import download_owid_chart
from etl.transform_owid import transform_owid_file
from etl.clean import clean_observations
from etl.load import (
    get_or_create_source,
    get_or_create_indicator,
    upsert_observations,
    log_import,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOURCE_NAME = "Our World in Data"
SOURCE_URL = "https://ourworldindata.org/"

INDICATORS = [
    ("maternal-mortality-rate", "Maternal mortality ratio (OWID series)", "per 100,000 live births"),
]

def main() -> None:
    logger.info("Starting OWID import...")
    session = SessionLocal()
    try:
        source_id = get_or_create_source(session, SOURCE_NAME, SOURCE_URL)

        # Get valid countries from DB
        valid_iso3 = set(session.execute(select(Country.iso3)).scalars().all())
        if not valid_iso3:
            logger.error("Country table is empty! Run python -m etl.import_worldbank first.")
            return

        for slug, name, unit in INDICATORS:
            path, url = download_owid_chart(slug)
            raw_df = transform_owid_file(path, slug)
            cleaned_df = clean_observations(raw_df, valid_iso3)
            ind_id = get_or_create_indicator(session, slug, name, unit, source_id)
            loaded = upsert_observations(session, cleaned_df, ind_id)
            log_import(session, SOURCE_NAME, slug, url, loaded)
            session.commit()
            logger.info("Imported %s: loaded %d rows.", slug, loaded)

        logger.info("OWID import complete successfully.")
    except Exception as e:
        session.rollback()
        logger.exception("OWID import failed: %s", e)
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
