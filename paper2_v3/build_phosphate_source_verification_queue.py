"""Build the Paper 2 V3 phosphate primary-source verification queue.

This is metadata triage only. Rows from the compilation are NOT admitted to V3 by
this script. Each primary paper remains PENDING until its data are checked against
the primary article/supplement.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import requests
import pandas as pd

OUT = Path("paper2_v3/outputs/phosphate_source_queue")
OUT.mkdir(parents=True, exist_ok=True)
URL = "https://raw.githubusercontent.com/Sara-Iftikhar/po4_removal_ml/main/scripts/master_sheet_0802.xlsx"
UA = {"User-Agent": "Mozilla/5.0 Paper2-V3-source-queue/1.0"}


def norm_doi(v):
    if pd.isna(v): return None
    s = str(v).strip().lower()
    for p in ["https://doi.org/", "http://doi.org/", "http://dx.doi.org/", "https://dx.doi.org/", "doi:"]:
        s = s.replace(p, "")
    return s.strip() or None

r = requests.get(URL, headers=UA, timeout=90); r.raise_for_status()
df = pd.read_excel(BytesIO(r.content), sheet_name=0).dropna(how="all").reset_index(drop=True)
df["primary_doi"] = df["doi"].map(norm_doi).ffill()
df["source_ref"] = df["ref"].ffill()
df["qe_num"] = pd.to_numeric(df["qe"], errors="coerce")

p1 = ["Feedstock", "Adsorption_time (min)", "Ci_ppm", "solution pH", "loading (g)", "adsorption_temp"]
p2 = ["Feedstock", "Pyrolysis_temp", "Surface area", "Adsorption_time (min)", "Ci_ppm", "solution pH", "loading (g)", "adsorption_temp"]
p3 = ["Feedstock", "Pyrolysis_temp", "C", "O", "Surface area", "Adsorption_time (min)", "Ci_ppm", "solution pH", "loading (g)", "adsorption_temp"]

records = []
for doi, g in df.groupby("primary_doi", sort=False):
    valid_target = g["qe_num"].gt(0)
    rec = {
        "primary_doi": doi,
        "source_ref_from_compilation": str(g["source_ref"].iloc[0]),
        "raw_block_rows": int(len(g)),
        "positive_qe_rows": int(valid_target.sum()),
        "core_process_complete_rows": int((valid_target & g[p1].notna().all(axis=1)).sum()),
        "plus_basic_material_rows": int((valid_target & g[p2].notna().all(axis=1)).sum()),
        "plus_elemental_CO_rows": int((valid_target & g[p3].notna().all(axis=1)).sum()),
        "qe_min_compilation": float(g.loc[valid_target, "qe_num"].min()) if valid_target.any() else None,
        "qe_max_compilation": float(g.loc[valid_target, "qe_num"].max()) if valid_target.any() else None,
        "primary_metadata_verified": "NO",
        "primary_fulltext_or_supplement_checked": "NO",
        "row_values_verified_against_primary": "NO",
        "target_semantics_verified": "NO",
        "units_verified": "NO",
        "duplicate_lineage_checked": "NO",
        "v3_admission_status": "PENDING_PRIMARY_SOURCE_VERIFICATION",
        "verification_notes": "",
    }
    records.append(rec)

q = pd.DataFrame(records)
if len(q) != 70 or q["primary_doi"].nunique() != 70:
    raise RuntimeError(f"Expected 70 unique source blocks, got {len(q)} rows / {q.primary_doi.nunique()} DOIs")
q.to_csv(OUT / "PHOSPHATE_PRIMARY_SOURCE_VERIFICATION_QUEUE_V0.csv", index=False)

summary = pd.DataFrame([{
    "source_blocks": len(q),
    "raw_rows": int(q.raw_block_rows.sum()),
    "positive_qe_rows": int(q.positive_qe_rows.sum()),
    "studies_with_core_process_rows": int((q.core_process_complete_rows > 0).sum()),
    "studies_with_basic_material_rows": int((q.plus_basic_material_rows > 0).sum()),
    "studies_with_elemental_CO_rows": int((q.plus_elemental_CO_rows > 0).sum()),
    "admitted_primary_studies": int((q.v3_admission_status == "ADMITTED").sum()),
}])
summary.to_csv(OUT / "phosphate_source_queue_summary.csv", index=False)
print(summary.to_string(index=False))
print(q[["primary_doi","raw_block_rows","positive_qe_rows","core_process_complete_rows","plus_basic_material_rows","v3_admission_status"]].to_string(index=False))
