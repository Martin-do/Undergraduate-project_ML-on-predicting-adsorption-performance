# ID-SEAD Independent Review Response — V2

Status: **review actions executed; conference manuscript requires V2 rewrite before finalisation**  
Independent review received: 2026-08-30

## Executive disposition

The independent review did **not** overturn the conference salvage. It independently reproduced the central qualitative validation effect and agreed that the legacy R²=0.847, QMAX=624, Table III, stacking-superiority and deployment claims should not be defended.

However, the review identified a mechanistic question that materially improved the analysis: whether study-correlated material/pollutant/context categories in the corrected feature-parity representation were themselves driving negative transfer. The reviewer was right to require this test.

The resulting ablation changes the conference interpretation:

- the **full engineered representation** still reproduces the severe row-random versus unseen-study gap;
- removing identity-adjacent engineered categories recovers substantial study-aware predictive performance;
- therefore the extreme collapse was partly a **feature-representation / proxy-learning problem**, not evidence that useful cross-study forward prediction is impossible on the entire strict corpus;
- despite this recovery, the original agricultural-waste inverse-design claim remains unsupported and the broader domains retain reliability failures that block actionable inverse design.

The revised conference paper must present that complete result rather than the earlier one-directional collapse narrative.

## Review point → action → result → disposition

| Review concern | Action taken | Result | Conference disposition |
|---|---|---|---|
| Reviewer pack omitted the actual modelling scripts | Repository source path rechecked; final pack will include the current `validation_v2` modelling/preprocessing scripts plus reviewer-gate scripts and outputs | The source code was present in GitHub; omission was a packaging defect | **Closed for next pack** |
| Material/context categories may act as study-identity proxies | Ran matched RF/XGB ablation: full engineered vs no identity-adjacent categories vs physical numeric only; followed with full LOSO and domain LOSO | Removing context categories raises RF grouped R² 0.0265→0.6370 and LOSO 0.0085→0.6278; physical numeric RF grouped 0.5796 / LOSO 0.5734 | **Major scientific finding; manuscript interpretation changed** |
| Cluster-size imbalance / singleton concern | Quantified study-size distribution and effective study count; ran n>=5 LOSO sensitivity | 8, not 10, singleton studies; top five studies are 71.79% of rows; 12 studies have n>=5. Category-stripped improvement persists for n>=5 studies (RF LOSO ≈0.616) | **Concern acknowledged and robustness passed** |
| Missingness is not disclosed | Quantified parsed missingness; ran feature-removal sensitivity; crossed missingness removal with category stripping | Dose 61.54% missing; contact time 38.10%. Removing both does not remove improved transfer; no-identity RF grouped 0.6522 / LOSO 0.6549 | **Limitation must be disclosed; not driver of recovered transfer** |
| Table I hides grouped-fold instability | Reconstructed per-fold metrics and fold manifest | Full-engineered grouped RF fold R² mean -6.45, SD 8.47; XGB -4.29, SD 5.47. Pooled R² remains matched whole-population statistic | **Report dispersion / avoid stable-fold interpretation** |
| Need well-powered-study-only robustness | Ran two n>=5 sensitivities: hold out only n>=5 studies while retaining all other training studies; and refit population using only n>=5 studies | No-identity RF R² ≈0.616 and ≈0.615 respectively; physical-only also remains positive ≈0.56–0.59 | **Small clusters do not explain recovered transfer** |
| Broad-biogenic pooled R² may conceal catastrophic failure | Recomputed domain LOSO under feature ablation and inspected study-level predictions | Broad-biogenic XGB no-identity R² ≈0.642 but Alshabib MAE remains 1489.39 mg/g | **Pooled domain result remains diagnostic only** |
| “Agreement ≠ correctness” should be promoted | Rechecked the Alshabib study after category removal | No-identity RF/XGB differ by only 29–51 mg/g (mean 40.27) while both are ≈1.5 g/g wrong | **Core inverse-design reliability warning survives ablation** |
| Reviewer could not independently verify exact metrics from supplied ZIP | Next reviewer pack will include the modelling code, current workflow scripts, outputs and hashes; full public branch remains authoritative | Original reviewer independently verified qualitative effect using a different pipeline; exact-author-pipeline auditability will be improved in V2 pack | **Packaging action required before re-review** |

