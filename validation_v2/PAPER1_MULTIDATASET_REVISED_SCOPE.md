# Paper 1 — Multi-Dataset Revised Scope

Status: **LOCKED FOR MANUSCRIPT RECONSTRUCTION**

This scope supersedes the earlier single-corpus framing in `REVISED_PAPER_SCOPE.md` for Paper 1. The V2.1 audit remains the foundational case study, but the manuscript is now a predeclared multi-dataset reproducibility/provenance study.

## Working title

**Random-Split Optimism and Study-Aware Generalisation in Literature-Derived Adsorption Machine Learning: A Multi-Dataset Reproducibility Study**

Alternative title for journal fit:

**How Validation Units Change Apparent Generalisation in Literature-Derived Machine Learning for Adsorption: A Multi-Dataset Study-Aware Reanalysis**

The title is provisional until target-journal selection; the scientific scope below is locked.

## Central research question

> **How sensitive are apparent machine-learning generalisation results in literature-derived adsorption datasets to the unit at which observations are split, and under what corpus structures can strong source-held-out performance persist?**

## Core scientific contribution

Paper 1 is **not** a paper claiming discovery of GroupKFold, nor a paper claiming that random splitting is universally invalid.

Its contribution is a reproducible empirical study that combines:

1. a predeclared dataset-eligibility and non-cherry-picking protocol;
2. primary-study provenance reconstruction for literature-derived adsorption corpora whose modelling matrices do not always retain usable source IDs;
3. matched random-versus-primary-study-aware validation on the same rows, features and model family;
4. three independently reconstructed primary corpora with common RF and XGB comparisons;
5. reproduction of high conventional/random performance before imposing study separation in the external replications;
6. a lineage-overlapping matched sensitivity (Moosavi 2021) that is explicitly excluded from the independent-replication count;
7. independent published corroboration (Aguiar & Kasemodel 2026); and
8. a positive published source-aware counterexample (Huang et al. 2026) demonstrating that strong source-held-out performance can persist in a suitable corpus.

## Primary evidence set

### Dataset A — V2.1 strict comparable corpus
- 273 rows / 24 reconstructed primary studies.
- RF: random R² 0.9042 → grouped R² 0.0265.
- XGB: random R² 0.8936 → grouped R² 0.1929.
- Deepest provenance and validation audit.

### Dataset B — Liu 2025 dye/biochar corpus
- strict: 624 rows / 17 high-confidence primary-study groups.
- RF: random R² 0.930377 → grouped R² -0.339908.
- XGB: random R² 0.938244 → grouped R² -0.036089.
- CatBoost representative result: 0.935977 → 0.109642.
- Extended 668-row/19-group sensitivity retained separately.
- Published-style random diagnostic reproduces high conventional performance and is not substituted for matched validation.

### Dataset C — Liu ammonia-N/biochar corpus
- 409 rows / 7 reconstructed primary studies.
- Primary-study DOI set disjoint from Dataset A and Dataset B.
- RF: random R² 0.837380 → grouped R² -0.420734.
- XGB: random R² 0.851681 → grouped R² -0.640524.
- CatBoost representative result: 0.883650 → -0.058128.
- Public-style diagnostic reproduces the published random holdout almost exactly before study-aware validation.

### Common-model synthesis

RF and XGB are the pre-specified common model families available across all three independent matched corpora. Across the six common-model comparisons:

- random R² > grouped R² in 6/6;
- ΔR² ranges from 0.7007 to 1.492205;
- descriptive median ΔR² = 1.1162235;
- no formal meta-analytic pooling is claimed.

## Supporting evidence classes

### Moosavi 2021 — lineage-overlapping matched sensitivity
- 344 directly recoverable rows / 12 source references.
- published-hyperparameter nine-variable RF: 0.893093 random → 0.466536 grouped.
- retained as a sensitivity demonstrating a more moderate validation gap.
- **not counted as an independent replication** because the reconstructed source-study lineage overlaps historical V2.1.

### Aguiar & Kasemodel 2026 — published independent corroboration
- 1,098 experiments from 38 studies overall.
- broad M5 model: 726 rows / 23 studies.
- conventional CV R² 0.79 → source-GroupKFold R² approximately 0.66.
- confirms that adsorption-ML validation gaps are already recognized in current literature.
- therefore Paper 1 cannot claim first use/recommendation of study-aware validation.

### Huang et al. 2026 — positive source-aware counterexample
- 452 adsorption-capacity records.
- publication-level 4:1 source separation.
- preprocessing derived from training data only.
- XGB source-separated test R² 0.99; five-fold training R² 0.92 ± 0.04.
- demonstrates that source-aware validation does not inherently produce poor performance.
- raw modelling rows are author-request only; this project does not claim an independent rerun.

## Claims Paper 1 may make

