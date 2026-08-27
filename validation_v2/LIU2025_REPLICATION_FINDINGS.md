# Liu et al. 2025 — Provenance Reconstruction and Matched Study-Aware Replication

DOI: `10.1007/s44246-025-00213-9`

Status: **CI-VERIFIED MATCHED REPLICATION — PRIMARY STRICT PROVENANCE GATE LOCKED**

This document records the scientific disposition of the Liu et al. 2025 public biochar/dye dataset under the frozen Paper 1 multi-dataset protocol. It does not alter Dataset V2.1 and does not assume in advance that group-aware performance must be lower than row-random performance.

## 1. Public-source reconstruction

The public workbook is `Biochar_dye_filtered.xlsx` with SHA-256:

`2a7219c309fe09187e4c3e4ef7f55794051643570fe612fd7c2241a4cd16de11`

The article reports:

- 685 collected literature observations;
- removal of 17 observations above the stated `Q > 4 mmol/g` gate;
- 668 observations used for modelling;
- a random 80:20 train/test split;
- CatBoost as the best reported model with `R² = 0.9880`.

The public workbook requires an important reproducibility distinction. A plain pandas read of the public modelling sheet returns 685 rows, but the workbook's logical adsorption table contains 668 rows. Excel rows 670–686 form a 17-row malformed/shifted spreadsheet tail that cannot be reconciled to the workbook's dye-descriptor lookup. Those 17 rows are **not** the article's original high-Q observations: every Q value in the public preprocessing sheets is below 4 mmol/g and the maximum public Q is approximately 3.879365 mmol/g. The original excluded high-Q observations are therefore not recoverable from the public workbook.

The 17 spreadsheet-tail rows are quarantined from all primary grouped analyses.

## 2. Primary-study provenance

The workbook retains a `literature collection` sheet containing 20 source DOIs but no row-level study identifier in the modelling table. A deterministic reconstruction was therefore performed using:

1. the exact order of the 20 listed source DOIs;
2. contiguous row blocks in the logical 668-row adsorption table;
3. decoded dye-descriptor identities;
4. material fingerprints such as BET area, elemental ratios and pH-related descriptors; and
5. primary-paper dye/material scope.

No DOI was assigned solely because a material name looked similar.

### Provenance gates

**Strict primary population:**

- 624 rows
- 17 primary studies
- only high-confidence source mappings

**Extended source-order sensitivity:**

- 668 rows
- 19 primary studies
- includes 44 medium-confidence rows from two source blocks

One listed source, DOI `10.1002/sia.6575`, is retained in the source ledger but assigned **zero** modelling rows because no retained interval can be mapped to it without guessing.

The largest strict-set primary study contributes 110 of 624 rows (17.63%).

## 3. Matched validation design

For every model within a population:

- the random and grouped arms use exactly the same observations;
- the same feature set is used;
- the same fixed model specification is used;
- `StandardScaler` is fitted inside each training fold;
- no model is retuned separately to improve either validation arm.

Feature set follows the public model representation after dropping `O/C`, `PV` and `E`.

Validation:

- row-random comparator: shuffled 5-fold CV, seed 1;
- group-aware comparator: 5-fold `GroupKFold` by reconstructed primary DOI;
- robustness: `LeaveOneGroupOut` (study-LOSO).

Models:

- RF500
- XGB500
- CatBoost500

CatBoost is scientifically important because CatBoost is the best-performing model family reported by the original article. The fixed CatBoost500 comparison below is a matched validation experiment; it must not be described as an exact reproduction of the article's optimized CatBoost model.

## 4. Primary strict results — 624 rows / 17 studies

| Model | Random 5-fold R² | Study GroupKFold R² | ΔR² | Study-LOSO R² | Random RMSE | Grouped RMSE | Random MAE | Grouped MAE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RF500 | 0.930377 | -0.339908 | 1.270285 | -0.010160 | 0.196850 | 0.863570 | 0.097052 | 0.510036 |
| XGB500 | 0.938244 | -0.036089 | 0.974333 | 0.235235 | 0.185395 | 0.759379 | 0.094459 | 0.451490 |
| CatBoost500 | 0.935977 | 0.109642 | 0.826335 | 0.059409 | 0.188767 | 0.703951 | 0.104975 | 0.434974 |

