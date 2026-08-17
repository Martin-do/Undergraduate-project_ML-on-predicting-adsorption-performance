# Dataset V2.1 — Numerical Source of Truth

Use the following files for all revised-paper numerical claims after Phase 8:

1. `adsorption_dataset_v2_1.csv` — canonical 322-row provenance-aware dataset.
2. `adsorption_dataset_v2_1_summary.json` — locked population/provenance counts.
3. `final_validation_v21_metrics.csv` — matched row-random vs primary-study GroupKFold results.
4. `robustness_v21_loso_pooled.csv` — strict and conventional-only leave-one-study-out results.
5. `PHASE8_V21_PROVENANCE_AND_FINAL_VALIDATION.md` — scientific interpretation, robustness sensitivities, external-transfer results, and artifact hashes.

## Headline manuscript values

Primary analysis population: **273 rows from 24 reconstructed primary studies**.

- Random 5-fold RF: R² **0.9042**, RMSE **217.70 mg/g**, MAE **108.26 mg/g**.
- Random 5-fold XGB: R² **0.8936**, RMSE **229.44 mg/g**, MAE **128.26 mg/g**.
- Primary-study GroupKFold RF: R² **0.0265**, RMSE **693.96 mg/g**, MAE **473.45 mg/g**.
- Primary-study GroupKFold XGB: R² **0.1929**, RMSE **631.90 mg/g**, MAE **443.41 mg/g**.
- Strict-set LOSO XGB: R² **0.1624**, RMSE **643.73 mg/g**, MAE **447.46 mg/g**.

Sensitivity:
- Conventional-aqueous-only LOSO XGB (264 rows / 23 studies): R² **0.1851**.
- Condition-level-only primary-study GroupKFold XGB (257 rows / 14 studies): R² **0.1377**.

External transfer from strict 273-row training scope:
- Liu 2025 / RF: R² **0.2977**, RMSE **381.87 mg/g**.
- Jaffari 2023 / RF: R² **-1.2503**, RMSE **110.12 mg/g**.

## Prohibited carry-over claims

Do not use the legacy `Q_MAX = 624 mg/g` constraint, do not use `removal_percent` as a predictor, do not claim stacked-ensemble superiority, do not claim ~0.90 unseen-study generalisation, and do not reinstate inverse-design/deployment claims without new validation evidence.
