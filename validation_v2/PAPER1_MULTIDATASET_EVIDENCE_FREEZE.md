# Paper 1 — Multi-Dataset Evidence Freeze

Status: **SCIENTIFIC EVIDENCE BASE FROZEN FOR MANUSCRIPT RECONSTRUCTION**

Freeze date: **2026-08-28**

Branch: `paper1/multidataset-study-aware-replication`

Parent protocol: `MULTIDATASET_VALIDATION_PROTOCOL.md` — frozen before external grouped-validation outcomes.

## 1. Reason for freezing now

The purpose of the multi-dataset extension was to determine whether the validation-gap finding in Dataset V2.1 was merely an idiosyncrasy of one project or whether the sensitivity to scientific grouping could be demonstrated and contextualised across other literature-derived adsorption datasets.

That objective is now satisfied without continuing to search for datasets that produce a preferred result.

The evidence set now contains:

1. a deeply reconstructed primary case (V2.1);
2. two additional **primary-source-independent matched reanalyses** on different adsorption targets;
3. a lineage-overlapping matched sensitivity that must not be double-counted;
4. an independent cross-team published conventional-versus-grouped corroboration;
5. a positive good-practice comparator where publication-level separation retains strong performance; and
6. prior methodological literature showing that data handling/leakage concerns are already recognised, which constrains the novelty claim appropriately.

This is sufficient for an outcome-neutral methodological paper. Additional dataset collection is therefore stopped as a primary objective.

## 2. Primary matched evidence

### A. Dataset V2.1 — deep provenance case

Strict population: **273 rows / 24 primary studies**.

Representative XGBoost result:

- row-random 5-fold R² = **0.8936**
- primary-study GroupKFold R² = **0.1929**
- ΔR² = **0.7007**
- LOSO R² = **0.1624**

This case provides the deepest provenance reconstruction, source-overlap audit, domain-sensitivity analysis, external-transfer assessment and historical-claim disposition.

### B. Liu et al. dye/biochar 2025 — matched primary-source-independent corpus

Strict population: **624 rows / 17 primary studies**.

Representative CatBoost500 result:

- row-random 5-fold R² = **0.935977**
- primary-study GroupKFold R² = **0.109642**
- ΔR² = **0.826335**
- LOSO R² = **0.059409**

Public-pipeline reconstruction independently reproduces very high random holdout performance (R² = **0.978611** on the executable 685-row sheet), showing that the grouped drop is not caused by an inability to reproduce the original random-performance regime.

CI run: `33092348428`; artifact `9654942941`.

### C. Liu et al. ammonia-N/biochar 2025 — second matched primary-source-independent corpus

Matched executable population: **409 rows / 7 primary studies**.

Representative CatBoost500 result:

- row-random 5-fold R² = **0.883650**
- primary-study GroupKFold R² = **-0.058128**
- ΔR² = **0.941778**
- LOSO R² = **-0.054673**

A public-style random 80:20 reconstruction gives R² = **0.932643** and RMSE = **0.538641**, almost exactly reproducing the article's CatBoost R² = **0.9329** and RMSE = **0.5378**.

The seven contributing primary-study DOIs do not overlap the V2.1 or Liu dye source sets. The two Liu datasets nevertheless share a broader dataset-curation/author-team lineage, which must be disclosed.

CI run: `33206265927`; artifact `9699800084`.

## 3. Matched lineage sensitivity — not independent evidence

### Moosavi et al. 2021

Recoverable population: **344 rows / 12 source studies**.

Published-style nine-variable RF:

- random 5-fold R² = **0.893093**
- grouped R² = **0.466536**
- ΔR² = **0.426557**
- LOSO R² = **0.462893**

However, all 344 recoverable rows arise from source-study lineage already represented in the historical V2.1/Iftikhar corpus. Moosavi is retained as a CI-verified lineage sensitivity and source-reconstruction check, but **is excluded from the independent-replication count**.

