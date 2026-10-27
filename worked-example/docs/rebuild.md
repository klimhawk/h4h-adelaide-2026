# Rebuild from scratch

**Learn from it, but do not submit it or copy its code.** Your project must be your team's own work, built during the event. Look at how it is set up, how it calls Gemma and how CoCo helped, then build your own.

For the prompt-led design we followed, see [Rebuild with CoCo](rebuild-with-coco.md).
This guide supplies the SQL and commands for those steps. The app requirements, input schema,
Gemma prompt and acceptance checks are defined in [APP-SPEC.md](../APP-SPEC.md).

These instructions document the project's Snowflake Marketplace workflow: get the two listings,
load the CER CSVs, build the join, then export the three files read by the local app.
The CER source CSVs and monthly SA series are included in this repository. The joined CSV and
boundaries are not distributed; generate them in your own account before running the app.
See [data.md](data.md) for the file status, sources and terms.

You need a Snowflake account with access to the two listings, a warehouse and permission to
create the demo database and tables. The account holder reviews and accepts listing terms.
Replace `<connection name>`, `<account region>` and `<project folder>` with your own values,
and select your own warehouse. Run local-file `PUT` and `GET` commands through a Snowflake
client that supports them, as in the original CoCo build. Use an absolute folder path
(starting with `/`) for `<absolute-project-path>` in those commands.

## 1. Get the two Marketplace listings

1. Find your region:

   ```sql
   SELECT CURRENT_REGION();
   ```

2. Optional: install the `cortex` CLI and search the Marketplace by region:

   ```bash
   curl -qLsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh
   cortex search marketplace "Data Army Intel SEIFA 2021" --connection="<connection name>" \
     --marketplace-type=public --filter='{"cloudRegion":["<account region>"]}'
   cortex search marketplace "Data Army Intel geography boundaries Australia" --connection="<connection name>" \
     --marketplace-type=public --filter='{"cloudRegion":["<account region>"]}'
   ```

3. Check that each listing is free and available in your region:

   ```sql
   DESCRIBE AVAILABLE LISTING GZSUZ2MM5HIL;   -- ABS SEIFA 2021 Data - Free
   DESCRIBE AVAILABLE LISTING GZSUZCN9CY;     -- Geography - Boundaries & Insights - Australia
   ```

4. In Snowsight, open each listing, click Get and accept the terms. This is a manual step that the
   account holder does. Keep the default database names: the steps below assume
   `ABS_SOCIOECONOMIC_INDEXES_FOR_AREAS_SEIFA_2021_DATA_FREE` and
   `GEOGRAPHY_BOUNDARIES_INSIGHTS_AUSTRALIA`.

5. Confirm both databases are mounted:

   ```sql
   SHOW DATABASES ->> SELECT "name","kind","origin","created_on" FROM $1 WHERE "kind"='IMPORTED DATABASE';
   ```

## 2. Get the CER files

Put the two Clean Energy Regulator CSV files in `data/`:

- `sgu-battery-installations-2011-to-present-and-totals.csv`
- `sgu-solar-installations-2011-to-present-and-totals.csv`

Download the installation CSVs from the [CER postcode data page](https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data). The included snapshot ends in August 2026; current downloads can differ.

## 3. Database, stage, file format and upload

