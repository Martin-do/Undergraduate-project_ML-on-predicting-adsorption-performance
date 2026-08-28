"""Paper 2 V3 candidate-domain feasibility audit.

Downloads only public source datasets and reports provenance/descriptor feasibility.
NO model is trained here.
"""
from __future__ import annotations

from pathlib import Path
from io import BytesIO
import json, re, zipfile
import requests
import pandas as pd

OUT = Path("paper2_v3/outputs/domain_feasibility")
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = [
    {
        "domain": "PHOSPHATE_BIOCHAR",
        "source": "Iftikhar phosphate 2025",
        "url": "https://raw.githubusercontent.com/Sara-Iftikhar/po4_removal_ml/main/scripts/master_sheet_0802.xlsx",
    },
    {
        "domain": "DYE_BIOCARBON",
        "source": "Liu dye 2025",
        "url": "https://raw.githubusercontent.com/17609858895/ML-predict-biochar-adsorb-dye/main/Biochar_dye_filtered.xlsx",
    },
    {
        "domain": "HEAVY_METAL_BIOCHAR",
        "source": "Yu PbCd 2026",
        "url": "https://www.mdpi.com/article/10.3390/w18121416/s1",
    },
]

FIELD_FAMILIES = {
    "primary_source": [r"^ref$", r"reference", r"source", r"doi", r"paper", r"literature"],
    "adsorbent_id": [r"adsorbent", r"biochar", r"material"],
    "feedstock": [r"feedstock", r"precursor", r"biomass"],
    "modification": [r"activation", r"modification", r"modified", r"activating"],
    "pyrolysis_temp": [r"pyrolysis.*temp", r"pyrol.*temp", r"carbonization.*temp"],
    "pyrolysis_time": [r"pyrolysis.*time", r"pyrol.*time", r"residence.*time"],
    "surface_area": [r"surface.*area", r"\bbet\b"],
    "pore_volume": [r"pore.*volume", r"\bpv\b"],
    "pore_size": [r"pore.*size", r"pore.*diam"],
    "carbon": [r"^c$", r"carbon.*content", r"\bc\s*\(%"],
    "oxygen": [r"^o$", r"oxygen.*content", r"\bo\s*\(%"],
    "nitrogen": [r"^n$", r"nitrogen.*content", r"\bn\s*\(%"],
    "ash": [r"ash"],
    "solution_pH": [r"solution.*ph", r"^ph$", r"ph_sol"],
    "initial_concentration": [r"initial.*con", r"\bci\b", r"c0", r"concentration"],
    "dose_loading": [r"dose", r"loading", r"solid.*liquid", r"s/l"],
    "contact_time": [r"contact.*time", r"adsorption.*time"],
    "adsorption_temp": [r"adsorption.*temp", r"temperature"],
    "target_qe": [r"^qe$", r"adsorption.*capacity", r"equilibrium.*capacity", r"^q$"],
    "pollutant_or_ion": [r"dye", r"pollutant", r"ion_type", r"metal", r"adsorbate"],
}


def normalise(x):
    return re.sub(r"\s+", " ", str(x).strip().lower())


def acquire(src):
    headers = {"User-Agent": "Mozilla/5.0 V3-feasibility-audit/1.0"}
    r = requests.get(src["url"], timeout=60, headers=headers, allow_redirects=True)
    info = {
        "domain": src["domain"], "source": src["source"], "requested_url": src["url"],
        "status": r.status_code, "final_url": r.url,
        "content_type": r.headers.get("content-type", ""),
        "content_disposition": r.headers.get("content-disposition", ""),
        "bytes": len(r.content),
    }
    r.raise_for_status()
    content = r.content
    # XLSX is a ZIP container. If an HTML landing page was returned, flag rather than guess data.
    if content[:2] == b"PK":
        return content, info
    if b"<html" in content[:1000].lower() or b"<!doctype" in content[:1000].lower():
        info["parse_error"] = "HTML returned instead of spreadsheet"
        return None, info
    info["parse_error"] = "Unrecognized non-XLSX payload"
    return None, info


