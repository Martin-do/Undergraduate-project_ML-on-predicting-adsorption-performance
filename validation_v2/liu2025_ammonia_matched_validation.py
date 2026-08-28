"""Matched random-vs-primary-study validation for Liu et al. ammonia-N corpus.

Uses the exact 409-row population implied by the historical Final sheet and the
public CatBoost notebook's Q <= 10 gate. The same fixed model specification is used
for random, GroupKFold and leave-one-study-out arms. All learned preprocessing is
fold-safe in the matched comparison.

A separate public-style random 80:20 diagnostic intentionally reproduces the public
code's global preprocessing order to check correspondence with the published
CatBoost test result. That diagnostic is not used as the matched comparator.
"""
from __future__ import annotations

from pathlib import Path
import io
import json

import numpy as np
import pandas as pd
import requests
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import KNNImputer
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import KFold, GroupKFold, LeaveOneGroupOut, train_test_split
from sklearn.preprocessing import PowerTransformer, StandardScaler
from xgboost import XGBRegressor

HERE = Path(__file__).resolve().parent
PROV = HERE / "outputs" / "multidataset" / "liu2025_ammonia_primary_provenance"
OUT = HERE / "outputs" / "multidataset" / "liu2025_ammonia_matched_validation"
OUT.mkdir(parents=True, exist_ok=True)

FEATURES = ["C", "H/C", "O/C", "Ash", "pH_bio", "BET", "V", "Temp", "pH", "C0(mg/g)"]
TARGET = "Q(mg/g)"


def numeric_frame(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for c in cols:
        out[c] = pd.to_numeric(
            df[c].astype(str).str.replace("\u202f", "", regex=False).str.replace("\xa0", "", regex=False),
            errors="coerce",
        )
    return out


def fit_preprocess(Xtr, Xte):
    """Fold-safe implementation of the public KNN -> Box-Cox -> Z-score sequence."""
    imp = KNNImputer(n_neighbors=5)
    a = imp.fit_transform(Xtr)
    b = imp.transform(Xte)
    a = np.maximum(a, 1e-5)
    b = np.maximum(b, 1e-5)
    pt = PowerTransformer(method="box-cox", standardize=False)
    a = pt.fit_transform(a)
    b = pt.transform(b)
    sc = StandardScaler()
    return sc.fit_transform(a), sc.transform(b)


def model_factories():
    return {
        "RF500": lambda: RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1),
        "XGB500": lambda: XGBRegressor(
            n_estimators=500, max_depth=6, learning_rate=0.05,
            subsample=0.9, colsample_bytree=0.9,
            objective="reg:squarederror", random_state=42, n_jobs=-1,
        ),
        "CatBoost500": lambda: CatBoostRegressor(
            iterations=500, depth=6, learning_rate=0.05,
            loss_function="RMSE", random_seed=42, verbose=0,
        ),
    }


def metrics(y, p):
    return {
        "r2": float(r2_score(y, p)),
        "rmse": float(np.sqrt(mean_squared_error(y, p))),
        "mae": float(mean_absolute_error(y, p)),
    }


def out_of_fold(X, y, groups, splitter, factory):
    pred = np.full(len(y), np.nan, dtype=float)
    fold_rows = []
    for fold, (tr, te) in enumerate(splitter.split(X, y, groups), start=1):
        Xtr, Xte = fit_preprocess(X[tr], X[te])
        model = factory()
        model.fit(Xtr, y[tr])
        pp = model.predict(Xte)
        pred[te] = pp
        fm = metrics(y[te], pp)
        fold_rows.append({
            "fold": fold,
            "n_train": len(tr),
            "n_test": len(te),
            "test_groups": "|".join(sorted(set(groups[te]))) if groups is not None else "",
            **fm,
        })
    assert np.isfinite(pred).all()
    return pred, pd.DataFrame(fold_rows)


def public_style_diagnostic(X, y):
    """Reproduce public ordering: global imputation/Box-Cox/scaling, then random 80:20."""
    imp = KNNImputer(n_neighbors=5)
    z = imp.fit_transform(X)
    z = np.maximum(z, 1e-5)
    pt = PowerTransformer(method="box-cox", standardize=False)
    z = pt.fit_transform(z)
    sc = StandardScaler()
    z = sc.fit_transform(z)
    Xtr, Xte, ytr, yte = train_test_split(z, y, test_size=0.2, random_state=1)
    model = model_factories()["CatBoost500"]()
    model.fit(Xtr, ytr)
    p = model.predict(Xte)
    return {"rows": len(y), "test_rows": len(yte), **metrics(yte, p)}


