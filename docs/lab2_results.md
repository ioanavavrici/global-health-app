# Lab 2 - Task Results and Data Quality Checks

## Task 2.2: IQR Outlier Detection Results
In `etl/clean.py` (`clean_observations()`), for each indicator we compute the first quartile ($Q_1$), third quartile ($Q_3$), and interquartile range ($IQR = Q_3 - Q_1$). Observations outside $[Q_1 - 1.5 \times IQR,\; Q_3 + 1.5 \times IQR]$ are flagged with `is_outlier = True` instead of being dropped, and stored in the `observation` table (`app/models.py`).

Query used:

    SELECT i.code,
           COUNT(*) AS total_rows,
           SUM(CASE WHEN o.is_outlier THEN 1 ELSE 0 END) AS outlier_rows
    FROM observation o
    JOIN indicator i USING (indicator_id)
    GROUP BY i.code
    ORDER BY i.code;

| Indicator Code | Total Rows | Flagged Outliers (`is_outlier = true`) | Share (%) |
| :--- | ---: | ---: | ---: |
| `life-expectancy` | 5,160 | 54 | 1.05% |
| `MDG_0000000025` | 2,518 | 415 | 16.48% |
| `NY.GDP.PCAP.CD` | 5,242 | 423 | 8.07% |
| `SH.IMM.MEAS` | 4,805 | 264 | 5.49% |
| `SH.XPD.CHEX.GD.ZS` | 4,562 | 69 | 1.51% |
| `SP.DYN.IMRT.IN` | 4,900 | 131 | 2.67% |
| `WHOSIS_000001` | 13,320 | 66 | 0.50% |

---

## Task 2.3: Idempotent Imports and Deduplication
All three import scripts (`python -m etl.import_worldbank`, `python -m etl.import_who`, `python -m etl.import_owid`) were run twice consecutively. Because `etl/load.py` uses PostgreSQL `INSERT ... ON CONFLICT (country_iso3, indicator_id, year, sex) DO UPDATE`, the second run updates existing rows without creating duplicates.

### Overview query (`Rows per indicator`) after running twice:
| `code` | `name` | `rows` | `first_year` | `last_year` |
| :--- | :--- | ---: | ---: | ---: |
| `life-expectancy` | Life expectancy (OWID series) | 5,160 | 2000 | 2023 |
| `MDG_0000000025` | Births attended by skilled health personnel | 2,518 | 2000 | 2024 |
| `NY.GDP.PCAP.CD` | GDP per capita | 5,242 | 2000 | 2024 |
| `SH.IMM.MEAS` | Measles immunization | 4,805 | 2000 | 2024 |
| `SH.XPD.CHEX.GD.ZS` | Current health expenditure (% of GDP) | 4,562 | 2000 | 2024 |
| `SP.DYN.IMRT.IN` | Infant mortality rate | 4,900 | 2000 | 2024 |
| `WHOSIS_000001` | Life expectancy at birth | 13,320 | 2000 | 2023 |

Row counts remained identical between the first and second run.

### Query 2 (`No duplicates on the natural key`):
Returned **0 rows** (`(0 rows)`), confirming no duplicates on `(country_iso3, indicator_id, year, sex)`.

### Recent entries in `import_log` (showing both consecutive runs):
| `source_name` | `indicator_code` | `rows_loaded` | `imported_at` (GMT) |
| :--- | :--- | ---: | :--- |
| Our World in Data | `life-expectancy` | 5,160 | 2026-11-23 10:14:10 |
| WHO | `MDG_0000000025` | 2,518 | 2026-11-23 10:14:05 |
| WHO | `WHOSIS_000001` | 13,320 | 2026-11-23 10:14:01 |
| World Bank | `NY.GDP.PCAP.CD` | 5,242 | 2026-11-23 10:13:59 |
| World Bank | `SP.DYN.IMRT.IN` | 4,900 | 2026-11-23 10:13:58 |
| World Bank | `SH.IMM.MEAS` | 4,805 | 2026-11-23 10:13:58 |
| World Bank | `SH.XPD.CHEX.GD.ZS` | 4,562 | 2026-11-23 10:13:57 |
| Our World in Data | `life-expectancy` | 5,160 | 2026-11-23 10:13:21 |
| WHO | `MDG_0000000025` | 2,518 | 2026-11-23 10:13:20 |
| WHO | `WHOSIS_000001` | 13,320 | 2026-11-23 10:13:10 |
| World Bank | `NY.GDP.PCAP.CD` | 5,242 | 2026-11-23 10:13:08 |
| World Bank | `SP.DYN.IMRT.IN` | 4,900 | 2026-11-23 10:13:07 |
| World Bank | `SH.IMM.MEAS` | 4,805 | 2026-11-23 10:13:07 |
| World Bank | `SH.XPD.CHEX.GD.ZS` | 4,562 | 2026-11-23 10:12:58 |

---

## Task 2.4: Data Quality Checks and Source Comparison

### 1. Countries (`SELECT COUNT(*) AS countries, COUNT(DISTINCT region) AS regions FROM country;`)
- **Result:** `countries = 217`, `regions = 7`.
- **Explanation:** `transform_worldbank_countries()` drops all records whose region is `"Aggregates"`, leaving only the 217 valid World Bank economies across 7 geographic regions (no `"World"` or regional totals).

### 2. No duplicates on natural key
- **Result:** `0 rows`.
- **Explanation:** Both deduplication in `clean_observations()` (`keep="last"`) and the `uq_observation` unique constraint enforced by `ON CONFLICT DO UPDATE` guarantee zero duplicates on `(country_iso3, indicator_id, year, sex)`.

