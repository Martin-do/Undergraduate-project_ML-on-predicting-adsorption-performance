"""Matched validation comparator on the same 238 provenance-confirmed rows.

This removes an avoidable apples-vs-oranges comparison in the manuscript. The same
rows and original engineered feature representation are evaluated under:

1. ordinary shuffled 5-fold row CV;
2. 5-fold GroupKFold by reconstructed primary study.

All preprocessing remains fitted inside each fold. The legacy QMAX and
removal_percent are excluded.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import feature_parity_validation as fp
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor
import primary_study_holdout_validation as psh

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor


def main() -> None:
    data, groups, audit = psh.build_strict_dataset()
    frames = []
    fold_frames = []
    alpha_frames = []

    for scheme, scheme_groups in [
        ("matched_row_random_5fold", None),
        ("matched_primary_group_5fold", groups),
    ]:
        results, preds, folds, alphas, features = fp.evaluate_scheme(data, scheme, scheme_groups)
        frames.append(pd.DataFrame(results))
        fold_frames.append(pd.DataFrame(folds))
        alpha_frames.append(pd.DataFrame(alphas))

    metrics = pd.concat(frames, ignore_index=True)
    metrics.to_csv(OUT / "matched_primary_comparator_metrics.csv", index=False)
    pd.concat(fold_frames, ignore_index=True).to_csv(OUT / "matched_primary_comparator_folds.csv", index=False)
    pd.concat(alpha_frames, ignore_index=True).to_csv(OUT / "matched_primary_comparator_stack_alphas.csv", index=False)

    summary = {
        "rows": int(len(data)),
        "primary_studies": int(pd.Series(groups).nunique()),
        "schemes": ["matched_row_random_5fold", "matched_primary_group_5fold"],
        "same_rows_in_both_schemes": True,
        "qmax_used": False,
        "removal_percent_used": False,
    }
    pd.DataFrame([summary]).to_json(OUT / "matched_primary_comparator_audit.json", orient="records", indent=2)

    print("=== MATCHED 238-ROW COMPARATOR ===")
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
