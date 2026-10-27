# Rebuild with CoCo

Use this guide to explore how Battery Race was built with Cortex Code (CoCo). Paste one prompt
at a time, check the result, then continue. You can adapt the same sequence to your own project:
find data, understand it, prepare it, build an app and check its answers.

**Learn from it, but do not submit it or copy its code.** Your event project must be your team's
own work. Battery Race is a worked example to learn from.

For the SQL and commands behind these steps, see [Rebuild from scratch](rebuild.md).
[How CoCo helped](how-coco-helped.md) describes CoCo's contribution to this example.

## What you are building

Battery Race compares home-battery uptake across South Australian postcodes. It combines CER
installation counts with SEIFA disadvantage deciles and postal-area boundaries from Snowflake
Marketplace. A local Streamlit app displays a map, an animated race, a scatter plot and a
postcode card. Gemma 4 explains the selected postcode's figures through the Gemini API.

## Before the first prompt

1. Sign in to Snowflake and confirm CoCo answers a greeting. Check your available credit and
   select a warehouse. If CoCo is unavailable, resolve access before starting.
2. Use CoCo Desktop or a local Cortex CLI session with your project folder open for local file
   loading, app building and tests. Snowsight can help explore data, but cannot read your local CSVs.
3. To reconstruct this example, create a separate project folder. Copy
   [APP-SPEC.md](../APP-SPEC.md) and `sample.env` into its root, and the two CER source CSVs from
   `worked-example/data/` into its `data/` folder. See [data.md](data.md) for sources and licences.
4. Follow [the Gemini API key setup guide](gemini-api-key.md). Copy `sample.env` to `.env` in
   your project folder and replace the placeholder yourself. Never paste the key into CoCo.
5. Create a `.gitignore` excluding `.env`, each Marketplace export by name, `.venv/`, `__pycache__/`, `.DS_Store` and any
   raw build notes. Keep generated Marketplace exports local.

You can ask CoCo to keep local notes of your prompts, queries, results and fixes to help write
accurate documentation later. Keep credentials and data rows out of those notes.

## B1. Find the Marketplace data

> Find the free Data Army Intel SEIFA 2021 and Geography boundaries listings for Australia in
> the Snowflake Marketplace. Tell me what tables each has and whether they are free in my region.

Open the listings in Snowsight. Check pricing and availability in your region, select Get,
and review and accept the terms yourself.

| Listing | ID | Table needed |
|---|---|---|
| ABS Socio-Economic Indexes for Areas (SEIFA 2021) Data - Free | `GZSUZ2MM5HIL` | `SEIFA.SEIFA_POA` |
| Geography - Boundaries & Insights - Australia | `GZSUZCN9CY` | `GEOGRAPHY_AUS_FREE.ABS_POA_2021_AUST_GDA2020` |

**Check:** both datasets are available in your account and CoCo can describe the tables.
If a listing needs a provider sync to your region, wait for the notification, then return to
complete Get. Confirm the current offer rather than assuming it is free.

## B2. Understand SEIFA before joining

> Explain SEIFA_POA: what one row is, which index and measure I should use for 'how disadvantaged
> is this area', and how postal areas are written. Show me South Australian rows only.

**Check:** the table is in long format: one postal area, index and measure per row. For Battery
Race, use IRSD, national decile `RWAD`, state decile `RWSD` and population `URP`. National decile
1 means most disadvantaged, 10 least. Join on the four-character `POA` code and retain missing
scores. Ask CoCo to inspect actual columns before using a provider's example query.

## B3. Load and reshape the CER files

> Load data/sgu-battery-installations-2011-to-present-and-totals.csv and
> data/sgu-solar-installations-2011-to-present-and-totals.csv into new tables. Keep postcodes as
> text. Reshape the months into rows.

**Check:** raw row counts match the files, installations are numeric and postcode text retains
leading zeros. Include the separate historic 2001 to 2010 solar total in all-time solar counts.
Compare monthly sums with the source totals.

With the supplied August 2026 snapshot, expect 2,473 raw battery rows and 2,811 raw solar rows;
the long tables have 34,622 and 528,468 rows. Run SQL statements individually so a later result
does not hide an earlier failure. Confirm CoCo is using your intended account connection.

## B4. Join and diagnose missing matches

> For South Australian postcodes, join batteries since July 2025 and total solar to the SEIFA
> decile by postal area. Add batteries per 100 solar homes. Tell me how many postcodes did not
> match and why.

**Check:** keep postcodes without a SEIFA match. The rate is 100 times batteries divided by
solar installations; leave it missing where solar is zero. Solar installations are not unique
homes, and CER postcodes and ABS postal areas are different geographies.

