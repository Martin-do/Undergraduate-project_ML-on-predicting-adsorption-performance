# Phase 8 — Dataset V2.1 Provenance and Final Study-Aware Validation

## Status

**SCIENTIFIC GATE: LOCKED FOR MANUSCRIPT REVISION**

This phase extends Dataset V2 provenance to the non-Iftikhar source block, separates provenance recovery from target/data comparability, and reruns the decisive validation using reconstructed primary-study IDs.

The original 325-row source CSV remains unchanged. `validation_v2/adsorption_dataset_v2_1.csv` is the canonical derived dataset for this phase.

## 1. Dataset V2.1 disposition

- Original source rows: **325**
- Usable-target rows retained in V2.1: **322**
- Primary-study-confirmed rows: **307 / 322 (95.34%)**
- Reconstructed primary studies: **29**
- Newly reconstructed non-Iftikhar rows relative to V2: **69**
- Primary-unresolved rows: **15**
  - Iftikhar-inherited `CS`: **13**
  - Ajien review-composite rows: **2**
- Strict comparable modelling set: **273 rows / 24 primary studies**
- Conventional-aqueous-capacity-only sensitivity: **264 rows / 23 primary studies**
- Condition-level-only sensitivity: **257 rows / 14 primary studies**

A recovered citation does **not** automatically make a row modelling-eligible. Thirty-four primary-confirmed rows remain outside the 273-row strict set because of target incompatibility or data-quality flags. Three Sulyman-derived records have processing-field conflicts with their recovered primary sources and remain excluded pending source-level correction.

## 2. Headline matched validation

Within each comparison, the random and primary-study splits use exactly the same observations.

### Strict comparable set — 273 rows / 24 studies

| Model | Random 5-fold R² | Primary-study GroupKFold R² | Group RMSE (mg/g) | Group MAE (mg/g) |
|---|---:|---:|---:|---:|
| LR | 0.5913 | -3.9785 | 1569.38 | 879.25 |
| SVR | -0.2511 | -0.6490 | 903.22 | 714.43 |
| RF | **0.9042** | 0.0265 | 693.96 | 473.45 |
| XGB | 0.8936 | **0.1929** | **631.90** | **443.41** |
| Ridge stack | 0.9027 | -0.5566 | 877.53 | 737.63 |

**Interpretation:** the high row-random score persists, but only weak genuine cross-study transfer remains. XGBoost is the strongest model under primary-study holdout, while the stacked model does not generalise better than the individual trees.

### All primary-confirmed rows — 307 rows / 29 studies

- Random RF R²: **0.9072**
- Grouped RF R²: **0.0862**
- Random XGB R²: **0.8939**
- Grouped XGB R²: **0.0532**
- Random stack R²: **0.9063**
- Grouped stack R²: **-0.0568**

The stricter target/data-quality gate improves XGB grouped performance from 0.053 to 0.193, supporting the use of explicit comparability screening rather than indiscriminate pooling.

## 3. Leave-one-primary-study-out robustness

### Strict comparable — 273 rows / 24 studies

- RF pooled LOSO R²: **0.0085**, RMSE **700.37 mg/g**, MAE **476.24 mg/g**
- XGB pooled LOSO R²: **0.1624**, RMSE **643.73 mg/g**, MAE **447.46 mg/g**
- RF median study MAE: **99.70 mg/g**
- XGB median study MAE: **143.34 mg/g**

Pooled error is disproportionately affected by several large/high-capacity studies. Therefore the manuscript must report per-study/equal-study error summaries alongside pooled R².

## 4. Pre-specified sensitivity checks

### Condition-level records only — 257 rows / 14 studies

Random 5-fold:
- RF R² **0.8841**
- XGB R² **0.8812**
- stack R² **0.8916**

Primary-study GroupKFold:
- RF R² **0.0074**
- XGB R² **0.1377**
- stack R² **-1.1830**

Thus the weak-positive XGB transfer is not created by study-summary/qmax rows.

### Conventional aqueous adsorption capacity only — 264 rows / 23 studies

This sensitivity removes the nine rows pre-classified as `aqueous_operational_uptake`; it was not selected from model residuals.

Random 5-fold:
- RF R² **0.9018**
- XGB R² **0.8900**
- stack R² **0.8886**

Primary-study GroupKFold:
- RF R² **-0.0468**
- XGB R² **0.1329**
- stack R² **-0.1956**

LOSO:
- RF R² **-0.0108**
- XGB R² **0.1851**

The conclusion is stable: row-random performance is high, while unseen-study transfer remains weak.

## 5. External transfer with V2.1 training scopes

External targets were not used for tuning. The invalid `Q_MAX=624` censoring and legacy external preprocessing errors remain removed.

### Liu et al. 2025 dye dataset — 676 rows

Training on strict comparable 273:
- RF R² **0.2977**, RMSE **381.87 mg/g**, MAE **249.15 mg/g**
- XGB R² **0.0645**, RMSE **440.72 mg/g**, MAE **293.25 mg/g**

### Jaffari et al. 2023 emerging-contaminant dataset — 3,673 rows

Training on strict comparable 273:
- RF R² **-1.2503**, RMSE **110.12 mg/g**, MAE **59.17 mg/g**
- XGB R² **-1.9729**, RMSE **126.58 mg/g**, MAE **70.49 mg/g**

External transfer is therefore **domain dependent**, not a general validation success.

## 6. Scientific disposition

1. **Do not claim ~0.90 unseen-study generalisation.** The ~0.90 values are row-random baselines.
2. **There is genuine but weak cross-study signal.** XGB is approximately R² 0.13–0.19 across the grouped/LOSO sensitivity analyses.
3. **The stacked ensemble is not supported as a superior model** and should not be the paper's novelty claim.
4. **Inverse design remains excluded** from the revised claim. Earlier applicability-domain and uncertainty gates did not support engineering optimisation/deployment.
5. **The study is not deployment-ready.** Results support methodological analysis, screening-level research, and a study-aware/domain-shift paper framing.
6. **The main publishable finding is the validation gap:** literature-derived adsorption models can appear excellent under row-random splitting while transferring poorly to genuinely unseen primary studies.
7. Any future performance improvement should come first from broader, harmonised, independently sourced experimental data and better domain/descriptor definitions—not model shopping.

## 7. Reproducibility lock

### Final matched V2.1 validation
- Workflow: `Final validation V2.1`
- Run: **32003217034**
- Job: **95307465955**
- Artifact: **9279131675**
- Artifact SHA-256: `58e6f6c5d3cab01f7b0cfb346a79feda90e8b0c6e558b0f9cef1d9adbd8f6245`

### Final robustness / LOSO / external / conventional sensitivity
- Workflow: `Robustness validation V2.1`
- Run: **32003678479**
- Job: **95308786043**
- Artifact: **9279289740**
- Artifact SHA-256: `1b7facc585f0a6b8771545e7e2af1d397a1e0c1f128618918f672a27a35f106e`

### Canonical dataset publication
- Workflow: `Publish adsorption dataset V2.1`
- Run: **32003557349**
- Result: success

## 8. Manuscript gate

The next manuscript revision must use Dataset V2.1 and the Phase 8 values above as its numerical source of truth. Superseded IEEM/V1/V2 headline metrics must not be copied into the revised Results/Discussion unless explicitly labelled as legacy baselines or audit findings.