def choose_sheet(xls: pd.ExcelFile):
    # Prefer names indicating original/raw data, otherwise first sheet.
    for name in xls.sheet_names:
        if any(k in name.lower() for k in ["original", "raw", "data", "sheet1"]):
            return name
    return xls.sheet_names[0]


def find_matches(columns, patterns):
    hits = []
    for c in columns:
        nc = normalise(c)
        if any(re.search(p, nc) for p in patterns):
            hits.append(c)
    return hits


def coverage(df, cols):
    if not cols:
        return None
    # For synonymous columns choose the one with highest non-null coverage.
    vals = [float(df[c].notna().mean()) for c in cols if c in df]
    return max(vals) if vals else None


summary_rows, coverage_rows, source_rows, acquisition = [], [], [], []

for src in SOURCES:
    try:
        payload, acq = acquire(src)
    except Exception as e:
        acquisition.append({"domain": src["domain"], "source": src["source"], "error": repr(e)})
        summary_rows.append({"domain": src["domain"], "source": src["source"], "status": "ACQUISITION_FAILED"})
        continue
    acquisition.append(acq)
    if payload is None:
        summary_rows.append({"domain": src["domain"], "source": src["source"], "status": "NOT_PARSEABLE"})
        continue

    xls = pd.ExcelFile(BytesIO(payload))
    sheet = choose_sheet(xls)
    df = pd.read_excel(BytesIO(payload), sheet_name=sheet)
    df = df.dropna(how="all").reset_index(drop=True)
    cols = list(df.columns)

    family_hits = {fam: find_matches(cols, pats) for fam, pats in FIELD_FAMILIES.items()}
    source_cols = family_hits["primary_source"]
    source_nonnull = None
    source_unique = None
    if source_cols:
        best = max(source_cols, key=lambda c: df[c].notna().mean())
        source_nonnull = float(df[best].notna().mean())
        source_unique = int(df[best].dropna().astype(str).nunique())
    else:
        best = None

    ads_cols = family_hits["adsorbent_id"]
    ads_unique = None
    if ads_cols:
        best_ads = max(ads_cols, key=lambda c: df[c].notna().mean())
        ads_unique = int(df[best_ads].dropna().astype(str).nunique())

    exact_dupes = int(df.astype(str).duplicated().sum())
    summary_rows.append({
        "domain": src["domain"], "source": src["source"], "status": "PARSED",
        "sheet": sheet, "sheet_count": len(xls.sheet_names), "rows": len(df), "columns": len(cols),
        "source_column": best or "", "source_nonnull_fraction": source_nonnull,
        "unique_source_values": source_unique, "unique_adsorbent_values": ads_unique,
        "exact_duplicate_rows": exact_dupes,
    })
    source_rows.append({
        "domain": src["domain"], "source": src["source"], "all_columns": " | ".join(map(str, cols)),
        "source_candidate_columns": " | ".join(map(str, source_cols)),
        "best_source_column": best or "", "unique_source_values": source_unique,
    })
    for fam, hits in family_hits.items():
        coverage_rows.append({
            "domain": src["domain"], "source": src["source"], "field_family": fam,
            "matching_columns": " | ".join(map(str, hits)),
            "best_nonnull_fraction": coverage(df, hits),
        })

pd.DataFrame(summary_rows).to_csv(OUT / "dataset_screen.csv", index=False)
pd.DataFrame(source_rows).to_csv(OUT / "source_column_screen.csv", index=False)
pd.DataFrame(coverage_rows).to_csv(OUT / "descriptor_coverage.csv", index=False)
(OUT / "acquisition_log.json").write_text(json.dumps(acquisition, indent=2), encoding="utf-8")

print(pd.DataFrame(summary_rows).to_string(index=False))
print("\nOutputs:", OUT)
