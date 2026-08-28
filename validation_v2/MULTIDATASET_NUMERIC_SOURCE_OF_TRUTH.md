# Paper 1 Multi-Dataset Numerical Source of Truth

Status: **SCIENTIFIC GATE LOCKED FOR MANUSCRIPT SYNTHESIS**

This file is the numerical authority for the multi-dataset extension of Paper 1. It supplements, and does not replace, `V21_NUMERIC_SOURCE_OF_TRUTH.md` for the original V2.1 corpus.

## 1. Canonical evidence files

1. `MULTIDATASET_RESULTS_REGISTRY.csv` — CI-locked matched validation results and sensitivities.
2. `SOURCE_AWARE_COMPARATOR_REGISTRY.csv` — published source-aware comparators/corroboration that cannot be independently rerun with current public data.
3. `multidataset_synthesis.py` — deterministic synthesis script. It does **not** retrain models.
4. GitHub Actions run `33212475321` — deterministic synthesis run, conclusion `success`.
5. Artifact `9702119314`, name `paper1-multidataset-synthesis`, SHA-256 `148532e250de75cff9dde98d84b6501d3eb459ef9447c691bb929abf78d59f4a`.
6. Synthesis commit `acac568c716d674c9e16a9679e5703281780e2fc`.

Registry blob SHA at this lock:
- `MULTIDATASET_RESULTS_REGISTRY.csv`: `d687ef04f0f5b9b06b9420d5233e8b9be8f3fed1`
- `SOURCE_AWARE_COMPARATOR_REGISTRY.csv`: `4ec32f17b0588e1e3f2678fb4d91fdf50d536f2d`

## 2. Primary independent matched datasets

The primary cross-dataset analysis contains **three independent matched corpora**. The common-model synthesis is deliberately restricted to RF and XGB because those two model families are available across all three datasets. This avoids choosing a different post-hoc “best model” for each corpus.

| Dataset | Rows | Primary studies | Model | Random CV R² | Study-aware R² | ΔR² | LOSO R² |
|---|---:|---:|---|---:|---:|---:|---:|
| V2.1 strict | 273 | 24 | RF | 0.9042 | 0.0265 | 0.8777 | 0.0085 |
| V2.1 strict | 273 | 24 | XGB | 0.8936 | 0.1929 | 0.7007 | 0.1624 |
| Liu 2025 dyes, strict | 624 | 17 | RF | 0.930377 | -0.339908 | 1.270285 | -0.010160 |
| Liu 2025 dyes, strict | 624 | 17 | XGB | 0.938244 | -0.036089 | 0.974333 | 0.235235 |
| Liu ammonia-N | 409 | 7 | RF | 0.837380 | -0.420734 | 1.258114 | -0.421031 |
| Liu ammonia-N | 409 | 7 | XGB | 0.851681 | -0.640524 | 1.492205 | -0.649272 |

Across these six pre-specified common-model comparisons:
- random R² exceeds study-aware R² in **6/6** comparisons;
- ΔR² ranges from **0.7007 to 1.492205**;
- the descriptive median ΔR² is **1.1162235**;
- random R² ranges from **0.837380 to 0.938244**;
- study-aware R² ranges from **-0.640524 to 0.1929**.

The median ΔR² is a **descriptive summary only**. These heterogeneous adsorption datasets are not pooled as a formal meta-analysis.

## 3. Dataset-specific locked evidence

### 3.1 V2.1 strict

- CI source: final validation run `32003217034`, artifact `9279131675`.
- Primary analysis: 273 rows / 24 reconstructed primary studies.
- The full V2.1 numerical authority remains `V21_NUMERIC_SOURCE_OF_TRUTH.md`.

### 3.2 Liu 2025 dye corpus

- CI source: run `33092348428`, artifact `9654942941`.
- Strict primary analysis: 624 rows / 17 high-confidence primary-study groups.
- Extended sensitivity: 668 rows / 19 groups, including 44 medium-confidence rows.
- Strict CatBoost diagnostic: random R² `0.935977`, grouped R² `0.109642`, LOSO R² `0.059409`.
- Public optimized-style reconstruction reproduced high random-test performance separately; those optimized diagnostic values are **not** substituted for the matched common-model comparison.

### 3.3 Liu ammonia-N corpus

