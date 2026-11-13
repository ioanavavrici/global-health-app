# Lab 2 - AI Prompts Log

## Prompt 1 – Extractors and Network Handling
- Tool and model: ChatGPT / Assistant
- Date: 2026-11-03
- Prompt: Help me write the raw data extractors for Lab 2 (World Bank, WHO OData API, and OWID CSV) and fix connection timeout errors (502 Gateway / ReadTimeout) when fetching large datasets.
- Result: Created etl/extract_worldbank.py, etl/extract_who.py, and etl/extract_owid.py with robust request sessions, retry limits, and increased timeouts.
- Your changes: Verified that raw responses successfully cache into data/raw/ directories before transformation.

## Prompt 2 – Transform Modules
- Tool and model: ChatGPT / Assistant
- Date: 2026-11-03
- Prompt: Write the raw-to-DB transform modules (transform_worldbank.py, transform_who.py, transform_owid.py) using json_types.py to normalize heterogeneous sources into country_iso3, indicator_code, year, sex, and value.
- Result: Created transformation scripts and verified fallback logic for missing country codes.
- Your changes: Handled edge cases where country codes were nested inside dictionary IDs.

## Prompt 3 – Cleaning Module & IQR Outlier Flag
- Tool and model: ChatGPT / Assistant
- Date: 2026-11-03
- Prompt: Implement etl/clean.py applying data cleaning techniques (valid country filtering, type conversions, whole year enforcement, sex code harmonization, deduplication, year window 2000-2024, and indicator range bounds) and add Task 2.2 IQR outlier detection flagging rows in an is_outlier column.
- Result: Created etl/clean.py, added is_outlier to app/models.py, and updated the PostgreSQL observation table.
- Your changes: Added empty DataFrame safety checks to prevent KeyError during test runs.

## Prompt 4 – Loader and Per-Source Imports
- Tool and model: ChatGPT / Assistant
- Date: 2026-11-03
- Prompt: Build etl/load.py using PostgreSQL upsert (on_conflict_do_update on natural key uq_observation) and write the per-source import scripts (import_worldbank.py, import_who.py, import_owid.py) to load observations and write import logs.
- Result: Created etl/load.py and import scripts, successfully executing data loads into PostgreSQL.
- Your changes: Imported insert from sqlalchemy.dialects.postgresql to resolve dialect-specific upsert compilation errors.
