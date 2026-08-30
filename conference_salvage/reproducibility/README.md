# ID-SEAD Conference Salvage Reproducibility Package

This directory is the submission-facing execution layer for the corrected ID-SEAD conference evidence.

It deliberately **does not** reproduce or reinstate the legacy manuscript's R2=0.847, Q_MAX=624, or deployment-ready inverse-design claims. It executes the corrected V2.1 provenance-controlled validation under the exact historical software environment and requires the regenerated evidence to match the frozen successful V2.1 runs.

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

## Frozen historical lineage

The reproducibility baseline is tied to two successful GitHub Actions runs from 17 August 2026:

- matched V2.1 validation: run `32003217034`, commit `f815a168f2c9689ae6582da6fe47f333c30a5f2e`, artifact `9279131675`, ZIP SHA-256 `58e6f6c5d3cab01f7b0cfb346a79feda90e8b0c6e558b0f9cef1d9adbd8f6245`;
- V2.1 robustness/LOSO: run `32003678479`, commit `88b0217a1bda99a87e23d3057aa86dab732e40d6`, artifact `9279289740`, ZIP SHA-256 `1b7facc585f0a6b8771545e7e2af1d397a1e0c1f128618918f672a27a35f106e`.

The historical runtime was CPython 3.11.15 with NumPy 2.4.6, pandas 3.0.5, SciPy 1.17.1, scikit-learn 1.9.0 and XGBoost 3.2.0. Robustness/external validation additionally requires openpyxl 3.1.5 for the two repository-frozen Excel workbooks. These versions are now explicitly pinned rather than depending on `pip install` resolving whatever versions are current.

`baseline_expectations.json` contains the exact expected strict-scope matched and LOSO metrics. A run fails if Python/package versions, scope counts, or numerical results do not match that baseline within the declared tolerance.

## One-command local run

Use Python 3.11.15, then from the repository root:

```bash
python -m pip install -r conference_salvage/reproducibility/requirements.txt
python conference_salvage/reproducibility/run_corrected_validation.py
python -m unittest discover conference_salvage/reproducibility/tests -v
```

GitHub Actions performs the same run automatically with Python 3.11.15.

The runner rebuilds Dataset V2.1 from the frozen source maps, executes matched row-random versus primary-study-grouped validation, executes LOSO and external robustness checks, validates the anti-leakage contract, verifies the historical numerical baseline, hashes the code/data inputs including the external Excel workbooks, and writes evidence under:

`conference_salvage/reproducibility/outputs/`

## Key outputs

- `conference_metrics_snapshot.json` — compact values permitted for conference drafting.
- `final_validation_v21_metrics.csv` — matched row-random versus primary-study-grouped metrics.
- `final_validation_v21_folds.csv` — fold audit including primary-study overlap counts.
- `robustness_v21_loso_pooled.csv` — pooled LOSO metrics.
- `robustness_v21_loso_per_study.csv` — held-out-study errors.
- `final_validation_v21_predictions.csv` and `robustness_v21_loso_predictions.csv` — row-level predictions.
- `contract_checks.json` — anti-leakage assertions.
- `baseline_verification.json` — exact historical environment/scope/numerical reproduction checks.
- `environment_freeze.txt` — installed environment from the successful rerun.
- `run_manifest.json` — Git SHA, source/input SHA-256 hashes, output SHA-256 hashes, package versions, configuration and historical run lineage.

## Interpretation rule

A high row-random metric must never be presented as evidence of transfer to an unseen study. The conference manuscript must distinguish conventional row-random performance from corrected study-aware performance.

A successful reproducibility rerun demonstrates that the **corrected V2.1 evidence is computationally reproducible**. It does not rehabilitate the invalidated legacy ID-SEAD numerical/deployment claims. The current failure of reliable unseen-study transfer means a validated inverse-design claim remains disabled. A future rebuilt ID-SEAD may retest that proposition using a purpose-built dataset and prospective reliability gate.
