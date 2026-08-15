"""Study-aware empirical residual-interval diagnostic for restricted domains.

This is intentionally NOT labelled formal conformal prediction. The literature
studies are heterogeneous, rows within studies are dependent, and only 6-7 primary
studies are available in the candidate domains.

For every OUTER leave-one-primary-study-out fold:
- use only outer-training studies to create INNER leave-one-study-out predictions;
- calculate XGB absolute residuals and RF-XGB prediction disagreement;
- give each inner held-out study equal total calibration weight;
- derive empirical 90% and 95% residual quantiles;
- fit RF/XGB on all outer-training studies and evaluate intervals on the untouched
  outer-held-out primary study.

Two interval forms are audited:
1. fixed: XGB prediction +/- study-balanced residual quantile;
2. disagreement-scaled: XGB prediction +/- quantile(residual/scale) * scale,
   where scale = median inner disagreement + RF-XGB disagreement.

No outer-test target or feature is used to calibrate interval width.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import LeaveOneGroupOut

import feature_parity_validation as fp
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor
import primary_study_holdout_validation as psh

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
DOMAIN_MAP = HERE / "adsorbent_domain_map.csv"
SUBSETS = ["broad_biogenic_waste", "waste_derived_carbon"]
LEVELS = [0.90, 0.95]
EPS = 1e-9

fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if len(values) == 0 or len(values) != len(weights):
        raise ValueError("Invalid weighted quantile input")
    order = np.argsort(values)
    v = values[order]
    w = weights[order]
    total = float(w.sum())
    if total <= 0:
        raise ValueError("Calibration weights must sum to a positive value")
    cumulative = np.cumsum(w) / total
    return float(v[min(np.searchsorted(cumulative, q, side="left"), len(v) - 1)])


def fit_predict_pair(raw_train: pd.DataFrame, y_train: np.ndarray, raw_test: pd.DataFrame):
    prep = DtypeSafeParityPreprocessor().fit(raw_train)
    xtr = prep.transform(raw_train)
    xte = prep.transform(raw_test)
    bank = fp.models()
    rf = clone(bank["RF"]).fit(xtr, y_train)
    xgb = clone(bank["XGB"]).fit(xtr, y_train)
    return rf.predict(xte), xgb.predict(xte)


def inner_calibration(raw_train: pd.DataFrame, y_train: np.ndarray, groups_train: np.ndarray) -> pd.DataFrame:
    logo = LeaveOneGroupOut()
    frames = []
    row_index = np.arange(len(raw_train))
    for inner_fold, (itr, iva) in enumerate(logo.split(row_index, y_train, groups_train), start=1):
        rf_pred, xgb_pred = fit_predict_pair(
            raw_train.iloc[itr], y_train[itr], raw_train.iloc[iva]
        )
        held = groups_train[iva]
        frames.append(pd.DataFrame({
            "inner_fold": inner_fold,
            "inner_held_out_study": held,
            "actual": y_train[iva],
            "rf_pred": rf_pred,
            "xgb_pred": xgb_pred,
            "abs_residual": np.abs(y_train[iva] - xgb_pred),
            "rf_xgb_disagreement": np.abs(rf_pred - xgb_pred),
        }))
    cal = pd.concat(frames, ignore_index=True)
    counts = cal.groupby("inner_held_out_study").size().to_dict()
    cal["equal_study_weight"] = cal["inner_held_out_study"].map(lambda s: 1.0 / counts[s])
    return cal


def main() -> None:
    confirmed, _, _ = psh.build_strict_dataset()
    dmap = pd.read_csv(DOMAIN_MAP, keep_default_na=False)
    confirmed = confirmed.merge(
        dmap[["project_adsorbent", *SUBSETS]].rename(columns={"project_adsorbent": "adsorbent"}),
        on="adsorbent", how="left", validate="many_to_one"
    )

    prediction_rows = []
    fold_rows = []
    calibration_rows = []

    for subset in SUBSETS:
        data = confirmed[confirmed[subset].eq("yes")].copy().reset_index(drop=True)
        groups = data["primary_study_id"].to_numpy(str)
        y = data[psh.base.TARGET].to_numpy(float)
        raw = data[psh.base.RAW_FEATURES + ["removal_percent", "source_link"]].copy()
        logo = LeaveOneGroupOut()

        for outer_fold, (tr, te) in enumerate(logo.split(np.arange(len(data)), y, groups), start=1):
            held_out = str(np.unique(groups[te])[0])
            gtr = groups[tr]
            cal = inner_calibration(raw.iloc[tr].reset_index(drop=True), y[tr], gtr)
            median_disagreement = float(np.median(cal["rf_xgb_disagreement"]))
            baseline_scale = max(median_disagreement, EPS)
            cal["disagreement_scale"] = baseline_scale + cal["rf_xgb_disagreement"]
            cal["scaled_score"] = cal["abs_residual"] / cal["disagreement_scale"]
            cal["outer_subset"] = subset
            cal["outer_fold"] = outer_fold
            cal["outer_held_out_study"] = held_out
            calibration_rows.append(cal)

            rf_test, xgb_test = fit_predict_pair(raw.iloc[tr], y[tr], raw.iloc[te])
            test_disagreement = np.abs(rf_test - xgb_test)
            test_scale = baseline_scale + test_disagreement

            for level in LEVELS:
                fixed_half = weighted_quantile(
                    cal["abs_residual"].to_numpy(),
                    cal["equal_study_weight"].to_numpy(),
                    level,
                )
                scaled_q = weighted_quantile(
                    cal["scaled_score"].to_numpy(),
                    cal["equal_study_weight"].to_numpy(),
                    level,
                )

                fixed_lower = xgb_test - fixed_half
                fixed_upper = xgb_test + fixed_half
                scaled_half = scaled_q * test_scale
                scaled_lower = xgb_test - scaled_half
                scaled_upper = xgb_test + scaled_half
                fixed_covered = (y[te] >= fixed_lower) & (y[te] <= fixed_upper)
                scaled_covered = (y[te] >= scaled_lower) & (y[te] <= scaled_upper)

                fold_rows.extend([
                    {
                        "subset": subset,
                        "outer_fold": outer_fold,
                        "held_out_study": held_out,
                        "level": level,
                        "interval_type": "fixed_equal_study_residual",
                        "test_rows": int(len(te)),
                        "inner_calibration_rows": int(len(cal)),
                        "inner_calibration_studies": int(cal["inner_held_out_study"].nunique()),
                        "median_inner_rf_xgb_disagreement": median_disagreement,
                        "calibrated_half_width_or_multiplier": fixed_half,
                        "empirical_coverage": float(np.mean(fixed_covered)),
                        "mean_interval_width_mg_g": float(2.0 * fixed_half),
                        "median_interval_width_mg_g": float(2.0 * fixed_half),
                        "mean_abs_error_mg_g": float(np.mean(np.abs(y[te] - xgb_test))),
                        "mean_rf_xgb_disagreement": float(np.mean(test_disagreement)),
                    },
                    {
                        "subset": subset,
                        "outer_fold": outer_fold,
                        "held_out_study": held_out,
                        "level": level,
                        "interval_type": "rf_xgb_disagreement_scaled",
                        "test_rows": int(len(te)),
                        "inner_calibration_rows": int(len(cal)),
                        "inner_calibration_studies": int(cal["inner_held_out_study"].nunique()),
                        "median_inner_rf_xgb_disagreement": median_disagreement,
                        "calibrated_half_width_or_multiplier": scaled_q,
                        "empirical_coverage": float(np.mean(scaled_covered)),
                        "mean_interval_width_mg_g": float(np.mean(2.0 * scaled_half)),
                        "median_interval_width_mg_g": float(np.median(2.0 * scaled_half)),
                        "mean_abs_error_mg_g": float(np.mean(np.abs(y[te] - xgb_test))),
                        "mean_rf_xgb_disagreement": float(np.mean(test_disagreement)),
                    },
                ])

                for local_i, global_i in enumerate(te):
                    for interval_type, lower, upper, half, covered in [
                        ("fixed_equal_study_residual", fixed_lower, fixed_upper, np.full(len(te), fixed_half), fixed_covered),
                        ("rf_xgb_disagreement_scaled", scaled_lower, scaled_upper, scaled_half, scaled_covered),
                    ]:
                        prediction_rows.append({
                            "subset": subset,
                            "outer_fold": outer_fold,
                            "held_out_study": held_out,
                            "subset_row_id": int(global_i),
                            "adsorbent": str(data.iloc[global_i]["adsorbent"]),
                            "level": level,
                            "interval_type": interval_type,
                            "actual_qe_mg_g": float(y[global_i]),
                            "xgb_prediction_mg_g": float(xgb_test[local_i]),
                            "rf_prediction_mg_g": float(rf_test[local_i]),
                            "rf_xgb_disagreement_mg_g": float(test_disagreement[local_i]),
                            "lower_mg_g": float(lower[local_i]),
                            "upper_mg_g": float(upper[local_i]),
                            "interval_width_mg_g": float(2.0 * half[local_i]),
                            "covered": bool(covered[local_i]),
                            "abs_error_mg_g": float(abs(y[global_i] - xgb_test[local_i])),
                        })

    predictions = pd.DataFrame(prediction_rows)
    folds = pd.DataFrame(fold_rows)
    calibration = pd.concat(calibration_rows, ignore_index=True)
    predictions.to_csv(OUT / "group_aware_uncertainty_predictions.csv", index=False)
    folds.to_csv(OUT / "group_aware_uncertainty_per_study.csv", index=False)
    calibration.to_csv(OUT / "group_aware_uncertainty_inner_calibration.csv", index=False)

    summary_rows = []
    for (subset, level, interval_type), g in predictions.groupby(["subset", "level", "interval_type"], sort=False):
        study_cov = g.groupby("held_out_study")["covered"].mean()
        study_width = g.groupby("held_out_study")["interval_width_mg_g"].mean()
        summary_rows.append({
            "subset": subset,
            "level": level,
            "interval_type": interval_type,
            "rows": int(len(g)),
            "studies": int(g["held_out_study"].nunique()),
            "row_weighted_coverage": float(g["covered"].mean()),
            "equal_study_mean_coverage": float(study_cov.mean()),
            "studies_with_zero_coverage": int((study_cov == 0).sum()),
            "mean_interval_width_mg_g": float(g["interval_width_mg_g"].mean()),
            "equal_study_mean_width_mg_g": float(study_width.mean()),
            "median_interval_width_mg_g": float(g["interval_width_mg_g"].median()),
        })
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "group_aware_uncertainty_summary.csv", index=False)

    study_failure = folds.sort_values(
        ["subset", "level", "interval_type", "empirical_coverage", "mean_abs_error_mg_g"],
        ascending=[True, True, True, True, False]
    )
    study_failure.to_csv(OUT / "group_aware_uncertainty_study_failures.csv", index=False)

    audit = {
        "subsets": SUBSETS,
        "outer_validation": "leave-one-primary-study-out",
        "inner_calibration": "leave-one-primary-study-out within outer-training studies only",
        "calibration_weighting": "each inner-held-out study has equal total weight",
        "prediction_model": "XGB original-feature parity model",
        "uncertainty_signals": ["absolute inner XGB residual", "RF-XGB disagreement"],
        "levels": LEVELS,
        "formal_conformal_guarantee_claimed": False,
        "reason_no_formal_guarantee": "few heterogeneous studies and dependent rows within studies",
        "outer_test_used_for_calibration": False,
    }
    (OUT / "group_aware_uncertainty_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    print("=== GROUP-AWARE UNCERTAINTY AUDIT ===")
    print(json.dumps(audit, indent=2))
    print("\n=== SUMMARY ===")
    print(summary.to_string(index=False))
    print("\n=== PER-STUDY COVERAGE / WIDTH / ERROR ===")
    print(study_failure.to_string(index=False))


if __name__ == "__main__":
    main()
