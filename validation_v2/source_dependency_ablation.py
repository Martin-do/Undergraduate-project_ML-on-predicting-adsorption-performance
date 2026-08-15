"""Quantify how much model performance depends on the Moosavi secondary compilation.

This diagnostic is not a final validation result. It answers a novelty/source-
dependence question: does the apparent predictive signal persist outside the
251-row secondary compilation, and how asymmetric is transfer between that
compilation and the rest of the corpus?
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline

from xgboost import XGBRegressor

import study_aware_validation as base

OUT_DIR = Path(__file__).resolve().parent / "outputs"
DOMINANT = "moosavi et al., 2023"


def estimators():
    return {
        "RF": RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=base.RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGB": XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=base.RANDOM_STATE,
            n_jobs=-1,
            verbosity=0,
        ),
    }


def pipe(est):
    return Pipeline([("prep", base.make_preprocessor()), ("model", est)])


def metrics(y, pred):
    return {
        "n": int(len(y)),
        "r2": float(r2_score(y, pred)) if len(y) >= 2 and np.std(y) > 0 else None,
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, pred))),
        "mae_mg_g": float(mean_absolute_error(y, pred)),
        "median_ae_mg_g": float(np.median(np.abs(y - pred))),
    }


def random_cv(subset, model):
    n_splits = min(5, max(2, len(subset) // 10))
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=base.RANDOM_STATE)
    y = subset[base.TARGET].to_numpy(float)
    pred = cross_val_predict(
        pipe(clone(model)), subset[base.RAW_FEATURES], y, cv=cv, n_jobs=-1
    )
    return metrics(y, pred)


def transfer(train, test, model):
    m = pipe(clone(model))
    m.fit(train[base.RAW_FEATURES], train[base.TARGET].to_numpy(float))
    pred = m.predict(test[base.RAW_FEATURES])
    return metrics(test[base.TARGET].to_numpy(float), pred)


def target_summary(df):
    y = df[base.TARGET].to_numpy(float)
    return {
        "rows": int(len(df)),
        "min": float(np.min(y)),
        "median": float(np.median(y)),
        "mean": float(np.mean(y)),
        "max": float(np.max(y)),
        "std": float(np.std(y)),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = base.load_data()
    dom = df.loc[df["study_group"].eq(DOMINANT)].copy()
    rest = df.loc[~df["study_group"].eq(DOMINANT)].copy()

    rows = []
    for name, est in estimators().items():
        for subset_name, subset in [("all_rows", df), ("moosavi_only", dom), ("non_moosavi_only", rest)]:
            rows.append({
                "model": name,
                "experiment": "within_subset_random_cv",
                "subset": subset_name,
                **random_cv(subset, est),
            })

        rows.append({
            "model": name,
            "experiment": "cross_source_transfer",
            "subset": "train_moosavi_test_non_moosavi",
            **transfer(dom, rest, est),
        })
        rows.append({
            "model": name,
            "experiment": "cross_source_transfer",
            "subset": "train_non_moosavi_test_moosavi",
            **transfer(rest, dom, est),
        })

    result = pd.DataFrame(rows)
    result.to_csv(OUT_DIR / "source_dependency_ablation.csv", index=False)

    summary = {
        "dominant_source_label": DOMINANT,
        "all": target_summary(df),
        "moosavi": target_summary(dom),
        "non_moosavi": target_summary(rest),
        "dominant_row_share_percent": float(100 * len(dom) / len(df)),
        "interpretation_guardrail": (
            "Strong performance within the Moosavi subset is not evidence of independent "
            "generalisation. The decisive evidence is performance under reconstructed primary-"
            "study holdout, source-ablation stability, and truly external datasets."
        ),
    }
    (OUT_DIR / "source_dependency_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print("=== SOURCE-DEPENDENCY ABLATION ===")
    print(result.to_string(index=False))
    print("\n=== SOURCE / TARGET SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
