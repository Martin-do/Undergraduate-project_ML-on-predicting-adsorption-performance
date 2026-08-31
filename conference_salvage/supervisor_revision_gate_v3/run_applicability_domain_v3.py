from __future__ import annotations

"""Post-hoc, target-independent applicability-domain diagnostic for OAU V3.

This does NOT tune a safety threshold to prediction error and does NOT establish
inverse-design reliability. It asks a narrower question: under LOSO, do simple
training-only descriptor-support diagnostics identify the high-error held-out
studies for the exploratory representations that improved pooled transfer?

Support is computed only from training studies. The held-out target is used only
after the support decision to audit whether support status tracks error.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VALIDATION = REPO / "validation_v2"
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(VALIDATION))

import run_supervisor_revision_gate_v3 as gate  # noqa: E402
import feature_parity_validation as fp  # noqa: E402
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor  # noqa: E402

VARIANTS = [
    "remove_pollutant_class",
    "remove_all_four_context_families",
    "physical_numeric_only",
]
MODELS = ["RF", "XGB"]
K_STUDIES = 5
TRAIN_STD_MIN = 1e-8
SUPPORT_FEATURES = list(fp.SCALE_COLS)


def metric(y, p):
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    return {
        "r2": float(r2_score(y, p)) if len(y) >= 2 and np.var(y) > 0 else np.nan,
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, p))),
        "mae_mg_g": float(mean_absolute_error(y, p)),
    }


def mean_nearest_studies(row, xtrain, train_groups, k=K_STUDIES):
    per_study = []
    for s in np.unique(train_groups):
        block = xtrain[train_groups == s]
        d = np.sqrt(np.sum((block - row) ** 2, axis=1))
        per_study.append(float(np.min(d)))
    kk = min(k, len(per_study))
    vals = np.partition(np.asarray(per_study), kk - 1)[:kk]
    return float(np.mean(vals))


def training_cross_study_distance(xtrain, train_groups, k=K_STUDIES):
    out = np.empty(len(xtrain), float)
    for i, row in enumerate(xtrain):
        other = train_groups != train_groups[i]
        out[i] = mean_nearest_studies(row, xtrain[other], train_groups[other], k=k)
    return out


def remaining_categorical_families(variant):
    if variant == "remove_pollutant_class":
        return ["activation_agent", "base_material", "material_class"]
    return []


def categorical_novelty(prep, raw_train, raw_test, variant):
    families = remaining_categorical_families(variant)
    if not families:
        return np.zeros(len(raw_test), int), ["" for _ in range(len(raw_test))]
    etr = fp.engineer_deterministic(raw_train).reset_index(drop=True)
    ete = fp.engineer_deterministic(raw_test).reset_index(drop=True)
    count = np.zeros(len(ete), int)
    detail = [[] for _ in range(len(ete))]
    for fam in families:
        known = set(etr[fam].astype(str))
        for i, val in enumerate(ete[fam].astype(str)):
            if val not in known:
                count[i] += 1
                detail[i].append(f"{fam}={val}")
    return count, [" | ".join(v) for v in detail]


def main():
    _, strict = gate.load_strict()
    y = strict[gate.base.TARGET].to_numpy(float)
    groups = strict["primary_study_id_v21"].astype(str).to_numpy()
    raw = strict[gate.RAW_MODEL_COLS].copy()
    bank = fp.models()

    row_records = []
    fold_records = []

    for variant in VARIANTS:
        for study in sorted(np.unique(groups)):
            te = np.flatnonzero(groups == study)
            tr = np.flatnonzero(groups != study)
            prep = DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
            xtr_full = prep.transform(raw.iloc[tr])
            xte_full = prep.transform(raw.iloc[te])
            model_idx, kept = gate.mask_variant(prep.output_cols, variant)

            # Support space is deliberately limited to scaled continuous/process
            # descriptors retained by the model representation. Training-constant
            # dimensions are excluded; no held-out information defines the space.
            candidate = [c for c in SUPPORT_FEATURES if c in kept and c in prep.output_cols]
            cidx_full = [prep.output_cols.index(c) for c in candidate]
            if not cidx_full:
                raise RuntimeError(f"No support features for {variant}/{study}")
            std = np.std(xtr_full[:, cidx_full], axis=0, ddof=0)
            active_mask = np.isfinite(std) & (std > TRAIN_STD_MIN)
            active = [c for c, ok in zip(candidate, active_mask) if ok]
            active_idx = [i for i, ok in zip(cidx_full, active_mask) if ok]
            excluded = [c for c, ok in zip(candidate, active_mask) if not ok]
            if len(active_idx) < 3:
                raise RuntimeError(f"Too few active support features for {variant}/{study}: {active}")

            ztr = xtr_full[:, active_idx]
            zte = xte_full[:, active_idx]
            train_dist = training_cross_study_distance(ztr, groups[tr])
            q95 = float(np.quantile(train_dist, 0.95))
            q99 = float(np.quantile(train_dist, 0.99))
            test_dist = np.array([mean_nearest_studies(r, ztr, groups[tr]) for r in zte])

            # Numeric-range novelty is separate from distance: any retained
            # support descriptor outside the training min/max is flagged.
            lo = np.min(ztr, axis=0)
            hi = np.max(ztr, axis=0)
            outside = (zte < lo) | (zte > hi)
            outside_count = outside.sum(axis=1)
            outside_fraction = outside.mean(axis=1)

            cat_n, cat_detail = categorical_novelty(prep, raw.iloc[tr], raw.iloc[te], variant)
            strict_support = (test_dist <= q95) & (outside_count == 0) & (cat_n == 0)

            preds = {}
            for model in MODELS:
                m = clone(bank[model]).fit(xtr_full[:, model_idx], y[tr])
                preds[model] = m.predict(xte_full[:, model_idx])

            fold_records.append({
                "variant": variant,
                "held_out_primary_study": study,
                "train_rows": int(len(tr)),
                "test_rows": int(len(te)),
                "train_studies": int(len(np.unique(groups[tr]))),
                "active_support_features": int(len(active)),
                "active_support_feature_names": " | ".join(active),
                "excluded_training_constant_features": " | ".join(excluded),
                "train_q95_distance": q95,
                "train_q99_distance": q99,
                "heldout_q95_supported_fraction": float(np.mean(test_dist <= q95)),
                "heldout_range_supported_fraction": float(np.mean(outside_count == 0)),
                "heldout_strict_supported_fraction": float(np.mean(strict_support)),
            })

            for j, pos in enumerate(te):
                for model in MODELS:
                    pred = float(preds[model][j])
                    row_records.append({
                        "variant": variant,
                        "model": model,
                        "held_out_primary_study": study,
                        "row_index": int(pos),
                        "actual_qe_mg_g": float(y[pos]),
                        "predicted_qe_mg_g": pred,
                        "abs_error_mg_g": float(abs(y[pos] - pred)),
                        "support_distance": float(test_dist[j]),
                        "train_q95_distance": q95,
                        "train_q99_distance": q99,
                        "distance_supported_q95": bool(test_dist[j] <= q95),
                        "outside_training_range_feature_count": int(outside_count[j]),
                        "outside_training_range_fraction": float(outside_fraction[j]),
                        "remaining_category_novelty_count": int(cat_n[j]),
                        "remaining_category_novelty_detail": cat_detail[j],
                        "strict_supported_q95": bool(strict_support[j]),
                    })

    rows = pd.DataFrame(row_records)
    folds = pd.DataFrame(fold_records)
    rows.to_csv(OUT / "v3_applicability_domain_rows.csv", index=False)
    folds.to_csv(OUT / "v3_applicability_domain_folds.csv", index=False)

    summaries = []
    study_rows = []
    for (variant, model), g in rows.groupby(["variant", "model"]):
        rho, pval = spearmanr(g["support_distance"], g["abs_error_mg_g"])
        for rule, mask in [
            ("all", np.ones(len(g), dtype=bool)),
            ("distance_q95", g["distance_supported_q95"].to_numpy(bool)),
            ("strict_q95", g["strict_supported_q95"].to_numpy(bool)),
        ]:
            s = g.loc[mask]
            m = metric(s.actual_qe_mg_g, s.predicted_qe_mg_g) if len(s) else {"r2":np.nan,"rmse_mg_g":np.nan,"mae_mg_g":np.nan}
            summaries.append({
                "variant": variant,
                "model": model,
                "support_rule": rule,
                "coverage_fraction": float(len(s)/len(g)),
                "n_rows": int(len(s)),
                **m,
                "spearman_distance_vs_abs_error": float(rho),
                "spearman_p_value": float(pval),
            })
        for study, sg in g.groupby("held_out_primary_study"):
            study_rows.append({
                "variant": variant,
                "model": model,
                "held_out_primary_study": study,
                "n_rows": int(len(sg)),
                "mae_mg_g": float(sg.abs_error_mg_g.mean()),
                "mean_support_distance": float(sg.support_distance.mean()),
                "distance_q95_supported_fraction": float(sg.distance_supported_q95.mean()),
                "range_supported_fraction": float((sg.outside_training_range_feature_count == 0).mean()),
                "strict_q95_supported_fraction": float(sg.strict_supported_q95.mean()),
            })

    summ = pd.DataFrame(summaries)
    study_df = pd.DataFrame(study_rows)
    summ.to_csv(OUT / "v3_applicability_domain_summary.csv", index=False)
    study_df.to_csv(OUT / "v3_applicability_domain_per_study.csv", index=False)

    alsh = study_df[study_df.held_out_primary_study.str.contains("Alshabib", case=False, na=False)]
    audit = {
        "status": "post-hoc diagnostic; not a validated safety gate",
        "variants": VARIANTS,
        "models": MODELS,
        "support_features": SUPPORT_FEATURES,
        "k_nearest_training_studies": K_STUDIES,
        "threshold": "q95 of training-row cross-study distance, defined independently inside each LOSO fold",
        "strict_rule": "distance<=training q95 AND no retained-support descriptor outside training min/max AND no novelty in remaining categorical families",
        "target_used_to_define_support": False,
        "threshold_tuned_to_error": False,
        "legacy_qmax_used": False,
        "alshabib_rows": alsh.to_dict(orient="records"),
    }
    (OUT / "v3_applicability_domain_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    print("=== V3 APPLICABILITY-DOMAIN SUMMARY ===")
    print(summ.to_string(index=False))
    print("\n=== ALShABIB SUPPORT CHECK ===")
    print(alsh.to_string(index=False))


if __name__ == "__main__":
    main()
