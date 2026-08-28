# Liu et al. ammonia-N adsorption — matched study-aware replication findings

Status: **CI-VERIFIED INDEPENDENT MATCHED REPLICATION**

Paper: *Machine learning prediction of ammonia nitrogen adsorption on biochar with model evaluation and optimization*, npj Clean Water 8, 13 (2025). DOI: `10.1038/s41545-024-00429-z`.

## 1. Reproducibility and data recovery

The article reports **417 literature-derived observations** and an ordinary random 80:20 train/test split. The repository linked by the paper (`17609858895/Ammonia-nitrogen`) currently omits the raw modelling workbook, but Git history shows that `Original.xlsx` was explicitly deleted on 23 December 2024 (commit `6905f8e047ad865216d17b4c7ad052d3fd3bb2be`). The exact pre-deletion workbook remains recoverable from parent commit `25f525f7e67771367948087f18e6c91ee8fa994f`.

Historical workbook SHA-256:

`e9f334ca479673aa3f753151d64573b74c13cc8d26235e804509657123d79ff0`

The historical workbook contains:

- `Original`: 430 rows
- `Full`: **417 rows**, matching the article's reported collected population
- `Final`: 416 rows
- `Literature collected`: source bibliography

The public CatBoost notebook applies a target gate `Q <= 10` before modelling and globally fits KNN imputation, Box-Cox transformation, and standardisation before its random split. Reconciliation of the historical sheets and executable code produces a **409-row modelling population**.

## 2. Primary-study provenance reconstruction

The 409 modelled rows were reconstructed to **7 contributing primary studies** using the ordered literature ledger plus source-specific feedstock/material blocks retained in the historical workbook. No study identifier was inferred solely from a model result.

| Primary study / source | DOI | Model rows |
|---|---|---:|
| Fruit-peel biochars | `10.1016/j.scitotenv.2019.135544` | 180 |
| Multi-feedstock Gai et al. biochars | `10.1371/journal.pone.0113888` | 95 |
| Food-waste biochars | `10.1016/j.biortech.2019.121927` | 64 |
| *Thalia dealbata* biochars | `10.1007/s11356-022-19870-z` | 41 |
| Digested-sludge biochar | `10.1016/j.jclepro.2018.10.268` | 13 |
| Reed-straw/clay-biochar composite | `10.1007/s11802-020-4150-9` | 12 |
| Engineered sewage-sludge/willow biochars | `10.1016/j.jclepro.2021.129994` | 4 |

Largest-study contribution: **180/409 = 44.01%**.

Three bibliography entries were assigned zero rows rather than guessed:

- `10.1038/s41598-022-08591-5`
- `10.2166/aqua.2020.062`
- `10.1007/s10653-019-00474-5`

A Ca-modified soybean-straw source (`10.1371/journal.pone.0290714`) is identifiable in the earlier raw sheet but contributes no rows to the final executable modelling population.

Seven final-sheet observations with `Q > 10` are removed by the public-code target gate. The resulting primary matched population is therefore **409 rows / 7 primary studies**.

## 3. Independence from Dataset V2.1

None of the seven model-contributing primary-study DOIs appears in the 29-study V2.1 bibliography. The ammonia-N corpus is therefore **primary-source independent of Dataset V2.1**.

The ammonia-N and Liu dye corpora also use disjoint contributing primary-study DOI sets. However, both public datasets were curated by the same broader author/repository lineage. Paper 1 must therefore distinguish **independent underlying primary-study corpora** from **independence of the dataset-curation research team**.

## 4. Public-pipeline reproducibility diagnostic

A deliberately public-style diagnostic reproduces the repository's preprocessing order: global KNN imputation, global Box-Cox transformation, global standardisation, then random 80:20 splitting.

Using fixed CatBoost500 on the reconstructed 409-row population:

- test R² = **0.932643**
- test RMSE = **0.538641**
- test MAE = **0.353891**

The article reports CatBoost test R² = **0.9329** and RMSE = **0.5378**. The near-exact agreement strongly supports the reconstructed executable modelling population.

This globally preprocessed diagnostic is **not** the matched random-versus-grouped comparator.

## 5. Matched fold-safe validation

For the matched experiment, the exact same 409 rows, predictor definition, and fixed model specification are used in both arms. KNN imputation, Box-Cox transformation and scaling are fitted within each training fold only.

| Model | Random 5-fold R² | Primary-study GroupKFold R² | ΔR² | LOSO R² |
|---|---:|---:|---:|---:|
| RF500 | **0.837380** | **-0.420734** | **1.258114** | -0.421031 |
| XGB500 | **0.851681** | **-0.640524** | **1.492205** | -0.649272 |
| CatBoost500 | **0.883650** | **-0.058128** | **0.941778** | -0.054673 |

CatBoost error metrics:

- random RMSE = **0.674666**
- grouped RMSE = **2.034582**
- random MAE = **0.423072**
- grouped MAE = **1.417852**

Thus the strong row-random signal does not survive transfer to completely unseen primary studies in this corpus.

## 6. Interpretation

This result is not interpreted as proof that ammonia-N adsorption is intrinsically unpredictable. The corpus contains only seven model-contributing primary studies and is highly imbalanced, with one study contributing 44% of the rows. The result instead demonstrates that hundreds of literature observations and many biochar variants do not necessarily represent hundreds of independent experimental systems.

The scientifically supported conclusion is:

> For this independently sourced ammonia-N corpus, conventional row-random validation substantially overestimates performance for the distinct estimand of transfer to an unseen primary study.

## 7. CI evidence

Matched-validation workflow:

- run: `33206265927`
- conclusion: `success`
- artifact: `9699800084`
- artifact SHA-256: `5195a8ce6632e337935966fe5b23d0ccc22d3b51b0deb1641945f19a8e7e64ff`

Historical-data screen:

- run: `33205801642`
- artifact: `9699597804`
- artifact SHA-256: `801e0dca5e8cb4cf30e344acbda98140525348b97d22829b098f620c61aacc6e`

## 8. Paper 1 role

Classify this dataset as:

**CI-VERIFIED INDEPENDENT MATCHED REPLICATION — independent primary-source corpus; shared dataset-curation team lineage with Liu dye 2025.**

It is the second primary-source-independent matched corpus added after the V2.1 deep case, and it materially strengthens the empirical evidence for a validation-design gap while preserving the outcome-neutral protocol.
