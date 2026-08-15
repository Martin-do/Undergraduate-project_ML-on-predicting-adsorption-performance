"""Quantify precursor-domain composition for the reconstructed Iftikhar block.

The audit is descriptive. It never changes the raw dataset and it never promotes an
uncertain precursor class to a stricter domain.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import study_aware_validation as base

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
PRIMARY_MAP = HERE / "primary_study_map.csv"
DOMAIN_MAP = HERE / "adsorbent_domain_map.csv"
DOMINANT_LEGACY_TOKEN = "moosavi"


def norm(v: object) -> str:
    return "" if pd.isna(v) else " ".join(str(v).strip().lower().split())


def main() -> None:
    df = base.load_data().copy()
    dominant = df["source_link"].map(norm).str.contains(DOMINANT_LEGACY_TOKEN, na=False)
    inherited = df.loc[dominant].copy()

    pmap = pd.read_csv(PRIMARY_MAP, keep_default_na=False)
    dmap = pd.read_csv(DOMAIN_MAP, keep_default_na=False)
    merged_map = pmap.merge(dmap, on="project_adsorbent", how="left", validate="one_to_one")
    if merged_map["domain_class"].eq("").any() or merged_map["domain_class"].isna().any():
        missing = merged_map.loc[merged_map["domain_class"].fillna("").eq(""), "project_adsorbent"].tolist()
        raise ValueError(f"Missing domain classification for mapped adsorbents: {missing}")

    cols = [
        "project_adsorbent", "primary_study_id", "status", "doi",
        "domain_class", "strict_agricultural_waste", "broad_biogenic_waste",
        "waste_derived_carbon", "domain_confidence", "domain_note",
    ]
    lookup = merged_map[cols].rename(columns={"project_adsorbent": "adsorbent"})
    inherited["adsorbent"] = inherited["adsorbent"].astype(str).str.strip()
    inherited = inherited.merge(lookup, on="adsorbent", how="left", validate="many_to_one")

    if inherited["domain_class"].isna().any():
        missing = sorted(inherited.loc[inherited["domain_class"].isna(), "adsorbent"].unique().tolist())
        raise ValueError(f"Inherited rows missing domain map: {missing}")

    inherited.to_csv(OUT / "inherited_rows_with_domain_class.csv", index=False)

    by_domain = (
        inherited.groupby("domain_class", dropna=False)
        .agg(rows=("qe_mg_g", "size"), adsorbents=("adsorbent", "nunique"), primary_studies=("primary_study_id", lambda s: s[s != ""].nunique()))
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    by_domain["row_percent"] = 100.0 * by_domain["rows"] / len(inherited)
    by_domain.to_csv(OUT / "precursor_domain_counts.csv", index=False)

    subset_rows = []
    for flag in ["strict_agricultural_waste", "broad_biogenic_waste", "waste_derived_carbon"]:
        selected = inherited[inherited[flag].eq("yes")].copy()
        confirmed = selected[selected["primary_study_id"].ne("")]
        subset_rows.append({
            "subset": flag,
            "rows": int(len(selected)),
            "confirmed_primary_rows": int(len(confirmed)),
            "adsorbents": int(selected["adsorbent"].nunique()),
            "primary_studies": int(confirmed["primary_study_id"].nunique()),
            "primary_study_ids": " | ".join(sorted(confirmed["primary_study_id"].unique().tolist())),
        })
    subsets = pd.DataFrame(subset_rows)
    subsets.to_csv(OUT / "precursor_domain_candidate_subsets.csv", index=False)

    study_domain = (
        inherited[inherited["primary_study_id"].ne("")]
        .groupby("primary_study_id")
        .agg(
            rows=("qe_mg_g", "size"),
            adsorbents=("adsorbent", lambda s: " | ".join(sorted(set(s)))),
            domain_classes=("domain_class", lambda s: " | ".join(sorted(set(s)))),
            strict_agri_rows=("strict_agricultural_waste", lambda s: int((s == "yes").sum())),
            broad_biogenic_rows=("broad_biogenic_waste", lambda s: int((s == "yes").sum())),
            waste_derived_rows=("waste_derived_carbon", lambda s: int((s == "yes").sum())),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    study_domain.to_csv(OUT / "primary_study_domain_composition.csv", index=False)

    strict_n = int(subsets.loc[subsets["subset"].eq("strict_agricultural_waste"), "primary_studies"].iloc[0])
    broad_n = int(subsets.loc[subsets["subset"].eq("broad_biogenic_waste"), "primary_studies"].iloc[0])
    waste_n = int(subsets.loc[subsets["subset"].eq("waste_derived_carbon"), "primary_studies"].iloc[0])

    summary = {
        "inherited_rows": int(len(inherited)),
        "domain_classes": int(inherited["domain_class"].nunique()),
        "strict_agricultural_primary_studies": strict_n,
        "broad_biogenic_waste_primary_studies": broad_n,
        "waste_derived_carbon_primary_studies": waste_n,
        "strict_agricultural_support_gate": "insufficient_for_5fold_groupcv" if strict_n < 5 else "supports_5fold_groupcv",
        "guardrails": [
            "Only rows explicitly marked yes enter a candidate subset.",
            "unknown/mixed/uncertain rows are excluded rather than promoted.",
            "Subset labels describe precursor provenance, not proof of chemical comparability.",
        ],
    }
    (OUT / "precursor_domain_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== PRECURSOR DOMAIN COUNTS ===")
    print(by_domain.to_string(index=False))
    print("\n=== CANDIDATE SUBSETS ===")
    print(subsets.to_string(index=False))
    print("\n=== PRIMARY-STUDY DOMAIN COMPOSITION ===")
    print(study_domain.to_string(index=False))
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
