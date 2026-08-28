"""Build Paper 1 Manuscript Draft V3 from the controlled Draft V2.

Draft V3 integrates the verified bounded literature-practice context and complete
Dataset-A bibliography-verification status. It does not change frozen model results.

Run from repository root:
    python paper1/manuscript/build_draft_v3.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = HERE / "PAPER1_MANUSCRIPT_DRAFT_V2.md"
DST = HERE / "PAPER1_MANUSCRIPT_DRAFT_V3.md"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one occurrence of {old!r}; found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = SRC.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "**Manuscript status:** Draft V2 — scientific/editorial refinement of the numerically reconciled frozen-evidence draft",
        "**Manuscript status:** Draft V3 — controlled literature-context and bibliography-verification refinement of the frozen-evidence manuscript",
    )

    anchor = (
        "Machine learning (ML) has become increasingly common in adsorption research because it can represent nonlinear relationships among adsorbent properties, pollutant characteristics and operating conditions without requiring a single mechanistic equation to describe every interaction. Literature-derived datasets are particularly attractive: a single modelling table can contain hundreds or thousands of adsorption observations assembled from multiple publications, substantially increasing the apparent sample size available for model development. Recent adsorption studies have reported strong predictive performance using tree ensembles, boosting methods, neural networks and related algorithms, often with coefficient-of-determination values above 0.90."
    )
    replacement = anchor + (
        "\n\nRecent literature-derived adsorption-ML studies also illustrate that validation practice is heterogeneous rather than uniform. For example, Yadav et al. (2025) used an 80:20 observation-level train/test split with ten-fold cross-validation for a literature-derived Congo-red/biochar dataset, while Liu et al. (2025) used observation-level random evaluation in the dye and ammonia-N corpora reanalysed here. Abu-Shareha et al. (2026) explicitly randomized 1,150 pooled Cd(II)/biochar observations into 90% training and 10% validation irrespective of literature source, with random five-fold cross-validation. By contrast, Aguiar and Kasemodel (2026) evaluated GroupKFold by source study, and Huang et al. (2026) separated their train/test data at the source-publication level. These examples are used only to establish that multiple validation estimands remain in active use; they are not a systematic prevalence survey and do not support a claim that one design is used by most adsorption-ML papers."
    )
    text = replace_once(text, anchor, replacement)

    provenance_anchor = (
        "Cross-corpus source overlap was audited to avoid double counting. This procedure led to reclassification of the Moosavi dataset from an apparent independent replication to a lineage sensitivity. It also established that the two Liu-derived matched corpora contain disjoint contributing primary-study DOI sets despite their shared broader research-team lineage."
    )
    provenance_replacement = provenance_anchor + (
        " The 29 reconstructed primary-study records underlying Dataset A were subsequently reviewed against publisher, journal, DOI-indexed, institutional, or primary-document sources. Bibliographic corrections were recorded in a separate citation ledger without altering historical study IDs or row-to-study assignments; this separation preserves the validation grouping while allowing reference metadata to be corrected transparently."
    )
    text = replace_once(text, provenance_anchor, provenance_replacement)

    ref_anchor = "## References — verified core set for Draft V2"
    text = replace_once(text, ref_anchor, "## References — verified core set for Draft V3")

    yadav_ref = (
        "Yadav, S., Rajput, P., Balasubramanian, P., Liu, C., Li, F., & Zhang, P. (2025). Machine learning-driven prediction of biochar adsorption capacity for effective removal of Congo red dye. *Carbon Research, 4*, 11. https://doi.org/10.1007/s44246-024-00168-3\n\n"
    )
    abu_ref = (
        "Abu-Shareha, A. A., Alfilh, R., Yaseen, A. M., Sudhamsu, G., Sahu, P. K., Roselin Jenifer, D., Sharma, S., Jain, V., & Hekmatyar, Z. (2026). Robust Data driven modeling of Cd(II) adsorption on biochar. *Journal of Hazardous Materials Advances, 21*, 101004. https://doi.org/10.1016/j.hazadv.2026.101004\n\n"
    )
    refs_marker = "Aguiar, L. G., & Kasemodel, M. C. (2026)."
    if refs_marker not in text:
        raise RuntimeError("Reference insertion marker not found")
    text = text.replace(refs_marker, abu_ref + yadav_ref + refs_marker, 1)

    text = replace_once(
        text,
        "Draft V2 intentionally does not invent incomplete bibliographic metadata.",
        "Draft V3 intentionally does not invent incomplete bibliographic metadata. Dataset A's 29 reconstructed primary-study citation records are maintained in a separately verified correction ledger so bibliographic cleanup cannot silently change validation groups.",
    )

    DST.write_text(text, encoding="utf-8")
    print(f"Wrote {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
