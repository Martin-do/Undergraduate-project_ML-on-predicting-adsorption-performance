"""Feature-level diagnosis of the corrected cross-study applicability distances.

For every LOSO fold and held-out row this script identifies the k nearest training
rows in the same training-standardized continuous space used by the applicability
audit, then decomposes squared distance by ACTIVE feature.

Candidate variables with zero/near-zero training variation are explicitly recorded
but excluded from distance, because a training-constant variable has no empirical
scale with which to normalize a held-out difference.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

import applicability_domain_validation as ad
import primary_study_holdout_validation as psh
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
DOMAIN_MAP = HERE / "adsorbent_domain_map.csv"
SUBSETS = ["broad_biogenic_waste", "waste_derived_carbon"]
K = ad.K_NEIGHBORS


def nearest_indices(ztr: np.ndarray, row: np.ndarray, k: int) -> np.ndarray:
    d2 = np.sum((ztr - row) ** 2, axis=1)
    kk = min(k, len(d2))
    return np.argpartition(d2, kk - 1)[:kk]


def main() -> None:
    confirmed, _, _ = psh.build_strict_dataset()
    dmap = pd.read_csv(DOMAIN_MAP, keep_default_na=False)
    confirmed = confirmed.merge(
        dmap[["project_adsorbent", *SUBSETS]].rename(columns={"project_adsorbent": "adsorbent"}),
        on="adsorbent", how="left", validate="many_to_one"
    )

    point_rows = []
    fold_feature_rows = []
    study_feature_rows = []

    for subset in SUBSETS:
        data = confirmed[confirmed[subset].eq("yes")].copy().reset_index(drop=True)
        groups = data["primary_study_id"].to_numpy(str)
        y = data[psh.base.TARGET].to_numpy(float)
        raw = data[psh.base.RAW_FEATURES + ["removal_percent", "source_link"]].copy()
        logo = LeaveOneGroupOut()

        for fold, (tr, te) in enumerate(logo.split(np.arange(len(data)), y, groups), start=1):
            held_out = str(np.unique(groups[te])[0])
            prep = DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
            xtr = prep.transform(raw.iloc[tr])
            xte = prep.transform(raw.iloc[te])
            names = list(prep.output_cols)
            features, idx, excluded = ad.select_variable_support_features(xtr, names)

            # Record geometry for ALL candidate features so exclusions are auditable.
            candidates = [f for f in ad.CONTINUOUS_SUPPORT_FEATURES if f in names]
            for feat in candidates:
                j_all = names.index(feat)
                train_vals = xtr[:, j_all]
                test_vals = xte[:, j_all]
                train_std = float(np.std(train_vals, ddof=0))
                fold_feature_rows.append({
                    "subset": subset,
                    "fold": fold,
                    "held_out_study": held_out,
                    "feature": feat,
                    "active_in_distance": bool(feat in features),
                    "excluded_training_constant": bool(feat in excluded),
                    "train_mean_pre_support_scale": float(np.mean(train_vals)),
                    "train_std_pre_support_scale": train_std,
                    "train_min_pre_support_scale": float(np.min(train_vals)),
                    "train_max_pre_support_scale": float(np.max(train_vals)),
                    "test_min_pre_support_scale": float(np.min(test_vals)),
                    "test_max_pre_support_scale": float(np.max(test_vals)),
                    "inactive_in_parity_preprocessor": bool(feat in getattr(prep, "inactive_training_features", set())),
                })

            support_input_train = xtr[:, idx]
            support_input_test = xte[:, idx]
            scaler = StandardScaler().fit(support_input_train)
            ztr = scaler.transform(support_input_train)
            zte = scaler.transform(support_input_test)

            held_feature_accumulator = {f: [] for f in features}
            held_fraction_accumulator = {f: [] for f in features}

            for local_i, global_i in enumerate(te):
                nbr = nearest_indices(ztr, zte[local_i], K)
                diffs = ztr[nbr] - zte[local_i]
                mean_sq = np.mean(diffs ** 2, axis=0)
                total_sq = float(np.sum(mean_sq))
                fractions = mean_sq / total_sq if total_sq > 0 else np.zeros_like(mean_sq)
                mean_euclid = float(np.mean(np.sqrt(np.sum(diffs ** 2, axis=1))))

                for j, feat in enumerate(features):
                    held_feature_accumulator[feat].append(float(mean_sq[j]))
                    held_fraction_accumulator[feat].append(float(fractions[j]))
                    point_rows.append({
                        "subset": subset,
                        "fold": fold,
                        "held_out_study": held_out,
                        "subset_row_id": int(global_i),
                        "adsorbent": str(data.iloc[global_i]["adsorbent"]),
                        "actual_qe_mg_g": float(y[global_i]),
                        "feature": feat,
                        "mean_squared_standardized_difference_to_k_neighbors": float(mean_sq[j]),
                        "fraction_of_total_squared_difference": float(fractions[j]),
                        "mean_euclidean_knn_distance": mean_euclid,
                    })

            for feat in features:
                vals = np.asarray(held_feature_accumulator[feat], dtype=float)
                fracs = np.asarray(held_fraction_accumulator[feat], dtype=float)
                study_feature_rows.append({
                    "subset": subset,
                    "held_out_study": held_out,
                    "n_rows": int(len(te)),
                    "feature": feat,
                    "mean_squared_standardized_difference": float(vals.mean()),
                    "median_squared_standardized_difference": float(np.median(vals)),
                    "mean_fraction_of_total_squared_difference": float(fracs.mean()),
                    "median_fraction_of_total_squared_difference": float(np.median(fracs)),
                })

    points = pd.DataFrame(point_rows)
    folds = pd.DataFrame(fold_feature_rows)
    studies = pd.DataFrame(study_feature_rows)

    points.to_csv(OUT / "distance_driver_point_feature_contributions.csv", index=False)
    folds.to_csv(OUT / "distance_driver_fold_feature_geometry.csv", index=False)
    studies.to_csv(OUT / "distance_driver_study_feature_contributions.csv", index=False)

    ranked = studies.sort_values(
        ["subset", "held_out_study", "mean_fraction_of_total_squared_difference"],
        ascending=[True, True, False],
    ).groupby(["subset", "held_out_study"], as_index=False).head(5)
    ranked.to_csv(OUT / "distance_driver_top5_by_study.csv", index=False)

    excluded_df = folds[~folds["active_in_distance"]].copy()
    excluded_df.to_csv(OUT / "distance_driver_excluded_training_constant_features.csv", index=False)

    audit = {
        "subsets": SUBSETS,
        "k_neighbors": K,
        "decomposition": "mean squared standardized difference to the k nearest training rows; fractions sum to one per held-out row",
        "support_space": "corrected training-only continuous space used by applicability_domain_validation.py",
        "constant_feature_rule": f"exclude when training std <= {ad.TRAIN_STD_MIN}",
        "targets_used_to_compute_distance": False,
        "threshold_changed_here": False,
    }
    (OUT / "distance_driver_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    print("=== DISTANCE DRIVER AUDIT ===")
    print(json.dumps(audit, indent=2))
    print("\n=== TOP 5 ACTIVE DISTANCE DRIVERS BY HELD-OUT STUDY ===")
    print(ranked.to_string(index=False))
    print("\n=== EXCLUDED TRAINING-CONSTANT FEATURES ===")
    print(excluded_df.to_string(index=False) if len(excluded_df) else "None")


if __name__ == "__main__":
    main()
