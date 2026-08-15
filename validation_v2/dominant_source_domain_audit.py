"""Audit the dominant Moosavi source against the rest of the literature corpus.

Goals:
- establish whether the dominant source occupies a distinct target/feature regime;
- inspect material/pollutant diversity inside the 251-row block;
- flag whether one `source_link` may actually represent a compiled secondary
  dataset requiring finer provenance IDs before grouped validation is locked.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import study_aware_validation as base

OUT_DIR = Path(__file__).resolve().parent / "outputs"
DOMINANT_LABEL = "moosavi et al., 2023"


def summarize_numeric(frame: pd.DataFrame, cols: list[str]) -> list[dict]:
    rows = []
    for col in cols:
        s = pd.to_numeric(frame[col], errors="coerce")
        nonnull = s.dropna()
        rows.append(
            {
                "feature": col,
                "n": int(nonnull.size),
                "missing_percent": float(100 * s.isna().mean()),
                "min": float(nonnull.min()) if len(nonnull) else None,
                "p25": float(nonnull.quantile(0.25)) if len(nonnull) else None,
                "median": float(nonnull.median()) if len(nonnull) else None,
                "p75": float(nonnull.quantile(0.75)) if len(nonnull) else None,
                "max": float(nonnull.max()) if len(nonnull) else None,
            }
        )
    return rows


def categorical_counts(frame: pd.DataFrame, col: str, n=30):
    counts = frame[col].astype("string").fillna("<missing>").value_counts(dropna=False)
    return [
        {"value": str(idx), "rows": int(val), "percent": float(100 * val / len(frame))}
        for idx, val in counts.head(n).items()
    ]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = base.load_data()
    dom = df.loc[df["study_group"].eq(DOMINANT_LABEL)].copy()
    other = df.loc[~df["study_group"].eq(DOMINANT_LABEL)].copy()
    if dom.empty:
        raise RuntimeError(f"Dominant source not found: {DOMINANT_LABEL}")

    numeric_cols = base.NUMERIC_FEATURES + [base.TARGET]
    dom_num = pd.DataFrame(summarize_numeric(dom, numeric_cols))
    other_num = pd.DataFrame(summarize_numeric(other, numeric_cols))
    dom_num.to_csv(OUT_DIR / "dominant_source_numeric_summary.csv", index=False)
    other_num.to_csv(OUT_DIR / "other_sources_numeric_summary.csv", index=False)

    # Direct range-overlap diagnostic: fraction of dominant rows whose numeric
    # value lies outside the non-dominant observed min/max for each feature.
    overlap_rows = []
    for col in numeric_cols:
        ds = pd.to_numeric(dom[col], errors="coerce")
        os = pd.to_numeric(other[col], errors="coerce").dropna()
        if os.empty:
            overlap_rows.append({"feature": col, "other_min": None, "other_max": None,
                                 "dominant_nonmissing": int(ds.notna().sum()),
                                 "dominant_outside_other_range_percent": None})
            continue
        mask = ds.notna()
        outside = ((ds < os.min()) | (ds > os.max())) & mask
        pct = 100 * outside.sum() / max(mask.sum(), 1)
        overlap_rows.append(
            {
                "feature": col,
                "other_min": float(os.min()),
                "other_max": float(os.max()),
                "dominant_nonmissing": int(mask.sum()),
                "dominant_outside_other_range_percent": float(pct),
            }
        )
    pd.DataFrame(overlap_rows).to_csv(OUT_DIR / "dominant_source_range_overlap.csv", index=False)

    report = {
        "dominant_source": DOMINANT_LABEL,
        "dominant_rows": int(len(dom)),
        "other_rows": int(len(other)),
        "dominant_unique_adsorbents": int(dom["adsorbent"].nunique(dropna=True)),
        "dominant_unique_pollutants": int(dom["pollutant"].nunique(dropna=True)),
        "dominant_unique_processing_descriptions": int(dom["method_processing"].nunique(dropna=True)),
        "dominant_adsorbents_top": categorical_counts(dom, "adsorbent"),
        "dominant_pollutants_top": categorical_counts(dom, "pollutant"),
        "dominant_processing_top": categorical_counts(dom, "method_processing", n=20),
        "other_pollutants_top": categorical_counts(other, "pollutant"),
        "provenance_flag": (
            "A single citation contributes 251 rows and contains many distinct adsorbents/pollutants/processing settings. "
            "If that source is a secondary compiled ML dataset rather than one primary experiment, grouping all rows under "
            "one source is conservative but too coarse for final study-aware validation. Recover original-paper provenance "
            "for each row before locking grouped CV."
        ),
    }
    (OUT_DIR / "dominant_source_domain_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=== DOMINANT SOURCE DOMAIN AUDIT ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\n=== DOMINANT NUMERIC SUMMARY ===")
    print(dom_num.to_string(index=False))
    print("\n=== OTHER SOURCES NUMERIC SUMMARY ===")
    print(other_num.to_string(index=False))
    print("\n=== RANGE OVERLAP ===")
    print(pd.DataFrame(overlap_rows).to_string(index=False))


if __name__ == "__main__":
    main()
