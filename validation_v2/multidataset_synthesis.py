"""Deterministic synthesis for Paper 1 multi-dataset validation evidence.

This script does not retrain any adsorption model. It synthesizes only CI-locked
matched-validation results already registered in MULTIDATASET_RESULTS_REGISTRY.csv
and separates them from published source-aware comparators that cannot be rerun
because their raw modelling matrices are not openly distributed.

Primary cross-dataset comparison uses the two model families common to all three
independent matched corpora (RF and XGB). This avoids selecting a different
'best' algorithm per dataset after observing outcomes.
"""
from __future__ import annotations

from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "MULTIDATASET_RESULTS_REGISTRY.csv"
COMPARATORS = HERE / "SOURCE_AWARE_COMPARATOR_REGISTRY.csv"
OUT = HERE / "outputs" / "multidataset" / "synthesis"
OUT.mkdir(parents=True, exist_ok=True)

PRIMARY_DATASETS = [
    "martin_v21_strict",
    "liu_2025_strict",
    "liu_2025_ammonia",
]

DATASET_LABELS = {
    "martin_v21_strict": "V2.1 strict",
    "liu_2025_strict": "Liu 2025 dyes",
    "liu_2025_ammonia": "Liu ammonia-N",
}


def normalize_model(name: str) -> str:
    s = str(name).upper()
    if s.startswith("RF"):
        return "RF"
    if s.startswith("XGB"):
        return "XGB"
    if "CATBOOST" in s:
        return "CatBoost"
    if "RIDGE" in s:
        return "Ridge stack"
    return str(name)


def load_primary() -> pd.DataFrame:
    df = pd.read_csv(RESULTS)
    df["model_family"] = df["model"].map(normalize_model)
    primary = df[
        df["dataset_id"].isin(PRIMARY_DATASETS)
        & df["model_family"].isin(["RF", "XGB"])
    ].copy()
    # exactly one RF and one XGB row per independent primary dataset
    expected = {(d, m) for d in PRIMARY_DATASETS for m in ["RF", "XGB"]}
    observed = set(zip(primary["dataset_id"], primary["model_family"]))
    if observed != expected:
        raise RuntimeError(f"Primary registry mismatch. Expected {expected}, got {observed}")
    primary["dataset_short"] = primary["dataset_id"].map(DATASET_LABELS)
    primary["pair_label"] = primary["dataset_short"] + " — " + primary["model_family"]
    numeric = [
        "random_r2", "grouped_r2", "delta_r2_random_minus_grouped", "loso_r2",
        "random_rmse", "grouped_rmse", "random_mae", "grouped_mae",
    ]
    for c in numeric:
        primary[c] = pd.to_numeric(primary[c], errors="coerce")
    primary = primary.sort_values(["dataset_id", "model_family"]).reset_index(drop=True)
    return primary


def write_tables(primary: pd.DataFrame) -> None:
    cols = [
        "dataset_id", "dataset_short", "n_rows", "n_groups", "model_family",
        "random_validation", "random_r2", "grouped_validation", "grouped_r2",
        "delta_r2_random_minus_grouped", "loso_r2", "random_rmse",
        "grouped_rmse", "random_mae", "grouped_mae", "ci_run", "artifact_id",
    ]
    primary[cols].to_csv(OUT / "primary_common_model_synthesis.csv", index=False)

    # Separate auxiliary results so lineage-overlapping Moosavi is never silently
    # counted as an independent replication.
    full = pd.read_csv(RESULTS)
    full["model_family"] = full["model"].map(normalize_model)
    auxiliary = full[~full["dataset_id"].isin(PRIMARY_DATASETS)].copy()
    auxiliary.to_csv(OUT / "auxiliary_and_sensitivity_results.csv", index=False)

    comparators = pd.read_csv(COMPARATORS)
    comparators.to_csv(OUT / "published_source_aware_comparators.csv", index=False)


def figure_pairs(primary: pd.DataFrame) -> None:
    # Fixed ordering by dataset then RF/XGB for direct visual comparison.
    order = []
    for d in PRIMARY_DATASETS:
        for m in ["RF", "XGB"]:
            order.append((d, m))
    rows = []
    for d, m in order:
        rows.append(primary[(primary.dataset_id == d) & (primary.model_family == m)].iloc[0])
    p = pd.DataFrame(rows)

    x = np.arange(len(p))
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for i, row in p.reset_index(drop=True).iterrows():
        ax.plot([i, i], [row["random_r2"], row["grouped_r2"]], linewidth=1.5)
        ax.scatter(i, row["random_r2"], marker="o", s=55, label="Random CV" if i == 0 else None)
        ax.scatter(i, row["grouped_r2"], marker="s", s=55, label="Study-aware CV" if i == 0 else None)
    ax.axhline(0, linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(p["pair_label"], rotation=25, ha="right")
    ax.set_ylabel("R²")
    ax.set_title("Matched row-random versus primary-study-aware validation")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "figure_primary_random_vs_grouped.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def figure_delta(primary: pd.DataFrame) -> None:
    p = primary.copy()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(p))
    ax.bar(x, p["delta_r2_random_minus_grouped"])
    ax.set_xticks(x)
    ax.set_xticklabels(p["pair_label"], rotation=25, ha="right")
    ax.set_ylabel("ΔR² = random R² − grouped R²")
    ax.set_title("Validation optimism gap across independent matched corpora")
    fig.tight_layout()
    fig.savefig(OUT / "figure_primary_delta_r2.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_summary(primary: pd.DataFrame) -> None:
    deltas = primary["delta_r2_random_minus_grouped"].dropna().to_numpy(float)
    random_vals = primary["random_r2"].dropna().to_numpy(float)
    grouped_vals = primary["grouped_r2"].dropna().to_numpy(float)
    summary = {
        "primary_independent_matched_datasets": len(PRIMARY_DATASETS),
        "primary_common_model_comparisons": int(len(primary)),
        "common_model_families": ["RF", "XGB"],
        "comparisons_with_random_r2_gt_grouped_r2": int((primary.random_r2 > primary.grouped_r2).sum()),
        "delta_r2_min": float(np.min(deltas)),
        "delta_r2_max": float(np.max(deltas)),
        "delta_r2_median_descriptive": float(np.median(deltas)),
        "random_r2_range": [float(np.min(random_vals)), float(np.max(random_vals))],
        "grouped_r2_range": [float(np.min(grouped_vals)), float(np.max(grouped_vals))],
        "aggregation_warning": (
            "The median delta is descriptive only. R2 values from heterogeneous datasets are not pooled as a formal meta-analysis."
        ),
        "independence_rule": (
            "Moosavi 2021 is excluded from the independent dataset count because its primary-study lineage overlaps V2.1."
        ),
        "comparator_rule": (
            "Huang 2026 and Aguiar 2026 are published source-aware comparators/corroboration, not CI-rerun matched datasets."
        ),
    }
    (OUT / "multidataset_synthesis_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )


def main() -> None:
    primary = load_primary()
    write_tables(primary)
    figure_pairs(primary)
    figure_delta(primary)
    write_summary(primary)
    print(primary[[
        "dataset_short", "model_family", "random_r2", "grouped_r2",
        "delta_r2_random_minus_grouped", "loso_r2"
    ]].to_string(index=False))
    print("\nOutputs:", OUT)


if __name__ == "__main__":
    main()
