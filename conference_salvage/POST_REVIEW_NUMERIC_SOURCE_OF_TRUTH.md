# ID-SEAD Conference Salvage — Post-Review Numerical Source of Truth

Status: **authoritative conference evidence after independent-review revision gate**  
Date: 2026-08-30  
Branch: `conference/id-sead-salvage`

This document supersedes any conference narrative that interpreted the full-engineered study-aware collapse as representation-independent. It does **not** reinstate the legacy ID-SEAD inverse-design/deployment claim.

## 1. Evidence hierarchy

1. **Legacy ID-SEAD** — historical architecture and manuscript-era outputs only; governed by `NUMERICAL_LINEAGE_AUDIT.md`.
2. **Frozen V2.1 baseline** — corrected full-engineered representation; reproducible under `conference_salvage/reproducibility/`.
3. **Independent-review revision gate** — supplemental, explicitly post-review sensitivity analysis prompted by an external reviewer. It tests cluster imbalance, missingness and feature-representation dependence.
4. **Inverse-design disposition** — remains a separate reliability decision. Improved forward-prediction transfer does not automatically validate inverse design.

## 2. Independent review checkpoint

The independent reviewer:
- independently recovered the 322 / 307 / 29 / 273 / 24 corpus counts;
- independently confirmed that many valid target values exceed the retired `Q_MAX=624 mg/g`;
- independently identified `removal_percent` as a strong target-proxy channel;
- independently reproduced the qualitative row-random versus study-grouped performance gap using a different Random Forest pipeline;
- rated the supplied work **defensible with major revisions**, with the material/context feature-representation question and reproducibility-packaging gap as the two highest-priority items.

The reviewer package omitted several current `validation_v2/*.py` files. That was a handoff-packaging defect, not absence of modelling code in the repository. The corrected reviewer pack must include the full submission-facing source path.

## 3. Strict-comparable corpus

- usable-target corpus: **322 rows**;
- primary-confirmed: **307 rows / 29 primary studies**;
- strict comparable: **273 rows / 24 primary studies**;
- grouping variable: `primary_study_id_v21`.

### Study-size imbalance

| Diagnostic | Value |
|---|---:|
| Singleton studies | **8 / 24** |
| Studies with n >= 5 | **12 / 24** |
| Studies with n >= 10 | **7 / 24** |
| Largest study | **67 rows** |
| Median rows per study | **5** |
| Top five studies | **196 / 273 rows = 71.79%** |
| Kish effective study count by row weight | **7.62** |
| Entropy effective study count by row weight | **11.07** |

The external review stated 10 singleton studies; direct reconstruction gives **8**. The substantive imbalance concern remains valid.

## 4. Missingness in the strict 273-row set

After applying the same numeric parser used by the corrected pipeline:

| Predictor | Missing rows | Missing % |
|---|---:|---:|
| `dose_gL` | **168** | **61.54%** |
| `contact_time_min` | **104** | **38.10%** |
| `surface_area_m2g` | 29 | 10.62% |
| `pore_volume_cm3g` | 29 | 10.62% |
| `initial_concentration_mgL` | 14 | 5.13% |
| `particle_size_mm` | 14 | 5.13% |
| `ph` | 13 | 4.76% |
| `temperature_c` | 5 | 1.83% |

All imputation remains training-fold-local. These rates must be disclosed in the conference paper.

## 5. Full-engineered baseline remains reproducible

This is the original corrected V2.1 feature-parity representation, including engineered material/pollutant/context categories derived from raw descriptors.

| Model | Row-random 5-fold R² | Primary-study-grouped 5-fold R² | Strict LOSO R² |
|---|---:|---:|---:|
| RF | **0.9042** | **0.0265** | **0.0085** |
| XGB | **0.8936** | **0.1929** | **0.1624** |
| Unconstrained Ridge stack | **0.9027** | **-0.5566** | not primary LOSO model |

These numbers are reproducible, but their interpretation has changed after the review-triggered ablation below.

### Fold dispersion warning

For the full engineered representation, the grouped five-fold **per-fold R²** is extremely unstable because held-out study mixtures have very different target distributions:

- RF mean fold R² = **-6.445**, SD **8.474**, range **-20.593 to 0.458**;
- XGB mean fold R² = **-4.286**, SD **5.474**, range **-13.536 to 0.436**.