- CI source: run `33206265927`, artifact `9699800084`.
- Primary analysis: 409 rows / 7 reconstructed primary studies.
- Underlying primary-study DOI set is disjoint from V2.1 and Liu dye.
- Public-style CatBoost diagnostic reproduces the article's random holdout almost exactly (`R²=0.932643` versus published `0.9329`; RMSE `0.538641` versus `0.5378`).
- The matched CatBoost comparison is random R² `0.883650` versus grouped R² `-0.058128` and LOSO `-0.054673`.

## 4. Lineage-overlapping sensitivity — not an independent replication

Moosavi et al. 2021 is retained because it is a valuable matched sensitivity, but it is **excluded from the independent-replication count** after provenance reconstruction showed that its source-study lineage is already represented in historical V2.1.

Recoverable subset:
- 344 rows / 12 verified primary references;
- published-hyperparameter nine-variable RF: random R² `0.893093`, grouped R² `0.466536`, LOSO `0.462893`;
- five-variable RF: random R² `0.808141`, grouped R² `0.480998`, LOSO `0.476675`.

The six absent source-PDF rows are not imputed or invented.

## 5. Published source-aware comparators and prior art

These studies are contextual evidence, not CI-rerun primary matched datasets.

### Huang et al. 2026 — positive counterexample

DOI `10.3390/f17030326`.

- Data 2: 452 adsorption-capacity records.
- 4:1 train/test separation at the **literature-source level**.
- All rows from the same publication are assigned exclusively to train or test.
- Preprocessing is fitted from training data only.
- XGB q_e test R² `0.99`, test RMSE `0.02`, five-fold R² `0.92 ± 0.04`.
- Raw modelling rows are available only on request, so an independent rerun is not currently possible.

**Interpretation:** source-aware validation does not inherently force poor performance. Dataset structure/domain coherence can permit strong source-held-out prediction.

### Aguiar & Kasemodel 2026 — independent published corroboration

DOI `10.1007/s00521-026-12200-1`.

- Full compilation: 1,098 experiments from 38 studies.
- Model M5: 726 experiments / 23 studies.
- Conventional CV R² `0.79`.
- study-GroupKFold R² approximately `0.66`, MAE approximately `48`, RMSE `69`.
- Other smaller feature-rich models show larger drops and some negative grouped R².

**Interpretation:** the validation-gap phenomenon is already independently recognized in adsorption ML. Therefore Paper 1 must **not** claim to be the first work to recommend GroupKFold or the first work to observe a random-versus-grouped performance gap.

## 6. Locked scientific interpretation

Paper 1 may support the following claims:

1. Across three independently reconstructed literature-derived adsorption corpora, the two common model families (RF and XGB) show materially higher performance under row-random CV than under primary-study-aware validation.
2. The magnitude of the validation gap is dataset dependent; it is not a universal constant.
3. The gap cannot be interpreted simply as “ML does not work for adsorption,” because published source-aware counterexamples retain strong performance.
4. Primary-paper provenance is itself a methodological problem: source grouping cannot always be recovered from the modelling matrix without reconstruction.
5. Dataset diversity, domain coherence, study count, source imbalance and descriptor adequacy are plausible determinants of study-held-out performance and should be discussed as hypotheses unless directly tested.
6. Strong random-split R² alone is not evidence of transfer to unseen experimental studies.

Paper 1 must **not** claim:

- that random splitting is always invalid;
- that every adsorption model will collapse under source-aware validation;
- that this is the first adsorption study to use or advocate study-aware splitting;
- that the descriptive median ΔR² is a formal pooled effect size;
- that Huang 2026 or Aguiar 2026 were independently rerun by this project;
- that Moosavi 2021 is an independent external replication;
- that the old ID-SEAD stack, inverse design, QMAX=624 mg/g constraint or deployment claims are restored.

## 7. Manuscript synthesis gate

**DATASET HUNTING IS CLOSED FOR THE PRIMARY MANUSCRIPT UNLESS A NEW DATASET IS REQUIRED TO RESOLVE A SPECIFIC REVIEWER-LEVEL GAP.**

Yadav 2025, Abu-Shareha 2026, Jaffari 2023 and other request-only/insufficiently grouped datasets may remain in the literature audit or future-replication queue. They are not required before drafting the current Paper 1.

Next controlled phase: generate final manuscript tables/figures from this source of truth and reconstruct Paper 1 around the multi-dataset empirical question.
