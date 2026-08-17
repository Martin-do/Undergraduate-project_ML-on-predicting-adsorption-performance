"""Robustness checks for adsorption Dataset V2.1.

Checks:
1. leave-one-primary-study-out (LOSO) transfer on the 273-row strict set;
2. matched random-vs-study-group validation using condition-level records only;
3. pre-classified conventional-aqueous-capacity-only sensitivity (264 rows);
4. external transfer to corrected Liu 2025 and Jaffari 2023 datasets.

The 264-row sensitivity is supplemental: it does not replace the pre-existing
273-row strict result. It excludes the nine rows classified before modelling as
`aqueous_operational_uptake` rather than conventional aqueous adsorption capacity.
No Q_MAX=624 filtering and no removal_percent predictor are used.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import build_dataset_v21
import external_validation_v2 as extv2
import feature_parity_validation as fp
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor
import study_aware_validation as base

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
V21 = OUT / "adsorption_dataset_v2_1.csv"
OUT.mkdir(parents=True, exist_ok=True)
fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor
RAW_MODEL_COLS = base.RAW_FEATURES + ["removal_percent", "source_link"]


def load_v21() -> pd.DataFrame:
    build_dataset_v21.main()
    df = pd.read_csv(V21, encoding="utf-8-sig")
    for col in base.NUMERIC_FEATURES + [base.TARGET]:
        df[col] = df[col].map(base.parse_numeric)
    for col in base.CATEGORICAL_FEATURES:
        df[col] = df[col].astype("string").fillna("Unknown")
    if df[base.TARGET].isna().any():
        raise RuntimeError("V2.1 contains an unusable target after parsing")
    return df


def metric(y, p):
    return {
        "r2": float(r2_score(y, p)),
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, p))),
        "mae_mg_g": float(mean_absolute_error(y, p)),
        "median_ae_mg_g": float(np.median(np.abs(y - p))),
    }


def run_loso(data: pd.DataFrame, scope: str):
    studies = sorted(data["primary_study_id_v21"].astype(str).unique())
    bank = fp.models()
    pred_frames, per_study_rows = [], []
    for study in studies:
        te = data["primary_study_id_v21"].astype(str).eq(study).to_numpy()
        train, test = data.loc[~te].copy(), data.loc[te].copy()
        prep = DtypeSafeParityPreprocessor().fit(train[RAW_MODEL_COLS])
        xtr, xte = prep.transform(train[RAW_MODEL_COLS]), prep.transform(test[RAW_MODEL_COLS])
        ytr, yte = train[base.TARGET].to_numpy(float), test[base.TARGET].to_numpy(float)
        for name in ["RF", "XGB"]:
            p = clone(bank[name]).fit(xtr, ytr).predict(xte)
            pred_frames.append(pd.DataFrame({
                "scope": scope, "held_out_primary_study": study, "model": name,
                "actual_qe_mg_g": yte, "predicted_qe_mg_g": p,
                "abs_error_mg_g": np.abs(yte - p),
            }))
            per_study_rows.append({
                "scope": scope, "held_out_primary_study": study, "model": name,
                "n_rows": int(len(test)), "mae_mg_g": float(mean_absolute_error(yte, p)),
                "rmse_mg_g": float(np.sqrt(mean_squared_error(yte, p))),
                "median_ae_mg_g": float(np.median(np.abs(yte - p))),
            })
    preds, per_study = pd.concat(pred_frames, ignore_index=True), pd.DataFrame(per_study_rows)
    pooled, equal = [], []
    for name, g in preds.groupby("model", sort=False):
        pooled.append({"scope": scope, "model": name, "n_rows": int(len(g)), "n_studies": len(studies), **metric(g.actual_qe_mg_g, g.predicted_qe_mg_g)})
        ps = per_study[per_study.model.eq(name)]
        equal.append({
            "scope": scope, "model": name, "n_studies": int(len(ps)),
            "mean_study_mae_mg_g": float(ps.mae_mg_g.mean()),
            "median_study_mae_mg_g": float(ps.mae_mg_g.median()),
            "mean_study_rmse_mg_g": float(ps.rmse_mg_g.mean()),
            "median_study_rmse_mg_g": float(ps.rmse_mg_g.median()),
            "mean_study_median_ae_mg_g": float(ps.median_ae_mg_g.mean()),
        })
    return pd.DataFrame(pooled), per_study, pd.DataFrame(equal), preds


def run_matched(data: pd.DataFrame, prefix: str):
    data = data.copy().reset_index(drop=True)
    groups = data["primary_study_id_v21"].astype(str).to_numpy()
    frames, folds = [], []
    for scheme, scheme_groups in [
        (f"{prefix}__row_random_5fold", None),
        (f"{prefix}__primary_group_5fold", groups),
    ]:
        results, _, fold_rows, _, _ = fp.evaluate_scheme(data, scheme, scheme_groups)
        frames.append(pd.DataFrame(results)); folds.append(pd.DataFrame(fold_rows))
    return data, pd.concat(frames, ignore_index=True), pd.concat(folds, ignore_index=True)


def external_metrics(y, p):
    return {**metric(y, p), "prediction_min_mg_g": float(np.min(p)), "prediction_max_mg_g": float(np.max(p))}


def run_external(df: pd.DataFrame):
    liu, liu_audit, _ = extv2.load_liu()
    jaffari, jaffari_audit = extv2.load_jaffari()
    scopes = {
        "primary_confirmed_307": df[df["analysis_eligible_primary_provenance_v21"].astype(bool)].copy().reset_index(drop=True),
        "strict_comparable_273": df[df["analysis_eligible_strict_comparable_v21"].astype(bool)].copy().reset_index(drop=True),
    }
    bank, rows, preds = fp.models(), [], []
    for dataset_name, ext in [("liu_2025_dyes", liu), ("jaffari_2023_ec", jaffari)]:
        yext = ext[base.TARGET].to_numpy(float)
        for scope_name, train in scopes.items():
            prep = DtypeSafeParityPreprocessor().fit(train[RAW_MODEL_COLS])
            xtr, xext = prep.transform(train[RAW_MODEL_COLS]), prep.transform(ext[RAW_MODEL_COLS])
            ytr = train[base.TARGET].to_numpy(float)
            for name in ["LR", "RF", "XGB"]:
                p = clone(bank[name]).fit(xtr, ytr).predict(xext)
                rows.append({
                    "dataset": dataset_name, "training_scope": scope_name, "model": name,
                    "n_training": int(len(train)), "n_training_primary_studies": int(train.primary_study_id_v21.nunique()),
                    "n_external": int(len(ext)), **external_metrics(yext, p),
                })
                preds.append(pd.DataFrame({
                    "dataset": dataset_name, "training_scope": scope_name, "model": name,
                    "external_row_id": np.arange(len(ext)), "actual_qe_mg_g": yext,
                    "predicted_qe_mg_g": p,
                }))
    return pd.DataFrame(rows), pd.concat(preds, ignore_index=True), liu_audit, jaffari_audit


def main():
    df = load_v21()
    strict = df[df["analysis_eligible_strict_comparable_v21"].astype(bool)].copy().reset_index(drop=True)
    condition_only = strict[strict["record_granularity_v21"].eq("experimental_condition")].copy().reset_index(drop=True)
    conventional = strict[strict["target_comparability_class_v21"].eq("conventional_aqueous_adsorption_capacity")].copy().reset_index(drop=True)
    if len(conventional) != 264:
        raise RuntimeError(f"Conventional-only sensitivity expected 264 rows, found {len(conventional)}")

    loso_pooled, loso_per_study, loso_equal, loso_preds = run_loso(strict, "strict_comparable_273")
    conv_loso_pooled, conv_loso_per_study, conv_loso_equal, conv_loso_preds = run_loso(conventional, "conventional_only_264")
    condition_data, condition_metrics, condition_folds = run_matched(condition_only, "condition_only")
    conventional_data, conventional_metrics, conventional_folds = run_matched(conventional, "conventional_only")
    ext_metrics, ext_preds, liu_audit, jaffari_audit = run_external(df)

    pd.concat([loso_pooled, conv_loso_pooled], ignore_index=True).to_csv(OUT / "robustness_v21_loso_pooled.csv", index=False)
    pd.concat([loso_per_study, conv_loso_per_study], ignore_index=True).to_csv(OUT / "robustness_v21_loso_per_study.csv", index=False)
    pd.concat([loso_equal, conv_loso_equal], ignore_index=True).to_csv(OUT / "robustness_v21_loso_equal_study.csv", index=False)
    pd.concat([loso_preds, conv_loso_preds], ignore_index=True).to_csv(OUT / "robustness_v21_loso_predictions.csv", index=False)
    condition_metrics.to_csv(OUT / "robustness_v21_condition_only_metrics.csv", index=False)
    condition_folds.to_csv(OUT / "robustness_v21_condition_only_folds.csv", index=False)
    conventional_metrics.to_csv(OUT / "robustness_v21_conventional_only_metrics.csv", index=False)
    conventional_folds.to_csv(OUT / "robustness_v21_conventional_only_folds.csv", index=False)
    ext_metrics.to_csv(OUT / "robustness_v21_external_metrics.csv", index=False)
    ext_preds.to_csv(OUT / "robustness_v21_external_predictions.csv", index=False)

    audit = {
        "strict_comparable_rows": int(len(strict)), "strict_comparable_studies": int(strict.primary_study_id_v21.nunique()),
        "condition_only_rows": int(len(condition_data)), "condition_only_studies": int(condition_data.primary_study_id_v21.nunique()),
        "conventional_only_rows": int(len(conventional_data)), "conventional_only_studies": int(conventional_data.primary_study_id_v21.nunique()),
        "conventional_only_rationale": "Supplemental pre-classified target-type sensitivity; removes aqueous_operational_uptake, not selected by prediction error.",
        "loso_models": ["RF", "XGB"],
        "external_training_scopes": ["primary_confirmed_307", "strict_comparable_273"],
        "external_models": ["LR", "RF", "XGB"],
        "liu_preparation": liu_audit, "jaffari_preparation": jaffari_audit,
        "qmax_624_used": False, "removal_percent_used_as_predictor": False,
        "external_targets_used_for_tuning": False,
    }
    (OUT / "robustness_v21_audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== V2.1 LOSO POOLED (STRICT + CONVENTIONAL SENSITIVITY) ===")
    print(pd.concat([loso_pooled, conv_loso_pooled], ignore_index=True).to_string(index=False))
    print("\n=== V2.1 LOSO EQUAL-STUDY ===")
    print(pd.concat([loso_equal, conv_loso_equal], ignore_index=True).to_string(index=False))
    print("\n=== CONDITION-ONLY MATCHED VALIDATION ===")
    print(condition_metrics.to_string(index=False))
    print("\n=== CONVENTIONAL-ONLY MATCHED SENSITIVITY ===")
    print(conventional_metrics.to_string(index=False))
    print("\n=== V2.1 EXTERNAL TRANSFER ===")
    print(ext_metrics.to_string(index=False))
    print("\n=== AUDIT ===")
    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
