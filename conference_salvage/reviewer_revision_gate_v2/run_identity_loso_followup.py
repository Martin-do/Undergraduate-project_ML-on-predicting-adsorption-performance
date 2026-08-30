"""Follow-up required by the reviewer-gate identity-ablation result.

The first reviewer-gate run found that removing identity-adjacent engineered
categorical features materially improved pooled GroupKFold transfer. This script
checks whether that improvement survives the stricter leave-one-primary-study-out
(LOSO) test, including well-powered-study and domain-restricted sensitivities.

It is supplemental evidence and does not overwrite the frozen V2.1 baseline.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone

import run_reviewer_revision_gate_v2 as gate

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
VARIANTS = ["full_engineered", "no_identity_adjacent_categories", "physical_numeric_only"]


def loso_variants(data: pd.DataFrame, held_out_studies, scope: str, training_mode: str):
    raw = data[gate.RAW_MODEL_COLS].copy()
    bank = gate.fp.models()
    pred_rows = []
    per_study_rows = []

    for study in held_out_studies:
        te = data["primary_study_id_v21"].astype(str).eq(str(study)).to_numpy()
        if not te.any():
            continue
        tr = ~te
        train_raw = raw.loc[tr]
        test_raw = raw.loc[te]
        ytr = data.loc[tr, gate.base.TARGET].to_numpy(float)
        yte = data.loc[te, gate.base.TARGET].to_numpy(float)

        prep = gate.DtypeSafeParityPreprocessor().fit(train_raw)
        xtr_full = prep.transform(train_raw)
        xte_full = prep.transform(test_raw)

        for variant in VARIANTS:
            idx, kept = gate.mask_for_variant(prep.output_cols, variant)
            xtr, xte = xtr_full[:, idx], xte_full[:, idx]
            for model in ["RF", "XGB"]:
                p = clone(bank[model]).fit(xtr, ytr).predict(xte)
                m = gate.metric(yte, p)
                per_study_rows.append({
                    "scope": scope,
                    "training_mode": training_mode,
                    "variant": variant,
                    "held_out_primary_study": str(study),
                    "model": model,
                    "n_test_rows": int(len(yte)),
                    "n_train_rows": int(len(ytr)),
                    "n_train_studies": int(data.loc[tr, "primary_study_id_v21"].nunique()),
                    "n_features": int(len(idx)),
                    **m,
                })
                pred_rows.append(pd.DataFrame({
                    "scope": scope,
                    "training_mode": training_mode,
                    "variant": variant,
                    "held_out_primary_study": str(study),
                    "model": model,
                    "actual_qe_mg_g": yte,
                    "predicted_qe_mg_g": p,
                    "abs_error_mg_g": np.abs(yte - p),
                }))

    per_study = pd.DataFrame(per_study_rows)
    preds = pd.concat(pred_rows, ignore_index=True)
    pooled_rows = []
    equal_rows = []
    for (variant, model), g in preds.groupby(["variant", "model"], sort=False):
        pooled_rows.append({
            "scope": scope,
            "training_mode": training_mode,
            "variant": variant,
            "model": model,
            "n_rows": int(len(g)),
            "n_held_out_studies": int(g.held_out_primary_study.nunique()),
            **gate.metric(g.actual_qe_mg_g.to_numpy(float), g.predicted_qe_mg_g.to_numpy(float)),
        })
        ps = per_study[(per_study.variant == variant) & (per_study.model == model)]
        equal_rows.append({
            "scope": scope,
            "training_mode": training_mode,
            "variant": variant,
            "model": model,
            "n_held_out_studies": int(len(ps)),
            "mean_study_mae_mg_g": float(ps.mae_mg_g.mean()),
            "median_study_mae_mg_g": float(ps.mae_mg_g.median()),
            "mean_study_rmse_mg_g": float(ps.rmse_mg_g.mean()),
            "median_study_rmse_mg_g": float(ps.rmse_mg_g.median()),
        })
    return pd.DataFrame(pooled_rows), per_study, pd.DataFrame(equal_rows), preds


def main():
    full, strict = gate.load_strict()
    pieces = []

    # 1. Full strict 273 / 24-study LOSO.
    studies = sorted(strict.primary_study_id_v21.astype(str).unique())
    pieces.append(loso_variants(strict, studies, "strict_comparable_273", "all_other_strict_studies"))

    # 2. Well-powered held-out studies (n>=5), train on all other strict studies.
    counts = strict.groupby("primary_study_id_v21").size()
    large = sorted(counts[counts >= 5].index.astype(str).tolist())
    pieces.append(loso_variants(strict, large, "strict_heldout_n_ge_5", "all_other_strict_studies"))

    # 3. Population restricted entirely to n>=5 studies.
    large_data = strict[strict.primary_study_id_v21.astype(str).isin(large)].copy().reset_index(drop=True)
    pieces.append(loso_variants(large_data, large, "strict_population_n_ge_5_only", "large_studies_only"))

    # 4. Domain-restricted LOSO. These are diagnostic; no post-hoc study removal.
    domain_specs = [
        ("strict_agricultural_waste", "analysis_eligible_strict_agricultural_v2"),
        ("broad_biogenic_waste", "analysis_eligible_broad_biogenic_v2"),
        ("waste_derived_carbon", "analysis_eligible_waste_derived_carbon_v2"),
    ]
    domain_meta = []
    for name, flag in domain_specs:
        data = full[full[flag].astype(bool)].copy().reset_index(drop=True)
        studies_d = sorted(data.primary_study_id_v21.astype(str).unique())
        domain_meta.append({"scope": name, "rows": int(len(data)), "studies": int(len(studies_d))})
        pieces.append(loso_variants(data, studies_d, name, "domain_only"))

    pooled = pd.concat([x[0] for x in pieces], ignore_index=True)
    per_study = pd.concat([x[1] for x in pieces], ignore_index=True)
    equal = pd.concat([x[2] for x in pieces], ignore_index=True)
    preds = pd.concat([x[3] for x in pieces], ignore_index=True)

    pooled.to_csv(OUT / "identity_ablation_loso_pooled.csv", index=False)
    per_study.to_csv(OUT / "identity_ablation_loso_per_study.csv", index=False)
    equal.to_csv(OUT / "identity_ablation_loso_equal_study.csv", index=False)
    preds.to_csv(OUT / "identity_ablation_loso_predictions.csv", index=False)
    (OUT / "identity_ablation_loso_scope_summary.json").write_text(
        json.dumps({
            "variants": VARIANTS,
            "well_powered_threshold": 5,
            "well_powered_studies": len(large),
            "well_powered_rows": int(len(large_data)),
            "domain_scopes": domain_meta,
        }, indent=2),
        encoding="utf-8",
    )

    print("=== IDENTITY-ABLATION LOSO POOLED ===")
    print(pooled.to_string(index=False))
    print("\n=== IDENTITY-ABLATION LOSO EQUAL-STUDY ===")
    print(equal.to_string(index=False))
    print("\n=== DOMAIN META ===")
    print(json.dumps(domain_meta, indent=2))


if __name__ == "__main__":
    main()
