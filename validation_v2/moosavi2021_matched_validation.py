"""Matched random-vs-primary-study validation for Moosavi et al. 2021.

This analysis follows MULTIDATASET_VALIDATION_PROTOCOL.md and operates only on the
344 rows recoverable from the official Table S1 PDF. The population is identical in
the random and grouped arms. Reference ID from Table S1 is the primary-study group.

The source paper reports RF as the best model and Table 7 selects 20 trees / maximum
depth 7 (model no. 9, selected over 140 trees/depth 7 because performance was nearly
identical with lower complexity). The paper reports normalization to [0,1] but does
not provide enough information to reconstruct an exact row-level train/test seed or
the categorical encoding. Accordingly, this is a matched methodological replication,
not a claim to reproduce the exact published test partition.
"""
from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "outputs" / "multidataset" / "moosavi2021_table_s1" / "moosavi2021_table_s1_recovered.csv"
OUT = HERE / "outputs" / "multidataset" / "moosavi2021_matched_validation"
OUT.mkdir(parents=True, exist_ok=True)

TARGET = "qe_mg_g"
GROUP = "reference_id"

NINE_NUMERIC = [
    "pyrolysis_temp_c",
    "agrowaste_ph",
    "particle_size_mm",
    "surface_area_m2g",
    "pore_volume_cm3g",
    "adsorption_temp_c",
    "adsorption_ph",
    "c0_mgL",
]
NINE_CATEGORICAL = ["dye_type"]
FIVE_FEATURES = [
    "c0_mgL",
    "pore_volume_cm3g",
    "surface_area_m2g",
    "agrowaste_ph",
    "particle_size_mm",
]

MODEL_SPECS = {
    # Published optimization selected this tree-count/depth combination.
    "rf_published_hyperparams": dict(n_estimators=20, max_depth=7, random_state=42, n_jobs=-1),
    # Stabilized common RF baseline predeclared as a cross-dataset tree comparator.
    "rf_500_common": dict(n_estimators=500, max_depth=None, random_state=42, n_jobs=-1),
}


def build_pipeline(feature_set: str, model_spec: dict) -> Pipeline:
    rf = RandomForestRegressor(**model_spec)
    if feature_set == "nine_variables":
        pre = ColumnTransformer(
            transformers=[
                ("num", MinMaxScaler(), NINE_NUMERIC),
                ("dye", OneHotEncoder(handle_unknown="ignore", sparse_output=False), NINE_CATEGORICAL),
            ],
            remainder="drop",
        )
        return Pipeline([("preprocess", pre), ("model", rf)])
    if feature_set == "five_selected":
        return Pipeline([("preprocess", MinMaxScaler()), ("model", rf)])
    raise ValueError(feature_set)


def feature_frame(df: pd.DataFrame, feature_set: str) -> pd.DataFrame:
    if feature_set == "nine_variables":
        return df[NINE_NUMERIC + NINE_CATEGORICAL]
    if feature_set == "five_selected":
        return df[FIVE_FEATURES]
    raise ValueError(feature_set)


