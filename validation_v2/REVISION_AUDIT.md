# ID-SEAD V2 Revision Audit

Status: **working audit — feature branch only**

This file separates scientific-validation issues from manuscript-production issues. A manuscript fix must not be used to conceal or substitute for an unresolved scientific issue.

## A. Scientific validation — blocking before journal resubmission

### A1. Study-level leakage risk — CONFIRMED / PRIMARY GATE FAILED

The dataset contains multiple observations from the same literature studies. The submitted/original implementation uses random row-level splitting, allowing closely related experiments to appear on both sides of a train/test split.

Confirmed evidence:
- legacy-style 80/20 split: **62/64 test rows (96.875%)** share a source label with training rows;
- the dominant 251-row block was incorrectly collapsed under `Moosavi et al., 2023` and is actually inherited from the Iftikhar et al. 2023 secondary dataset;
- primary-study reconstruction now covers **238/251 inherited rows (94.82%) across 11 primary studies**;
- strict primary-study holdout collapses the strong row-random results: RF R² = **-0.134**, XGB R² = **-0.189**, unconstrained Ridge stack R² = **-0.156**; LR is only slightly positive at **0.080** with RMSE ~691 mg/g.

**Disposition:** the submitted row-random performance cannot be presented as unseen-study generalization. The stack has failed the current predictive-superiority gate.

### A2. Fold-safe preprocessing — RESOLVED FOR CURRENT VALIDATION HARNESS

All imputation, scaling, encoding and train-derived transformations are fit only on the training portion of each fold.

Known original-code issue: class-conditioned test imputation used the training-frame `material_class` index when mapping medians to test rows. That was corrected in V2.

Primary-study holdout exposed a second hidden edge case: a numerical feature can be entirely missing from all training studies in a fold. V2 now marks such a feature inactive and assigns a neutral constant in both train and held-out data; held-out values are never used to create an imputation statistic or activate a feature absent from training.

### A3. Target-proxy leakage — RESOLVED FOR PRIMARY V2 FEATURE SET

`removal_percent` can be mathematically linked to adsorption capacity (`qe`) through experimental mass-balance relationships when concentration, volume and dose are known. Using it as a predictor risks encoding the target.

**V2 action implemented:** `removal_percent` is excluded from the primary predictive feature set. Any later sensitivity analysis including it must be clearly labelled non-primary and justified.

### A4. External validation collapse — BLOCKING

Existing notebook outputs show severe performance collapse on two independent datasets, with strongly negative R² values and high feasibility-violation rates.

**V2 action:** retain these failures as evidence. Diagnose:
- feature coverage mismatch;
- material/pollutant domain shift;
- missing-variable imputation burden;
- target/range shift;
- distance from the training applicability domain.

Do not describe external validation as successful unless revised results support that claim.

### A5. Constraint-vs-accuracy trade-off — BLOCKING / LEGACY QMAX INVALID

The constraint-aware model currently trades predictive accuracy for reduced physical-bound violations, but the underlying universal `Q_MAX = 624 mg/g` is contradicted by the corpus: 115/322 usable rows exceed 624 mg/g and the observed maximum is 2239 mg/g.

**Disposition:** do not reintroduce the legacy constraint layer until the modelling domain is narrowed and any physical limits are derived conditionally for that domain.

### A6. Inverse-design claim strength — BLOCKING

An optimiser finding an input at which the surrogate predicts the requested target demonstrates numerical inversion of the surrogate, not experimental attainment of that adsorption capacity.

Primary-study holdout now adds a stronger blocker: the surrogate itself does not generalize reliably to unseen studies over the reconstructed heterogeneous domain.

**V2 action required before any inverse-design claim:**
- define a defensible applicability domain;
- quantify predictive uncertainty;
- penalise out-of-domain candidates;
- use scaled/nearest-neighbour, Mahalanobis or density-based distance rather than unscaled Euclidean distance across incompatible units;
- label outputs as model-predicted candidate conditions rather than validated optima;
- separate local surrogate stability from experimental robustness.

### A7. Corpus scope / “agricultural waste” claim — BLOCKING

Primary-source reconstruction shows that the training corpus is not exclusively agricultural-waste adsorbents. Confirmed examples include:
- Maghara industrial mine coal (`MC350`–`MC600`);
- textile sludge;
- wastewater-sludge char;
- commercial/mixed activated-carbon families including coal-based material;
- refined white sugar;
- crab shell;
- agricultural residues and agro-industrial wastes.

**Disposition:** the submitted title/domain phrase “using agricultural waste adsorbents” is materially broader/narrower than the actual corpus composition. A precursor-domain audit is required. Domain-restricted modelling may proceed only if enough independent primary studies remain for meaningful study-held-out validation.

## B. Manuscript ↔ code reconciliation — BLOCKING

The submitted manuscript and current notebooks appear to contain values from different pipeline stages.

**Required:**
1. generate Tables I–III directly from one deterministic validation pipeline;
2. create a machine-readable result manifest (metric, value, unit, dataset/split, code version);
3. verify every manuscript number against that manifest;
4. specifically investigate the submitted Table I ID-SEAD RMSE value reported as approximately 369.48 mg/g in the manuscript review notes;
5. prohibit hand-edited table numbers in the revised manuscript.

The final manuscript tables must use the revised study-aware results, not the legacy random-split values, unless the latter are explicitly labelled as a leakage-prone diagnostic comparator.

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

- [x] zero study overlap in current primary-study grouped folds;
- [x] current validation preprocessing proven fold-safe, including all-missing training-fold handling;
- [x] removal-percent target-proxy issue resolved for primary feature set;
- [x] grouped baseline metrics generated;
- [x] original feature-engineered model family rerun on primary-study grouped folds;
- [x] provenance reconstructed for 238/251 inherited rows across 11 primary studies;
- [ ] remaining `CS` primary provenance resolved or explicitly excluded permanently;
- [ ] precursor/domain composition audited and manuscript scope corrected;
- [ ] domain-restricted primary-study validation run if enough independent studies remain;
- [ ] grouped uncertainty intervals generated for the final chosen domain/model;
- [ ] external validation rerun and domain-shift diagnostics documented;
- [ ] inverse-design applicability-domain/uncertainty layer implemented, if inverse design remains in scope;
- [ ] deterministic manuscript result manifest generated;
- [ ] Tables I–III reconciled to pipeline outputs;
- [ ] manuscript production defects repaired after result lock.

## F. Current scientific direction

The submitted framing has **not** passed V2 validation. In particular:

- stacking is not supported as a superior cross-study predictor;
- the heterogeneous full corpus does not support broad unseen-study deployment;
- the agricultural-waste-only title is not supported by confirmed provenance;
- the legacy universal QMAX and inverse-design claims cannot currently be reinstated.

The next decision depends on the precursor/domain audit. If a coherent agricultural/biomass-waste subset contains enough independent studies and shows credible primary-study transfer, the paper can narrow to that domain. If it does not, the stronger contribution is likely an applicability-domain/data-leakage/domain-shift study rather than a universal inverse-design model.
