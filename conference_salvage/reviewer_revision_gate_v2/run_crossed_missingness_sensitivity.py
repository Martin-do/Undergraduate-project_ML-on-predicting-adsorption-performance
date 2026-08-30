"""Check whether the identity-ablation improvement depends on heavily imputed variables.

The strict 273-row set has substantial missingness in dose and contact time. This
supplement crosses the reviewer-triggered identity/context ablation with removal
of dose/contact-time features, using the same fold-safe preprocessing and the
same row-random / primary-study-grouped split definitions.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GroupKFold, KFold

import run_reviewer_revision_gate_v2 as gate

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def mask(cols, variant):
    cols = list(cols)
    prefixes = ("base_material_", "material_class_", "pollutant_class_", "activation_agent_")
    physical_allowed = {
        "surface_area_m2g", "particle_size_mm", "pore_volume_cm3g",
        "initial_concentration_mgL", "temperature_c", "contact_time_min", "ph",
        "dose_gL", "pyrolysis_temp_c", "conc_dose_ratio",
        "surface_area_x_pore_vol", "ph_x_temperature",
    }
    if variant.startswith("no_identity"):
        keep = np.array([not c.startswith(prefixes) for c in cols], dtype=bool)
    elif variant.startswith("physical_numeric"):
        keep = np.array([c in physical_allowed for c in cols], dtype=bool)
    else:
        raise ValueError(variant)

    if "no_dose" in variant:
        keep &= np.array([c not in {"dose_gL", "conc_dose_ratio"} for c in cols])
    if "no_contact" in variant:
        keep &= np.array([c != "contact_time_min" for c in cols])
    idx = np.flatnonzero(keep)
    if not len(idx):
        raise RuntimeError(f"No features retained for {variant}")
    return idx


def matched(strict, variants):
    y = strict[gate.base.TARGET].to_numpy(float)
    groups = strict.primary_study_id_v21.astype(str).to_numpy()
    raw = strict[gate.RAW_MODEL_COLS].copy()
    bank = gate.fp.models()
    rows = []

    for scheme, scheme_groups in [("row_random_5fold", None), ("primary_group_5fold", groups)]:
        splits = list(
            KFold(n_splits=5, shuffle=True, random_state=42).split(np.arange(len(strict)), y)
            if scheme_groups is None
            else GroupKFold(n_splits=5).split(np.arange(len(strict)), y, groups)
        )
        for variant in variants:
            preds = {m: np.empty(len(strict), dtype=float) for m in ["RF", "XGB"]}
            nfeatures = []
            for tr, te in splits:
                prep = gate.DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
                xtr_full = prep.transform(raw.iloc[tr])
                xte_full = prep.transform(raw.iloc[te])
                idx = mask(prep.output_cols, variant)
                nfeatures.append(len(idx))
                for model in ["RF", "XGB"]:
                    est = clone(bank[model]).fit(xtr_full[:, idx], y[tr])
                    preds[model][te] = est.predict(xte_full[:, idx])
            for model, p in preds.items():
                rows.append({
                    "scheme": scheme,
                    "variant": variant,
                    "model": model,
                    "n_rows": len(strict),
                    "n_studies": int(strict.primary_study_id_v21.nunique()),
                    "mean_n_features": float(np.mean(nfeatures)),
                    **gate.metric(y, p),
                })
    return pd.DataFrame(rows)


def loso(strict, variants):
    y = strict[gate.base.TARGET].to_numpy(float)
    raw = strict[gate.RAW_MODEL_COLS].copy()
    bank = gate.fp.models()
    studies = sorted(strict.primary_study_id_v21.astype(str).unique())
    pred_rows = []
    per_study_rows = []
    for study in studies:
        te = strict.primary_study_id_v21.astype(str).eq(study).to_numpy()
        tr = ~te
        prep = gate.DtypeSafeParityPreprocessor().fit(raw.loc[tr])
        xtr_full = prep.transform(raw.loc[tr])
        xte_full = prep.transform(raw.loc[te])
        for variant in variants:
            idx = mask(prep.output_cols, variant)
            for model in ["RF", "XGB"]:
                est = clone(bank[model]).fit(xtr_full[:, idx], y[tr])
                p = est.predict(xte_full[:, idx])
                m = gate.metric(y[te], p)
                per_study_rows.append({
                    "variant": variant, "model": model,
                    "held_out_primary_study": study,
                    "n_test_rows": int(te.sum()), **m,
                })
                pred_rows.append(pd.DataFrame({
                    "variant": variant, "model": model,
                    "held_out_primary_study": study,
                    "actual_qe_mg_g": y[te], "predicted_qe_mg_g": p,
                }))
    preds = pd.concat(pred_rows, ignore_index=True)
    per_study = pd.DataFrame(per_study_rows)
    pooled = []
    equal = []
    for (variant, model), g in preds.groupby(["variant", "model"], sort=False):
        pooled.append({
            "variant": variant, "model": model, "n_rows": len(g),
            "n_studies": int(g.held_out_primary_study.nunique()),
            **gate.metric(g.actual_qe_mg_g.to_numpy(float), g.predicted_qe_mg_g.to_numpy(float)),
        })
        ps = per_study[(per_study.variant == variant) & (per_study.model == model)]
        equal.append({
            "variant": variant, "model": model, "n_studies": len(ps),
            "mean_study_mae_mg_g": float(ps.mae_mg_g.mean()),
            "median_study_mae_mg_g": float(ps.mae_mg_g.median()),
        })
    return pd.DataFrame(pooled), per_study, pd.DataFrame(equal), preds


def main():
    _full, strict = gate.load_strict()
    variants = [
        "no_identity",
        "no_identity_no_dose",
        "no_identity_no_contact",
        "no_identity_no_dose_no_contact",
        "physical_numeric",
        "physical_numeric_no_dose_no_contact",
    ]
    matched_df = matched(strict, variants)
    loso_variants = [
        "no_identity", "no_identity_no_dose_no_contact",
        "physical_numeric", "physical_numeric_no_dose_no_contact",
    ]
    loso_pooled, loso_per_study, loso_equal, loso_preds = loso(strict, loso_variants)

    matched_df.to_csv(OUT / "identity_missingness_crossed_matched.csv", index=False)
    loso_pooled.to_csv(OUT / "identity_missingness_crossed_loso_pooled.csv", index=False)
    loso_per_study.to_csv(OUT / "identity_missingness_crossed_loso_per_study.csv", index=False)
    loso_equal.to_csv(OUT / "identity_missingness_crossed_loso_equal_study.csv", index=False)
    loso_preds.to_csv(OUT / "identity_missingness_crossed_loso_predictions.csv", index=False)

    print("=== CROSSED MATCHED SENSITIVITY ===")
    print(matched_df.to_string(index=False))
    print("\n=== CROSSED LOSO SENSITIVITY ===")
    print(loso_pooled.to_string(index=False))
    print("\n=== CROSSED LOSO EQUAL-STUDY ===")
    print(loso_equal.to_string(index=False))


if __name__ == "__main__":
    main()