def metric_dict(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def run_cv(df: pd.DataFrame, feature_set: str, model_name: str, cv_name: str):
    X = feature_frame(df, feature_set)
    y = df[TARGET].to_numpy(float)
    groups = df[GROUP].to_numpy(int)

    if cv_name == "random_5fold":
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        split_iter = cv.split(X, y)
    elif cv_name == "study_groupkfold_5":
        cv = GroupKFold(n_splits=5)
        split_iter = cv.split(X, y, groups)
    elif cv_name == "study_logo":
        cv = LeaveOneGroupOut()
        split_iter = cv.split(X, y, groups)
    else:
        raise ValueError(cv_name)

    pred = np.full(len(df), np.nan, dtype=float)
    fold_rows = []
    prediction_rows = []

    for fold, (train_idx, test_idx) in enumerate(split_iter, start=1):
        model = build_pipeline(feature_set, MODEL_SPECS[model_name])
        model.fit(X.iloc[train_idx], y[train_idx])
        p = model.predict(X.iloc[test_idx])
        pred[test_idx] = p

        held_groups = sorted(set(groups[test_idx].tolist()))
        fm = metric_dict(y[test_idx], p) if len(test_idx) >= 2 else {"r2": np.nan, "rmse": 0.0, "mae": 0.0}
        fold_rows.append({
            "feature_set": feature_set,
            "model": model_name,
            "validation": cv_name,
            "fold": fold,
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "n_train_groups": len(set(groups[train_idx].tolist())),
            "n_test_groups": len(held_groups),
            "held_reference_ids": "|".join(map(str, held_groups)),
            **fm,
        })
        for idx, yt, yp in zip(test_idx, y[test_idx], p):
            prediction_rows.append({
                "row_id": int(df.iloc[idx]["row_id"]),
                "reference_id": int(groups[idx]),
                "feature_set": feature_set,
                "model": model_name,
                "validation": cv_name,
                "fold": fold,
                "y_true": float(yt),
                "y_pred": float(yp),
                "error": float(yp - yt),
                "abs_error": float(abs(yp - yt)),
            })

    if np.isnan(pred).any():
        raise AssertionError(f"Incomplete OOF predictions for {feature_set}/{model_name}/{cv_name}")
    pooled = metric_dict(y, pred)
    pooled.update({
        "feature_set": feature_set,
        "model": model_name,
        "validation": cv_name,
        "n_rows": len(df),
        "n_studies": int(df[GROUP].nunique()),
    })
    return pooled, fold_rows, prediction_rows


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"{SOURCE} not found. Run moosavi2021_table_s1_extract.py first in the same workspace."
        )
    df = pd.read_csv(SOURCE)
    if len(df) != 344:
        raise AssertionError(f"Expected 344 recoverable Table-S1 rows, found {len(df)}")
    expected_refs = set(range(1, 12)) | {13}
    if set(df[GROUP].astype(int).unique()) != expected_refs:
        raise AssertionError("Recovered primary-study group set changed")

    pooled_rows, fold_rows, prediction_rows = [], [], []
    for feature_set in ["nine_variables", "five_selected"]:
        for model_name in MODEL_SPECS:
            for cv_name in ["random_5fold", "study_groupkfold_5", "study_logo"]:
                pooled, folds, preds = run_cv(df, feature_set, model_name, cv_name)
                pooled_rows.append(pooled)
                fold_rows.extend(folds)
                prediction_rows.extend(preds)

    pooled = pd.DataFrame(pooled_rows)
    folds = pd.DataFrame(fold_rows)
    preds = pd.DataFrame(prediction_rows)

    # Matched random-vs-group deltas. Positive delta means random validation is more optimistic.
    pivot = pooled.pivot_table(
        index=["feature_set", "model"], columns="validation", values=["r2", "rmse", "mae"]
    )
    delta_rows = []
    for (feature_set, model_name), _ in pivot.iterrows():
        rr = pooled[(pooled.feature_set == feature_set) & (pooled.model == model_name) & (pooled.validation == "random_5fold")].iloc[0]
        gg = pooled[(pooled.feature_set == feature_set) & (pooled.model == model_name) & (pooled.validation == "study_groupkfold_5")].iloc[0]
        ll = pooled[(pooled.feature_set == feature_set) & (pooled.model == model_name) & (pooled.validation == "study_logo")].iloc[0]
        delta_rows.append({
            "feature_set": feature_set,
            "model": model_name,
            "r2_random": rr.r2,
            "r2_grouped": gg.r2,
            "delta_r2_random_minus_grouped": rr.r2 - gg.r2,
            "rmse_random": rr.rmse,
            "rmse_grouped": gg.rmse,
            "delta_rmse_grouped_minus_random": gg.rmse - rr.rmse,
            "mae_random": rr.mae,
            "mae_grouped": gg.mae,
            "delta_mae_grouped_minus_random": gg.mae - rr.mae,
            "r2_logo": ll.r2,
            "rmse_logo": ll.rmse,
            "mae_logo": ll.mae,
        })
    deltas = pd.DataFrame(delta_rows)

    # Per-study LOSO diagnostics are important because one source can contribute many rows.
    logo_preds = preds[preds.validation == "study_logo"].copy()
    study_rows = []
    for (feature_set, model_name, ref_id), sub in logo_preds.groupby(["feature_set", "model", "reference_id"]):
        yt = sub.y_true.to_numpy(float)
        yp = sub.y_pred.to_numpy(float)
        r2 = np.nan if len(sub) < 2 or np.allclose(np.var(yt), 0.0) else float(r2_score(yt, yp))
        study_rows.append({
            "feature_set": feature_set,
            "model": model_name,
            "reference_id": int(ref_id),
            "n_rows": len(sub),
            "r2": r2,
            "rmse": float(mean_squared_error(yt, yp) ** 0.5),
            "mae": float(mean_absolute_error(yt, yp)),
        })
    per_study = pd.DataFrame(study_rows)

    pooled.to_csv(OUT / "moosavi2021_pooled_metrics.csv", index=False)
    folds.to_csv(OUT / "moosavi2021_fold_metrics.csv", index=False)
    preds.to_csv(OUT / "moosavi2021_oof_predictions.csv", index=False)
    deltas.to_csv(OUT / "moosavi2021_random_vs_grouped_deltas.csv", index=False)
    per_study.to_csv(OUT / "moosavi2021_loso_per_study.csv", index=False)

    paper9 = deltas[(deltas.feature_set == "nine_variables") & (deltas.model == "rf_published_hyperparams")].iloc[0]
    paper5 = deltas[(deltas.feature_set == "five_selected") & (deltas.model == "rf_published_hyperparams")].iloc[0]
    common9 = deltas[(deltas.feature_set == "nine_variables") & (deltas.model == "rf_500_common")].iloc[0]

    summary = {
        "dataset": "Moosavi et al. 2021 Table S1 recoverable subset",
        "doi": "10.3390/nano11102734",
        "rows": int(len(df)),
        "primary_study_groups": int(df[GROUP].nunique()),
        "published_table_claimed_rows": 350,
        "source_pdf_missing_rows": [340, 341, 342, 343, 344, 345],
        "source_pdf_missing_reference_group": 12,
        "published_reported_rf_nine_variable_test_r2": 0.84,
        "published_reported_rf_five_variable_test_r2": 0.81,
        "published_rf_hyperparams_from_table7": {"n_estimators": 20, "max_depth": 7},
        "matched_published_hyperparams_nine": {
            "random_5fold_r2": float(paper9.r2_random),
            "study_groupkfold_r2": float(paper9.r2_grouped),
            "delta_r2": float(paper9.delta_r2_random_minus_grouped),
            "study_logo_r2": float(paper9.r2_logo),
        },
        "matched_published_hyperparams_five": {
            "random_5fold_r2": float(paper5.r2_random),
            "study_groupkfold_r2": float(paper5.r2_grouped),
            "delta_r2": float(paper5.delta_r2_random_minus_grouped),
            "study_logo_r2": float(paper5.r2_logo),
        },
        "matched_common_rf_nine": {
            "random_5fold_r2": float(common9.r2_random),
            "study_groupkfold_r2": float(common9.r2_grouped),
            "delta_r2": float(common9.delta_r2_random_minus_grouped),
            "study_logo_r2": float(common9.r2_logo),
        },
        "interpretation_gate": "Report as recoverable-subset matched replication, not exact reproduction of the paper's unpublished row-level partition. Preserve the result whether the grouped score is lower, similar, or higher.",
    }
    (OUT / "moosavi2021_matched_validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print("\nMatched deltas:\n", deltas.to_string(index=False))


if __name__ == "__main__":
    main()