```sql
CREATE DATABASE IF NOT EXISTS DEMO2_BATTERY_RACE;
CREATE SCHEMA IF NOT EXISTS DEMO2_BATTERY_RACE.SGU;
CREATE STAGE IF NOT EXISTS DEMO2_BATTERY_RACE.SGU.SGU_STAGE;
CREATE OR REPLACE FILE FORMAT DEMO2_BATTERY_RACE.SGU.SGU_CSV
  TYPE = CSV FIELD_DELIMITER = ',' RECORD_DELIMITER = '\n' PARSE_HEADER = TRUE
  FIELD_OPTIONALLY_ENCLOSED_BY = '"' ESCAPE_UNENCLOSED_FIELD = NONE TRIM_SPACE = TRUE
  NULL_IF = ('', 'NULL', 'null', '\\N') EMPTY_FIELD_AS_NULL = TRUE
  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE REPLACE_INVALID_CHARACTERS = TRUE
  MULTI_LINE = FALSE COMPRESSION = NONE ENCODING = 'UTF8';

PUT 'file://<absolute-project-path>/data/sgu-*.csv' @DEMO2_BATTERY_RACE.SGU.SGU_STAGE/raw/
  AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

## 4. Raw tables (all TEXT) and long monthly tables

Run each statement on its own. When several statements run in one call, only the last result is
reported, so an earlier failure can go unnoticed.

```sql
CREATE OR REPLACE TABLE DEMO2_BATTERY_RACE.SGU.BATTERY_RAW USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT('COLUMN_NAME', COLUMN_NAME, 'TYPE', 'TEXT', 'NULLABLE', TRUE))
         WITHIN GROUP (ORDER BY ORDER_ID)
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@DEMO2_BATTERY_RACE.SGU.SGU_STAGE/raw/sgu-battery-installations-2011-to-present-and-totals.csv',
    FILE_FORMAT => 'DEMO2_BATTERY_RACE.SGU.SGU_CSV', IGNORE_CASE => TRUE)));

CREATE OR REPLACE TABLE DEMO2_BATTERY_RACE.SGU.SOLAR_RAW USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT('COLUMN_NAME', COLUMN_NAME, 'TYPE', 'TEXT', 'NULLABLE', TRUE))
         WITHIN GROUP (ORDER BY ORDER_ID)
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@DEMO2_BATTERY_RACE.SGU.SGU_STAGE/raw/sgu-solar-installations-2011-to-present-and-totals.csv',
    FILE_FORMAT => 'DEMO2_BATTERY_RACE.SGU.SGU_CSV', IGNORE_CASE => TRUE)));

COPY INTO DEMO2_BATTERY_RACE.SGU.BATTERY_RAW FROM @DEMO2_BATTERY_RACE.SGU.SGU_STAGE/raw/
  FILES = ('sgu-battery-installations-2011-to-present-and-totals.csv')
  FILE_FORMAT = (FORMAT_NAME = 'DEMO2_BATTERY_RACE.SGU.SGU_CSV')
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE ON_ERROR = ABORT_STATEMENT;

COPY INTO DEMO2_BATTERY_RACE.SGU.SOLAR_RAW FROM @DEMO2_BATTERY_RACE.SGU.SGU_STAGE/raw/
  FILES = ('sgu-solar-installations-2011-to-present-and-totals.csv')
  FILE_FORMAT = (FORMAT_NAME = 'DEMO2_BATTERY_RACE.SGU.SGU_CSV')
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE ON_ERROR = ABORT_STATEMENT;

CREATE OR REPLACE TABLE DEMO2_BATTERY_RACE.SGU.BATTERY_MONTHLY
  (POSTCODE VARCHAR(4), MONTH DATE, INSTALLATIONS NUMBER(10,0))
AS WITH o AS (SELECT "SMALL UNIT POSTCODE" pc, OBJECT_CONSTRUCT(*) obj
              FROM DEMO2_BATTERY_RACE.SGU.BATTERY_RAW)
SELECT o.pc, TO_DATE(SPLIT_PART(f.key, ' - ', 1), 'MON YYYY'),
       REPLACE(f.value::STRING, ',', '')::NUMBER(10,0)
FROM o, LATERAL FLATTEN(INPUT => o.obj) f
WHERE f.key LIKE '% - INSTALLATION QUANTITY' AND f.key NOT LIKE 'TOTAL%';

CREATE OR REPLACE TABLE DEMO2_BATTERY_RACE.SGU.SOLAR_MONTHLY
  (POSTCODE VARCHAR(4), MONTH DATE, INSTALLATIONS NUMBER(10,0))
AS WITH o AS (SELECT "SMALL UNIT INSTALLATION POSTCODE" pc, OBJECT_CONSTRUCT(*) obj
              FROM DEMO2_BATTERY_RACE.SGU.SOLAR_RAW)
