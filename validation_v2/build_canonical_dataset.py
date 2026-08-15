"""Build the canonical provenance-aware adsorption dataset V2.

Scientific rules
----------------
* The original `final_final_adsorption_done_dataset.csv` remains read-only.
* V2 contains only rows with a usable adsorption-capacity target under the same
  conservative parser used by the validation harness (322 rows at the locked
  revision state).
* Original row identity is preserved so every V2 row is traceable back to the
  325-row source file.
* Rows historically labelled `Moosavi et al., 2023` receive the corrected
  Iftikhar et al. 2023 secondary-source attribution in NEW fields; the legacy
  source label is never overwritten.
* Primary-study IDs are attached only for confirmed mappings.
* Domain labels are attached only to the inherited adsorbent codes for which a
  reviewed domain map exists. Unknowns remain explicit.
* Analysis eligibility is expressed with flags; rows are not silently deleted to
  manufacture a preferred modelling subset.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "final_final_adsorption_done_dataset.csv"
MAP = Path(__file__).resolve().parent / "primary_study_map.csv"
DOMAIN_MAP = Path(__file__).resolve().parent / "adsorbent_domain_map.csv"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

DOMINANT_LEGACY_TOKEN = "moosavi"
SECONDARY_SOURCE_ID = "Iftikhar_2023_SPT_124891"
SECONDARY_CITATION = (
    "Iftikhar S., Zahra N., Rubab F., Sumra R.A., Khan M.B., Abbas A., Jaffari Z.H. "
    "Artificial neural networks for insights into adsorption capacity of industrial dyes using "
    "carbon-based materials. Separation and Purification Technology 326 (2023) 124891."
)
SECONDARY_DOI = "10.1016/j.seppur.2023.124891"
UPSTREAM_REPOSITORY = "Sara-Iftikhar/ai4adsorption"
UPSTREAM_WORKBOOK = "Adsorption and regeneration data_1007c.xlsx"

# These values are the locked V2 scientific audit counts. The builder fails if a
# future edit changes them without an explicit scientific review.
LOCKED_COUNTS = {
    "source_rows": 325,
    "usable_target_rows_v2": 322,
    "iftikhar_inherited_rows": 251,
    "confirmed_primary_rows": 238,
    "confirmed_primary_studies": 11,
    "unresolved_inherited_rows": 13,
    "non_iftikhar_rows": 71,
    "strict_agricultural_rows": 65,
    "broad_biogenic_rows": 92,
    "waste_derived_carbon_rows": 138,
}

MISSING_TOKENS = {
    "", "n/a", "na", "n/p", "np", "not provided", "none", "nan"
}


def norm(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def parse_numeric(value: object) -> float:
    """Mirror the validation harness's conservative heterogeneous-number parser."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.number)):
        return float(value)
    s = str(value).strip().lower().replace("−", "-").replace("–", "-")
    if s in MISSING_TOKENS:
        return np.nan
    s = s.replace(",", "")
    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if not nums:
        return np.nan
    vals = [float(x) for x in nums]
    if len(vals) >= 2 and "-" in s and not s.lstrip().startswith("-"):
        return float(np.mean(vals[:2]))
    return vals[0]


def pollutant_class(value: object) -> str:
    s = norm(value)
    if not s:
        return "unknown"

    dye_tokens = [
        "dye", "methylene blue", "malachite green", "basic violet", "indigo carmine",
        "phenol red", "rhodamine", "congo red", "methyl violet", "alizarin red",
        "reactive", "yellow", "neutral red", "acid blue", "ab25", "rb5", "rhd b",
        " c-red", "cblue", "ccb", "ccr", "ccy", "gr", " am", "mo", "mb", "mv",
    ]
    metal_tokens = ["pb", "cu", "zn", "cd", "cr(vi)", "heavy metal"]
    water_quality_tokens = [
        "acidity", "total suspended solids", "ammoniacal nitrogen", "oil & grease",
    ]
    pharmaceutical_tokens = ["sulfonamide", "antibiotic", "diclofenac"]

    if any(t in s for t in dye_tokens):
        return "dye"
    if any(t in s for t in metal_tokens):
        return "metal_ion"
    if any(t in s for t in pharmaceutical_tokens):
        return "pharmaceutical"
    if any(t in s for t in water_quality_tokens):
        return "bulk_water_quality"
    if "phenol" in s:
        return "organic_contaminant"
    return "other_or_unresolved"


def _yes(series: pd.Series) -> pd.Series:
    return series.astype("string").str.lower().eq("yes")


