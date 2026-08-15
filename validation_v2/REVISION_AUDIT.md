# ID-SEAD V2 Revision Audit

Status: **working audit — feature branch only**

This file separates scientific-validation issues from manuscript-production issues. A manuscript fix must not be used to conceal or substitute for an unresolved scientific issue.

## A. Scientific validation — blocking before journal resubmission

### A1. Study-level leakage risk — BLOCKING

The dataset contains multiple observations from the same literature source (`source_link`). The submitted/original implementation uses random row-level splitting. Closely related experiments from one source can therefore occur on both sides of a train/test split.

**V2 action:** compare row-wise K-fold against GroupKFold keyed by normalized `source_link`. No study may appear in both train and validation within a grouped fold.

**Evidence required:**
- source-overlap audit for the legacy-style split;
- random-CV vs grouped-CV metrics for identical model families;
- per-study out-of-fold predictions;
- study-cluster bootstrap confidence intervals.

### A2. Fold-safe preprocessing — BLOCKING

All imputation, scaling, encoding and train-derived transformations must be fit only on the training portion of each fold.

Known original-code issue: class-conditioned test imputation used the training-frame `material_class` index when mapping medians to test rows. That is not the intended test-row group mapping.

**V2 action:** use sklearn pipelines for the baseline harness, then migrate original feature engineering into explicitly fitted train-fold transformers.

### A3. Target-proxy leakage — BLOCKING

`removal_percent` can be mathematically linked to adsorption capacity (`qe`) through experimental mass-balance relationships when concentration, volume and dose are known. Using it as a predictor risks encoding the target.

**V2 action:** exclude `removal_percent` from the primary predictive feature set. Any later sensitivity analysis including it must be clearly labelled non-primary and justified.

### A4. External validation collapse — BLOCKING

Existing notebook outputs show severe performance collapse on two independent datasets, with strongly negative R² values and high feasibility-violation rates.

**V2 action:** retain these failures as evidence. Diagnose:
- feature coverage mismatch;
- material/pollutant domain shift;
- missing-variable imputation burden;
- target/range shift;
- distance from the training applicability domain.

Do not describe external validation as successful unless revised results support that claim.

### A5. Constraint-vs-accuracy trade-off — MAJOR

The constraint-aware model currently trades predictive accuracy for reduced physical-bound violations. The scientific contribution should be expressed as a multi-objective trade-off unless future results establish predictive dominance.

**V2 action:** report predictive error, violation rate and perturbation stability jointly; avoid a generic "superior model" claim.

### A6. Inverse-design claim strength — BLOCKING

An optimiser finding an input at which the surrogate predicts the requested target demonstrates numerical inversion of the surrogate, not experimental attainment of that adsorption capacity.

**V2 action:**
- label outputs as candidate operating conditions;
- quantify predictive uncertainty;
- penalise out-of-domain candidates;
- use scaled/applicability-domain distance rather than unscaled Euclidean distance across incompatible units;
- separate local surrogate stability from experimental robustness.

## B. Manuscript ↔ code reconciliation — BLOCKING

The submitted manuscript and current notebooks appear to contain values from different pipeline stages.

**Required:**
1. generate Tables I–III directly from one deterministic validation pipeline;
2. create a machine-readable result manifest (metric, value, unit, dataset/split, code version);
3. verify every manuscript number against that manifest;
4. specifically investigate the submitted Table I ID-SEAD RMSE value reported as approximately 369.48 mg/g in the manuscript review notes;
5. prohibit hand-edited table numbers in the revised manuscript.

## C. IEEM manuscript-production defects — CONFIRMED/REPORTED

These issues do not determine scientific validity but must be fixed in any revised paper:

- Figure 1 legend/boxes overlap the bottom output banner/text.
- Equation (4), the inverse-design objective, reportedly renders blank in the submitted document.
- inconsistent section hierarchy/numbering;
- missing mathematical membership symbols (`∈`) in some ranges;
- caption/layout defects around Figure 1;
- submitted conference layout reportedly not in standard IEEE double-column form;
- table/text justification and general IEEE formatting need correction.

These should be repaired only after the new scientific results are locked.

## D. Reviewer disposition

### Reviewer 1

**Disposition:** substantially valid. Formatting/presentation issues are real and fixable. The request for clearer method description is also valid.

### Reviewer 2

**Disposition:** scope objection substantially valid; discipline label is imprecise. The work is better characterised as environmental/chemical/process engineering + machine learning than mechanical engineering. IEEM is not the natural primary venue for the current application framing.

### Reviewer 4

**Disposition:** mixed/weakly supported. "No related references" conflicts with the submitted paper's reference list; "does not relate to engineering" is not a defensible description of adsorption/process optimisation. However, "basic" cannot simply be dismissed by listing sophisticated components: the validation design must demonstrate a robust contribution.

## E. Acceptance gates for V2

The revised scientific paper should not be treated as submission-ready until all gates below are satisfied:

- [ ] zero study overlap in grouped folds;
- [ ] all preprocessing proven fold-safe;
- [ ] removal-percent target-proxy issue resolved;
- [ ] grouped baseline metrics generated;
- [ ] original ID-SEAD model rerun on identical grouped folds;
- [ ] grouped uncertainty intervals generated;
- [ ] external validation rerun and domain-shift diagnostics documented;
- [ ] inverse-design applicability-domain/uncertainty layer implemented;
- [ ] deterministic manuscript result manifest generated;
- [ ] Tables I–III reconciled to pipeline outputs;
- [ ] manuscript production defects repaired after result lock.