The central matched CatBoost result is therefore:

`R² 0.935977 (random) -> 0.109642 (primary-study GroupKFold)`

with `ΔR² = 0.826335`.

This is the primary Liu result for Paper 1.

## 5. Extended provenance sensitivity — 668 rows / 19 studies

| Model | Random 5-fold R² | Study GroupKFold R² | ΔR² | Study-LOSO R² |
|---|---:|---:|---:|---:|
| RF500 | 0.929825 | 0.145585 | 0.784239 | 0.030503 |
| XGB500 | 0.936733 | 0.341369 | 0.595364 | 0.140998 |
| CatBoost500 | 0.939852 | 0.105311 | 0.834542 | 0.064606 |

The CatBoost conclusion is highly stable to the provenance sensitivity: grouped R² is approximately 0.110 in the strict set and 0.105 in the extended set. XGB is more sensitive to inclusion of the two medium-confidence source blocks, which is why the strict provenance population remains the primary analysis.

## 6. Public-workbook 685-row diagnostic

Using the same fixed models under row-random five-fold CV only:

| Model | Public sheet 685 R² | Logical 668 R² |
|---|---:|---:|
| RF500 | 0.944472 | 0.929825 |
| XGB500 | 0.948619 | 0.936733 |
| CatBoost500 | 0.949370 | 0.939852 |

The 17 spreadsheet-tail rows modestly raise row-random performance, but this effect is far smaller than the random-versus-study-aware gap. They are therefore a separate reproducibility defect, not the main explanation for the validation gap.

## 7. Relation to the published CatBoost score

The original article reports optimized CatBoost `R² = 0.9880`. The public notebook:

- loads `Biochar_dye_filtered.xlsx` with a plain pandas read;
- globally standardizes predictors before splitting;
- uses a random 80:20 split with `random_state=1`;
- performs ordinary five-fold Bayesian hyperparameter search;
- later constructs one fixed shuffled five-fold object and reuses those same folds inside a 1000-iteration loop.

A separate deterministic public-pipeline reconstruction is being retained as a reproducibility diagnostic. Its purpose is to determine how closely the public executable workflow approaches the published random-split score. It does **not** replace the matched study-aware comparison above.

## 8. Scientific interpretation

Liu 2025 provides a second independent published-dataset replication beyond Moosavi 2021 and a third case when Dataset V2.1 is included.

The result supports the Paper 1 hypothesis without requiring identical collapse across datasets. Under matched validation:

- Dataset V2.1 shows a large random-to-study-aware gap;
- Moosavi 2021 shows a substantial but smaller gap while retaining moderate cross-study signal;
- Liu 2025 shows a very large gap in the strict provenance population, including for the CatBoost model family emphasized by the original paper.

The defensible conclusion is not that random splitting is intrinsically invalid. It is that row-random validation can estimate interpolation among already represented literature systems and can materially overstate performance for the stronger claim of transfer to an unseen primary study. The magnitude is dataset-, model- and provenance-dependent.

## 9. Reproducibility record

Primary-study provenance workflow:

- GitHub Actions run: `33092156615`
- conclusion: `success`
- artifact: `paper1-liu2025-primary-provenance`
- artifact ID: `9654813125`
- artifact SHA-256: `c03a9d0a7b408225ac57c0297fe882774225008dfa9e2269089c9516d8467c16`

Matched validation workflow:

- GitHub Actions run: `33092348428`
- conclusion: `success`
- artifact: `paper1-liu2025-matched-validation`
- artifact ID: `9654942941`
- artifact SHA-256: `aa363d84ef2dac918c31791cbd35cad5aaced57d2b7e557a7fe7e936452934d9`

No Liu results should be copied into the final manuscript from memory or manually retyped when deterministic registry/table generation is available.