def build_data_dictionary() -> pd.DataFrame:
    rows = [
        ("v2_row_id", "Stable 1..N row identifier within adsorption_dataset_v2.csv."),
        ("original_row_id", "1-based row identifier in final_final_adsorption_done_dataset.csv before V2 target filtering."),
        ("legacy_source_link", "Original source_link retained verbatim for forensic traceability."),
        ("source_scope_v2", "Whether the row belongs to the inherited Iftikhar block or the non-Iftikhar remainder."),
        ("secondary_source_id", "Corrected secondary compilation identifier where established."),
        ("secondary_source_citation", "Corrected secondary-source citation where established."),
        ("secondary_source_doi", "Corrected secondary-source DOI where established."),
        ("secondary_source_repository", "Upstream reproducibility repository where established."),
        ("secondary_source_workbook", "Upstream workbook lineage where established."),
        ("source_label_correction_status", "Whether a legacy source attribution was corrected in V2 metadata."),
        ("primary_study_id", "Confirmed underlying primary-study identifier; blank if not reconstructed/confirmed."),
        ("primary_study_citation", "Confirmed primary-study citation."),
        ("primary_study_doi", "Confirmed primary-study DOI."),
        ("primary_provenance_confidence", "Confidence recorded by the reviewed provenance map."),
        ("primary_provenance_status", "confirmed / unresolved / not_reconstructed_non_iftikhar."),
        ("primary_provenance_evidence", "Evidence note supporting the primary-study assignment."),
        ("provenance_tier_v2", "primary_confirmed, secondary_only_unresolved_primary, or source_not_reconstructed."),
        ("pollutant_class_v2", "Coarse pollutant class used for corpus/domain auditing."),
        ("domain_class_v2", "Reviewed precursor/material-domain class where mapped."),
        ("domain_confidence_v2", "Confidence of the precursor-domain classification."),
        ("domain_note_v2", "Human-readable reason for the precursor-domain classification."),
        ("strict_agricultural_waste_v2", "yes/no/unknown domain flag from the reviewed map."),
        ("broad_biogenic_waste_v2", "yes/no/unknown domain flag from the reviewed map."),
        ("waste_derived_carbon_v2", "yes/no/unknown domain flag from the reviewed map."),
        ("analysis_eligible_full_corpus_v2", "True for every row in this 322-row usable-target V2 file."),
        ("analysis_eligible_confirmed_primary_v2", "True only for inherited rows with confirmed primary-study provenance."),
        ("analysis_eligible_strict_agricultural_v2", "Confirmed-primary rows also classified as strict agricultural waste."),
        ("analysis_eligible_broad_biogenic_v2", "Confirmed-primary rows also classified as broad biogenic waste."),
        ("analysis_eligible_waste_derived_carbon_v2", "Confirmed-primary rows also classified as waste-derived carbon."),
        ("confirmed_primary_exclusion_reason_v2", "Reason a row is excluded from strict confirmed-primary analysis."),
    ]
    return pd.DataFrame(rows, columns=["column", "description"])


