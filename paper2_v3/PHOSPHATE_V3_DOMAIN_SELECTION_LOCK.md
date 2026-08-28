# Paper 2 / V3 Domain Selection Lock

Status: **PRIMARY MODELLING DOMAIN LOCKED — DATASET NOT YET ADMITTED — NO MODEL TRAINED**

Branch: `paper2/v3-provenance-aware-model-development`

Decision date: 2026-08-28

## 1. Selected primary domain

**Equilibrium phosphate/phosphorus adsorption capacity (`qe`, mg/g) on biochar-based adsorbents in aqueous batch systems.**

The primary scientific task is transfer to an entirely unseen primary study. Study identity remains validation metadata and is never a predictor.

This decision selects the scientific domain only. It does **not** admit the public compilation rows into Dataset V3. Every row remains outside V3 until its primary source, target semantics, units and values are verified according to the frozen V3 protocol.

## 2. Why phosphate was selected

The choice was made before V3 model training and without using any preliminary V3 model score.

### Phosphate feasibility evidence

Public discovery source: Iftikhar et al. 2025, *Chemosphere*, DOI `10.1016/j.chemosphere.2024.144031`, plus the authors' public `po4_removal_ml` master workbook.

Deterministic source-structure audit of the public workbook found:

- 5,014 raw rows;
- 70 sparse DOI markers, all unique;
- every DOI-marker row also contains a bibliographic `ref` marker;
- the first DOI marker occurs on row 0;
- the workbook therefore forms 70 contiguous DOI-defined source blocks;
- block sizes range from 10 to 306 rows, median 69.5;
- forward propagation of a DOI only within its contiguous block maps all 5,014 discovery rows to a source block without guessing across gaps;
- 4,914 rows have positive numeric `qe` targets;
- all 70 source blocks contribute at least one positive-`qe` row;
- 62 source blocks contribute at least one row complete for the core process tier;
- 59 source blocks contribute at least one row after adding pyrolysis temperature and surface area;
- 41 source blocks contribute at least one row after additionally requiring both C and O;
- the much stricter public-code complete-case feature set retains 2,932 rows from 38 source blocks.

The source-target population therefore exceeds the predeclared minimum development gate of 30 independent primary studies and the preferred 50-study planning target at the core/basic-material tiers, subject to primary-source verification.

### Comparison with the other shortlisted domains

**Pb/Cd heavy-metal corpus (Yu et al. 2026):** the recovered public supplement contains 781 rows with an explicit `reference` field, but only 13 source studies; 11 remain after a core-process complete-case gate and nine after adding basic material descriptors. This is valuable as a future comparator or secondary domain but does not meet the V3 independent-study target by itself.

**Dye corpus:** the public Liu dye workbook contains 685 modelling rows but none of its modelling/data sheets preserves a row-level DOI/reference/source column. Paper 1 reconstructed 17 high-confidence primary studies for its strict dye population, below the V3 planning target. Expanding the dye domain would require substantial additional provenance reconstruction and deduplication across overlapping compilations.

Thus phosphate offers the strongest combination of source-count depth, deterministic source-block recoverability, chemical target coherence and descriptor coverage under the predeclared selection criteria.

## 3. Important discrepancies retained, not silently reconciled

The Chemosphere article describes 71 shortlisted articles, whereas the public master workbook contains 70 DOI-defined source blocks. V3 will not assume that the missing/extra article contributed modelling observations. The discrepancy remains open until the source bibliography is reconciled against the article and primary papers.

The article/public materials also contain different row-count descriptions (including 5,014 collected rows and approximately 2,952/2,959 modelling observations), while a deterministic reproduction of the current public-code complete-case feature gate yields 2,932 rows. V3 does **not** adopt any of those counts as its modelling population. V3 will build a new verified population from primary evidence and report its own deterministic inclusion count.

## 4. Target definition

Primary V3 target:

- experimentally observed equilibrium/terminal phosphate adsorption capacity, normalized to `qe_mg_g`.

Do not silently mix into this target:

- removal efficiency/percentage;
- residual concentration;
- fitted Langmuir `qmax`;
- kinetic intermediate uptake;
- column/breakthrough capacity;
- model-generated or optimized capacity values.

Where a primary paper reports phosphate as P rather than PO4, unit/species basis must be recorded explicitly and converted only with a documented stoichiometric transformation when scientifically appropriate.

## 5. Material scope

Primary scope includes biochar-based adsorbents produced by thermal conversion of biomass or biogenic residuals and used for aqueous phosphate adsorption.

Pristine and modified biochars may both enter the discovery pool, but modification chemistry must be represented explicitly. Prespecified sensitivity analyses will distinguish at minimum:

1. all verified biochar-based phosphate adsorbents;
2. pristine/unmodified biochar where enough studies remain;
3. metal/mineral-modified biochar where enough studies remain.

A material is not admitted merely because the secondary compilation calls it biochar. The primary source must support the classification.

## 6. Source verification gate

The 70-source queue is a **verification queue, not Dataset V3**.

For each DOI before any associated row is admitted:

1. resolve and verify primary bibliographic metadata;
2. inspect the primary article and/or supplementary information;
3. confirm that the material and pollutant fall within the locked domain;
4. confirm `qe` semantics and species/unit basis;
5. verify the experimental values used for each proposed V3 row;
6. verify preparation and operating-condition fields against the primary source;
7. check for duplicate inheritance through another compilation;
8. assign a stable `primary_study_id` and row-level provenance record;
9. mark the source/rows `ADMITTED` only after all required checks pass.

No automated source propagation alone is sufficient for final V3 admission.

## 7. External validation policy

The development corpus will be based on verified source studies from the pre-2025 discovery lineage. Post-cutoff primary experimental studies are reserved as a temporal external-validation pool and must not be used for feature selection, hyperparameter tuning, imputation design decisions or model selection.

A study in the holdout registry may be removed only for a documented domain/target incompatibility identified without viewing model performance. It cannot be moved into development because the external score is inconvenient.

## 8. Modelling remains blocked

No V3 predictive model may be trained until:

- the primary-source verification queue has a sufficient admitted subset;
- the final V3 schema and mandatory/optional feature tiers are locked;
- duplicate/source-lineage reconciliation is completed;
- the external holdout DOI registry is frozen;
- the V3 dataset validator passes;
- the primary and sensitivity populations are hashed/versioned.

Only then may the baseline → grouped model-development sequence begin.

## 9. Reproducibility records supporting this decision

- Deep provenance workflow: GitHub Actions run `33215886637`, conclusion `success`, artifact `9703322527`, SHA-256 `862205bde37eb96d265aeacf9dc5084d262d1114e9ae0f81737c2d7d8e7dca24`.
- Domain selection gate: run `33216064784`, conclusion `success`, artifact `9703385456`, SHA-256 `d490a9e28a3a5074f14713abf24b785295646f3b8f1c912ac0cd485eebf4af05`.
- Source verification queue: run `33216194764`, conclusion `success`, artifact `9703430535`, SHA-256 `e1abf83dd9da2d80bf82a223ae085d1630f4191f88bbddcfb854982d70215c19`.

## 10. Decision

**LOCKED: phosphate adsorption on biochar-based adsorbents is the Paper 2 V3 primary modelling domain.**

Next scientific phase: primary-paper verification and row-level V3 corpus construction. Model training remains prohibited.
