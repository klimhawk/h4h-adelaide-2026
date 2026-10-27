# How CoCo helped

This document records CoCo's contribution as evidence for the Snowflake challenge: finding and
understanding freely accessible Marketplace data, preparing it in Snowflake, and building a
project that uses Gemma 4 through the Gemini API.

CoCo here means Cortex Code, Snowflake's AI coding agent, used through the desktop app and the
`cortex` CLI. This account of the build was prepared from a private session log, which is not included.
Prompts recorded verbatim are quoted; other prompts are summaries marked "not recorded".
The build used Data Army Intel's SEIFA 2021 and Geography Marketplace listings, together with
CER installation data. Marketplace exports are not distributed in this repository.

## 1. Finding the Marketplace listings

**Prompt (from the log's goal line; exact wording not recorded):** find the free Data Army Intel
SEIFA 2021 and Geography boundaries listings for Australia in the Snowflake Marketplace, list their
tables, check they are free in the account region, add them, and verify them with SQL.

**What CoCo did:** found the account region and installed the `cortex` CLI. It then searched the
Marketplace, filtered to that region, and read each listing's metadata to confirm both are free
and available there. We clicked Get and accepted the terms; CoCo then checked the tables,
row counts and joins with SQL.

**Key commands and queries:**

```sql
SELECT CURRENT_REGION();
```

```bash
curl -qLsS https://ai.snowflake.com/static/cc-scripts/install.sh | sh
cortex search marketplace "Data Army Intel SEIFA 2021" --connection="<connection name>" \
  --marketplace-type=public --filter='{"cloudRegion":["<account region>"]}'
```

```sql
DESCRIBE AVAILABLE LISTING GZSUZ2MM5HIL;   -- SEIFA
DESCRIBE AVAILABLE LISTING GZSUZCN9CY;     -- Geography
```

**Traps CoCo flagged:**
- The first search timed out because the CLI's default connection pointed to a different
  account. The fix was to pass the connection explicitly.
- The SEIFA listing's quick start query names `SEIFA.SEIFA_SAl` and a column
  `statistical_area_sal_2021`, so it should not be copied as is.
- The listing description mentions SEIFA_SA3, but there is no SEIFA_SA3 table; there is a
  SEIFA_SAL table instead.
- SEIFA tables are in long format (`INDEX_TYPE`, `MEASURE`, `OBS_VALUE`), and the code column is
  the one named after the table.

## 2. Explaining the data (SEIFA_POA)

**Prompt (summary of the recorded content; exact wording not recorded):** "Explain
SEIFA_POA: what one row is, which index and measure I should use for 'how disadvantaged is this
area', and how postal areas are written. Show me South Australian rows only."

**What CoCo explained:** one row is one postal area x one index x one measure. For "how
disadvantaged" the right index is IRSD and the measure is `RWAD`, the national decile, where 1 is
the most disadvantaged. Postal areas are 4-character text postcodes with no "POA" prefix.

**Key query:**

```sql
SELECT poa AS postcode,
  MAX(IFF(seifa_measure='URP',   obs_value, NULL)) AS population,
  MAX(IFF(seifa_measure='SCORE', obs_value, NULL)) AS irsd_score,
  MAX(IFF(seifa_measure='RWAD',  obs_value, NULL)) AS aus_decile,
  MAX(IFF(seifa_measure='RWSD',  obs_value, NULL)) AS sa_decile
FROM ABS_SOCIOECONOMIC_INDEXES_FOR_AREAS_SEIFA_2021_DATA_FREE.SEIFA.SEIFA_POA
WHERE seifaindextype = 'IRSD' AND poa BETWEEN '5000' AND '5999'
GROUP BY poa ORDER BY irsd_score NULLS LAST;
```

**Traps CoCo flagged:**
- `POA` and `POSTAL_AREA_CODE` differ for two national catch-all codes (9494 and 9797), so join on
  `POA`.
- Three SA postal areas have no score (5111, 5160, 5950); all have tiny populations.
- Small populations distort the rankings: the most disadvantaged postcodes include some with
  very few residents. CoCo suggested a population floor such as URP >= 1000.

## 3. Loading and reshaping the CSVs

**Prompt (verbatim from the session):** "Load data/sgu-battery-installations-2011-to-present-and-totals.csv
and data/sgu-solar-installations-2011-to-present-and-totals.csv into new tables. Keep postcodes as
text. Reshape the months into rows."

**What CoCo did:** profiled both files locally first. It then proposed a load plan, which we
approved, and loaded every column as TEXT. Finally it unpivoted the month columns into one row per
postcode and month and checked the totals against the CSV's Total column.

**Key queries:**

```sql
CREATE OR REPLACE TABLE DEMO2_BATTERY_RACE.SGU.BATTERY_RAW USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT('COLUMN_NAME', COLUMN_NAME, 'TYPE', 'TEXT', 'NULLABLE', TRUE))
         WITHIN GROUP (ORDER BY ORDER_ID)
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@DEMO2_BATTERY_RACE.SGU.SGU_STAGE/raw/sgu-battery-installations-2011-to-present-and-totals.csv',
    FILE_FORMAT => 'DEMO2_BATTERY_RACE.SGU.SGU_CSV', IGNORE_CASE => TRUE)));

CREATE OR REPLACE TABLE DEMO2_BATTERY_RACE.SGU.BATTERY_MONTHLY
  (POSTCODE VARCHAR(4), MONTH DATE, INSTALLATIONS NUMBER(10,0))
AS WITH o AS (SELECT "SMALL UNIT POSTCODE" pc, OBJECT_CONSTRUCT(*) obj
              FROM DEMO2_BATTERY_RACE.SGU.BATTERY_RAW)
SELECT o.pc, TO_DATE(SPLIT_PART(f.key, ' - ', 1), 'MON YYYY'),
       REPLACE(f.value::STRING, ',', '')::NUMBER(10,0)
FROM o, LATERAL FLATTEN(INPUT => o.obj) f
WHERE f.key LIKE '% - INSTALLATION QUANTITY' AND f.key NOT LIKE 'TOTAL%';
```

**Traps CoCo flagged:**
- Some postcodes have leading zeros (30 in the battery file, 48 in the solar file), so postcodes
  stay as text.
- The solar file has quoted thousands such as "1,006".
- Despite its file name, the battery file covers only July 2025 to August 2026.
- The solar file has a separate historic total for 2001 to 2010.
- `FLATTEN(OBJECT_CONSTRUCT(r.*))` is not allowed, so the row object is built in a CTE first.
- When several statements run in one call, only the last result is reported, which hid a
  failure. Statements are now run one at a time.

## 4. The join

**Prompt (verbatim from the session):** "For South Australian postcodes, join batteries since July
2025 and total solar to the SEIFA decile by postal area. Add batteries per 100 solar homes. Tell me
how many postcodes did not match and why."

**What CoCo did:** ran match diagnostics in both directions, also checking against the ABS postal
area boundaries. It then built the view `SA_POSTCODE_BATTERY_SEIFA` with a match status column and
summarised the rate by decile. Decile 10 reached 17.2 batteries per 100 solar installations and
decile 1 reached 9.5.

**Key query:** the view is shown in full in [rebuild.md](rebuild.md#5-join-view). Its core is:

```sql
CASE WHEN poa.poa IS NULL THEN 'NO_POSTAL_AREA'
     WHEN poa.irsd_decile_aus IS NULL THEN 'NO_DECILE'
     ELSE 'MATCHED' END AS match_status
```

**Traps CoCo flagged:**
- 9 of 347 SA postcodes are unmatched: 6 are not ABS postal areas and 3 have no decile.
- 14 matched postcodes are absent from the battery file, so they count as 0 batteries.
- Solar figures are installation counts, so replacements are counted again, and some batteries go
  to homes without solar.
- The log assumes a postcode and its postal area are the same thing; this was not checked.

## 5. The export

**Prompt (verbatim from the session):** "Save for my app, into the data folder: the joined table as
CSV, the monthly SA battery series per postcode as CSV, and the SA postal-area boundaries as
simplified GeoJSON."

**What CoCo did:** compared simplification tolerances and chose 100 m: it cut the boundary points
from 238,545 to 32,344 with no invalid shapes. It then unloaded the three files to a stage,
downloaded them with GET, and checked them locally.

**Key query:**

```sql
COPY INTO @DEMO2_BATTERY_RACE.SGU.SGU_STAGE/export/sa_postal_areas_simplified.geojson
FROM (SELECT OBJECT_CONSTRUCT('type', 'FeatureCollection',
         'features', ARRAY_AGG(OBJECT_CONSTRUCT('type', 'Feature',
            'properties', OBJECT_CONSTRUCT('postcode', poa_code_2021, 'area_sqkm', ROUND(area_albers_sqkm, 2)),
            'geometry', ST_ASGEOJSON(ST_SIMPLIFY(geography, 100)))) WITHIN GROUP (ORDER BY poa_code_2021))
      FROM GEOGRAPHY_BOUNDARIES_INSIGHTS_AUSTRALIA.GEOGRAPHY_AUS_FREE.ABS_POA_2021_AUST_GDA2020
      WHERE poa_code_2021 BETWEEN '5000' AND '5999')
FILE_FORMAT = (FORMAT_NAME = 'DEMO2_BATTERY_RACE.SGU.UNLOAD_JSON')
SINGLE = TRUE OVERWRITE = TRUE MAX_FILE_SIZE = 100000000;
```

**Traps CoCo flagged:**
- `OBJECT_CONSTRUCT(*)` does not accept GEOMETRY columns, and `ST_ISEMPTY` does not exist.
- 21 SA postcodes have no rows in the monthly battery file and must be treated as 0 in charts.
- Empty strings in the joined CSV mean NULL.

## 6. Building the app

**Prompt (verbatim from the log):** "Build the app described in APP-SPEC.md in this folder, using
the files in data/. Follow its data rules and Gemma section exactly."

**What CoCo did:**
- Copied the spec to `APP-SPEC.md` and computed reference answers from `data/`.
- Wrote `app.py`, which uses Streamlit and Plotly, with a Gemma 4 call through `google-genai`.
- Wrote the headless test harness `tests/check_app.py`, which uses a fake Gemma client, and fixed
  the issues listed in the log.
- In the follow-ups:
  - Found that Gemma's hidden thinking caused 22 to 69 s answers and cut that to about 3 s.
  - Replaced "SEIFA decile" with plain wording, added a glossary and the footer sentence.
  - Handled Gemini API errors with a "Try again" button.

**Key code:**

```python
resp = client.models.generate_content(
    model="gemma-4-26b-a4b-it", contents=prompt,
    config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level="minimal")))
```

```bash
.venv/bin/python tests/check_app.py   # 15 of 15 pass at the last recorded run
```

**Traps CoCo flagged:**
- The coding agent needed the specification saved as `APP-SPEC.md` before building.
- Pandas raised an error because `postcode` was both the index and a column.
- `thinking_budget` and `thinking_level="low"` are rejected for this model; only `"minimal"`
  works.
- Browser automation did not reliably trigger Streamlit reruns.
- An occasional Gemini `500 INTERNAL` error comes from Google's side, so the app shows the
  fallback message and a "Try again" button.

**Credential practice:** create and store your own API key privately. Never print it, paste it
into a chat, or commit it. A presence check should report only whether a key is set.