def main() -> None:
    raw = pd.read_csv(DATA, encoding="utf-8-sig")
    mapping = pd.read_csv(MAP, encoding="utf-8-sig", keep_default_na=False)
    domain_map = pd.read_csv(DOMAIN_MAP, encoding="utf-8-sig", keep_default_na=False)

    if "source_link" not in raw or "adsorbent" not in raw or "qe_mg_g" not in raw:
        raise ValueError("Expected source_link, adsorbent and qe_mg_g in original dataset")

    # Preserve the exact source-row identity before filtering.
    raw = raw.copy()
    raw.insert(0, "original_row_id", range(1, len(raw) + 1))
    target_numeric = raw["qe_mg_g"].map(parse_numeric)
    usable = target_numeric.notna()
    canonical = raw.loc[usable].copy().reset_index(drop=True)
    canonical.insert(0, "v2_row_id", range(1, len(canonical) + 1))
    canonical["qe_mg_g"] = target_numeric.loc[usable].to_numpy(float)

    legacy_dom = canonical["source_link"].map(norm).str.contains(DOMINANT_LEGACY_TOKEN, na=False)

    # Preserve legacy evidence and add corrected secondary provenance without
    # overwriting the source field used in the historical project.
    canonical["legacy_source_link"] = canonical["source_link"]
    canonical["source_scope_v2"] = np.where(legacy_dom, "iftikhar_inherited", "non_iftikhar")
    canonical["secondary_source_id"] = ""
    canonical["secondary_source_citation"] = ""
    canonical["secondary_source_doi"] = ""
    canonical["secondary_source_repository"] = ""
    canonical["secondary_source_workbook"] = ""
    canonical["source_label_correction_status"] = "not_applicable"

    canonical.loc[legacy_dom, "secondary_source_id"] = SECONDARY_SOURCE_ID
    canonical.loc[legacy_dom, "secondary_source_citation"] = SECONDARY_CITATION
    canonical.loc[legacy_dom, "secondary_source_doi"] = SECONDARY_DOI
    canonical.loc[legacy_dom, "secondary_source_repository"] = UPSTREAM_REPOSITORY
    canonical.loc[legacy_dom, "secondary_source_workbook"] = UPSTREAM_WORKBOOK
    canonical.loc[legacy_dom, "source_label_correction_status"] = (
        "legacy_label_misattributed_corrected_in_v2_metadata"
    )

    # Primary provenance starts explicit rather than implied.
    canonical["primary_study_id"] = ""
    canonical["primary_study_citation"] = ""
    canonical["primary_study_doi"] = ""
    canonical["primary_provenance_confidence"] = ""
    canonical["primary_provenance_status"] = np.where(
        legacy_dom, "unresolved", "not_reconstructed_non_iftikhar"
    )
    canonical["primary_provenance_evidence"] = ""

    confirmed = mapping[mapping["status"].str.startswith("confirmed")].copy()
    duplicate_ads = confirmed["project_adsorbent"].duplicated(keep=False)
    if duplicate_ads.any():
        raise ValueError(
            "Confirmed primary map currently requires unique project_adsorbent keys; "
            f"duplicates found: {confirmed.loc[duplicate_ads, 'project_adsorbent'].tolist()}"
        )

    lookup = confirmed.set_index("project_adsorbent").to_dict("index")
    for idx in canonical.index[legacy_dom]:
        ads = str(canonical.at[idx, "adsorbent"]).strip()
        item = lookup.get(ads)
        if not item:
            continue
        canonical.at[idx, "primary_study_id"] = item["primary_study_id"]
        canonical.at[idx, "primary_study_citation"] = item["primary_citation"]
        canonical.at[idx, "primary_study_doi"] = item["doi"]
        canonical.at[idx, "primary_provenance_confidence"] = item["confidence"]
        canonical.at[idx, "primary_provenance_status"] = item["status"]
        canonical.at[idx, "primary_provenance_evidence"] = item["evidence_note"]

    confirmed_primary = legacy_dom & canonical["primary_study_id"].ne("")
    canonical["provenance_tier_v2"] = "source_not_reconstructed"
    canonical.loc[legacy_dom & ~confirmed_primary, "provenance_tier_v2"] = (
        "secondary_only_unresolved_primary"
    )
    canonical.loc[confirmed_primary, "provenance_tier_v2"] = "primary_confirmed"

    # Pollutant and precursor-domain metadata.
    canonical["pollutant_class_v2"] = canonical["pollutant"].map(pollutant_class)
    canonical["domain_class_v2"] = "not_classified"
    canonical["strict_agricultural_waste_v2"] = "unknown"
    canonical["broad_biogenic_waste_v2"] = "unknown"
    canonical["waste_derived_carbon_v2"] = "unknown"
    canonical["domain_confidence_v2"] = ""
    canonical["domain_note_v2"] = ""

    if domain_map["project_adsorbent"].duplicated().any():
        raise ValueError("adsorbent_domain_map.csv must have unique project_adsorbent keys")
    dlookup = domain_map.set_index("project_adsorbent").to_dict("index")
    for idx in canonical.index[legacy_dom]:
        ads = str(canonical.at[idx, "adsorbent"]).strip()
        item = dlookup.get(ads)
        if not item:
            continue
        canonical.at[idx, "domain_class_v2"] = item["domain_class"]
        canonical.at[idx, "strict_agricultural_waste_v2"] = item["strict_agricultural_waste"]
        canonical.at[idx, "broad_biogenic_waste_v2"] = item["broad_biogenic_waste"]
        canonical.at[idx, "waste_derived_carbon_v2"] = item["waste_derived_carbon"]
        canonical.at[idx, "domain_confidence_v2"] = item["domain_confidence"]
        canonical.at[idx, "domain_note_v2"] = item["domain_note"]

    # Analysis-scope flags. These are the canonical selectors used by the revised
    # study; they make inclusion/exclusion inspectable at row level.
    canonical["analysis_eligible_full_corpus_v2"] = True
    canonical["analysis_eligible_confirmed_primary_v2"] = confirmed_primary
    canonical["analysis_eligible_strict_agricultural_v2"] = (
        confirmed_primary & _yes(canonical["strict_agricultural_waste_v2"])
    )
    canonical["analysis_eligible_broad_biogenic_v2"] = (
        confirmed_primary & _yes(canonical["broad_biogenic_waste_v2"])
    )
    canonical["analysis_eligible_waste_derived_carbon_v2"] = (
        confirmed_primary & _yes(canonical["waste_derived_carbon_v2"])
    )

    canonical["confirmed_primary_exclusion_reason_v2"] = ""
    canonical.loc[~legacy_dom, "confirmed_primary_exclusion_reason_v2"] = (
        "non_iftikhar_source_not_reconstructed_to_primary_study_in_v2"
    )
    canonical.loc[legacy_dom & ~confirmed_primary, "confirmed_primary_exclusion_reason_v2"] = (
        "inherited_row_primary_study_unresolved"
    )

    out_csv = OUT / "adsorption_dataset_v2.csv"
    canonical.to_csv(out_csv, index=False, encoding="utf-8-sig")
    # Keep the previous filename as a compatibility alias for existing audit code.
    canonical.to_csv(OUT / "canonical_adsorption_dataset.csv", index=False, encoding="utf-8-sig")

    counts = {
        "source_rows": int(len(raw)),
        "usable_target_rows_v2": int(len(canonical)),
        "excluded_missing_target_rows": int((~usable).sum()),
        "iftikhar_inherited_rows": int(legacy_dom.sum()),
        "confirmed_primary_rows": int(canonical["analysis_eligible_confirmed_primary_v2"].sum()),
        "confirmed_primary_studies": int(
            canonical.loc[canonical["analysis_eligible_confirmed_primary_v2"], "primary_study_id"].nunique()
        ),
        "unresolved_inherited_rows": int((legacy_dom & ~confirmed_primary).sum()),
        "non_iftikhar_rows": int((~legacy_dom).sum()),
        "strict_agricultural_rows": int(canonical["analysis_eligible_strict_agricultural_v2"].sum()),
        "broad_biogenic_rows": int(canonical["analysis_eligible_broad_biogenic_v2"].sum()),
        "waste_derived_carbon_rows": int(canonical["analysis_eligible_waste_derived_carbon_v2"].sum()),
    }

    mismatches = {
        k: {"expected": LOCKED_COUNTS[k], "actual": counts[k]}
        for k in LOCKED_COUNTS
        if counts.get(k) != LOCKED_COUNTS[k]
    }
    if mismatches:
        raise RuntimeError(
            "Canonical dataset no longer matches locked V2 scientific counts: "
            + json.dumps(mismatches, indent=2)
        )

    unresolved_adsorbents = sorted(
        canonical.loc[legacy_dom & ~confirmed_primary, "adsorbent"].astype(str).unique().tolist()
    )
    summary = {
        **counts,
        "output_file": str(out_csv.relative_to(ROOT)),
        "unresolved_inherited_adsorbents": unresolved_adsorbents,
        "target_rule": "retain rows where qe_mg_g parses to a finite numeric value; no Q_MAX upper truncation",
        "primary_analysis_scope": "238 confirmed Iftikhar-derived rows from 11 reconstructed primary studies",
        "guardrails": [
            "The original 325-row CSV is not modified.",
            "All 322 usable-target rows remain in adsorption_dataset_v2.csv.",
            "Iftikhar attribution is stored as a corrected secondary-source field; the legacy label is retained.",
            "Unresolved rows retain blank primary-study IDs and explicit exclusion reasons.",
            "Non-Iftikhar rows remain in the canonical dataset but are not silently treated as reconstructed primary studies.",
            "Domain subsets are row-level eligibility flags, not destructive filters.",
            "No Q_MAX=624 target or prediction truncation is applied.",
        ],
    }
    (OUT / "adsorption_dataset_v2_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # Compatibility with earlier provenance audit artifact name.
    (OUT / "canonical_provenance_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    dictionary = build_data_dictionary()
    dictionary.to_csv(OUT / "adsorption_dataset_v2_data_dictionary.csv", index=False, encoding="utf-8-sig")

    print("=== ADSORPTION DATASET V2 SUMMARY ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nDataset written to: {out_csv}")
    print(f"Columns: {len(canonical.columns)}")
    print("\nEligibility counts:")
    for key in [
        "usable_target_rows_v2", "confirmed_primary_rows", "strict_agricultural_rows",
        "broad_biogenic_rows", "waste_derived_carbon_rows",
    ]:
        print(f"  {key}: {counts[key]}")


if __name__ == "__main__":
    main()
