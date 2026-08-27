# Paper 1 Multi-Dataset Study-Aware Validation Protocol

Status: **FROZEN BEFORE EXTERNAL GROUPED-VALIDATION OUTCOMES**

Protocol date: 2026-08-27

Branch: `paper1/multidataset-study-aware-replication`

Parent manuscript branch: `paper1/v21-manuscript-reconstruction`

Frozen scientific baseline: `feature/study-aware-validation-v2` at `5f88c6a2d70326d70633188c2c62485554460ddc`.

## 1. Central research question

**How sensitive are reported machine-learning performance estimates in literature-derived adsorption datasets to the unit at which observations are separated for validation?**

The protocol does not assume that study-aware validation must reduce performance. The directional hypothesis is deliberately weaker:

> When literature-derived adsorption datasets contain repeated observations from common primary studies or experimental campaigns, row-random validation may produce materially different—and potentially optimistic—estimates of transfer performance relative to validation that withholds the relevant scientific grouping unit.

A dataset remains in the analysis whether grouped performance collapses, decreases modestly, remains similar, or improves.

## 2. Evidence layers

Paper 1 will distinguish three evidence layers.

### Layer A — structured literature-practice audit

Recent adsorption-ML studies will be classified by dataset origin, data hierarchy, split strategy, reported performance, generalisation language, code/data availability, and whether source identity was retained.

### Layer B — matched empirical replications

For every eligible dataset with defensible grouping information, the same observations and predictor definition will be evaluated under row-random and group-aware validation. This is the main empirical extension beyond the V2.1 case study.

### Layer C — good-practice comparators

Studies that already separate literature sources or experimental groups will be retained as methodological comparators. They are not treated as failures and are important for showing that strong performance can survive stricter validation in some domains.

## 3. Dataset inclusion criteria for matched replication

A dataset is eligible for the primary matched-replication set only if all of the following are satisfied:

1. The prediction problem concerns experimental adsorption performance or adsorption capacity.
2. The modelling dataset contains observations from at least two independent primary publications, laboratories, experimental campaigns, or another scientifically defensible grouping unit relevant to the claimed generalisation target.
3. The original work reports row-random train/test splitting, ordinary shuffled K-fold validation, or another scheme that allows observations from the same relevant group to occur in both training and validation; good-practice source-aware datasets may be included as comparator replications where raw data permit.
4. Raw modelling data are publicly available, supplied by the authors, or otherwise reproducibly obtainable under lawful reuse conditions.
5. Group identity is supplied by the source dataset or can be reconstructed from primary evidence with defensible row-level or block-level mapping.
6. At least two validation groups remain after all predeclared comparability exclusions.
7. The target and predictor semantics can be reproduced closely enough to permit a fair matched comparison.

## 4. Exclusion criteria

A dataset is excluded from the primary matched-replication set if any of the following applies:

- it is generated from a single experimental study with no meaningful higher-level holdout unit relevant to the paper's claim;
- source/campaign identity is absent and cannot be reconstructed without guessing;
- only summary performance values are available and raw data cannot be obtained;
- the available public dataset materially differs from the dataset used for the published model and the difference cannot be reconciled;
- the dataset substantially duplicates another benchmark already counted as an independent replication, unless it is explicitly analysed as a lineage/sensitivity dataset;
- legal/licensing restrictions do not permit the proposed reuse.

Excluded studies may remain in the literature-practice audit.

## 5. Independence and double-counting rule

Datasets with substantial row or source lineage overlap will not be counted as independent replications merely because they were published in different papers.

In particular, the Iftikhar et al. 2023 compilation is part of the provenance lineage of the Martin V2.1 dataset and therefore cannot be treated as an independent confirmation of the V2.1 random-versus-study-aware gap. It may be reported as lineage evidence or a non-independent sensitivity analysis.

## 6. Group-definition hierarchy

Group IDs must never be inferred solely to produce a desired validation result.

Preferred hierarchy:

1. explicit row-level primary-study identifier supplied by the source;
2. explicit bibliographic/reference field that can be deterministically mapped to a primary paper;
3. deterministic experimental block/campaign mapping supported by the source paper, supplementary material, repository metadata, or primary reports;
4. reconstructed primary-study mapping supported by exact combinations of material, pollutant, processing, and experimental signatures plus bibliographic evidence.

If group identity remains ambiguous, the affected rows are marked unresolved and are excluded from primary grouped claims or analysed in a declared sensitivity analysis.

## 7. Matched validation design

For each eligible dataset, the primary comparison must hold the modelling population fixed.

### 7.1 Row-random comparator

