# Paper 2 / V3 Phosphate Feature and Validation Lock

Status: **LOCKED BEFORE V3 MODEL TRAINING**

This specification applies only after primary-source row verification and Dataset V3 admission. It does not authorize use of the secondary compilation as training data.

## 1. Primary prediction target

Primary target: experimentally observed equilibrium/terminal phosphate adsorption capacity, `qe_mg_g`.

Primary reported performance is evaluated on the **original mg/g scale**.

A `log1p(qe)` target may be evaluated only as a prespecified sensitivity. Predictions from a log-target model must be inverse-transformed before the primary raw-scale R²/RMSE/MAE are reported. A favorable log-space metric alone cannot establish success.

## 2. Primary feature tier — V3-P2

The initial primary feature set is designed to balance physicochemical relevance against independent-study retention. It must contain the following harmonized variables where the verified corpus supports them:

### Material / preparation
- `precursor_class` — harmonized biomass/biogenic feedstock class, not a paper-specific material code;
- `modification_family` — e.g. pristine, Ca-based, Mg-based, Fe-based, Al-based, mixed metal/mineral, other verified family;
- `pyrolysis_temperature_c`;
- `surface_area_m2_g`.

### Adsorption conditions
- `initial_concentration_mg_l` on the locked phosphate species/basis;
- `adsorbent_dose_g_l`;
- `ph`;
- `temperature_c`;
- `contact_time_min`.

No exact DOI, author, journal, publication year, study ID, row order, adsorbent product/code name, extraction method or missingness/provenance flag is a predictor.

The exact categorical harmonization vocabulary for `precursor_class` and `modification_family` must be frozen before the first primary model is trained.

## 3. Feature-tier rationale

The public discovery workbook shows that a complete-case gate containing feedstock, pyrolysis temperature, surface area and core adsorption conditions can preserve approximately 4,226 discovery observations from 59 source blocks before primary verification. This is used only as a feasibility signal; the final V3 counts will be determined from verified primary rows.

The primary tier deliberately avoids requiring C/O, pore volume or pore size because their discovery-level completeness materially reduces independent-study coverage.

## 4. Prespecified richer sensitivity tiers

### V3-P3 elemental sensitivity

Add where sufficiently verified:
- carbon fraction / `c_wt_percent`;
- oxygen fraction / `o_wt_percent`.

Current discovery feasibility suggests approximately 41 source blocks may survive a strict C/O complete-case gate, which remains above the minimum 30-study planning threshold but below the preferred 50-study target.

### V3-P4 pore-structure sensitivity

Add where sufficiently verified:
- pore volume;
- mean/representative pore size;
- optional ash content when consistently defined.

This is a secondary sensitivity only unless primary-source verification shows much stronger coverage than the secondary compilation suggests.

### Mechanism/material sensitivities

Where study counts permit, rerun the primary protocol for:
- pristine/unmodified biochar;
- metal/mineral-modified biochar;
- major modification families with adequate independent-study counts.

These are not searched selectively after seeing favorable scores.

## 5. Missing-data policy

The preferred primary V3-P2 population is a scientifically harmonized complete-core population rather than a maximally large row set with widespread source-dependent missingness.

If isolated missing values remain after primary verification:
- imputation must be fitted within the training fold only;
- no global median/mean may be computed before splitting;
- source/study identity may not be used for imputation;
- missingness indicators are **not** primary predictors, because reporting practices can become source proxies;
- a complete-case sensitivity must be reported if imputation is used materially.

No value is filled from a secondary review estimate merely to increase row count.

## 6. Categorical representation

High-cardinality raw material names are not used as the primary categorical representation.

Primary categories are harmonized scientific descriptors such as precursor class and modification family. Any category definition must be based on material chemistry/processing and fixed before model fitting.

For models requiring encoding:
- encoders are fitted within training folds;
- unseen validation categories must be handled explicitly without peeking at held-out studies;
- target encoding is not permitted in the primary pipeline unless implemented in a strictly nested group-safe manner and declared as a later sensitivity.

## 7. Validation hierarchy

### Primary development estimate
- GroupKFold by `primary_study_id`.
- No row from a held-out primary study may enter model fitting or preprocessing.
- Number of folds selected from verified study count and locked before tuning.

### Robustness
- Leave-One-Primary-Study-Out / LeaveOneGroupOut where computationally feasible.
- report pooled predictions plus per-study MAE/RMSE;
- report median and interquartile range of per-study errors so large studies do not dominate interpretation.

### Hyperparameter selection
- nested group-aware CV inside the development corpus;
- outer grouped folds remain untouched by inner tuning;
- no random-CV hyperparameter choice is carried into the primary grouped analysis merely because it performs better randomly.

### Diagnostic comparator
- shuffled row-random CV is retained only to quantify interpolation performance and the random-versus-study-aware gap.
- it is not the success criterion.

## 8. External validation

The locked post-2024 DOI registry is never used for feature selection, category design, hyperparameter tuning or model-family choice.

External evaluation occurs after the development pipeline is frozen. Holdout rows must independently pass the same target/material/units verification standard.

If more than one eligible holdout study is available, report:
- pooled external metrics;
- per-study metrics;
- equal-study descriptive summaries.

## 9. Model-development order

After the verified-data gate opens:
1. constant/mean or median baseline;
2. regularized linear model;
3. Random Forest;
4. XGBoost;
5. ExtraTrees and/or CatBoost only after the core baselines are complete;
6. hierarchical/mixed-effects or domain-adaptation approaches if scientifically justified;
7. stacking only if it improves study-aware outer-fold performance reproducibly.

A complex model is not retained because it wins only under row-random validation.

## 10. Metrics

Primary:
- R² on pooled held-out predictions;
- RMSE (mg/g);
- MAE (mg/g).

Required study-level context:
- per-study MAE;
- per-study RMSE where defined;
- median/IQR per-study MAE;
- study row count and study share.

Secondary:
- Spearman/Pearson correlation where useful;
- raw-vs-log target sensitivity;
- calibration/slope diagnostics where appropriate.

## 11. Success interpretation

No single R² threshold is treated as a proof of deployment readiness.

A genuinely improved V3 model should show:
- positive and materially useful grouped performance across outer folds;
- stability under LOSO and major domain sensitivities;
- no dependence on one dominant study;
- improvement over simple baselines under the same grouped protocol;
- confirmation on locked temporal external studies.

Random-split R² is never sufficient evidence of success.

## 12. Change control

Changes to the primary feature tier, target transformation, grouping unit, success metrics or external-holdout policy after model results are observed require a dated protocol amendment. The original specification remains in Git history.