def main():
    if not (PROV / "liu2025_ammonia_model_population_409.csv").exists():
        raise FileNotFoundError("Run liu2025_ammonia_primary_provenance.py first")

    df = pd.read_csv(PROV / "liu2025_ammonia_model_population_409.csv")
    assert len(df) == 409
    assert df["primary_study_id"].nunique() == 7

    X = numeric_frame(df, FEATURES).to_numpy(dtype=float)
    y = numeric_frame(df, [TARGET])[TARGET].to_numpy(dtype=float)
    groups = df["primary_study_id"].astype(str).to_numpy()

    group_counts = pd.Series(groups).value_counts()
    largest = int(group_counts.max())
    largest_share = float(largest / len(df))

    public_diag = public_style_diagnostic(X, y)
    (OUT / "public_style_catboost_diagnostic.json").write_text(json.dumps(public_diag, indent=2), encoding="utf-8")

    results = []
    all_predictions = []
    for model_name, factory in model_factories().items():
        random_split = KFold(n_splits=5, shuffle=True, random_state=42)
        grouped_split = GroupKFold(n_splits=5)
        logo_split = LeaveOneGroupOut()

        p_random, f_random = out_of_fold(X, y, groups, random_split, factory)
        p_group, f_group = out_of_fold(X, y, groups, grouped_split, factory)
        p_logo, f_logo = out_of_fold(X, y, groups, logo_split, factory)

        mr = metrics(y, p_random)
        mg = metrics(y, p_group)
        ml = metrics(y, p_logo)
        results.append({
            "population": "public_code_q_le_10",
            "model": model_name,
            "rows": len(df),
            "groups": int(len(group_counts)),
            "largest_group_rows": largest,
            "largest_group_share": largest_share,
            "random_r2": mr["r2"],
            "random_rmse": mr["rmse"],
            "random_mae": mr["mae"],
            "grouped_r2": mg["r2"],
            "grouped_rmse": mg["rmse"],
            "grouped_mae": mg["mae"],
            "delta_r2_random_minus_grouped": mr["r2"] - mg["r2"],
            "delta_rmse_grouped_minus_random": mg["rmse"] - mr["rmse"],
            "delta_mae_grouped_minus_random": mg["mae"] - mr["mae"],
            "logo_r2": ml["r2"],
            "logo_rmse": ml["rmse"],
            "logo_mae": ml["mae"],
        })

        f_random.to_csv(OUT / f"{model_name}_random_folds.csv", index=False)
        f_group.to_csv(OUT / f"{model_name}_grouped_folds.csv", index=False)
        f_logo.to_csv(OUT / f"{model_name}_logo_folds.csv", index=False)
        all_predictions.append(pd.DataFrame({
            "row_index": np.arange(len(df)),
            "primary_study_id": groups,
            "y_true": y,
            "model": model_name,
            "pred_random": p_random,
            "pred_grouped": p_group,
            "pred_logo": p_logo,
        }))

    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv(OUT / "liu2025_ammonia_matched_metrics.csv", index=False)
    pd.concat(all_predictions, ignore_index=True).to_csv(OUT / "liu2025_ammonia_predictions.csv", index=False)
    group_counts.rename_axis("primary_study_id").reset_index(name="n_rows").to_csv(OUT / "group_counts.csv", index=False)

    summary = {
        "doi": "10.1038/s41545-024-00429-z",
        "paper_reported_collected_rows": 417,
        "public_code_matched_population_rows": len(df),
        "primary_studies": int(len(group_counts)),
        "largest_group_rows": largest,
        "largest_group_share": largest_share,
        "published_catboost_test_r2": 0.9329,
        "published_catboost_test_rmse": 0.5378,
        "public_style_fixed_catboost_diagnostic": public_diag,
        "matched_metrics_file": "liu2025_ammonia_matched_metrics.csv",
        "interpretation_rule": "Matched claims use fold-safe random vs primary-study splits on identical 409 rows; public-style global-preprocessing holdout is diagnostic only.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Public-style CatBoost diagnostic:")
    print(json.dumps(public_diag, indent=2))
    print("\nMatched metrics:")
    print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
