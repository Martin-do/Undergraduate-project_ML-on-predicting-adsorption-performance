# ID-SEAD V2 — Phase 5 Applicability-Domain Findings

Status: **confirmed scientific gate result; feature branch only**

Phase 4 identified two candidate restricted domains with non-trivial leave-one-primary-study-out (LOSO) performance: broad biogenic waste and waste-derived carbon. Phase 5 asks whether a training-only support rule can identify unsupported held-out cases reliably enough to condition prediction or inverse design.

## 1. Training-only support rule

The applicability-domain (AD) diagnostic is target-independent.

For each LOSO fold:

1. fit the fold-safe original-feature preprocessor on training studies only;
2. retain continuous engineered/process descriptors and standardize them with training statistics only;
3. for every training row, calculate the mean distance to its five nearest rows from **other primary studies** so dense repeated points from one paper cannot define support;
4. set q95 and q99 thresholds from those training cross-study distances;
5. measure each held-out point against the training set in the same standardized space;
6. separately flag engineered categorical levels absent from training;
7. define the strict q95 rule as continuous q95 support **and** zero categorical novelty.

No target value is used to decide whether a point is supported. The legacy `Q_MAX = 624 mg/g` is not used.

## 2. Broad-biogenic-waste domain

XGB before filtering:

- 92 rows / 6 primary studies;
- pooled R² = **0.619**;
- RMSE = **476.29 mg/g**;
- MAE = **376.27 mg/g**.

Training-derived AD coverage is very low:

| Rule | Coverage | Rows | R² | RMSE | MAE |
|---|---:|---:|---:|---:|---:|
| All | 100% | 92 | 0.619 | 476.29 | 376.27 |
| Continuous q95 | **11.96%** | 11 | -1.664 | 376.57 | 308.81 |
| Strict q95 | **10.87%** | 10 | -5.623 | 323.67 | 268.12 |
| Continuous q99 | 16.30% | 15 | -1.543 | 335.23 | 265.20 |

The q95 rule correctly flags the catastrophic Alshabib/groundnut-shell study as unsupported, but it also rejects complete or nearly complete held-out studies whose prediction errors are materially lower:

- Alshabib: 0% supported, XGB MAE 1532.57 mg/g;
- Archin: 0% supported, XGB MAE 145.28 mg/g;
- Gao: 4.76% continuous support / 0% strict, XGB MAE 496.97 mg/g;
- Gupta: 100% supported, XGB MAE 268.12 mg/g;
- Li: 0% supported, XGB MAE 348.52 mg/g;
- Ravenni: 0% supported, XGB MAE 129.23 mg/g.

Therefore the distance rule is not a practical rescue: it retains only about one tenth of the broad-biogenic observations and rejects several cases on which the model actually transfers reasonably well.

## 3. Waste-derived-carbon domain

XGB before filtering:

- 138 rows / 7 primary studies;
- pooled R² = **0.495**;
- RMSE = **581.33 mg/g**;
- MAE = **408.58 mg/g**.

AD filtering lowers absolute error on the retained points but again at substantial coverage loss:

| Rule | Coverage | Rows | R² | RMSE | MAE |
|---|---:|---:|---:|---:|---:|
| All | 100% | 138 | 0.495 | 581.33 | 408.58 |
| Continuous q95 | **31.16%** | 43 | -2.867 | 388.02 | 202.48 |
| Strict q95 | **30.43%** | 42 | -5.283 | 376.93 | 190.35 |

Negative R² after filtering must not be interpreted in isolation because the retained subset has a narrower target range; the meaningful observation is that MAE falls while coverage falls to about 30%.

More importantly, the rule is **not reliably safety-selective**. In this broader domain the catastrophic Alshabib study is classified as 100% supported despite XGB MAE ≈ **1545 mg/g**. Thus support status changes materially with the chosen training domain and does not by itself identify high-error cases.

## 4. Distance–error relationship

Point-level distance has some diagnostic signal but is not sufficient as a deployment gate.

Spearman correlation between cross-study kNN distance and absolute error:

- broad biogenic: RF **0.414**, XGB **0.205**;
- waste-derived carbon: RF **0.645**, XGB **0.654**.

The stronger relationship in the waste-derived domain justifies keeping distance as one component of an applicability assessment, but not as the sole acceptance criterion.

## 5. Extreme-distance diagnosis required

Several studies show extremely large standardized cross-study distances, especially Li and Gao (~500 mean distance in some folds), while other studies are commonly in the ~2–9 range.

This may represent genuine covariate/domain separation, but before interpreting the magnitude scientifically we must inspect:

- feature-level contributions to nearest-neighbour distance;
- training standard deviations within each fold;
- whether near-constant training features are amplifying standardized differences;
- which experimental variables drive the separation.

No threshold tuning should be performed until this audit is complete.

## 6. Scientific decision gate

**Distance-only applicability-domain gate: FAIL for deployment/inverse design.**

The result is informative, but it does not provide a sufficiently reliable acceptance rule:

1. broad-biogenic q95 coverage is only ~11%;
2. several accurately predicted studies are rejected;
3. in the waste-derived domain the catastrophic Alshabib study is incorrectly accepted;
4. support is sensitive to the chosen training domain;
5. distance–error correlation is not consistently strong enough to act as a safety criterion.

Therefore:

- inverse design remains **BLOCKED**;
- do not remove difficult studies post hoc;
- do not tune the support threshold to maximize validation performance;
- retain cross-study distance as a diagnostic feature only;
- next evaluate feature-level distance drivers and a **group-aware predictive-uncertainty / residual-interval diagnostic** calibrated strictly from training studies.

If uncertainty calibration also fails to identify unreliable study transfer, the inverse-design framing should be abandoned rather than weakened into a post-hoc filtered demonstration.
