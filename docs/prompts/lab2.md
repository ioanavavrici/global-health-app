# Lab 2 - AI Prompts Log

## Prompt 1
- Tool and model: Google AI Studio
- Date: 2026-11-13
- Prompt: I uploaded the Lab 2 document. Start with the data extractors: write etl/extract_worldbank.py, etl/extract_who.py, and etl/extract_owid.py to download raw files into data/raw/ and raise WhoApiError or WorldBankApiError on invalid API responses.
- Result: Created `etl/extract_worldbank.py`, `etl/extract_who.py`, and `etl/extract_owid.py` (commit `"Lab 2: raw data extractors (WHO, World Bank, OWID)"`).

## Prompt 2
- Tool and model: Google AI Studio
- Date: 2026-11-13
- Prompt: Modify the WHO and World Bank extractors: WHO @odata.nextLink already includes the $filter so don't resend params on the next pages, and add retries with a User-Agent header in World Bank so requests don't time out.
- Result: Updated pagination and retry logic in `etl/extract_who.py` and `etl/extract_worldbank.py` (commit `"Lab 2: raw data extractors (WHO, World Bank, OWID)"`).

## Prompt 3
- Tool and model: Google AI Studio
- Date: 2026-11-13
- Prompt: Now create etl/json_types.py and the three transform modules (transform_worldbank.py, transform_who.py, transform_owid.py) to return country_iso3, indicator_code, year, sex, and value. Drop Aggregates from World Bank countries and only take Dim1 when Dim1Type is SEX in WHO.
- Result: Created `etl/json_types.py`, `etl/transform_worldbank.py`, `etl/transform_who.py`, and `etl/transform_owid.py` (commit `"Lab 2: raw-to-DB transform modules"`).

## Prompt 4
- Tool and model: Google AI Studio
- Date: 2026-11-13
- Prompt: Write etl/clean.py with clean_observations() and _drop() logging for all the cleaning rules in section 2.3, and add the Sex enum (BTSX, MLE, FMLE) to app/models.py.
- Result: Created `etl/clean.py` and updated `app/models.py` (commit `"Lab 2: observation cleaning module with IQR outlier flag"`).

## Prompt 5
- Tool and model: Google AI Studio
- Date: 2026-11-13
- Prompt: Modify etl/clean.py to also handle empty DataFrames safely, update _INDICATOR_BOUNDS to match our actual indicators (including life-expectancy and MDG_0000000025), and add the Task 2.2 IQR outlier flag is_outlier to clean_observations() and Observation in app/models.py.
- Result: Updated `etl/clean.py` and added `is_outlier` on `Observation` in `app/models.py` (commit `"Lab 2: observation cleaning module with IQR outlier flag"`).

## Prompt 6
- Tool and model: Google AI Studio
- Date: 2026-11-13
- Prompt: Create etl/load.py with PostgreSQL INSERT ... ON CONFLICT DO UPDATE on uq_observation, plus etl/import_worldbank.py, etl/import_who.py, and etl/import_owid.py.
- Result: Created `etl/load.py` and `etl/import_*.py` (commit `"Lab 2: observation loader and per-source import scripts"`).

## Prompt 7
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Change etl/load.py to use sqlalchemy.dialects.postgresql.insert and update is_outlier on conflict. Also NY.GDP.PCAP.CD and SP.DYN.IMRT.IN saved as empty 2-byte files and WHOSIS_000001 is missing from WHO imports ? fix etl/extract_worldbank.py (use per_page=1000 and raise WorldBankApiError instead of saving []) and add WHOSIS_000001 to etl/import_who.py.
- Result: Fixed `etl/load.py`, `etl/extract_worldbank.py`, and `etl/import_who.py`, and re-imported all indicators cleanly (commit `"Lab 2: observation loader and per-source import scripts"`).

## Prompt 8
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Do Task 2.1: create notebooks/exploration.ipynb calling each extractor and transform function, showing df.head(), df.info(), df.isna().sum(), and the percentage of missing values per indicator. Make sure it works even if run from inside notebooks/ and save the outputs.
- Result: Executed and saved `notebooks/exploration.ipynb` with all outputs (commit `"Lab 2: exploration notebook and missing values analysis"`).

## Prompt 9
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: For Task 2.3 and 2.4, run the imports twice, run the 7 data quality SQL queries and the IQR outlier count query on PostgreSQL, and compare Romania 2021 values across all three sources. Replace the placeholder summary in docs/lab2_results.md with the real numbers and tables from the database.
- Result: Created `docs/lab2_results.md` with real PostgreSQL query results, `import_log` rows, outlier counts per indicator, and ROU 2021 comparison (commit `"Lab 2: data quality checks and results"`).

## Prompt 10
- Tool and model: Google AI Studio
- Date: 2026-11-23
- Prompt: Write README.md with setup, extraction, and import instructions from scratch, and split the last commit into smaller logical Lab 2 commits on GitHub without extra files.
- Result: Updated `README.md`, organized the clean `Lab 2:` commits, and pushed to `origin/main` (commit `"Lab 2: prompts log and setup README"`).
