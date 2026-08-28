"""Build Paper 1 draft figures from frozen machine-readable evidence.

This script is intentionally descriptive. It does not fit new predictive models,
retune existing models, or search for a favourable subset. Project-generated
numerical values are read from MULTIDATASET_RESULTS_REGISTRY.csv.

Outputs
-------
paper1/manuscript/figures/
    fig2_random_vs_grouped_r2.png
    fig3_validation_gap_vs_study_count.png
    fig4_loso_r2_summary.png
    fig5_claim_validation_alignment.png
    figure_values_used.csv

Run from repository root:
    python paper1/manuscript/build_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "validation_v2" / "MULTIDATASET_RESULTS_REGISTRY.csv"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)


# Frozen representative choices from PAPER1_MULTIDATASET_EVIDENCE_FREEZE.md.
# feature_match is required where a dataset contains multiple rows with the same
# model label. Moosavi is retained only as lineage sensitivity.
SELECTIONS = [
    ("martin_v21_strict", "XGB", None, "Dataset A\nV2.1", "primary"),
    ("liu_2025_strict", "CatBoost500", None, "Liu dye\n2025", "primary"),
    ("liu_2025_ammonia", "CatBoost500", None, "Liu ammonia-N\n2025", "primary"),
    (
        "moosavi_2021_recoverable",
        "RF",
        "published nine-variable feature set",
        "Moosavi\n2021*",
        "lineage",
    ),
]


def load_representatives() -> pd.DataFrame:
    df = pd.read_csv(REGISTRY)
    rows = []
    for dataset_id, model, feature_match, label, role in SELECTIONS:
        hit = df[(df["dataset_id"] == dataset_id) & (df["model"] == model)]
        if feature_match is not None:
            hit = hit[hit["feature_set"].astype(str).str.contains(feature_match, regex=False)]
        if len(hit) != 1:
            qualifier = f" / feature contains {feature_match!r}" if feature_match else ""
            raise RuntimeError(
                f"Expected exactly one registry row for {dataset_id}/{model}{qualifier}; found {len(hit)}"
            )
        r = hit.iloc[0].copy()
        r["plot_label"] = label
        r["plot_role"] = role
        rows.append(r)
    out = pd.DataFrame(rows)
    required = [
        "random_r2",
        "grouped_r2",
        "delta_r2_random_minus_grouped",
        "loso_r2",
        "n_rows",
        "n_groups",
    ]
    for col in required:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def fig2_paired_r2(rep: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 5.3))
    for _, r in rep.iterrows():
        linestyle = "--" if r["plot_role"] == "lineage" else "-"
        ax.plot(
            [0, 1],
            [r["random_r2"], r["grouped_r2"]],
            marker="o",
            linewidth=2,
            linestyle=linestyle,
            label=r["plot_label"].replace("\n", " "),
        )
    ax.axhline(0, linewidth=0.8)
    ax.set_xticks([0, 1], ["Row-random", "Primary-study grouped"])
    ax.set_ylabel("R²")
    ax.set_title("Matched performance changes when the validation unit changes")
    ax.legend(frameon=False)
    ax.text(
        0.01,
        0.01,
        "*Moosavi is lineage-overlapping and is not counted as independent replication.",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig2_random_vs_grouped_r2.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig3_gap_vs_groups(rep: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 5.3))
    for _, r in rep.iterrows():
        marker = "x" if r["plot_role"] == "lineage" else "o"
        ax.scatter(r["n_groups"], r["delta_r2_random_minus_grouped"], s=75, marker=marker)
        ax.annotate(
            r["plot_label"].replace("\n", " "),
            (r["n_groups"], r["delta_r2_random_minus_grouped"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
        )
    ax.set_xlabel("Independent primary-study groups")
    ax.set_ylabel("ΔR² (row-random − grouped)")
    ax.set_title("Validation-gap magnitude and primary-study count")
    ax.text(
        0.01,
        0.01,
        "Descriptive only; four points do not support a causal trend analysis.",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig3_validation_gap_vs_study_count.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig4_loso(rep: pd.DataFrame) -> None:
    data = rep.dropna(subset=["loso_r2"]).copy()
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.bar(data["plot_label"], data["loso_r2"])
    ax.axhline(0, linewidth=0.8)
    ax.set_ylabel("Pooled study-LOSO R²")
    ax.set_title("Leave-one-study-out robustness")
    ax.text(
        0.01,
        0.01,
        "Pooled LOSO should be interpreted alongside per-study errors and group sizes.",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig4_loso_r2_summary.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig5_claim_validation_schematic() -> None:
    fig, ax = plt.subplots(figsize=(10.0, 4.7))
    ax.axis("off")

    ax.text(0.20, 0.90, "Row-random validation", ha="center", fontsize=13, weight="bold")
    ax.text(
        0.20,
        0.67,
        "Rows from the same study\ncan occur in training and validation",
        ha="center",
        va="center",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5"),
    )
    ax.annotate("", xy=(0.20, 0.42), xytext=(0.20, 0.56), arrowprops=dict(arrowstyle="->"))
    ax.text(
        0.20,
        0.27,
        "Estimates interpolation to new rows\nfrom represented systems",
        ha="center",
        va="center",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5"),
    )

    ax.text(0.78, 0.90, "Primary-study grouped validation", ha="center", fontsize=13, weight="bold")
    ax.text(
        0.78,
        0.67,
        "All rows from a held-out study\nremain outside training",
        ha="center",
        va="center",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5"),
    )
    ax.annotate("", xy=(0.78, 0.42), xytext=(0.78, 0.56), arrowprops=dict(arrowstyle="->"))
    ax.text(
        0.78,
        0.27,
        "Estimates transfer to an\nunseen primary study",
        ha="center",
        va="center",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5"),
    )

    ax.text(
        0.50,
        0.05,
        "Neither design is universally 'correct': the validation unit must match the scientific claim.",
        ha="center",
        fontsize=11,
        weight="bold",
    )
    fig.tight_layout()
    fig.savefig(OUT / "fig5_claim_validation_alignment.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    rep = load_representatives()
    rep[
        [
            "dataset_id",
            "plot_label",
            "plot_role",
            "model",
            "feature_set",
            "n_rows",
            "n_groups",
            "random_r2",
            "grouped_r2",
            "delta_r2_random_minus_grouped",
            "loso_r2",
        ]
    ].to_csv(OUT / "figure_values_used.csv", index=False)

    fig2_paired_r2(rep)
    fig3_gap_vs_groups(rep)
    fig4_loso(rep)
    fig5_claim_validation_schematic()
    print(f"Wrote Paper 1 figures to {OUT}")


if __name__ == "__main__":
    main()
