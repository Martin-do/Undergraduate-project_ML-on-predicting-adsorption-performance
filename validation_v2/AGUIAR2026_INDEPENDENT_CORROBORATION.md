# Aguiar & Kasemodel 2026 — Independent Published Corroboration

Status: **INDEPENDENT PUBLISHED RANDOM-VS-GROUPED ADSORPTION COMPARISON**

Citation: Leandro G. Aguiar and Mariana C. Kasemodel. *Application of random forest regression in modeling the adsorption of methylene blue onto clays*. Neural Computing and Applications 38, 496 (2026). DOI: `10.1007/s00521-026-12200-1`.

## Why this study matters

This paper was published independently of the present project and directly compares conventional validation with study-grouped cross-validation on a literature-derived adsorption dataset. It is therefore strong external corroboration of Paper 1's central methodological question.

The article compiles **1,098 methylene-blue adsorption experiments from 38 independent studies**. Separate RF models are constructed depending on feature completeness rather than imputing unreported variables.

## Validation designs

The paper explicitly distinguishes:

1. conventional validation, in which observations are distributed without enforcing study separation; and
2. `GroupKFold` validation, in which rows are grouped by their source study/reference so that one article cannot contribute rows to both training and validation within a fold.

The authors explicitly state that the group-based analysis is intended to provide a more realistic estimate of generalisation across independent datasets.

## Representative published results

Under conventional cross-validation the five representative RF models report:

| Model | Experiments | Conventional CV R2 |
|---|---:|---:|
| M1 | 64 | 0.94 |
| M2 | 165 | 0.92 |
| M3 | 283 | 0.87 |
| M4 | 422 | 0.80 |
| M5 | 726 | **0.79** |

Model M5 is the largest and most diverse subset, comprising **726 observations from 23 studies**. Under study-grouped validation, M5 retains approximately **R2 = 0.66**, with MAE about 48 mg/g and RMSE about 69 mg/g.

The paper reports substantially poorer grouped results for several smaller/more feature-rich subsets, including negative R2 values in some cases. It concludes that conventional validation can overestimate predictive performance when correlations within source studies are not accounted for.

## Interpretation for Paper 1

This study is important because it was not selected or reanalysed by the present authors after seeing an expected performance collapse. It is an independent contemporary publication reaching a compatible conclusion using a different adsorbent domain (clays rather than biochar/activated carbon) and a substantially larger literature compilation.

At the same time, M5 retains a meaningful grouped R2 of about 0.66. This supports Paper 1's outcome-neutral interpretation:

> Study-aware validation often lowers apparent performance, but the amount of reduction depends on dataset structure, domain coherence and independent-study coverage. Some datasets retain useful transferable signal.

## Counting rule

Aguiar 2026 is **not counted as one of our own matched computational replications**, because we are citing the authors' published conventional and grouped results rather than rerunning their dataset. It is classified as independent published corroboration within the literature-practice layer.

Public evidence checked 2026-08-28 from the open-access Springer article.
