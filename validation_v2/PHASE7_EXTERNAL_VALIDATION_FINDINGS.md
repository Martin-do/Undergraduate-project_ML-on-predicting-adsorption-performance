# ID-SEAD V2 — Phase 7 External-Validation Reconstruction and Rerun

Status: **confirmed scientific/reproducibility gate result; feature branch only**

Phase 7 reconstructs the two legacy external-validation pipelines from the committed notebooks/workbooks, corrects source/citation and feature-mapping defects, removes the invalid project-wide `Q_MAX = 624 mg/g` censoring, and reruns external prediction using the V2 feature-parity pipeline.

## 1. External source identities corrected

### Dataset A

The legacy notebook labels this dataset `Shen et al. 2024`, but the DOI and workbook correspond to:

- **Liu et al. (2025)**, *Enhanced machine learning prediction of biochar adsorption for dyes: Parameter optimization and experimental validation*, Carbon Research 4, 46 (2025);
- DOI: `10.1007/s44246-025-00213-9`;
- repository workbook: `Biochar_dye_filtered.xlsx`.

The workbook contains 685 rows in both the `After preprocessing` and `original` sheets. Dye identity is recovered from `original.TypeDye`; adsorption capacity Q and initial concentration C0 are converted from mmol-based units to mg units using the legacy notebook's molecular-weight map.

### Dataset B

The legacy notebook identifies Jaffari et al. 2023 but gives an incorrect DOI ending `144684`.

Verified source:

- **Jaffari et al. (2023)**, *Machine-learning-based prediction and optimization of emerging contaminants' adsorption capacity on biochar materials*, Chemical Engineering Journal 466, 143073;
- correct DOI: `10.1016/j.cej.2023.143073`;
- repository workbook: `Raw_data.xlsx`, 3,757 rows.

## 2. Legacy external-pipeline defects

The forensic audit confirms multiple issues that materially affect interpretation of the old external numbers.

### Both datasets

The legacy pipeline removed observations with target `qe > 624 mg/g` and evaluated predictions under the same universal upper bound. Phase 1 already showed that 624 mg/g is not a valid universal physical ceiling for the project corpus. Therefore the legacy external sets were target-censored by a project assumption that is itself invalid.

### Liu dataset

The legacy prediction helper supplied only the small set of features available in the external workbook and filled the rest from a project-training template. V2 instead represents unavailable cross-dataset variables as missing and lets the training-fitted fold-safe preprocessor handle them explicitly.

### Jaffari dataset

Two additional implementation defects are confirmed:

1. the workbook header `Pyrolysis temperature  ` contains trailing whitespace, while the old rename key did not. Consequently the legacy code silently failed to use Jaffari's actual pyrolysis temperature and retained a project-training template value;
2. `Average pore size` was mapped to `particle_size_mm`. Pore diameter and adsorbent particle size are different physical quantities. V2 leaves particle size missing instead of making that substitution.

## 3. Legacy Liu N=525 result is not reproducible from saved inputs

The notebook contains a saved output:

> `Dataset A loaded: 525 rows after filtering`

V2 now parses `Q_MAX` and `DYE_MW` directly from the saved `ID_SEAD_Master.ipynb` source and replays the exact Dataset-A filtering sequence against the currently committed workbook.

Forensic replay:

- workbook rows: **685**;
- notebook QMAX: **624 mg/g**;
- notebook dye-MW keys: **17**;
- mapped dye rows: **668**;
- unmapped rows: **17**, all `tartrazine`;
- positive convertible rows: **578**;
- exact notebook-source filter `0 < qe <= 624` plus `C0 > 0`: **548 rows**;
- saved notebook output: **525 rows**.

Thus the currently committed notebook source and workbook do **not** reproduce the saved N=525 output. A threshold near 550–575 mg/g would produce counts around 523–527, but the saved notebook source explicitly says 624 mg/g.

**Disposition:** N=525 and its associated legacy external metrics are retained only as historical saved-execution artifacts. They are not treated as reproducible external-dataset definitions or used as V2 benchmarks.

## 4. V2 external-data preparation

### Liu 2025

V2 retains all positive, finite, molecular-weight-convertible observations without applying the project's QMAX:

- **N = 578**;
- converted qe range: up to approximately **1809.16 mg/g**;
- 30 of these rows would have been removed solely by the legacy 624 mg/g rule;
- `tartrazine` remains excluded because the legacy conversion map provides no molecular weight for it;
- directly available model inputs: surface area, pore volume, C0, adsorption temperature, pH and pollutant identity;
- unavailable cross-dataset fields: particle size, contact time, dose and pyrolysis temperature.

### Jaffari 2023

V2 retains all positive finite targets:

- **N = 3,757**;
- qe maximum approximately **1557.46 mg/g**;
- 80 rows would have been removed solely by the legacy 624 mg/g rule;
- actual pyrolysis temperature/time are supplied through `method_processing`;
- contact time and dose are supplied;
- `Average pore size` is not used as adsorbent particle size.

No external target values are used for preprocessing/model tuning.

## 5. Clean external metrics

Three predeclared training scopes are tested using LR/RF/XGB:

