"""Export the public Liu et al. 2025 workbook to deterministic CSV evidence.

No study IDs are assigned here and no model is run. This script exposes the exact
public row structure plus the entire literature-collection sheet so provenance can
be reconstructed from bibliographic evidence rather than inferred from material
names alone.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "Biochar_dye_filtered.xlsx"
OUT = Path(__file__).resolve().parent / "outputs" / "multidataset" / "liu2025_full_extract"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    raw = BOOK.read_bytes()
    original = pd.read_excel(BOOK, sheet_name="original")
    processed = pd.read_excel(BOOK, sheet_name="After preprocessing")
    literature = pd.read_excel(BOOK, sheet_name="literature collection", header=None)

    original = original.copy()
    original.insert(0, "excel_row_1based", range(2, len(original) + 2))
    processed = processed.copy()
    processed.insert(0, "excel_row_1based", range(2, len(processed) + 2))
    literature = literature.copy()
    literature.insert(0, "excel_row_1based", range(1, len(literature) + 1))

    original.to_csv(OUT / "liu2025_original_full.csv", index=False)
    processed.to_csv(OUT / "liu2025_after_preprocessing_full.csv", index=False)
    literature.to_csv(OUT / "liu2025_literature_collection_full.csv", index=False)

    summary = {
        "workbook_sha256": hashlib.sha256(raw).hexdigest(),
        "original_rows": len(original),
        "processed_rows": len(processed),
        "literature_sheet_rows": len(literature),
        "original_columns": list(original.columns),
        "processed_columns": list(processed.columns),
        "model_run": False,
        "study_ids_assigned": False,
    }
    (OUT / "liu2025_full_extract_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("\nLiterature collection sheet:\n")
    print(literature.to_string(index=False))

if __name__ == "__main__":
    main()