Therefore the pooled grouped R² remains useful as a matched whole-population summary, but it must not be described as a stable per-fold estimate. Report per-fold MAE/RMSE or dispersion alongside it.

## 6. Reviewer-triggered feature-representation ablation — central new finding

This analysis was **not predeclared before the independent review**. It is a reviewer-requested sensitivity analysis and must be labelled as such.

Three representations were compared on the same strict 273 rows with the same fold definitions:

1. **Full engineered** — existing V2.1 feature-parity representation.
2. **No identity-adjacent categories** — removes encoded `base_material`, `material_class`, `pollutant_class` and `activation_agent` categories while retaining measured/process variables and binary treatment indicators.
3. **Physical numeric only** — retains measured/derived numeric variables only.

### Matched 5-fold results

| Representation | Model | Row-random R² | Study-grouped R² |
|---|---|---:|---:|
| Full engineered | RF | 0.9042 | 0.0265 |
| Full engineered | XGB | 0.8936 | 0.1929 |
| No identity-adjacent categories | RF | **0.8250** | **0.6370** |
| No identity-adjacent categories | XGB | **0.8214** | **0.4807** |
| Physical numeric only | RF | **0.8252** | **0.5796** |
| Physical numeric only | XGB | **0.8201** | **0.4964** |

### Strict LOSO results

| Representation | Model | LOSO R² | RMSE (mg/g) | MAE (mg/g) |
|---|---|---:|---:|---:|
| Full engineered | RF | 0.0085 | 700.37 | 476.24 |
| Full engineered | XGB | 0.1624 | 643.73 | 447.46 |
| No identity-adjacent categories | RF | **0.6278** | **429.08** | **316.55** |
| No identity-adjacent categories | XGB | **0.4574** | **518.11** | **354.43** |
| Physical numeric only | RF | **0.5734** | **459.39** | **329.34** |
| Physical numeric only | XGB | **0.4692** | **512.43** | **348.59** |

### Interpretation

The extreme full-engineered collapse is **partly feature-representation dependent**. Engineered categorical context variables behave as harmful study-correlated proxies under study transfer. Removing them substantially improves unseen-study prediction.

Therefore the conference paper must **not** claim that the heterogeneous corpus is intrinsically incapable of useful cross-study forward prediction. The defensible claim is narrower and more informative:

> Study-aware validation exposed a feature-representation failure that conventional row-random validation largely concealed.

## 7. Cluster-size robustness after category removal

The improved transfer is not explained by singleton studies.

For the 12 studies with at least 5 rows (253 total rows):

### Held out n>=5 studies, train on all other strict studies

| Representation | RF R² | XGB R² |
|---|---:|---:|
| Full engineered | -0.0307 | 0.1314 |
| No identity-adjacent categories | **0.6163** | **0.4385** |
| Physical numeric only | **0.5592** | **0.4509** |

### Population restricted to n>=5 studies only

| Representation | RF R² | XGB R² |
|---|---:|---:|
| Full engineered | -0.0392 | 0.1136 |
| No identity-adjacent categories | **0.6150** | **0.4604** |
| Physical numeric only | **0.5870** | **0.4707** |

The representation effect therefore survives removal of the smallest study clusters.

## 8. Crossed missingness x representation sensitivity

The reviewer correctly required disclosure of severe missingness. However, the improved category-stripped transfer does **not** depend on the heavily imputed dose/contact-time variables.

### Study-grouped 5-fold

| Representation | RF R² | XGB R² |
|---|---:|---:|
| No identity-adjacent categories | 0.6370 | 0.4807 |
| No identity + remove dose/contact time | **0.6522** | **0.5012** |
| Physical numeric only | 0.5796 | 0.4964 |
| Physical numeric + remove dose/contact time | **0.6819** | **0.4979** |

### Strict LOSO

| Representation | RF R² | XGB R² |
|---|---:|---:|
| No identity-adjacent categories | 0.6278 | 0.4574 |
| No identity + remove dose/contact time | **0.6549** | **0.5019** |
| Physical numeric only | 0.5734 | 0.4692 |
| Physical numeric + remove dose/contact time | **0.6725** | **0.4955** |

Thus high missingness is an important limitation and disclosure requirement, but it does not explain the improved study-transfer result after representation correction.