The supplied snapshot produces 347 postcodes: 338 MATCHED, 3 NO_DECILE (5111, 5160, 5950), and
6 NO_POSTAL_AREA (5001, 5071, 5175, 5207, 5312, 5875). If you use newer data, investigate changes
rather than forcing it to match these counts.

## B5. Export the local app files

> Save for my app, into the data folder: the joined table as CSV, the monthly SA battery series
> per postcode as CSV, and the SA postal-area boundaries as simplified GeoJSON.

**Check:** the files have the exact names and fields expected by
[APP-SPEC.md](../APP-SPEC.md) and the [export SQL](rebuild.md#6-export-the-app-files):

| File | Contents | Supplied snapshot |
|---|---|---|
| `sa_postcode_battery_seifa.csv` | Postcode, battery and solar totals, rate, national and state deciles, population, match status | 347 rows |
| `sa_battery_monthly.csv` | `postcode`, `month` (`YYYY-MM`), `installations` | 4,564 rows |
| `sa_postal_areas_simplified.geojson` | FeatureCollection with `postcode` and `area_sqkm` properties | 341 features |

Ask CoCo to simplify boundaries to 100 metres, check that shapes remain valid and keep the
GeoJSON under about 10 MB. Compare exported totals with the source CSVs. Keep the
Marketplace-derived exports out of your public repository.

## B6. Build from the app specification

[APP-SPEC.md](../APP-SPEC.md) defines the layout, input files, data rules, Gemma prompt and
acceptance checks. Make sure it is in your project folder, then paste:

> Build the app described in APP-SPEC.md in this folder, using the files in data/. Follow its
> data rules and Gemma section exactly. Run the acceptance tests in section 7, fix failures and
> report each test as pass or fail with what you observed. Do not open or print .env; let the
> app load the key.

**Check:** the app starts, the map and race render, and the checks have evidence. Headless tests
use a fake Gemma client; also try a real answer in the app. Select the same postcode again to
confirm it uses the cached answer rather than making another API call.

For this Gemma integration, the final example uses `thinking_level="minimal"` to reduce latency,
and shows a fallback with a Try again button if a request fails. See the
[recorded implementation fixes](how-coco-helped.md#6-building-the-app) if you encounter similar issues.

## B6b. Check the result independently

Ask a teammate to check the app against the data, rather than relying only on CoCo's report.
They can calculate the figures themselves or use a separate coding assistant with this prompt:

> Check Battery Race independently. Calculate reference answers from data/ without reusing
> the app's calculation code.
>
> 1. Header: check SA batteries since July 2025, the postcode count and the leading postcode.
> 2. Scatter: confirm missing deciles are absent, not plotted at zero. Recalculate the averages
>    for deciles 1 to 3 and 8 to 10 and compare them with the caption.
> 3. Gemma: select the leader and a postcode near the median. Check every number in the answers
>    against the data. Confirm the answers name no suburb and give no advice.
> 4. Missing data: select a postcode without a postal area. Confirm the app shows an explanation
>    and makes no Gemma call.
>
> Never open or print .env. Report the evidence for each check and any corrections needed.

**Check:** fix disagreements and document any remaining limitations.

## B7. Write the project documentation

> Using the work completed in this session and any local build notes, write the project
> documentation. Describe only what we actually did; mark anything unverified clearly.
>
> 1. docs/how-coco-helped.md: explain where CoCo helped find, understand and prepare data or
>    build the app. Include useful prompts, queries, results and fixes as evidence.
> 2. docs/data.md: list sources, providers, licences or terms, tables, columns, join keys,
>    match rates and missing matches. Mark which files are included and how to obtain the rest.
> 3. docs/rebuild.md: explain how to reproduce the project, with queries, commands and run steps.
> 4. README.md: explain the problem, app, Gemma integration, model and licence, data, CoCo's
>    contribution, AI tools, tech stack and how to run it. Link the supporting documents and spec.
>
> Use placeholders for account and connection names. Never include credentials, private
> identifiers, raw session logs or Marketplace data rows in public documentation.

**Check:** someone unfamiliar with your project can understand what it does, where its data
comes from, how AI contributes and how to run it. Keep the explanation of CoCo's contribution
separate from the rebuild instructions.

## B8. Package your own project

> Add requirements.txt for the app and an appropriate open-source licence. Ensure .gitignore
> excludes .env, Marketplace exports, .venv/, __pycache__/, .DS_Store and raw build notes. Show the
> files to include in the repository.

Check that the dependency list is complete, your chosen licence covers your code, and data
licences and model terms are documented separately. This example uses the repository's root
MIT licence and links Gemma 4's Apache 2.0 licence in its README.

Before uploading, inspect the files for keys, private identifiers and data you cannot
redistribute. If you upload through a browser, select files carefully: dragging a folder into
GitHub does not apply your local `.gitignore` rules.
