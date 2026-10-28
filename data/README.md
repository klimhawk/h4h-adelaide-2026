# Data guide

Real South Australian open data, already downloaded and checked, so your team spends the
afternoon building, not searching. Everything in this folder is open data you may use in your
project, as long as you credit the source (see [Credit the source](#credit-the-source)).

```text
data/
  1_health/  2_education/  3_sustainability/  4_foundation/   start here
  extras/                                                      more sets, same theme folders
  LICENCES/                                                    licence texts
```

## How to use this guide

1. **Pick your theme**, then open its **Start here** datasets. Each one matches a challenge
   idea and is small enough to understand in 15 minutes.
2. **Add context from [Works with every theme](#4-works-with-every-theme)**: population, income,
   disadvantage, jobs, maps. These turn "a number" into "a number per person in this suburb".
3. **Join on a shared key** (see [How datasets connect](#how-datasets-connect)). That is where
   most good projects come from.
4. **Need more?** Look in the same theme folder or in `extras/`. Sets marked ↗ are not in this
   repo: links and steps are in [Get it yourself](#get-it-yourself).

**Legend:** ★ Start here (in this repo) · ● in this repo · ↗ get it yourself (link)

---

## 1. Health

**Adelaide angles:** aged care support; rural and regional access to health care.

### Aged care

| | Dataset | What it tells you | Level | Period | Format | Where |
| --- | --- | --- | --- | --- | --- | --- |
| ★ | **A2 People using aged care by region** | How many people use home support, home care, residential and flexible care | aged care planning region | 2024-25 | XLSX ×5 | [folder](1_health/A2_people-using-aged-care-by-region/) |
| ★ | **A3 My aged care region tables** | Quick profile of each SA planning region and the two SA Primary Health Networks | planning region, PHN | 2024-25 | XLSX | [folder](1_health/A3_my-aged-care-region-tables/) |
| ↗ | A1 Aged care service list (SA) | Every government-funded aged care service in SA: type, provider, location | service, planning region | at 30 Jun 2025 | XLSX | [publisher](https://www.gen-agedcaredata.gov.au/resources/access-data/2025/october/aged-care-service-list-30-june-2025) |

Tip: A2 is counts, not rates. Divide by population (F2) to compare regions fairly.

### Rural and regional access

| | Dataset | What it tells you | Level | Period | Format | Where |
| --- | --- | --- | --- | --- | --- | --- |
| ★ | **H2 Mortality Over Regions and Time (MORT)** | Deaths, leading causes and premature deaths by region: country SA against Adelaide | LGA, SA3, PHN | 2020 to 2024 | CSV | [folder](1_health/H2_mort-books/) |
| ↗ | H1 MyHospitals data (SA) | Emergency presentations and waits, elective surgery, admissions by hospital | hospital | to Aug 2026 | XLSX, CSV | [publisher](https://www.aihw.gov.au/hospitals/other-resources/myhospitals-api) |
| ↗ | A4 Medicare local areas | Use of GP, allied health and specialist care by local area | SA3, PHN | 2017-18 to 2024-25 | XLSX | [publisher](https://www.aihw.gov.au/reports/primary-health-care/medicare-subsidised-gp-allied-health-specialist/data) |
| ↗ | H3 PHIDU Social Health Atlas (SA) | Hundreds of health and social indicators per area | LGA, population health area | 2026 release | XLSX | [publisher](https://phidu.torrens.edu.au/social-health-atlases/data) |
| ↗ | H12 Medicare statistics by remoteness | Bulk billing and GP use from city to very remote | remoteness, SA3 | to 2025-26 | XLSX | [publisher](https://www.health.gov.au/resources/collections/medicare-statistics-collection) |
| ↗ | H10 AIHW hospital statistics | National and state hospital tables | state | various | XLSX | [publisher](https://www.aihw.gov.au/hospitals/latest-updates-and-downloads/data) |
| ↗ | H11 MBS and PBS item statistics | Services and medicines by item, via a query tool | state | ongoing | query | [publisher](https://www.servicesaustralia.gov.au/medicare-statistics?context=22) |
| ↗ | H4 World Bank health indicators | International comparisons | country | to 2026 | CSV | [publisher](https://datacatalog.worldbank.org/search/dataset/0037712/world-development-indicators) |

Tip: present deaths data with care. Small numbers are suppressed, and behind each one is a person.

**Project ideas:** *Getting help at home* (A2, A3) · *Distance should not decide* (H2)

---

## 2. Education

**Adelaide angle:** reskilling and career change for SA's manufacturing and defence workforce.

| | Dataset | What it tells you | Level | Period | Format | Where |
| --- | --- | --- | --- | --- | --- | --- |
| ★ | **R1 Occupation Shortage List 2025** | Which occupations are in shortage, with an SA rating | occupation (ANZSCO) | 2025 | XLSX | [folder](2_education/R1_occupation-shortage-list-2025/) |
| ★ | **R2 Internet Vacancy Index** | Online job ads by occupation, Greater Adelaide and SA regions | occupation, SA4 region | monthly to Aug 2026 | XLSX | [folder](2_education/R2_internet-vacancy-index-aug-2026/) |
| ★ | **R4 ABS labour force detail and Defence Industry Account** | Manufacturing and defence workforce numbers for your pitch | state, industry | Mar 2026; 2024-25 | XLSX | [folder](2_education/R4_abs-labour-force-defence-context/) |
| ● | E1 Enrolments by school (SA government) | Enrolments per school | school | 2009 to 2023 | CSV | [folder](extras/2_education/E1_sa-gov-enrolments-by-school/) |
| ● | E2 Attendance rate by school | Attendance per school | school | 2014 to 2023 | CSV | [folder](extras/2_education/E2_sa-attendance-rate-by-school/) |
| ● | E14 School and preschool sites | Where each site is (latitude, longitude) | site | 2023 | CSV | [folder](extras/2_education/E14_sa-gov-preschool-school-sites/) |
| ● | E3 Education sites (map layer) | Same sites as a map layer | site | 2026 | GeoJSON | [folder](extras/2_education/E3_sa-gov-education-sites-geojson/) |
| ● | E4 Schools, Australia 2025 | Students, staff and schools | state | 2025 | XLSX | [folder](extras/2_education/E4_abs-schools-australia-2025/) |
| ↗ | R3 NCVER Apprentices and trainees | Who is training in which trade, with a 20-year series | occupation, state | at 31 Mar 2026 | XLSX | [publisher](https://www.ncver.edu.au/research-and-statistics/publications/all-publications/apprentices-and-trainees-2026-march-quarter) |
| ↗ | E10 ACARA My School files | School profiles, locations, enrolments by grade | school | 2025 | XLSX | [publisher](https://www.acara.edu.au/contact-us/acara-data-access) |
| ↗ | E12 Australian Early Development Census | Child development by area | SA2, LGA | 2009 to 2024 | XLSX, GIS | [publisher](https://www.aedc.gov.au/data-hub/public-data/additional-data) |
| ↗ | E13 NCVER VOCSTATS | Detailed training data (needs an account) | various | ongoing | query | [publisher](https://www.ncver.edu.au/research-and-statistics/vocstats) |
| ↗ | E11 National Report on Schooling portal | National and state school figures | state | 2025 | interactive | [publisher](https://www.acara.edu.au/reporting/national-report-on-schooling-in-australia-data-portal) |

Tip: R1 and R2 (and R3, if you get it) use ANZSCO occupation codes. Join on the code, not the
job title.

**Project ideas:** *Next job, next skill* (R1, R2) · *Filling the trade pipeline* (R1, R4, and R3 from [Get it yourself](#get-it-yourself))

---

## 3. Sustainability

**Adelaide angles:** household and small-business energy transition; water security; regional agriculture.

### Energy transition

| | Dataset | What it tells you | Level | Period | Format | Where |
| --- | --- | --- | --- | --- | --- | --- |
| ★ | **S1 Small-scale installations** | Rooftop solar, batteries and heat pumps installed, by postcode | postcode | 2011 to Aug 2026 | CSV | [folder](3_sustainability/S1_cer-small-scale-installations/) |
| ● | S16 AEMO price and demand (SA) | Wholesale electricity price and demand every 5 minutes | SA region | Oct 2025 to Sep 2026 | CSV ×12 | [folder](extras/3_sustainability/S16_aemo-price-demand-sa1/) |
| ● | S12 NGER facility data | Generation and emissions of SA power stations | facility | 2024-25 | CSV | [folder](extras/3_sustainability/S12_nger-2024-25/) |
| ● | S11 State greenhouse gas inventories | SA emissions by sector over 35 years | state | 1989-90 to 2023-24 | XLSX | [folder](extras/3_sustainability/S11_state-territory-ghg-inventories-2024/) |

Tip: S1 is by postcode. Join it to income (F6) or Census postcode files (F1) to ask *who* is
being left behind.

### Water security

| | Dataset | What it tells you | Level | Period | Format | Where |
| --- | --- | --- | --- | --- | --- | --- |
| ★ | **W1 SA Water reservoir volumes** | How full Adelaide's reservoirs are each month, plus 5 years of operations | reservoir | May 2018 to Aug 2026 | CSV | [folder](3_sustainability/W1_sa-water-reservoir-volumes/) |
| ↗ | W2 Water Data SA | River Murray flows and Lower Lakes levels | site | live | CSV | [publisher](https://water.data.sa.gov.au/) |

### Regional agriculture

| | Dataset | What it tells you | Level | Period | Format | Where |
| --- | --- | --- | --- | --- | --- | --- |
| ★ | **G1 Broadacre crops** | Area and production of wheat, barley, canola and more | state | 2024-25 | XLSX | [folder](3_sustainability/G1_abs-broadacre-crops/) |
| ★ | **G2 ABARES Australian crop report** | This season's crop forecast | state | Sep 2026 | XLSX | [folder](3_sustainability/G2_abares-crop-report-sep-2026/) |
| ↗ | S5 SILO weather for SA stations | Daily rainfall, temperature, evaporation | weather station | daily to yesterday | CSV | [publisher](https://www.longpaddock.qld.gov.au/silo/) |
| ↗ | S15 BoM Climate Data Online | Station data from the Bureau (12 SA station numbers listed below) | weather station | to Oct 2026 | CSV | [publisher](https://www.bom.gov.au/climate/data/) |

Tip: G1 and G2 are state totals. For rainfall, get S5 for a few farming-district stations and
compare the season's rain with what SA grew. G1 uses new methods, so older years are not directly
comparable.

### Urban environment (cross-theme)

| | Dataset | What it tells you | Level | Period | Format | Where |
| --- | --- | --- | --- | --- | --- | --- |
| ● | S3 Urban heat and social vulnerability | Hottest areas and who lives there, day and night | area | 2022 | GeoJSON | [folder](extras/3_sustainability/S3_adelaide-urban-heat-2022/) |
| ● | S2 Tree canopy | Canopy cover per suburb and change since 2018-19 | suburb | 2022 | CSV | [folder](extras/3_sustainability/S2_adelaide-tree-canopy-suburb/) |
| ● | S4 Adelaide CBD air quality | Fine particle readings | one station | 2014 to 2026 | CSV | [folder](extras/3_sustainability/S4_adelaide-cbd-air-quality-particle/) |
| ● | S10 Waste and resource recovery | Waste generated and recycled | state | 2026 database | XLSX | [folder](extras/3_sustainability/S10_nwrr-database-2026/) |
| ↗ | S13, S14 Digital Earth Australia | Land cover and surface water from satellites | grid | 1986 to now | GeoTIFF (large) | [steps](#get-it-yourself) |

**Project ideas:** *Power to the people* (S1) · *Every drop counts* (W1) · *Rain to harvest* (G1, G2, with S5 from [Get it yourself](#get-it-yourself))

---

## 4. Works with every theme

Population, money, work and maps. Pair any theme dataset with these.

| Group | | Dataset | What it tells you | Level | Period | Where |
| --- | --- | --- | --- | --- | --- | --- |
| People | ● | F1 Census 2021 community profiles (SA) | Age, household, language, health conditions, travel to work and more | SA2, LGA, postcode, suburb | 2021 | [folder](4_foundation/F1_census-2021-gcp-sa/) |
| People | ● | F2 Regional population | How many people live there now, and growth | SA2, LGA | 2024-25 | [folder](4_foundation/F2_abs-regional-population-2024-25/) |
| Advantage | ● | F4 SEIFA 2021 | Relative advantage and disadvantage score per area | SA2, LGA, postcode, suburb | 2021 | [folder](4_foundation/F4_seifa-2021/) |
| Money | ● | F5 Personal income | Earners and income per area | SA2, LGA | 2022-23 | [folder](4_foundation/F5_abs-personal-income-2022-23/) |
| Money | ● | F6 ATO taxation statistics | Median and average taxable income | postcode | 2023-24 | [folder](4_foundation/F6_ato-taxation-stats-2023-24/) |
| Money | ● | F8 DSS payment recipients | People on Age Pension, JobSeeker and other payments | SA2, LGA | to Jun 2026 | [folder](4_foundation/F8_dss-payment-demographics/) |
| Work | ● | F7 Small Area Labour Markets | Unemployment rate estimates | SA2, LGA | Mar quarter 2026 | [folder](4_foundation/F7_salm-mar-2026/) |
| Maps | ● | F12 Boundaries | Shapes to map any SA2 dataset (LGA and postcode shapes too) | SA2, LGA, postcode | 2021 edition | [folder](4_foundation/F12_asgs-edition3-boundaries/) |
| Maps | ● | F13 Geography correspondences | Converts postcode or LGA data to SA2 and back | all | 2021 edition | [folder](4_foundation/F13_asgs-edition3-correspondences/) |
| Getting around | ● | F14 Adelaide Metro timetable (GTFS) | Every stop, route and timetable | stop | Oct 2026 | [folder](extras/4_foundation/F14_adelaide-metro-gtfs/) |
| Cost of living | ● | F10 Monthly household spending (SA) | Spending trend by category | state | Aug 2026 | [folder](extras/4_foundation/F10_abs-household-spending-indicator-aug-2026/) |
| Cost of living | ● | F11 Living cost indexes | Cost of living by household type | capital cities | Jun quarter 2026 | [folder](extras/4_foundation/F11_abs-selected-living-cost-indexes-jun-2026/) |
| Cost of living | ● | F9 Household Expenditure Survey | What households spend on what | state | 2015-16 (old) | [folder](extras/4_foundation/F9_abs-household-expenditure-2015-16/) |
| Regional summary | ↗ | F3 Data by Region | Ready-made regional facts across topics | SA2, LGA | 2011 to 2025 | [publisher](https://dbr.abs.gov.au/) |

---

## How datasets connect

| Key | Found in | Use it to |
| --- | --- | --- |
| **SA2** (statistical area, about 10,000 people) | F1, F2, F4, F5, F7, F8, F12 | map anything; compare suburbs fairly |
| **LGA** (council area) | F1, F2, F4, F5, F7, F8, H2 (and H3 ↗) | talk to councils; regional SA |
| **Postcode** | S1, F6, F1, F4 | link solar or income to people; convert to SA2 with F13 |
| **Occupation code (ANZSCO)** | R1, R2 (and R3 ↗) | match shortages, job ads and training |
| **Aged care planning region, PHN** | A2, A3, H2 (and A1 ↗) | compare aged care and health regions |
| **Weather station** | S5 ↗, S15 ↗ | link rainfall to water and crops (match stations to regions by distance) |

---

## Get it yourself

These sets are not in this repo. You need the internet on the day; most take a few minutes.
Two things to know for all of them: download them yourself rather than passing files between
teams, and where the terms say "own use", keep the downloaded files out of your public repo
(link to the source instead).

### Health

**A1 Aged care service list (SA)**: <https://www.gen-agedcaredata.gov.au/resources/access-data/2025/october/aged-care-service-list-30-june-2025>
Every government-funded aged care service in SA: type, provider, location. The list is at
30 June 2025, before the Support at Home program started (1 November 2025).

**H1 MyHospitals data**: <https://www.aihw.gov.au/hospitals/other-resources/myhospitals-api>
Emergency presentations and waits, elective surgery and admissions, by hospital. Filter to SA
hospitals. *CC BY.*

**A4 Medicare local areas**: <https://www.aihw.gov.au/reports/primary-health-care/medicare-subsidised-gp-allied-health-specialist/data>
Use of GP, allied health and specialist care by local area. Filter to SA. *CC BY.*

**H3 PHIDU Social Health Atlas (SA)**: <https://phidu.torrens.edu.au/social-health-atlases/data>
Hundreds of health and social indicators per council area and population health area. Its
licence (CC BY-NC-SA) does not allow commercial use, and asks you to share anything you make
from it under the same licence.

**H12 Medicare statistics by remoteness**: <https://www.health.gov.au/resources/collections/medicare-statistics-collection>
Download "Medicare annual statistics: Modified Monash Model locations" (XLSX) for city to very
remote, or the quarterly SA3 summary for local areas. Filter to SA. *Terms: own use only; keep
the file out of public repos.*

**H10 AIHW hospital statistics**: <https://www.aihw.gov.au/hospitals/latest-updates-and-downloads/data>
Pick a topic (emergency departments, elective surgery, admitted care) and download its data
tables (XLSX). State and national level; for single SA hospitals use H1. *CC BY.*

**H11 MBS and PBS item statistics**: <https://www.servicesaustralia.gov.au/medicare-statistics?context=22>
Choose a report, enter the item numbers and date range, then export as CSV. Results are by
state, not by suburb.

**H4 World Bank health indicators**: <https://datacatalog.worldbank.org/search/dataset/0037712/world-development-indicators>
The full file is 270 MB. Use the DataBank link on that page instead: pick Australia and the
countries you want to compare, tick the health indicators, download as CSV. *CC BY.*

### Education

**R3 NCVER Apprentices and trainees**: <https://www.ncver.edu.au/research-and-statistics/publications/all-publications/apprentices-and-trainees-2026-march-quarter>
Who is training in which trade, with a 20-year series. Use "Download all data" (XLSX).
*CC BY 3.0 AU.*

**E10 ACARA My School files**: <https://www.acara.edu.au/contact-us/acara-data-access>
Download School Profile 2025, School Location 2025 and Enrolments by Grade 2025 (XLSX; the 2008
to 2025 histories are about 30 MB each). Filter to SA. *Terms: My School terms of use, personal
non-commercial educational use. Keep the files and raw rows out of public repos.*

**E12 Australian Early Development Census**: <https://www.aedc.gov.au/data-hub/public-data/additional-data>
Download the SA2 or LGA table (2009 to 2024, XLSX), or the South Australia GIS files to map it.
*Terms: own, non-commercial use; keep the files out of public repos.*

**E13 NCVER VOCSTATS**: <https://www.ncver.edu.au/research-and-statistics/vocstats>
Needs an application and a login, which may not come through on the day. Apply beforehand, or
use R3 above, which covers apprentices and trainees without a login.

**E11 National Report on Schooling data portal**: <https://www.acara.edu.au/reporting/national-report-on-schooling-in-australia-data-portal>
Open a table, set the filters, export to XLSX. State level. *CC BY.*

### Sustainability

**W2 Water Data SA**: <https://water.data.sa.gov.au/>
River Murray flows and Lower Lakes levels, by monitoring site, exported as CSV. *CC BY.*

**S5 SILO weather for SA stations**: <https://www.longpaddock.qld.gov.au/silo/>
Daily rainfall, temperature and evaporation for SA weather stations (use the station numbers in
the S15 table below). *CC BY.*

**S15 BoM Climate Data Online**: <https://www.bom.gov.au/climate/data/>
Choose the data type (for example daily rainfall), enter a station number, select "Get data",
then download "All years of data" (zip of CSV). Stations:

| Station | Number | Station | Number |
| --- | --- | --- | --- |
| Adelaide (West Terrace / ngayirdapira) | 023000 | Minlaton Aero | 022031 |
| Adelaide Airport | 023034 | Port Lincoln AWS | 018192 |
| Roseworthy AWS | 023122 | Kimba | 018040 |
| Nuriootpa PIRSA | 023373 | Renmark Aero | 024048 |
| Clare High School | 021131 | Loxton Research Centre | 024024 |
| Mount Gambier Aero | 026021 | Murray Bridge (Pallamana) | 024584 |

*Terms: own use; do not share copies or script the downloads. For anything you publish, use S5:
the same stations under CC BY.*

**S13 DEA Land Cover and S14 DEA Water Observations**:

- <https://knowledge.dea.ga.gov.au/data/product/dea-land-cover-landsat/index.html>
- <https://knowledge.dea.ga.gov.au/data/product/dea-water-observations-landsat/index.html>

Satellite layers for all of Australia since 1986. Use the product page's data access links to
view them on a map or cut out an area. Large files and GIS skills needed: plan for it. *CC BY.*

### Works with every theme

**F3 Data by Region**: <https://dbr.abs.gov.au/>
Ready-made regional facts across topics (population, income, health, environment) by SA2 and
LGA. Filter to SA. *CC BY.*

---

## Using the data in Snowflake

Set up your Snowflake account and CoCo first: [Snowflake setup](https://klimhawk.github.io/h4h-adelaide-2026/snowflake-setup.html).
Every table here is CSV or XLSX (maps are GeoJSON or shapefiles). To get a CSV into Snowflake,
ask CoCo to load it, for example: "Load data/[file].csv into a new table. Keep postcodes as text."

---

## Credit the source

The licences ask for this, so it is the one thing you must do: **for every dataset you use, put
its credit line in your project's README and on your final slide.** If you changed the data
(filtered, joined, summarised), say so, for example by starting with "Based on".

Most sets are CC BY 4.0: use them freely and credit the source. Four sets use older Australian
licences that also ask for **a copy of the licence text (or its web address) with every copy you
share**: H2 (CC BY 3.0 AU), and F6, F8 and S10 (CC BY 2.5 AU). S16 comes under AEMO's own
copyright permissions. The licence texts are in [`LICENCES/`](LICENCES/).

For ↗ sets, the terms are the ones you accept when you download them.

### Health

| Set | Credit line | Licence |
| --- | --- | --- |
| A2 | Source: Australian Institute of Health and Welfare, GEN Aged Care Data, People using aged care by region 2024-25. | CC BY 4.0 |
| A3 | Source: Australian Institute of Health and Welfare, GEN Aged Care Data, My aged care region supplementary tables 2024-25. | CC BY 4.0 |
| H2 | Source: Australian Institute of Health and Welfare, Mortality Over Regions and Time (MORT) books, data.gov.au. | CC BY 3.0 AU |

### Education

| Set | Credit line | Licence |
| --- | --- | --- |
| R1 | © Commonwealth of Australia. Jobs and Skills Australia, Occupation Shortage List 2025. | CC BY 4.0 |
| R2 | © Commonwealth of Australia. Jobs and Skills Australia, Internet Vacancy Index, August 2026. | CC BY 4.0 |
| R4 | Australian Bureau of Statistics, Labour Force, Australia, Detailed, Mar 2026 (Table 05); Australian Defence Industry Account 2024-25. | CC BY 4.0 |
| E1, E2, E3, E14 | Source: Department for Education, Government of South Australia, licensed under CC BY 4.0 (data.sa.gov.au). | CC BY 4.0 |
| E4 | Australian Bureau of Statistics, Schools, Australia, 2025. | CC BY 4.0 |

### Sustainability

| Set | Credit line | Licence |
| --- | --- | --- |
| S1, S12 | Licensed from the Clean Energy Regulator, Commonwealth of Australia under a Creative Commons Attribution 4.0 licence. | CC BY 4.0 |
| S16 | Source: Australian Energy Market Operator (AEMO), Aggregated price and demand data, SA1, October 2025 to September 2026, aemo.com.au. | AEMO copyright permissions |
| S11 | Department of Climate Change, Energy, the Environment and Water. 2026. State and territory greenhouse gas inventories 2024. | CC BY 4.0 |
| W1 | Source: SA Water, Government of South Australia, licensed under CC BY 4.0 (data.sa.gov.au). | CC BY 4.0 |
| G1 | Australian Bureau of Statistics, Australian Agriculture: Broadacre Crops, 2024-25. | CC BY 4.0 |
| G2 | ABARES 2026, Australian crop report: September 2026, No. 219, Canberra. | CC BY 4.0 |
| S2, S3 | Source: Department for Environment and Water, Government of South Australia, licensed under CC BY 4.0 (data.sa.gov.au). | CC BY 4.0 |
| S4 | Source: Environment Protection Authority, Government of South Australia, licensed under CC BY 4.0 (data.sa.gov.au). | CC BY 4.0 |
| S10 | Department of Climate Change, Energy, the Environment and Water. 2026. National Waste and Resource Recovery Database 2026, data.gov.au. | CC BY 2.5 AU |

### Works with every theme

| Set | Credit line | Licence |
| --- | --- | --- |
| F1 | Australian Bureau of Statistics (2021) Census of Population and Housing, General Community Profile DataPack, South Australia. | CC BY 4.0 |
| F2 | Australian Bureau of Statistics, Regional Population, 2024-25. | CC BY 4.0 |
| F4 | Australian Bureau of Statistics, Socio-Economic Indexes for Areas (SEIFA), Australia, 2021. | CC BY 4.0 |
| F5 | Australian Bureau of Statistics, Personal Income in Australia, 2022-23. | CC BY 4.0 |
| F6 | Source: Australian Taxation Office, Taxation Statistics 2023-24, data.gov.au. | CC BY 2.5 AU |
| F7 | © Commonwealth of Australia (Department of Employment and Workplace Relations), Small Area Labour Markets, March quarter 2026. | CC BY 4.0 |
| F8 | Source: Department of Social Services, DSS Benefit and Payment Recipient Demographics, data.gov.au. | CC BY 2.5 AU |
| F12 | Australian Bureau of Statistics, Australian Statistical Geography Standard (ASGS) Edition 3, digital boundary files. | CC BY 4.0 |
| F13 | Australian Bureau of Statistics, ASGS Edition 3 correspondences, data.gov.au. | CC BY 4.0 |
| F14 | Source: Department for Infrastructure and Transport, Government of South Australia, licensed under CC BY 4.0 (data.sa.gov.au). | CC BY 4.0 |
| F9 | Australian Bureau of Statistics, Household Expenditure Survey, Australia: Summary of Results, 2015-16. | CC BY 4.0 |
| F10 | Australian Bureau of Statistics, Monthly Household Spending Indicator, August 2026. | CC BY 4.0 |
| F11 | Australian Bureau of Statistics, Selected Living Cost Indexes, Australia, June 2026. | CC BY 4.0 |
