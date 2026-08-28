# Paper 1 — Manuscript Reconstruction Status

Status: **DRAFT V2 CREATED, PERSISTED AND FULLY RECONCILED AGAINST FROZEN EVIDENCE**

Date: **2026-08-28**

Branch: `paper1/multidataset-study-aware-replication`

## Scientific authority

1. `validation_v2/PAPER1_MULTIDATASET_EVIDENCE_FREEZE.md`
2. `validation_v2/MULTIDATASET_RESULTS_REGISTRY.csv`
3. `validation_v2/MULTIDATASET_VALIDATION_PROTOCOL.md`
4. Dataset-specific finding files and Dataset V2.1 Phase 8 source-of-truth outputs

No new primary benchmark may be added merely to strengthen the observed direction.

## Current controlled manuscript

`paper1/manuscript/PAPER1_MANUSCRIPT_DRAFT_V2.md`

Draft V2 is an editorial/scientific-precision refinement of the frozen-evidence Draft V1. It does **not** alter the locked modelling results. Key V2 changes include:

- replaced potentially over-broad “independent” language for the two Liu corpora with **primary-study-disjoint** terminology;
- explicitly states that the Liu dye and ammonia-N corpora share a broader data-curation/author-team lineage;
- added manuscript callouts for Figures 1–5;
- corrected the full verified Liu ammonia-N author list;
- corrected the full verified Moosavi author list;
- retains the positive Huang source-aware counterexample and the Aguiar cross-team corroboration;
- retains all retired ID-SEAD claims outside the manuscript contribution.

## Manuscript assets now created

- `paper1/manuscript/PAPER1_MANUSCRIPT_DRAFT_V1.md`
  - archived first full multi-dataset reconstruction
- `paper1/manuscript/PAPER1_MANUSCRIPT_DRAFT_V2.md`
  - **current working manuscript**
- `paper1/manuscript/build_draft_v2.py`
  - deterministic asserted transformation from V1 to V2
- `paper1/manuscript/TABLES_V1.md`
  - corpus/provenance table
  - random-performance reproduction table
  - representative matched comparison
  - full primary matched metrics
  - sensitivity table
  - independent comparator table
  - reporting checklist
- `paper1/manuscript/REFERENCES_VERIFIED.md`
  - authoritative core bibliography and citation-use constraints
- `paper1/manuscript/LITERATURE_PRACTICE_CONTEXT_V1.md`
  - bounded verified examples of observation-level versus source-aware adsorption-ML validation practice
  - explicitly **not** a systematic prevalence estimate
- `paper1/manuscript/FIGURE_CAPTIONS_V1.md`
  - captions for Figures 1–5
- `paper1/manuscript/build_figures.py`
  - deterministic figure generator reading the frozen results registry
- `.github/workflows/paper1-build-manuscript-figures.yml`
  - CI figure rendering and artifact archival
- `paper1/manuscript/reconcile_manuscript_numbers.py`
  - Draft V2 numerical/wording integrity gate
- `.github/workflows/paper1-manuscript-reconciliation.yml`
  - CI manuscript reconciliation
- `.github/workflows/paper1-build-draft-v2.yml`
  - deterministic V2 generation, persistence and artifact archival

## Figures

The deterministic figure CI now produces:

1. **Figure 1 — Evidence and provenance hierarchy**
2. **Figure 2 — Matched random versus study-aware R²**
3. **Figure 3 — Validation-gap magnitude versus primary-study count**
4. **Figure 4 — Pooled study-LOSO R² summary**
5. **Figure 5 — Claim–validation alignment schematic**

Figure 3 is explicitly descriptive; no cross-corpus causal trend is fitted from the small number of matched cases. Figure 4 is labelled as pooled LOSO and is not presented as a replacement for per-study errors.

## Draft V2 reconciliation status

The current Draft V2 gate checks:

- all representative V2.1, Liu dye, Liu ammonia-N and Moosavi headline R² values;
- corresponding ΔR² and LOSO values;
- core row/study population counts;
- Moosavi lineage non-independence disclosure;
- Liu shared broader curation lineage disclosure;
- **primary-study-disjoint** wording;
- verified full Liu ammonia-N and Moosavi author strings;
- Figure 1–5 manuscript callouts;
- absence of retired legacy claims.

**Current CI result: PASS.**

## Working title

**Validation-Unit Sensitivity in Literature-Derived Adsorption Machine Learning: A Multi-Dataset Study-Aware Reanalysis**

## Manuscript-level central conclusion

The paper does not claim that random splitting is universally invalid or that adsorption ML cannot generalise. It shows that performance estimates can change materially when the validation unit is changed from individual observations to primary studies, and that the appropriate design depends on the scientific generalisation claim.

## Independence language locked for Draft V2

- Dataset A: primary deep case.
- Liu dye: **primary-study-disjoint** matched corpus relative to the other primary cases.
- Liu ammonia-N: **primary-study-disjoint** relative to Dataset A and Liu dye, but shares broader dataset-curation/author-team lineage with Liu dye.
- Moosavi: lineage-overlapping sensitivity only; **not** independent replication.
- Aguiar 2026: independent cross-team published corroboration; not a project rerun.
- Huang 2026: positive source-aware published comparator; not independently rerun.

## Claims prohibited

- ~0.90 unseen-study generalisation for Dataset A.
- stacked-ensemble superiority.
- validated inverse design or engineering deployment.
- universal QMAX = 624 mg/g.
- agricultural-waste-only description of the heterogeneous full historical corpus.
- claim that all row-random validation is wrong.
- claim that all adsorption ML fails under study-aware validation.
- claim that grouped validation itself is novel.

## Remaining gates before a submission-format DOCX

1. Complete verification of the Dataset A primary-study bibliography, including non-DOI legacy sources.
2. Integrate the bounded verified literature-practice context into the Introduction with formal references.
3. Decide whether final Figure 4 should remain a pooled LOSO summary or be replaced/supplemented with per-study LOSO error distributions from existing outputs.
4. Perform one scientific/editorial pass for repetition, terminology and precision consistency.
5. Decide authorship, affiliations, acknowledgements and funding statements.
6. Select a target journal based on the stabilized methodological emphasis and manuscript length.
7. Freeze a submission candidate after supervisor/internal review.
8. Convert the stable manuscript to the selected journal's DOCX/template format.
9. Archive code/data/results in a persistent release/DOI before submission.

## Immediate next action

**Finish bibliography/literature-context verification, then move to target-journal selection and submission-candidate polishing.**
