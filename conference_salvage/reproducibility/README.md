# ID-SEAD Conference Salvage Reproducibility Package

This directory is the submission-facing execution layer for the corrected ID-SEAD conference evidence.

It deliberately **does not** reproduce the legacy manuscript's R2=0.847 / Q_MAX=624 / inverse-design deployment claims. Instead, it executes the corrected V2.1 provenance-controlled validation already maintained under `validation_v2/`, then freezes the evidence needed for the conference case-study framing.

## Scientific contract

- Primary grouping unit: reconstructed `primary_study_id_v21`.
- Primary scientific scope: 273 strict-comparable rows from 24 primary studies.
- Row-random 5-fold CV is a diagnostic comparator only.
- Primary generalisation evidence: 5-fold GroupKFold by primary study plus leave-one-primary-study-out (LOSO) robustness.
- Preprocessing and stack tuning are fitted inside training folds.
- `removal_percent` is not a predictor.
- `source_link` and study identifiers are not predictors.
- The legacy `Q_MAX=624 mg/g` constraint is disabled.
- No inverse-design, procurement, commissioning or deployment claim is enabled by this package.

## One-command run

From the repository root:

```bash
python -m pip install -r conference_salvage/reproducibility/requirements.txt
python conference_salvage/reproducibility/run_corrected_validation.py
python -m unittest discover conference_salvage/reproducibility/tests -v
```

The runner rebuilds Dataset V2.1 from the frozen source maps, executes matched row-random vs study-grouped validation, executes LOSO/external robustness checks, validates the anti-leakage contract, and writes evidence under:

`conference_salvage/reproducibility/outputs/`

## Key outputs

- `conference_metrics_snapshot.json` — compact values permitted for conference drafting.
- `final_validation_v21_metrics.csv` — matched row-random vs primary-study-grouped metrics.
- `final_validation_v21_folds.csv` — fold audit including primary-study overlap counts.
- `robustness_v21_loso_pooled.csv` — pooled LOSO metrics.
- `robustness_v21_loso_per_study.csv` — held-out-study errors.
- `final_validation_v21_predictions.csv` and `robustness_v21_loso_predictions.csv` — row-level predictions.
- `contract_checks.json` — anti-leakage assertions.
- `environment_freeze.txt` — exact installed environment from the run.
- `run_manifest.json` — Git SHA, input/output SHA-256 hashes, package versions and configuration.

## Interpretation rule

A high row-random metric must never be presented as evidence of transfer to an unseen study. The conference manuscript must distinguish the apparent conventional-validation result from the corrected study-aware result.

Likewise, the absence of reliable study-level transfer means the present evidence cannot be converted into a validated inverse-design claim. A future rebuilt ID-SEAD may retest that proposition on a purpose-built dataset, but it is outside this conference salvage package.
