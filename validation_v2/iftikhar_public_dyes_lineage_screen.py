"""Screen the public Iftikhar et al. Dyes workbook for Moosavi-lineage rows.

Purpose: Moosavi et al. 2021 Table S1's distributed PDF omits numbered rows 340-345,
which correspond to Reference 12 (tea-waste activated carbon / Basic Violet-14).
The Iftikhar public repository contains a `Dyes data.xlsx` workbook and its code
explicitly drops a `Ref` column before modelling. This script checks whether that
public workbook retains the missing rows or other exact Moosavi lineage records.

No rows are added to any canonical dataset here. This is a provenance screen only.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "multidataset" / "iftikhar_lineage_screen"
OUT.mkdir(parents=True, exist_ok=True)

URL = "https://raw.githubusercontent.com/Sara-Iftikhar/ai4adsorption/main/scripts/Dyes%20data.xlsx"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def norm_col(s: str) -> str:
    return " ".join(str(s).strip().lower().replace("_", " ").split())


def find_col(df: pd.DataFrame, *needles: str):
    mapping = {norm_col(c): c for c in df.columns}
    for n in needles:
        nn = norm_col(n)
        if nn in mapping:
            return mapping[nn]
    for key, original in mapping.items():
        if all(piece in key for piece in needles):
            return original
    return None


def main():
    r = requests.get(URL, timeout=90)
    r.raise_for_status()
    b = r.content
    sha = sha256_bytes(b)
    book = OUT / "Dyes_data_Iftikhar_public.xlsx"
    book.write_bytes(b)

    xl = pd.ExcelFile(book)
    inventory = []
    matches = []
    for sheet in xl.sheet_names:
        df = pd.read_excel(book, sheet_name=sheet)
        inventory.append({"sheet": sheet, "rows": len(df), "columns": "|".join(map(str, df.columns))})

        ads_col = find_col(df, "adsorbent")
        ref_col = find_col(df, "ref") or find_col(df, "reference")
        dye_col = find_col(df, "pollutant") or find_col(df, "dye")
        if ads_col is None:
            continue

        ads = df[ads_col].astype("string").str.strip().str.upper()
        wanted = ads.isin(["TWAC", "CS"])
        if wanted.any():
            sub = df.loc[wanted].copy()
            sub.insert(0, "__sheet", sheet)
            sub.insert(1, "__source_row_1based", sub.index + 2)
            matches.append(sub)

        # Also screen by reference/source strings that mention Moosavi or the primary papers.
        if ref_col is not None:
            refs = df[ref_col].astype("string")
            wanted_ref = refs.str.contains("Moosavi|Lu|Rani|2011|2015", case=False, na=False)
            if wanted_ref.any():
                sub = df.loc[wanted_ref].copy()
                sub.insert(0, "__sheet", sheet)
                sub.insert(1, "__source_row_1based", sub.index + 2)
                matches.append(sub)

    inv = pd.DataFrame(inventory)
    inv.to_csv(OUT / "iftikhar_dyes_workbook_inventory.csv", index=False)
    combined = pd.concat(matches, ignore_index=True, sort=False).drop_duplicates() if matches else pd.DataFrame()
    combined.to_csv(OUT / "iftikhar_moosavi_lineage_candidate_rows.csv", index=False)

    summary = {
        "source_url": URL,
        "sha256": sha,
        "sheets": xl.sheet_names,
        "candidate_rows": int(len(combined)),
        "model_run": False,
        "canonical_dataset_modified": False,
        "purpose": "Recover or corroborate Moosavi Table-S1 provenance, especially source-PDF-missing Reference-12 rows 340-345.",
    }
    (OUT / "iftikhar_lineage_screen_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("\nWorkbook inventory:\n", inv.to_string(index=False))
    if not combined.empty:
        print("\nCandidate lineage rows:\n", combined.to_string(index=False))


if __name__ == "__main__":
    main()
