"""Primary-study provenance reconstruction for Liu et al. ammonia-N biochar data.

Paper: Liu et al., npj Clean Water 8, 13 (2025), DOI 10.1038/s41545-024-00429-z.

The paper reports 417 literature-derived observations. The repository linked by the
paper historically contained ``Original.xlsx`` (later deleted). Its ``Full`` sheet
contains 417 rows. The public CatBoost notebook applies ``Q <= 10`` before modelling.
The historical ``Final`` sheet plus that public-code gate deterministically yields the
same 409-row modelling population.

Study IDs below are assigned from row blocks only where both the workbook's ordered
literature ledger and source-specific feedstock/material signatures agree. No unused
literature citation is assigned rows merely because it appears in the workbook.
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
OUT = HERE / "outputs" / "multidataset" / "liu2025_ammonia_primary_provenance"
OUT.mkdir(parents=True, exist_ok=True)

PARENT_COMMIT = "25f525f7e67771367948087f18e6c91ee8fa994f"
RAW_URL = f"https://raw.githubusercontent.com/17609858895/Ammonia-nitrogen/{PARENT_COMMIT}/Original.xlsx"

# Original-sheet 1-based DATA-row ranges (header excluded).
# Source 3 occurs in two separated experiment blocks but is one primary paper.
SOURCE_RULES = [
    ("A01_food_waste", "10.1016/j.biortech.2019.121927", [(1, 64)], "high",
     "Bean dregs / fruit-pericarp biochars match Xue et al. food-waste biochar study."),
    ("A02_CaSSB", "10.1371/journal.pone.0290714", [(65, 78)], "high",
     "Ca-modified soybean-straw biochar; source is present in raw corpus but absent from final model population."),
    ("A03_clay_reed", "10.1007/s11802-020-4150-9", [(79, 84), (404, 409)], "high",
     "Reed-straw/clay-biochar composite; DOI occurs twice in workbook literature ledger and both blocks are merged."),
    ("A04_thalia", "10.1007/s11356-022-19870-z", [(85, 127)], "high",
     "Thalia dealbata biochars at multiple carbonization temperatures."),
    ("A05_feedstock_Gai", "10.1371/journal.pone.0113888", [(128, 223)], "high",
     "Wheat-straw, corn-straw and peanut-shell biochars match Gai et al."),
    ("A06_fruit_peels", "10.1016/j.scitotenv.2019.135544", [(224, 403)], "high",
     "Orange-, pineapple- and pitaya-peel biochars match the comparative fruit-peel study."),
    ("A07_engineered_sludge", "10.1016/j.jclepro.2021.129994", [(410, 417)], "high",
     "BCSSL/BCSSLW labels and N2/CO2 variants match engineered sewage-sludge/willow biochars."),
    ("A08_digested_sludge", "10.1016/j.jclepro.2018.10.268", [(418, 430)], "high",
     "BC450 digested-sludge biochar adsorption series matches Tang et al."),
]

UNUSED_LISTED_SOURCES = [
    "10.1038/s41598-022-08591-5",   # sorghum-straw biochar
    "10.2166/aqua.2020.062",        # mixed wood-chip biochar
    "10.1007/s10653-019-00474-5",   # ball-milled bamboo biochar
]

FEATURE_COLS = ["C", "H/C", "O/C", "(O+N)/C", "Ash", "pH_bio", "BET", "V", "Temp", "pH"]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ranges_contain(rownum: int, ranges: list[tuple[int, int]]) -> bool:
    return any(a <= rownum <= b for a, b in ranges)


def assign_source(rownum: int):
    hits = [(sid, doi, conf, note) for sid, doi, rr, conf, note in SOURCE_RULES if ranges_contain(rownum, rr)]
    if len(hits) != 1:
        raise AssertionError(f"Expected exactly one source for original row {rownum}, got {hits}")
    return hits[0]


def canon(v):
    if pd.isna(v):
        return "<NA>"
    s = str(v).replace("\u202f", "").replace("\xa0", "").strip()
    try:
        return f"{float(s):.8g}"
    except Exception:
        return s


def row_key(row, q_col):
    return tuple(canon(row[c]) for c in ["C", "Ash", "pH_bio", "BET", "V", "Temp", "pH"]) + (canon(row[q_col]),)


def main():
    r = requests.get(RAW_URL, timeout=90)
    r.raise_for_status()
    content = r.content
    if not content.startswith(b"PK"):
        raise AssertionError("Historical workbook retrieval failed")

    original = pd.read_excel(io.BytesIO(content), sheet_name="Original")
    full = pd.read_excel(io.BytesIO(content), sheet_name="Full")
    final = pd.read_excel(io.BytesIO(content), sheet_name="Final")
    lit = pd.read_excel(io.BytesIO(content), sheet_name="Literature collected", header=None)

    assert len(original) == 430, len(original)
    assert len(full) == 417, len(full)
    assert len(final) == 416, len(final)

    # Deterministically establish the Final-sheet lineage. Exact core-feature+Q
    # reconciliation shows Final is Original with rows 65-78 omitted.
    original_rows_for_final = [i for i in range(1, 431) if not 65 <= i <= 78]
    assert len(original_rows_for_final) == 416
    for j, original_rownum in enumerate(original_rows_for_final):
        ko = row_key(original.iloc[original_rownum - 1], "Q")
        kf = row_key(final.iloc[j], "Q(mg/g)")
        if ko != kf:
            raise AssertionError(f"Final/Original row reconciliation failed at final index {j}, original row {original_rownum}: {ko} != {kf}")

    lineage = final.copy()
    lineage.insert(0, "original_data_row_1based", original_rows_for_final)
    assigned = lineage["original_data_row_1based"].apply(assign_source)
    lineage["primary_study_id"] = assigned.apply(lambda x: x[0])
    lineage["primary_doi"] = assigned.apply(lambda x: x[1])
    lineage["provenance_confidence"] = assigned.apply(lambda x: x[2])
    lineage["provenance_note"] = assigned.apply(lambda x: x[3])
    lineage["model_q_gate"] = pd.to_numeric(lineage["Q(mg/g)"], errors="coerce") <= 10.0

    modelled = lineage.loc[lineage["model_q_gate"]].copy().reset_index(drop=True)
    excluded_q = lineage.loc[~lineage["model_q_gate"]].copy()

    # Source A02 was already absent from Final; after the public Q gate the model
    # therefore contains 7 primary studies.
    assert len(modelled) == 409, len(modelled)
    assert modelled["primary_study_id"].nunique() == 7, modelled["primary_study_id"].value_counts()
    assert "A02_CaSSB" not in set(modelled["primary_study_id"])

    counts = (modelled.groupby(["primary_study_id", "primary_doi"], as_index=False)
              .size().rename(columns={"size": "n_model_rows"})
              .sort_values("n_model_rows", ascending=False))
    counts["share"] = counts["n_model_rows"] / len(modelled)

    source_ledger = []
    for sid, doi, ranges, conf, note in SOURCE_RULES:
        n_original = sum(b - a + 1 for a, b in ranges)
        n_final = int((lineage["primary_study_id"] == sid).sum())
        n_model = int((modelled["primary_study_id"] == sid).sum())
        source_ledger.append({
            "primary_study_id": sid,
            "doi": doi,
            "original_row_ranges": ";".join(f"{a}-{b}" for a, b in ranges),
            "confidence": conf,
            "n_original_rows": n_original,
            "n_final_sheet_rows": n_final,
            "n_model_rows_q_le_10": n_model,
            "note": note,
        })
    for doi in UNUSED_LISTED_SOURCES:
        source_ledger.append({
            "primary_study_id": "listed_zero_rows",
            "doi": doi,
            "original_row_ranges": "",
            "confidence": "zero_rows_not_assigned",
            "n_original_rows": 0,
            "n_final_sheet_rows": 0,
            "n_model_rows_q_le_10": 0,
            "note": "Listed in workbook bibliography but no row block was assigned without direct material/row evidence.",
        })

    # Literature list is retained verbatim for audit.
    lit_values = [str(v).strip() for v in lit.iloc[:, 0].dropna() if str(v).strip()]

    lineage.to_csv(OUT / "liu2025_ammonia_final_lineage.csv", index=False)
    modelled.to_csv(OUT / "liu2025_ammonia_model_population_409.csv", index=False)
    excluded_q.to_csv(OUT / "liu2025_ammonia_q_gt10_excluded.csv", index=False)
    counts.to_csv(OUT / "liu2025_ammonia_group_counts.csv", index=False)
    pd.DataFrame(source_ledger).to_csv(OUT / "liu2025_ammonia_source_ledger.csv", index=False)
    pd.DataFrame({"literature_entry": lit_values}).to_csv(OUT / "liu2025_ammonia_literature_list.csv", index=False)

    summary = {
        "doi": "10.1038/s41545-024-00429-z",
        "workbook_sha256": sha256(content),
        "historical_raw_rows": 430,
        "paper_reported_collected_rows": 417,
        "historical_full_sheet_rows": 417,
        "historical_final_sheet_rows": 416,
        "public_code_target_gate": "Q <= 10",
        "matched_model_population_rows": int(len(modelled)),
        "matched_model_primary_studies": int(modelled["primary_study_id"].nunique()),
        "largest_group_rows": int(counts["n_model_rows"].max()),
        "largest_group_share": float(counts["share"].max()),
        "q_gate_exclusions_from_final": int(len(excluded_q)),
        "listed_bibliographic_entries_in_workbook": int(len(lit_values) + 1),
        "contributing_primary_studies_before_model_gate": 8,
        "contributing_primary_studies_after_model_gate": 7,
        "unused_listed_sources_zero_rows": UNUSED_LISTED_SOURCES,
        "v21_doi_overlap": 0,
        "grouping_ready": True,
        "model_run": False,
        "interpretation": "409-row primary matched population follows the executable public-code Q gate; seven primary studies remain."
    }
    (OUT / "liu2025_ammonia_provenance_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print("\nModelled group counts:")
    print(counts.to_string(index=False))
    print("\nQ>10 exclusions:")
    print(excluded_q[["original_data_row_1based", "primary_study_id", "primary_doi", "Q(mg/g)"]].to_string(index=False))


if __name__ == "__main__":
    main()
