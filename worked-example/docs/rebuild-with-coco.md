# Rebuild with CoCo

This is the prompt-led design used to build Battery Race: paste one prompt into Cortex Code
(CoCo), review its work, check the result, then continue. It combines the original data-build
sequence with the app-specification and documentation continuation used from B6 onward.
It is adapted for a public reader, not a verbatim transcript. Recorded results and fixes are in
[how-coco-helped.md](how-coco-helped.md); the SQL and commands are in [rebuild.md](rebuild.md).

**Learn from it, but do not submit it or copy its code.** For the event, build your own team's
project. These prompts show how this worked example was developed.

## What you are building

Battery Race asks which South Australian postcodes are leading the home-battery boom since
July 2025, and how battery uptake relates to area disadvantage. The local Streamlit app has a
postcode card explained by Gemma, a map, an animated race, a scatter plot and a glossary.
Gemma receives only the selected postcode's facts through the Gemini API.

The original design targeted 90 minutes of building, with a two-hour stop point. These were
planning targets, not a measured completion-time claim.

## Before the first prompt

- Sign in to your own Snowflake account and confirm CoCo answers a greeting. Stop if access is
  refused. Check your trial balance and use a warehouse you are authorised to run.
- Use CoCo Desktop or a local Cortex CLI session with your project folder open for file loading,
  app building and local tests. Snowsight can help explore data, but cannot read your local CSVs.
- For a full reconstruction, create a separate empty project folder. Copy in `APP-SPEC.md`, `sample.env` and
  the two CER source CSVs under `data/`. Keep postcodes as text. The source CSVs are included in
  this worked example; [data.md](data.md) records their provenance and August 2026 snapshot.
- Follow [the Gemini API key setup guide](gemini-api-key.md) to create your own key in Google AI
  Studio and save it as `GEMINI_API_KEY` in `.env` beside `app.py`. Do not paste
  it into CoCo or a chat. Do not ask an agent to open `.env`, print environment variables or read
  connection files. Sign in and handle credentials yourself.
- Before building, create a `.gitignore` covering `.env`, `data/`, `.venv/`, `__pycache__/`,
  `.DS_Store` and `SESSIONS-LOG.md`. The reconstruction keeps all generated data local. This
  published worked example separately includes only the CER files permitted for redistribution.

Keep a note of elapsed time, each checkpoint, any rephrased prompt, and anything you needed to
know that CoCo did not explain. Review proposed changes before CoCo makes them.

## D0. Keep a local build record

The documentation design added this prompt so later documentation could be drawn from the work:

> Document every step in SESSIONS-LOG.md in this folder as we go: the goal, what you ran
> (queries and commands), the result, and any problem and fix. Use placeholders for account,
> connection and user names. Never copy data rows into it. Never read or print credentials.

**Checkpoint:** the local log grows after each step. Keep it private and out of commits.

## B1. Find the Marketplace data

> Find the free Data Army Intel SEIFA 2021 and Geography boundaries listings for Australia in
> the Snowflake Marketplace. Tell me what tables each has and whether they are free in my region.

**Your step:** open each listing yourself, check pricing and availability, click Get, and review
and accept its terms. The original listings were:

| Listing | ID | Table needed |
|---|---|---|
| ABS Socio-Economic Indexes for Areas (SEIFA 2021) Data - Free | `GZSUZ2MM5HIL` | `SEIFA.SEIFA_POA` |
| Geography - Boundaries & Insights - Australia | `GZSUZCN9CY` | `GEOGRAPHY_AUS_FREE.ABS_POA_2021_AUST_GDA2020` |

**Checkpoint:** both datasets are available in your account and CoCo can describe the tables.
In the original run, SEIFA needed a provider sync to the account region: wait for the notification,
then return and Get it again. Do not assume a listing is currently free or available without checking.

## B2. Understand SEIFA before joining

> Explain SEIFA_POA: what one row is, which index and measure I should use for 'how disadvantaged
> is this area', and how postal areas are written. Show me South Australian rows only.

**Checkpoint:** CoCo recognises long format: one postal area, index and measure per row. For this
app, use IRSD, national decile `RWAD`, state decile `RWSD` and population `URP`. National decile
1 means most disadvantaged, 10 least. Join on the four-character `POA` code. Missing scores stay
missing. Confirm actual table and column names; the original provider example query was inaccurate.

## B3. Load and reshape the CER files

> Load data/sgu-battery-installations-2011-to-present-and-totals.csv and
> data/sgu-solar-installations-2011-to-present-and-totals.csv into new tables. Keep postcodes as
> text. Reshape the months into rows.

**Checkpoint:** raw row counts match the local files; installations are numeric; postcode text
retains leading zeros. Include the separate historic 2001 to 2010 solar total when calculating
all-time solar installations. Check monthly sums against the source totals.

For the included snapshot, the recorded raw counts were 2,473 battery rows and 2,811 solar rows;
the long tables had 34,622 and 528,468 rows. Run SQL statements individually so an earlier failure
is not hidden by the last result. Use your intended account connection explicitly.

## B4. Join and diagnose missing matches

> For South Australian postcodes, join batteries since July 2025 and total solar to the SEIFA
> decile by postal area. Add batteries per 100 solar homes. Tell me how many postcodes did not
> match and why.

**Checkpoint:** retain postcodes with missing SEIFA matches. Calculate the rate as 100 times
batteries divided by solar installations; leave the rate missing if solar is zero. Explain that
solar installations are not unique homes and that CER postcodes and ABS postal areas differ.

The original result had 347 postcodes: 338 MATCHED, 3 NO_DECILE (5111, 5160, 5950), and
6 NO_POSTAL_AREA (5001, 5071, 5175, 5207, 5312, 5875). Investigate differences rather than forcing
new data to match these historical counts.

