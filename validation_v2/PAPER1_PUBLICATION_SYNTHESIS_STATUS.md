# Paper 1 Publication Synthesis Status

Status: **MULTI-DATASET SCIENTIFIC EVIDENCE LOCKED — MANUSCRIPT RECONSTRUCTION IN PROGRESS**

Date: 2026-08-28

Branch: `paper1/multidataset-study-aware-replication`

## Completed scientific gates

- V2.1 provenance and study-aware audit locked.
- Multi-dataset validation protocol frozen before external grouped outcomes.
- Three independent matched primary corpora completed.
- Common RF/XGB matched synthesis completed across all three corpora.
- Moosavi 2021 reclassified correctly as lineage-overlapping sensitivity, not independent replication.
- Aguiar & Kasemodel 2026 retained as published independent corroboration.
- Huang et al. 2026 retained as published positive source-aware counterexample.
- Primary dataset hunting closed unless a specific reviewer-level gap later requires reopening it.

## Numerical authority

`MULTIDATASET_NUMERIC_SOURCE_OF_TRUTH.md`

Deterministic synthesis:
- run `33212475321`
- conclusion `success`
- artifact `9702119314`
- artifact SHA-256 `148532e250de75cff9dde98d84b6501d3eb459ef9447c691bb929abf78d59f4a`

Primary common-model result:
- 3 independent matched corpora
- 6 RF/XGB comparisons
- random R² > study-aware R² in 6/6
- ΔR² range `0.7007` to `1.492205`
- descriptive median ΔR² `1.1162235`
- no formal meta-analysis claim

## Revised manuscript scope

`PAPER1_MULTIDATASET_REVISED_SCOPE.md`

Central question:

> How sensitive are apparent machine-learning generalisation results in literature-derived adsorption datasets to the unit at which observations are split, and under what corpus structures can strong source-held-out performance persist?

Working title:

**Random-Split Optimism and Study-Aware Generalisation in Literature-Derived Adsorption Machine Learning: A Multi-Dataset Reproducibility Study**

## Publication figure package

Rendering-only script:
`paper1_manuscript_figures.py`

Final verified run:
- run `33213007662`
- conclusion `success`
- artifact `9702313627`
- artifact SHA-256 `6f275a428d94f0feb596ecac8b7fe7d054a3f7a200ae63c21c7e25ba89cdc7f7`
- figure-render commit `d0c3c7745bfcff92de8f8f865190782112c076a5`

Figures:
1. `Figure_1_matched_random_vs_study_aware` — common RF/XGB matched comparison.
2. `Figure_2_delta_r2` — dataset/model-specific validation gap.
3. `Figure_3_evidence_context` — independent reruns, lineage sensitivity, published corroboration and positive counterexample clearly separated.

All three figures were visually inspected after the successful run. No numerical values are generated or changed by the manuscript-figure script.

## Working manuscript

A new multi-dataset working DOCX was generated from the locked scope and evidence:

`Paper1_MultiDataset_StudyAware_WORKING_DRAFT_v1.docx`

The document was rendered to nine pages using the controlled DOCX QA pipeline and every page was visually inspected. No clipping, broken tables, figure overlap or page-layout defects were observed.

The previous V2.1-only working DOCX is superseded conceptually by this multi-dataset reconstruction.

## Manuscript claims currently permitted

- random and study-aware validation estimate different generalisation tasks;
- across the three independently reconstructed primary corpora, RF and XGB show materially higher row-random than primary-study-aware performance;
- the gap is dataset dependent rather than universal;
- strong source-aware performance can persist in a suitable corpus;
- preserved primary-study provenance is necessary for reproducible claim-aligned validation;
- strong random-split R² alone is insufficient evidence of transfer to unseen primary studies.

## Claims prohibited

- random splitting is always invalid;
- study-aware validation always reduces performance;
- all adsorption ML is non-generalizable;
- this project is the first adsorption study to use or recommend GroupKFold;
- the descriptive median ΔR² is a formal pooled effect size;
- Moosavi is an independent replication;
- Aguiar or Huang were independently rerun in this repository;
- old ID-SEAD stack superiority, inverse-design validation, QMAX=624 mg/g or deployment claims are restored.

## Remaining before Paper 1 can be called submission-ready

1. Confirm final authorship, affiliations and corresponding author.
2. Select the target journal and align scope/title/article structure to that journal.
3. Complete publisher/DOI-level verification and formatting of the full reference set, including provenance and literature-audit sources.
4. Prepare supplementary provenance tables, group-size distributions and per-study LOSO diagnostics.
5. Decide main-text versus supplement placement for the evidence-context figure.
6. Create a versioned repository release and persistent archive/DOI.
7. Apply journal formatting and perform final manuscript-to-registry numerical reconciliation.
8. Conduct a final submission-readiness audit after all editorial changes.

Paper 2 model-development work remains outside this branch and should start only after the Paper 1 package is frozen for submission.
