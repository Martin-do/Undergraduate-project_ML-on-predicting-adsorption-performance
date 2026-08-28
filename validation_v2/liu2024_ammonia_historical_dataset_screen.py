"""Recover and screen the historical raw workbook for Liu et al. ammonia-N study.

Paper
-----
Machine learning prediction of ammonia nitrogen adsorption on biochar with model
evaluation and optimization. npj Clean Water (2024), DOI 10.1038/s41545-024-00429-z.

The paper links https://github.com/17609858895/Ammonia-nitrogen and states that raw
data are available there. The current repository omits the raw workbook. Git history
shows commit 6905f8e047ad865216d17b4c7ad052d3fd3bb2be explicitly deleted
Original.xlsx. This script recovers the exact previous blob from parent commit
25f525f7e67771367948087f18e6c91ee8fa994f and performs a provenance-readiness
screen. It does NOT assign study IDs and does NOT run models.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import io
import json
import re

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "multidataset" / "liu2024_ammonia_historical_screen"
OUT.mkdir(parents=True, exist_ok=True)

PARENT_COMMIT = "25f525f7e67771367948087f18e6c91ee8fa994f"
DELETED_BLOB_SHA = "43a5e4aea00e62c4e1df8a62f902048338027206"
RAW_URL = f"https://raw.githubusercontent.com/17609858895/Ammonia-nitrogen/{PARENT_COMMIT}/Original.xlsx"

SOURCE_PAT = re.compile(r"source|reference|ref\b|doi|paper|study|article|citation|literature", re.I)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def normalise(v):
    if pd.isna(v):
        return "<NA>"
    if isinstance(v, (float, np.floating)):
        return f"{float(v):.12g}"
    return str(v).strip()


def contiguous_blocks(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if not cols or df.empty:
        return pd.DataFrame()
    sigs = df[cols].apply(lambda r: "||".join(normalise(v) for v in r), axis=1)
    out = []
    start = 0
    sig_list = sigs.tolist()
    for i in range(1, len(sig_list) + 1):
        if i == len(sig_list) or sig_list[i] != sig_list[start]:
            out.append({
                "block_id": len(out) + 1,
                "start_data_row_1based": start + 1,
                "end_data_row_1based": i,
                "n_rows": i - start,
                "signature": sig_list[start],
            })
            start = i
    return pd.DataFrame(out)


def main():
    r = requests.get(RAW_URL, timeout=90)
    r.raise_for_status()
    content = r.content
    if not content.startswith(b"PK"):
        raise AssertionError("Historical object is not an XLSX/ZIP container")
    (OUT / "Original_historical.xlsx").write_bytes(content)

    book = pd.ExcelFile(io.BytesIO(content))
    sheet_records = []
    source_candidates = []

    for sheet in book.sheet_names:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet)
        df.to_csv(OUT / f"sheet_{re.sub(r'[^A-Za-z0-9_.-]+', '_', sheet)}.csv", index=False)
        source_cols = [str(c) for c in df.columns if SOURCE_PAT.search(str(c))]
        sheet_records.append({
            "sheet": sheet,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": "|".join(map(str, df.columns)),
            "source_like_columns": "|".join(source_cols),
        })
        for col in source_cols:
            s = df[col]
            source_candidates.append({
                "sheet": sheet,
                "column": col,
                "non_null": int(s.notna().sum()),
                "unique_non_null": int(s.dropna().astype(str).nunique()),
                "examples": " || ".join(s.dropna().astype(str).drop_duplicates().head(12).tolist()),
            })

        # If this looks like a modelling table, create a conservative exact-signature
        # profile from low-cardinality feature combinations. This helps detect source
        # concatenation but is never promoted to a study ID without bibliography.
        if len(df) >= 100:
            nunique = df.nunique(dropna=True)
            candidate_cols = [str(c) for c in df.columns if 1 < nunique[c] <= 80]
            # Exclude likely target/capacity fields and obvious row identifiers.
            candidate_cols = [c for c in candidate_cols if not re.search(r"^(q|qe|target|y|id)$|capacity", c, re.I)]
            # Prefer material-property columns whose values repeat across experiment rows.
            chosen = candidate_cols[:8]
            if chosen:
                blocks = contiguous_blocks(df, chosen)
                blocks.to_csv(OUT / f"blocks_{re.sub(r'[^A-Za-z0-9_.-]+', '_', sheet)}.csv", index=False)

    pd.DataFrame(sheet_records).to_csv(OUT / "workbook_sheet_inventory.csv", index=False)
    pd.DataFrame(source_candidates).to_csv(OUT / "source_column_candidates.csv", index=False)

    summary = {
        "doi": "10.1038/s41545-024-00429-z",
        "historical_parent_commit": PARENT_COMMIT,
        "deleted_blob_sha": DELETED_BLOB_SHA,
        "historical_raw_url": RAW_URL,
        "workbook_sha256": sha256(content),
        "workbook_bytes": len(content),
        "sheet_names": book.sheet_names,
        "sheet_inventory": sheet_records,
        "explicit_source_like_columns_found": bool(source_candidates),
        "source_candidates": source_candidates,
        "model_run": False,
        "study_ids_assigned": False,
        "next_gate": "If explicit row-level source identity is absent, reconstruct groups only from primary bibliographic evidence plus deterministic row/block signatures."
    }
    (OUT / "screen_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

    # Print bounded previews for reproducible inspection in CI logs.
    for sheet in book.sheet_names:
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet)
        print(f"\n--- SHEET {sheet!r}: shape={df.shape} ---")
        print("columns:", list(df.columns))
        print(df.head(12).to_string(index=True))
        if len(df) > 12:
            print("... tail ...")
            print(df.tail(8).to_string(index=True))


if __name__ == "__main__":
    main()
