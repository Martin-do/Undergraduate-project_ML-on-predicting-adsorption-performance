# Revised paper scope — draft pending deterministic-manifest lock

Status: **scientific scope draft; do not use as final manuscript title until the deterministic V2 manifest passes**

## Recommended working title

**Study-Aware Validation and Domain Shift in Literature-Derived Machine Learning for Adsorption Capacity Prediction**

This is the preferred journal-style title because it states the contribution without overstating a model, material class, or optimization capability that the V2 evidence does not support.

## Alternative title

**When Random Splits Mislead: Provenance, Study Leakage and Domain Shift in Literature-Derived Adsorption Machine Learning**

This is more direct and potentially more memorable, but the preferred title above is more neutral for an engineering/environmental journal.

## Claims explicitly removed from the revised paper

The revised paper should **not** claim:

- a generally superior stacked ensemble;
- validated inverse design or engineering optimization;
- a universal adsorption-capacity upper bound of 624 mg/g;
- broad unseen-study generalization from row-random train/test scores;
- an agricultural-waste-only modelling corpus;
- reliable failure detection from simple Euclidean applicability distance;
- reliable uncertainty from RF–XGB disagreement;
- clean independent external validation unless primary-paper overlap is explicitly reconstructed.

## Revised central research question

> How much of the apparent predictive performance of literature-derived adsorption machine-learning models survives when data provenance, primary-study separation, precursor-domain heterogeneity, missing-feature transfer, and external domain shift are treated explicitly?

## Main contribution

The revised study should be framed as a **validation and reproducibility investigation** of adsorption-capacity machine learning built from heterogeneous literature data.

Its strongest contributions are:

1. reconstruction of primary-study provenance for a secondary compiled adsorption dataset whose project-level source labels collapsed many experiments into one source;
2. direct quantification of source/study overlap under conventional row-random validation;
3. comparison of row-random, proxy-grouped, and reconstructed primary-study-held-out performance using the original feature representation;
4. demonstration that the originally proposed Ridge stacking layer does not consistently outperform the strongest tree model under study-aware validation;
5. explicit precursor-domain reconstruction showing that the corpus is not agricultural-waste-only;
6. leave-one-primary-study-out evaluation within strict agricultural, broad biogenic-waste, and waste-derived-carbon subsets;
7. evaluation—and documented limits—of training-only applicability-distance and study-aware residual-interval diagnostics;
8. forensic reconstruction of the two legacy external-validation pipelines, including source/citation errors, QMAX target censoring, a Jaffari header bug, and pore-size/particle-size mismatch;
9. clean external-transfer tests showing modest rather than catastrophic but still insufficient generalization;
10. a deterministic result manifest linking every manuscript-eligible number to data, code, split, model, metric, unit and Git commit.

## Primary results to foreground

Assuming the deterministic manifest reproduces the current branch results, the paper should foreground the following result hierarchy.

### 1. Leakage/provenance result

The legacy-style random partition places **62 of 64 test rows (96.875%)** in source labels already represented in training. This demonstrates that the original random-split score cannot be interpreted as new-study transfer.

### 2. Reconstructed primary-study transfer

After primary provenance reconstruction, the strict confirmed-primary analysis contains approximately **238 rows across 11 primary studies**. Under complete primary-study holdout, RF, XGB and the unconstrained Ridge stack all have negative pooled R²; the stack does not demonstrate superiority.

This is the central validation result.

### 3. Domain restriction

The corpus contains non-agricultural material classes, including industrial mine coal and sludge-derived carbons.

- strict agricultural waste: 65 rows / 4 primary studies — too few studies and poor LOSO performance;
- broad biogenic waste: 92 rows / 6 primary studies — XGB is the strongest current restricted-domain diagnostic, pooled R² around 0.619, but a complete held-out study fails catastrophically;
- waste-derived carbon: 138 rows / 7 primary studies — RF/XGB around R² 0.49, with substantial study-level variability.

The restricted-domain results should therefore be presented as evidence that domain definition matters, not as a new universal predictor.

### 4. Reliability diagnostics

Correcting the applicability-distance scaling artifact shows that descriptor distance does not reliably rank absolute prediction error. Study-aware residual intervals become extremely wide and still fail to cover the catastrophic Alshabib study.

These negative results are important because they show why a seemingly reasonable post-hoc applicability or uncertainty layer does not automatically make inverse optimization safe.

### 5. External transfer

The legacy external results are not reproducible clean benchmarks. After correcting target censoring and feature-mapping defects:

- Liu et al. 2025: best tested result is full-corpus RF, R² around **0.223**;
- Jaffari et al. 2023: best tested result is waste-derived RF, R² around **0.181**.

These results are modest rather than catastrophically negative, but still do not support broad deployment.

## Proposed paper structure

### 1. Introduction

Focus on the widespread use of literature-compiled adsorption datasets and the risk that row-random validation confuses interpolation within published experimental systems with generalization to unseen studies.

