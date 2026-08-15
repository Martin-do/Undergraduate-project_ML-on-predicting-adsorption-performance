# ID-SEAD / Adsorption ML — Final V2 Scientific Audit

Status: **scientific validation phase complete; manuscript rewrite not yet performed**

Branch: `feature/study-aware-validation-v2`

The original `main` branch and submitted-paper history remain untouched.

## Executive disposition

The submitted paper's central framing does **not** survive rigorous V2 validation.

### Rejected scientific claims

- **Stacked ensemble superiority:** not supported under reconstructed primary-study validation.
- **Validated inverse design:** rejected; reliability/applicability/uncertainty gates fail.
- **Universal QMAX = 624 mg/g:** contradicted by the corpus.
- **Agricultural-waste-only scope:** contradicted by primary-source reconstruction.
- **Broad unseen-study generalization from row-random results:** invalid because the random split is heavily source-overlapping.

### Revised defensible contribution

The strongest paper is now a study of:

**provenance reconstruction, study-aware validation, domain shift, external transfer and generalization limits in literature-derived adsorption machine learning.**

Locked working title:

> **Study-Aware Validation and Domain Shift in Literature-Derived Machine Learning for Adsorption Capacity Prediction**

See `REVISED_PAPER_SCOPE.md`.

---

## Gate 1 — Leakage / source overlap

**PASS as an audit; original validation interpretation FAILS.**

Legacy-style random 80/20 partition:

- test rows: 64;
- test rows whose source label also occurs in training: **62**;
- overlap fraction: **96.875%**.

Therefore row-random performance is an interpolation comparator, not evidence of unseen-study transfer.

---

## Gate 2 — Physical-bound audit

**Legacy universal bound FAILS.**

- legacy QMAX: 624 mg/g;
- usable project rows: 322;
- observed maximum: **2239 mg/g**;
- rows above 624: **115 / 322 = 35.714%**.

The universal QMAX/constraint layer is retired from the revised paper.

---

## Gate 3 — Primary provenance reconstruction

**PASS at sufficient coverage for strict inherited-block validation.**

The 251-row block labelled `Moosavi et al., 2023` is treated as secondary-compilation inheritance from Iftikhar et al. 2023 rather than one primary experiment.

Confirmed primary provenance:

- **238 / 251 rows = 94.82%**;
- **11 primary studies**.

Unresolved:

- `CS`: **13 rows**.

Final policy: `CS` remains unresolved and is permanently excluded from primary-study claims unless future primary-source evidence establishes its provenance. No guessed study ID is permitted.

---

## Gate 4 — Fold-safe feature-parity implementation

**PASS.**

Corrections include:

- removal-percent excluded from predictors because of target-proxy/mass-balance leakage risk;
- test group-median imputation corrected to use test material class;
- preprocessing fitted within training folds only;
- when a feature is completely unobserved in a training fold, it is marked inactive and neutralized in both training and held-out data rather than borrowing held-out information;
- original engineered feature representation retained for forensic comparability.

---

## Gate 5 — Strict primary-study holdout

**Full heterogeneous-domain predictive claim FAILS.**

Analysis set:

- 238 rows;
- 11 primary studies.

Pooled results:

| Model | R² | RMSE (mg/g) | MAE (mg/g) |
|---|---:|---:|---:|
| LR | 0.080 | 691.39 | 529.41 |
| SVR | -0.988 | 1016.37 | 884.40 |
| RF | -0.134 | 767.73 | 550.29 |
| XGB | -0.189 | 786.20 | 547.20 |
| Ridge stack | -0.156 | 775.18 | 642.46 |

The historical Ridge stack does not outperform the strongest base model in a way that supports its original novelty claim.

---

## Gate 6 — Precursor-domain reconstruction

**PASS as corpus audit; original agricultural-waste scope FAILS.**

Confirmed corpus includes agricultural/agro-industrial residues but also industrial mine coal, textile/wastewater sludge, commercial/mixed activated carbons, white sugar and crab shell.

Predeclared candidate scopes:

- strict agricultural waste: **65 rows / 4 studies**;
- broad biogenic waste: **92 rows / 6 studies**;
- waste-derived carbon: **138 rows / 7 studies**.

Strict agriculture is both statistically thin and predictively poor under LOSO.

---

## Gate 7 — Domain-restricted leave-one-study-out validation

**Mixed diagnostic result; no universal model rescue.**

### Strict agricultural waste

- RF R² ≈ **-1.750**;
- XGB R² ≈ **-2.038**.

**FAIL.**

### Broad biogenic waste

- RF R² ≈ **0.276**;
- XGB R² ≈ **0.619**;
- Ridge stack R² ≈ **-2.286**.

This is the strongest restricted internal result, but one complete held-out study (Alshabib) has XGB MAE ≈ **1533 mg/g**.

**PROVISIONAL DIAGNOSTIC ONLY.**

### Waste-derived carbon

- RF R² ≈ **0.487**;
- XGB R² ≈ **0.495**;
- Ridge stack R² ≈ **0.225**.

**PROVISIONAL DIAGNOSTIC ONLY.**

---

## Gate 8 — Applicability-domain distance

**FAIL as a reliability/deployment gate.**

