"""Training-only applicability-domain audit for precursor-restricted LOSO models.

The support rule is deliberately independent of held-out targets:

1. fit the fold-safe original-feature preprocessor on training studies only;
2. select continuous engineered/process descriptors with non-zero variation in
   the TRAINING fold and standardize them using training rows only;
3. for every *training* row, measure mean distance to its k nearest rows from
   OTHER training primary studies (not same-paper repeats);
4. define q95/q99 support thresholds from those cross-study training distances;
5. measure held-out rows against the training set using the identical space;
6. separately count engineered categorical levels not seen in training.

Training-constant continuous variables are excluded from that fold's distance.
Otherwise StandardScaler has no empirical scale to normalize a held-out change and
would leave the difference in the variable's original units, creating an arbitrary
mixed-unit distance artifact.

A strict supported prediction requires q95 continuous support AND zero novel
engineered categorical levels. No target value is used to decide support.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

import feature_parity_validation as fp
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor
import primary_study_holdout_validation as psh

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
DOMAIN_MAP = HERE / "adsorbent_domain_map.csv"
SUBSETS = ["broad_biogenic_waste", "waste_derived_carbon"]
MODELS = ["RF", "XGB"]
K_NEIGHBORS = 5
TRAIN_STD_MIN = 1e-8

CONTINUOUS_SUPPORT_FEATURES = [
    "surface_area_m2g",
    "particle_size_mm",
    "pore_volume_cm3g",
    "initial_concentration_mgL",
    "temperature_c",
    "contact_time_min",
    "ph",
    "dose_gL",
    "pyrolysis_temp_c",
    "conc_dose_ratio",
    "surface_area_x_pore_vol",
    "ph_x_temperature",
]

fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor


def cross_study_knn_distance(x: np.ndarray, groups: np.ndarray, k: int) -> np.ndarray:
    """Mean k-NN distance for each training row using only OTHER studies."""
    n = len(x)
    out = np.empty(n, dtype=float)
    for i in range(n):
        allowed = groups != groups[i]
        candidates = x[allowed]
        if len(candidates) == 0:
            raise ValueError("Need at least two training studies for cross-study support")
        dist = np.sqrt(np.sum((candidates - x[i]) ** 2, axis=1))
        kk = min(k, len(dist))
        out[i] = float(np.mean(np.partition(dist, kk - 1)[:kk]))
    return out


def test_knn_distance(x_train: np.ndarray, x_test: np.ndarray, k: int) -> np.ndarray:
    out = np.empty(len(x_test), dtype=float)
    for i, row in enumerate(x_test):
        dist = np.sqrt(np.sum((x_train - row) ** 2, axis=1))
        kk = min(k, len(dist))
        out[i] = float(np.mean(np.partition(dist, kk - 1)[:kk]))
    return out


def select_variable_support_features(xtr: np.ndarray, names: list[str]):
    """Return training-variable continuous feature names/indices and exclusions."""
    candidates = [c for c in CONTINUOUS_SUPPORT_FEATURES if c in names]
    candidate_idx = [names.index(c) for c in candidates]
    std = np.std(xtr[:, candidate_idx], axis=0, ddof=0)
    active_mask = np.isfinite(std) & (std > TRAIN_STD_MIN)
    active = [c for c, keep in zip(candidates, active_mask) if keep]
    active_idx = [i for i, keep in zip(candidate_idx, active_mask) if keep]
    excluded = [c for c, keep in zip(candidates, active_mask) if not keep]
    return active, active_idx, excluded


def category_novelty(prep: DtypeSafeParityPreprocessor, raw_test: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    engineered = fp.engineer_deterministic(raw_test).reset_index(drop=True)
    novelty = np.zeros(len(engineered), dtype=int)
    detail = [[] for _ in range(len(engineered))]
    for j, col in enumerate(fp.CAT_COLS):
        known = {str(v) for v in prep.encoder.categories_[j]}
        vals = engineered[col].astype(str).tolist()
        for i, val in enumerate(vals):
            if val not in known:
                novelty[i] += 1
                detail[i].append(f"{col}={val}")
    return novelty, [" | ".join(v) for v in detail]


def safe_metrics(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"n_rows": 0, "r2": np.nan, "rmse_mg_g": np.nan, "mae_mg_g": np.nan, "median_ae_mg_g": np.nan}
    y = frame["actual_qe_mg_g"].to_numpy(float)
    p = frame["predicted_qe_mg_g"].to_numpy(float)
    return {
        "n_rows": int(len(frame)),
        "r2": float(r2_score(y, p)) if len(frame) >= 2 and np.var(y) > 0 else np.nan,
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, p))),
        "mae_mg_g": float(mean_absolute_error(y, p)),
        "median_ae_mg_g": float(np.median(np.abs(y - p))),
    }


def main() -> None:
    confirmed, _, _ = psh.build_strict_dataset()
    dmap = pd.read_csv(DOMAIN_MAP, keep_default_na=False)
    confirmed = confirmed.merge(
        dmap[["project_adsorbent", *SUBSETS]].rename(columns={"project_adsorbent": "adsorbent"}),
        on="adsorbent", how="left", validate="many_to_one"
    )

    model_bank = fp.models()
    row_records = []
    fold_records = []

    for subset in SUBSETS:
        data = confirmed[confirmed[subset].eq("yes")].copy().reset_index(drop=True)
        groups = data["primary_study_id"].to_numpy(str)
        logo = LeaveOneGroupOut()
        y_all = data[psh.base.TARGET].to_numpy(float)
        raw_all = data[psh.base.RAW_FEATURES + ["removal_percent", "source_link"]].copy()

        for fold, (tr, te) in enumerate(logo.split(np.arange(len(data)), y_all, groups), start=1):
            train_groups = groups[tr]
            held_out_study = str(np.unique(groups[te])[0])
            prep = DtypeSafeParityPreprocessor().fit(raw_all.iloc[tr])
            xtr = prep.transform(raw_all.iloc[tr])
            xte = prep.transform(raw_all.iloc[te])
            names = list(prep.output_cols)
            continuous, idx, excluded_constant = select_variable_support_features(xtr, names)
            if len(continuous) < 5:
                raise RuntimeError(
                    f"Too few training-variable support features in fold {fold}: {continuous}; "
                    f"excluded={excluded_constant}"
                )

            support_scaler = StandardScaler().fit(xtr[:, idx])
            ztr = support_scaler.transform(xtr[:, idx])
            zte = support_scaler.transform(xte[:, idx])
            train_dist = cross_study_knn_distance(ztr, train_groups, K_NEIGHBORS)
            test_dist = test_knn_distance(ztr, zte, K_NEIGHBORS)
            q95 = float(np.quantile(train_dist, 0.95))
            q99 = float(np.quantile(train_dist, 0.99))
            novelty_count, novelty_detail = category_novelty(prep, raw_all.iloc[te])

            preds = {}
            for model_name in MODELS:
                m = clone(model_bank[model_name]).fit(xtr, y_all[tr])
                preds[model_name] = m.predict(xte)

            fold_records.append({
                "subset": subset,
                "fold": fold,
                "held_out_study": held_out_study,
                "train_rows": int(len(tr)),
                "test_rows": int(len(te)),
                "train_studies": int(len(np.unique(train_groups))),
                "continuous_candidate_features": int(len([c for c in CONTINUOUS_SUPPORT_FEATURES if c in names])),
                "continuous_active_features": int(len(continuous)),
                "active_feature_names": " | ".join(continuous),
                "excluded_training_constant_features": " | ".join(excluded_constant),
                "support_knn_k": K_NEIGHBORS,
                "train_cross_study_knn_q50": float(np.quantile(train_dist, 0.50)),
                "train_cross_study_knn_q95": q95,
                "train_cross_study_knn_q99": q99,
                "test_knn_mean": float(np.mean(test_dist)),
                "test_knn_min": float(np.min(test_dist)),
                "test_knn_max": float(np.max(test_dist)),
                "q95_continuous_supported_fraction": float(np.mean(test_dist <= q95)),
                "q95_strict_supported_fraction": float(np.mean((test_dist <= q95) & (novelty_count == 0))),
                "novel_category_fraction": float(np.mean(novelty_count > 0)),
            })

            for local_i, global_i in enumerate(te):
                base_rec = {
                    "subset": subset,
                    "fold": fold,
                    "held_out_study": held_out_study,
                    "subset_row_id": int(global_i),
                    "adsorbent": str(data.iloc[global_i]["adsorbent"]),
                    "actual_qe_mg_g": float(y_all[global_i]),
                    "cross_study_knn_distance": float(test_dist[local_i]),
                    "train_q95_threshold": q95,
                    "train_q99_threshold": q99,
                    "category_novelty_count": int(novelty_count[local_i]),
                    "category_novelty_detail": novelty_detail[local_i],
                    "continuous_supported_q95": bool(test_dist[local_i] <= q95),
                    "continuous_supported_q99": bool(test_dist[local_i] <= q99),
                    "strict_supported_q95": bool((test_dist[local_i] <= q95) and (novelty_count[local_i] == 0)),
                }
                for model_name, p in preds.items():
                    rec = dict(base_rec)
                    rec["model"] = model_name
                    rec["predicted_qe_mg_g"] = float(p[local_i])
                    rec["abs_error_mg_g"] = float(abs(y_all[global_i] - p[local_i]))
                    row_records.append(rec)

    rows = pd.DataFrame(row_records)
    folds = pd.DataFrame(fold_records)
    rows.to_csv(OUT / "applicability_domain_rows.csv", index=False)
    folds.to_csv(OUT / "applicability_domain_folds.csv", index=False)

    summaries = []
    for (subset, model), g in rows.groupby(["subset", "model"], sort=False):
        for rule, mask in [
            ("all", np.ones(len(g), dtype=bool)),
            ("continuous_q95", g["continuous_supported_q95"].to_numpy(bool)),
            ("strict_q95", g["strict_supported_q95"].to_numpy(bool)),
            ("continuous_q99", g["continuous_supported_q99"].to_numpy(bool)),
        ]:
            s = g.loc[mask]
            met = safe_metrics(s)
            summaries.append({
                "subset": subset,
                "model": model,
                "support_rule": rule,
                "coverage_fraction": float(len(s) / len(g)),
                **met,
            })
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(OUT / "applicability_domain_performance_by_support.csv", index=False)

    study_rows = []
    for (subset, model, study), g in rows.groupby(["subset", "model", "held_out_study"], sort=False):
        study_rows.append({
            "subset": subset,
            "model": model,
            "held_out_study": study,
            "n_rows": int(len(g)),
            "mae_mg_g": float(g["abs_error_mg_g"].mean()),
            "median_ae_mg_g": float(g["abs_error_mg_g"].median()),
            "mean_knn_distance": float(g["cross_study_knn_distance"].mean()),
            "max_knn_distance": float(g["cross_study_knn_distance"].max()),
            "continuous_q95_supported_fraction": float(g["continuous_supported_q95"].mean()),
            "strict_q95_supported_fraction": float(g["strict_supported_q95"].mean()),
            "novel_category_fraction": float((g["category_novelty_count"] > 0).mean()),
        })
    study_df = pd.DataFrame(study_rows)
    study_df.to_csv(OUT / "applicability_domain_per_study.csv", index=False)

    corr_rows = []
    for (subset, model), g in rows.groupby(["subset", "model"], sort=False):
        corr_rows.append({
            "subset": subset,
            "model": model,
            "spearman_distance_vs_abs_error": float(g["cross_study_knn_distance"].corr(g["abs_error_mg_g"], method="spearman")),
            "pearson_distance_vs_abs_error": float(g["cross_study_knn_distance"].corr(g["abs_error_mg_g"], method="pearson")),
        })
    corr_df = pd.DataFrame(corr_rows)
    corr_df.to_csv(OUT / "applicability_domain_error_distance_correlation.csv", index=False)

    audit = {
        "subsets": SUBSETS,
        "models": MODELS,
        "continuous_support_candidates": CONTINUOUS_SUPPORT_FEATURES,
        "training_std_min": TRAIN_STD_MIN,
        "fold_constant_feature_rule": "exclude from distance whenever training standard deviation <= threshold",
        "reason": "a training-constant variable has no data-derived scale; retaining its held-out difference would mix original units into standardized Euclidean distance",
        "support_knn_k": K_NEIGHBORS,
        "thresholds": "q95 and q99 of training-row cross-primary-study kNN distance, computed independently within each LOSO fold",
        "strict_rule": "q95 continuous support AND zero engineered categorical novelty",
        "target_used_for_support_decision": False,
        "legacy_qmax_used": False,
    }
    (OUT / "applicability_domain_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    print("=== APPLICABILITY DOMAIN AUDIT ===")
    print(json.dumps(audit, indent=2))
    print("\n=== FOLD FEATURE SELECTION ===")
    print(folds[["subset", "held_out_study", "continuous_active_features", "excluded_training_constant_features"]].to_string(index=False))
    print("\n=== PERFORMANCE BY SUPPORT ===")
    print(summary_df.to_string(index=False))
    print("\n=== PER-STUDY SUPPORT + ERROR ===")
    print(study_df.to_string(index=False))
    print("\n=== ERROR-DISTANCE CORRELATION ===")
    print(corr_df.to_string(index=False))


if __name__ == "__main__":
    main()
