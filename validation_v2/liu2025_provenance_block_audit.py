"""Deterministic provenance-block audit for Liu et al. 2025 public workbook.

This script does NOT assign primary-study IDs. It profiles contiguous blocks and
material signatures in the modelling sheets to determine whether row-to-source
mapping can be reconstructed from bibliographic evidence without guessing.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "Biochar_dye_filtered.xlsx"
OUT = Path(__file__).resolve().parent / "outputs" / "multidataset" / "liu2025_provenance_blocks"
OUT.mkdir(parents=True, exist_ok=True)

MATERIAL_COLS = ["pH_pzc", "C", "H/C", "O/C", "(O+N)/C", "BET", "PV", "D"]
EXPERIMENT_COLS = ["T", "pH_sol", "C0", "TypeDye"]


def norm(v):
    if pd.isna(v):
        return "<NA>"
    if isinstance(v, (float, np.floating)):
        return f"{float(v):.12g}"
    return str(v).strip()


def signature(row, cols):
    return "||".join(norm(row[c]) for c in cols)


def extract_doi(text: str) -> str | None:
    m = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.I)
    return m.group(0).rstrip(".)]").lower() if m else None


def contiguous_blocks(df: pd.DataFrame, sig_col: str) -> pd.DataFrame:
    sig = df[sig_col].tolist()
    rows = []
    start = 0
    block_id = 1
    for i in range(1, len(sig) + 1):
        if i == len(sig) or sig[i] != sig[start]:
            sub = df.iloc[start:i]
            rows.append({
                "block_id": block_id,
                "start_row_1based": start + 2,  # Excel header in row 1
                "end_row_1based": i + 1,
                "n_rows": i - start,
                "material_signature": sig[start],
                "n_dyes": int(sub["TypeDye"].nunique(dropna=True)) if "TypeDye" in sub else np.nan,
                "dyes": "|".join(sorted(sub["TypeDye"].dropna().astype(str).unique())) if "TypeDye" in sub else "",
                "n_C0": int(sub["C0"].nunique(dropna=True)) if "C0" in sub else np.nan,
                "q_min": float(pd.to_numeric(sub["Q"], errors="coerce").min()) if "Q" in sub else np.nan,
                "q_max": float(pd.to_numeric(sub["Q"], errors="coerce").max()) if "Q" in sub else np.nan,
            })
            block_id += 1
            start = i
    return pd.DataFrame(rows)


def main():
    raw = BOOK.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    orig = pd.read_excel(BOOK, sheet_name="original")
    pre = pd.read_excel(BOOK, sheet_name="After preprocessing")
    lit = pd.read_excel(BOOK, sheet_name="literature collection", header=None)

    missing = [c for c in MATERIAL_COLS if c not in orig.columns]
    if missing:
        raise ValueError(f"Missing expected material columns: {missing}")

    orig = orig.copy()
    orig["material_signature"] = orig.apply(lambda r: signature(r, MATERIAL_COLS), axis=1)
    blocks = contiguous_blocks(orig, "material_signature")
    blocks.to_csv(OUT / "liu2025_contiguous_material_blocks.csv", index=False)

    sig_counts = (orig.groupby("material_signature", dropna=False)
                  .agg(rows=("Q", "size"), n_dyes=("TypeDye", "nunique"), q_min=("Q", "min"), q_max=("Q", "max"))
                  .reset_index().sort_values(["rows", "material_signature"], ascending=[False, True]))
    sig_counts.to_csv(OUT / "liu2025_material_signature_summary.csv", index=False)

    # A second signature excludes D (which may be derived/filled) to quantify
    # whether material identity is robust to that field.
    cols_no_d = [c for c in MATERIAL_COLS if c != "D"]
    orig["material_signature_no_D"] = orig.apply(lambda r: signature(r, cols_no_d), axis=1)
    sig_no_d = (orig.groupby("material_signature_no_D", dropna=False)
                .agg(rows=("Q", "size"), n_dyes=("TypeDye", "nunique"))
                .reset_index().sort_values("rows", ascending=False))
    sig_no_d.to_csv(OUT / "liu2025_material_signature_no_D_summary.csv", index=False)

    # Flatten DOI list exactly as retained in the workbook.
    entries = []
    for excel_row, val in enumerate(lit.iloc[:, 0].tolist(), start=1):
        if pd.notna(val) and str(val).strip():
            text = str(val).strip()
            entries.append({"literature_sheet_row": excel_row, "text": text, "doi": extract_doi(text)})
    lit_df = pd.DataFrame(entries)
    lit_df.to_csv(OUT / "liu2025_literature_dois.csv", index=False)

    # Profile row-order transitions, useful for testing whether primary studies
    # were concatenated in source order. No study assignment is made here.
    transitions = []
    prev = None
    for idx, row in orig.iterrows():
        sig = row["material_signature"]
        if sig != prev:
            transitions.append({
                "excel_row_1based": idx + 2,
                "material_signature": sig,
                "TypeDye": row.get("TypeDye"),
                "Q": row.get("Q"),
                "C0": row.get("C0"),
            })
            prev = sig
    pd.DataFrame(transitions).to_csv(OUT / "liu2025_signature_transitions.csv", index=False)

    summary = {
        "workbook_sha256": sha,
        "original_rows": int(len(orig)),
        "after_preprocessing_rows": int(len(pre)),
        "listed_primary_dois": int(lit_df["doi"].notna().sum()),
        "unique_material_signatures": int(orig["material_signature"].nunique(dropna=False)),
        "unique_material_signatures_no_D": int(orig["material_signature_no_D"].nunique(dropna=False)),
        "contiguous_material_blocks": int(len(blocks)),
        "material_signature_reappears_noncontiguously": bool((blocks.groupby("material_signature").size() > 1).any()),
        "max_blocks_for_one_signature": int(blocks.groupby("material_signature").size().max()),
        "grouping_ready": False,
        "reason": "This audit profiles candidate blocks only; primary-study IDs require bibliographic confirmation.",
    }
    (OUT / "liu2025_provenance_block_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("\nTop contiguous blocks:")
    print(blocks.head(50).to_string(index=False))


if __name__ == "__main__":
    main()
