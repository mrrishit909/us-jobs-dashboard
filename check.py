"""The project's check (standard library only).

    python3 check.py

1. Every number in dashboard/data.json equals the raw BLS file it came from, and every published raw row made it in.
2. The 51 states add up to the US total (within rounding) for every industry and year.
3. Recompute, from the raw files, the tiles the dashboard shows for two views, to compare with the page:
   US all industries 2025 vs 2024, and US leisure & hospitality 2025 vs 2019.
"""
import csv
import json
from pathlib import Path

from prepare import INDUSTRIES, RAW, YEARS, is_county, is_state

HERE = Path(__file__).parent


def raw_rows():
    for key, (_, file_code, own) in INDUSTRIES.items():
        for y in YEARS:
            with (RAW / f"{y}_{file_code}.csv").open(encoding="utf-8", errors="replace") as f:
                for r in csv.DictReader(f):
                    if r["own_code"] == own and r["disclosure_code"] != "N":
                        yield key, y, r


def main():
    D = json.loads((HERE / "dashboard" / "data.json").read_text())
    seen = 0
    for key, y, r in raw_rows():
        f, want = r["area_fips"], [int(r["annual_avg_emplvl"]), int(r["annual_avg_wkly_wage"])]
        if f == "US000":
            got = D["us"][key][str(y)]
        elif is_state(f):
            got = D["states"][f[:2]]["data"][key][str(y)]
        elif is_county(f) and key == "total":
            got = D["counties"][f]["data"][str(y)]
        else:
            continue
        assert got == want, (key, y, f, got, want)
        seen += 1
    n_json = sum(len(v) for v in D["us"].values()) + sum(len(v) for s in D["states"].values() for v in s["data"].values()) + \
        sum(len(c["data"]) for c in D["counties"].values())
    assert seen == n_json, (seen, n_json)

    for key in D["us"]:
        for y in map(str, YEARS):
            parts = [s["data"].get(key, {}).get(y) for s in D["states"].values()]
            if all(parts):                                    # skip where BLS withheld a state's figure
                assert abs(sum(p[0] for p in parts) - D["us"][key][y][0]) <= 51, (key, y)

    def tiles(ind, year, base):
        us = D["us"][ind]
        now, then = us[str(year)][0], us[str(base)][0]
        w_now, w_then = us[str(year)][1], us[str(base)][1]
        ch = [s["data"].get(ind, {}) for s in D["states"].values()]
        adding = sum(1 for s in ch if str(year) in s and str(base) in s and s[str(year)][0] > s[str(base)][0])
        known = sum(1 for s in ch if str(year) in s and str(base) in s)
        return (f"{now / 1e6:.2f}M jobs, {100 * (now / then - 1):+.1f}% ({now - then:+,} jobs), wage ${w_now:,} "
                f"({100 * (w_now / w_then - 1):+.1f}%), {adding} of {known} states adding jobs")
    print(f"OK: {seen:,} values in data.json equal the raw BLS files; states sum to the US total")
    print("  US, all industries, 2025 vs 2024:       " + tiles("total", 2025, 2024))
    print("  US, leisure & hospitality, 2025 vs 2019: " + tiles("1026", 2025, 2019))


if __name__ == "__main__":
    main()