Use shuffled K-fold cross-validation or the original paper's reproducible row-random scheme. Five-fold shuffled CV is the common cross-dataset comparator unless dataset size/group constraints justify another K. The random seed is fixed and reported.

### 7.2 Group-aware comparator

Use GroupKFold by the predeclared scientific grouping variable. No group may appear in both training and validation within a fold.

### 7.3 LOSO / leave-one-group-out robustness

Where the number and size of groups permit, Leave-One-Group-Out (study/campaign) validation will be reported as a robustness analysis.

### 7.4 Fold-safe preprocessing

All data-dependent preprocessing—including imputation, scaling, encoding, feature selection and target-independent learned transformations—must be fitted only on the training portion of each fold. Where faithfully reproducing an original paper requires a preprocessing step that was fitted globally, two results may be reported: `published_pipeline_replication` and `fold_safe_replication`, clearly distinguished.

## 8. Model policy

The objective is not model shopping. For each dataset:

1. reproduce at least one central/high-performing model from the original paper when feasible;
2. include a common cross-dataset tree baseline (RF and/or XGB where appropriate) to improve comparability;
3. use the same model specification for the matched random and grouped comparison;
4. hyperparameter tuning, if performed, must use only training data and respect groups for the grouped arm.

A model is not retuned differently merely to improve one validation arm.

## 9. Primary metrics

For every matched model/dataset pair report:

- `R2_random`
- `R2_grouped`
- `delta_R2 = R2_random - R2_grouped`
- `RMSE_random`
- `RMSE_grouped`
- `delta_RMSE = RMSE_grouped - RMSE_random`
- `MAE_random`
- `MAE_grouped`
- number of rows
- number of independent groups
- rows per group distribution
- largest-group share

Where LOSO is feasible, also report pooled LOSO R²/RMSE/MAE and per-group MAE distribution.

## 10. Interpretation policy

Random splitting is not labelled intrinsically invalid. Interpretation depends on the intended estimand:

- row-random validation can estimate interpolation to additional observations from a mixture of already represented systems;
- study/campaign-aware validation is required when the scientific claim concerns transfer to an unseen study, laboratory, material system, or experimental campaign represented by that grouping unit.

The manuscript will therefore focus on **claim–validation alignment**, not on declaring all random splitting erroneous.

## 11. Outcome-neutral reporting rule

All datasets that satisfy the frozen eligibility rules will remain in the result set regardless of the direction or magnitude of `delta_R2`.

No dataset will be removed because study-aware performance remains high or because the expected validation gap is absent.

## 12. Literature-audit fields

For each screened paper record:

- citation / DOI / year
- adsorption domain and target
- dataset origin (single experiment, multi-publication literature, mixed, computational)
- number of rows
- number of independent studies/groups if stated
- material and pollutant scope
- original split strategy
- cross-validation strategy
- preprocessing timing if recoverable
- reported best model and metrics
- language used for generalisation/unseen prediction
- row-level provenance retained? yes/no/unclear
- raw data availability
- source IDs reconstructible? yes/no/unclear
- replication eligibility and reason
- overlap with another benchmark

## 13. Initial benchmark roles before grouped outcomes

- **Dataset A — Martin V2.1:** primary deep case study; already provenance reconstructed and evidence locked.
- **Liu et al. 2025 biochar/dye:** high-priority public-data candidate; published workflow uses random 80:20 partitioning and repeated random evaluation. Primary-study reconstruction is required before grouped reanalysis.
- **Moosavi et al. 2021 agricultural-waste activated carbon/dyes:** high-priority provenance candidate because the compilation explicitly names contributing literature and supplementary data are available; exact original outer validation must be verified.
- **Yadav et al. 2025 Congo Red/biochar:** literature-audit candidate; dataset reported available on request.
- **Abu-Shareha et al. 2026 Cd(II)/biochar:** high-priority literature-audit candidate because the paper explicitly randomises pooled observations irrespective of literature source; raw data currently reported available on request.
- **Huang et al. 2026 heavy-metal/biochar:** good-practice comparator because publication-level separation is already used.
- **Jaffari et al. 2023 emerging contaminants/biochar:** auxiliary candidate only until a defensible higher-level source/campaign grouping is established; public modelling data do not contain a publication-source field.
- **Iftikhar et al. 2023 carbon materials/dyes:** lineage/non-independent dataset relative to Dataset A; not counted as an independent replication.

## 14. Change control

Any change to inclusion criteria, grouping hierarchy, primary metrics or outcome-neutral reporting rules after grouped outcomes are observed must be documented in a separate amendment with rationale and commit timestamp. The original protocol remains preserved in Git history.
