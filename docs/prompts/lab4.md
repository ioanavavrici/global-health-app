# Lab 4 - AI Prompts Log

## Message 1 - Designing the domain types and Pydantic DTOs
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: I uploaded the Lab 4 document. Start with the domain types in app/domain.py (PeriodAverageQuery, IndicatorInfo, PeriodInfo, CountrySeries, PeriodAverageReport, plus domain errors) and the Pydantic DTOs in app/controllers/api/schemas.py. Should we convert Decimal averages to strings or floats in the DTO?
- Result: Created domain dataclasses/errors and `CountryResponse`, `IndicatorResponse`, `IndicatorDetailResponse`, `PeriodResponse`, `CountrySeriesResponse`, and `PeriodAveragesResponse`.
- Your changes: Made sure `_to_number()` converts `Decimal` to `float | None` (returning JSON numbers instead of strings) so Chart.js plots the series cleanly without parsing strings in the browser.

## Message 2 - PostgreSQL period bucketing in PeriodAverageRepository
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Implement app/repositories/period_average_repository.py so PostgreSQL computes the averages per period directly instead of loading all observations into Python. Why does section 4.6 say we need a subquery for GROUP BY?
- Result: Created `PeriodAverageRepository` using a `bucketed` subquery computing `period_start` and an outer `GROUP BY` query with `func.avg()`.
- Your changes: Verified the SQL query against our real PostgreSQL data for `ROU` and `FRA` and confirmed that `2020-2023` correctly forms a shorter final bucket when `last_year=2023`.

## Message 3 - PeriodAverageService validation and rounding rules
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Write app/services/period_average_service.py with _validate(), _periods(), and _series(). Make sure averages are rounded to 2 decimals half-up and missing periods stay None instead of 0.
- Result: Created `PeriodAverageService` with `ROUND_HALF_UP` quantization and validation for `period_years < 1`, `first_year > last_year`, and `> 20` countries.
- Your changes: Replaced the Unicode en-dash in period labels (`2000?2004`) with a plain ASCII hyphen (`2000-2004`) after noticing encoding issues rendered it as `2000?2004` in the Windows terminal and UI.

## Message 4 - Lookup API endpoints and filtering countries by region
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Add the lookup endpoints in app/controllers/api/reference_data_api.py (/api/regions, /api/countries, /api/indicators) and update dependencies.py. Can we reuse ObservationService from Lab 3?
- Result: Added `list_countries(region)`, `list_indicators()`, and `list_regions()` forwarding methods on `ObservationService` and wired `reference_data_api.router`.
- Your changes: Updated `ObservationRepository.list_countries(region: str | None = None)` so `/api/countries?region=...` filters countries in SQL instead of filtering in Python.

## Message 5 - Period averages endpoint and OpenAPI setup
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Implement app/controllers/api/period_average_api.py with period_average_query() dependency and error mapping to 404/422, then enable /api/openapi.json, /api/docs, and /static in app/main.py.
- Result: Created `period_average_api.py` and updated `app/main.py`, passing `include_in_schema=False` on the Lab 3 HTML routers.
- Your changes: Confirmed in `/api/docs` that only JSON endpoints appear in the OpenAPI schema, while HTML routes stay hidden from Swagger.

## Message 6 - Adding the single indicator endpoint (Task 4.4)
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Add GET /api/indicators/{indicator_code} returning IndicatorDetailResponse (code, name, unit) or 404 if unknown.
- Result: Initially implemented `get_indicator()` calling `service._repository.find_indicator()`.
- Your changes: Rejected accessing private `_repository` from the controller; added a public `find_indicator()` method on `PeriodAverageService` so presentation never reaches past the service layer.

## Message 7 - Sex choice in the API and page
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Add the sex parameter to PeriodAverageQuery and GET /api/indicators/{code}/period-averages so users can switch between BTSX, MLE, and FMLE just like in Lab 3.
- Result: Added `sex: Sex = Sex.BOTH` to `PeriodAverageQuery` and parsed the optional `sex` query parameter using `to_sex_or_none()` (defaulting to `Sex.BOTH`).
- Your changes: Verified that `PeriodAverageRepository.average_by_period()` passes the selected sex code to PostgreSQL so male and female series never mix into the same average.

