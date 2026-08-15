"""Primary-study holdout within evidence-based precursor domains.

Three nested descriptive domains are evaluated without changing the raw data:
1. strict_agricultural_waste -- only explicitly agricultural/agro-industrial wastes;
2. broad_biogenic_waste -- adds other biogenic waste/residual feedstocks;
3. waste_derived_carbon -- adds industrial sludge-derived waste carbons.

Only rows with confirmed primary-study provenance and an explicit `yes` domain flag
are admitted. `unknown`, uncertain and non-waste feedstocks are excluded.

Leave-One-Primary-Study-Out (LOSO) is used for interpretability. For the strict
agricultural subset, only four independent studies are currently available, so its
results are exploratory and cannot support a broad generalization claim.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut

import feature_parity_validation as fp
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor
import primary_study_holdout_validation as psh

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
DOMAIN_MAP = HERE / "adsorbent_domain_map.csv"
SUBSETS = ["strict_agricultural_waste", "broad_biogenic_waste", "waste_derived_carbon"]

# Reuse the tested dtype/fold-safe preprocessor and replace GroupKFold with full LOSO.
fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor


def loso_splitter(groups, seed_offset=0):
    if groups is None:
        raise ValueError("Domain-restricted validation requires primary-study groups")
    return LeaveOneGroupOut()


fp.splitter = loso_splitter


def main() -> None:
    strict, _, base_audit = psh.build_strict_dataset()
    dmap = pd.read_csv(DOMAIN_MAP, keep_default_na=False)
    dcols = ["project_adsorbent"] + SUBSETS + ["domain_class", "domain_confidence"]
    strict = strict.merge(
        dmap[dcols].rename(columns={"project_adsorbent": "adsorbent"}),
        on="adsorbent",
        how="left",
        validate="many_to_one",
    )
    if strict["domain_class"].isna().any():
        missing = sorted(strict.loc[strict["domain_class"].isna(), "adsorbent"].unique().tolist())
        raise ValueError(f"Confirmed rows missing precursor-domain mapping: {missing}")

    all_metrics = []
    all_predictions = []
    all_per_study = []
    all_equal = []
    all_folds = []
    all_alphas = []
    all_feature_counts = []
    audits = {}

    for subset in SUBSETS:
        data = strict[strict[subset].eq("yes")].copy().reset_index(drop=True)
        groups = data["primary_study_id"].to_numpy(str)
        n_groups = len(np.unique(groups))
        if n_groups < 3:
            audits[subset] = {
                "status": "not_run",
                "reason": "fewer_than_3_primary_studies",
                "rows": int(len(data)),
                "primary_studies": int(n_groups),
            }
            continue

        scheme = f"loso_{subset}"
        results, pred_frames, fold_records, alpha_records, feature_counts = fp.evaluate_scheme(
            data, scheme, groups
        )
        metrics = pd.DataFrame(results)
        preds = pd.concat(pred_frames, ignore_index=True)
        per_study = psh.per_study_metrics(preds, groups)
        equal = psh.equal_study_summary(per_study)
        for frame in (per_study, equal):
            frame.insert(0, "subset", subset)

        all_metrics.append(metrics)
        all_predictions.append(preds)
        all_per_study.append(per_study)
        all_equal.append(equal)
        all_folds.extend(fold_records)
        all_alphas.extend(alpha_records)
        all_feature_counts.extend(feature_counts)

        counts = data.groupby("primary_study_id").size().sort_values(ascending=False)
        audits[subset] = {
            "status": "completed",
            "rows": int(len(data)),
            "primary_studies": int(n_groups),
            "primary_study_row_counts": {str(k): int(v) for k, v in counts.items()},
            "exploratory_only": bool(n_groups < 5),
            "validation": "leave_one_primary_study_out",
        }

    if not all_metrics:
        raise RuntimeError("No precursor-domain subset had enough primary studies to run")

    pd.concat(all_metrics, ignore_index=True).to_csv(OUT / "domain_restricted_loso_metrics.csv", index=False)
    pd.concat(all_predictions, ignore_index=True).to_csv(OUT / "domain_restricted_loso_predictions.csv", index=False)
    pd.concat(all_per_study, ignore_index=True).to_csv(OUT / "domain_restricted_loso_per_study.csv", index=False)
    pd.concat(all_equal, ignore_index=True).to_csv(OUT / "domain_restricted_loso_equal_study.csv", index=False)
    pd.DataFrame(all_folds).to_csv(OUT / "domain_restricted_loso_folds.csv", index=False)
    pd.DataFrame(all_alphas).to_csv(OUT / "domain_restricted_loso_stack_alphas.csv", index=False)
    pd.DataFrame(all_feature_counts).to_csv(OUT / "domain_restricted_loso_feature_counts.csv", index=False)

    payload = {
        "base_confirmed_primary_audit": base_audit,
        "subsets": audits,
        "guardrails": [
            "Only explicit yes domain flags are admitted.",
            "All validation folds hold out complete primary studies.",
            "Strict agricultural results with fewer than five studies are exploratory only.",
            "The legacy QMAX/constraint layer is excluded.",
            "No model or subset is selected because it preserves the submitted title.",
        ],
    }
    (OUT / "domain_restricted_loso_audit.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== DOMAIN-RESTRICTED LOSO AUDIT ===")
    print(json.dumps(payload, indent=2))
    print("\n=== POOLED METRICS ===")
    print(pd.concat(all_metrics, ignore_index=True).to_string(index=False))
    print("\n=== EQUAL-STUDY SUMMARY ===")
    print(pd.concat(all_equal, ignore_index=True).to_string(index=False))
    print("\n=== PER-STUDY METRICS ===")
    print(pd.concat(all_per_study, ignore_index=True).to_string(index=False))


if __name__ == "__main__":
    main()
