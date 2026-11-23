from pathlib import Path
import pytest
from app.services.etl_service import EtlService, ExtractJob, ImportJob
from etl.step_result import StepResult, StepStatus


def test_extract_all_collects_ok_and_expected_errors(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text("a,b\n1,2\n", encoding="utf-8")

    def _fail():
        raise ValueError("bad response shape")

    service = EtlService(
        extract_jobs=[
            ExtractJob("OWID", "life-expectancy", lambda: (sample, "https://example.test")),
            ExtractJob("WHO", "WHOSIS_000001", _fail),
        ],
        import_jobs=[],
    )

    results = service.extract_all()

    assert len(results) == 2
    assert results[0].status == StepStatus.OK
    assert "sample.csv" in results[0].detail
    assert results[1].status == StepStatus.FAILED
    assert "ValueError" in results[1].detail


def test_transform_and_load_all_returns_results() -> None:
    expected = [StepResult.ok("World Bank", "NY.GDP.PCAP.CD", "loaded=10")]
    service = EtlService(
        extract_jobs=[],
        import_jobs=[ImportJob("World Bank", lambda: expected)],
    )
    assert service.transform_and_load_all() == expected


def test_unexpected_bug_is_not_hidden() -> None:
    def _bug():
        raise RuntimeError("unexpected bug")

    service = EtlService(
        extract_jobs=[ExtractJob("WHO", "X", _bug)],
        import_jobs=[],
    )
    with pytest.raises(RuntimeError, match="unexpected bug"):
        service.extract_all()
