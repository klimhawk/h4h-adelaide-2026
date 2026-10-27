# Data

Battery Race was built by loading Clean Energy Regulator (CER) CSVs into Snowflake, joining them
with two Data Army Intel listings from Snowflake Marketplace, and exporting local app files.
CoCo helped with discovery, SQL, match checks and exports. The app reads the exported files;
it does not query Snowflake at runtime.

## Included files and provenance

| File in `data/` | Status in this repository | Source and preparation | Licence or terms |
|---|---|---|---|
| `sgu-battery-installations-2011-to-present-and-totals.csv` | Included | CER, SGU battery installations, July 2025 to August 2026 snapshot; unchanged source CSV | CC BY 4.0 |
| `sgu-solar-installations-2011-to-present-and-totals.csv` | Included | CER, SGU solar installations, January 2011 to August 2026 plus historic 2001 to 2010 total; unchanged source CSV | CC BY 4.0 |
| `sa_battery_monthly.csv` | Included | CER battery CSV loaded into Snowflake and reshaped into monthly rows; SA postcodes exported for the app | CC BY 4.0 |
| `sa_postcode_battery_seifa.csv` | Not included; generate in your own Snowflake account | CER battery and solar totals joined to Data Army Intel's ABS SEIFA 2021 listing `GZSUZ2MM5HIL`, table `SEIFA.SEIFA_POA` | Snowflake Marketplace terms apply; export not redistributed |
| `sa_postal_areas_simplified.geojson` | Not included; generate in your own Snowflake account | Data Army Intel's Geography listing `GZSUZCN9CY`, table `GEOGRAPHY_AUS_FREE.ABS_POA_2021_AUST_GDA2020`; SA boundaries simplified to 100 m in Snowflake | Snowflake Marketplace terms apply; export not redistributed |

## Source the Marketplace data and prepare the app files

To work through these steps by pasting prompts into CoCo, follow
[Rebuild with CoCo](rebuild-with-coco.md). The SQL route is in [rebuild.md](rebuild.md).

1. In Snowsight Marketplace, search for **ABS Socio-Economic Indexes for Areas (SEIFA 2021)
   Data - Free**, provided by **Data Army Intel** (listing `GZSUZ2MM5HIL`).
2. Search for **Geography - Boundaries & Insights - Australia**, also provided by
   **Data Army Intel** (listing `GZSUZCN9CY`).
3. Check pricing and availability in your account region. The account holder clicks **Get** and
   reviews and accepts each listing's terms. The original build used free listings; confirm
   the current offer before proceeding.
4. Follow [rebuild.md, steps 1 to 4](rebuild.md#1-get-the-two-marketplace-listings) to mount the
   databases and load the included CER source CSVs into Snowflake.
5. Run the [join SQL in step 5](rebuild.md#5-join-view), then the
   [export and download commands in step 6](rebuild.md#6-export-the-app-files). Save the joined CSV
   and GeoJSON under the exact filenames above in your local `data/` folder.
6. Once all three app files are present, follow the test and run instructions in the README.

The two Marketplace-derived exports are intentionally absent and ignored by git. Keep your
locally generated copies out of commits. The documentation supplies the sourcing and preparation
steps used in the project, rather than distributing the exports.

## CER source downloads

The two CER CSVs were downloaded on 3 October 2026 from the
[CER small-scale installation postcode data](https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data)
page. They are the same files as in
[`data/3_sustainability/S1_cer-small-scale-installations/`](../../data/3_sustainability/S1_cer-small-scale-installations/).
The included CSV headers identify their final month as August 2026. Official source pages verified
on 27 October 2026:

- [CER small-scale installation postcode data](https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data)
- [CER battery installation download](https://cer.gov.au/document/sgu-battery-installations-2011-to-present-and-totals)
- [CER solar installation download](https://cer.gov.au/document/sgu-solar-installations-2011-to-present-and-totals)
- [CER copyright and attribution policy](https://cer.gov.au/about-us/our-policies/copyright)
- [ABS SEIFA 2021 release and downloads](https://www.abs.gov.au/statistics/people/people-and-communities/socio-economic-indexes-areas-seifa-australia/2021)
- [ABS ASGS Edition 3 digital boundary files](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files)
- [ABS copyright policy](https://www.abs.gov.au/website-privacy-copyright-and-disclaimer)

Current CER downloads can contain extra months and revised historical counts. The included
snapshot is kept so the worked example and its acceptance checks remain reproducible.

## Attribution and terms

The included CER files are provided under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Source CER CSVs: Licensed from the Clean Energy Regulator, Commonwealth of Australia under a
Creative Commons Attribution 4.0 licence.

Monthly SA series: Based on Clean Energy Regulator material licensed under a Creative Commons
Attribution 4.0 licence. Changes: SA filtering and monthly reshaping in Snowflake.

The original project obtained ABS SEIFA 2021 and ASGS 2021 postal area data through Data Army
Intel's Snowflake Marketplace listings. Access and use of those listings are subject to their
terms. Their exported data is not redistributed here. The ABS's own downloads have a separate
CC BY 4.0 policy; those direct downloads were not the route used to execute this project.

## Join and limits

- Key: four-character CER postcode = ABS Postal Area code; SA is codes 5000 to 5999.
- Batteries: installations since July 2025. Solar: monthly installations plus the historic total.
- Rate: 100 times batteries divided by solar installations. The divisor counts installations,
  not unique homes. Replacements can be counted again, and batteries need not accompany solar.
- 347 joined postcodes: 338 MATCHED, 3 NO_DECILE (5111, 5160, 5950), 6 NO_POSTAL_AREA
  (5001, 5071, 5175, 5207, 5312, 5875). Missing deciles stay blank, not zero.
- 4,564 monthly rows and 341 postal area shapes. Postcodes and ABS Postal Areas are not identical
  geographies; joining by code is an approximation. SEIFA describes areas, not individual people.
- CER allows 12 months for certificate creation, so recent counts can rise in later releases.