## Specific corrections to the independent review

### Singleton count

The review stated that 10 of 24 strict-comparable studies contribute exactly one row. Direct reconstruction using the canonical strict-273 set gives **8 singleton studies**.

The larger conclusion is unchanged: cluster sizes are highly imbalanced, with the top five studies contributing **196/273 = 71.79%** of rows and a Kish row-weight effective study count of **7.62**.

### Reproducibility-code availability

The review correctly described the supplied ZIP as non-executable because the wrapper imported files that were omitted from that ZIP. The following current scripts do exist on `conference/id-sead-salvage` and will be included in the corrected handoff:

- `validation_v2/build_dataset_v21.py`
- `validation_v2/final_validation_v21.py`
- `validation_v2/robustness_validation_v21.py`
- `validation_v2/study_aware_validation.py`
- `validation_v2/feature_parity_validation.py`
- `validation_v2/feature_parity_validation_fixed.py`
- associated mapping/source files required by the runner.

The omission should therefore be described as **incomplete reviewer packaging**, not absence of a reproducibility pipeline.

## What the reviewer was most importantly right about

The original corrected conference draft implicitly attributed the large random/grouped gap mainly to clustered study dependence and corpus heterogeneity. That was incomplete.

The reviewer correctly pointed out that derived material/context categories could encode study-correlated information. The post-review ablation provides strong evidence for that mechanism:

- row-random accuracy remains fairly high after removing those categories (~0.82 R²),
- but study-aware transfer improves dramatically,
- which means the removed categories were useful for within-study discrimination while harmful for transfer to unseen studies.

This makes the conference contribution more specific:

> **Study-aware validation can act as a feature-representation diagnostic, revealing context variables that appear predictive under row-wise validation but induce negative transfer across studies.**

That is a stronger engineering lesson than merely repeating that grouped validation is stricter.

## Why the inverse-design gate still fails

The improved forward-prediction result must not be mistaken for a restored inverse-design claim.

1. The strict agricultural-waste domain remains only 65 rows / 4 studies and performs badly under every representation.
2. The promising broad-biogenic domain still contains a complete held-out study for which RF and XGB are both wrong by roughly 1.5 g/g.
3. The category-stripped representation that transfers better deliberately removes material/pollutant categories; a prescriptive adsorbent-process design system cannot silently discard the very context required to define what material/pollutant is being designed for.
4. Dose and contact time are heavily missing.
5. Independent-study depth is limited and imbalanced.
6. Legacy test-informed model selection, QMAX=624, optimizer/target lineage conflict and target-objective mismatch remain historical defects.
7. No external or laboratory verification supports a new inverse-design recommendation.

## Revised conference contribution

The paper should no longer be framed as simply:

> random validation looked good, grouped validation collapsed, therefore the dataset cannot generalise.

It should be framed as:

> ID-SEAD is used as a forensic engineering case study showing that (i) conventional validation can conceal source dependence; (ii) study-aware evaluation can expose harmful feature representations; (iii) representation correction can recover meaningful forward transfer; but (iv) predictive recovery alone is still insufficient for reliable inverse design when domain coverage, contextual completeness and failure detection remain inadequate.

## Revision status

- reviewer-gate CI: **PASS**;
- final revision-gate run ID: `33338908933`;
- job ID: `99330787391`;
- artifact ID: `9739944134`;
- head SHA: `6e048d106a33f241c3a2161ae9f2827cf05f653b`;
- artifact digest: `sha256:9fecfe3121f7ed2e216cf81eb9d2b7c1441bfd90a8701cd3a36b593dd7a18940`.

## Required before resending for independent review

1. Replace the conference manuscript with V2 based on `POST_REVIEW_NUMERIC_SOURCE_OF_TRUTH.md`.
2. Replace the old validation-collapse figure with a representation × validation comparison figure.
3. Add explicit missingness and study-size disclosures.
4. Label all feature-ablation work as reviewer-triggered/post-review sensitivity analysis.
5. Preserve the strict-agricultural failure and broad-biogenic catastrophic failure in the main text.
6. Rebuild the reviewer pack with the actual modelling/preprocessing source code and new revision-gate results.
7. Update the defence dossier so it no longer claims the full-engineered collapse is representation-independent.
