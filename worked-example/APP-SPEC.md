# Battery Race: app specification

**Learn from it, but do not submit it or copy its code.** Your project must be your team's own work, built during the event. Look at how it is set up, how it calls Gemma and how CoCo helped, then build your own.

**Status:** v1, 2026-10-24. App specification for the Battery Race worked example.

## 1. Purpose

A one-page local web app that answers: **which South Australian postcodes are winning the home-battery
boom since July 2025, and is it the well-off ones?** Visitors type their postcode and get a plain-English
answer from Gemma 4. It must work as a three-minute live demo on a projector.

Judges look for Gemma "through the Gemini API" shown working, so the Gemma moment is visible and
labelled.

## 2. Inputs

The three app files in `data/` (see [docs/data.md](docs/data.md)):

1. **Joined table** (CSV), one row per SA postcode: postcode, batteries since July 2025, total solar
   installations, batteries per 100 solar homes, SEIFA decile (IRSD), population, and
   the match flags (`NO_DECILE`, `NO_POSTAL_AREA`).
2. **Monthly series** (CSV): postcode, month, batteries installed that month, from July 2025.
3. **Postal-area shapes** (GeoJSON), SA only, simplified, postcode as a text property.

Plus `.env` with `GEMINI_API_KEY`. Nothing is fetched from Snowflake while the app runs.

## 3. Data rules

- Postcodes are text everywhere (CSVs and GeoJSON); never convert to numbers.
- A South Australian postcode missing from the monthly file has 0 batteries in every month.
- In the joined table a blank decile means no SEIFA value, and a blank population means no postal
  area. Show "no data"; never treat either as zero, never colour it as a value, and leave it out of
  the scatter and its caption.
- "Batteries per 100 solar homes" = batteries since July 2025 / total solar installations x 100;
  "no data" where solar is 0.
- Rank = position among SA postcodes by batteries since July 2025 (1 = most).

## 4. Layout (single page, top to bottom)

**1. Header.** Title "Battery Race: who is winning South Australia's home-battery boom?". Subtitle "Home
batteries installed since July 2025, by postcode". Three big numbers: SA batteries since July 2025;
postcodes in the race; the leading postcode with its count.

**2. Your postcode** (narrow left column) beside **3. Map** (wide right column).

- *Your postcode:* a text box "Type your postcode" and three example buttons: the leader, a postcode near
  the SA median, and one with no data. On submit, a card: batteries since July 2025, batteries per 100
  solar homes, rank in SA ("12th of 340"), SEIFA decile. Under the card, Gemma's answer in a box labelled
  **"Explained by Gemma 4"**.
- *Map:* SA postal areas coloured by batteries per 100 solar homes; one colour-blind-safe sequential
  scale with a legend; grey for no data. Hover shows postcode, batteries, rate, decile. Opens on Greater
  Adelaide (about -34.93, 138.60) with the rest of SA reachable by zoom. The typed postcode is outlined.
  No map token needed (an open basemap).

**4. The race** (full width). Animated horizontal bar chart: top 15 postcodes by **cumulative** batteries,
one frame per month from July 2025 to the latest month, re-ranked each frame. Play, pause and a month
slider. Bars labelled with postcode and count; the frame shows the month.

**5. Is it the well-off?** (full width). Scatter: SEIFA decile (x, 1 to 10) against batteries per 100
solar homes (y), one dot per postcode with data, hover shows the postcode. A straight trend line
computed in the app (no extra packages). Caption computed from the data, plain and non-causal, for
example "Postcodes in deciles 8 to 10 average X batteries per 100 solar homes, against Y in deciles 1 to 3."

**6. Footer.** "Data: Clean Energy Regulator small-scale installations (CC BY 4.0); ABS SEIFA 2021 and ABS
postal-area boundaries via Data Army Intel on Snowflake Marketplace. Snowflake Marketplace rows are not
redistributed. AI: Gemma 4 through the Gemini API."

## 5. Gemma

- Model `gemma-4-26b-a4b-it` through the Gemini API; key from `.env`; never printed or logged.
- One call per new postcode; cache answers for the session, so repeats make no call.
- No call for a postcode that is not in the data or not four digits; show a plain message instead.
- Prompt template (fill the braces from the joined table):

  > You explain home-battery data for one South Australian postcode to a local resident. Use only these
  > facts: postcode {postcode}; batteries installed since July 2025: {batteries}; rank {rank} of {n} SA
  > postcodes; batteries per 100 solar homes: {rate} (SA median {median}); disadvantage decile {decile}
  > (1 = most disadvantaged, 10 = least; "no data" if missing). Write two or three plain sentences. Do not
  > name suburbs, give advice, or add any fact not listed.

- If the API fails or is rate-limited: keep the card, and show "Gemma is not available right now, try
  again in a minute" in the Gemma box.

## 6. Style and behaviour

- Large fonts that read on a projector; two colours plus grey; works at 1280x720 with nothing cut off.
- Data loads cached; the page responds in under two seconds after the first load.
- Input accepts spaces around the postcode; anything that is not four digits gets "Please enter a
  4-digit postcode".
- Packages: streamlit, pandas, numpy, plotly, google-genai, python-dotenv (in `requirements.txt`).

## 7. Acceptance tests (checked after the build)

| # | Test | Pass when |
| --- | --- | --- |
| A1 | Start | The app starts locally with no error and no key in the code |
| A2 | Header | The three numbers match the reference answers prepared in preflight |
| A3 | Map | No-data areas grey; legend present; hover fields correct; opens on Adelaide |
| A4 | Race | Frames run July 2025 to the latest month; top 15 re-ranked; play and slider work |
| A5 | Scatter | No-data deciles absent (not at zero); caption numbers match a manual check |
| A6 | Leader postcode | Card matches the table; Gemma's text uses only the given numbers and names no suburb |
| A7 | Repeat | Asking the same postcode again makes no new Gemma call |
| A8 | No-data postcode | Plain message; no Gemma call |
| A9 | Bad input | "abc" and "123" get the 4-digit message |
| A10 | Footer | Sources, licences and the Marketplace line present |
| A11 | Projector | Readable at 1280x720; nothing cut off |

## 8. Out of scope

Live Snowflake queries from the app; user accounts; deployment to the web; suburb names (the data has
postcodes only); any advice on buying batteries.
