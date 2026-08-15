"""Strict holdout validation using only inherited rows with confirmed primary provenance.

Scientific scope
----------------
This analysis deliberately excludes inherited Iftikhar-derived rows whose primary
study is still unresolved. It therefore answers a narrower but defensible question:
can the original ID-SEAD feature representation generalize across *confirmed primary
studies* rather than across randomly split literature rows?

The physical Q_MAX/constraint layer is intentionally excluded pending domain repair.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

import study_aware_validation as base
import feature_parity_validation as fp
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor

ROOT = Path(__file__).resolve().parents[1]
MAP = Path(__file__).resolve().parent / "primary_study_map.csv"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
DOMINANT_LEGACY_TOKEN = "moosavi"

# Use the dtype-safe implementation already established by the feature-parity audit.
fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor


def norm(v: object) -> str:
    return "" if pd.isna(v) else " ".join(str(v).strip().lower().split())


def build_strict_dataset() -> tuple[pd.DataFrame, np.ndarray, dict]:
    df = base.load_data().copy()
    mapping = pd.read_csv(MAP, keep_default_na=False)
    confirmed = mapping[mapping["status"].str.startswith("confirmed")].copy()
    if confirmed["project_adsorbent"].duplicated().any():
        raise ValueError("Confirmed primary study map must have unique project_adsorbent keys")
    id_map = confirmed.set_index("project_adsorbent")["primary_study_id"].to_dict()

    dominant = df["source_link"].map(norm).str.contains(DOMINANT_LEGACY_TOKEN, na=False)
    inherited = df.loc[dominant].copy()
    inherited["primary_study_id"] = inherited["adsorbent"].astype(str).str.strip().map(id_map).fillna("")

    unresolved = inherited["primary_study_id"].eq("")
    strict = inherited.loc[~unresolved].copy().reset_index(drop=True)
    groups = strict["primary_study_id"].to_numpy(str)

    audit = {
        "usable_target_rows_full_corpus": int(len(df)),
        "iftikhar_inherited_usable_rows": int(len(inherited)),
        "strict_confirmed_primary_rows": int(len(strict)),
        "strict_confirmed_primary_studies": int(pd.Series(groups).nunique()),
        "excluded_unresolved_inherited_rows": int(unresolved.sum()),
        "excluded_unresolved_adsorbents": sorted(
            inherited.loc[unresolved, "adsorbent"].astype(str).unique().tolist()
        ),
        "non_iftikhar_rows_not_in_strict_analysis": int((~dominant).sum()),
        "analysis_scope": "confirmed Iftikhar-derived primary studies only",
        "constraint_layer": "excluded pending physical-domain repair",
    }
    return strict, groups, audit


def per_study_metrics(predictions: pd.DataFrame, groups: np.ndarray) -> pd.DataFrame:
    frames = []
    for model, gmodel in predictions.groupby("model", sort=False):
        gmodel = gmodel.copy()
        gmodel["primary_study_id"] = groups[gmodel["row_id"].to_numpy(int)]
        for study, g in gmodel.groupby("primary_study_id", sort=True):
            y = g["actual_qe_mg_g"].to_numpy(float)
            p = g["predicted_qe_mg_g"].to_numpy(float)
            frames.append({
                "model": model,
                "primary_study_id": study,
                "n_rows": int(len(g)),
                "mae_mg_g": float(mean_absolute_error(y, p)),
                "rmse_mg_g": float(np.sqrt(mean_squared_error(y, p))),
                "median_ae_mg_g": float(np.median(np.abs(y - p))),
            })
    return pd.DataFrame(frames)


def equal_study_summary(per_study: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, g in per_study.groupby("model", sort=False):
        rows.append({
            "model": model,
            "n_primary_studies": int(g["primary_study_id"].nunique()),
            "mean_study_mae_mg_g": float(g["mae_mg_g"].mean()),
            "median_study_mae_mg_g": float(g["mae_mg_g"].median()),
            "mean_study_rmse_mg_g": float(g["rmse_mg_g"].mean()),
            "median_study_rmse_mg_g": float(g["rmse_mg_g"].median()),
            "mean_study_median_ae_mg_g": float(g["median_ae_mg_g"].mean()),
        })
    return pd.DataFrame(rows)


def main() -> None:
    strict, groups, audit = build_strict_dataset()
    if len(np.unique(groups)) < 5:
        raise RuntimeError("Fewer than five confirmed primary-study groups; strict 5-fold holdout is not supportable")

    results, pred_frames, fold_records, alpha_records, feature_counts = fp.evaluate_scheme(
        strict, "confirmed_primary_study_holdout", groups
    )
    metrics = pd.DataFrame(results)
    predictions = pd.concat(pred_frames, ignore_index=True)
    per_study = per_study_metrics(predictions, groups)
    equal_summary = equal_study_summary(per_study)

    metrics.to_csv(OUT / "primary_study_holdout_metrics.csv", index=False)
    predictions.to_csv(OUT / "primary_study_holdout_predictions.csv", index=False)
    per_study.to_csv(OUT / "primary_study_holdout_per_study_metrics.csv", index=False)
    equal_summary.to_csv(OUT / "primary_study_holdout_equal_study_summary.csv", index=False)
    pd.DataFrame(fold_records).to_csv(OUT / "primary_study_holdout_folds.csv", index=False)
    pd.DataFrame(alpha_records).to_csv(OUT / "primary_study_holdout_stack_alphas.csv", index=False)
    pd.DataFrame(feature_counts).to_csv(OUT / "primary_study_holdout_feature_counts.csv", index=False)
    (OUT / "primary_study_holdout_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=== STRICT PRIMARY-STUDY HOLDOUT AUDIT ===")
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    print("\n=== POOLED METRICS ===")
    print(metrics.to_string(index=False))
    print("\n=== EQUAL-STUDY SUMMARY ===")
    print(equal_summary.to_string(index=False))
    print("\n=== PER-STUDY METRICS ===")
    print(per_study.to_string(index=False))


if __name__ == "__main__":
    main()
