# Paper 1 — Verified Literature-Practice Context V1

Verification date: **2026-08-28**

Purpose: support the Introduction's statement that validation practice in literature-derived adsorption ML is heterogeneous. This is a **bounded illustrative context set**, not a systematic review and not a prevalence estimate. Papers are included only when their split/grouping practice could be verified from a publisher/full-text source or from the executable/public materials already audited in this project.

## A. Observation-level / globally randomized examples

### 1. Yadav et al. 2025 — Congo red adsorption by biochar

**Paper:** Yadav, S., Rajput, P., Balasubramanian, P., Liu, C., Li, F., & Zhang, P. *Machine learning-driven prediction of biochar adsorption capacity for effective removal of Congo red dye.* Carbon Research 4, 11 (2025). DOI: `10.1007/s44246-024-00168-3`.

**Verified practice:** The article states that the literature-derived dataset was split **80:20** into training and test data with `random_state=42`, followed by **10-fold cross-validation** for model/hyperparameter evaluation. The scaler was fitted on training data and applied to train/test.

**Reported headline performance:** RF test R² = **0.9785**; RF 10-fold CV R² = **0.9762**.

**Why it is relevant here:** The split is at the row/observation level rather than by source publication. The paper describes the held-out rows as unseen data; Paper 1 should use it as an example of an observation-level generalisation design, not as evidence that the result is invalid.

### 2. Liu et al. 2025 — dye adsorption by biochar

**Paper:** Liu, C., Balasubramanian, P., Nguyen, X. C., An, J., Praneeth, S., Zhang, P., & Huang, H. *Enhanced machine learning prediction of biochar adsorption for dyes: Parameter optimization and experimental validation.* Carbon Research 4, 46 (2025). DOI: `10.1007/s44246-025-00213-9`.

**Verified practice:** Public/paper workflow uses ordinary row-level training/test and cross-validation rather than primary-publication grouping. The executable reconstruction reproduces very high conventional random performance before source-aware regrouping.

**Reported headline performance:** CatBoost R² = **0.9880**.

**Project matched evidence:** strict 624 rows / 17 reconstructed primary studies; fixed CatBoost500 random R² = **0.935977**, GroupKFold R² = **0.109642**.

### 3. Liu et al. 2025 — ammonia-N adsorption by biochar

**Paper:** Liu, C., Balasubramanian, P., An, J., & Li, F. *Machine learning prediction of ammonia nitrogen adsorption on biochar with model evaluation and optimization.* npj Clean Water 8, 13 (2025). DOI: `10.1038/s41545-024-00429-z`.

**Verified practice:** Public workflow uses an ordinary **80:20 random split** and repeated row-level K-fold evaluation. The historical workbook and executable pipeline were recovered in this project.

**Reported headline performance:** CatBoost test R² = **0.9329**, RMSE = **0.5378**.

**Project reproduction:** public-style reconstruction R² = **0.932643**, RMSE = **0.538641**; matched 409 rows / 7 primary studies give CatBoost500 random R² = **0.883650**, grouped R² = **-0.058128**.

### 4. Abu-Shareha et al. 2026 — Cd(II) adsorption by biochar

**Paper:** *Robust Data driven modeling of Cd(II) adsorption on biochar.* Journal of Hazardous Materials Advances 21, 101004 (2026). DOI: `10.1016/j.hazadv.2026.101004`.

**Verified practice:** The article explicitly states that its 1,150 pooled literature observations were globally randomized into **90% training / 10% validation irrespective of literature source**. It argues that distributing source/laboratory effects across both partitions supports generalisation testing. Five-fold CV is also performed by randomly dividing observations into folds.

**Reported headline performance:** CNN, AdaBoost and RF report R² values above **0.99** in the study's evaluation framework.

**Why it is relevant here:** This is a particularly clear contemporary example of the exact estimand distinction examined in Paper 1: the authors intentionally mix literature sources across train/test, whereas our unseen-primary-study estimand requires keeping source groups separate. The manuscript should describe the difference neutrally rather than characterizing the authors' design as fraudulent or automatically invalid.

---

## B. Explicit source/study-aware examples

### 5. Aguiar & Kasemodel 2026 — methylene blue adsorption onto clays

**Paper:** Aguiar, L. G., & Kasemodel, M. C. *Application of random forest regression in modeling the adsorption of methylene blue onto clays.* Neural Computing and Applications 38, 496 (2026). DOI: `10.1007/s00521-026-12200-1`.

**Verified practice:** The authors directly compare conventional CV with **GroupKFold by source study**. Their largest M5 model contains 726 observations from 23 studies.

**Published result:** conventional CV R² ≈ **0.79** vs grouped R² ≈ **0.66** for M5; smaller models show larger decreases and some negative grouped values.

**Role:** independent cross-team corroboration that the validation unit can matter without implying universal collapse.

### 6. Huang et al. 2026 — heavy-metal adsorption by biochar

**Paper:** Huang, X., Bai, X., Yang, Y., Li, W., & Xu, D. *Machine Learning-Based Prediction and Optimization of Heavy Metal Adsorption Performance of Biochar.* Forests 17(3), 326 (2026). DOI: `10.3390/f17030326`.

**Verified practice:** The 452-record corpus is divided at the **literature-source/publication level** using a 4:1 train/test split. All rows from one publication remain exclusively in train or test, and preprocessing parameters are derived from training data.

**Published result:** XGB test R² = **0.99**; training five-fold CV R² = **0.92 ± 0.04**.

**Role:** positive source-aware counterexample. Strong performance can survive scientific grouping when domain coherence/descriptors/data coverage support transfer.

---

## C. Methodological prior art

### 7. Cahyana & Jang 2025

**Paper:** Cahyana, D., & Jang, H. J. *Addressing data handling shortcomings in machine learning studies on biochar for heavy metal remediation.* Journal of Hazardous Materials 491, 137887 (2025). DOI: `10.1016/j.jhazmat.2025.137887`.

**Verified relevance:** identifies data leakage and inadequate splitting as important concerns in compiled biochar ML datasets.

**Novelty implication:** Paper 1 must not claim novelty for discovering leakage, recommending grouped validation, or recognizing hierarchical dependence.

### 8. Roberts et al. 2017

**Paper:** Roberts, D. R., et al. *Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure.* Ecography 40, 913–929 (2017). DOI: `10.1111/ecog.02881`.

**Verified relevance:** general methodological basis for matching blocking/grouping design to dependence structure and the intended prediction task.

---

## Manuscript-safe synthesis

A defensible Introduction statement is:

> Recent literature-derived adsorption-ML studies use heterogeneous validation strategies. Observation-level random holdouts and random K-fold validation remain in active use, including recent biochar adsorption studies, while other recent work explicitly separates observations by source publication or source study. These designs estimate different prediction targets; therefore, performance should be interpreted with respect to the scientific unit withheld during validation.

Do **not** convert this bounded evidence set into a numerical claim such as “most adsorption ML papers use random splits.” Establishing prevalence would require a systematic search and screening protocol beyond Paper 1's current scope.
