# Paper 1 — Revised Multi-Dataset Manuscript Scope

Status: **MANUSCRIPT RECONSTRUCTION STARTED AFTER EVIDENCE FREEZE**

Evidence authority: `PAPER1_MULTIDATASET_EVIDENCE_FREEZE.md` + `MULTIDATASET_RESULTS_REGISTRY.csv`

## Working title

**Validation-Unit Sensitivity in Literature-Derived Adsorption Machine Learning: A Multi-Dataset Study-Aware Reanalysis**

Alternative title for journal targeting:

**When Row-Random Validation Does Not Measure Unseen-Study Transfer: Evidence from Literature-Derived Adsorption Machine Learning**

The first title is preferred at reconstruction start because it remains outcome-neutral and accurately represents the multi-dataset design.

## Central research question

**How sensitive are performance estimates in literature-derived adsorption machine learning to the scientific unit at which observations are separated for validation, and when does row-level interpolation fail to represent transfer to an unseen primary study?**

## Primary contribution

This is not a novel-model paper and not a paper whose novelty is simply recommending GroupKFold.

The contribution is a reproducible, multi-layer assessment of **claim–validation alignment** in literature-derived adsorption ML, combining:

1. reconstruction of primary-study provenance;
2. matched random-versus-study-aware validation on fixed observations and models;
3. replication of original high row-random performance before changing validation design;
4. explicit primary-source overlap/double-counting audits;
5. comparison across distinct adsorption targets and corpus structures;
6. independent published corroboration from another research team;
7. a positive source-aware comparator where strong performance survives stricter validation.

## Evidence hierarchy

### Tier 1 — Primary matched computational evidence generated in this project

#### Dataset A: V2.1 deep case
273 rows / 24 studies.

Representative XGB:
- random R² 0.8936
- study-aware R² 0.1929
- ΔR² 0.7007
- LOSO R² 0.1624

#### Dataset B: Liu dye/biochar 2025
624 strict rows / 17 studies.

Representative CatBoost500:
- random R² 0.935977
- study-aware R² 0.109642
- ΔR² 0.826335
- LOSO R² 0.059409

Original-style random performance is independently reproducible before regrouping.

#### Dataset C: Liu ammonia-N/biochar 2025
409 rows / 7 studies.

Representative CatBoost500:
- random R² 0.883650
- study-aware R² -0.058128
- ΔR² 0.941778
- LOSO R² -0.054673

Public-style random holdout R² 0.932643 closely reproduces published 0.9329.

Datasets B and C have disjoint primary-study DOI sets but share a broader data-curation/author-team lineage. This distinction is disclosed explicitly.

### Tier 2 — Lineage sensitivity

Moosavi 2021:
- 344 rows / 12 references
- RF random 0.893093
- grouped 0.466536
- Δ 0.426557

Not counted as independent because its recoverable source-study lineage overlaps V2.1.

### Tier 3 — Independent published corroboration

Aguiar & Kasemodel 2026:
- 1,098 methylene-blue/clay experiments / 38 studies
- largest M5 726 / 23 studies
- conventional CV ~0.79
- grouped ~0.66

This supplies cross-team corroboration and demonstrates a smaller, non-catastrophic validation gap in a different adsorbent domain.

### Tier 4 — Positive source-aware comparator

Huang et al. 2026:
- 452 heavy-metal/biochar records
- publication-level train/test separation
- training-only preprocessing
- XGB test R² 0.99
- training CV 0.92 ± 0.04

This prevents a universal-collapse narrative.

## Manuscript thesis

The paper should establish four propositions, in this order:

1. **Rows are not automatically independent scientific units.** Literature-derived adsorption datasets may contain many observations per primary publication or experimental campaign.
2. **Validation design answers a particular generalisation question.** Row-random splitting can be valid for interpolation among already represented systems, but it does not by itself estimate transfer to an unseen primary study.
3. **The difference is empirically large in several reconstructed corpora.** Matched experiments show substantial random-to-study-aware performance gaps while holding observations, predictors and models fixed.
4. **The gap is not universal.** Its magnitude depends on corpus structure, domain coherence, study count, study imbalance and descriptor informativeness; some source-aware datasets retain strong performance.

## Results structure

### 3.1 Literature-practice and validation-design context

Summarise contemporary adsorption-ML practices:
- row-random splitting remains common;
- some recent studies explicitly use publication-aware validation;
- recent methodological criticism already recognises leakage/data-handling risks.

This section establishes that practice is inconsistent, not that grouped validation is newly invented.

### 3.2 Dataset provenance and independence structure

For each empirical corpus report:
- total observations;
- independent primary studies;
- rows/study distribution;
- largest-study share;
- unresolved provenance;
- cross-corpus source overlap.

A key message is that **row count and independent-study count are different sample-size concepts**.

### 3.3 Reproduction of conventional random-performance regimes

Before presenting grouped results, show that public/original random performance can be reproduced where executable evidence permits:

