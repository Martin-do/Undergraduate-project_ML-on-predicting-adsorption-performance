# ID-SEAD Conference Salvage — Reproducibility Status

Status: **PASS / FROZEN FOR CONFERENCE RECONSTRUCTION**

Date: 2026-08-30

## What this checkpoint establishes

The corrected V2.1 evidence used for the ID-SEAD conference salvage is now independently rerunnable in GitHub Actions under a pinned historical software environment. The regenerated dataset counts, matched row-random versus primary-study-grouped validation metrics, and strict leave-one-primary-study-out (LOSO) metrics match the frozen successful V2.1 evidence within the declared numerical tolerance.

This checkpoint **does not** reinstate the legacy manuscript's R2=0.847, Q_MAX=624 mg/g, Table-III inverse-design recommendations, or deployment-readiness claims. Those legacy claims remain governed by `NUMERICAL_LINEAGE_AUDIT.md` and `CLAIM_RECONCILIATION_MATRIX.md`.

## Successful conference-salvage reproducibility run

- Workflow: `ID-SEAD conference salvage reproducibility`
- Run ID: `33329803087`
- Job ID: `99306223058`
- Branch: `conference/id-sead-salvage`
- Head SHA: `c5a421deea589ba325893795d1fa8683d61a6c49`
- Conclusion: **success**
- Reproducibility-contract tests: **8/8 passed**
- Runner assertion: **Historical V2.1 baseline match: PASS**

### Generated evidence artifact

- Artifact name: `id-sead-conference-salvage-reproducibility`
- Artifact ID: `9737327504`
- Size: `479269` bytes
- SHA-256: `116e4b86f685130e961043c16468e936c1d8d3b706dfa36d8fda3eb1ff73e2ed`
- Retention expiry: 2026-11-28
- Files uploaded: 25

## Pinned execution environment

- Python `3.11.15`
- NumPy `2.4.6`
- pandas `3.0.5`
- SciPy `1.17.1`
- scikit-learn `1.9.0`
- XGBoost `3.2.0`
- openpyxl `3.1.5`

The complete resolved environment is recorded in the generated `environment_freeze.txt`; `run_manifest.json` records package versions, Git SHA, configuration, source hashes and output hashes.

## Frozen scientific scope

Dataset V2.1 rebuild:

- usable-target rows: `322`
- primary-confirmed rows: `307`
- primary-confirmed studies: `29`
- unresolved rows: `15`
- strict-comparable population: `273` rows from `24` primary studies

Primary grouping variable: `primary_study_id_v21`.

The validation contract enforces:

1. study-aware grouping for the primary generalisation analysis;
2. zero primary-study overlap between training and held-out folds;
3. fold-local preprocessing/model selection;
4. `removal_percent` excluded as a predictor;
5. source/study identifiers excluded as predictors;
6. legacy `Q_MAX=624 mg/g` disabled;
7. external targets not used for tuning;
8. row-random performance labelled diagnostic only.

## Frozen strict-scope results

### Diagnostic row-random 5-fold CV — 273 rows

| Model | R2 | RMSE (mg/g) | MAE (mg/g) |
|---|---:|---:|---:|
| RF | 0.9042022321 | 217.6977289 | 108.2563240 |
| XGB | 0.8935888731 | 229.4403119 | 128.2633750 |
| Unconstrained Ridge stack | 0.9027450236 | 219.3472125 | 118.1081576 |

These values are retained **only as a conventional-validation comparator**.

### Primary-study-grouped 5-fold CV — same 273 rows / 24 studies

| Model | R2 | RMSE (mg/g) | MAE (mg/g) |
|---|---:|---:|---:|
| RF | 0.0265340789 | 693.9634213 | 473.4465479 |
| XGB | 0.1928783061 | 631.8961561 | 443.4072659 |
| Unconstrained Ridge stack | -0.5565653795 | 877.5257853 | 737.6312331 |

### Strict leave-one-primary-study-out robustness

| Model | R2 | RMSE (mg/g) | MAE (mg/g) | Median AE (mg/g) |
|---|---:|---:|---:|---:|
| RF | 0.0084726175 | 700.3716520 | 476.2408442 | 215.8659843 |
| XGB | 0.1623548902 | 643.7336801 | 447.4621469 | 257.2422424 |

## Historical evidence lineage reproduced

### Final matched V2.1 validation

- Historical run ID: `32003217034`
- Historical job ID: `95307465955`
- Historical commit SHA: `f815a168f2c9689ae6582da6fe47f333c30a5f2e`
- Historical artifact ID: `9279131675`
- Historical artifact name: `final-validation-v21-results`
- Historical artifact ZIP SHA-256: `58e6f6c5d3cab01f7b0cfb346a79feda90e8b0c6e558b0f9cef1d9adbd8f6245`

### V2.1 robustness / LOSO

- Historical run ID: `32003678479`
- Historical job ID: `95308786043`
- Historical commit SHA: `88b0217a1bda99a87e23d3057aa86dab732e40d6`
- Historical artifact ID: `9279289740`
- Historical artifact name: `robustness-validation-v21-results`
- Historical artifact ZIP SHA-256: `1b7facc585f0a6b8771545e7e2af1d397a1e0c1f128618918f672a27a35f106e`

## Submission interpretation

The computationally reproducible result is **not** that ID-SEAD is presently validated for engineering inverse design. The reproducible result is that the same literature-derived dataset can produce apparently strong performance under row-random validation while performance collapses when complete primary studies are withheld.

Therefore the conference manuscript may defensibly use ID-SEAD as the engineering case study through which this validation failure and its inverse-design consequences are demonstrated.

The following remain disabled for the conference submission unless new prospective evidence is generated:

- validated inverse-design recommendations;
- universal physical feasibility based on `Q_MAX=624 mg/g`;
- procurement / commissioning / deployment readiness;
- the legacy manuscript's R2=0.847 and associated CI/RMSE claims;
- the original Table III recommendations and robustness claim.

## Reproducibility package

The executable submission-facing layer is under:

`conference_salvage/reproducibility/`

Primary entry point:

`python conference_salvage/reproducibility/run_corrected_validation.py`

Tests:

`python -m unittest discover conference_salvage/reproducibility/tests -v`

Any later change to dataset lineage, validation code, package versions, grouping logic, or permitted scientific claims must cause this status to be re-opened and the reproducibility workflow rerun before manuscript numbers are updated.
