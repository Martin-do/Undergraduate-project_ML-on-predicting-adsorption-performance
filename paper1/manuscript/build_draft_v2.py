"""Build Paper 1 Manuscript Draft V2 from the numerically reconciled Draft V1.

Draft V2 is an editorial/scientific-precision revision only. It does not change the
frozen evidence base or recompute model results. Replacements are asserted so that
an upstream wording change cannot silently bypass a required correction.

Run from repository root:
    python paper1/manuscript/build_draft_v2.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = HERE / "PAPER1_MANUSCRIPT_DRAFT_V1.md"
DST = HERE / "PAPER1_MANUSCRIPT_DRAFT_V2.md"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one occurrence of {old!r}; found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = SRC.read_text(encoding="utf-8")

    # 1. Tighten independence language in the abstract. The two Liu corpora have
    # disjoint contributing primary-study DOI sets, but share a broader curation/team lineage.
    text = replace_once(
        text,
        "In an independently sourced biochar–dye corpus (624 observations, 17 studies), CatBoost decreased from R² = 0.9360 to 0.1096 (LOSO R² = 0.0594). In a second independent primary-study corpus of ammonia-N adsorption on biochar (409 observations, 7 studies), CatBoost decreased from R² = 0.8837 to −0.0581 (LOSO R² = −0.0547).",
        "In a primary-study-disjoint biochar–dye corpus (624 observations, 17 studies), CatBoost decreased from R² = 0.9360 to 0.1096 (LOSO R² = 0.0594). In a second primary-study-disjoint corpus of ammonia-N adsorption on biochar (409 observations, 7 studies), CatBoost decreased from R² = 0.8837 to −0.0581 (LOSO R² = −0.0547). The two Liu corpora had non-overlapping contributing primary-study DOI sets but shared a broader data-curation/author-team lineage.",
    )

    # 2. Make the evidence-flow figure explicit before Results.
    text = replace_once(
        text,
        "After the evidence freeze, additional datasets are not added to the primary analysis merely because they might strengthen the observed direction. Any post-freeze addition requires a documented methodological reason before its grouped result is inspected.\n\n---\n\n## 3. Results",
        "After the evidence freeze, additional datasets are not added to the primary analysis merely because they might strengthen the observed direction. Any post-freeze addition requires a documented methodological reason before its grouped result is inspected. Figure 1 summarizes the resulting provenance and evidence hierarchy used for interpretation.\n\n---\n\n## 3. Results",
    )

    # 3. Add explicit figure/table callouts at the main quantitative result.
    text = replace_once(
        text,
        "### 3.3 Matched study-aware validation materially reduced performance in all three primary reanalyses\n\nTable 3 summarizes representative fixed-model results.",
        "### 3.3 Matched study-aware validation materially reduced performance in all three primary reanalyses\n\nTable 3 and Figure 2 summarize the representative fixed-model comparisons.",
    )

    text = replace_once(
        text,
        "### 3.4 Study-aware performance was heterogeneous rather than uniformly absent\n\nDataset A retained weak positive unseen-study signal",
        "### 3.4 Study-aware performance was heterogeneous rather than uniformly absent\n\nFigures 3 and 4 place the representative validation gaps and LOSO results alongside corpus structure. Dataset A retained weak positive unseen-study signal",
    )

    # 4. Tie the Discussion estimand distinction to the conceptual schematic.
    text = replace_once(
        text,
        "### 4.1 Row-random interpolation and unseen-study transfer are different estimands\n\nThe main finding is not that random cross-validation is intrinsically invalid.",
        "### 4.1 Row-random interpolation and unseen-study transfer are different estimands\n\nFigure 5 summarizes the claim–validation distinction. The main finding is not that random cross-validation is intrinsically invalid.",
    )

    # 5. Correct verified bibliography details.
    text = replace_once(
        text,
        "Liu, C., Balasubramanian, P., An, J., et al. (2025). Machine learning prediction of ammonia nitrogen adsorption on biochar with model evaluation and optimization.",
        "Liu, C., Balasubramanian, P., An, J., & Li, F. (2025). Machine learning prediction of ammonia nitrogen adsorption on biochar with model evaluation and optimization.",
    )

    text = replace_once(
        text,
        "Moosavi, S., et al. (2021). A Study on Machine Learning Methods’ Application for Dye Adsorption Prediction onto Agricultural Waste Activated Carbon.",
        "Moosavi, S., Manta, O., El-Badry, Y. A., Hussein, E. E., El-Bahy, Z. M., Mohd Fawzi, N. F. B., Urbonavičius, J., & Moosavi, S. M. H. (2021). A Study on Machine Learning Methods’ Application for Dye Adsorption Prediction onto Agricultural Waste Activated Carbon.",
    )

    # 6. Mark version and caption source without altering scientific claims.
    text = replace_once(
        text,
        "**Manuscript status:** Draft V1 — reconstructed from the frozen Paper 1 evidence base",
        "**Manuscript status:** Draft V2 — scientific/editorial refinement of the numerically reconciled frozen-evidence draft",
    )
    text = replace_once(
        text,
        "## References — verified core set for Draft V1",
        "## References — verified core set for Draft V2",
    )
    text = replace_once(
        text,
        "Draft V1 intentionally does not invent incomplete bibliographic metadata.",
        "Draft V2 intentionally does not invent incomplete bibliographic metadata.",
    )

    caption_note = (
        "\n\n> **Figure-caption source:** Final Draft V2 figure captions are maintained in "
        "`paper1/manuscript/FIGURE_CAPTIONS_V1.md` and correspond to deterministic CI-rendered figures.\n"
    )
    marker = "\n## Data and code availability\n"
    if marker not in text:
        raise RuntimeError("Could not find Data and code availability marker")
    text = text.replace(marker, caption_note + marker, 1)

    DST.write_text(text, encoding="utf-8")
    print(f"Wrote {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
