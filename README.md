# Where America's jobs grew: an interactive dashboard

A Tableau-style dashboard of US employment and pay, 2019–2025, built in the browser with D3 and hosted free on
GitHub Pages; no BI licence or account needed.

**Live dashboard:** https://mrrishit909.github.io/projects/us-jobs-dashboard/dashboard/

- **Filters:** area (US or any state), year, comparison year (the year before, or 2019), industry, and map measure
  (job change or average weekly wage).
- **Map:** states coloured by the selected measure. Click a state to zoom into its counties.
- **KPI tiles:** jobs, change, weekly wage, and how many states added jobs.
- **Ranking:** top and bottom 10 states (or the selected state's counties). Click a state to drill in.
- **Trend:** jobs indexed to 2019 = 100, selected state vs the US.
- **Industry breakdown:** job change by industry. Click a bar to filter the whole dashboard to that industry.
- **Interaction:** hover tooltips everywhere, keyboard-reachable map and controls, and it works at phone width.

## Steps

| Step | File | What it does |
|---|---|---|
| 1 | `prepare.py` → `dashboard/data.json` | BLS QCEW annual averages, 2019–2025: US and 51 states for 12 industry groups, and 3,202 counties for all industries (0.69 MB) |
| 2 | `dashboard/index.html` | the dashboard: D3 v7, us-atlas county boundaries, vanilla JS, no build step |
| 3 | `check.py` | all 26,618 values in data.json equal the raw BLS files; states sum to the US; recomputes the tiles for two views to compare with the page |

## Run it

```
python3 prepare.py && python3 check.py          # standard library only
cd dashboard && python3 -m http.server          # then open http://localhost:8000
```

## What it shows (2025)

- **155.73M jobs, +0.5% on 2024 (+741,922)**, with the average weekly wage up 4.1% to $1,514. 41 of 51 states
  added jobs. Fastest: Idaho +1.8%, South Carolina and Utah +1.6%. Biggest fall: District of Columbia −2.4%.
- **By industry, 2024–25:** education & health services +3.2% and construction +1.4% grew; natural resources &
  mining (−2.1%), information (−1.9%) and manufacturing (−1.2%) shrank.
- **Since 2019:** US jobs are up 5.1%, led by education & health (+13.5%) and construction (+10.7%). Idaho is up
  16.2%, Utah 14.5% and Texas 12.1%; DC (−4.4%), Hawaii (−2.2%) and Vermont (−0.8%) are still below 2019.

## Checks done

- `check.py`: every number in the dashboard's data equals BLS's files, and the two views' tiles recompute exactly
  (US 2025 vs 2024: 155.73M, +0.5%, +741,922, $1,514, 41 of 51; leisure & hospitality 2025 vs 2019: 16.79M,
  +2.0%, +330,275, $657, 30 of 51). The page showed the same values in Chrome.
- Clicked through in Chrome: drill-down into Texas (254 counties), industry filter, wage view, 2019 comparison,
  reset, no console errors; tested at phone width.

Fixed during testing: a D3 scale built with one argument (treated as the range, so the trend lines were off-chart);
a zoom animation that stalls when the tab isn't focused (now instant); a focus outline drawn as a box around Texas;
cut-off and colliding labels at phone width; and the three libraries now ship with the page instead of loading
from a CDN, so one slow CDN can't blank the dashboard.

## Data and licences

- U.S. Bureau of Labor Statistics, Quarterly Census of Employment and Wages, annual averages
  (https://data.bls.gov/cew/data/api/), jobs covered by unemployment insurance. Industry groups are private-sector
  NAICS supersectors; "All industries" includes government.
- Figures BLS doesn't publish (to protect individual employers) show as "not published", never as zero.
  Connecticut replaced counties with planning regions in 2024, so its county map covers 2019–2023 only.
- Bundled in `dashboard/vendor/` with their licences: D3 7.9.0, topojson-client 3.1.0, us-atlas 3 (US Census
  boundaries), all ISC.

## Not done

- Annual data only (no quarterly or monthly view); counties show all industries only.
- No metro-area level; no export or share-link for a filtered view.
