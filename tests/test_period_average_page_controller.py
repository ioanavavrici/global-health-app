from fastapi.testclient import TestClient
from app.main import app


def test_period_average_page_serves_html_shell_and_scripts() -> None:
    client = TestClient(app)
    resp = client.get("/period-averages")
    assert resp.status_code == 200
    assert "period-averages-page.js" in resp.text
    assert "chart.umd.min.js" in resp.text
    assert 'id="averages-chart"' in resp.text
    assert 'id="averages-table"' in resp.text
