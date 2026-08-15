# Revised paper scope — LOCKED V2

Status: **scientific scope locked after Phases 1–7 and deterministic-manifest success**

## Working title

**Study-Aware Validation and Domain Shift in Literature-Derived Machine Learning for Adsorption Capacity Prediction**

This replaces the submitted inverse-design/stacking/agricultural-waste framing.

## Central research question

> How much of the apparent predictive performance of literature-derived adsorption machine-learning models survives when provenance, primary-study separation, precursor-domain heterogeneity, missing-feature transfer and external domain shift are treated explicitly?

## Core contribution

The revised work is a **validation, provenance and reproducibility study** of adsorption-capacity machine learning built from heterogeneous literature data.

The manuscript should establish that:

1. conventional row-random splitting can materially overstate transferable performance when many rows originate from the same primary experiments;
2. reconstructed primary-study holdout is a more defensible evaluation unit for literature-derived adsorption data;
3. added model complexity (the historical Ridge stacking layer) does not solve study/domain shift;
4. precursor-domain definition materially changes apparent transfer performance;
5. simple descriptor-distance and model-disagreement heuristics are insufficient as reliability gates;
6. external transfer remains modest after correcting legacy preprocessing/citation defects;
7. provenance and validation design should be treated as first-class parts of adsorption-ML methodology.

## Claims removed permanently from V2 manuscript

Do **not** claim:

- superior stacked-ensemble generalization;
- validated inverse design or engineering optimization;
- a universal physical adsorption-capacity ceiling of 624 mg/g;
- agricultural-waste-only coverage of the complete corpus;
- unseen-study generalization from row-random scores;
- reliable out-of-domain detection from the tested Euclidean/kNN distance rule;
- reliable predictive uncertainty from RF–XGB disagreement;
- guaranteed source-independent external validation without complete primary-paper overlap reconstruction.

## Locked evidence hierarchy

### 1. Leakage / provenance

Legacy-style random splitting places **62/64 test rows (96.875%)** in source labels already represented in training.

The dominant 251-row block is a secondary-compilation inheritance rather than one experiment. Primary provenance has been reconstructed for **238/251 rows (94.82%) across 11 primary studies**.

The remaining `CS` family (**13 rows**) remains unresolved. It is **permanently excluded from primary-study validation claims unless future primary-source evidence establishes its provenance**. It may remain in the raw archival corpus but must not be silently assigned a study ID.

### 2. Full reconstructed primary-study transfer

On 238 confirmed rows / 11 primary studies:

- LR: R² ≈ 0.080;
- RF: R² ≈ -0.134;
- XGB: R² ≈ -0.189;
- unconstrained Ridge stack: R² ≈ -0.156.

This is the main result demonstrating that strong row-random performance did not translate to broad unseen-study generalization.

### 3. Precursor-domain restriction

The complete corpus is not agricultural-waste-only. Confirmed precursor classes include agricultural/agro-industrial residues, crab shell, textile/wastewater sludge, white sugar, commercial/mixed carbons and industrial mine coal.

Candidate domains:

- **strict agricultural waste:** 65 rows / 4 primary studies — insufficiently broad and poor LOSO performance;
- **broad biogenic waste:** 92 rows / 6 studies — XGB pooled LOSO R² ≈ 0.619, but one complete held-out study fails catastrophically;
- **waste-derived carbon:** 138 rows / 7 studies — RF/XGB pooled R² ≈ 0.49, with substantial study-level variability.

These are domain-sensitivity results, not a replacement universal model claim.

### 4. Reliability diagnostics

The corrected cross-study descriptor-distance rule does not reliably rank prediction error. Study-aware residual intervals become extremely wide and still fail on the catastrophic held-out Alshabib study. RF and XGB can agree closely while both are badly wrong.

Therefore inverse optimization is not scientifically defensible with the present corpus/model evidence.

### 5. External transfer

After correcting legacy source/preprocessing defects and removing project-QMAX target censoring:

- Liu et al. 2025: best tested result = full-corpus RF, R² ≈ **0.223**;
- Jaffari et al. 2023: best tested result = waste-derived RF, R² ≈ **0.181**.

These results are modest, not evidence of deployment-grade transfer. The old catastrophic external scores remain historical execution artifacts, not V2 benchmarks.

## Model role in revised paper

- **RF and XGB:** comparative nonlinear surrogates used to study transfer behavior.
- **LR and SVR:** simpler reference baselines.
- **Ridge stack:** historical proposed model retained as a comparison demonstrating that added ensemble complexity did not solve study shift.
- **No single model is the paper's novelty.**

## Revised manuscript structure

### 1. Introduction

Motivate the central methodological problem: literature-derived adsorption datasets may contain many rows but relatively few independent experimental sources, so row-random validation can measure interpolation within studies rather than transfer to new studies.

### 2. Data provenance and corpus reconstruction

Cover the project corpus, secondary compilation lineage, primary-study reconstruction, unresolved provenance policy, precursor classes, target cleaning, removal-percent exclusion and the failure of universal QMAX=624 mg/g.

### 3. Study-aware validation methodology

Describe the original feature representation, fold-safe preprocessing, row-random comparator, primary-study holdout, domain-restricted LOSO, equal-study metrics, applicability-domain diagnostics, empirical study-aware residual intervals and external transfer methodology.

### 4. Results

Use this order:

1. provenance/source-overlap audit;
2. row-random versus primary-study performance;
3. base models versus historical stack;
4. precursor-domain composition and restricted LOSO;
5. applicability/uncertainty diagnostic failures;
6. corrected external-transfer results.

### 5. Discussion

Interpret the results through repeated within-study conditions, source-specific material/process distributions, target-range concentration, missing features, categorical novelty and the difference between row count and independent-study count.

### 6. Practical recommendations

Recommend that adsorption-ML studies:

- preserve primary-paper provenance at row level;
- split by primary study/material system before model selection;
- report study counts alongside row counts;
- report pooled and equal-study errors;
- avoid target-derived predictors;
- justify physical bounds within a defined material/pollutant domain;
- verify semantic equivalence before mapping external features;
- validate applicability and uncertainty heuristics rather than assuming them;
- disclose possible overlap between literature compilations.

### 7. Conclusion

Conclude that validation design and provenance materially change the apparent generalization of literature-derived adsorption ML, and that the present evidence does not support the original universal stacked inverse-design claim.

## Figures to build from the deterministic manifest

1. provenance reconstruction flow;
2. row-random versus primary-study performance comparison;
3. precursor-domain row/study composition;
4. per-study LOSO error for restricted domains;
5. external-transfer + feature-coverage/domain-mismatch figure.

## Tables to build from the deterministic manifest

1. corpus/provenance summary;
2. row-random vs strict primary-study performance;
3. domain-restricted LOSO performance with study counts;
4. external-transfer metrics and feature-coverage caveats;
5. applicability/uncertainty diagnostic table (main or supplementary, depending journal length).

## Reproducibility rule

All numerical values in the revised manuscript must be pulled from the deterministic V2 result manifest generated by CI. No result table should be maintained manually.

## Journal-positioning note

This scope is best positioned as environmental/process-engineering machine learning methodology and adsorption modelling—not industrial-engineering optimization. Journal selection should follow this revised contribution rather than the rejected IEEM framing.