# ID-SEAD V2 — Source Dependence and Novelty Guardrails

Status: **active scientific safeguard; not a manuscript claim lock**

## Why this matters

The current 322-row modelling corpus contains 251 rows (77.95%) attributed to a Moosavi secondary compilation. That compilation corresponds to Moosavi et al. (2021), *A Study on Machine Learning Methods’ Application for Dye Adsorption Prediction onto Agricultural Waste Activated Carbon*, Nanomaterials 11(10), 2734, DOI 10.3390/nano11102734.

Moosavi et al. compiled 350 experimental records from 13 prior publications and used supervised ML (DT, RF and gradient boosting) for forward prediction of dye adsorption capacity and feature importance. Their reported RF performance reached approximately R² 0.92 with nine variables and R² 0.90 after feature selection.

Reusing part of that public/literature-derived corpus does **not by itself make ID-SEAD a replication**. The risk of being perceived as incremental becomes high, however, if the revised paper merely reruns alternative regressors on essentially the same rows and makes the same forward-prediction claim.

## Novelty line that must be preserved

The revised study should only claim novelty where the evidence supports a genuinely different research question, such as:

1. primary-study-aware / leakage-resistant validation rather than row-random validation;
2. evaluation across a broader heterogeneous adsorption corpus rather than only the Moosavi dye/activated-carbon domain;
3. explicit applicability-domain and uncertainty diagnostics;
4. source-ablation and external-transfer tests;
5. inverse design framed as candidate generation under uncertainty, not as experimentally validated optimum discovery;
6. physically/domain-qualified constraints, replacing the invalid universal `Q_MAX=624 mg/g` assumption.

If these contributions do not survive validation, the manuscript must be reframed rather than preserving the original title by force.

## Required anti-replication tests

Before journal submission, the evidence package must contain all of the following:

- **Primary provenance reconstruction** for the Moosavi-derived rows, so rows from the same underlying paper cannot leak across folds.
- **Dominant-source ablation:** report model behavior on the Moosavi subset, on non-Moosavi data, and transfer in both directions.
- **Leave-primary-study-out validation:** final grouped CV after provenance reconstruction.
- **Source-balanced reporting:** include study-level/equal-study summaries, not only row-weighted metrics.
- **Independent external validation:** datasets that were not used by Moosavi and are not represented in model fitting.
- **Novelty comparison table:** explicitly distinguish the Moosavi objective/method/data from the revised ID-SEAD objective/method/data.

## Publication positioning

Do **not** claim:

> First use of machine learning to predict adsorption performance of agricultural-waste adsorbents.

Moosavi et al. and other prior studies already cover that ground.

A defensible future claim, if supported by the completed experiments, would be closer to:

> A provenance-aware, domain-qualified framework for evaluating and inversely designing agricultural-waste adsorption systems from heterogeneous literature data.

This wording remains provisional until primary-study validation, applicability-domain analysis and external validation are complete.

## Dataset-diversification recommendation

The present corpus is too dependent on one secondary compilation for a strong general-purpose claim. Provenance reconstruction is necessary but not sufficient. After reconstruction, the next data-curation phase should deliberately add independent primary studies from under-represented material classes and pollutant classes, with source IDs retained at row level. The objective is not an arbitrary row count; it is broader independent-study coverage and reduced dependence on any one compiled source.