## B5. Export the local app files

> Save for my app, into the data folder: the joined table as CSV, the monthly SA battery series
> per postcode as CSV, and the SA postal-area boundaries as simplified GeoJSON.

**Checkpoint:** the files are saved under the names and schema expected by `APP-SPEC.md`:

| File | Contents | Original result |
|---|---|---|
| `sa_postcode_battery_seifa.csv` | Postcode, battery and solar totals, rate, national and state deciles, population, match status | 347 rows |
| `sa_battery_monthly.csv` | `postcode`, `month` (`YYYY-MM`), `installations` | 4,564 rows |
| `sa_postal_areas_simplified.geojson` | FeatureCollection with `postcode` and `area_sqkm` properties | 341 features |

The original build simplified boundaries to 100 metres. Check valid shapes and keep the GeoJSON
small enough for the app (the design target was under about 10 MB). Compare totals with the
source CSVs. Keep the Marketplace-derived exports local; do not publish them.

## B6. Build from the app specification

[APP-SPEC.md](../APP-SPEC.md) defines the layout, input files, data rules, Gemma prompt and
acceptance checks. Make sure it is in the project folder, then paste:

> Build the app described in APP-SPEC.md in this folder, using the files in data/. Follow its
> data rules and Gemma section exactly. Then run the acceptance tests in its section 7 yourself,
> fix what fails (at most two rounds), and report each test as pass or fail with what you saw.
> Keep logging every step in SESSIONS-LOG.md. Do not open or print .env; let the app load the key.

**Checkpoint:** the app starts, the map and race render, and each acceptance check has evidence.
Headless tests use a fake Gemma client. Separately check a live answer if your key is configured.
Allow at most one Gemma call per new postcode; repeated selections should use the session cache.

Follow-up fixes in the original build included Gemma latency and API-error handling. The final
code uses `thinking_level="minimal"`, and shows a fallback with a Try again button when a call
fails. See [how-coco-helped.md](how-coco-helped.md#6-building-the-app) for the recorded issues.

## B6b. Check the result independently

The design used Codex for a separate check after CoCo's own tests. You can give another reviewer
this prompt, with the reconstructed project folder selected:

> CoCo has built Battery Race and reported its acceptance tests. Check four independently;
> do not rely on CoCo's report or reuse its code for the reference answers.
>
> 1. A2 Header: compute SA batteries since July 2025, the postcode count and leader from data/.
>    Compare them with the running app.
> 2. A5 Scatter: check that blank deciles are absent, not plotted at zero, and calculate the
>    averages for deciles 1 to 3 and 8 to 10 independently.
> 3. A6 Gemma grounding: select the leader and a postcode near the median. Check every number in
>    each answer against the data, and that it names no suburb and gives no advice.
> 4. A8 No-data postcode: confirm the plain message and that no Gemma call is made for a postcode
>    with no postal area.
>
> Let the app load its key; never open or print .env. Report each check, evidence and any
> disagreement. End with a focused correction prompt I can paste into CoCo if needed.

**Checkpoint:** resolve disagreements or document them as known issues.

## B7. Generate documentation from the build record

> Using SESSIONS-LOG.md in this folder as the record of what we did, write the project
> documentation. Only describe steps that are in the log; where something is unclear, write
> "not recorded".
>
> 1. docs/how-coco-helped.md: for finding listings, explaining data, loading and reshaping CSVs,
>    joining, exporting and building the app, give the prompt, what CoCo did, the key query or
>    command, and data traps it flagged.
> 2. docs/data.md: record each dataset's name, provider, source, licence or terms, tables and
>    columns, join key, match rate and unmatched postcodes with reasons. Clearly mark which files
>    are included and which readers generate themselves. Do not redistribute Marketplace exports.
> 3. docs/rebuild.md: record the executed steps in order, with queries and commands, ending with
>    how to run the app. Also keep the prompt sequence and checkpoints in docs/rebuild-with-coco.md.
> 4. README.md: explain the app and Gemma's role, model and licence, data, how CoCo helped, AI tools
>    used, and how to run it. Link the docs and APP-SPEC.md. For Gemma 4 link its Apache 2.0 licence
>    at https://ai.google.dev/gemma/apache_2 and retain the Gemini API terms link.
>
> Replace account names, locators, connection names, usernames, emails, keys and tokens with
> placeholders. Do not copy data rows or private session material into the published documents.

**Checkpoint:** docs match the work you actually did. Screenshots are optional; inspect any you
choose to share for private information first. Do not publish the raw session log.

## B8. Prepare the repository

> Add an MIT LICENSE and requirements.txt for the app. Ensure .gitignore excludes .env, data/,
> .venv/, __pycache__/, .DS_Store and SESSIONS-LOG.md. Show the files that would be committed.
> Do not commit or publish yet.

**Checkpoint:** inspect the complete file list and scan the proposed public content for private
identifiers and credentials. Review licences separately for code, model and data. The existing
participant repository already has a root licence; do not overwrite it when using that repository.

## B9. Publish only after your review

Publishing was a separate owner decision in the design. Review the app, documents, licences and
file list first. Commit and push only when you choose to publish. If uploading through a browser,
select files individually: browser uploads do not apply `.gitignore` to files you drag in.

Do not publish credentials, Marketplace exports or raw session logs.

## Rehearse the demo

Show the project in about three minutes: the question, header numbers, map, race, one postcode
answer, scatter caption, then how CoCo helped. Check the trial balance again, and record unresolved
issues. Stop if CoCo access is refused or a step needs spending or permissions you have not agreed.
The original build did not need Cortex AI function calls; Gemma runs through the Gemini API.
