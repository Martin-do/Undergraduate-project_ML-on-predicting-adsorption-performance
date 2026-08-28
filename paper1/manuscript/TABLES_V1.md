# Paper 1 — Deterministic Tables V1

Status: **Draft tables generated from frozen evidence files.**

Numerical authority for project-generated matched results: `validation_v2/MULTIDATASET_RESULTS_REGISTRY.csv`, Dataset V2.1 Phase 8 outputs, and the source-specific replication finding files. Published comparator values are not mixed with project-generated matched metrics.

---

## Table 1. Corpus structure, provenance and evidence role

| Corpus | Domain | Analysis population | Independent primary studies | Provenance / grouping status | Evidence role |
|---|---|---:|---:|---|---|
| Dataset A (V2.1 strict) | Heterogeneous literature-derived adsorption capacity | 273 | 24 | Strict comparable subset of 307 primary-confirmed rows / 29 reconstructed studies; 15 unresolved source rows excluded from primary-study claims | Primary deep matched case |
| Liu dye 2025 strict | Dye adsorption by biochar | 624 | 17 | High-confidence reconstruction from 20-source literature ledger; 44 medium-confidence rows reserved for sensitivity | Primary-source-independent matched replication |
| Liu ammonia-N 2025 | NH4+-N adsorption by biochar | 409 | 7 | Historical workbook recovered from Git history; primary groups reconstructed from literature ledger and source-specific blocks | Primary-source-independent matched replication; shared broader curation-team lineage with Liu dye |
| Moosavi 2021 | Dye adsorption on agricultural-waste activated carbon | 344 recoverable | 12 | Explicit references recoverable from official supplement; six numbered rows absent from distributed PDF | Lineage-overlapping matched sensitivity; **not independent** |
| Aguiar & Kasemodel 2026 | Methylene-blue adsorption onto clays | 1,098 overall; M5 = 726 | 38 overall; M5 = 23 | Authors explicitly group by source study | Independent published cross-team corroboration |
| Huang et al. 2026 | Primarily Cu(II)/Pb(II) adsorption by biochar | 452 | Multiple publications | Publication-level 4:1 train/test separation; training-only preprocessing | Positive source-aware comparator |

**Interpretive note.** Row count and independent-study count are deliberately reported separately. The independent-study count is the relevant nominal group sample size for unseen-primary-study validation.

---

## Table 2. Reproduction of conventional random-performance regimes before regrouping

| Corpus | Published / source-reported random result | Project reproduction diagnostic | Interpretation |
|---|---:|---:|---|
| Liu dye 2025 | CatBoost R² = 0.9880 | Optimized-style public reconstruction: R² = 0.978611 on executable 685-row sheet; 0.966277 on logical 668 rows | High public random-performance regime reproduced before study grouping |
| Liu ammonia-N 2025 | CatBoost test R² = 0.9329; RMSE = 0.5378 | Public-style 80:20 diagnostic: R² = 0.932643; RMSE = 0.538641 | Near-exact recovery of reported random holdout performance |
| Moosavi 2021 | Five-variable RF test R² ≈ 0.81 | Shuffled five-fold reconstruction R² = 0.808141 | Conventional performance regime closely recovered; dataset retained only as lineage sensitivity |

**Important:** These are reproduction diagnostics, not the primary matched random-versus-grouped experiments. Where public workflows fitted preprocessing globally, that behaviour is isolated here and not used in the fold-safe matched arm.

---

## Table 3. Representative matched random-versus-primary-study results

| Corpus | Model | Rows / studies | Row-random R² | Study-aware R² | ΔR² | LOSO R² |
|---|---|---:|---:|---:|---:|---:|
| Dataset A (V2.1 strict) | XGB | 273 / 24 | **0.8936** | **0.1929** | **0.7007** | **0.1624** |
| Liu dye 2025 strict | CatBoost500 | 624 / 17 | **0.935977** | **0.109642** | **0.826335** | **0.059409** |
| Liu ammonia-N 2025 | CatBoost500 | 409 / 7 | **0.883650** | **-0.058128** | **0.941778** | **-0.054673** |
| Moosavi 2021 lineage sensitivity | RF, published nine-variable specification | 344 / 12 | 0.893093 | 0.466536 | 0.426557 | 0.462893 |

**Counting rule:** Moosavi 2021 is shown because it is a useful matched sensitivity, but it is excluded from the independent-replication count because its recoverable source-study lineage overlaps Dataset A.

---

## Table 4. Full matched model results for the three primary computational corpora

