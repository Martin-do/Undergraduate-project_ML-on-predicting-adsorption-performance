# Paper 1 — Manuscript Reconstruction Status

Status: **FULL DRAFT V1 CREATED; FIGURE/TABLE RECONCILIATION IN PROGRESS**

Date: **2026-08-28**

Branch: `paper1/multidataset-study-aware-replication`

## Scientific authority

1. `validation_v2/PAPER1_MULTIDATASET_EVIDENCE_FREEZE.md`
2. `validation_v2/MULTIDATASET_RESULTS_REGISTRY.csv`
3. `validation_v2/MULTIDATASET_VALIDATION_PROTOCOL.md`
4. Dataset-specific finding files and Dataset V2.1 Phase 8 source-of-truth outputs

No new primary benchmark may be added merely to strengthen the observed direction.

## Manuscript assets now created

- `paper1/manuscript/PAPER1_MANUSCRIPT_DRAFT_V1.md`
  - full Abstract through Conclusions
  - multi-dataset Methods and Results
  - limitations and reporting recommendations
  - core reference list
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
- `paper1/manuscript/build_figures.py`
  - deterministic figure generator reading the frozen results registry
- `.github/workflows/paper1-build-manuscript-figures.yml`
  - CI workflow for figure rendering and artifact archival

## Working title

**Validation-Unit Sensitivity in Literature-Derived Adsorption Machine Learning: A Multi-Dataset Study-Aware Reanalysis**

## Manuscript-level central conclusion

The paper does not claim that random splitting is universally invalid or that adsorption ML cannot generalise. It shows that performance estimates can change materially when the validation unit is changed from individual observations to primary studies, and that the appropriate design depends on the scientific generalisation claim.

## Independence language locked for Draft V1

- Dataset A: primary deep case.
- Liu dye: primary-source-independent matched corpus.
- Liu ammonia-N: disjoint primary-study DOI set from Dataset A and Liu dye, but shared broader dataset-curation/author-team lineage with Liu dye.
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

1. Inspect CI-rendered figures and refine captions/layout.
2. Build a complete manuscript-number reconciliation report against the registry.
3. Verify the complete Dataset A primary-study bibliography and external benchmark metadata.
4. Expand literature-practice context without turning Paper 1 into an unfocused systematic review.
5. Decide authorship, affiliations, acknowledgements and funding statements.
6. Select a target journal after the final methodological emphasis and manuscript length are clear.
7. Freeze Draft V2 after scientific/internal review.
8. Convert the stable manuscript to the selected journal's DOCX/template format.
9. Archive code/data/results in a persistent release/DOI before submission.

## Immediate next action

**Run/inspect the deterministic figures, then perform manuscript ↔ registry numerical reconciliation before stylistic polishing.**
