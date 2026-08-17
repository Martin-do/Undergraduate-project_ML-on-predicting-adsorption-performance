"""Final matched V2.1 validation after expanded provenance reconstruction.

Two populations are evaluated with identical rows under two split schemes:
1) all provenance-confirmed rows;
2) strict target-comparable/data-quality-passed rows.

For each population, compare shuffled row 5-fold CV against 5-fold GroupKFold by
reconstructed primary study. Uses the original engineered feature representation,
fold-safe preprocessing, and LR/SVR/RF/XGB/unconstrained Ridge stack. The legacy
Q_MAX=624 layer and removal_percent are not used for fitting.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import build_dataset_v21
import feature_parity_validation as fp
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor
import study_aware_validation as base

OUT = Path(__file__).resolve().parent / "outputs"
V21 = OUT / "adsorption_dataset_v2_1.csv"
OUT.mkdir(parents=True, exist_ok=True)
fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor


def load_v21() -> pd.DataFrame:
    build_dataset_v21.main()
    df = pd.read_csv(V21, encoding="utf-8-sig")
    for col in base.NUMERIC_FEATURES + [base.TARGET]:
        df[col] = df[col].map(base.parse_numeric)
    for col in base.CATEGORICAL_FEATURES:
        df[col] = df[col].astype("string").fillna("Unknown")
    if df[base.TARGET].isna().any():
        raise RuntimeError("V2.1 unexpectedly contains an unusable target after parsing")
    return df


def run_scope(df: pd.DataFrame, scope: str, mask: pd.Series):
    data = df.loc[mask].copy().reset_index(drop=True)
    groups = data["primary_study_id_v21"].astype(str).to_numpy()
    if (pd.Series(groups).str.strip() == "").any():
        raise RuntimeError(f"Blank primary-study ID inside {scope}")
    if pd.Series(groups).nunique() < 5:
        raise RuntimeError(f"Fewer than five study groups inside {scope}")

    frames = []
    fold_frames = []
    alpha_frames = []
    pred_frames = []
    count_frames = []

    schemes = [
        (f"{scope}__row_random_5fold", None),
        (f"{scope}__primary_group_5fold", groups),
    ]
    for scheme, scheme_groups in schemes:
        results, preds, folds, alphas, features = fp.evaluate_scheme(data, scheme, scheme_groups)
        frames.append(pd.DataFrame(results))
        fold_frames.append(pd.DataFrame(folds))
        alpha_frames.append(pd.DataFrame(alphas))
        pred_frames.append(pd.concat(preds, ignore_index=True))
        count_frames.append(pd.DataFrame(features))

    return {
        "metrics": pd.concat(frames, ignore_index=True),
        "folds": pd.concat(fold_frames, ignore_index=True),
        "alphas": pd.concat(alpha_frames, ignore_index=True),
        "predictions": pd.concat(pred_frames, ignore_index=True),
        "feature_counts": pd.concat(count_frames, ignore_index=True),
        "n_rows": int(len(data)),
        "n_studies": int(pd.Series(groups).nunique()),
    }


def main() -> None:
    df = load_v21()
    scopes = {
        "primary_confirmed_307": df["analysis_eligible_primary_provenance_v21"].astype(bool),
        "strict_comparable_273": df["analysis_eligible_strict_comparable_v21"].astype(bool),
    }

    outputs = {name: run_scope(df, name, mask) for name, mask in scopes.items()}
    metrics = pd.concat([o["metrics"] for o in outputs.values()], ignore_index=True)
    folds = pd.concat([o["folds"] for o in outputs.values()], ignore_index=True)
    alphas = pd.concat([o["alphas"] for o in outputs.values()], ignore_index=True)
    preds = pd.concat([o["predictions"] for o in outputs.values()], ignore_index=True)
    counts = pd.concat([o["feature_counts"] for o in outputs.values()], ignore_index=True)

    metrics.to_csv(OUT / "final_validation_v21_metrics.csv", index=False)
    folds.to_csv(OUT / "final_validation_v21_folds.csv", index=False)
    alphas.to_csv(OUT / "final_validation_v21_stack_alphas.csv", index=False)
    preds.to_csv(OUT / "final_validation_v21_predictions.csv", index=False)
    counts.to_csv(OUT / "final_validation_v21_feature_counts.csv", index=False)

    audit = {
        "dataset": "adsorption_dataset_v2_1.csv",
        "scopes": {
            name: {"rows": o["n_rows"], "primary_studies": o["n_studies"]}
            for name, o in outputs.items()
        },
        "same_rows_within_each_random_vs_group_comparison": True,
        "group_split": "5-fold GroupKFold by primary_study_id_v21",
        "random_split": "5-fold shuffled KFold, random_state=42",
        "models": ["LR", "SVR", "RF", "XGB", "STACK_RIDGE_UNCONSTRAINED"],
        "qmax_624_used": False,
        "removal_percent_used_as_predictor": False,
        "preprocessing": "fit within each outer and inner fold",
    }
    (OUT / "final_validation_v21_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )

    print("=== FINAL V2.1 MATCHED VALIDATION ===")
    print(json.dumps(audit, indent=2))
    print("\n=== METRICS ===")
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