1. **Row-random validation and primary-study-aware validation answer different scientific questions.** Random validation can estimate interpolation within the observed mixture; study-aware validation targets transfer to an unseen primary study.
2. **In the three independently reconstructed corpora analysed here, conventional row-random validation materially overestimates study-held-out performance for both RF and XGB.**
3. **The magnitude of this optimism is dataset dependent.** It ranges from moderate in the lineage-overlapping Moosavi sensitivity to severe in several independent matched comparisons.
4. **High random-split R² alone is insufficient evidence for transfer to unseen experimental studies.**
5. **Primary-study provenance is itself a reproducibility requirement.** Some public modelling matrices omit source identity even when the data were compiled from many papers.
6. **Strong source-aware performance is possible.** Huang 2026 prevents any universal claim that grouped validation necessarily destroys adsorption-ML performance.
7. **Dataset/domain design is likely more important than model shopping once the target claim is unseen-study transfer.** This is a discussion-level inference, not yet a causal result.

## Claims Paper 1 must not make

- Random splitting is always wrong.
- Study-aware validation always lowers performance.
- All adsorption ML is invalid or non-generalizable.
- This is the first adsorption paper to use/recommend GroupKFold.
- The descriptive median ΔR² is a formal pooled effect size.
- Moosavi 2021 is an independent external replication.
- Huang or Aguiar were rerun by this project.
- The two Liu datasets are independent research-team replications; their **primary-study corpora** are distinct, but the broader curation/research-team lineage overlaps.
- ID-SEAD stack superiority, inverse-design validation, universal QMAX=624 mg/g, or deployment readiness.

## Manuscript structure

### 1. Introduction
- literature-derived adsorption ML and the difference between rows and independent experimental studies;
- intended generalisation target versus validation unit;
- existing recognition of leakage/grouped-validation concerns;
- remaining gap: matched multi-dataset empirical quantification with explicit provenance reconstruction and independence accounting;
- research question and contributions.

### 2. Study protocol and evidence classification
- predeclared inclusion criteria;
- no outcome-based dataset selection;
- independent matched datasets versus lineage-overlap sensitivities versus published-only comparators;
- rules for unresolved provenance.

### 3. Dataset provenance and reconstruction
- V2.1 reconstruction;
- Liu dye reconstruction and strict/extended confidence classes;
- Liu ammonia reconstruction;
- Moosavi overlap finding;
- source IDs as non-predictive metadata only.

### 4. Matched validation methodology
- same observations/features/model in random and grouped arms;
- fold-safe preprocessing;
- GroupKFold by primary study and LOSO;
- common RF/XGB synthesis;
- dataset-specific CatBoost diagnostics where available;
- metrics and reporting conventions.

### 5. Results
#### 5.1 Reproducing strong conventional/random performance
Show that the external reconstruction pipelines recover performance consistent with the published random workflows before the study-aware intervention.

#### 5.2 Primary matched comparison across three independent corpora
Main table and paired plot for RF/XGB.

#### 5.3 Dataset-specific sensitivities
Liu extended grouping; CatBoost; Moosavi lineage-overlap sensitivity.

#### 5.4 Published contextual evidence
Aguiar corroboration and Huang positive counterexample.

### 6. Discussion
- why random and grouped validation estimate different deployment/generalisation tasks;
- why severe gaps occur in some corpora and not universally;
- source imbalance, domain coherence, study count and descriptor adequacy as hypotheses;
- implications for literature-derived adsorption ML reporting and dataset construction;
- why model complexity/stacking cannot compensate for an inappropriate validation unit.

### 7. Reporting recommendations
- retain row-level primary provenance;
- report both row count and independent-study count;
- predeclare target generalisation unit;
- use fold-safe preprocessing;
- group by the scientific unit matching the claim;
- report per-study/LOSO errors where practical;
- distinguish external-file validation from proven source independence;
- avoid target proxies and unsupported universal physical bounds.

### 8. Limitations
- three independently rerun corpora, not a field-wide meta-analysis;
- two Liu datasets share broader research-team/curation lineage although their underlying primary-study DOI sets are disjoint;
- request-only data prevent independent reruns of Huang/Aguiar/Yadav/Abu-Shareha within this project;
- some provenance reconstruction depends on published tables/source ordering and confidence classes;
- heterogeneous target domains prevent formal pooling of R² across datasets;
- study-aware validation still does not guarantee transfer to new adsorbate classes, feedstocks, laboratories, future time periods, or entirely novel descriptor space.

### 9. Conclusion
The conclusion must emphasize that the correct validation unit follows the intended claim. The project demonstrates substantial random-versus-study-aware gaps across multiple reconstructed corpora, while retaining counterevidence that strong source-aware performance can persist. The practical implication is methodological calibration of claims—not blanket rejection of adsorption ML.

## Figure plan

1. **Matched random versus study-aware R²** for common RF/XGB across three independent corpora.
2. **ΔR² validation gap** for the same six comparisons.
3. **Evidence-context panel**: representative independent reruns, Moosavi overlap sensitivity, Aguiar published corroboration, Huang positive source-aware comparator.
4. Provenance/evidence-class flow diagram if journal space permits.
5. Optional per-study LOSO distribution figure in supplement.

## Table plan

1. Dataset eligibility, provenance and independence classification.
2. Primary common-model matched results.
3. Dataset-specific sensitivities and published-performance reproduction diagnostics.
4. Published source-aware corroboration/counterexamples.
5. Reporting recommendations.

## Data-acquisition gate

Primary dataset hunting is closed. Request-only datasets may be revisited only if a concrete reviewer-level gap emerges. The manuscript should now be reconstructed from the locked evidence rather than delayed by indefinite additional screening.
