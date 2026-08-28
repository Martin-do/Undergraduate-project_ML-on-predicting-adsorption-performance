# Paper 1 — Verified Core Reference Ledger

Verification date: **2026-08-28**

Purpose: prevent incomplete or invented bibliography entries during manuscript reconstruction. This ledger contains the core methodological and benchmark references already used in Draft V1. The complete provenance bibliography for Dataset A will remain a supplementary/source-ledger product and will be reconciled separately.

## R1 — Structured-data cross-validation methodology

Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*, 913–929. DOI: `10.1111/ecog.02881`.

**Verification:** Wiley/DOI record checked. The article explicitly discusses hierarchical dependence, predictive-error bias under uncorrected random CV, and the need to choose blocking according to the prediction problem.

## R2 — Contemporary methodological prior art in biochar ML

Cahyana, D., & Jang, H. J. (2025). Addressing data handling shortcomings in machine learning studies on biochar for heavy metal remediation. *Journal of Hazardous Materials, 491*, 137887. DOI: `10.1016/j.jhazmat.2025.137887`.

**Verification:** ScienceDirect and PubMed records checked. The paper explicitly discusses data leakage and inadequate dataset splitting in compiled biochar/experimental ML data.

**Novelty implication:** Paper 1 must not claim that grouped validation, leakage awareness, or the general dependence problem is newly discovered here.

## R3 — Liu dye matched benchmark

Liu, C., Balasubramanian, P., Nguyen, X. C., An, J., Praneeth, S., Zhang, P., & Huang, H. (2025). Enhanced machine learning prediction of biochar adsorption for dyes: Parameter optimization and experimental validation. *Carbon Research, 4*, 46. DOI: `10.1007/s44246-025-00213-9`.

**Verification:** Springer Nature/Carbon Research publisher record checked. The article reports CatBoost R² = 0.9880 and is the source paper for the public biochar–dye workbook used in the matched reanalysis.

**Project role:** strict reconstructed population 624 rows / 17 primary studies; primary representative matched CatBoost500 R² 0.935977 random → 0.109642 grouped.

## R4 — Liu ammonia-N matched benchmark

Liu, C., Balasubramanian, P., An, J., & Li, F. (2025). Machine learning prediction of ammonia nitrogen adsorption on biochar with model evaluation and optimization. *npj Clean Water, 8*, 13. DOI: `10.1038/s41545-024-00429-z`.

**Verification:** Nature Portfolio, Crossmark/Crossref and DOAJ records checked. The article was published 22 February 2025 and lists four authors: Chong Liu, Paramasivan Balasubramanian, Jingxian An and Fayong Li. The reported CatBoost test performance is R² = 0.9329 and RMSE = 0.5378.

**Project role:** historical raw workbook recovered from the linked Git repository history; executable matched population 409 rows / 7 primary studies; representative CatBoost500 R² 0.883650 random → -0.058128 grouped.

## R5 — Moosavi lineage sensitivity

Moosavi, S., Manta, O., El-Badry, Y. A., Hussein, E. E., El-Bahy, Z. M., Mohd Fawzi, N. F. B., Urbonavičius, J., & Moosavi, S. M. H. (2021). A Study on Machine Learning Methods’ Application for Dye Adsorption Prediction onto Agricultural Waste Activated Carbon. *Nanomaterials, 11*(10), 2734. DOI: `10.3390/nano11102734`.

**Verification:** MDPI, PubMed/PMC and institutional publication records checked.

**Project role:** 344/350 numbered supplementary rows are directly recoverable; source-lineage audit shows overlap with Dataset A historical lineage. It is therefore a matched **lineage sensitivity**, not an independent replication.

## R6 — Independent cross-team published corroboration

Aguiar, L. G., & Kasemodel, M. C. (2026). Application of random forest regression in modeling the adsorption of methylene blue onto clays. *Neural Computing and Applications, 38*, 496. DOI: `10.1007/s00521-026-12200-1`.

**Verification:** Springer Nature publisher record checked; published 15 June 2026.

**Relevant published evidence:** 1,098 experiments from 38 independent studies. The largest M5 model uses 726 observations from 23 studies and reports conventional CV R² ≈ 0.79 versus study-grouped R² ≈ 0.66, with MAE ≈ 48 and RMSE ≈ 69.

**Project role:** independent cross-team corroboration. Not counted as one of our own matched computational reruns.

## R7 — Positive source-aware comparator

Huang, X., Bai, X., Yang, Y., Li, W., & Xu, D. (2026). Machine Learning-Based Prediction and Optimization of Heavy Metal Adsorption Performance of Biochar. *Forests, 17*(3), 326. DOI: `10.3390/f17030326`.

**Verification:** MDPI publisher record checked; published 5 March 2026.

**Relevant published evidence:** 452 adsorption-capacity records. The article separates train/test observations at the literature-source level, derives preprocessing from training data, and reports XGB test R² = 0.99 with training five-fold CV R² = 0.92 ± 0.04.

**Project role:** positive source-aware comparator demonstrating that study/publication-aware validation does not inevitably produce poor performance.

---

## Citation-use rules for Draft V1 onward

1. Do not cite R5 (Moosavi) as independent replication.
2. Do not describe R6 (Aguiar) as a project rerun; use the authors' published results only.
3. Do not describe R7 (Huang) as independently reproduced; raw modelling data are currently available only on request.
4. R2 establishes important prior art; Paper 1 novelty must be framed as provenance reconstruction + matched multi-corpus empirical quantification + source-lineage audit + executable performance reproduction + outcome-neutral comparison.
5. Add new references to the manuscript only after DOI/publisher or equivalent authoritative verification.
6. Before submission, replace any provisional `et al.` bibliography entry in the manuscript with the verified author list from this ledger or another authoritative record.
