"""Sensitivity analysis for provenance granularity and target scale.

The dominant Moosavi citation appears to represent a secondary literature
compilation rather than one primary study. This script brackets the validation
result under several grouping assumptions instead of treating either extreme as
truth.

Grouping schemes
----------------
row_random:
    Ordinary shuffled row-wise KFold (legacy optimistic reference only).
citation_strict:
    Group by source_link. Conservative for the secondary Moosavi compilation.
secondary_system_proxy:
    For the Moosavi compilation only, split into material/process/pollutant
    systems; retain source_link groups for all other citations. This is a
    PROVISIONAL proxy, not a substitute for primary-paper provenance.
adsorbent_holdout:
    Group by normalized adsorbent identity globally; tests transfer to unseen
    adsorbents/material labels.

Target scales
-------------
raw:
    Fit qe directly.
log1p:
    Fit log1p(qe), back-transform predictions, and report metrics on the
    original mg/g scale plus RMSLE. This tests sensitivity to the extreme
    0.025--2239 mg/g dynamic range without deleting high-capacity observations.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import Pipeline

import study_aware_validation as base

OUT_DIR = Path(__file__).resolve().parent / "outputs"
DOMINANT = "moosavi et al., 2023"
N_SPLITS = 5


def norm_token(x):
    if pd.isna(x):
        return "unknown"
    return re.sub(r"\s+", " ", str(x).strip().lower()) or "unknown"


def build_groups(df: pd.DataFrame) -> dict[str, np.ndarray | None]:
    citation = df["study_group"].astype(str).to_numpy()

    proxy = []
    for _, r in df.iterrows():
        if r["study_group"] == DOMINANT:
            proxy.append(
                "secondary-system::"
                + "::".join(
                    [
                        norm_token(r["adsorbent"]),
                        norm_token(r["method_processing"]),
                        norm_token(r["pollutant"]),
                    ]
                )
            )
        else:
            proxy.append("citation::" + str(r["study_group"]))

    adsorbent = df["adsorbent"].map(norm_token).map(lambda x: "adsorbent::" + x).to_numpy()

    return {
        "row_random": None,
        "citation_strict": citation,
        "secondary_system_proxy": np.asarray(proxy, dtype=object),
        "adsorbent_holdout": adsorbent,
    }


def make_model():
    return Pipeline(
        [
            ("prep", base.make_preprocessor()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=300,
                    min_samples_leaf=2,
                    random_state=base.RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def metric_row(y, pred):
    pred_nonneg = np.maximum(pred, 0)
    return {
        "r2": float(r2_score(y, pred)),
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, pred))),
        "mae_mg_g": float(mean_absolute_error(y, pred)),
        "rmsle": float(np.sqrt(np.mean((np.log1p(y) - np.log1p(pred_nonneg)) ** 2))),
        "median_absolute_error_mg_g": float(np.median(np.abs(y - pred))),
    }


def cv_predict(df, groups, target_scale):
    X = df[base.RAW_FEATURES]
    y_raw = df[base.TARGET].to_numpy(float)
    y_fit = np.log1p(y_raw) if target_scale == "log1p" else y_raw

    if groups is None:
        splitter = KFold(n_splits=N_SPLITS, shuffle=True, random_state=base.RANDOM_STATE)
        splits = splitter.split(X, y_fit)
    else:
        n_groups = len(np.unique(groups))
        splitter = GroupKFold(n_splits=min(N_SPLITS, n_groups))
        splits = splitter.split(X, y_fit, groups=groups)

    pred_fit = np.empty(len(df), dtype=float)
    fold_rows = []
    for fold, (tr, te) in enumerate(splits, start=1):
        model = make_model()
        model.fit(X.iloc[tr], y_fit[tr])
        pf = model.predict(X.iloc[te])
        pred_fit[te] = pf

        if groups is not None:
            train_groups = set(groups[tr])
            test_groups = set(groups[te])
            overlap = len(train_groups.intersection(test_groups))
        else:
            overlap = None
        fold_rows.append(
            {
                "fold": fold,
                "train_rows": int(len(tr)),
                "test_rows": int(len(te)),
                "group_overlap": overlap,
            }
        )

    pred_raw = np.expm1(pred_fit) if target_scale == "log1p" else pred_fit
    return pred_raw, fold_rows


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = base.load_data()
    schemes = build_groups(df)

    scheme_info = []
    results = []
    all_preds = []
    fold_records = []

    for scheme, groups in schemes.items():
        scheme_info.append(
            {
                "scheme": scheme,
                "n_groups": None if groups is None else int(len(np.unique(groups))),
                "largest_group_rows": None
                if groups is None
                else int(pd.Series(groups).value_counts().max()),
                "description": {
                    "row_random": "shuffled row-wise KFold; optimistic reference only",
                    "citation_strict": "one group per source_link; over-groups secondary compilation",
                    "secondary_system_proxy": "Moosavi rows split by adsorbent+processing+pollutant; provisional provenance proxy",
                    "adsorbent_holdout": "one group per adsorbent label; tests unseen-material transfer",
                }[scheme],
            }
        )

        for target_scale in ["raw", "log1p"]:
            pred, folds = cv_predict(df, groups, target_scale)
            m = metric_row(df[base.TARGET].to_numpy(float), pred)
            results.append(
                {
                    "scheme": scheme,
                    "target_scale": target_scale,
                    "n_rows": int(len(df)),
                    "n_groups": None if groups is None else int(len(np.unique(groups))),
                    **m,
                }
            )
            for f in folds:
                fold_records.append({"scheme": scheme, "target_scale": target_scale, **f})
            all_preds.append(
                pd.DataFrame(
                    {
                        "row_id": np.arange(len(df)),
                        "study_group": df["study_group"].astype(str),
                        "adsorbent": df["adsorbent"].astype(str),
                        "pollutant": df["pollutant"].astype(str),
                        "actual_qe_mg_g": df[base.TARGET].to_numpy(float),
                        "predicted_qe_mg_g": pred,
                        "scheme": scheme,
                        "target_scale": target_scale,
                    }
                )
            )

    pd.DataFrame(results).to_csv(OUT_DIR / "grouping_target_scale_sensitivity.csv", index=False)
    pd.DataFrame(scheme_info).to_csv(OUT_DIR / "grouping_scheme_summary.csv", index=False)
    pd.DataFrame(fold_records).to_csv(OUT_DIR / "grouping_fold_integrity.csv", index=False)
    pd.concat(all_preds, ignore_index=True).to_csv(
        OUT_DIR / "grouping_sensitivity_predictions.csv", index=False
    )

    guardrail = {
        "status": "sensitivity_only",
        "primary_provenance_not_locked": True,
        "reason": (
            "The dominant Moosavi-labelled rows originate from a secondary literature compilation. "
            "The secondary_system_proxy grouping is a bracketing analysis only. Final study-aware "
            "validation requires row-level recovery of the underlying primary literature sources."
        ),
    }
    (OUT_DIR / "grouping_sensitivity_guardrail.json").write_text(
        json.dumps(guardrail, indent=2), encoding="utf-8"
    )

    print("=== GROUPING SCHEMES ===")
    print(pd.DataFrame(scheme_info).to_string(index=False))
    print("\n=== GROUPING / TARGET-SCALE SENSITIVITY ===")
    print(pd.DataFrame(results).to_string(index=False))
    print("\nGuardrail:")
    print(json.dumps(guardrail, indent=2))


if __name__ == "__main__":
    main()
