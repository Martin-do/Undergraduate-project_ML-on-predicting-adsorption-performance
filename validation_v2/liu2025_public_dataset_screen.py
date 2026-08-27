"""Deterministic screening of the public Liu et al. 2025 biochar/dye workbook.

This script does NOT perform study-aware modelling. Its sole purpose is to establish
whether a defensible grouping variable exists in the public workbook and to export
information needed for provenance reconstruction before any grouped outcomes are
observed.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "outputs" / "multidataset" / "liu2025_screen"
OUT.mkdir(parents=True, exist_ok=True)
WORKBOOK = ROOT / "Biochar_dye_filtered.xlsx"

SOURCE_PAT = re.compile(r"(source|reference|ref\b|doi|literature|citation|paper|study|author)", re.I)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_col(x) -> str:
    return str(x).strip().replace("\n", " ")


def nonempty_count(s: pd.Series) -> int:
    return int(s.notna().sum())


def main() -> None:
    xls = pd.ExcelFile(WORKBOOK)
    inventory = []
    candidate_rows = []
    sheet_details = {}

    for sheet in xls.sheet_names:
        # Use ordinary header first; the literature sheet is also read raw later.
        df = pd.read_excel(WORKBOOK, sheet_name=sheet)
        cols = [clean_col(c) for c in df.columns]
        inventory.append({
            "sheet": sheet,
            "rows": int(len(df)),
            "columns": int(df.shape[1]),
            "column_names": " | ".join(cols),
        })
        candidates = [c for c in cols if SOURCE_PAT.search(c)]
        for c in candidates:
            candidate_rows.append({
                "sheet": sheet,
                "candidate_column": c,
                "reason": "column name matches source/reference/study pattern",
            })
        sheet_details[sheet] = {
            "rows": int(len(df)),
            "columns": cols,
            "candidate_source_columns": candidates,
        }

    pd.DataFrame(inventory).to_csv(OUT / "liu2025_sheet_inventory.csv", index=False)
    pd.DataFrame(candidate_rows, columns=["sheet", "candidate_column", "reason"]).to_csv(
        OUT / "liu2025_candidate_source_columns.csv", index=False
    )

    # Preserve the literature collection exactly as tabular values for later manual/
    # bibliographic reconciliation. No row mapping is inferred here.
    lit = pd.read_excel(WORKBOOK, sheet_name="literature collection", header=None)
    lit.to_csv(OUT / "liu2025_literature_collection_raw.csv", index=False, header=False)

    nonempty_lit_rows = []
    for i, row in lit.iterrows():
        vals = [str(v).strip() for v in row.tolist() if pd.notna(v) and str(v).strip()]
        if vals:
            nonempty_lit_rows.append({"row": int(i), "text": " | ".join(vals)})
    pd.DataFrame(nonempty_lit_rows).to_csv(OUT / "liu2025_literature_entries_flat.csv", index=False)

    # Inspect modelling sheets for explicit source/provenance fields.
    row_level_sheets = [s for s in ["original", "After preprocessing"] if s in xls.sheet_names]
    row_level_source_columns = {}
    for sheet in row_level_sheets:
        df = pd.read_excel(WORKBOOK, sheet_name=sheet)
        cols = [clean_col(c) for c in df.columns]
        row_level_source_columns[sheet] = [c for c in cols if SOURCE_PAT.search(c)]

    # Export a compact profile of the original sheet to help identify repeat material
    # signatures without declaring them to be primary studies.
    orig_profile = None
    if "original" in xls.sheet_names:
        orig = pd.read_excel(WORKBOOK, sheet_name="original")
        orig.columns = [clean_col(c) for c in orig.columns]
        profile = []
        for c in orig.columns:
            profile.append({
                "column": c,
                "nonempty": nonempty_count(orig[c]),
                "unique_nonempty": int(orig[c].dropna().nunique()),
                "dtype": str(orig[c].dtype),
            })
        pd.DataFrame(profile).to_csv(OUT / "liu2025_original_column_profile.csv", index=False)
        orig_profile = profile

        # Candidate quasi-static material descriptors. This is diagnostic only.
        fixed_candidates = [
            c for c in ["C", "H/C", "(O + N)/C", "(O+N)/C", "O/H", "BET", "D", "PV", "pHpzc", "pH_pzc"]
            if c in orig.columns
        ]
        if fixed_candidates:
            sig = orig[fixed_candidates].astype("string").fillna("<NA>").agg("||".join, axis=1)
            counts = sig.value_counts(dropna=False).rename_axis("material_signature").reset_index(name="rows")
            counts.to_csv(OUT / "liu2025_material_signature_counts.csv", index=False)

    explicit_row_level_source = any(bool(v) for v in row_level_source_columns.values())
    summary = {
        "workbook": WORKBOOK.name,
        "sha256": sha256(WORKBOOK),
        "sheets": xls.sheet_names,
        "sheet_details": sheet_details,
        "row_level_source_columns": row_level_source_columns,
        "explicit_row_level_source_identifier_found": explicit_row_level_source,
        "literature_collection_nonempty_rows": len(nonempty_lit_rows),
        "grouping_ready_for_primary_study_cv": False,
        "grouping_gate_reason": (
            "Explicit row-level source field found but still requires semantic verification."
            if explicit_row_level_source
            else "No explicit row-level source/study field found in modelling sheets; provenance reconstruction required before grouped CV."
        ),
        "warning": "Material signatures are diagnostics only and must not be treated as primary-study IDs without bibliographic evidence.",
    }
    (OUT / "liu2025_workbook_screen_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== LIU 2025 PUBLIC WORKBOOK SCREEN ===")
    print(json.dumps(summary, indent=2))
    print("\n=== LITERATURE COLLECTION (NONEMPTY ROWS) ===")
    for row in nonempty_lit_rows:
        print(f"[{row['row']}] {row['text']}")
    if orig_profile is not None:
        print("\n=== ORIGINAL SHEET COLUMN PROFILE ===")
        for item in orig_profile:
            print(f"{item['column']}: nonempty={item['nonempty']}, unique={item['unique_nonempty']}, dtype={item['dtype']}")


if __name__ == "__main__":
    main()
