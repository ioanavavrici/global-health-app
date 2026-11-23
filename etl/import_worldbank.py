import logging
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from etl.import_runner import (
    IndicatorSpec,
    RAW_ROOT,
    SourceSpec,
    import_indicators_with_session,
    report_and_exit_on_failure,
)
from etl.load import upsert_countries
from etl.step_result import StepResult
from etl.transform_worldbank import (
    transform_worldbank_countries,
    transform_worldbank_file,
)

SOURCE = SourceSpec(
    name="World Bank",
    url="https://data.worldbank.org/",
    raw_dir=RAW_ROOT / "worldbank",
)

INDICATORS = (
    IndicatorSpec(
        code="SH.XPD.CHEX.GD.ZS",
        remote_id="SH.XPD.CHEX.GD.ZS",
        name="Current health expenditure (% of GDP)",
        unit="% of GDP",
        raw_filename="SH.XPD.CHEX.GD.ZS_from2000.json",
    ),
    IndicatorSpec(
        code="SH.IMM.MEAS",
        remote_id="SH.IMM.MEAS",
        name="Measles immunization",
        unit="% of children ages 12-23 months",
        raw_filename="SH.IMM.MEAS_from2000.json",
    ),
    IndicatorSpec(
        code="SP.DYN.IMRT.IN",
        remote_id="SP.DYN.IMRT.IN",
        name="Infant mortality rate",
        unit="per 1,000 live births",
        raw_filename="SP.DYN.IMRT.IN_from2000.json",
    ),
    IndicatorSpec(
        code="NY.GDP.PCAP.CD",
        remote_id="NY.GDP.PCAP.CD",
        name="GDP per capita",
        unit="current US$",
        raw_filename="NY.GDP.PCAP.CD_from2000.json",
    ),
)


def import_all() -> list[StepResult]:
    countries_path = SOURCE.raw_dir / "countries.json"
    if not countries_path.exists():
        return [
            StepResult.from_error(
                SOURCE.name, "countries", FileNotFoundError(f"Missing {countries_path}")
            )
        ]

    session = SessionLocal()
    try:
        try:
            df_countries = transform_worldbank_countries(countries_path)
            count = upsert_countries(session, df_countries)
            session.commit()
            results = [StepResult.ok(SOURCE.name, "countries", f"upserted={count}")]
            valid_iso3 = set(df_countries["iso3"])
        except (ValueError, OSError, SQLAlchemyError) as error:
            session.rollback()
            return [StepResult.from_error(SOURCE.name, "countries", error)]

        results.extend(
            import_indicators_with_session(
                session, SOURCE, INDICATORS, transform_worldbank_file, valid_iso3
            )
        )
        return results
    finally:
        session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    report_and_exit_on_failure(import_all())
