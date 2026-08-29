"""Integrity gate for the Paper 2 / V3 primary-verified phosphate staging ledger.

This is deliberately NOT a modelling-release gate. It validates that rows already
placed in PHOSPHATE_V3_PRIMARY_VERIFIED_STAGING.csv are internally coherent,
primary-source traceable, holdout-safe and still quarantined from model training.

It writes deterministic audit outputs but never trains a model or changes a row's
inclusion status.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
STAGING = HERE / "PHOSPHATE_V3_PRIMARY_VERIFIED_STAGING.csv"
SCHEMA = HERE / "DATASET_SCHEMA_V3.csv"
HOLDOUT = HERE / "PHOSPHATE_EXTERNAL_HOLDOUT_REGISTRY_V0.csv"
OUT = HERE / "outputs" / "phosphate_verified_staging_gate"

REQUIRED_STAGING_FIELDS = {
    "record_id",
    "primary_study_id",
    "source_doi",
    "source_title",
    "source_year",
    "source_table_figure",
    "extraction_method",
    "extraction_confidence",
    "provenance_confidence",
    "duplicate_status",
    "inclusion_status",
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
    "study_row_count",
    "study_share_primary_population",
}

ALLOWED_DERIVATIONS = {"reported", "calculated_from_mass_balance", "other"}


def normalize_doi(v: object) -> str:
    if pd.isna(v):
        return ""
    s = str(v).strip().lower()
    for prefix in (
        "https://doi.org/", "http://doi.org/",
        "https://dx.doi.org/", "http://dx.doi.org/", "doi:"
    ):
        s = s.replace(prefix, "")
    return s.strip()


def blank_mask(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().eq("")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    for p in (STAGING, SCHEMA, HOLDOUT):
        if not p.exists():
            errors.append(f"Required gate input missing: {p}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        raise SystemExit(1)

    df = pd.read_csv(STAGING)
    schema = pd.read_csv(SCHEMA)
    registry = pd.read_csv(HOLDOUT)

    expected_cols = schema["field_name"].astype(str).tolist()
    missing_cols = [c for c in expected_cols if c not in df.columns]
    unexpected_cols = [c for c in df.columns if c not in expected_cols]
    if missing_cols:
        errors.append(f"Staging file is missing schema columns: {missing_cols}")
    if unexpected_cols:
        errors.append(f"Staging file has unregistered schema columns: {unexpected_cols}")

    if df.empty:
        errors.append("Primary-verified staging ledger must not be empty")

    if not errors:
        # This ledger is a quarantine layer. It must not silently become a modelling dataset.
        bad_status = sorted(set(df["inclusion_status"].dropna().astype(str)) - {"sensitivity"})
        if bad_status:
            errors.append(
                "Staging ledger may contain only inclusion_status=sensitivity before lineage/population freeze; "
                f"found {bad_status}"
            )

        for col in sorted(REQUIRED_STAGING_FIELDS):
            if blank_mask(df[col]).any():
                errors.append(f"Required staging field {col} has {int(blank_mask(df[col]).sum())} blank/missing value(s)")

        if df["record_id"].duplicated().any():
            dup_ids = df.loc[df["record_id"].duplicated(keep=False), "record_id"].astype(str).unique().tolist()
            errors.append(f"Duplicate record_id values: {dup_ids}")

        # Source identity and confidence.
        doi_norm = df["source_doi"].map(normalize_doi)
        if doi_norm.eq("").any():
            errors.append("Every staging row must have a resolvable primary DOI")
        if df["provenance_confidence"].astype(str).str.lower().eq("low").any():
            errors.append("Low-confidence provenance is not allowed in primary-verified staging")
        if df["extraction_confidence"].astype(str).str.lower().eq("low").any():
            errors.append("Low-confidence extraction is not allowed in primary-verified staging")
        if df["duplicate_status"].astype(str).eq("exact_duplicate").any():
            errors.append("exact_duplicate rows are not allowed in primary-verified staging")

        derivations = set(df["qe_derivation"].dropna().astype(str))
        if not derivations.issubset(ALLOWED_DERIVATIONS):
            errors.append(f"Unexpected qe_derivation values: {sorted(derivations - ALLOWED_DERIVATIONS)}")

        # Numeric/semantic integrity of the experimentally conditioned target.
        positive_fields = [
            "qe_mg_g", "initial_concentration_mg_l", "adsorbent_dose_g_l", "contact_time_min"
        ]
        for col in positive_fields:
            vals = pd.to_numeric(df[col], errors="coerce")
            if vals.isna().any():
                errors.append(f"{col} must be numeric for every staging row")
            elif (vals <= 0).any():
                errors.append(f"{col} must be > 0 for every staging row")

        ph = pd.to_numeric(df["ph"], errors="coerce")
        if ph.isna().any() or ((ph < 0) | (ph > 14)).any():
            errors.append("pH must be numeric and within 0-14 for every staging row")

        temp = pd.to_numeric(df["temperature_c"], errors="coerce")
        if temp.isna().any():
            errors.append("temperature_c must be numeric for every staging row")

        if not df["experiment_mode"].astype(str).str.lower().eq("batch").all():
            errors.append("Locked phosphate staging domain currently permits only batch rows")
        if not df["equilibrium_status"].astype(str).str.lower().eq("equilibrium").all():
            errors.append("Every staging target must be verified as equilibrium/terminal")

        # Canonical phosphate basis documentation.
        adsorbate_text = df["adsorbate_name"].fillna("").astype(str).str.lower()
        if not adsorbate_text.str.contains("phosphate|po4", regex=True).all():
            errors.append("Every staging row must identify phosphate/PO4 as the adsorbate")

        p_basis = df["raw_unit_qe"].fillna("").astype(str).str.lower().str.contains("p/g", regex=False)
        if p_basis.any():
            notes = df.loc[p_basis, "unit_conversion_note"].fillna("").astype(str).str.lower()
            bad = ~(notes.str.contains("po4", regex=False) & notes.str.contains("p/g", regex=False))
            if bad.any():
                bad_ids = df.loc[p_basis].loc[bad, "record_id"].astype(str).tolist()
                errors.append(
                    "P-basis rows must document deterministic P-to-PO4 conversion in unit_conversion_note; "
                    f"failed rows: {bad_ids}"
                )

        # Study-accounting fields must be deterministic, not manually stale.
        counts = df.groupby("primary_study_id").size().sort_index()
        n_studies = int(counts.size)
        if n_studies < 3:
            errors.append(f"Staging pilot must contain >=3 independent primary studies; found {n_studies}")

        expected_count = df["primary_study_id"].map(counts).astype(int)
        stored_count = pd.to_numeric(df["study_row_count"], errors="coerce")
        if stored_count.isna().any() or not (stored_count.astype(int).to_numpy() == expected_count.to_numpy()).all():
            errors.append("study_row_count does not match deterministic counts in the staging ledger")

        expected_share = expected_count / len(df)
        stored_share = pd.to_numeric(df["study_share_primary_population"], errors="coerce")
        if stored_share.isna().any() or not ((stored_share - expected_share).abs() <= 1e-6).all():
            errors.append("study_share_primary_population does not match deterministic staging shares within 1e-6")

        largest_share = float(counts.max() / len(df))
        if largest_share > 0.20:
            warnings.append(
                f"Largest study share is {largest_share:.3f} (>0.20 planning target). Expected in this small staging pilot; "
                "it remains a mandatory sensitivity consideration at development freeze."
            )
        if n_studies < 30:
            warnings.append(
                f"Only {n_studies} independently verified studies are staged; this is below the frozen 30-study minimum "
                "development gate. MODEL TRAINING REMAINS PROHIBITED."
            )

        # Missing richer descriptors are allowed, but make them visible.
        py_temp_missing = int(df["pyrolysis_temperature_c"].isna().sum())
        if py_temp_missing:
            warnings.append(
                f"{py_temp_missing} row(s) lack primary-reported pyrolysis_temperature_c; retained as missing rather than inferred."
            )

        # Temporal external holdouts are prohibited even in staging/quarantine.
        if "primary_doi" not in registry.columns:
            errors.append("External holdout registry must contain primary_doi")
        else:
            holdouts = {normalize_doi(v) for v in registry["primary_doi"].dropna()}
            holdouts.discard("")
            leaked = sorted(set(doi_norm) & holdouts)
            if leaked:
                errors.append(f"Locked external-holdout DOI(s) found in primary-verified staging: {leaked}")

        # Every staged record needs an exact source locator, not only a DOI.
        if blank_mask(df["source_table_figure"]).any():
            errors.append("Every staging row must retain an exact primary source table/figure/text locator")

        # qmax/removal may exist for audit, but must not replace target semantics.
        qe = pd.to_numeric(df["qe_mg_g"], errors="coerce")
        if qe.isna().any():
            errors.append("qe_mg_g contains nonnumeric values")

    OUT.mkdir(parents=True, exist_ok=True)

    # Always emit deterministic audit products, including on warning-only passes.
    if not df.empty and "primary_study_id" in df.columns:
        study_counts = (
            df.groupby(["primary_study_id", "source_doi", "source_title"], dropna=False)
            .size()
            .reset_index(name="staging_rows")
            .sort_values(["staging_rows", "primary_study_id"], ascending=[False, True])
        )
        study_counts["staging_share"] = study_counts["staging_rows"] / len(df)
        study_counts.to_csv(OUT / "verified_staging_study_counts.csv", index=False)
    else:
        study_counts = pd.DataFrame()

    summary = {
        "gate": "Paper 2 V3 phosphate primary-verified staging integrity",
        "staging_file": str(STAGING.relative_to(HERE.parent)),
        "staging_sha256": sha256_file(STAGING),
        "rows": int(len(df)),
        "primary_studies": int(df["primary_study_id"].nunique()) if "primary_study_id" in df.columns and not df.empty else 0,
        "evidence_class_a_proxy_reported_rows": int(df["qe_derivation"].astype(str).eq("reported").sum()) if "qe_derivation" in df.columns else 0,
        "evidence_class_b_proxy_mass_balance_rows": int(df["qe_derivation"].astype(str).eq("calculated_from_mass_balance").sum()) if "qe_derivation" in df.columns else 0,
        "model_released_rows": int(df["inclusion_status"].astype(str).eq("include").sum()) if "inclusion_status" in df.columns else 0,
        "locked_external_holdout_overlap_count": 0,
        "errors": errors,
        "warnings": warnings,
        "model_training_permitted": False,
    }
    (OUT / "verified_staging_gate_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    print(json.dumps({k: v for k, v in summary.items() if k not in {"errors", "warnings"}}, indent=2))

    if errors:
        print("PHOSPHATE VERIFIED STAGING GATE: FAIL")
        raise SystemExit(1)

    print("PHOSPHATE VERIFIED STAGING GATE: PASS")
    print("MODEL RELEASE: BLOCKED — staging integrity pass is not a development-population freeze.")


if __name__ == "__main__":
    main()
