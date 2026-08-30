"""Close the major analysis requests from the independent ID-SEAD review.

This script is intentionally supplemental to the frozen conference reproducibility
checkpoint. It does NOT change the frozen V2.1 headline metrics. It stress-tests
their interpretation through:

1. primary-study cluster-size/effective-cluster diagnostics;
2. explicit strict-273 missingness disclosure;
3. per-fold row-random and GroupKFold performance dispersion;
4. material/context-identity feature ablations;
5. high-missingness-variable sensitivity (dose/contact time removal);
6. LOSO sensitivity restricted to meaningfully sized studies (n>=5), both
   (a) reporting only n>=5 held-out studies while training on all remaining data,
   and (b) refitting using only studies with n>=5.

All preprocessing remains fitted on training folds only. No legacy QMAX=624
constraint and no removal_percent predictor are used.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VALIDATION = REPO / "validation_v2"
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(VALIDATION))
import build_dataset_v21  # noqa: E402
import feature_parity_validation as fp  # noqa: E402
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor  # noqa: E402
import study_aware_validation as base  # noqa: E402

fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor
RAW_MODEL_COLS = base.RAW_FEATURES + ["removal_percent", "source_link"]
RANDOM_STATE = 42
N_SPLITS = 5


def metric(y, p):
    return {
        "r2": float(r2_score(y, p)),
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, p))),
        "mae_mg_g": float(mean_absolute_error(y, p)),
        "median_ae_mg_g": float(np.median(np.abs(y - p))),
    }


def load_strict():
    build_dataset_v21.main()
    path = VALIDATION / "outputs" / "adsorption_dataset_v2_1.csv"
    df = pd.read_csv(path, encoding="utf-8-sig")
    for col in base.NUMERIC_FEATURES + [base.TARGET]:
        df[col] = df[col].map(base.parse_numeric)
    for col in base.CATEGORICAL_FEATURES:
        df[col] = df[col].astype("string").fillna("Unknown")
    strict = df[df["analysis_eligible_strict_comparable_v21"].astype(bool)].copy().reset_index(drop=True)
    if len(strict) != 273 or strict["primary_study_id_v21"].nunique() != 24:
        raise RuntimeError(
            f"Expected strict 273/24, got {len(strict)}/{strict.primary_study_id_v21.nunique()}"
        )
    return df, strict


def study_size_diagnostics(strict):
    counts = (
        strict.groupby("primary_study_id_v21", dropna=False)
        .size()
        .sort_values(ascending=False)
        .rename("n_rows")
        .reset_index()
    )
    counts.to_csv(OUT / "study_size_distribution_strict273.csv", index=False)
    n = counts["n_rows"].to_numpy(float)
    w = n / n.sum()
    kish = float(1.0 / np.sum(w**2))
    entropy = float(np.exp(-np.sum(w * np.log(w))))
    top5 = int(counts.head(5)["n_rows"].sum())
    summary = {
        "rows": int(n.sum()),
        "studies": int(len(n)),
        "singleton_studies": int(np.sum(n == 1)),
        "studies_n_ge_5": int(np.sum(n >= 5)),
        "studies_n_ge_10": int(np.sum(n >= 10)),
        "top5_rows": top5,
        "top5_share": float(top5 / n.sum()),
        "largest_study_rows": int(n.max()),
        "median_rows_per_study": float(np.median(n)),
        "kish_effective_studies_by_row_weight": kish,
        "entropy_effective_studies_by_row_weight": entropy,
    }
    (OUT / "study_size_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return counts, summary


def missingness_diagnostics(strict):
    rows = []
    for col in base.NUMERIC_FEATURES:
        miss = int(strict[col].isna().sum())
        rows.append(
            {
                "feature": col,
                "missing_rows": miss,
                "total_rows": int(len(strict)),
                "missing_percent": float(100 * miss / len(strict)),
            }
        )
    out = pd.DataFrame(rows).sort_values("missing_percent", ascending=False)
    out.to_csv(OUT / "strict273_missingness.csv", index=False)
    return out


def reconstruct_fold_metrics(strict):
    y = strict[base.TARGET].to_numpy(float)
    groups = strict["primary_study_id_v21"].astype(str).to_numpy()
    all_fold_rows = []
    all_pooled_rows = []
    fold_manifest = []

    for scheme_name, scheme_groups in [
        ("strict273__row_random_5fold", None),
        ("strict273__primary_group_5fold", groups),
    ]:
        results, pred_frames, _fold_rows, _alphas, _features = fp.evaluate_scheme(
            strict, scheme_name, scheme_groups
        )
        all_pooled_rows.extend(results)
        pred_by_model = {p["model"].iloc[0]: p.set_index("row_id") for p in pred_frames}
        if scheme_groups is None:
            split_iter = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE).split(
                np.arange(len(strict)), y
            )
        else:
            split_iter = GroupKFold(n_splits=5).split(
                np.arange(len(strict)), y, groups
            )
        for fold, (_tr, te) in enumerate(split_iter, start=1):
            test_studies = sorted(set(groups[te]))
            fold_manifest.append(
                {
                    "scheme": scheme_name,
                    "fold": fold,
                    "test_rows": int(len(te)),
                    "test_studies": len(test_studies) if scheme_groups is not None else None,
                    "test_study_ids": " | ".join(test_studies) if scheme_groups is not None else "",
                }
            )
            for model, pf in pred_by_model.items():
                yy = pf.loc[te, "actual_qe_mg_g"].to_numpy(float)
                pp = pf.loc[te, "predicted_qe_mg_g"].to_numpy(float)
                all_fold_rows.append(
                    {
                        "scheme": scheme_name,
                        "fold": fold,
                        "model": model,
                        "test_rows": int(len(te)),
                        **metric(yy, pp),
                    }
                )

    folds = pd.DataFrame(all_fold_rows)
    pooled = pd.DataFrame(all_pooled_rows)
    folds.to_csv(OUT / "table1_per_fold_metrics.csv", index=False)
    pooled.to_csv(OUT / "table1_pooled_metrics_regenerated.csv", index=False)
    pd.DataFrame(fold_manifest).to_csv(OUT / "table1_fold_manifest.csv", index=False)

    spread = (
        folds.groupby(["scheme", "model"], as_index=False)
        .agg(
            mean_fold_r2=("r2", "mean"),
            std_fold_r2=("r2", "std"),
            min_fold_r2=("r2", "min"),
            max_fold_r2=("r2", "max"),
            mean_fold_rmse=("rmse_mg_g", "mean"),
            std_fold_rmse=("rmse_mg_g", "std"),
            mean_fold_mae=("mae_mg_g", "mean"),
            std_fold_mae=("mae_mg_g", "std"),
        )
    )
    spread.to_csv(OUT / "table1_fold_dispersion_summary.csv", index=False)
    return folds, pooled, spread


def mask_for_variant(cols, variant):
    cols = list(cols)
    if variant == "full_engineered":
        keep = [True] * len(cols)
    elif variant == "no_identity_adjacent_categories":
        prefixes = ("base_material_", "material_class_", "pollutant_class_", "activation_agent_")
        keep = [not c.startswith(prefixes) for c in cols]
    elif variant == "physical_numeric_only":
        allowed = {
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
        }
        keep = [c in allowed for c in cols]
    elif variant == "no_dose":
        banned = {"dose_gL", "conc_dose_ratio"}
        keep = [c not in banned for c in cols]
    elif variant == "no_contact_time":
        keep = [c != "contact_time_min" for c in cols]
    elif variant == "no_dose_or_contact_time":
        banned = {"dose_gL", "conc_dose_ratio", "contact_time_min"}
        keep = [c not in banned for c in cols]
    else:
        raise ValueError(variant)
    idx = np.flatnonzero(np.asarray(keep, dtype=bool))
    if len(idx) == 0:
        raise RuntimeError(f"Variant {variant} removed all features")
    return idx, [cols[i] for i in idx]


def evaluate_feature_variants(strict, variants, label):
    y = strict[base.TARGET].to_numpy(float)
    groups = strict["primary_study_id_v21"].astype(str).to_numpy()
    raw = strict[RAW_MODEL_COLS].copy()
    bank = fp.models()
    records = []
    fold_records = []

    for scheme, scheme_groups in [("row_random_5fold", None), ("primary_group_5fold", groups)]:
        if scheme_groups is None:
            splits = list(
                KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE).split(
                    np.arange(len(strict)), y
                )
            )
        else:
            splits = list(GroupKFold(n_splits=5).split(np.arange(len(strict)), y, groups))

        for variant in variants:
            pred = {m: np.empty(len(strict), dtype=float) for m in ["RF", "XGB"]}
            nfeat = []
            kept_example = None
            for fold, (tr, te) in enumerate(splits, start=1):
                prep = DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
                xtr_full = prep.transform(raw.iloc[tr])
                xte_full = prep.transform(raw.iloc[te])
                idx, kept = mask_for_variant(prep.output_cols, variant)
                kept_example = kept
                xtr, xte = xtr_full[:, idx], xte_full[:, idx]
                nfeat.append(len(idx))
                for model in ["RF", "XGB"]:
                    est = clone(bank[model]).fit(xtr, y[tr])
                    p = est.predict(xte)
                    pred[model][te] = p
                    fold_records.append(
                        {
                            "analysis": label,
                            "scheme": scheme,
                            "variant": variant,
                            "fold": fold,
                            "model": model,
                            "n_features": len(idx),
                            "test_rows": int(len(te)),
                            **metric(y[te], p),
                        }
                    )
            for model, p in pred.items():
                records.append(
                    {
                        "analysis": label,
                        "scheme": scheme,
                        "variant": variant,
                        "model": model,
                        "n_rows": len(strict),
                        "n_studies": int(pd.Series(groups).nunique()),
                        "mean_n_features": float(np.mean(nfeat)),
                        "min_n_features": int(np.min(nfeat)),
                        "max_n_features": int(np.max(nfeat)),
                        "kept_features_example": " | ".join(kept_example or []),
                        **metric(y, p),
                    }
                )

    summary = pd.DataFrame(records)
    fold_df = pd.DataFrame(fold_records)
    summary.to_csv(OUT / f"{label}_pooled.csv", index=False)
    fold_df.to_csv(OUT / f"{label}_per_fold.csv", index=False)
    return summary, fold_df


def run_loso_selected(data, held_out_studies, scope, training_mode):
    bank = fp.models()
    pred_frames = []
    per_study = []
    for study in held_out_studies:
        te = data["primary_study_id_v21"].astype(str).eq(study).to_numpy()
        if not te.any():
            continue
        train = data.loc[~te].copy()
        test = data.loc[te].copy()
        prep = DtypeSafeParityPreprocessor().fit(train[RAW_MODEL_COLS])
        xtr = prep.transform(train[RAW_MODEL_COLS])
        xte = prep.transform(test[RAW_MODEL_COLS])
        ytr = train[base.TARGET].to_numpy(float)
        yte = test[base.TARGET].to_numpy(float)
        for model in ["RF", "XGB"]:
            p = clone(bank[model]).fit(xtr, ytr).predict(xte)
            pred_frames.append(
                pd.DataFrame(
                    {
                        "scope": scope,
                        "training_mode": training_mode,
                        "held_out_primary_study": study,
                        "model": model,
                        "actual_qe_mg_g": yte,
                        "predicted_qe_mg_g": p,
                        "abs_error_mg_g": np.abs(yte - p),
                    }
                )
            )
            per_study.append(
                {
                    "scope": scope,
                    "training_mode": training_mode,
                    "held_out_primary_study": study,
                    "model": model,
                    "n_rows": int(len(test)),
                    "train_rows": int(len(train)),
                    "train_studies": int(train.primary_study_id_v21.nunique()),
                    **metric(yte, p),
                }
            )
    preds = pd.concat(pred_frames, ignore_index=True)
    ps = pd.DataFrame(per_study)
    pooled = []
    equal = []
    for model, g in preds.groupby("model", sort=False):
        pooled.append(
            {
                "scope": scope,
                "training_mode": training_mode,
                "model": model,
                "n_rows": int(len(g)),
                "n_held_out_studies": int(g.held_out_primary_study.nunique()),
                **metric(g.actual_qe_mg_g.to_numpy(float), g.predicted_qe_mg_g.to_numpy(float)),
            }
        )
        x = ps[ps.model.eq(model)]
        equal.append(
            {
                "scope": scope,
                "training_mode": training_mode,
                "model": model,
                "n_held_out_studies": int(len(x)),
                "mean_study_mae_mg_g": float(x.mae_mg_g.mean()),
                "median_study_mae_mg_g": float(x.mae_mg_g.median()),
                "mean_study_rmse_mg_g": float(x.rmse_mg_g.mean()),
                "median_study_rmse_mg_g": float(x.rmse_mg_g.median()),
            }
        )
    return pd.DataFrame(pooled), ps, pd.DataFrame(equal), preds


def well_powered_loso(strict, threshold=5):
    counts = strict.groupby("primary_study_id_v21").size()
    large = sorted(counts[counts >= threshold].index.astype(str).tolist())

    # A: keep all other strict-set studies in training; only report held-out studies n>=threshold.
    a = run_loso_selected(strict, large, f"heldout_n_ge_{threshold}", "train_on_all_other_strict_studies")

    # B: remove small studies from the modelling population altogether, then LOSO among large studies.
    large_data = strict[strict.primary_study_id_v21.astype(str).isin(large)].copy().reset_index(drop=True)
    b = run_loso_selected(large_data, large, f"population_n_ge_{threshold}_only", "train_on_large_studies_only")

    pooled = pd.concat([a[0], b[0]], ignore_index=True)
    per_study = pd.concat([a[1], b[1]], ignore_index=True)
    equal = pd.concat([a[2], b[2]], ignore_index=True)
    preds = pd.concat([a[3], b[3]], ignore_index=True)
    pooled.to_csv(OUT / "well_powered_loso_pooled.csv", index=False)
    per_study.to_csv(OUT / "well_powered_loso_per_study.csv", index=False)
    equal.to_csv(OUT / "well_powered_loso_equal_study.csv", index=False)
    preds.to_csv(OUT / "well_powered_loso_predictions.csv", index=False)
    return pooled, per_study, equal


def main():
    _all, strict = load_strict()
    study_counts, study_summary = study_size_diagnostics(strict)
    missing = missingness_diagnostics(strict)
    fold_metrics, pooled_metrics, fold_spread = reconstruct_fold_metrics(strict)

    identity_summary, identity_folds = evaluate_feature_variants(
        strict,
        ["full_engineered", "no_identity_adjacent_categories", "physical_numeric_only"],
        "feature_identity_ablation",
    )
    missing_summary, missing_folds = evaluate_feature_variants(
        strict,
        ["full_engineered", "no_dose", "no_contact_time", "no_dose_or_contact_time"],
        "high_missingness_feature_sensitivity",
    )
    wp_pooled, wp_per_study, wp_equal = well_powered_loso(strict, threshold=5)

    key = {
        "status": "supplemental reviewer revision gate; does not overwrite frozen baseline",
        "strict_rows": int(len(strict)),
        "strict_studies": int(strict.primary_study_id_v21.nunique()),
        "study_size_summary": study_summary,
        "largest_missingness": missing.head(5).to_dict(orient="records"),
        "identity_ablation": identity_summary.to_dict(orient="records"),
        "missingness_sensitivity": missing_summary.to_dict(orient="records"),
        "well_powered_loso": wp_pooled.to_dict(orient="records"),
        "well_powered_loso_equal_study": wp_equal.to_dict(orient="records"),
    }
    (OUT / "reviewer_revision_gate_v2_summary.json").write_text(
        json.dumps(key, indent=2), encoding="utf-8"
    )

    print("=== STUDY SIZE ===")
    print(json.dumps(study_summary, indent=2))
    print("\n=== MISSINGNESS ===")
    print(missing.to_string(index=False))
    print("\n=== TABLE-I FOLD DISPERSION ===")
    print(fold_spread.to_string(index=False))
    print("\n=== FEATURE IDENTITY ABLATION ===")
    print(identity_summary.to_string(index=False))
    print("\n=== HIGH-MISSINGNESS FEATURE SENSITIVITY ===")
    print(missing_summary.to_string(index=False))
    print("\n=== WELL-POWERED LOSO ===")
    print(wp_pooled.to_string(index=False))
    print("\n=== WELL-POWERED LOSO EQUAL STUDY ===")
    print(wp_equal.to_string(index=False))


if __name__ == "__main__":
    main()
