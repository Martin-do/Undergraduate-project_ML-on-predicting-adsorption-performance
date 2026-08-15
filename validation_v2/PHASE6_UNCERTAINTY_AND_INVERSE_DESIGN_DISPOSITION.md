# ID-SEAD V2 — Phase 6 Study-Aware Uncertainty and Inverse-Design Disposition

Status: **confirmed scientific gate result; feature branch only**

Phase 5 showed that corrected cross-study descriptor distance is useful for explaining domain shift but does not reliably rank prediction error. Phase 6 evaluates whether training-only predictive uncertainty can provide a credible reliability gate for the restricted-domain XGB surrogate.

## 1. Why this is not called formal conformal prediction

The available literature data contain only six broad-biogenic primary studies and seven waste-derived-carbon primary studies. Rows within a study are dependent and study distributions are visibly heterogeneous.

Accordingly, V2 does **not** claim exchangeable-conformal coverage guarantees.

The implemented analysis is an empirical **group-aware residual-interval diagnostic**:

- outer validation: leave one complete primary study out;
- inner calibration: leave one complete training primary study out, using only the outer-training studies;
- each inner held-out study receives equal total calibration weight so the largest paper cannot dominate the residual quantile;
- prediction model: XGB in the original engineered-feature representation;
- comparison uncertainty signal: RF–XGB disagreement;
- nominal levels: 90% and 95%;
- the outer held-out study is never used to choose interval width.

Two interval forms are tested:

1. **fixed study-balanced residual interval**: XGB prediction ± empirical inner-study residual quantile;
2. **RF–XGB disagreement-scaled interval**: residuals are normalized by a training-derived baseline plus RF–XGB disagreement, then rescaled at the outer test point.

## 2. Broad-biogenic-waste result

### Fixed study-balanced residual intervals

| Nominal level | Row-weighted coverage | Equal-study mean coverage | Studies with zero coverage | Mean interval width |
|---|---:|---:|---:|---:|
| 90% | **97.83%** | **83.33%** | **1 / 6** | **2957.57 mg/g** |
| 95% | **97.83%** | **83.33%** | **1 / 6** | **3037.59 mg/g** |

The apparently high row-weighted coverage is misleadingly easy to achieve because the intervals are enormous: their average width is around 3,000 mg/g, larger than the approximate observed response span of the current corpus.

Despite those very wide intervals, the catastrophic **Alshabib** held-out study still has **0% coverage**:

- XGB mean absolute error: **1532.57 mg/g**;
- 90% fixed interval width: **1150.40 mg/g** in that fold;
- 95% fixed interval width: **1412.59 mg/g**;
- both rows remain outside the intervals.

### RF–XGB disagreement-scaled intervals

The disagreement-scaled approach is worse as a practical uncertainty measure:

| Nominal level | Row-weighted coverage | Equal-study mean coverage | Studies with zero coverage | Mean interval width |
|---|---:|---:|---:|---:|
| 90% | 97.83% | 83.33% | 1 / 6 | **12,995.56 mg/g** |
| 95% | 97.83% | 83.33% | 1 / 6 | **13,002.13 mg/g** |

The Li fold alone reaches mean interval widths above 20,000 mg/g. Such intervals do not provide useful engineering resolution.

More importantly, Alshabib again has **0% coverage**. RF and XGB disagree by only about **5.5 mg/g** there while both are wrong by more than 1,500 mg/g. Model-to-model agreement therefore does not imply correctness.

## 3. Waste-derived-carbon result

### Fixed intervals

| Nominal level | Row-weighted coverage | Equal-study mean coverage | Studies with zero coverage | Mean interval width |
|---|---:|---:|---:|---:|
| 90% | **98.55%** | **85.71%** | **1 / 7** | **2919.67 mg/g** |
| 95% | **98.55%** | **85.71%** | **1 / 7** | **3040.74 mg/g** |

Again, high aggregate coverage is purchased through intervals roughly 3,000 mg/g wide, while the Alshabib study still has zero coverage.

For Alshabib in this broader training domain:

- XGB mean absolute error: **1545.18 mg/g**;
- RF–XGB mean disagreement: only **14.74 mg/g**;
- 90% fixed interval width: **1003.30 mg/g**;
- 95% fixed interval width: **1290.26 mg/g**;
- empirical coverage: **0%**.

### Disagreement-scaled intervals

The disagreement-scaled diagnostic does not solve the failure:

- 90% row-weighted coverage: **74.64%** with mean width **3338.79 mg/g**;
- 95% row-weighted coverage: **89.86%** with mean width **4318.94 mg/g**;
- Alshabib coverage remains **0%** at both levels.

Thus RF–XGB disagreement is neither sharp nor reliably conservative across unseen studies.

## 4. What this means scientifically

The uncertainty analysis fails in two distinct ways:

1. **Fixed residual intervals are too wide to be useful** for engineering decision support, yet still miss the most severe held-out-study failure.
2. **Model disagreement is not a dependable epistemic-uncertainty proxy**: two tree models can make similar predictions and be jointly wrong by >1500 mg/g.

This is exactly the failure mode that makes inverse optimization dangerous. An optimizer can exploit a confident-looking region of the surrogate even when the available literature studies do not identify the model error there.

## 5. Final inverse-design gate

**Inverse-design framing: FAIL for this dataset and current scientific evidence.**

This is no longer merely “blocked pending one more safeguard.” The sequential V2 tests have now shown:

- row-random validation is strongly study-overlapping;
- true primary-study holdout collapses full-domain performance;
- stacking is not superior to the best base model;
- the universal `Q_MAX = 624 mg/g` is contradicted by the training corpus;
- the submitted agricultural-waste-only scope does not match the actual data;
- the strict agricultural subset has only four studies and fails LOSO badly;
- broader restricted domains improve average transfer but retain complete-study failures;
- corrected cross-study distance does not reliably rank prediction error;
- study-aware residual intervals are extremely wide and still miss the catastrophic study;
- RF–XGB agreement can coexist with catastrophic shared error.

Therefore V2 should **not** restore the original claim that the model performs reliable inverse design of adsorption conditions.

The optimizer code may remain in the repository as a historical/numerical demonstration, but it should not be presented as a validated engineering-design contribution in the revised scientific paper.

## 6. Recommended paper pivot

The scientifically strongest contribution now is not “a superior stacked inverse-design algorithm.” It is the demonstration that literature-derived adsorption ML can appear strong under row-random validation while failing under reconstructed study-aware validation because of provenance collapse, domain heterogeneity and study shift.

A defensible revised paper can center on:

- provenance reconstruction of literature-derived adsorption data;
- quantification of study leakage in conventional random splits;
- primary-study-held-out performance;
- precursor-domain restriction and its limits;
- failure of simple distance and model-disagreement reliability heuristics;
- practical recommendations for evaluating adsorption ML built from heterogeneous literature data.

The broad-biogenic XGB result (LOSO R² ≈ 0.619 across six studies) can remain as an important **restricted-domain diagnostic**, but not as evidence of universally reliable deployment or inverse design.

## 7. Next work

The scientific workflow should now move away from attempts to rescue inverse design and toward reproducibility of the revised evidence:

1. rerun/standardize the independent external-dataset failures through the clean V2 pipeline where source data permit;
2. generate a deterministic result manifest linking every reported metric to code version, dataset, split and seed;
3. decide the final paper scope/title around study-aware validation/domain shift;
4. then rewrite tables, figures, equations and manuscript layout from the locked result manifest.