SELECT o.pc, TO_DATE(SPLIT_PART(f.key, ' - ', 1), 'MON YYYY'),
       REPLACE(f.value::STRING, ',', '')::NUMBER(10,0)
FROM o, LATERAL FLATTEN(INPUT => o.obj) f
WHERE f.key LIKE '% - INSTALLATION QUANTITY' AND f.key NOT LIKE 'TOTAL%';

CREATE OR REPLACE TABLE DEMO2_BATTERY_RACE.SGU.SOLAR_HISTORIC_2001_2010
  (POSTCODE VARCHAR(4), INSTALLATIONS_2001_2010 NUMBER(10,0))
AS SELECT "SMALL UNIT INSTALLATION POSTCODE",
          REPLACE("HISTORIC TOTAL INSTALLATION QUANTITY (2001 - 2010)", ',', '')::NUMBER(10,0)
FROM DEMO2_BATTERY_RACE.SGU.SOLAR_RAW;
```

The solar statements use the solar postcode column and the same load pattern as the battery statements.

Expected: BATTERY_RAW has 2,473 rows, SOLAR_RAW 2,811, BATTERY_MONTHLY 34,622 and SOLAR_MONTHLY
528,468.

## 5. Join view

```sql
CREATE OR REPLACE VIEW DEMO2_BATTERY_RACE.SGU.SA_POSTCODE_BATTERY_SEIFA AS
WITH bat AS (SELECT postcode, SUM(installations) batteries FROM DEMO2_BATTERY_RACE.SGU.BATTERY_MONTHLY
             WHERE month >= '2025-07-01' AND postcode BETWEEN '5000' AND '5999' GROUP BY 1),
sol AS (SELECT m.postcode, SUM(m.installations) + MAX(h.installations_2001_2010) solar_total
        FROM DEMO2_BATTERY_RACE.SGU.SOLAR_MONTHLY m
        JOIN DEMO2_BATTERY_RACE.SGU.SOLAR_HISTORIC_2001_2010 h USING (postcode)
        WHERE m.postcode BETWEEN '5000' AND '5999' GROUP BY 1),
poa AS (SELECT poa,
          MAX(IFF(seifa_measure='RWAD', obs_value, NULL)) irsd_decile_aus,
          MAX(IFF(seifa_measure='RWSD', obs_value, NULL)) irsd_decile_sa,
          MAX(IFF(seifa_measure='URP',  obs_value, NULL)) population
        FROM ABS_SOCIOECONOMIC_INDEXES_FOR_AREAS_SEIFA_2021_DATA_FREE.SEIFA.SEIFA_POA
        WHERE seifaindextype='IRSD' AND poa BETWEEN '5000' AND '5999' GROUP BY 1)
SELECT COALESCE(bat.postcode, sol.postcode) AS postcode,
       COALESCE(bat.batteries, 0) AS batteries_since_jul2025,
       COALESCE(sol.solar_total, 0) AS solar_total,
       ROUND(100 * COALESCE(bat.batteries, 0) / NULLIF(sol.solar_total, 0), 2) AS batteries_per_100_solar,
       poa.irsd_decile_aus, poa.irsd_decile_sa, poa.population,
       CASE WHEN poa.poa IS NULL THEN 'NO_POSTAL_AREA'
            WHEN poa.irsd_decile_aus IS NULL THEN 'NO_DECILE'
            ELSE 'MATCHED' END AS match_status
FROM bat FULL JOIN sol USING (postcode)
LEFT JOIN poa ON poa.poa = COALESCE(bat.postcode, sol.postcode);
```

Expected: 347 rows, of which 338 are MATCHED, 3 NO_DECILE and 6 NO_POSTAL_AREA.

## 6. Export the app files

```sql
CREATE OR REPLACE FILE FORMAT DEMO2_BATTERY_RACE.SGU.UNLOAD_CSV
  TYPE = CSV COMPRESSION = NONE FIELD_OPTIONALLY_ENCLOSED_BY = '"' NULL_IF = ('') EMPTY_FIELD_AS_NULL = FALSE;
