"""Lightweight deterministic leakage audit for the manuscript result manifest.

This reuses the V2 dataset loader and legacy-style partition audit but does not run
models or bootstraps. It exists so leakage counts are regenerated in the same CI
job as the final manifest.
"""
from __future__ import annotations

import json
from pathlib import Path

import study_aware_validation as base

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    df = base.load_data()
    counts = df.groupby("study_group", dropna=False).size().sort_values(ascending=False)
    payload = {
        "dataset_rows_with_target": int(len(df)),
        "unique_legacy_source_groups": int(df["study_group"].nunique()),
        "largest_legacy_source_group_rows": int(counts.max()),
        "median_rows_per_legacy_source_group": float(counts.median()),
        "legacy_style_random_partition_overlap": base.random_split_overlap_audit(df),
        "guardrail": "Legacy source labels are provenance diagnostics only; primary-study IDs supersede them where reconstructed.",
    }
    (OUT / "manifest_leakage_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("=== MANIFEST LEAKAGE AUDIT ===")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
