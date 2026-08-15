"""Leakage-aware comparison of the original ID-SEAD model family.

This stage tests LR, SVR, RF, XGB and an UNCONSTRAINED Ridge stack using the
same outer folds. The physical-constraint penalty is intentionally excluded
because the legacy Q_MAX=624 mg/g has failed the data-consistency audit.

The Moosavi secondary-compilation proxy remains a sensitivity grouping, not a
final primary-provenance split.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR

try:
    from xgboost import XGBRegressor
except Exception as exc:  # pragma: no cover
    raise RuntimeError("xgboost is required for model_family_validation.py") from exc

import grouping_sensitivity as grouping
import study_aware_validation as base

OUT_DIR = Path(__file__).resolve().parent / "outputs"
ALPHAS = [0.01, 0.05, 0.1, 0.5, 1.0]
N_SPLITS = 5


def estimators():
    # These match the selected/tuned settings recorded in the original notebook.
    return {
        "LR": LinearRegression(),
        "SVR": SVR(kernel="rbf", C=10, epsilon=0.1),
        "RF": RandomForestRegressor(
            n_estimators=200,
            max_depth=None,
            min_samples_split=3,
            random_state=base.RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGB": XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            objective="reg:squarederror",
            random_state=base.RANDOM_STATE,
            verbosity=0,
            n_jobs=-1,
        ),
    }


def pipe(model):
    return Pipeline([("prep", base.make_preprocessor()), ("model", model)])


def metrics(y, pred):
    pred_nonneg = np.maximum(pred, 0)
    return {
        "r2": float(r2_score(y, pred)),
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, pred))),
        "mae_mg_g": float(mean_absolute_error(y, pred)),
        "median_ae_mg_g": float(np.median(np.abs(y - pred))),
        "rmsle": float(np.sqrt(np.mean((np.log1p(y) - np.log1p(pred_nonneg)) ** 2))),
    }


def splitter_for(groups, n_rows, seed_offset=0):
    if groups is None:
        return KFold(
            n_splits=N_SPLITS,
            shuffle=True,
            random_state=base.RANDOM_STATE + seed_offset,
        )
    return GroupKFold(n_splits=min(N_SPLITS, len(np.unique(groups))))


def split_iter(splitter, X, y, groups):
    return splitter.split(X, y) if groups is None else splitter.split(X, y, groups)


def choose_alpha(meta_x, y, groups):
    """Choose Ridge alpha using leakage-aware CV on OOF meta-features."""
    cv = splitter_for(groups, len(y), seed_offset=17)
    scores = []
    for alpha in ALPHAS:
        fold_scores = []
        for tr, va in split_iter(cv, meta_x, y, groups):
            m = Ridge(alpha=alpha)
            m.fit(meta_x[tr], y[tr])
            p = m.predict(meta_x[va])
            fold_scores.append(r2_score(y[va], p))
        scores.append((float(np.mean(fold_scores)), alpha))
    return max(scores, key=lambda x: x[0])[1]


def oof_meta_features(X, y, groups):
    """Generate inner OOF base predictions using only inner-training data."""
    inner_cv = splitter_for(groups, len(y), seed_offset=31)
    meta = np.empty((len(y), 4), dtype=float)
    model_names = list(estimators().keys())

    for tr, va in split_iter(inner_cv, X, y, groups):
        for j, (name, est) in enumerate(estimators().items()):
            m = pipe(clone(est))
            m.fit(X.iloc[tr], y[tr])
            meta[va, j] = m.predict(X.iloc[va])
    return meta, model_names


def outer_validation(df, scheme_name, groups):
    X = df[base.RAW_FEATURES].copy()
    y = df[base.TARGET].to_numpy(float)
    outer_cv = splitter_for(groups, len(y))

    pred_store = {name: np.empty(len(y), dtype=float) for name in estimators()}
    pred_store["STACK_RIDGE_UNCONSTRAINED"] = np.empty(len(y), dtype=float)
    alpha_by_fold = []
    fold_integrity = []

    for fold, (tr, te) in enumerate(split_iter(outer_cv, X, y, groups), start=1):
        gtr = None if groups is None else groups[tr]
        gte = None if groups is None else groups[te]

        # Individual models on identical outer split.
        fitted_full = {}
        for name, est in estimators().items():
            m = pipe(clone(est))
            m.fit(X.iloc[tr], y[tr])
            pred_store[name][te] = m.predict(X.iloc[te])
            fitted_full[name] = m

        # Inner group-safe OOF predictions for the meta-learner.
        meta_train, names = oof_meta_features(X.iloc[tr].reset_index(drop=True), y[tr], gtr)
        alpha = choose_alpha(meta_train, y[tr], gtr)
        meta_model = Ridge(alpha=alpha)
        meta_model.fit(meta_train, y[tr])

        meta_test = np.column_stack([fitted_full[n].predict(X.iloc[te]) for n in names])
        pred_store["STACK_RIDGE_UNCONSTRAINED"][te] = meta_model.predict(meta_test)
        alpha_by_fold.append({"scheme": scheme_name, "fold": fold, "ridge_alpha": alpha})

        overlap = None
        if groups is not None:
            overlap = len(set(gtr).intersection(set(gte)))
        fold_integrity.append(
            {
                "scheme": scheme_name,
                "fold": fold,
                "train_rows": int(len(tr)),
                "test_rows": int(len(te)),
                "outer_group_overlap": overlap,
            }
        )

    result_rows = []
    pred_frames = []
    for name, pred in pred_store.items():
        result_rows.append(
            {
                "scheme": scheme_name,
                "model": name,
                "n_rows": int(len(y)),
                "n_groups": None if groups is None else int(len(np.unique(groups))),
                **metrics(y, pred),
            }
        )
        pred_frames.append(
            pd.DataFrame(
                {
                    "row_id": np.arange(len(y)),
                    "actual_qe_mg_g": y,
                    "predicted_qe_mg_g": pred,
                    "study_group": df["study_group"].astype(str),
                    "model": name,
                    "scheme": scheme_name,
                }
            )
        )
    return result_rows, pred_frames, alpha_by_fold, fold_integrity


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = base.load_data()
    schemes = grouping.build_groups(df)

    # Keep all four views for transparency. `secondary_system_proxy` is the
    # working bracketing split until original primary-paper IDs are reconstructed.
    results, preds, alphas, folds = [], [], [], []
    for scheme_name in ["row_random", "citation_strict", "secondary_system_proxy", "adsorbent_holdout"]:
        r, p, a, f = outer_validation(df, scheme_name, schemes[scheme_name])
        results.extend(r)
        preds.extend(p)
        alphas.extend(a)
        folds.extend(f)

    result_df = pd.DataFrame(results)
    result_df.to_csv(OUT_DIR / "model_family_grouped_comparison.csv", index=False)
    pd.concat(preds, ignore_index=True).to_csv(
        OUT_DIR / "model_family_oof_predictions.csv", index=False
    )
    pd.DataFrame(alphas).to_csv(OUT_DIR / "stack_ridge_alpha_by_fold.csv", index=False)
    pd.DataFrame(folds).to_csv(OUT_DIR / "model_family_fold_integrity.csv", index=False)

    print("=== LEAKAGE-AWARE MODEL FAMILY COMPARISON ===")
    print(result_df.to_string(index=False))
    print("\nNote: constrained ID-SEAD is intentionally excluded until Q_MAX/domain is repaired.")


if __name__ == "__main__":
    main()
