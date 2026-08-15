"""Source-dominance diagnostics for the ID-SEAD literature dataset.

This complements grouped CV by showing how much one large source controls the
row-weighted result and by measuring transfer between the dominant study and all
other studies.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

import study_aware_validation as base

OUT_DIR = Path(__file__).resolve().parent / "outputs"


def score(y, pred):
    out = {
        "n": int(len(y)),
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, pred))),
    }
    out["r2"] = float(r2_score(y, pred)) if len(y) >= 2 and np.std(y) > 0 else np.nan
    return out


def make_rf():
    return Pipeline(
        [
            ("prep", base.make_preprocessor()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=200,
                    min_samples_leaf=2,
                    random_state=base.RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def fit_transfer(train, test):
    model = make_rf()
    model.fit(train[base.RAW_FEATURES], train[base.TARGET].to_numpy(float))
    pred = model.predict(test[base.RAW_FEATURES])
    return score(test[base.TARGET].to_numpy(float), pred)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = base.load_data()

    stats = (
        df.groupby("study_group")[base.TARGET]
        .agg(rows="size", qe_min="min", qe_median="median", qe_mean="mean", qe_max="max", qe_std="std")
        .sort_values("rows", ascending=False)
        .reset_index()
    )
    stats["row_share_percent"] = 100 * stats["rows"] / len(df)
    stats.to_csv(OUT_DIR / "study_target_distribution.csv", index=False)

    dominant = stats.iloc[0]["study_group"]
    dominant_rows = int(stats.iloc[0]["rows"])
    dom_mask = df["study_group"].eq(dominant)
    dominant_df = df.loc[dom_mask].copy()
    other_df = df.loc[~dom_mask].copy()

    transfer = {
        "dominant_study": dominant,
        "dominant_rows": dominant_rows,
        "dominant_row_share_percent": float(100 * dominant_rows / len(df)),
        "train_others_test_dominant": fit_transfer(other_df, dominant_df),
        "train_dominant_test_others": fit_transfer(dominant_df, other_df),
    }
    (OUT_DIR / "dominant_study_transfer.json").write_text(
        json.dumps(transfer, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Leave-one-study-out: MAE/RMSE are defined even for one-row studies. R² is
    # only reported when the held-out study has >=2 non-constant targets.
    loso_rows = []
    for study, test in df.groupby("study_group"):
        train = df.loc[~df["study_group"].eq(study)]
        result = fit_transfer(train, test)
        loso_rows.append(
            {
                "study_group": study,
                "train_rows": int(len(train)),
                "test_rows": int(len(test)),
                **result,
            }
        )
    loso = pd.DataFrame(loso_rows).sort_values("test_rows", ascending=False)
    loso.to_csv(OUT_DIR / "leave_one_study_out_rf.csv", index=False)

    # Equal-study summary prevents the 251-row source from dominating every
    # descriptive transfer statistic.
    equal_study = {
        "n_studies": int(len(loso)),
        "median_study_mae": float(loso["mae"].median()),
        "mean_study_mae": float(loso["mae"].mean()),
        "median_study_rmse": float(loso["rmse"].median()),
        "mean_study_rmse": float(loso["rmse"].mean()),
        "studies_with_defined_r2": int(loso["r2"].notna().sum()),
        "median_defined_study_r2": float(loso["r2"].dropna().median()) if loso["r2"].notna().any() else None,
    }
    (OUT_DIR / "equal_study_summary.json").write_text(
        json.dumps(equal_study, indent=2), encoding="utf-8"
    )

    print("=== SOURCE DOMINANCE ===")
    print(stats.to_string(index=False))
    print("\n=== DOMINANT-STUDY TRANSFER ===")
    print(json.dumps(transfer, indent=2, ensure_ascii=False))
    print("\n=== LEAVE-ONE-STUDY-OUT RF ===")
    print(loso.to_string(index=False))
    print("\n=== EQUAL-STUDY SUMMARY ===")
    print(json.dumps(equal_study, indent=2))


if __name__ == "__main__":
    main()