The initial distance implementation exposed a scaling artifact when a continuous variable was constant throughout a training fold. This was corrected by excluding fold-constant/near-constant continuous variables from distance.

After correction:

- broad-biogenic XGB distance-vs-error Spearman ≈ **-0.068**;
- waste-derived XGB ≈ **-0.283**.

Support status does not reliably distinguish catastrophic from successful held-out studies and can worsen filtered performance in the waste-derived domain.

Distance may remain as a domain-shift explanatory diagnostic only.

---

## Gate 9 — Study-aware empirical uncertainty

**FAIL as a reliability/deployment gate.**

Calibration uses only outer-training studies with inner leave-one-primary-study-out residuals and equal total calibration weight per study. No formal conformal guarantee is claimed.

Broad-biogenic fixed residual intervals:

- nominal 90% row coverage ≈ **97.83%**;
- equal-study mean coverage ≈ **83.33%**;
- mean width ≈ **2958 mg/g**;
- Alshabib remains **0% covered**.

Waste-derived fixed residual intervals:

- nominal 90% row coverage ≈ **98.55%**;
- equal-study mean coverage ≈ **85.71%**;
- mean width ≈ **2920 mg/g**;
- Alshabib remains **0% covered**.

RF–XGB disagreement scaling becomes even wider and still misses the catastrophic failure. Two models can agree while both are badly wrong.

---

## Gate 10 — Inverse-design disposition

**FINAL FAIL / REMOVED FROM REVISED CLAIM.**

The optimizer can numerically invert the surrogate, but the surrogate has not demonstrated sufficient unseen-study reliability and the tested applicability/uncertainty safeguards do not provide a credible engineering acceptance rule.

The historical optimizer may remain in the repository as archival/numerical work. It must not be presented as validated design optimization in the revised paper.

---

## Gate 11 — External-validation source reconstruction

**PASS as forensic audit.**

Corrections:

- legacy `Shen et al. 2024` dataset is Liu et al. 2025, Carbon Research, DOI `10.1007/s44246-025-00213-9`;
- Jaffari DOI corrected to `10.1016/j.cej.2023.143073`;
- project-QMAX target censoring removed;
- Jaffari pyrolysis-temperature trailing-whitespace bug corrected;
- `Average pore size` is no longer misused as adsorbent particle size;
- unavailable external fields remain missing and are handled by training-fitted preprocessing.

The legacy Liu saved N=525 is not reproducible from the currently committed workbook + notebook source. Exact replay gives **548** rows under the notebook's own 624 mg/g filter. N=525 is therefore a stale historical execution artifact.

---

## Gate 12 — Clean external transfer

**PASS as transfer test; broad deployment claim still FAILS.**

### Liu et al. 2025, N=578

Best tested result:

- full-corpus RF R² ≈ **0.223**;
- RMSE ≈ **167.38 mg/g**;
- MAE ≈ **106.16 mg/g**.

### Jaffari et al. 2023, N=3757

Best tested result:

- waste-derived RF R² ≈ **0.181**;
- RMSE ≈ **63.35 mg/g**;
- MAE ≈ **46.28 mg/g**.

The old catastrophic negative external R² values are superseded as clean benchmarks because their pipeline contained multiple defects. The corrected results are modest, not deployment-grade.

External source-disjointness is not claimed as proven because complete primary-paper overlap reconstruction is unavailable.

---

## Gate 13 — Deterministic result manifest

**PASS.**

Successful CI run: `31880398376`

Scientific commit represented by the first locked manifest: `33def2c7ba90571314b8ec3574dcfc98a61e26b8`

Manifest artifact:

- total result rows: **331**;
- manuscript-eligible rows: **279**;
- input SHA-256 hashes recorded for the project CSV, Liu workbook, Jaffari workbook, primary-study map and precursor-domain map;
- historical/superseded values remain machine-visible but manuscript-ineligible;
- inverse-design and universal-QMAX outputs are intentionally absent from eligible predictive results.

Generated files:

- `result_manifest_v2.csv`;
- `result_manifest_v2.json`;
- `result_manifest_v2_metadata.json`;
- `RESULT_MANIFEST_V2_SUMMARY.md`.

Rule for manuscript rewrite: **no numerical result is to be typed from memory or manually maintained; manuscript tables/figures must be generated from the manifest/evidence outputs.**

---

# Final paper decision

## Keep

- provenance reconstruction;
- leakage audit;
- study-aware validation;
- original-feature model comparison;
- domain-restricted LOSO;
- applicability/uncertainty negative findings;
- corrected external transfer;
- practical methodological recommendations for literature-derived adsorption ML.

## Remove or demote to historical context

- ID-SEAD as a superior algorithm name;
- stacked-ensemble novelty;
- universal constraint layer;
- inverse-design optimization claim;
- agricultural-waste-only full-corpus framing;
- legacy external-validation numbers as primary evidence.

## Manuscript status

**Scientific evidence is ready for manuscript reconstruction.**

The next phase is editorial/communication work:

1. build revised tables and figures directly from the deterministic evidence;
2. rewrite the paper around the locked scope;
3. repair equations/figure rendering/section hierarchy/reference errors;
4. select a journal aligned to environmental/process-engineering ML methodology;
5. perform final manuscript ↔ manifest reconciliation before submission.
