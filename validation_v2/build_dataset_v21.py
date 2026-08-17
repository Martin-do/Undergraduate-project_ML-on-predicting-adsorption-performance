"""Build adsorption_dataset_v2_1.csv by extending frozen V2 provenance.

V2.1 rules:
- V2 (322 rows) is input and is never overwritten.
- Recover primary provenance for non-Iftikhar rows using reviewed source map.
- Keep review/composite rows unresolved if one primary adsorption experiment cannot be traced.
- Separate provenance confidence from modelling eligibility.
- Do not silently correct contradictory experimental fields; flag them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
import pandas as pd

V2 = Path(__file__).resolve().parent / "adsorption_dataset_v2.csv"
MAP = Path(__file__).resolve().parent / "non_iftikhar_primary_source_map_v21.csv"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED = {
    "rows": 322,
    "primary_confirmed_rows": 307,
    "primary_confirmed_studies": 29,
    "unresolved_rows": 15,
    "strict_comparable_rows": 273,
    "strict_comparable_studies": 24,
}


def norm(v: object) -> str:
    if pd.isna(v):
        return ""
    return " ".join(str(v).replace("\u00a0", " ").strip().lower().split())


def is_confirmed_status(s: object) -> bool:
    return norm(s).startswith("confirmed")


def main() -> None:
    df = pd.read_csv(V2, encoding="utf-8-sig")
    mp = pd.read_csv(MAP, encoding="utf-8-sig", keep_default_na=False)

    if len(df) != EXPECTED["rows"]:
        raise RuntimeError(f"Frozen V2 row count changed: {len(df)} != {EXPECTED['rows']}")

    out = df.copy()
    out["primary_study_id_v21"] = out["primary_study_id"].fillna("").astype(str)
    out["primary_study_citation_v21"] = out["primary_study_citation"].fillna("").astype(str)
    out["primary_study_doi_v21"] = out["primary_study_doi"].fillna("").astype(str)
    out["primary_provenance_confidence_v21"] = out["primary_provenance_confidence"].fillna("").astype(str)
    out["primary_provenance_status_v21"] = out["primary_provenance_status"].fillna("").astype(str)
    out["primary_provenance_evidence_v21"] = out["primary_provenance_evidence"].fillna("").astype(str)

    inherited_confirmed = out["primary_study_id_v21"].ne("")
    out["source_type_v21"] = ""
    out.loc[inherited_confirmed, "source_type_v21"] = "secondary_compilation_primary_reconstructed"
    out["record_granularity_v21"] = ""
    out.loc[inherited_confirmed, "record_granularity_v21"] = "experimental_condition"
    out["target_comparability_class_v21"] = ""
    out.loc[inherited_confirmed, "target_comparability_class_v21"] = "conventional_aqueous_adsorption_capacity"
    out["data_quality_note_v21"] = ""
    out["recommended_method_correction_v21"] = ""
    out["analysis_eligible_primary_provenance_v21"] = inherited_confirmed
    out["analysis_eligible_strict_comparable_v21"] = inherited_confirmed

    match_counts = []
    for _, r in mp.iterrows():
        src_token = norm(r["legacy_source_contains"])
        mask = out["source_link"].map(norm).str.contains(re.escape(src_token), regex=True, na=False)
        selector = str(r["adsorbent_selector"]).strip()
        if selector != "*":
            mask &= out["adsorbent"].astype(str).str.strip().eq(selector)

        n = int(mask.sum())
        if n == 0:
            raise RuntimeError(
                f"V2.1 source-map row matched zero records: {r['legacy_source_contains']} / {selector}"
            )
        match_counts.append({
            "legacy_source_contains": r["legacy_source_contains"],
            "adsorbent_selector": selector,
            "matched_rows": n,
            "status": r["provenance_status_v21"],
        })

        confirmed = is_confirmed_status(r["provenance_status_v21"])
        if confirmed:
            out.loc[mask, "primary_study_id_v21"] = r["primary_study_id_v21"]
            out.loc[mask, "primary_study_citation_v21"] = r["primary_citation_v21"]
            out.loc[mask, "primary_study_doi_v21"] = r["primary_doi_v21"]
            out.loc[mask, "primary_provenance_confidence_v21"] = r["confidence_v21"]
            out.loc[mask, "primary_provenance_status_v21"] = r["provenance_status_v21"]
            out.loc[mask, "primary_provenance_evidence_v21"] = r["data_quality_note_v21"]
            out.loc[mask, "analysis_eligible_primary_provenance_v21"] = True
        else:
            out.loc[mask, "primary_study_id_v21"] = ""
            out.loc[mask, "primary_study_citation_v21"] = ""
            out.loc[mask, "primary_study_doi_v21"] = ""
            out.loc[mask, "primary_provenance_confidence_v21"] = r["confidence_v21"]
            out.loc[mask, "primary_provenance_status_v21"] = r["provenance_status_v21"]
            out.loc[mask, "primary_provenance_evidence_v21"] = r["data_quality_note_v21"]
            out.loc[mask, "analysis_eligible_primary_provenance_v21"] = False

        out.loc[mask, "source_type_v21"] = r["source_type_v21"]
        out.loc[mask, "record_granularity_v21"] = r["record_granularity_v21"]
        out.loc[mask, "target_comparability_class_v21"] = r["target_comparability_class_v21"]
        out.loc[mask, "data_quality_note_v21"] = r["data_quality_note_v21"]
        out.loc[mask, "analysis_eligible_strict_comparable_v21"] = (
            norm(r["eligible_strict_comparable_v21"]) == "yes"
        )

    corrections = {
        "RH-IC": "Replace 'Untreated' with rice husk ash / thermally converted rice-husk material after source-level re-extraction.",
        "OP-Pb": "Replace 'Untreated' with xanthate-modified orange peel (CS2 treatment in alkaline medium) after source-level re-extraction.",
        "OliveS-Phenol": "Replace 'Untreated' with activated olive stones after source-level re-extraction.",
    }
    for ads, note in corrections.items():
        sel = out["adsorbent"].astype(str).str.strip().eq(ads)
        out.loc[sel, "recommended_method_correction_v21"] = note

    unresolved = out["primary_study_id_v21"].eq("")
    out.loc[unresolved, "analysis_eligible_primary_provenance_v21"] = False
    out.loc[unresolved, "analysis_eligible_strict_comparable_v21"] = False

    def exclusion_reason(row) -> str:
        if bool(row["analysis_eligible_strict_comparable_v21"]):
            return ""
        if not bool(row["analysis_eligible_primary_provenance_v21"]):
            if str(row["adsorbent"]).strip() == "CS":
                return "iftikhar_CS_primary_study_unresolved"
            if "Ajien" in str(row["source_link"]):
                return "review_composite_not_traceable_to_one_primary_adsorption_experiment"
            return "primary_study_unresolved"
        tc = str(row["target_comparability_class_v21"])
        if tc == "nonaqueous_oil_quality_derived_uptake":
            return "target_not_conventional_aqueous_adsorption_capacity"
        if tc == "bulk_water_quality_derived_uptake":
            return "bulk_water_quality_proxy_not_comparable_to_equilibrium_qe"
        if str(row["recommended_method_correction_v21"]).strip():
            return "processing_field_conflicts_with_recovered_primary_source"
        return "data_quality_or_comparability_gate"

    out["strict_comparable_exclusion_reason_v21"] = out.apply(exclusion_reason, axis=1)
    out["provenance_tier_v21"] = "unresolved"
    out.loc[out["analysis_eligible_primary_provenance_v21"], "provenance_tier_v21"] = "primary_confirmed"
    ajien = out["source_link"].astype(str).str.contains("Ajien", case=False, na=False)
    out.loc[ajien, "provenance_tier_v21"] = "review_secondary_composite"

    confirmed_rows = int(out["analysis_eligible_primary_provenance_v21"].sum())
    confirmed_studies = int(out.loc[
        out["analysis_eligible_primary_provenance_v21"], "primary_study_id_v21"
    ].nunique())
    strict_rows = int(out["analysis_eligible_strict_comparable_v21"].sum())
    strict_studies = int(out.loc[
        out["analysis_eligible_strict_comparable_v21"], "primary_study_id_v21"
    ].nunique())
    unresolved_rows = int((~out["analysis_eligible_primary_provenance_v21"]).sum())

    actual = {
        "rows": int(len(out)),
        "primary_confirmed_rows": confirmed_rows,
        "primary_confirmed_studies": confirmed_studies,
        "unresolved_rows": unresolved_rows,
        "strict_comparable_rows": strict_rows,
        "strict_comparable_studies": strict_studies,
    }
    if actual != EXPECTED:
        raise RuntimeError(f"V2.1 locked counts failed: actual={actual}, expected={EXPECTED}")

    baseline = int(df["analysis_eligible_confirmed_primary_v2"].sum())
    summary = {
        **actual,
        "v2_baseline_confirmed_rows": baseline,
        "newly_primary_reconstructed_non_iftikhar_rows": confirmed_rows - baseline,
        "remaining_unresolved_breakdown": {
            "iftikhar_CS": int(out["adsorbent"].astype(str).str.strip().eq("CS").sum()),
            "Ajien_review_composite": int(ajien.sum()),
        },
        "strict_comparable_excluded_but_primary_confirmed_rows": int(confirmed_rows - strict_rows),
        "method_field_conflict_rows": int(out["recommended_method_correction_v21"].ne("").sum()),
        "target_comparability_counts": out["target_comparability_class_v21"].replace("", "unresolved").value_counts().to_dict(),
        "record_granularity_counts": out["record_granularity_v21"].replace("", "unresolved").value_counts().to_dict(),
        "guardrails": [
            "Frozen adsorption_dataset_v2.csv is not modified.",
            "A recovered citation does not automatically make a row modelling-eligible.",
            "Ajien review-composite rows remain primary-unresolved.",
            "Three Sulyman-derived rows with processing-field conflicts are primary-traceable but excluded from strict-comparable validation until corrected.",
            "Schneider oil-acidity and Kuok bulk-water-quality targets are retained but excluded from conventional-aqueous-capacity validation.",
            "No Q_MAX=624 filtering is applied.",
        ],
    }

    out_path = OUT_DIR / "adsorption_dataset_v2_1.csv"
    out.to_csv(out_path, index=False)
    pd.DataFrame(match_counts).to_csv(OUT_DIR / "non_iftikhar_v21_match_audit.csv", index=False)
    (OUT_DIR / "adsorption_dataset_v2_1_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=== ADSORPTION DATASET V2.1 SUMMARY ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
