# Liu dye 2025 ↔ Liu ammonia-N 2025 primary-source independence audit

Status: **PRIMARY-STUDY SETS DISJOINT; CURATION-TEAM LINEAGE SHARED**

## Purpose

Paper 1 contains matched reanalyses of two literature-derived datasets associated with the same broader author/repository lineage:

1. biochar adsorption of dyes — DOI `10.1007/s44246-025-00213-9`
2. ammonia-N adsorption on biochar — DOI `10.1038/s41545-024-00429-z`

They must not be described as fully independent replications without distinguishing independence of the underlying primary-study data from independence of the dataset-curation research team.

## Dye-corpus source set

The reconstructed dye workbook contains 20 listed source DOIs; 19 contribute rows to the extended logical population and 17 contribute rows to the strict high-confidence population. The source DOI list is recorded deterministically in `liu2025_primary_study_provenance.py`.

## Ammonia-corpus contributing source set

The final 409-row ammonia matched population contains seven contributing primary-study DOIs:

- `10.1016/j.biortech.2019.121927`
- `10.1007/s11802-020-4150-9`
- `10.1007/s11356-022-19870-z`
- `10.1371/journal.pone.0113888`
- `10.1016/j.scitotenv.2019.135544`
- `10.1016/j.jclepro.2021.129994`
- `10.1016/j.jclepro.2018.10.268`

## Overlap result

**Primary-study DOI intersection = 0.**

None of the seven model-contributing ammonia-N primary studies appears in the dye corpus source ledger. None appears in the 29-study V2.1 bibliography either.

Therefore the two Liu corpora are independent with respect to the **underlying primary literature observations** used for the matched study-aware analyses.

## Dependence that remains

Both datasets are associated with the same broader curation/model-development team and public GitHub account. Their repository code also exhibits similar methodological patterns, including random row-level splitting and preprocessing performed globally before the split in the published executable pipelines.

Consequently, Paper 1 should use precise wording:

- acceptable: **two disjoint primary-study corpora from the same broader dataset-curation lineage**;
- acceptable: **two primary-source-independent matched reanalyses**;
- avoid: **two completely independent research-team replications**.

Cross-team corroboration is supplied separately by Aguiar & Kasemodel 2026, which independently reports conventional-versus-GroupKFold differences in a clay/methylene-blue literature corpus.

## Independence hierarchy used in Paper 1

The manuscript should distinguish at least three levels:

1. **row independence** — individual experimental observations;
2. **primary-study independence** — distinct source publications/experimental campaigns;
3. **curation/research-team independence** — distinct groups assembling and modelling the literature corpus.

The primary matched analyses are concerned principally with level 2. Evidence synthesis should nevertheless disclose level 3 wherever multiple datasets come from the same research group.
