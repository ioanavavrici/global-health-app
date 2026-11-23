# Global Health Data Platform

A data engineering and web platform project that extracts, transforms, cleans, and stores global health and economic indicators from the **World Bank**, **WHO Global Health Observatory (GHO)**, and **Our World in Data (OWID)** in PostgreSQL.

## 1. Prerequisites
- Python 3.11+
- PostgreSQL 15+ running locally (with a database named `global_health`)
- Git

## 2. Project Setup from Scratch

1. **Clone the repository and enter the project folder:**

       git clone <your-repo-url>
       cd global-health-app

2. **Create and activate a virtual environment:**

   On Windows (PowerShell):

       python -m venv .venv
       .\.venv\Scripts\Activate.ps1

   On Linux / macOS:

       python3 -m venv .venv
       source .venv/bin/activate

3. **Install dependencies:**

       pip install -r requirements.txt

4. **Configure environment variables:**

   Create a `.env` file in the project root (never commit `.env`):

       DATABASE_URL=postgresql+psycopg://gh_user:gh_pass@localhost:5432/global_health

5. **Create the database tables:**

       python -m app.create_tables

## 3. Extracting Raw Data

Raw data is cached under `data/raw/worldbank/`, `data/raw/who/`, and `data/raw/owid/`. You can run the extractors directly from Python:

    from etl.extract_worldbank import download_worldbank_countries, download_worldbank_indicator
    from etl.extract_who import download_who_indicator
    from etl.extract_owid import download_owid_chart

    download_worldbank_countries()
    for code in ("SH.XPD.CHEX.GD.ZS", "SH.IMM.MEAS", "SP.DYN.IMRT.IN", "NY.GDP.PCAP.CD"):
        download_worldbank_indicator(code)
    download_who_indicator("WHOSIS_000001")
    download_owid_chart("life-expectancy")

## 4. Running the ETL Imports

Always run **World Bank** first because it populates the `country` table used as the reference list for WHO and OWID cleaning:

    python -m etl.import_worldbank
    python -m etl.import_who
    python -m etl.import_owid

Imports are **idempotent**: running them multiple times updates existing rows via PostgreSQL `ON CONFLICT DO UPDATE` without creating duplicates and logs every run in `import_log`.

## 5. Exploration & Results

- `notebooks/exploration.ipynb`: raw extraction, transformation, and missing-value share inspection.
- `docs/lab2_results.md`: IQR outlier counts, idempotency verification, data quality SQL checks, and source website comparison.
- `docs/prompts/lab2.md`: log of AI prompts and manual edits.