CREATE OR REPLACE FILE FORMAT DEMO2_BATTERY_RACE.SGU.UNLOAD_JSON TYPE = JSON COMPRESSION = NONE;

COPY INTO @DEMO2_BATTERY_RACE.SGU.SGU_STAGE/export/sa_postcode_battery_seifa.csv
FROM (SELECT postcode, batteries_since_jul2025, solar_total, batteries_per_100_solar,
             irsd_decile_aus, irsd_decile_sa, population, match_status
      FROM DEMO2_BATTERY_RACE.SGU.SA_POSTCODE_BATTERY_SEIFA ORDER BY postcode)
FILE_FORMAT = (FORMAT_NAME = 'DEMO2_BATTERY_RACE.SGU.UNLOAD_CSV')
HEADER = TRUE SINGLE = TRUE OVERWRITE = TRUE MAX_FILE_SIZE = 100000000;

COPY INTO @DEMO2_BATTERY_RACE.SGU.SGU_STAGE/export/sa_battery_monthly.csv
FROM (SELECT postcode, TO_CHAR(month, 'YYYY-MM') AS month, installations
      FROM DEMO2_BATTERY_RACE.SGU.BATTERY_MONTHLY
      WHERE postcode BETWEEN '5000' AND '5999' ORDER BY postcode, month)
FILE_FORMAT = (FORMAT_NAME = 'DEMO2_BATTERY_RACE.SGU.UNLOAD_CSV')
HEADER = TRUE SINGLE = TRUE OVERWRITE = TRUE MAX_FILE_SIZE = 100000000;

COPY INTO @DEMO2_BATTERY_RACE.SGU.SGU_STAGE/export/sa_postal_areas_simplified.geojson
FROM (SELECT OBJECT_CONSTRUCT('type', 'FeatureCollection',
         'features', ARRAY_AGG(OBJECT_CONSTRUCT('type', 'Feature',
            'properties', OBJECT_CONSTRUCT('postcode', poa_code_2021, 'area_sqkm', ROUND(area_albers_sqkm, 2)),
            'geometry', ST_ASGEOJSON(ST_SIMPLIFY(geography, 100)))) WITHIN GROUP (ORDER BY poa_code_2021))
      FROM GEOGRAPHY_BOUNDARIES_INSIGHTS_AUSTRALIA.GEOGRAPHY_AUS_FREE.ABS_POA_2021_AUST_GDA2020
      WHERE poa_code_2021 BETWEEN '5000' AND '5999')
FILE_FORMAT = (FORMAT_NAME = 'DEMO2_BATTERY_RACE.SGU.UNLOAD_JSON')
SINGLE = TRUE OVERWRITE = TRUE MAX_FILE_SIZE = 100000000;

GET @DEMO2_BATTERY_RACE.SGU.SGU_STAGE/export/ 'file://<absolute-project-path>/data/';
```

Expected: the joined CSV has 347 rows, the monthly CSV 4,564 rows and the GeoJSON 341 features.

## 7. Python environment and Gemini key

```bash
cd "<project folder>"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # streamlit, pandas, numpy, plotly, google-genai, python-dotenv
```

The original build used these versions: Python 3.14.7, streamlit 1.66.1, plotly 7.1.0 and google-genai
2.33.0.

Follow [Set up the Gemini API key](gemini-api-key.md): create the key in Google AI Studio,
then save `GEMINI_API_KEY` in a private `.env` file beside `app.py`. The guide includes the exact
filename, location, file contents and a check that Git ignores it.

## 8. Test and run the app

Both the app and the headless tests require all three local app data files from step 6.
The test suite checks the original August 2026 snapshot; later source updates can change its
expected counts. A fake Gemma client replaces the API during headless tests.

```bash
.venv/bin/python tests/check_app.py   # uses a fake Gemma client; no key or API call needed
.venv/bin/streamlit run app.py
```

The app opens at http://localhost:8501. Type a South Australian postcode, or click one of the
example buttons.
