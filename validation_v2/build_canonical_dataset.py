"""Build a derived provenance-aware adsorption dataset without altering the original CSV.

Key rules
---------
* The original `final_final_adsorption_done_dataset.csv` is read-only.
* Rows currently labelled `Moosavi et al., 2023` are attributed to the
  Iftikhar et al. 2023 secondary compilation in a NEW field; the legacy label is
  retained for forensic traceability.
* Primary-study IDs are attached only when `primary_study_map.csv` marks the
  material/system mapping as confirmed. Unresolved rows remain unresolved.
* No unresolved row is assigned a guessed primary-study ID.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "final_final_adsorption_done_dataset.csv"
MAP = Path(__file__).resolve().parent / "primary_study_map.csv"
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


def norm(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip()).lower()


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


def main():
    df = pd.read_csv(DATA, encoding="utf-8-sig")
    mapping = pd.read_csv(MAP, encoding="utf-8-sig", keep_default_na=False)

    if "source_link" not in df or "adsorbent" not in df:
        raise ValueError("Expected source_link and adsorbent in original dataset")

    legacy_dom = df["source_link"].map(norm).str.contains(DOMINANT_LEGACY_TOKEN, na=False)

    # Preserve legacy evidence first.
    canonical = df.copy()
    canonical.insert(0, "canonical_row_id", range(1, len(canonical) + 1))
    canonical["legacy_source_link"] = canonical["source_link"]
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
    canonical.loc[legacy_dom, "source_label_correction_status"] = "legacy_label_misattributed_corrected_in_derived_dataset"

    # Primary provenance starts unresolved. Only confirmed mappings are applied.
    for col in [
        "primary_study_id", "primary_study_citation", "primary_study_doi",
        "primary_provenance_confidence", "primary_provenance_status", "primary_provenance_evidence",
    ]:
        canonical[col] = ""
    canonical.loc[legacy_dom, "primary_provenance_status"] = "unresolved"

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

    canonical["pollutant_class_v1"] = canonical["pollutant"].map(pollutant_class)
    canonical["candidate_dye_domain_v1"] = canonical["pollutant_class_v1"].eq("dye")
    canonical["domain_lock_status"] = "provisional_not_locked"

    out_csv = OUT / "canonical_adsorption_dataset.csv"
    canonical.to_csv(out_csv, index=False)

    dom = canonical.loc[legacy_dom]
    confirmed_rows = dom["primary_study_id"].ne("").sum()
    unresolved_rows = dom["primary_study_id"].eq("").sum()
    confirmed_systems = dom.loc[dom["primary_study_id"].ne(""), "primary_study_id"].nunique()
    unresolved_adsorbents = sorted(dom.loc[dom["primary_study_id"].eq(""), "adsorbent"].astype(str).unique())

    summary = {
        "total_rows": int(len(canonical)),
        "iftikhar_derived_rows": int(legacy_dom.sum()),
        "iftikhar_derived_percent": float(100 * legacy_dom.mean()),
        "primary_confirmed_rows_within_iftikhar_block": int(confirmed_rows),
        "primary_confirmed_percent_within_iftikhar_block": float(100 * confirmed_rows / max(int(legacy_dom.sum()), 1)),
        "primary_unresolved_rows_within_iftikhar_block": int(unresolved_rows),
        "confirmed_primary_studies": int(confirmed_systems),
        "unresolved_adsorbents": unresolved_adsorbents,
        "candidate_dye_rows_all_sources": int(canonical["candidate_dye_domain_v1"].sum()),
        "guardrails": [
            "The original CSV is not modified.",
            "Iftikhar attribution is stored as a secondary-source correction in the derived dataset.",
            "Unresolved rows retain blank primary-study IDs.",
            "candidate_dye_domain_v1 is a classification aid only; the final modelling domain is not locked.",
        ],
    }
    (OUT / "canonical_provenance_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=== CANONICAL PROVENANCE SUMMARY ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Canonical dataset written to {out_csv}")


if __name__ == "__main__":
    main()
