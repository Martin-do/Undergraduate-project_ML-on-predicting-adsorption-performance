# ID-SEAD V2 — Phase 5 Applicability-Domain Findings

Status: **confirmed scientific gate result; corrected feature branch result**

Phase 4 identified two candidate restricted domains with non-trivial leave-one-primary-study-out (LOSO) performance: broad biogenic waste and waste-derived carbon. Phase 5 asks whether a training-only support rule can identify unsupported held-out cases reliably enough to condition prediction or inverse design.

## 1. Training-only support rule

The applicability-domain (AD) diagnostic is target-independent.

For each LOSO fold:

1. fit the fold-safe original-feature preprocessor on training studies only;
2. identify the candidate continuous engineered/process descriptors;
3. **exclude any candidate that is constant or near-constant in that training fold** because no empirical scale exists to normalize a held-out change;
4. standardize the remaining continuous descriptors with training statistics only;
5. for every training row, calculate the mean distance to its five nearest rows from **other primary studies** so dense repeated points from one paper cannot define support;
6. set q95 and q99 thresholds from those training cross-study distances;
7. measure each held-out point against the training set in the same standardized space;
8. separately flag engineered categorical levels absent from training;
9. define the strict q95 rule as continuous q95 support **and** zero categorical novelty.

No target value is used to decide whether a point is supported. The legacy `Q_MAX = 624 mg/g` is not used.

## 2. Important correction to the first distance implementation

The first Phase-5 diagnostic exposed extreme distances around ~500 for Li and Gao. A feature-level audit showed that these magnitudes were dominated by `contact_time_min` in folds where contact time was constant across every training study.

Examples:

- Li held out: training contact time = 600 min for all relevant training rows; Li = 60 min;
- Gao held out: training contact time = 60 min; Gao includes 600 min.

`StandardScaler` cannot estimate a variance for a constant training variable and effectively leaves the held-out difference in original units. Mixing that unscaled minute difference with standardized dimensions created an arbitrary distance artifact.

**Correction:** fold-constant continuous variables are now excluded from distance. The earlier ~11%/~31% coverage figures and positive distance-error correlations are superseded and must not be cited as final V2 results.

`dose_gL` is also inactive/constant in these restricted-domain folds under the parity preprocessing and is therefore excluded from the corrected distance calculation.

## 3. Corrected broad-biogenic-waste AD result

XGB before filtering:

- 92 rows / 6 primary studies;
- pooled R² = **0.619**;
- RMSE = **476.29 mg/g**;
- MAE = **376.27 mg/g**.

Corrected support results:

| Rule | Coverage | Rows | R² | RMSE | MAE |
|---|---:|---:|---:|---:|---:|
| All | 100% | 92 | 0.619 | 476.29 | 376.27 |
| Continuous q95 | **85.87%** | 79 | 0.616 | 449.05 | 381.57 |
| Strict q95 | **61.96%** | 57 | 0.694 | 390.72 | 335.75 |
| Continuous q99 | **91.30%** | 84 | 0.645 | 437.23 | 366.38 |

The strict rule improves aggregate XGB metrics on retained observations, but it is not a reliable failure detector:

- Alshabib: 0% supported; XGB MAE 1532.57 mg/g;
- Archin: 0% supported; XGB MAE 145.28 mg/g;
- Gao: 100% continuously supported but 0% strict because its engineered category is novel; XGB MAE 496.97 mg/g;
- Gupta: 100% strict support; XGB MAE 268.12 mg/g;
- Li: 97.96% continuous / 95.92% strict support; XGB MAE 348.52 mg/g;
- Ravenni: 0% supported; XGB MAE 129.23 mg/g.

Thus the rule rejects both the catastrophic Alshabib study and several relatively successful held-out studies. Its apparent aggregate improvement is therefore not sufficient evidence of a dependable safety gate.

## 4. Corrected waste-derived-carbon AD result

XGB before filtering:

- 138 rows / 7 primary studies;
- pooled R² = **0.495**;
- RMSE = **581.33 mg/g**;
- MAE = **408.58 mg/g**.

Corrected support results:

| Rule | Coverage | Rows | R² | RMSE | MAE |
|---|---:|---:|---:|---:|---:|
| All | 100% | 138 | 0.495 | 581.33 | 408.58 |
| Continuous q95 | **80.43%** | 111 | 0.384 | 643.97 | 487.27 |
| Strict q95 | **64.49%** | 89 | 0.415 | 646.81 | 474.94 |
| Continuous q99 | **81.16%** | 112 | 0.382 | 643.73 | 488.42 |

Here the support filtering **makes predictive error worse**. Most importantly, the catastrophic Alshabib study is classified as 100% supported despite XGB MAE ≈ **1545 mg/g**.

This directly prevents the distance rule from being interpreted as a general reliability gate.

## 5. Corrected distance–error relationship

After removal of fold-constant artifacts, point-level distance is not positively associated with absolute error in a stable way.

Spearman correlation between corrected cross-study kNN distance and absolute error:

- broad biogenic: RF **0.123**, XGB **-0.068**;
- waste-derived carbon: RF **-0.279**, XGB **-0.283**.

Pearson correlations are similarly weak or negative.

Therefore the earlier apparent positive distance-error relationship was largely driven by the scaling artifact and is not retained as a scientific result.

## 6. What actually drives corrected distance

The corrected feature-decomposition audit shows real but study-specific covariate differences rather than one universal OOD direction.

Examples:

- **Alshabib, broad biogenic:** pyrolysis temperature contributes ~47% of squared distance, particle size ~25%, with pH/temperature terms also important;
- **Li, broad biogenic:** temperature contributes ~51%, particle size ~14%, followed by concentration/ratio terms;
- **Gao:** surface-area × pore-volume and pore-volume descriptors dominate;
- **Ravenni:** particle size and pyrolysis temperature dominate;
- **Wong, waste-derived:** temperature is the largest contributor.

This confirms genuine inter-study descriptor shifts exist, but simple Euclidean support distance does not translate those shifts into reliable prediction-risk ranking.

## 7. Scientific decision gate

**Corrected distance-only applicability-domain gate: FAIL for deployment/inverse design.**

The final Phase-5 reasoning is stronger than the provisional result:

1. the first extreme-distance magnitudes were partly caused by a fold-constant scaling artifact and have been corrected;
2. after correction, coverage is much higher, but support status still does not reliably separate high-error from low-error studies;
3. in the waste-derived domain, filtering worsens XGB performance;
4. the catastrophic Alshabib study is considered supported in the waste-derived domain;
5. corrected distance-error correlation is weak or negative;
6. support status remains sensitive to the chosen training domain.

Therefore:

- inverse design remains **BLOCKED**;
- do not remove difficult studies post hoc;
- do not tune the support threshold to maximize validation performance;
- retain the corrected distance analysis as an explanatory domain-shift diagnostic only;
- evaluate study-aware empirical residual intervals as the final reliability gate before deciding whether inverse design must be abandoned.
