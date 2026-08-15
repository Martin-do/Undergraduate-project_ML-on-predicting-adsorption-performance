# ID-SEAD V2 — Phase 3 Provenance and Primary-Study Holdout

Status: **confirmed scientific gate result; feature branch only**

This phase replaces the provisional citation/proxy grouping with primary-study provenance wherever it can be reconstructed defensibly from the upstream literature-derived dataset.

## 1. Provenance correction

The 251-row block labelled `Moosavi et al., 2023` in the project CSV is not treated as one primary experiment. The recovered upstream lineage identifies the block as inherited from the Iftikhar et al. 2023 adsorption dataset (`Separation and Purification Technology`, 326, 124891; DOI `10.1016/j.seppur.2023.124891`). The legacy `source_link` is preserved for auditability; the canonical derived dataset stores the corrected secondary source separately.

Primary studies were assigned only when material identity and experimental signatures were strong enough to support the mapping. Unresolved rows are never given inferred study IDs simply to increase coverage.

After reconstruction:

- inherited Iftikhar-derived rows with usable target: **251**;
- rows with confirmed primary-study provenance: **238 / 251 = 94.82%**;
- confirmed primary studies represented: **11**;
- unresolved inherited rows: **13**, all under the `CS` label;
- the remaining **71** usable rows outside the Iftikhar block are not included in this strict primary-study experiment because their primary provenance has not yet been reconstructed to the same standard.

## 2. Important corpus-domain discovery

The reconstructed primary sources show that the modelling corpus is not exclusively agricultural-waste adsorbents.

A clear example is the `MC350`–`MC600` family, which maps to Hassan, Elkady and Hamad (2019), `Journal of Materials Research and Technology`, DOI `10.1016/j.jmrt.2019.07.061`. That study uses activated carbon derived from **Maghara industrial mine coal**. Other confirmed families include textile/wastewater sludge, commercial or mixed activated carbons, refined white sugar, crab shell and agricultural residues.

Therefore the submitted title/domain phrase **“using agricultural waste adsorbents” is not currently supported by the full training corpus**. A precursor-domain audit and, if statistically supportable, an agricultural/biomass-waste restricted analysis are required before the final paper scope is chosen.

## 3. Fold-safe preprocessing under true study holdout

The stricter study split exposed an edge case that random row-wise validation had hidden: for some folds, a numerical variable is entirely missing from every training study.

The V2 rule is:

- if a training-fold median exists, impute using training-fold information only;
- if a feature is completely unobserved in the training fold, mark it inactive and set it to a neutral constant in both train and held-out data;
- never use held-out values to manufacture an imputation statistic or activate a feature absent from training.

This rule prevents test-fold leakage and makes missing-domain support explicit.

## 4. Strict confirmed-primary-study holdout

The original engineered feature representation was evaluated with primary-study grouping. The constraint/QMAX layer remains excluded because the legacy universal `Q_MAX = 624 mg/g` has already failed the physical-bound audit.

Strict analysis set:

- **238 rows**;
- **11 independent primary-study groups**;
- `CS` 13 rows excluded as unresolved;
- 71 non-Iftikhar rows excluded pending equivalent provenance reconstruction.

### Pooled out-of-study metrics

| Model | R² | RMSE (mg/g) | MAE (mg/g) | Median AE (mg/g) |
|---|---:|---:|---:|---:|
| LR | **0.0803** | **691.39** | **529.41** | 365.67 |
| SVR | -0.9876 | 1016.37 | 884.40 | 782.21 |
| RF | -0.1341 | 767.73 | 550.29 | 471.16 |
| XGB | -0.1893 | 786.20 | 547.20 | **305.24** |
| Ridge stack, unconstrained | -0.1562 | 775.18 | 642.46 | 496.69 |

### Equal-study error summary

Each primary study receives equal weight in this summary rather than allowing the largest studies to dominate.

| Model | Mean study MAE | Median study MAE | Mean study RMSE | Median study RMSE |
|---|---:|---:|---:|---:|
| LR | 454.30 | 299.02 | 496.85 | 335.16 |
| SVR | 660.85 | 742.71 | 698.42 | 778.19 |
| RF | 387.88 | 416.36 | 452.81 | 470.61 |
| XGB | **355.62** | **270.59** | **412.60** | **281.83** |
| Ridge stack, unconstrained | 552.43 | 473.04 | 586.92 | 488.51 |

## 5. Interpretation

This is the strongest validation result obtained so far because grouping now follows reconstructed primary experiments rather than rows, adsorbent names or a collapsed secondary citation label.

The result is unfavorable to the submitted claim, but scientifically important:

1. **No tested model demonstrates convincing transfer to unseen primary studies.** The only positive pooled R² is LR at ~0.08, with an RMSE still near 691 mg/g.
2. **The stacked ensemble fails the model-selection gate.** It is negative in pooled R² and is worse than the best base learners on both pooled and equal-study error views.
3. The strong row-random RF/XGB/stack scores therefore substantially reflected within-study similarity and source/domain overlap rather than broad literature-to-new-study generalization.
4. XGB has the best equal-study average absolute-error profile, but its pooled R² remains negative; this is not evidence of a generally deployable cross-study surrogate.
5. The Li et al. vinasse/high-capacity study is a severe held-out domain challenge. RF and XGB MAE exceed ~1200 mg/g on that study, showing that target/descriptor extrapolation dominates the pooled failure.
6. Unknown categorical levels appearing in held-out folds are expected under true study transfer and are themselves evidence that some studies occupy feature categories absent from training studies.

## 6. Scientific decision gate

**Decision: FAIL for the submitted “stacked ensemble superiority / general inverse design” framing.**

Until a defensible restricted applicability domain is found:

- do not claim unseen-study R² near the row-random values;
- do not retain stacking as the central novelty on the basis of predictive superiority;
- do not reintroduce the legacy physical constraint/QMAX layer;
- do not present inverse-designed candidates as validated optima;
- do not describe the full corpus as agricultural-waste-only.

The next experiment is a precursor/domain audit followed by domain-restricted, primary-study-held-out validation **only where enough independent studies remain to make such validation meaningful**. If a scientifically coherent subset is too small, the paper must be reframed around heterogeneous literature-data leakage, domain shift and applicability limits rather than forcing a positive predictive claim.