## 9. Domain-specific inverse-design relevance

Feature correction does **not** restore the original agricultural-waste inverse-design claim.

### Strict agricultural-waste domain — 65 rows / 4 studies

| Representation | RF LOSO R² | XGB LOSO R² |
|---|---:|---:|
| Full engineered | -1.750 | -2.038 |
| No identity-adjacent categories | -1.741 | -2.047 |
| Physical numeric only | -1.756 | -2.047 |

**Disposition: FAIL.** Too few independent studies and poor transfer under every tested representation.

### Broad biogenic-waste domain — 92 rows / 6 studies

| Representation | RF LOSO R² | XGB LOSO R² |
|---|---:|---:|
| Full engineered | 0.276 | 0.619 |
| No identity-adjacent categories | **0.411** | **0.642** |
| Physical numeric only | **0.426** | **0.642** |

The pooled XGB result improves modestly, but the catastrophic Alshabib held-out study remains:

- actual q_e: **270.27 and 199.76 mg/g**;
- no-identity RF predictions: **1775.47 and 1753.89 mg/g**;
- no-identity XGB predictions: **1724.41 and 1724.41 mg/g**;
- RF MAE: **1529.66 mg/g**;
- XGB MAE: **1489.39 mg/g**;
- mean RF-XGB prediction disagreement: only **40.27 mg/g**.

Thus **model agreement still does not imply correctness** after removal of the harmful categories.

### Waste-derived-carbon domain — 138 rows / 7 studies

| Representation | RF LOSO R² | XGB LOSO R² |
|---|---:|---:|
| Full engineered | 0.487 | 0.495 |
| No identity-adjacent categories | **0.574** | **0.520** |
| Physical numeric only | **0.551** | **0.520** |

Useful as a restricted-domain diagnostic only.

## 10. Inverse-design disposition after the review

**Validated engineering inverse-design framing remains FAIL for the current evidence.**

The reason is now more nuanced than the previous conference draft:

- a better forward representation can recover meaningful pooled unseen-study prediction;
- but the original target domain (strict agricultural waste) remains only four studies and fails badly;
- the broader promising domain retains a complete catastrophic held-out-study failure;
- RF and XGB can remain mutually close while both are wrong by about 1.5 g/g;
- the representation that improves transfer removes material/pollutant categorical context that a true prescriptive adsorbent-process recommendation would need to specify explicitly;
- dose and contact time are heavily missing in the current corpus;
- study size is highly imbalanced and effective independent-study depth is substantially below the nominal 24;
- the legacy QMAX, test-selection, target-objective and optimizer-lineage defects remain unresolved as historical claims;
- no new laboratory or independent external validation has been generated for an inverse-design recommendation.

The correct prospective statement is:

> ID-SEAD remains testable as an inverse-design research concept, but any renewed implementation must use a feature representation that survives study-aware validation while preserving scientifically necessary material/pollutant context, then pass an explicit reliability and external/experimental validation gate before recommendations are treated as actionable.

## 11. Reviewer revision-gate execution record

Final workflow:
- workflow: `ID-SEAD reviewer revision gate V2`;
- run ID: `33338908933`;
- job ID: `99330787391`;
- head SHA: `6e048d106a33f241c3a2161ae9f2827cf05f653b`;
- conclusion: **success**;
- artifact ID: `9739944134`;
- artifact digest: `sha256:9fecfe3121f7ed2e216cf81eb9d2b7c1441bfd90a8701cd3a36b593dd7a18940`.

Primary scripts:
- `conference_salvage/reviewer_revision_gate_v2/run_reviewer_revision_gate_v2.py`
- `conference_salvage/reviewer_revision_gate_v2/run_identity_loso_followup.py`
- `conference_salvage/reviewer_revision_gate_v2/run_crossed_missingness_sensitivity.py`

## 12. Non-negotiable reporting rules

1. Do not describe the full-engineered collapse as representation-independent.
2. Do not promote the post-review ablation as predeclared confirmatory analysis.
3. Do not use the recovered RF/XGB transfer performance to restore a deployment or inverse-design claim.
4. Always disclose the agricultural-domain failure, catastrophic broad-biogenic study, missingness and study-size imbalance when discussing the recovered transfer result.
5. Keep the legacy R²=0.847, QMAX=624 and original Table III disabled as current evidence.