- Liu dye public-style optimized CatBoost: high random score reproduced;
- Liu ammonia public-style CatBoost: 0.932643 vs published 0.9329;
- Moosavi five-variable RF: random reconstruction ~0.808 vs published ~0.81.

This addresses the alternative explanation that grouped degradation results from failed reproduction of the original models.

### 3.4 Matched random-versus-study-aware performance

Primary figure/table compares fixed-model matched results.

Representative headline cases:

| Corpus | Model | Rows / studies | Random R² | Study-aware R² | ΔR² |
|---|---|---:|---:|---:|---:|
| V2.1 | XGB | 273 / 24 | 0.8936 | 0.1929 | 0.7007 |
| Liu dye | CatBoost500 | 624 / 17 | 0.9360 | 0.1096 | 0.8263 |
| Liu ammonia-N | CatBoost500 | 409 / 7 | 0.8837 | -0.0581 | 0.9418 |
| Moosavi lineage sensitivity | RF | 344 / 12 | 0.8931 | 0.4665 | 0.4266 |

Moosavi must be visually or textually marked as lineage-overlapping, not a fourth independent corpus.

### 3.5 LOSO and study-level heterogeneity

Report pooled LOSO plus study-level errors rather than pooled R² alone.

Emphasise:
- performance varies materially among held-out studies;
- high row count can coexist with few and imbalanced study groups;
- ammonia-N largest source = 44.01% of rows;
- Liu dye largest source ≈17.63%;
- V2.1 includes 24 strict studies and remains heterogeneous.

### 3.6 Counterevidence and boundary conditions

Use Aguiar and Huang to show:
- some datasets lose moderately rather than catastrophically;
- some publication-aware workflows retain high performance;
- study-aware validation is a stricter estimand, not an automatic mechanism for generating low R².

## Discussion structure

### 4.1 Interpolation versus unseen-study transfer
Explain the estimand distinction without calling every random split 'wrong'.

### 4.2 Why validation gaps arise
Discuss plausible mechanisms:
- repeated measurements from same experimental campaign;
- material-specific fingerprints repeated across rows;
- laboratory/protocol effects;
- source-specific target ranges;
- study imbalance;
- domain heterogeneity;
- incomplete physicochemical descriptors.

Avoid causal claims that cannot be isolated experimentally.

### 4.3 Provenance is part of the ML method
A literature-derived dataset needs a source hierarchy, not just a flat CSV.

### 4.4 What the results do not show
They do not establish:
- that all published adsorption ML is invalid;
- that random splitting is intrinsically improper;
- that grouped scores are unbiased estimates of every deployment scenario;
- that adsorption ML lacks transferable signal;
- that a particular model family is generally superior.

### 4.5 Reporting recommendations
Require/recommend:
- observations + independent-study count;
- source IDs preserved at row level;
- largest-study share;
- validation unit linked to stated claim;
- fold-safe preprocessing;
- random interpolation metric and study-aware transfer metric where both are scientifically relevant;
- per-study/LOSO diagnostics;
- provenance and source-overlap disclosure for external validation.

## Proposed final figures

1. **Figure 1 — Evidence/provenance flow:** literature rows → primary-study groups → matched validation designs.
2. **Figure 2 — Random versus study-aware R²:** paired corpus/model estimates; lineage sensitivity visibly distinguished.
3. **Figure 3 — Validation-gap magnitude versus corpus structure:** ΔR² alongside study count/largest-study share; descriptive, not causal regression unless sample size justifies it.
4. **Figure 4 — Study-level LOSO error distributions:** primary matched corpora.
5. **Figure 5 — Claim–validation alignment schematic:** interpolation within represented systems versus transfer to unseen studies.

## Proposed final tables

1. Corpus/provenance summary.
2. Original/public random-performance reproducibility checks.
3. Matched random-versus-grouped metrics.
4. LOSO/per-study robustness summary.
5. Literature-practice audit and comparator studies.
6. Recommended reporting checklist.

## Abstract direction

The abstract must lead with the methodological problem, not with the historical ID-SEAD project. It should state that literature-derived adsorption datasets contain hierarchical dependence, describe the predeclared multi-dataset matched design, report representative performance gaps, mention the positive comparator/boundary condition, and conclude with claim–validation alignment.

## Historical ID-SEAD disposition

The ID-SEAD name, stack novelty, universal QMAX constraint and inverse-design claims are not part of the main contribution. The old project appears only as the historical origin of Dataset V2.1 if needed for transparency.

## Immediate reconstruction tasks

1. generate final manuscript tables directly from the deterministic registries;
2. generate paired-performance and study-composition figures;
3. rewrite Abstract, Introduction, Methods, Results, Discussion and Conclusion around this scope;
4. verify all cited literature and primary-study metadata;
5. select the target journal only after the manuscript's final methodological emphasis and length are known;
6. run final manuscript↔registry numerical reconciliation before submission.
