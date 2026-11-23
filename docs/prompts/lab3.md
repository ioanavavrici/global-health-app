# Lab 3 - AI Prompts Log

## Message 1 - ETL runner refactoring plan
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: I uploaded the Lab 3 document. Look at section 3.6 and 3.7: the lab requires refactoring our Lab 2 import scripts so that they can be invoked both from CLI and from a web service using a shared loop and StepResult objects. How should we structure etl/step_result.py and etl/import_runner.py-
- Result: Proposed creating `StepStatus`, `StepResult`, and `import_runner.py` with `import_indicators_with_session()` and `import_for_loaded_countries()`.
- Your changes: I verified that the existing indicator codes and filenames in World Bank, WHO, and OWID match our Lab 2 indicators exactly before generating any code.

## Message 2 - Fixing CLI exit behavior in import scripts
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Write etl/step_result.py, etl/import_runner.py, and update etl/import_worldbank.py, etl/import_who.py, and etl/import_owid.py. But don't make them swallow errors when run from terminal - if an indicator fails, report_and_exit_on_failure() should exit with code 1 so bash scripts know it failed.
- Result: Generated the refactored import modules with `report_and_exit_on_failure()`.
- Your changes: In `import_worldbank.py`, the AI initially omitted upserting countries before the indicators; I made sure `download_worldbank_countries()` runs first and populates `valid_iso3` for the remaining indicators.

## Message 3 - Testing refactored ETL runner from terminal
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: When running python -m etl.import_owid, does it print the same formatted line as before-
- Result: Showed how `StepResult` prints `[OK    ] Our World in Data life-expectancy raw=19452, clean=5160, loaded=5160`.
- Your changes: I ran the script locally and confirmed that the row counts in PostgreSQL and `import_log` remain intact.

## Message 4 - Defining domain types in app/domain.py
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Write app/domain.py according to section 3.4. Can these dataclasses have methods or default mutable arguments-
- Result: Created frozen dataclasses `ObservationCriteria`, `ObservationListItem`, `Option`, and `FilterOptions`.
- Your changes: Ensured `frozen=True` is set on every dataclass so the objects remain strictly immutable across layers, and used `Sex` enum from `app.models` instead of plain strings.

## Message 5 - Repository layer and stable ordering
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Create app/repositories/observation_repository.py. Make sure the query joins country and indicator, uses _STABLE_ORDER, and handles all filters dynamically without SQL injection.
- Result: Generated `ObservationRepository` with `find()`, `count()`, and option listing methods.
- Your changes: The AI forgot `Observation.observation_id` at the end of `_STABLE_ORDER`. I added it because section 3.5 explicitly states the tie-breaker must end with the primary key to prevent duplicate or missing rows across paginated requests.

## Message 6 - Service layer architecture rules
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Write app/services/observation_service.py and app/services/etl_service.py. If a page number is 0 or negative, should the service raise HTTPException(status_code=422)-
- Result: AI initially wrote `from fastapi import HTTPException` inside `observation_service.py`.
- Your changes: I rejected the FastAPI import immediately. Section 3.3 and 3.6 forbid HTTP imports in the service layer; the service must raise `ValueError`, and HTTP translation belongs strictly in the controller or FastAPI query validator (`Query(ge=1)`).

## Message 7 - ETL service jobs orchestration
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: In app/services/etl_service.py, how do extract_all() and transform_and_load_all() run without hardcoding external dependencies-
- Result: Created `ExtractJob` and `ImportJob` dataclasses with callables.
- Your changes: Wrapped extract calls in `_run_extract()` with `EXTRACT_ERRORS` tuple so expected network glitches return a failed `StepResult`, while any unexpected bug raises directly so it is not hidden.

## Message 8 - Controller dependencies and form parsing
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Build the presentation layer: app/controllers/form_fields.py, observation_controller.py, etl_controller.py, and app/dependencies.py. How do we prevent invalid numbers like -year_from=abc from throwing a 422 error-
- Result: Created `blank_to_none()` and `to_int_or_none()` helpers in `form_fields.py`.
- Your changes: Applied `blank_to_none()` to `country`, `indicator`, and `region` as well, so submitting empty `<option>` values produces `None` in `ObservationCriteria` instead of empty strings.

