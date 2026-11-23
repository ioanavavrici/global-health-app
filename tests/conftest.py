from decimal import Decimal
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import DATABASE_URL, get_db
from app.dependencies import get_etl_service
from app.main import app
from app.models import Base, Country, Indicator, Observation, Sex, Source


@pytest.fixture(scope="session")
def pg_schema():
    engine = create_engine(DATABASE_URL)
    schema = f"test_{uuid.uuid4().hex[:12]}"
    try:
        with engine.connect() as conn:
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            conn.execute(text(f'SET search_path TO "{schema}"'))
            Base.metadata.create_all(bind=conn)
            conn.commit()
    except SQLAlchemyError as exc:
        engine.dispose()
        pytest.skip(f"PostgreSQL not reachable for repository tests: {exc}")

    try:
        yield engine, schema
    finally:
        with engine.connect() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            conn.commit()
        engine.dispose()


@pytest.fixture()
def db_session(pg_schema):
    engine, schema = pg_schema
    conn = engine.connect()
    conn.execute(text(f'SET search_path TO "{schema}"'))
    conn.commit()
    trans = conn.begin()
    session = Session(bind=conn)

    wb = Source(name="World Bank", url="https://data.worldbank.org/")
    who = Source(name="WHO", url="https://www.who.int/data/gho")
    session.add_all([wb, who])
    session.flush()

    fra = Country(iso3="FRA", iso2="FR", name="France", region="Europe & Central Asia")
    rou = Country(iso3="ROU", iso2="RO", name="Romania", region="Europe & Central Asia")
    bra = Country(iso3="BRA", iso2="BR", name="Brazil", region="Latin America & Caribbean")
    deu = Country(iso3="DEU", iso2="DE", name="Germany", region="Europe & Central Asia")
    session.add_all([fra, rou, bra, deu])

    le = Indicator(code="WHOSIS_000001", name="Life expectancy at birth", unit="years", source_id=who.source_id)
    gdp = Indicator(code="NY.GDP.PCAP.CD", name="GDP per capita", unit="current US$", source_id=wb.source_id)
    session.add_all([le, gdp])
    session.flush()

    session.add_all([
        Observation(country_iso3="FRA", indicator_id=le.indicator_id, year=2020, sex=Sex.BOTH.value, value=Decimal("82.1000")),
        Observation(country_iso3="FRA", indicator_id=gdp.indicator_id, year=2015, sex=Sex.BOTH.value, value=Decimal("36652.0000")),
        Observation(country_iso3="ROU", indicator_id=le.indicator_id, year=2021, sex=Sex.BOTH.value, value=Decimal("72.7000")),
        Observation(country_iso3="ROU", indicator_id=le.indicator_id, year=2021, sex=Sex.MALE.value, value=Decimal("69.1000")),
        Observation(country_iso3="ROU", indicator_id=le.indicator_id, year=2021, sex=Sex.FEMALE.value, value=Decimal("76.5000")),
        Observation(country_iso3="ROU", indicator_id=gdp.indicator_id, year=2021, sex=Sex.BOTH.value, value=Decimal("14908.0413")),
        Observation(country_iso3="BRA", indicator_id=le.indicator_id, year=2020, sex=Sex.BOTH.value, value=Decimal("74.0000")),
        Observation(country_iso3="DEU", indicator_id=le.indicator_id, year=2020, sex=Sex.BOTH.value, value=Decimal("81.1000")),
        Observation(country_iso3="DEU", indicator_id=gdp.indicator_id, year=2020, sex=Sex.BOTH.value, value=Decimal("46772.0000")),
    ])
    session.flush()

    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        conn.close()


@pytest.fixture()
def client():
    def _fail_db():
        raise AssertionError("Controller test reached real get_db without override")

    def _fail_etl():
        raise AssertionError("Controller test reached real get_etl_service without override")

    app.dependency_overrides[get_db] = _fail_db
    app.dependency_overrides[get_etl_service] = _fail_etl
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
