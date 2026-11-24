from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.domain import CountrySeries, IndicatorInfo, Option, PeriodAverageReport, PeriodInfo


def _to_number(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


class CountryResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    iso3: str
    name: str

    @classmethod
    def from_option(cls, option: Option) -> "CountryResponse":
        return cls(iso3=option.value, name=option.label)


class IndicatorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: str
    name: str

    @classmethod
    def from_option(cls, option: Option) -> "IndicatorResponse":
        return cls(code=option.value, name=option.label)


class IndicatorDetailResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: str
    name: str
    unit: str | None

    @classmethod
    def from_domain(cls, info: IndicatorInfo) -> "IndicatorDetailResponse":
        return cls(code=info.code, name=info.name, unit=info.unit)


class PeriodResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    start: int
    end: int
    label: str

    @classmethod
    def from_domain(cls, p: PeriodInfo) -> "PeriodResponse":
        return cls(start=p.start, end=p.end, label=p.label)


class CountrySeriesResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    country_iso3: str
    country_name: str
    averages: list[float | None]

    @classmethod
    def from_domain(cls, series: CountrySeries) -> "CountrySeriesResponse":
        return cls(
            country_iso3=series.country_iso3,
            country_name=series.country_name,
            averages=[_to_number(a) for a in series.averages],
        )


class PeriodAveragesResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    indicator: IndicatorDetailResponse
    periods: list[PeriodResponse]
    series: list[CountrySeriesResponse]

    @classmethod
    def from_domain(cls, report: PeriodAverageReport) -> "PeriodAveragesResponse":
        return cls(
            indicator=IndicatorDetailResponse.from_domain(report.indicator),
            periods=[PeriodResponse.from_domain(p) for p in report.periods],
            series=[CountrySeriesResponse.from_domain(s) for s in report.series],
        )
