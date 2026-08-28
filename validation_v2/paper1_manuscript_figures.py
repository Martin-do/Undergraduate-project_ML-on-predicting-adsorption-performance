"""Publication-oriented figures for Paper 1.

Numerical inputs are read from the locked result registries. This script does not
retrain models and does not modify the multi-dataset numerical source of truth.
It exists only to render manuscript figures with consistent ordering, labeling,
and explicit evidence-class separation.
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
OUT = HERE / "outputs" / "paper1_manuscript_figures"
OUT.mkdir(parents=True, exist_ok=True)

ORDER = [
    ("martin_v21_strict", "RF"),
    ("martin_v21_strict", "XGB"),
    ("liu_2025_strict", "RF"),
    ("liu_2025_strict", "XGB"),
    ("liu_2025_ammonia", "RF"),
    ("liu_2025_ammonia", "XGB"),
]

DATASET_LABELS = {
    "martin_v21_strict": "V2.1 strict",
    "liu_2025_strict": "Liu 2025 dyes",
    "liu_2025_ammonia": "Liu ammonia-N",
}


def model_family(value: str) -> str:
    s = str(value).upper()
    if s.startswith("RF"):
        return "RF"
    if s.startswith("XGB"):
        return "XGB"
    if "CATBOOST" in s:
        return "CatBoost"
    return str(value)


def primary_common() -> pd.DataFrame:
    df = pd.read_csv(RESULTS)
    df["model_family"] = df["model"].map(model_family)
    rows = []
    for dataset_id, model in ORDER:
        hit = df[(df.dataset_id == dataset_id) & (df.model_family == model)]
        if len(hit) != 1:
            raise RuntimeError(f"Expected exactly one row for {(dataset_id, model)}, got {len(hit)}")
        row = hit.iloc[0].copy()
        row["dataset_short"] = DATASET_LABELS[dataset_id]
        row["pair_label"] = f"{DATASET_LABELS[dataset_id]}\n{model}"
        rows.append(row)
    out = pd.DataFrame(rows)
    for col in ["random_r2", "grouped_r2", "delta_r2_random_minus_grouped", "loso_r2"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.reset_index(drop=True)


def fig_matched_pairs(df: pd.DataFrame) -> None:
    x = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(10.5, 5.9))
    ax.vlines(x, df["grouped_r2"], df["random_r2"], linewidth=1.2, alpha=0.65)
    ax.scatter(x, df["random_r2"], marker="o", s=64, label="Row-random 5-fold CV", zorder=3)
    ax.scatter(x, df["grouped_r2"], marker="s", s=64, label="Primary-study GroupKFold", zorder=3)

    for i, row in df.iterrows():
        ax.annotate(f"{row['random_r2']:.2f}", (i, row["random_r2"]), xytext=(0, 7),
                    textcoords="offset points", ha="center", fontsize=8)
        ax.annotate(f"{row['grouped_r2']:.2f}", (i, row["grouped_r2"]), xytext=(0, -13),
                    textcoords="offset points", ha="center", fontsize=8)

    ax.axhline(0, linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(df["pair_label"])
    ax.set_ylabel("R²")
    ax.set_title("Matched validation on three independently reconstructed literature-derived corpora")
    ax.legend(frameon=False, ncol=2, loc="lower left")
    ax.margins(x=0.05)
    fig.tight_layout()
    fig.savefig(OUT / "Figure_1_matched_random_vs_study_aware.png", dpi=350, bbox_inches="tight")
    fig.savefig(OUT / "Figure_1_matched_random_vs_study_aware.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_delta(df: pd.DataFrame) -> None:
    x = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    bars = ax.bar(x, df["delta_r2_random_minus_grouped"])
    ax.set_xticks(x)
    ax.set_xticklabels(df["pair_label"])
    ax.set_ylabel("ΔR² = random R² − study-aware R²")
    ax.set_title("Magnitude of the validation optimism gap")
    ax.axhline(0, linewidth=0.9)
    for bar, value in zip(bars, df["delta_r2_random_minus_grouped"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{value:.2f}",
                ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "Figure_2_delta_r2.png", dpi=350, bbox_inches="tight")
    fig.savefig(OUT / "Figure_2_delta_r2.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_evidence_context() -> None:
    results = pd.read_csv(RESULTS)
    results["model_family"] = results["model"].map(model_family)
    comparators = pd.read_csv(COMPARATORS)
    records = []

    r = results[(results.dataset_id == "martin_v21_strict") & (results.model_family == "XGB")].iloc[0]
    records.append({"label": "V2.1\nXGB", "random": float(r.random_r2), "grouped": float(r.grouped_r2), "class": "CI-rerun independent"})

    r = results[(results.dataset_id == "liu_2025_strict") & (results.model_family == "CatBoost")].iloc[0]
    records.append({"label": "Liu dyes\nCatBoost", "random": float(r.random_r2), "grouped": float(r.grouped_r2), "class": "CI-rerun independent"})

    r = results[(results.dataset_id == "liu_2025_ammonia") & (results.model_family == "CatBoost")].iloc[0]
    records.append({"label": "Ammonia-N\nCatBoost", "random": float(r.random_r2), "grouped": float(r.grouped_r2), "class": "CI-rerun independent"})

    # Moosavi's registry stores the published-hyperparameter descriptor in
    # feature_set, while model is simply RF.
    hit = results[(results.dataset_id == "moosavi_2021_recoverable") &
                  (results.feature_set.astype(str).str.contains("published nine-variable", case=False, na=False))]
    if len(hit) != 1:
        raise RuntimeError(f"Expected one Moosavi published nine-variable result, got {len(hit)}")
    r = hit.iloc[0]
    records.append({"label": "Moosavi\nRF", "random": float(r.random_r2), "grouped": float(r.grouped_r2), "class": "CI-rerun lineage overlap"})

    a = comparators[comparators.comparator_id == "aguiar_2026_clays"].iloc[0]
    records.append({"label": "Aguiar\nRF", "random": float(a.conventional_r2), "grouped": float(a.source_aware_r2), "class": "Published comparator"})

    h = comparators[comparators.comparator_id == "huang_2026_heavy_metals"].iloc[0]
    records.append({"label": "Huang\nXGB", "random": np.nan, "grouped": float(h.source_aware_r2), "class": "Published source-aware positive comparator"})

    d = pd.DataFrame(records)
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(10.5, 5.8))

    paired = d.random.notna()
    ax.vlines(x[paired], d.loc[paired, "grouped"], d.loc[paired, "random"], linewidth=1.1, alpha=0.55)
    ax.scatter(x[paired], d.loc[paired, "random"], marker="o", s=58, label="Conventional/random")
    ax.scatter(x, d["grouped"], marker="s", s=58, label="Source/study-aware")

    ax.axhline(0, linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(d.label)
    ax.set_ylabel("R²")
    ax.set_title("Context: the study-aware effect is substantial but not universal")
    ax.legend(frameon=False, ncol=2, loc="lower left")

    foot = (
        "CI-rerun: V2.1, Liu dyes, ammonia-N, Moosavi.  "
        "Moosavi overlaps V2.1 lineage.  Aguiar/Huang are published-only comparators; Huang reports source-aware test R² only."
    )
    fig.text(0.5, 0.01, foot, ha="center", fontsize=7.5)
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(OUT / "Figure_3_evidence_context.png", dpi=350, bbox_inches="tight")
    fig.savefig(OUT / "Figure_3_evidence_context.pdf", bbox_inches="tight")
    d.to_csv(OUT / "Figure_3_evidence_context_values.csv", index=False)
    plt.close(fig)


def write_manifest(df: pd.DataFrame) -> None:
    manifest = {
        "source_files": [RESULTS.name, COMPARATORS.name],
        "primary_order": df[["dataset_id", "model_family"]].to_dict(orient="records"),
        "figures": [
            "Figure_1_matched_random_vs_study_aware",
            "Figure_2_delta_r2",
            "Figure_3_evidence_context",
        ],
        "numeric_mutation": False,
        "note": "Rendering-only pipeline. All numerical values originate in locked registries.",
    }
    (OUT / "manuscript_figure_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    df = primary_common()
    fig_matched_pairs(df)
    fig_delta(df)
    fig_evidence_context()
    write_manifest(df)
    print(df[["dataset_short", "model_family", "random_r2", "grouped_r2", "delta_r2_random_minus_grouped"]].to_string(index=False))
    print("Rendered publication figures to", OUT)


if __name__ == "__main__":
    main()