- full 322-row usable project corpus;
- broad-biogenic-waste confirmed-primary subset;
- waste-derived-carbon confirmed-primary subset.

Stacking and the physical-constraint layer are intentionally excluded because both already failed earlier V2 gates.

### Liu 2025, N=578

| Training scope | Model | R² | RMSE (mg/g) | MAE (mg/g) |
|---|---|---:|---:|---:|
| Full corpus | LR | -7.940 | 567.57 | 417.39 |
| Full corpus | **RF** | **0.223** | **167.38** | **106.16** |
| Full corpus | XGB | -0.133 | 202.01 | 124.75 |
| Broad biogenic | RF | -0.175 | 205.80 | 148.99 |
| Broad biogenic | XGB | -0.460 | 229.37 | 169.24 |
| Waste-derived | RF | **0.030** | **186.91** | **131.75** |
| Waste-derived | XGB | 0.073 | 182.79 | 131.95 |

The best V2 result is full-corpus RF, R² ≈ **0.223**. This is materially better than the legacy catastrophic negative result, but remains weak for broad engineering prediction.

### Jaffari 2023, N=3,757

| Training scope | Model | R² | RMSE (mg/g) | MAE (mg/g) |
|---|---|---:|---:|---:|
| Full corpus | LR | -46.396 | 482.00 | 401.96 |
| Full corpus | **RF** | **-0.011** | **70.39** | **55.76** |
| Full corpus | XGB | -1.656 | 114.06 | 76.03 |
| Broad biogenic | RF | -0.537 | 86.78 | 60.84 |
| Broad biogenic | XGB | -0.275 | 79.01 | 59.87 |
| Waste-derived | **RF** | **0.181** | **63.35** | **46.28** |
| Waste-derived | XGB | -1.014 | 99.33 | 67.43 |

The best V2 result is waste-derived RF, R² ≈ **0.181**. Again, this is much less catastrophic than the saved legacy result but is not evidence of reliable deployment.

## 6. External feature/domain mismatch remains substantial

### Liu

Four important model inputs have zero direct external coverage: particle size, contact time, dose and pyrolysis temperature.

The external rows are also categorically novel in material representation:

- full-corpus preprocessing: `base_material = other` is novel for 100% of rows;
- restricted scopes can additionally see `activation_agent = None` as novel.

### Jaffari

Particle size has zero valid direct coverage after correcting the pore-size/particle-size mistake.

Material representation is highly novel:

- `base_material = other`: 100% novel;
- `material_class = unknown_class`: 100% novel;
- `activation_agent = None`: about 93.2% novel in the tested mappings.

These mismatches explain why the external tests are useful as domain-transfer stress tests rather than as simple IID validation sets.

## 7. Corrected distance support does not rescue external transfer

Despite weak external predictive performance, the corrected training-derived continuous support metric classifies most external rows as within q95 support:

- Liu: approximately **89–91%** supported under the restricted training scopes;
- Jaffari: approximately **92–93%** supported.

This independently reinforces Phase 5: continuous descriptor distance is not a reliable predictor of model correctness. High apparent support can coexist with low/negative external R².

## 8. External independence caution

These are separate published compilations, but complete primary-paper disjointness from the project training corpus has not been proven. A literal search of the 11 currently confirmed training DOIs against the Liu literature sheet finds zero exact DOI matches, but absence of literal DOI strings is not proof that no underlying primary paper overlaps.

Accordingly the revised paper should describe these as **external published datasets/compilations used for transfer testing**, not claim guaranteed source-independent external validation unless primary-study overlap is explicitly reconstructed.

Row-level bootstrap confidence intervals are also not reported because observations within these compilations are not independent and row-level primary-study identifiers are unavailable/incomplete.

## 9. Scientific disposition

The external rerun changes one earlier interpretation but does **not** rescue the submitted method.

### What is superseded

The saved catastrophic external R² values around -18.8 and -16.1 should not be cited as clean evidence of inherent model failure. They came from a legacy pipeline containing target censoring, feature-template substitutions, a Jaffari header bug, and a pore-size/particle-size mismatch; Dataset A's saved N=525 is itself non-reproducible from the current saved source/workbook.

### What remains true

Clean external transfer is still modest at best:

- best Liu R² ≈ **0.223**;
- best Jaffari R² ≈ **0.181**;
- XGB, despite being the strongest restricted-domain internal LOSO model, often performs poorly or negatively on the external compilations;
- corrected continuous support labels most external observations supported despite weak performance.

Therefore the V2 evidence still supports the paper pivot toward **provenance, validation design, domain shift and generalization limits** rather than stacked-ensemble superiority or inverse design.

## 10. Next gate

With internal study-aware validation, domain restriction, applicability diagnostics, uncertainty diagnostics and external transfer now reconstructed, the next step is to generate a **deterministic result manifest** that links every manuscript-eligible number to:

- dataset/domain;
- validation split;
- model;
- metric and unit;
- script/workflow;
- source-data identity;
- Git commit SHA;
- whether the result is primary, diagnostic, superseded or historical only.

The revised title/scope and manuscript tables should be locked only from that manifest.
