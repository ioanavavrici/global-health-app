import logging
from etl.import_runner import (
    IndicatorSpec,
    RAW_ROOT,
    SourceSpec,
    import_for_loaded_countries,
    report_and_exit_on_failure,
)
from etl.step_result import StepResult
from etl.transform_owid import transform_owid_file

SOURCE = SourceSpec(
    name="Our World in Data",
    url="https://ourworldindata.org/",
    raw_dir=RAW_ROOT / "owid",
)

INDICATORS = (
    IndicatorSpec(
        code="life-expectancy",
        remote_id="life-expectancy",
        name="Life expectancy (OWID series)",
        unit="years",
        raw_filename="life-expectancy.csv",
    ),
)


def import_all() -> list[StepResult]:
    return import_for_loaded_countries(SOURCE, INDICATORS, transform_owid_file)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    report_and_exit_on_failure(import_all())
