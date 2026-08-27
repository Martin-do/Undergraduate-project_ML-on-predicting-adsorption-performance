# Paper 1 Multi-Dataset Screening Notes

Status: **SCREENING IN PROGRESS — NO EXTERNAL GROUPED OUTCOMES YET**

The validation protocol is frozen in `MULTIDATASET_VALIDATION_PROTOCOL.md`. These notes record eligibility evidence gathered after protocol freeze.

## 1. Liu et al. 2025 — biochar/dye dataset

Citation: Chong Liu et al., *Enhanced machine learning prediction of biochar adsorption for dyes: Parameter optimization and experimental validation*, Carbon Research 4 (2025), DOI `10.1007/s44246-025-00213-9`.

### Published dataset/method

- Literature data were collected from Web of Science, Google Scholar and Scopus using biochar/dye adsorption search terms.
- The paper reports 43 varieties of biochar, 15 dye categories and 685 collected experimental datasets.
- The paper states that 17 high-Q rows were removed during preprocessing, yielding 668 modelling rows.
- The modelling data were randomly partitioned 80:20.
- Five-fold cross-validation and evaluation across 1000 random train-test partitions are described.
- CatBoost is reported as the best model with `R² = 0.9880` and `RMSE = 0.0839`; experimental validation is reported at `R² = 0.9037`.

### Public repository

Repository: `17609858895/ML-predict-biochar-adsorb-dye`

The public repository contains `Biochar_dye_filtered.xlsx` plus model notebooks for CatBoost, XGB, RF and other algorithms.

The workbook is byte-identical at Git blob level to the `Biochar_dye_filtered.xlsx` copy already archived in the Martin project repository (`10514a9509ba37047f8b269bbd72f30c592d0c5d`).

### CI-verified public workbook screen

A dedicated deterministic screening workflow was added on the Paper 1 replication branch and completed successfully:

- GitHub Actions run: `33062243622`
- conclusion: `success`
- artifact: `paper1-liu2025-public-dataset-screen`
- artifact ID: `9642197856`
- artifact SHA-256: `952741b1d1bb4f4caee8147d4d52f150286d4cfd0cccad91ed6598ff691cde85`

The workbook SHA-256 reported by CI is `2a7219c309fe09187e4c3e4ef7f55794051643570fe612fd7c2241a4cd16de11`.

The workbook contains eight sheets:

- `After preprocessing`
- `PRE_KNN_filled`
- `molar_ratio`
- `pre_D_filled`
- `pre_Free-ASH`
- `original`
- `literature collection`
- `Experiment data`

The first six literature-data processing sheets each contain **685 rows**, including `After preprocessing`. The `Experiment data` sheet contains 51 prospective experimental-validation cases.

This exposes a reproducibility discrepancy requiring resolution: the article states that 17 outlier rows were removed to produce **668 modelling rows**, whereas the public `After preprocessing` sheet contains **685 rows** and the public model notebooks load `Biochar_dye_filtered.xlsx` without an additional 17-row filter. The matched replication must therefore distinguish the published 668-row claim from the public-code 685-row executable dataset rather than silently treating them as identical.

The `literature collection` sheet contains **20 non-empty DOI entries**. However, neither `original` nor `After preprocessing` contains an explicit source, reference, DOI, paper or study column. The CI gate therefore records:

- `explicit_row_level_source_identifier_found = false`
- `grouping_ready_for_primary_study_cv = false`

The V2 external-validation loader independently reached the same practical conclusion: the processed sheet does not preserve a row-level biochar/source identity, so it assigns the honest generic label `biochar_external_unspecified` rather than manufacturing a base-material identity.

### Reproducibility observations from public code

Both the public XGB and CatBoost notebooks:

1. fit `StandardScaler` on the complete predictor matrix **before** the 80:20 train/test split;
2. use ordinary `train_test_split(..., test_size=0.2, random_state=1)`;
3. use ordinary K-fold CV without study groups;
4. define one fixed `KFold(n_splits=5, shuffle=True, random_state=1)` and place it inside a 1000-iteration evaluation loop without changing the KFold seed.

The final point means the public code appears to repeat the **same five shuffled folds** 1000 times rather than generating 1000 distinct random K-fold partitions. This is logged as a reproducibility issue, not as evidence of source leakage by itself.

### Current gate

**PROVISIONALLY ELIGIBLE, GROUPING NOT YET READY.**

Next requirement: reconstruct row-to-primary-study or row-to-defensible experimental-source groups from the 20-study literature collection and primary publications. Material-feature signatures may be used to assist reconciliation, but they will not be declared to be primary-study IDs without bibliographic evidence. No grouped metric will be generated before this mapping is established.

---

## 2. Yadav et al. 2025 — Congo Red / biochar

DOI `10.1007/s44246-024-00168-3`.

- Literature-derived dataset.
- Random 80:20 train/test split with `random_state=42`.
- 10-fold CV used for model validation/hyperparameter selection.
- RF test `R² = 0.9785`; RF 10-fold CV `R² = 0.9762`; XGB test `R² = 0.9577`.
- The paper describes the held-out portion as unseen data.
- Raw dataset is reported as available from the corresponding author on request.

**Current role:** literature-practice audit; matched replication pending data acquisition and provenance assessment.

---

## 3. Abu-Shareha et al. 2026 — Cd(II) / biochar

DOI `10.1016/j.hazadv.2026.101004`.

- 1,150 observations drawn from peer-reviewed publications.
- 90:10 global random split.
- The paper explicitly states that observations were shuffled *irrespective of literature source* so laboratory/source effects would be distributed across training and testing.
- Random five-fold CV is used.
- CNN, AdaBoost and RF are reported with `R² > 0.99`.
- Data are currently reported as available on request.

This is a high-priority conceptual test because the paper explicitly treats cross-source mixing as a strategy against leakage. It should not be reanalysed until the raw dataset and source mapping are available.

---

## 4. Huang et al. 2026 — heavy metals / biochar

DOI `10.3390/f17030326`.

The paper explicitly separates samples at literature-source level: all samples originating from a publication are assigned exclusively to training or testing, with five-fold CV applied within training. Reported XGB performance remains strong in the published analysis.

**Current role:** good-practice comparator. It prevents Paper 1 from implying that all high adsorption-ML performance is an artefact of random splitting.

---

## 5. Jaffari et al. 2023 — emerging contaminants / biochar

DOI `10.1016/j.cej.2023.143073`.

Public repository: `ZeeshanHJ/Adsorption-capacity-prediction-for-ECs`.

- README identifies 3,757 data points and reports CatBoost test `R² = 0.9433`, MAE `4.95`.
- Public RF code uses `train_test_split(..., test_size=0.3, random_state=0)` and then repeats random train/test splitting across 1,000 seeds.
- Public `Raw_data.csv` contains material/adsorption features and capacity but no explicit publication/source column.

The current evidence does not establish a defensible primary-publication grouping. Therefore Jaffari 2023 is **not yet a primary matched-replication benchmark** and no study IDs will be invented from adsorbent names alone.

---

## 6. Independence warning — Iftikhar et al. 2023

DOI `10.1016/j.seppur.2023.124891`.

This compilation contributed the dominant inherited block in the Martin dataset. It may be analysed for lineage and methodology, but it is not counted as an independent external replication of Dataset A.
