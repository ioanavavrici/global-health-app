from app.dependencies import get_etl_service
from app.main import app
from etl.step_result import StepResult


class FakeEtlService:
    def __init__(self, results: list[StepResult]) -> None:
        self._results = results
        self.calls: list[str] = []

    def extract_all(self) -> list[StepResult]:
        self.calls.append("extract")
        return self._results

    def transform_and_load_all(self) -> list[StepResult]:
        self.calls.append("transform_and_load")
        return self._results


def test_post_extract_renders_results(client) -> None:
    fake = FakeEtlService([StepResult.ok("OWID", "life-expectancy", "life-expectancy.csv (100 bytes)")])
    app.dependency_overrides[get_etl_service] = lambda: fake

    resp = client.post("/actions/extract")

    assert resp.status_code == 200
    assert fake.calls == ["extract"]
    assert "Extract complete" in resp.text
    assert "life-expectancy.csv" in resp.text


def test_post_load_renders_results(client) -> None:
    fake = FakeEtlService([StepResult.ok("WHO", "WHOSIS_000001", "loaded=10")])
    app.dependency_overrides[get_etl_service] = lambda: fake

    resp = client.post("/actions/load")

    assert resp.status_code == 200
    assert fake.calls == ["transform_and_load"]
    assert "Transform &amp; Load complete" in resp.text


def test_get_action_returns_405(client) -> None:
    assert client.get("/actions/extract").status_code == 405
    assert client.get("/actions/load").status_code == 405