## Message 9 - Template inheritance and preventing XSS
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Create app/templates/base.html, observations.html, and action_result.html using Jinja2 and Pico CSS. Why don't we need custom auto-escaping filters for text values-
- Result: Created the templates using `TemplateResponse` and standard block inheritance.
- Your changes: Verified that Jinja2 autoescaping is active by default for `.html` templates, and checked that `<script>` tags in values are safely rendered as `&lt;script&gt;`.

## Message 10 - Writing layered unit tests in tests/
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Write unit tests for each layer: test_observation_service.py with a FakeRepository, test_etl_service.py with stub jobs, and test_observation_controller.py with dependency_overrides.
- Result: Created isolated tests without touching the database or network.
- Your changes: In `conftest.py`, added safety overrides for `get_db` and `get_etl_service` that raise `AssertionError` if a controller test accidentally hits the real DB or triggers ETL downloads.

## Message 11 - Repository tests with real PostgreSQL schemas
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Now add tests/test_observation_repository.py. How can we test against real PostgreSQL without corrupting our Lab 2 data-
- Result: Added `pg_schema` fixture in `conftest.py` creating a unique `test_<random>` schema per session and rolling back every test transaction.
- Your changes: Added `SET search_path TO <schema>` on both schema creation and transaction connections so tables are isolated and cleaned up automatically with `DROP SCHEMA CASCADE`.

## Message 12 - Architecture test with AST (Task 3.4)
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Implement Task 3.4: create tests/test_architecture.py to automatically inspect imports with python ast. Show me how to verify that it actually catches a violation.
- Result: Created `test_architecture.py` checking `FORBIDDEN_PREFIXES = ("fastapi", "app.controllers", "app.dependencies")`.
- Your changes: Temporarily injected `from fastapi import Request` into `app/services/observation_service.py`, verified that `pytest` fails with `AssertionError: Forbidden layer dependencies found: app/services/observation_service.py: imports fastapi`, then removed the line and recorded the failure output in `docs/lab3_results.md`.

## Message 13 - Adding the sex filter across all layers (Task 3.3)
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Task 3.3 asks for a sex filter through all layers: ObservationCriteria, _conditions(), observation_criteria(), drop-down in template, and tests. How should we handle unknown sex codes in the query string-
- Result: Added `sex: Sex | None` to `ObservationCriteria`, condition in repo, and `to_sex_or_none()` helper.
- Your changes: AI initially raised an error on invalid sex parameters. I corrected it to ignore unknown values (`to_sex_or_none()` returns `None`), matching the behavior of the other filters. Added one test per layer (`test_filter_by_sex_returns_only_that_sex`, `test_get_page_passes_sex_and_options_include_sexes`, and controller tests).

## Message 14 - Styling with modern pastel dashboard theme
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: I want a modern light pastel health analytics theme inspired by medical dashboards (lavender-blue gradient, floating white cards, colored sex pills BTSX/MLE/FMLE, status badges for OK/FAILED). Can we do this purely in CSS without JavaScript-
- Result: Replaced default styling in `base.html` with custom CSS custom properties, rounded cards, and pill badges.
- Your changes: Checked that all template element IDs, form input names, and text values required by controller and template tests remained unchanged so all 22 tests pass.

## Message 15 - Sidebar layout adjustment and bottom pagination
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: The filter form was taking too much vertical space and pushing the table down, and year to was wrapping awkwardly. Reorganize observations.html into a 2-column workspace with a compact filter sidebar on the left, and add centered pagination text (Page X of Y, Z rows) between the Previous and Next buttons at the bottom.
- Result: Updated `observations.html` and `base.html` with `.workspace` grid layout and centered bottom pagination.
- Your changes: Verified in browser with `uvicorn app.main:app --reload` at 100% zoom that 10+ observation rows are now visible without scrolling, took the 3 screenshots for Task 3.1, and wrote the call chain and explanations in `docs/lab3_results.md`.
