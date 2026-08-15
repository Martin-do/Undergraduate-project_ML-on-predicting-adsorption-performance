# ID-SEAD V2 — Phase 4 Precursor-Domain Restriction Findings

Status: **confirmed diagnostic result; feature branch only**

Phase 3 showed that the heterogeneous reconstructed corpus does not support broad unseen-primary-study prediction and that the submitted “agricultural waste” scope does not match the data. Phase 4 asks whether a defensible precursor restriction improves transfer without cherry-picking individual studies.

## 1. Evidence-based precursor composition

The 251-row inherited Iftikhar block contains at least 15 precursor-domain classes. Important components include cellulose-derived feedstock, vinasse waste, textile sludge, Maghara mine coal, crab shell, wastewater sludge, white sugar, wood-gasification residual char, tobacco residue, bean husk and groundnut shell.

Three nested candidate scopes were defined *before* model comparison. Only rows explicitly marked `yes` for a scope are admitted; uncertain or unresolved rows are excluded rather than promoted.

| Candidate scope | Rows | Confirmed primary studies | Interpretation |
|---|---:|---:|---|
| Strict agricultural waste | 65 | 4 | tobacco residue, bean husk, vinasse waste, groundnut shell |
| Broad biogenic waste | 92 | 6 | strict agricultural + crab shell + wood-gasification residual char |
| Waste-derived carbon | 138 | 7 | broad waste-derived set + industrial textile/wastewater sludge-derived carbon |

The strict agricultural subset has only **four independent primary studies**, so it is exploratory and is not sufficient for a strong general cross-study ML claim.

## 2. Validation design

- original engineered feature representation;
- fold-safe preprocessing;
- complete **leave-one-primary-study-out (LOSO)** validation;
- LR, SVR, RF, XGB and unconstrained Ridge stack;
- no legacy QMAX/constraint layer;
- no study removed because its error is inconvenient.

## 3. Pooled LOSO results

| Scope | Model | R² | RMSE (mg/g) | MAE (mg/g) |
|---|---|---:|---:|---:|
| Strict agricultural waste | RF | -1.750 | 1229.21 | 1039.58 |
| Strict agricultural waste | XGB | -2.038 | 1291.99 | 1083.82 |
| Strict agricultural waste | Ridge stack | -11.596 | 2630.99 | 1612.88 |
| Broad biogenic waste | RF | 0.276 | 656.66 | 537.40 |
| Broad biogenic waste | **XGB** | **0.619** | **476.29** | **376.27** |
| Broad biogenic waste | Ridge stack | -2.286 | 1398.79 | 1015.35 |
| Waste-derived carbon | RF | **0.487** | 585.68 | **407.95** |
| Waste-derived carbon | XGB | **0.495** | **581.33** | 408.58 |
| Waste-derived carbon | Ridge stack | 0.225 | 720.20 | 559.49 |

LR and SVR are not competitive in these scopes. LR also shows severe numerical/extrapolation instability in the broad-biogenic LOSO experiment and is not a credible candidate surrogate for that domain.

## 4. Equal-study view

The pooled broad-biogenic XGB result is encouraging but must not be read in isolation because the 49-row Li et al. study dominates the row count.

For broad biogenic waste:

- XGB mean study MAE: **486.78 mg/g**;
- XGB median study MAE: **308.32 mg/g**;
- XGB mean study RMSE: **524.60 mg/g**;
- XGB median study RMSE: **363.63 mg/g**.

For waste-derived carbon:

- RF mean study MAE: **458.84 mg/g**, median **235.67 mg/g**;
- XGB mean study MAE: **488.60 mg/g**, median **229.57 mg/g**.

Thus restriction improves transfer relative to the full heterogeneous domain, but substantial between-study instability remains.

## 5. The critical broad-biogenic outlier

Broad-biogenic XGB held-out-study MAE:

- Alshabib et al. / groundnut-shell family, 2 rows: **1532.57 mg/g**;
- Archin et al. / tobacco residue, 4 rows: **145.28 mg/g**;
- Gao et al. / crab shell, 21 rows: **496.97 mg/g**;
- Gupta et al. / bean husk, 10 rows: **268.12 mg/g**;
- Li et al. / vinasse, 49 rows: **348.52 mg/g**;
- Ravenni et al. / wood-gasification residual-char subset, 6 rows: **129.23 mg/g**.

Five of six studies are materially better than the full-corpus transfer result, but the Alshabib study is a severe failure. Because it has only two rows, pooled R² can mask its practical importance.

**The study will not be removed post hoc.** The next test is whether a training-only applicability-domain measure independently identifies those rows as unsupported. If it does not, the broad-biogenic model remains insufficiently reliable for inverse design.

## 6. Decision

### Strict agricultural-waste framing

**FAIL.** There are too few independent studies and LOSO performance is poor. The submitted agricultural-waste-only title should not be retained for a predictive-generalization paper on this dataset.

### Broad biogenic-waste framing

**PROVISIONAL / requires applicability-domain validation.** XGB pooled R² = 0.619 is the first genuinely encouraging unseen-study result, but one complete study fails catastrophically. This is not yet enough for deployment or inverse design.

### Waste-derived-carbon framing

**PROVISIONAL.** RF/XGB pooled R² is around 0.49 across seven studies, with better coverage but still substantial study-level variation.

### Stacking

**FAIL again.** The unconstrained Ridge stack is inferior to the strongest tree model in every restricted scope. Stacking should not remain the central novelty unless a separate, prospectively defined benefit is later demonstrated.

## 7. Next gate

Implement a training-only applicability-domain audit using:

- continuous-feature nearest-neighbour / k-nearest-neighbour support in training-standardized space;
- explicit novel-category flags for held-out rows;
- study-level and point-level error versus support distance;
- predeclared training-derived support thresholds (e.g. 95th percentile of training leave-one-out kNN distance);
- coverage-vs-error reporting rather than deleting difficult studies.

Only after that gate should we decide whether a domain-qualified surrogate is scientifically defensible and whether any inverse-design demonstration can remain in the revised work.
