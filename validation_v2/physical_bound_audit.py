"""Audit the manuscript/notebook Q_MAX constraint against observed data."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import study_aware_validation as base

OUT_DIR = Path(__file__).resolve().parent / "outputs"
Q_MAX_LEGACY = 624.0


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = base.load_data()
    y = df[base.TARGET].astype(float)
    above = df.loc[y > Q_MAX_LEGACY].copy()

    by_source = (
        above.groupby("study_group")[base.TARGET]
        .agg(rows_above_bound="size", min_above="min", median_above="median", max_above="max")
        .sort_values("rows_above_bound", ascending=False)
        .reset_index()
    )
    by_source.to_csv(OUT_DIR / "legacy_qmax_exceedances_by_study.csv", index=False)

    summary = {
        "legacy_q_max_mg_g": Q_MAX_LEGACY,
        "observed_rows": int(len(df)),
        "observed_min_mg_g": float(y.min()),
        "observed_median_mg_g": float(y.median()),
        "observed_max_mg_g": float(y.max()),
        "observed_p95_mg_g": float(y.quantile(0.95)),
        "observed_p99_mg_g": float(y.quantile(0.99)),
        "rows_above_legacy_qmax": int((y > Q_MAX_LEGACY).sum()),
        "percent_rows_above_legacy_qmax": float(100 * (y > Q_MAX_LEGACY).mean()),
        "studies_with_rows_above_legacy_qmax": int(above["study_group"].nunique()),
        "all_exceedance_studies": sorted(above["study_group"].unique().tolist()),
        "interpretation_guardrail": (
            "If observed qe values above 624 mg/g are legitimate and comparable, 624 mg/g cannot be described "
            "as a universal physical upper bound for the full dataset. The bound must be re-derived, made "
            "conditional/domain-specific, or the training domain must be narrowed explicitly."
        ),
    }
    (OUT_DIR / "physical_bound_audit.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=== LEGACY Q_MAX CONSISTENCY AUDIT ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("\n=== EXCEEDANCES BY STUDY ===")
    print(by_source.to_string(index=False) if len(by_source) else "No exceedances")


if __name__ == "__main__":
    main()