## Message 8 - Backend unit, repository, and API tests
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Write tests/test_period_average_service.py, test_period_average_repository.py, test_reference_data_api.py, and test_period_average_api.py following section 4.9.
- Result: Created the four test suites checking period bucketing, rounding, PostgreSQL aggregation, JSON numeric types, and 404/422 status mapping.
- Your changes: Fixed a leaking `app.dependency_overrides` bug in `test_period_average_api.py` by wrapping test runs in `try ... finally: app.dependency_overrides.clear()`.

## Message 9 - Page shell controller and template
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Create app/controllers/period_average_page_controller.py serving /period-averages without database access, plus app/templates/period_averages.html and tests/test_period_average_page_controller.py. Also add navigation links in observations.html and period_averages.html.
- Result: Created the page controller, template shell, navigation links (`Observations (SSR)`, `Averages per period (CSR)`, `API Docs`), and shell test.
- Your changes: Checked that adding navigation links to `observations.html` kept all Lab 3 controller tests passing.

## Message 10 - JavaScript data access and model modules
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Implement app/static/js/api-client.js and app/static/js/period-averages-model.js. Make sure fetch() rejects on 404/422 by checking response.ok and encodes query parameters safely with URLSearchParams.
- Result: Created `ApiError`, `getJson()`, `fetchRegions()`, `fetchCountries()`, `fetchIndicators()`, `fetchPeriodAverages()`, `ColorSlots`, `toTable()`, and `toChart()`.
- Your changes: Used `encodeURIComponent()` on `indicatorCode` in the path and configured `ColorSlots` for 8 stable series colors so toggling countries does not repaint existing lines.

## Message 11 - JavaScript view and Chart.js rendering
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Create app/static/js/period-averages-view.js to populate drop-downs, checkboxes (max 8 countries), the table, and the Chart.js line chart. How do we prevent XSS when rendering country names from the API?
- Result: Created `PeriodAveragesView` drawing the table, controls, and Chart.js chart with `spanGaps: false`.
- Your changes: Replaced any HTML template strings in the view with `document.createElement()` and `.textContent` so API strings are never interpreted as HTML, and missing averages render as `?`.

## Message 12 - JavaScript page controller and AbortController
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Write app/static/js/period-averages-page.js using Promise.all() for initial reference data and AbortController to cancel outdated requests when filters change quickly.
- Result: Created `PeriodAveragesPage` connecting filters, model, view, and `api-client.js`.
- Your changes: Tested rapid checkbox clicks in the browser and verified that aborted requests throw `AbortError`, which is caught and ignored cleanly without clearing valid results.

## Message 13 - Debugging 500 Internal Server Error in DevTools Network tab
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: When inspecting F12 Network tab while ticking countries in Europe & Central Asia, some period-averages requests returned 500 Internal Server Error (e.g. when selecting Gibraltar or Greenland). Find and fix the bug.
- Result: Found that `PeriodAverageService.get_report()` tried to execute `select(Country...)` via `self._repository._session` without importing `select` or `Country` whenever a selected country had zero rows for an indicator.
- Your changes: Rejected accessing `_session` inside the service; added a proper `find_country_names()` method in `PeriodAverageRepository`, called it from the service, and added `test_country_without_observations_gets_none_series()` to prevent regression.

## Message 14 - Fixing responsive filter widths in DevTools split view
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: The select boxes squish to two letters when DevTools is open side-by-side, and let's keep the period-averages page focused purely on filters, Chart.js chart, and table as required by Lab 4.
- Result: Updated `.filter-grid` in `base.html` to `repeat(auto-fit, minmax(175px, 1fr))` and streamlined `period_averages.html` and the JS modules.
- Your changes: Re-ran `pytest` (34 passed) and verified in browser DevTools (`F12`) that all `fetch()` calls now return `200 OK` without page reloads.

## Message 15 - Documenting Task 4.1, 4.2, and 4.4 results
- Tool and model: Google AI Studio
- Date: 2026-11-24
- Prompt: Save the screenshots lab4_page.png and lab4_devtools.png in docs/img/, test the REST endpoints locally, and write docs/lab4_results.md covering Tasks 4.1, 4.2, and 4.4.
- Result: Created `docs/lab4_results.md` with verified JSON outputs, DevTools screenshots, SSR vs. CSR comparison, and DTO design explanations.
- Your changes: Checked every endpoint output directly against `TestClient(app)` and confirmed `tests/test_architecture.py` still passes across all new backend layers.
