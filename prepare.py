"""Step 1: build the dashboard's data from BLS QCEW annual averages, 2019-2025.

    python3 prepare.py        (standard library only)

Downloads (cached in data/raw/, not committed) the annual industry slices for all industries (incl. government),
the ten private-sector supersectors, and the area names, then writes dashboard/data.json:
    us, states (51 incl. DC) by industry and year: [annual average employment, average weekly wage]
    counties: all industries only (industry detail is often suppressed for counties)
"""
import csv
import io
import json
import ssl
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
YEARS = list(range(2019, 2026))
INDUSTRIES = {  # code: (name, QCEW industry file, ownership code)
    "total": ("All industries", "10", "0"), "gov": ("Government", "10", "8"),
    "1011": ("Natural resources & mining", "1011", "5"), "1012": ("Construction", "1012", "5"),
    "1013": ("Manufacturing", "1013", "5"), "1021": ("Trade, transport & utilities", "1021", "5"),
    "1022": ("Information", "1022", "5"), "1023": ("Financial activities", "1023", "5"),
    "1024": ("Professional & business services", "1024", "5"), "1025": ("Education & health services", "1025", "5"),
    "1026": ("Leisure & hospitality", "1026", "5"), "1027": ("Other services", "1027", "5"),
}


def get(url, name):
    path = RAW / name
    if not path.exists():
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (student research script)"})
                path.write_bytes(urllib.request.urlopen(req, context=CTX, timeout=120).read())
                break
            except Exception:
                time.sleep(2 ** attempt)
        time.sleep(0.3)
    return path.read_text(encoding="utf-8", errors="replace")


def is_state(f):
    return f.endswith("000") and f[:2].isdigit() and f[:2] < "57"


def is_county(f):
    return f.isdigit() and not f.endswith("000") and f[:2] < "57"


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    titles = {r["area_fips"]: r["area_title"] for r in csv.DictReader(io.StringIO(
        get("https://data.bls.gov/cew/doc/titles/area/area_titles.csv", "area_titles.csv")))}
    us, states, counties = {}, {}, {}
    for key, (_, file_code, own) in INDUSTRIES.items():
        for y in YEARS:
            text = get(f"https://data.bls.gov/cew/data/api/{y}/a/industry/{file_code}.csv", f"{y}_{file_code}.csv")
            for r in csv.DictReader(io.StringIO(text)):
                if r["own_code"] != own or r["disclosure_code"] == "N":
                    continue
                f, val = r["area_fips"], [int(r["annual_avg_emplvl"]), int(r["annual_avg_wkly_wage"])]
                if f == "US000":
                    us.setdefault(key, {})[y] = val
                elif is_state(f):
                    states.setdefault(f[:2], {}).setdefault(key, {})[y] = val
                elif is_county(f) and key == "total":
                    counties.setdefault(f, {})[y] = val
    out = {
        "source": "U.S. Bureau of Labor Statistics, Quarterly Census of Employment and Wages, annual averages",
        "years": YEARS,
        "industries": [{"key": k, "name": v[0], "ownership": {"0": "all", "5": "private", "8": "government"}[v[2]]} for k, v in INDUSTRIES.items()],
        "us": us,
        "states": {s: {"name": titles[s + "000"].replace(" -- Statewide", "").replace(", not unknown", ""), "data": d} for s, d in sorted(states.items())},
        "counties": {c: {"name": titles.get(c, c), "data": d} for c, d in sorted(counties.items())},
    }
    (HERE / "dashboard").mkdir(exist_ok=True)
    text = json.dumps(out, separators=(",", ":"))
    (HERE / "dashboard" / "data.json").write_text(text)
    print(f"US + {len(states)} states x {len(INDUSTRIES)} industries x {len(YEARS)} years; {len(counties):,} counties; "
          f"data.json {len(text) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
