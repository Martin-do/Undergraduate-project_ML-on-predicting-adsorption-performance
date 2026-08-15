# ID-SEAD V2 — Phase 1 Findings

Status: **confirmed diagnostic findings; not yet a final manuscript result lock**

## 1. Legacy row-wise validation is strongly source-overlapping

The cleaned modelling target has 322 usable rows. Under a legacy-style shuffled 80/20 partition:

- 258 rows are assigned to training and 64 to test;
- 62 of the 64 test rows (96.875%) come from source labels that are also present in training;
- 8 source labels occur on both sides of the split.

The original high row-wise performance must therefore not be described as evidence of generalisation to unseen literature studies.

## 2. Validation performance is highly sensitive to grouping level

Random-forest diagnostic results on the same fold-safe preprocessing baseline:

| Validation design | R² | RMSE (mg/g) | MAE (mg/g) |
|---|---:|---:|---:|
| Row-random K-fold | 0.9108 | 203.66 | 99.78 |
| Strict `source_link` grouping | -0.4494 | 820.88 | 540.26 |

The strict source result is intentionally conservative, but the largest source label turns out not to represent one primary experiment.

## 3. The dominant source is a secondary literature compilation

The CSV label `Moosavi et al., 2023` contributes 251/322 rows (77.95%). Internally it spans:

- 24 adsorbent labels;
- 20 pollutant labels;
- 10 processing descriptions.

External provenance checking indicates that these characteristics correspond closely to the Nanomaterials paper:

> Moosavi, S. et al. (2021), *A Study on Machine Learning Methods’ Application for Dye Adsorption Prediction onto Agricultural Waste Activated Carbon*, Nanomaterials 11(10), 2734, DOI 10.3390/nano11102734.

That paper reports 350 experimental records compiled from 13 previous publications. The year/source label in the current CSV therefore requires correction/reconstruction before final study-grouped CV is locked.

## 4. Bracketing the unknown primary provenance gives intermediate performance

Because the 251-row secondary compilation currently lacks row-level primary-paper IDs, two provisional grouping schemes were added as sensitivity analyses:

| Grouping design | Groups | R² | RMSE (mg/g) | MAE (mg/g) |
|---|---:|---:|---:|---:|
| Row-random | — | 0.9098 | 204.73 | 100.01 |
| Strict citation | 16 | -0.4488 | 820.70 | 540.90 |
| Secondary-system proxy (`adsorbent + processing + pollutant` inside Moosavi) | 53 | 0.6745 | 388.99 | 261.66 |
| Adsorbent holdout | 58 | 0.7415 | 346.67 | 225.47 |

The proxy results are **not final unseen-study estimates**. They demonstrate that the truth is likely between the two invalid extremes of treating the secondary compilation as one study or treating every row as independent.

A log1p target did not rescue grouped generalisation and generally worsened raw-scale R²/RMSE, so the main issue is not merely target skew.

## 5. The hard-coded `Q_MAX = 624 mg/g` is inconsistent with the current dataset

Observed target distribution:

- minimum: 0.025 mg/g;
- median: 167.9065 mg/g;
- maximum: 2239 mg/g;
- 115/322 rows (35.714%) exceed 624 mg/g;
- all current exceedances occur inside the secondary Moosavi-labelled block.

Therefore 624 mg/g cannot be defended as a universal physical upper bound for the dataset as currently assembled, assuming those observations are correctly represented and comparable.

**Consequence:** the constraint-aware stack must not be re-tuned against `Q_MAX=624` until the domain and provenance are corrected. Options to investigate later are a domain-conditional physical bound, a target-specific bound derived from adsorption physics, or an explicitly narrower modelling population.

## 6. The secondary compilation occupies a materially different domain

Compared with the other 71 rows, the dominant block has substantial covariate-range separation:

- 62.55% of its surface-area values exceed the non-dominant observed range;
- 54.98% of particle-size values lie outside the non-dominant range;
- 68.53% of pore-volume values lie outside the non-dominant range;
- 27.09% of temperatures lie outside the non-dominant range;
- 56.97% of its `qe` values exceed the maximum `qe` observed in the other sources.

This explains why two-way transfer between the secondary block and the rest of the corpus fails badly. It is a domain-shift problem in addition to a validation-splitting problem.

## 7. Immediate scientific decisions

1. Preserve the original notebook and manuscript unchanged as historical baselines.
2. Do not report ~0.95 R² as unseen-study performance.
3. Recover primary provenance for the secondary Moosavi compilation if possible.
4. Keep `removal_percent` excluded from the primary predictor set because it can encode the adsorption-capacity target through mass-balance relationships.
5. Keep all imputation/encoding/scaling inside each training fold.
6. Evaluate LR, SVR, RF, XGB and unconstrained stacking under identical leakage-resistant folds next.
7. Redesign the physical constraint only after the modelling domain is fixed.
8. Re-run external validation only after the internal validation design is locked.

## Phase 1 conclusion

The study is **not invalid**, but the submitted validation claim was too optimistic. The data still contain predictive structure under tougher holdouts (provisional R² around 0.67–0.74 for RF under system/adsorbent grouping), which justifies continuing the project. The next question is whether the proposed stacked architecture provides reproducible value over strong RF/XGB baselines once leakage is controlled.
