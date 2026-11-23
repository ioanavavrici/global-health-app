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

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("import_owid")

SOURCE_NAME = "Our World in Data"
SOURCE_URL = "https://ourworldindata.org/"

INDICATORS = [
    ("life-expectancy", "Life expectancy (OWID series)", "years"),
]

def main() -> None:
    print("Starting OWID import...")
    session = SessionLocal()
    try:
        source_id = get_or_create_source(session, SOURCE_NAME, SOURCE_URL)

        valid_iso3 = set(session.execute(select(Country.iso3)).scalars().all())
        if not valid_iso3:
            print("Country table is empty! Run python -m etl.import_worldbank first.")
            return

        for slug, name, unit in INDICATORS:
            path, url = download_owid_chart(slug)
            raw_df = transform_owid_file(path, slug)
            cleaned_df = clean_observations(raw_df, valid_iso3)
            ind_id = get_or_create_indicator(session, slug, name, unit, source_id)
            loaded = upsert_observations(session, cleaned_df, ind_id)
            log_import(session, SOURCE_NAME, slug, url, loaded)
            session.commit()
            print(f"{slug:<22} raw={len(raw_df):>6} clean={len(cleaned_df):>6} loaded={loaded:>6}")

        print("OWID import completed successfully!")
    finally:
        session.close()

if __name__ == "__main__":
    main()