The motivation should be methodological and engineering-relevant: adsorption ML is useful only if evaluation reflects the conditions under which the surrogate will actually be used.

### 2. Data provenance and corpus reconstruction

Cover:

- original project corpus;
- secondary-source lineage;
- primary-paper reconstruction method;
- confirmed/unresolved provenance coverage;
- precursor-domain classification;
- target/feature cleaning and removal-percent exclusion;
- why 624 mg/g is invalid as a universal bound.

A provenance-flow figure should replace the old inverse-design architecture as the first conceptual figure.

### 3. Validation methodology

Cover:

- original engineered feature representation;
- fold-safe preprocessing;
- random-row comparator;
- reconstructed primary-study holdout;
- domain-restricted LOSO;
- models LR/SVR/RF/XGB and historical Ridge stack comparator;
- equal-study and pooled metrics;
- corrected applicability-domain diagnostic;
- empirical study-aware residual intervals;
- external transfer methodology.

Make clear that model hyperparameters are not selected from the external target data.

### 4. Results

Recommended order:

1. provenance/leakage audit;
2. random-vs-primary-study performance collapse;
3. base-model vs stack comparison;
4. precursor-domain composition and restricted LOSO;
5. failure of distance/uncertainty reliability heuristics;
6. corrected external-transfer results.

This order tells one coherent scientific story rather than presenting disconnected model tables.

### 5. Discussion

Interpret the gap between row-random and study-held-out performance in terms of:

- repeated conditions from the same papers;
- material/process distributions specific to individual studies;
- source-compilation provenance loss;
- high-capacity target regimes concentrated in particular papers;
- missing variables and novel categorical levels across datasets;
- why high-dimensional literature datasets can have many rows but few truly independent experimental sources.

Discuss broad-biogenic XGB as an example of improved but still unstable transfer—not as the new final model.

### 6. Practical recommendations for adsorption ML

A concise checklist can be a genuine contribution:

- preserve primary-paper provenance at row level;
- split by primary study/material system before tuning;
- report study counts, not only row counts;
- show both pooled and equal-study errors;
- avoid target-derived predictors;
- never impose a universal physical ceiling without domain-specific evidence;
- audit feature equivalence before external mapping;
- treat application-domain and uncertainty claims as validation targets, not decorations;
- report external compilation overlap limitations.

### 7. Conclusion

The conclusion should state that row-random validation materially overstates transferable performance in this corpus, while study-aware validation exposes substantial domain dependence. It should emphasize reproducible evaluation practice rather than a failed optimizer.

## Figures to build after manifest lock

1. **Provenance reconstruction flow:** project source label → Iftikhar secondary compilation → reconstructed primary studies → confirmed/unresolved rows.
2. **Random vs primary-study validation:** compact performance comparison for RF/XGB/stack.
3. **Precursor-domain composition:** study counts and row counts by domain; avoid misleading row-only dominance.
4. **Per-study LOSO error:** broad-biogenic and/or waste-derived, highlighting but not hiding Alshabib.
5. **External transfer / feature-coverage panel:** Liu and Jaffari prediction metrics plus missing/novel feature burden.

Avoid decorative inverse-design diagrams unless clearly labelled as historical methodology removed from the validated contribution.

## Tables to build after manifest lock

1. **Dataset/provenance table:** rows, source studies, precursor scope, unresolved provenance.
2. **Validation table:** random-row comparator versus strict primary-study holdout.
3. **Domain-restricted LOSO table:** strict agricultural, broad biogenic and waste-derived, with study counts.
4. **External-transfer table:** Liu/Jaffari clean V2 metrics and feature-coverage caveats.

Applicability and uncertainty results may be a compact table or supplementary table if journal length is constrained.

## Recommended manuscript language

Use:

- “study-held-out performance” rather than “test accuracy” when discussing primary-study CV;
- “external transfer test” rather than “independent external validation” until source overlap is ruled out;
- “restricted-domain diagnostic” for broad-biogenic XGB;
- “model-predicted” only for historical optimizer demonstrations, if retained at all;
- “literature-derived adsorption data” rather than “agricultural-waste dataset” for the complete corpus.

Avoid:

- “robust inverse design”;
- “physically guaranteed predictions”;
- “generalizable” without specifying the held-out unit;
- “external validation successful” based solely on an R² value;
- “state of the art” unless directly benchmarked against comparable study-held-out literature models.

## Current scope decision

**Preferred pivot:** validation methodology + provenance + domain shift/generalization limits.

**Model role:** RF/XGB as comparative surrogates; Ridge stack as a negative comparator showing that added ensemble complexity did not solve study shift.

**Inverse design:** removed as a validated contribution.

**Agricultural-waste framing:** removed as the full-corpus scope.

**Lock condition:** convert this draft to the final scope only after the deterministic result-manifest workflow succeeds and its regenerated values agree with the Phase 1–7 evidence.