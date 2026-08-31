from __future__ import annotations

"""Study-level LOSO uncertainty for the target-blind corrected pollutant class."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone

import run_pollutant_representation_forensic_v3 as forensic

fp = forensic.fp
gate = forensic.gate
DtypeSafeParityPreprocessor = forensic.DtypeSafeParityPreprocessor
OUT = Path(__file__).resolve().parent / "outputs"
RANDOM_STATE = 42
N_BOOT = 5000


def main():
    _, strict = gate.load_strict()
    y = strict[gate.base.TARGET].to_numpy(float)
    groups = strict["primary_study_id_v21"].astype(str).to_numpy()
    raw = strict[gate.RAW_MODEL_COLS].copy()
    bank = fp.models()

    pred_rows = []
    study_rows = []
    with forensic.corrected_pollutant_engineering():
        for study in sorted(np.unique(groups)):
            te = np.flatnonzero(groups == study)
            tr = np.flatnonzero(groups != study)
            prep = DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
            xtr = prep.transform(raw.iloc[tr]); xte = prep.transform(raw.iloc[te])
            for model in ["RF", "XGB"]:
                p = clone(bank[model]).fit(xtr, y[tr]).predict(xte)
                sm = gate.safe_study_metric(y[te], p)
                study_rows.append({
                    "held_out_primary_study": study,
                    "model": model,
                    "n_test_rows": len(te),
                    **sm,
                })
                for pos, pp in zip(te, p):
                    pred_rows.append({
                        "held_out_primary_study": study,
                        "model": model,
                        "row_index": int(pos),
                        "actual_qe_mg_g": float(y[pos]),
                        "predicted_qe_mg_g": float(pp),
                        "abs_error_mg_g": float(abs(y[pos] - pp)),
                    })

    preds = pd.DataFrame(pred_rows)
    studies = pd.DataFrame(study_rows)
    preds.to_csv(OUT / "corrected_pollutant_class_loso_predictions.csv", index=False)
    studies.to_csv(OUT / "corrected_pollutant_class_loso_per_study_uncertainty.csv", index=False)

    rng = np.random.default_rng(RANDOM_STATE)
    reps = []
    summary = []
    for model in ["RF", "XGB"]:
        pdat = preds[preds.model.eq(model)]
        ids = sorted(pdat.held_out_primary_study.unique())
        blocks = {s: pdat[pdat.held_out_primary_study.eq(s)] for s in ids}
        local = []
        for b in range(N_BOOT):
            sampled = rng.choice(ids, size=len(ids), replace=True)
            yy, pp = [], []
            for s in sampled:
                block = blocks[s]
                yy.extend(block.actual_qe_mg_g.to_numpy(float))
                pp.extend(block.predicted_qe_mg_g.to_numpy(float))
            m = forensic.metric(np.asarray(yy), np.asarray(pp))
            rec = {"model":model, "replicate":b, **m}
            reps.append(rec); local.append(rec)
        bdf = pd.DataFrame(local)
        sm = studies[studies.model.eq(model)]
        valid_r2 = sm.r2.dropna()
        obs = forensic.metric(pdat.actual_qe_mg_g.to_numpy(float), pdat.predicted_qe_mg_g.to_numpy(float))
        summary.append({
            "model":model,
            "n_studies":len(ids),
            "pooled_r2":obs["r2"],
            "pooled_mae_mg_g":obs["mae_mg_g"],
            "pooled_rmse_mg_g":obs["rmse_mg_g"],
            "study_mae_median":float(sm.mae_mg_g.median()),
            "study_mae_iqr_low":float(sm.mae_mg_g.quantile(.25)),
            "study_mae_iqr_high":float(sm.mae_mg_g.quantile(.75)),
            "study_mae_mean":float(sm.mae_mg_g.mean()),
            "study_mae_sd":float(sm.mae_mg_g.std(ddof=1)),
            "valid_study_r2_count":int(len(valid_r2)),
            "study_r2_median":float(valid_r2.median()) if len(valid_r2) else np.nan,
            "study_r2_iqr_low":float(valid_r2.quantile(.25)) if len(valid_r2) else np.nan,
            "study_r2_iqr_high":float(valid_r2.quantile(.75)) if len(valid_r2) else np.nan,
            "cluster_bootstrap_r2_ci_low":float(bdf.r2.quantile(.025)),
            "cluster_bootstrap_r2_ci_high":float(bdf.r2.quantile(.975)),
            "cluster_bootstrap_mae_mg_g_ci_low":float(bdf.mae_mg_g.quantile(.025)),
            "cluster_bootstrap_mae_mg_g_ci_high":float(bdf.mae_mg_g.quantile(.975)),
            "cluster_bootstrap_rmse_mg_g_ci_low":float(bdf.rmse_mg_g.quantile(.025)),
            "cluster_bootstrap_rmse_mg_g_ci_high":float(bdf.rmse_mg_g.quantile(.975)),
        })

    pd.DataFrame(reps).to_csv(OUT / "corrected_pollutant_class_cluster_bootstrap_replicates.csv", index=False)
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(OUT / "corrected_pollutant_class_uncertainty_summary.csv", index=False)
    (OUT / "corrected_pollutant_class_uncertainty_audit.json").write_text(json.dumps({
        "representation":"full engineered pipeline with target-blind exact-label correction of pollutant_class",
        "bootstrap_unit":"primary study",
        "bootstrap_replicates":N_BOOT,
        "random_state":RANDOM_STATE,
        "post_hoc_status":"forensic representation correction prompted by supervisor audit",
        "summary":summary,
    }, indent=2), encoding="utf-8")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
