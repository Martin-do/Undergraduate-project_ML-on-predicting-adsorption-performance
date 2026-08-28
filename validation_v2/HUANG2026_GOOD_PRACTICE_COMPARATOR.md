# Huang et al. 2026 — Good-Practice Source-Aware Comparator

Status: **CONFIRMED LITERATURE COMPARATOR — RAW MODELLING DATA NOT PUBLICLY RELEASED**

Citation: Xin Huang, Xiaopeng Bai, Yifei Yang, Wenbin Li, Daochun Xu. *Machine Learning-Based Prediction and Optimization of Heavy Metal Adsorption Performance of Biochar*. Forests 17(3), 326 (2026). DOI: `10.3390/f17030326`.

## Why this study matters for Paper 1

Huang et al. is retained as a deliberately positive counterexample. Paper 1 does not argue that high adsorption-ML performance is necessarily an artefact of row-random splitting. Huang et al. explicitly use publication-level separation and still report strong performance.

This study therefore supports the manuscript's outcome-neutral interpretation:

> Validation must match the intended unit of generalisation. Strong performance may survive source-aware evaluation in a sufficiently coherent and informative domain.

## Dataset

The article reports two literature-derived datasets. The adsorption-capacity dataset (`Data 2`) contains **452 adsorption records** compiled from independent literature sources and focuses primarily on Cu(II) and Pb(II) single-solute adsorption by biochar.

Only experimentally measured equilibrium adsorption capacity (`qe`) is used as the target; fitted Langmuir maximum-capacity values are excluded. Initial concentration, solution pH and temperature are included where available. Contact time and sorbent dosage are not consistently available and are omitted.

## Leakage-control design

The article explicitly states that train/test splitting is performed at the **literature-source level**:

- train:test ratio = **4:1**;
- every sample originating from one publication is assigned exclusively to either train or test;
- no publication contributes observations to both partitions;
- KNN imputation, outlier handling and standardisation are parameterised from the training data and then applied to test data;
- hyperparameter optimisation uses five-fold cross-validation within the training set.

This is aligned with the scientific unit-of-independence principle used in Paper 1.

## Reported adsorption-capacity performance

For `qe`, the article reports:

| Model | Train R2 | Test R2 | Test RMSE | Test MAE | 5-fold CV |
|---|---:|---:|---:|---:|---:|
| RF | 0.98 | 0.96 | 0.04 | 0.02 | 0.88 ± 0.04 |
| GBR | 0.99 | 0.98 | 0.03 | 0.02 | 0.92 ± 0.05 |
| XGB | 0.99 | **0.99** | **0.02** | **0.01** | **0.92 ± 0.04** |

The paper therefore demonstrates that stringent publication-level separation does **not** inevitably imply poor performance.

## Important interpretation caveat

The article itself acknowledges that heterogeneous literature sources may still contain study-specific patterns and that predictive performance should be interpreted within the experimental domain represented in the compiled dataset. Source-aware splitting reduces one major dependence problem but does not automatically establish universal deployment validity.

## Reproducibility gate

The article's Data Availability Statement says that the data are available **upon request from the author**. The publicly downloadable supplementary material contains Bayesian-optimisation parameters and a GUI schematic, but not the 452-row modelling dataset.

Therefore:

- Huang 2026 is **confirmed as a good-practice comparator**;
- it is **not counted as one of Paper 1's independently rerun matched replications** at present;
- no synthetic or reconstructed 452-row dataset will be created from article tables;
- an independent rerun may be added later only if the authors supply the original modelling data with source identity preserved.

## Paper 1 role

Use Huang 2026 to prevent overstatement. It directly supports the conclusion that the validation gap is **dataset-dependent**, not universal. In the discussion it should be contrasted with V2.1, Moosavi 2021 and Liu 2025, where matched random-versus-study-aware evaluation produces substantial performance reductions.

Public evidence checked 2026-08-28 from the publisher article and methods/results tables.
