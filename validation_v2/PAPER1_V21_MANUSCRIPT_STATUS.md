# Paper 1 — V2.1 manuscript reconstruction

Status: **EDITORIAL RECONSTRUCTION STARTED**

Branch: `paper1/v21-manuscript-reconstruction`

Scientific evidence baseline: `feature/study-aware-validation-v2` at commit `5f88c6a2d70326d70633188c2c62485554460ddc`.

The scientific-audit branch is treated as frozen. Manuscript work must not alter the V2.1 dataset, validation scripts, locked metrics, CI artifacts, or provenance decisions.

## Working title

**Study-Aware Validation and Domain Shift in Literature-Derived Machine Learning for Adsorption Capacity Prediction**

## Numerical source of truth

Use only:

1. `validation_v2/V21_NUMERIC_SOURCE_OF_TRUTH.md`
2. `validation_v2/adsorption_dataset_v2_1_summary.json`
3. `validation_v2/final_validation_v21_metrics.csv`
4. `validation_v2/robustness_v21_loso_pooled.csv`
5. `validation_v2/PHASE8_V21_PROVENANCE_AND_FINAL_VALIDATION.md`
6. CI artifacts recorded in Phase 8.

Legacy IEEM/V1/V2 numerical claims may appear only when explicitly labelled as historical or audit comparators.

## Paper 1 central claim

The paper does **not** claim that the current models are high-performing universal predictors. It tests whether conventional row-random validation overstates transferable performance in a literature-derived adsorption dataset.

On the same strict comparable 273 rows / 24 reconstructed primary studies:

- RF: random R² = 0.9042; primary-study GroupKFold R² = 0.0265.
- XGB: random R² = 0.8936; primary-study GroupKFold R² = 0.1929.
- historical Ridge stack: random R² = 0.9027; primary-study GroupKFold R² = -0.5566.
- strict LOSO XGB R² = 0.1624.

The scientific result is the validation/generalisation gap, not stacked-model superiority.

## Claims prohibited in Paper 1

- ~0.90 unseen-study generalisation.
- stacked-ensemble superiority.
- validated ID-SEAD inverse design.
- universal QMAX = 624 mg/g.
- deployment readiness.
- agricultural-waste-only description of the complete corpus.

## Dataset V2.1 disposition

- 325 archived rows.
- 322 usable-target rows.
- 307 primary-provenance-confirmed rows across 29 studies.
- 15 unresolved rows: 13 inherited `CS` + 2 Ajien review-composite rows.
- 273 strict comparable rows across 24 primary studies.
- 264 conventional-aqueous-only rows across 23 studies.
- 257 condition-level-only rows across 14 studies.

## Manuscript structure now being used

1. Introduction
2. Materials and methods
   - V2.1 provenance reconstruction
   - fold-safe preprocessing
   - matched row-random versus study-grouped validation
   - LOSO and pre-specified sensitivities
   - corrected external transfer
   - deterministic evidence pipeline
3. Results
   - source overlap/provenance
   - matched validation gap
   - LOSO/sensitivity robustness
   - external transfer
   - disposition of the historical ID-SEAD claim
4. Discussion
5. Practical recommendations
6. Limitations
7. Conclusions

## Remaining Paper 1 close-out tasks

1. Generate final figures directly from V2.1 machine-readable outputs.
2. Generate the complete 29-study provenance bibliography/supplement from Dataset V2.1.
3. Verify bibliographic metadata/DOIs against primary/public records.
4. Decide authorship/affiliations/acknowledgements for the submission version.
5. Select a journal aligned with environmental/process-engineering ML methodology.
6. Reconcile every manuscript number against V2.1 source-of-truth outputs.
7. Archive the submission dataset/code/result package under a persistent release/DOI.

## Paper 2 boundary

Paper 2 is deliberately not developed on this branch. After Paper 1 is frozen, a separate modelling branch/project should address genuine unseen-study performance through better independent-study coverage, domain definition, target harmonisation and physicochemical descriptor engineering before model optimisation.