## 4. Independent cross-team published corroboration

### Aguiar & Kasemodel 2026 — methylene-blue adsorption onto clays

- 1,098 experiments / 38 studies overall
- largest model M5: 726 observations / 23 studies
- conventional CV R² ≈ **0.79**
- study-GroupKFold R² ≈ **0.66**

Other smaller/feature-richer subsets show larger decreases and some negative grouped R² values.

This study is not our computational rerun. It is important because it supplies independently published, cross-team corroboration using another adsorbent class and directly compares conventional versus source-grouped validation.

## 5. Positive source-aware comparator

### Huang et al. 2026 — heavy-metal adsorption by biochar

The authors separate samples at the publication level before modelling:

- all rows from one publication are assigned exclusively to train or test;
- preprocessing is derived from training data;
- five-fold CV occurs inside training.

Reported XGBoost qe performance remains strong:

- test R² = **0.99**
- training CV R² = **0.92 ± 0.04**

This is a required counterexample. Paper 1 must not claim that study-aware splitting inevitably produces poor performance.

## 6. Core scientific conclusion supported by the frozen evidence

The evidence does **not** support the simplistic statement that random splitting is always wrong or that adsorption ML cannot generalise.

It supports the more precise conclusion:

> In literature-derived adsorption machine learning, performance estimates can be highly sensitive to the scientific unit of validation. Row-random evaluation often measures interpolation among experimental systems already represented in training and can substantially overstate performance for the distinct estimand of transfer to an unseen primary study. The magnitude of this validation gap is dataset-dependent, and strong performance can survive source-aware evaluation in some coherent datasets.

## 7. Novelty boundary

Paper 1 must not claim novelty for discovering that grouped cross-validation exists or that dependence can cause leakage. Those principles are established, and recent biochar/adsorption literature already discusses them.

The defensible contribution is the combination of:

1. **primary-study provenance reconstruction** in literature-derived adsorption corpora;
2. **matched random-versus-study-aware experiments** holding rows, predictors and models fixed;
3. **multi-corpus empirical quantification** of the validation gap;
4. **explicit source-lineage/double-counting audits**;
5. **executable-paper reproducibility checks** showing that original high random scores can be reproduced before changing the validation unit;
6. **outcome-neutral interpretation** including a positive source-aware comparator;
7. a reporting framework that distinguishes row count from independent-study count and aligns validation design with the scientific generalisation claim.

## 8. Independence hierarchy for manuscript language

Paper 1 will distinguish:

- observation-level independence;
- primary-study/campaign independence;
- corpus-curation/research-team independence.

The two Liu corpora are disjoint at the primary-study level but share a broader research-team/data-curation lineage. Aguiar 2026 supplies cross-team corroboration.

## 9. Datasets not required before manuscript reconstruction

The following may remain in the literature audit without blocking the paper:

- Yadav 2025 — data available on request;
- Abu-Shareha 2026 — data available on request;
- Liu hydrochar 2024 — raw/source mapping not presently adequate;
- Jaffari 2023 — public rows available, but higher-level source grouping not defensibly reconstructed;
- Jaffari 2024 — potential secondary candidate, not necessary for current evidence sufficiency.

They should not be pursued merely to increase the number of datasets or to obtain another large ΔR².

## 10. Evidence-freeze rule

From this point onward, a new matched dataset is added to the primary analysis only if it satisfies the frozen protocol **and** fills a clearly documented gap that materially changes inference. It must not be added because its result is expected to strengthen the current conclusion.

Any post-freeze addition requires an explicit amendment recording why it was necessary before its grouped result is inspected.

## 11. Next phase

**Proceed to manuscript reconstruction.**

The existing V2.1 working manuscript predates the multi-dataset extension and must now be rewritten around the frozen evidence hierarchy above. New final figures, tables, abstract, methods, discussion and title should be generated from the deterministic evidence registry and source-specific finding files.
