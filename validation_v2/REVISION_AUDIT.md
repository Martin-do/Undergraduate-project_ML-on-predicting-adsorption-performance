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

### A4. External validation collapse — BLOCKING / NEXT REPRODUCIBILITY GATE

Existing notebook outputs show severe performance collapse on two independent datasets, with strongly negative R² values and high feasibility-violation rates.

Legacy evidence to preserve:
- Shen dataset: R² ≈ **-18.786**, RMSE ≈ **696.09 mg/g**, legacy feasibility violation ≈ **45.71%**;
- Jaffari dataset: R² ≈ **-16.097**, RMSE ≈ **303.55 mg/g**, legacy feasibility violation ≈ **61.75%**.

**V2 action now required:** reproduce the external datasets and rerun them through the clean, unconstrained V2 predictive pipeline where source variables permit. Diagnose:
- feature coverage mismatch;
- material/pollutant domain shift;
- missing-variable imputation burden;
- target/range shift;
- categorical novelty;
- distance from the training applicability domain.

Do not describe external validation as successful unless revised results support that claim. The old failures are evidence and must not be removed if the new pipeline also performs poorly.

### A5. Constraint-vs-accuracy trade-off — BLOCKING / LEGACY QMAX INVALID

The constraint-aware model currently trades predictive accuracy for reduced physical-bound violations, but the underlying universal `Q_MAX = 624 mg/g` is contradicted by the corpus: 115/322 usable rows exceed 624 mg/g and the observed maximum is 2239 mg/g.

**Disposition:** the legacy universal constraint layer is retired from the revised scientific framing. Any future physical limit would need to be conditional on a separately justified material/pollutant domain; none is currently established strongly enough to support the submitted inverse-design claim.

### A6. Inverse-design claim — FAILED / ABANDONED FOR REVISED PAPER

An optimiser finding an input at which the surrogate predicts the requested target demonstrates numerical inversion of the surrogate, not experimental attainment of that adsorption capacity.

The sequential V2 reliability gates now provide enough evidence to make a final disposition:

- primary-study holdout shows poor full-domain transfer;
- stacking is not superior to the best tree model;
- the legacy universal QMAX is contradicted by the observed corpus;
- strict agricultural-waste LOSO fails;
- broader biogenic/waste-derived domains improve average prediction but retain complete-study failures;
- corrected cross-study distance does not reliably rank prediction error;
- study-aware residual intervals are extremely wide and still miss the catastrophic Alshabib study;
- RF and XGB can closely agree while both are wrong by >1500 mg/g.

**Disposition:** inverse design is **abandoned as a validated engineering contribution for the revised paper**. The historical optimizer may remain in the repository as a numerical demonstration, but it must not be presented as a validated design/optimization result.

### A7. Corpus scope / “agricultural waste” claim — RESOLVED AS A DEFECT / ORIGINAL SCOPE FAILS

Primary-source reconstruction shows that the training corpus is not exclusively agricultural-waste adsorbents. Confirmed examples include:
- Maghara industrial mine coal (`MC350`–`MC600`);
- textile sludge;
- wastewater-sludge char;
- commercial/mixed activated-carbon families including coal-based material;
- refined white sugar;
- crab shell;
- agricultural residues and agro-industrial wastes.

The explicit precursor audit finds:
- strict agricultural waste: **65 rows / 4 primary studies**;
- broad biogenic waste: **92 rows / 6 primary studies**;
- waste-derived carbon: **138 rows / 7 primary studies**.

Strict agricultural LOSO fails badly (RF R² ~-1.75; XGB ~-2.04), so filtering the corpus does not rescue the submitted title. Broad-biogenic XGB is the most encouraging restricted result (R² ~0.619 across six studies), but one complete held-out study fails catastrophically.

**Disposition:** do not retain “agricultural waste adsorbents” as the general predictive scope of the submitted paper. Any new scope must follow the validated evidence rather than the original title.

### A8. Corrected distance/applicability-domain audit — COMPLETED / FAIL AS RELIABILITY GATE

The first AD implementation exposed giant distances for Li/Gao because `contact_time_min` was constant in their training folds. A constant training feature has no empirical variance; retaining its held-out difference mixed original units into the standardized Euclidean distance.

V2 corrected the metric by excluding fold-constant/near-constant continuous variables from distance. After correction:

- broad-biogenic XGB distance-vs-error Spearman ≈ **-0.068**;
- waste-derived-carbon XGB distance-vs-error Spearman ≈ **-0.283**;
- broad-biogenic strict-q95 retained ~61.96% of rows and had aggregate R² ~0.694, but rejected low-error Archin/Ravenni studies as unsupported;
- waste-derived strict-q95 retained ~64.49% and **worsened** XGB error;
- catastrophic Alshabib is considered supported in the broader waste-derived domain.

Feature decomposition confirms genuine study-specific covariate shifts (pyrolysis temperature, particle size, pH, temperature, pore/surface descriptors), but no universal distance direction predicts error reliably.

**Disposition:** retain corrected distance only as a domain-shift diagnostic, not a deployment/inverse-design acceptance rule.

### A9. Study-aware uncertainty — COMPLETED / FAIL AS RELIABILITY GATE

V2 implemented empirical group-aware residual intervals using only outer-training studies for calibration, with inner leave-one-primary-study-out residuals and equal total calibration weight per study. No formal conformal guarantee is claimed because the domains contain only 6–7 heterogeneous studies and within-study rows are dependent.