### 3. Values inside plausible bounds (`MIN`, `MAX`, `AVG`)
| `code` | `unit` | `min` | `max` | `avg` |
| :--- | :--- | ---: | ---: | ---: |
| `life-expectancy` | years | 14.6655 | 86.3724 | 70.78 |
| `MDG_0000000025` | % | 6.0000 | 100.0000 | 91.34 |
| `NY.GDP.PCAP.CD` | current US$ | 109.5938 | 288001.5749 | 16314.53 |
| `SH.IMM.MEAS` | % of children ages 12-23 months | 8.0000 | 99.0000 | 85.81 |
| `SH.XPD.CHEX.GD.ZS` | % of GDP | 1.2226 | 27.0897 | 6.25 |
| `SP.DYN.IMRT.IN` | per 1,000 live births | 1.2000 | 239.9000 | 26.26 |
| `WHOSIS_000001` | years | 24.4000 | 87.1000 | 70.54 |

- **Explanation:** Every indicator falls strictly within its `_INDICATOR_BOUNDS` range (percentages in `[0, 100]`, life expectancy in `(0, 120]`, GDP per capita in `(0, 500000]`, infant mortality in `[0, 500]`).

### 4. Only known sex codes (`SELECT sex, COUNT(*) FROM observation GROUP BY sex;`)
- **Result:** `BTSX`: `31,627`, `FMLE`: `4,440`, `MLE`: `4,440`.
- **Explanation:** World Bank, OWID, and `MDG_0000000025` do not disaggregate by sex and default to `BTSX`, while WHO `WHOSIS_000001` provides `SEX_BTSX`, `SEX_MLE`, and `SEX_FMLE`, mapped cleanly to `BTSX`, `MLE`, and `FMLE`. No unknown sex codes remain.

### 5. No missing values and only years inside the window
- **Result:** `null_values = 0`, `out_of_window = 0`.
- **Explanation:** `clean_observations()` drops any row with missing/non-numeric `year` or `value` and restricts `year` to `[2000, 2024]`.

### 6. Rows stored match rows reported by the last import
| `indicator_code` | `rows_loaded` | `rows_stored` |
| :--- | ---: | ---: |
| `life-expectancy` | 5,160 | 5,160 |
| `MDG_0000000025` | 2,518 | 2,518 |
| `NY.GDP.PCAP.CD` | 5,242 | 5,242 |
| `SH.IMM.MEAS` | 4,805 | 4,805 |
| `SH.STA.MMRT` | 0 | 0 |
| `SH.XPD.CHEX.GD.ZS` | 4,562 | 4,562 |
| `SP.DYN.IMRT.IN` | 4,900 | 4,900 |
| `WHOSIS_000001` | 13,320 | 13,320 |

- **Explanation:** For every indicator, `rows_loaded` in the latest `import_log` entry matches `rows_stored` in `observation` exactly. (`SH.STA.MMRT` has `0 / 0` from an earlier exploratory test entry before standardizing the World Bank indicator list to the 4 core indicators.)

### 7. Countries without any life expectancy value (`WHOSIS_000001` coverage gaps)
- **Result:** **32 countries/territories**:
  `ASM` (American Samoa), `AND` (Andorra), `ABW` (Aruba), `BMU` (Bermuda), `VGB` (British Virgin Islands), `CYM` (Cayman Islands), `CHI` (Channel Islands), `CUW` (Curacao), `DMA` (Dominica), `FRO` (Faroe Islands), `PYF` (French Polynesia), `GIB` (Gibraltar), `GRL` (Greenland), `GUM` (Guam), `HKG` (Hong Kong SAR, China), `IMN` (Isle of Man), `XKX` (Kosovo), `LIE` (Liechtenstein), `MAC` (Macao SAR, China), `MHL` (Marshall Islands), `MCO` (Monaco), `NRU` (Naoero), `NCL` (New Caledonia), `MNP` (Northern Mariana Islands), `PLW` (Palau), `SMR` (San Marino), `SXM` (Sint Maarten), `KNA` (St. Kitts and Nevis), `MAF` (St. Martin), `TCA` (Turks and Caicos Islands), `TUV` (Tuvalu), `VIR` (Virgin Islands (U.S.)).
- **Explanation:** These 32 entities are microstates, autonomous territories, or special administrative regions included in the World Bank economy list (`country` table) for which WHO GHO does not publish `WHOSIS_000001` life-expectancy series.

---

### Source Website Comparison (Romania - `ROU`, Year `2021`, Sex `BTSX`)
| Source | Indicator | Stored in PostgreSQL | Raw Source Value | Source Portal |
| :--- | :--- | ---: | ---: | :--- |
| **World Bank** | `NY.GDP.PCAP.CD` (GDP per capita) | `14908.0413` | `14908.0412813921` | [World Bank Data - ROU](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=RO) |
| **WHO GHO** | `WHOSIS_000001` (Life expectancy at birth) | `72.7000` | `72.7` | [WHO GHO - WHOSIS_000001](https://www.who.int/data/gho/data/indicators/indicator-details/GHO/life-expectancy-at-birth-(years)) |
| **Our World in Data** | `life-expectancy` (Life expectancy) | `72.7405` | `72.7405` | [OWID - Life Expectancy (ROU)](https://ourworldindata.org/grapher/life-expectancy?country=~ROU) |

- **Conclusion:** All three stored values match the official source datasets. PostgreSQL stores `value` as `Numeric(14, 4)` (4 decimal places), which explains why `NY.GDP.PCAP.CD` is rounded to 4 decimals (`14908.0413`) and `WHOSIS_000001` (`72.7000`) vs. OWID (`72.7405`) differ slightly only because WHO publishes its own life-table rounded to 1 decimal while OWID uses UN WPP estimates.
