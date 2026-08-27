"""Audit Liu et al. 2025 preprocessing sheets and the two distinct 17-row issues.

The article states that 17 observations with Q > 4 mmol/g were removed, producing
668 modelling rows from 685 collected observations. The public workbook also has
side lookup tables that can extend the Excel used range. This audit separates
actual left-table adsorption observations from right-side lookup spillover and
profiles Q at each preprocessing stage. No model and no study grouping is run.
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "Biochar_dye_filtered.xlsx"
OUT = Path(__file__).resolve().parent / "outputs" / "multidataset" / "liu2025_preprocessing_lineage"
OUT.mkdir(parents=True, exist_ok=True)

SHEETS = ["original", "pre_Free-ASH", "pre_D_filled", "molar_ratio", "PRE_KNN_filled", "After preprocessing"]


def q_profile(df, sheet):
    qcols = [c for c in df.columns if str(c).strip().lower() in {"q", "qe", "adsorption"}]
    rec = {"sheet": sheet, "pandas_rows": len(df), "columns": "|".join(map(str, df.columns)), "q_columns": "|".join(map(str, qcols))}
    if qcols:
        q = pd.to_numeric(df[qcols[0]], errors="coerce")
        rec.update({
            "q_nonnull": int(q.notna().sum()),
            "q_gt4": int((q > 4).sum()),
            "q_max": float(q.max()) if q.notna().any() else None,
            "q_gt4_row_numbers_excel": "|".join(str(i+2) for i in q.index[q > 4].tolist()),
        })
    return rec


def main():
    profiles=[]
    tail_records=[]
    for sheet in SHEETS:
        df=pd.read_excel(BOOK, sheet_name=sheet)
        profiles.append(q_profile(df, sheet))
        # Preserve rows around the logical 668-row boundary for diagnosis.
        sub=df.iloc[max(0, 660):].copy()
        sub.insert(0, "__sheet", sheet)
        sub.insert(1, "__excel_row_1based", [i+2 for i in sub.index])
        tail_records.append(sub)
    prof=pd.DataFrame(profiles)
    prof.to_csv(OUT / "liu2025_preprocessing_sheet_profiles.csv", index=False)
    pd.concat(tail_records, ignore_index=True, sort=False).to_csv(OUT / "liu2025_preprocessing_tail_rows.csv", index=False)

    # Logical model table in After preprocessing: infer the contiguous numeric
    # left-table region beginning at row 2. Rows after a nonnumeric entry in a
    # column expected to be numeric are treated only as a structural diagnostic,
    # not automatically as observations.
    post=pd.read_excel(BOOK, sheet_name="After preprocessing")
    expected_numeric=list(post.columns)
    numeric_mask=pd.Series(True, index=post.index)
    for c in expected_numeric:
        numeric_mask &= pd.to_numeric(post[c], errors="coerce").notna()
    first_bad = int(np.where(~numeric_mask.to_numpy())[0][0]) if (~numeric_mask).any() else None

    summary={
        "article_collected_rows": 685,
        "article_outliers_removed_q_gt4": 17,
        "article_model_rows": 668,
        "after_preprocessing_pandas_rows": len(post),
        "after_preprocessing_all_rows_numeric": bool(numeric_mask.all()),
        "first_nonnumeric_row_zero_based": first_bad,
        "note": "A 685-row pandas read does not by itself prove 685 modelling observations because the workbook contains auxiliary lookup content. Compare the exact preprocessing stages and model code before assigning provenance.",
        "model_run": False,
        "study_ids_assigned": False,
    }
    (OUT / "liu2025_preprocessing_lineage_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(prof.to_string(index=False))
    print("\n"+json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