Broad-biogenic fixed intervals:
- nominal 90%: row coverage **97.83%**, equal-study coverage **83.33%**, mean width **~2958 mg/g**;
- nominal 95%: row coverage **97.83%**, equal-study coverage **83.33%**, mean width **~3038 mg/g**;
- Alshabib remains **0% covered** despite the extreme widths.

Waste-derived fixed intervals:
- nominal 90%: row coverage **98.55%**, equal-study coverage **85.71%**, mean width **~2920 mg/g**;
- nominal 95%: row coverage **98.55%**, equal-study coverage **85.71%**, mean width **~3041 mg/g**;
- Alshabib again remains **0% covered**.

RF–XGB-disagreement scaling is worse: broad-biogenic mean interval width grows to ~13,000 mg/g while Alshabib remains uncovered. In that failure fold RF and XGB disagree by only ~5.5 mg/g while both are wrong by ~1533 mg/g.

**Disposition:** the available study-aware uncertainty signals are too uninformative for engineering deployment or inverse optimization. This closes the inverse-design rescue attempt.

## B. Manuscript ↔ code reconciliation — BLOCKING

The submitted manuscript and current notebooks appear to contain values from different pipeline stages.

**Required:**
1. generate the revised result tables directly from one deterministic validation pipeline;
2. create a machine-readable result manifest (metric, value, unit, dataset/split, code version);
3. verify every manuscript number against that manifest;
4. specifically investigate the submitted Table I ID-SEAD RMSE value reported as approximately 369.48 mg/g in the manuscript review notes;
5. prohibit hand-edited table numbers in the revised manuscript.

The final manuscript must use revised study-aware results. Legacy random-split values may appear only when explicitly labelled as leakage-prone diagnostic comparators.

## C. IEEM manuscript-production defects — CONFIRMED/REPORTED

These issues do not determine scientific validity but must be fixed in any revised paper:

- Figure 1 legend/boxes overlap the bottom output banner/text.
- Equation (4), the inverse-design objective, reportedly renders blank in the submitted document.
- inconsistent section hierarchy/numbering;
- missing mathematical membership symbols (`∈`) in some ranges;
- caption/layout defects around Figure 1;
- submitted conference layout reportedly not in standard IEEE double-column form;
- table/text justification and general IEEE formatting need correction.

These should be repaired only after the revised scientific results are locked.

## D. Reviewer disposition

### Reviewer 1

**Disposition:** substantially valid. Formatting/presentation issues are real and fixable. The request for clearer method description is also valid.

### Reviewer 2

**Disposition:** scope objection substantially valid; discipline label is imprecise. The work is better characterised as environmental/chemical/process engineering + machine learning than mechanical engineering. IEEM is not the natural primary venue for the current application framing.

### Reviewer 4

**Disposition:** mixed/weakly supported. “No related references” conflicts with the submitted paper's reference list; “does not relate to engineering” is not a defensible description of adsorption/process modelling. However, “basic” cannot simply be dismissed by listing sophisticated components: the validation design must demonstrate a robust contribution.

## E. Acceptance gates for V2

The revised scientific paper should not be treated as submission-ready until all remaining gates are satisfied:

- [x] zero study overlap in current primary-study grouped folds;
- [x] current validation preprocessing proven fold-safe, including all-missing training-fold handling;
- [x] removal-percent target-proxy issue resolved for primary feature set;
- [x] grouped baseline metrics generated;
- [x] original feature-engineered model family rerun on primary-study grouped folds;
- [x] provenance reconstructed for 238/251 inherited rows across 11 primary studies;
- [ ] remaining `CS` primary provenance resolved or explicitly excluded permanently;
- [x] precursor/domain composition audited;
- [x] strict-agricultural scope tested and rejected as a general predictive framing;
- [x] broad-biogenic and waste-derived study-held-out validation generated;
- [x] corrected training-only cross-study distance diagnostic implemented;
- [x] feature-level distance-driver audit completed;
- [x] distance-only applicability gate shown insufficient;
- [x] group-aware residual intervals generated and evaluated;
- [x] uncertainty gate shown insufficient;
- [x] inverse-design framing explicitly abandoned for revised paper;
- [ ] external validation rerun and domain-shift diagnostics documented;
- [ ] deterministic manuscript result manifest generated;
- [ ] revised scientific scope/title locked;
- [ ] Tables/results reconciled to pipeline outputs;
- [ ] manuscript production defects repaired after result lock.

## F. Current scientific direction

The submitted framing has **not** passed V2 validation, and the attempt to rescue it as a reliable inverse-design method is closed.

The strongest defensible revised contribution is now a study on **provenance, study leakage, domain shift and applicability limits in literature-derived adsorption machine learning**. The model comparison becomes supporting evidence rather than the novelty claim.

Current evidence supports these decisions:

- stacking should not remain the title or central novelty;
- inverse design should not remain a validated engineering claim;
- the heterogeneous full corpus does not support broad unseen-study deployment;
- the agricultural-waste-only title is not supported and the strict agricultural subset performs poorly;
- broad-biogenic XGB (LOSO R² ~0.619 across six studies) is an informative restricted-domain diagnostic, not evidence of universal reliability;
- simple distance and RF–XGB disagreement do not provide dependable failure detection;
- the legacy universal QMAX cannot be reinstated.

**Next work:** reproduce the external datasets/failures under V2, document the corresponding domain shift, build a deterministic result manifest, and then lock the revised paper title/scope before rewriting the manuscript.
