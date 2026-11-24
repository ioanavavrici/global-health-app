from fastapi.testclient import TestClient
from app.main import app


def test_reference_data_endpoints() -> None:
    client = TestClient(app)

    # 1. Regions
    r_resp = client.get("/api/regions")
    assert r_resp.status_code == 200
    regions = r_resp.json()
    assert isinstance(regions, list)
    assert "Europe & Central Asia" in regions

    # 2. Countries (all and filtered by region)
    c_resp = client.get("/api/countries")
    assert c_resp.status_code == 200
    all_c = c_resp.json()
    assert len(all_c) > 50

    c_filt = client.get("/api/countries?region=Europe+%26+Central+Asia")
    assert c_filt.status_code == 200
    assert len(c_filt.json()) <= len(all_c)
    assert any(c["iso3"] == "ROU" for c in c_filt.json())

    # 3. Indicators
    i_resp = client.get("/api/indicators")
    assert i_resp.status_code == 200
    assert any(i["code"] == "WHOSIS_000001" for i in i_resp.json())

    # 4. Indicator detail
    det_resp = client.get("/api/indicators/WHOSIS_000001")
    assert det_resp.status_code == 200
    assert det_resp.json()["code"] == "WHOSIS_000001"
    assert det_resp.json()["unit"] == "years"

    det_404 = client.get("/api/indicators/NOT_EXIST")
    assert det_404.status_code == 404