| Corpus | Model | Random R² | Grouped R² | ΔR² | LOSO R² | Random RMSE | Grouped RMSE | Random MAE | Grouped MAE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dataset A | RF | 0.9042 | 0.0265 | 0.8777 | 0.0085 | 217.70 | 693.96 | 108.26 | 473.45 |
| Dataset A | XGB | 0.8936 | 0.1929 | 0.7007 | 0.1624 | 229.44 | 631.90 | 128.26 | 443.41 |
| Dataset A | Historical Ridge stack | 0.9027 | -0.5566 | 1.4593 | — | — | 877.53 | — | 737.63 |
| Liu dye strict | RF500 | 0.930377 | -0.339908 | 1.270285 | -0.010160 | 0.196850 | 0.863570 | 0.097052 | 0.510036 |
| Liu dye strict | XGB500 | 0.938244 | -0.036089 | 0.974333 | 0.235235 | 0.185395 | 0.759379 | 0.094459 | 0.451490 |
| Liu dye strict | CatBoost500 | 0.935977 | 0.109642 | 0.826335 | 0.059409 | 0.188767 | 0.703951 | 0.104975 | 0.434974 |
| Liu ammonia-N | RF500 | 0.837380 | -0.420734 | 1.258114 | -0.421031 | 0.797614 | 2.357558 | 0.515045 | 1.673058 |
| Liu ammonia-N | XGB500 | 0.851681 | -0.640524 | 1.492205 | -0.649272 | 0.761737 | 2.533363 | 0.460515 | 1.831279 |
| Liu ammonia-N | CatBoost500 | 0.883650 | -0.058128 | 0.941778 | -0.054673 | 0.674666 | 2.034582 | 0.423072 | 1.417852 |

**Scale note:** RMSE and MAE are meaningful within each corpus but should not be compared numerically across corpora with different targets/units and transformations.

---

## Table 5. Pre-specified robustness and provenance sensitivities

| Analysis | Model | Random R² | Grouped R² | LOSO R² | Interpretation |
|---|---|---:|---:|---:|---|
| Dataset A — condition-level records only, 257 rows / 14 studies | XGB | 0.8812 | 0.1377 | — | Weak positive transfer remains; result is not created by study-summary/qmax records |
| Dataset A — conventional aqueous capacity only, 264 rows / 23 studies | XGB | 0.8900 | 0.1329 | 0.1851 | Main validation-gap conclusion remains |
| Liu dye — extended source-order sensitivity, 668 rows / 19 studies | CatBoost500 | 0.939852 | 0.105311 | 0.064606 | CatBoost conclusion stable to inclusion of 44 medium-confidence rows |
| Liu dye — extended source-order sensitivity, 668 rows / 19 studies | XGB500 | 0.936733 | 0.341369 | 0.140998 | XGB more sensitive to provenance boundary |
| Moosavi recoverable subset | RF, nine-variable published specification | 0.893093 | 0.466536 | 0.462893 | Moderate grouped performance retained; lineage overlap prevents independent counting |

---

## Table 6. Independent published context and boundary conditions

| Study | Dataset / grouping | Conventional or training result | Source-aware result | Role in Paper 1 |
|---|---|---:|---:|---|
| Aguiar & Kasemodel 2026 | 1,098 MB/clay experiments / 38 studies; M5 = 726 / 23 | M5 conventional CV R² ≈ 0.79 | M5 GroupKFold R² ≈ 0.66; MAE ≈ 48; RMSE ≈ 69 | Independent cross-team corroboration of a validation gap with retained useful transfer |
| Huang et al. 2026 | 452 biochar/heavy-metal records; publication-level 4:1 split | XGB training R² = 0.99; training CV = 0.92 ± 0.04 | XGB publication-held-out test R² = 0.99 | Positive comparator showing that source-aware validation does not necessarily cause collapse |
| Cahyana & Jang 2025 | Methodological review/letter on biochar/heavy-metal ML | — | Highlights leakage and inadequate splitting concerns in compiled experimental data | Prior-art boundary: novelty is not the invention of grouped validation |
| Roberts et al. 2017 | General structured-data cross-validation methodology | — | Blocking/grouping should reflect dependence and prediction target | General methodological anchor for claim–validation alignment |

---

## Table 7. Proposed reporting checklist for literature-derived adsorption ML

| Item | Minimum information to report | Why it matters |
|---|---|---|
| Observation sample size | Total modelling rows after exclusions | Describes row-level information volume |
| Independent-group sample size | Number of primary studies/campaigns/labs relevant to claim | Defines the effective group count for transfer claims |
| Provenance | Row-level primary-source/campaign identifier | Enables grouping, duplicate detection and source-independent external validation |
| Group imbalance | Rows per group and largest-group share | Reveals domination by a few large studies |
| Prediction estimand | Interpolation within represented systems vs unseen-study/new-domain transfer | Determines whether the validation scheme answers the stated claim |
| Preprocessing timing | Explicitly state whether imputation/scaling/transformation is fitted inside training folds | Prevents information transfer across validation partitions |
| Validation design | Random and/or group-aware split, grouping variable, folds and seed | Makes performance estimates interpretable and reproducible |
| Matched comparison | Same rows/features/model across random and grouped arms where both are reported | Isolates validation-unit sensitivity from model/population changes |
| Study-level robustness | LOSO or per-study errors where feasible | Prevents pooled metrics from hiding heterogeneous transfer |
| External independence | Check primary-study and curation-lineage overlap | Avoids calling reused literature evidence “external” |
| Unresolved provenance | Report unmapped rows and handling rule | Avoids guessed group IDs and hidden exclusions |
| Generalisation language | Restrict claims to the tested validation unit/domain | Prevents row-random interpolation metrics from being presented as universal deployment evidence |

---

## Table-generation lock

Before submission, these Markdown tables should be regenerated automatically from machine-readable sources where possible. Manual edits to numerical cells should be treated as provisional. The manuscript reconciliation step must confirm that every displayed project-generated number exists in the frozen registry or a named V2.1 source-of-truth file.
