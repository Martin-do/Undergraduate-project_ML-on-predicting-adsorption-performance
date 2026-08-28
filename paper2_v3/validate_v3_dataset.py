"""Pre-modelling validation gate for Paper 2 / V3 datasets.

This script enforces provenance, target, duplicate and predictor-safety rules before
any model is permitted to consume a curated V3 CSV.

Usage:
    python paper2_v3/validate_v3_dataset.py paper2_v3/adsorption_v3_template.csv

The empty template is expected to pass schema checks. A populated dataset must also
pass row-level scientific integrity checks.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import pandas as pd

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "DATASET_SCHEMA_V3.csv"

PROVENANCE_REQUIRED_FOR_INCLUDED = {
    "record_id",
    "primary_study_id",
    "source_title",
    "source_year",
    "extraction_method",
    "extraction_confidence",
    "provenance_confidence",
    "duplicate_status",
    "inclusion_status",
}

PRIMARY_REQUIRED_FOR_INCLUDED = {
    "adsorbent_name",
    "precursor_name",
    "precursor_class",
    "material_class",
    "adsorbate_name",
    "adsorbate_class",
    "initial_concentration_mg_l",
    "adsorbent_dose_g_l",
    "ph",
    "temperature_c",
    "contact_time_min",
    "experiment_mode",
    "equilibrium_status",
    "qe_mg_g",
    "qe_derivation",
    "raw_unit_qe",
}

PROHIBITED_PREDICTOR_FIELDS = {
    "record_id",
    "primary_study_id",
    "lineage_cluster_id",
    "source_doi",
    "source_title",
    "source_year",
    "source_table_figure",
    "source_row_label",
    "extraction_method",
    "extraction_confidence",
    "provenance_confidence",
    "duplicate_status",
    "inclusion_status",
    "exclusion_reason",
    "qe_mg_g",
    "removal_percent",
    "qmax_langmuir_mg_g",
    "qe_derivation",
    "raw_unit_qe",
    "unit_conversion_note",
    "study_row_count",
    "study_share_primary_population",
    "notes",
}


def fail(errors: list[str]) -> None:
    for e in errors:
        print(f"ERROR: {e}")
    raise SystemExit(1)


def validate_schema(df: pd.DataFrame) -> list[str]:
    schema = pd.read_csv(SCHEMA)
    expected = schema["field_name"].astype(str).tolist()
    missing = [c for c in expected if c not in df.columns]
    unexpected = [c for c in df.columns if c not in expected]
    errors = []
    if missing:
        errors.append(f"Missing schema columns: {missing}")
    if unexpected:
        errors.append(f"Unexpected columns not registered in DATASET_SCHEMA_V3.csv: {unexpected}")
    return errors


def validate_rows(df: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    if df.empty:
        return errors

    if df["record_id"].isna().any() or (df["record_id"].astype(str).str.strip() == "").any():
        errors.append("record_id must be populated for every row")
    if df["record_id"].duplicated().any():
        dups = df.loc[df["record_id"].duplicated(keep=False), "record_id"].astype(str).unique().tolist()
        errors.append(f"Duplicate record_id values found: {dups[:20]}")

    allowed_status = {"include", "exclude", "sensitivity"}
    bad_status = set(df["inclusion_status"].dropna().astype(str)) - allowed_status
    if bad_status:
        errors.append(f"Invalid inclusion_status values: {sorted(bad_status)}")

    included = df[df["inclusion_status"].astype(str) == "include"].copy()
    if included.empty:
        return errors

    for col in sorted(PROVENANCE_REQUIRED_FOR_INCLUDED | PRIMARY_REQUIRED_FOR_INCLUDED):
        if included[col].isna().any() or (included[col].astype(str).str.strip() == "").any():
            n = int((included[col].isna() | (included[col].astype(str).str.strip() == "")).sum())
            errors.append(f"Included rows contain {n} missing/blank values in required field {col}")

    qe = pd.to_numeric(included["qe_mg_g"], errors="coerce")
    if qe.isna().any():
        errors.append("Included qe_mg_g values must be numeric")
    if (qe < 0).any():
        errors.append("Included qe_mg_g contains negative values")

    for col in ["initial_concentration_mg_l", "adsorbent_dose_g_l", "contact_time_min"]:
        vals = pd.to_numeric(included[col], errors="coerce")
        if vals.isna().any():
            errors.append(f"Included {col} values must be numeric")
        if (vals <= 0).any():
            errors.append(f"Included {col} must be > 0")

    ph = pd.to_numeric(included["ph"], errors="coerce")
    if ph.isna().any() or ((ph < 0) | (ph > 14)).any():
        errors.append("Included pH values must be numeric and within 0-14")

    temp = pd.to_numeric(included["temperature_c"], errors="coerce")
    if temp.isna().any():
        errors.append("Included temperature_c values must be numeric")

    if included["primary_study_id"].nunique() < 2:
        errors.append("At least two primary studies are required for grouped validation")

    duplicate_bad = included["duplicate_status"].astype(str).isin({"exact_duplicate"})
    if duplicate_bad.any():
        errors.append("Rows marked exact_duplicate cannot have inclusion_status=include")

    unresolved_prov = included["provenance_confidence"].astype(str).str.lower().eq("low")
    if unresolved_prov.any():
        errors.append("Low-confidence provenance rows cannot enter the primary included population")

    return errors


def validate_predictor_manifest(path: Path | None) -> list[str]:
    if path is None:
        return []
    manifest = pd.read_csv(path)
    if "feature" not in manifest.columns:
        return ["Predictor manifest must contain a 'feature' column"]
    features = set(manifest["feature"].dropna().astype(str))
    prohibited = sorted(features & PROHIBITED_PREDICTOR_FIELDS)
    if prohibited:
        return [f"Prohibited source/target/audit fields included as predictors: {prohibited}"]
    return []


def summary(df: pd.DataFrame) -> None:
    print(f"Rows: {len(df)}")
    if len(df) == 0:
        print("Empty schema template: row-level checks skipped.")
        return
    included = df[df["inclusion_status"].astype(str) == "include"]
    print(f"Included rows: {len(included)}")
    if len(included):
        counts = included.groupby("primary_study_id").size().sort_values(ascending=False)
        print(f"Primary studies: {len(counts)}")
        print(f"Largest-study share: {counts.iloc[0] / len(included):.3f}")
        if counts.iloc[0] / len(included) > 0.20:
            print("WARNING: largest-study share exceeds the 20% planning target; dominant-study sensitivity will be mandatory.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset", type=Path)
    ap.add_argument("--predictors", type=Path, default=None, help="Optional CSV containing a 'feature' column")
    args = ap.parse_args()

    df = pd.read_csv(args.dataset)
    errors = []
    errors.extend(validate_schema(df))
    if not errors:
        errors.extend(validate_rows(df))
    errors.extend(validate_predictor_manifest(args.predictors))

    if errors:
        fail(errors)

    summary(df)
    print("V3 DATA GATE: PASS")


if __name__ == "__main__":
    main()
