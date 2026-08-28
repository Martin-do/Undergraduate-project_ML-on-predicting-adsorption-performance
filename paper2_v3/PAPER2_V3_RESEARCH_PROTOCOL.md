# Paper 2 / V3 Provenance-Aware Model Development Protocol

Status: **FROZEN BEFORE V3 DATASET CONSTRUCTION OR MODEL TESTING**

Branch: `paper2/v3-provenance-aware-model-development`

Scientific parent: `feature/study-aware-validation-v2`

Paper 1 remains separate and is not modified by this branch.

## 1. Research objective

Paper 2 asks a different question from Paper 1:

> **Can a deliberately domain-coherent, provenance-aware adsorption dataset support useful prediction of entirely unseen primary studies?**

Paper 1 establishes that high row-random performance does not necessarily survive primary-study holdout. Paper 2 is therefore a prospective model-development study designed around the harder generalisation target from the beginning.

The V3 objective is **not** to maximize row-random R². The primary target is stable performance on primary studies that are completely absent during model fitting.

## 2. Non-negotiable scientific rules

1. Primary-study provenance must be retained at row level from the moment a record enters V3.
2. No source identifier, DOI, author, journal, publication year, row order, or deterministic proxy for source identity may be used as a predictor.
3. New records are added only after primary-source verification. Review articles and secondary compilations may be used for discovery but not as final provenance when a primary paper can be identified.
4. The modelling domain must be defined before model comparison.
5. Data-dependent preprocessing must be fitted inside training folds.
6. Hyperparameter optimisation for the primary analysis must respect primary-study groups.
7. Random CV is diagnostic only. It cannot be used as the primary success criterion.
8. External datasets selected for final evaluation are locked before final model tuning and are not used iteratively during development.
9. Model complexity is introduced only after simple baselines have been established.
10. Failed or weak study-aware results remain reportable; V3 will not be tuned indefinitely until a preferred R² appears.

## 3. Prediction target

Primary target:

- equilibrium adsorption capacity, `qe_mg_g`, in mg/g.

Records are eligible for the primary target only where the reported value is experimentally observed or reproducibly derived from reported quantities and corresponds to an equilibrium/terminal adsorption-capacity concept compatible with the selected domain.

The following are not silently mixed with `qe_mg_g`:

- removal percentage;
- rate constants;
- maximum Langmuir capacity (`qmax`) unless explicitly analysed as a separate target;
- breakthrough capacity from continuous columns;
- non-equilibrium intermediate uptake;
- model-fitted capacity values without experimental correspondence.

## 4. Candidate-domain gate

V3 will not begin as a universal adsorption corpus. Candidate domains will first be screened for independent-study coverage, descriptor availability and target comparability.

Initial candidate domains:

1. **Dye adsorption on biochar / activated carbon derived from biomass or agricultural waste.**
2. **Heavy-metal adsorption on biochar / activated carbon.**
3. **Ammonium/ammonia-nitrogen adsorption on biochar.**
4. **Emerging-organic-contaminant adsorption on biochar**, only if independent-study coverage and consistent descriptors are adequate.

A heterogeneous all-pollutant/all-material corpus is not the default V3 domain.

### 4.1 Domain-selection criteria

Each candidate domain will be scored before modelling using:

- number of independently verified primary studies;
- number of usable condition-level observations;
- largest-study share;
- diversity of studies rather than row count alone;
- consistency of `qe` semantics and units;
- proportion with key adsorbent descriptors;
- proportion with key adsorbate descriptors;
- proportion with core operating-condition variables;
- availability of at least one genuinely external validation corpus;
- degree of material and pollutant heterogeneity;
- evidence of duplicated or inherited literature compilations.

No domain will be selected because it happens to produce the highest preliminary model score.

## 5. Independent-study acquisition target

V3 prioritises **independent studies over additional rows from the same study**.

Planning targets:

- **Minimum development gate:** 30 independently verified primary studies.
- **Preferred development target:** 50 or more independently verified primary studies.
- No single study should ideally contribute more than 20% of the primary modelling rows; if this cannot be achieved, dominant-study sensitivity analyses are mandatory.
- A candidate domain below 30 studies may remain a pilot/sensitivity dataset but should not be presented as a mature transferable model without strong external evidence.

These thresholds are project design gates rather than universal statistical laws. They are intended to prevent a repeat of the high-row/low-independence problem documented in Paper 1.

## 6. Study inclusion criteria

A primary paper can contribute records to V3 only when:

1. the publication is identifiable by DOI or another persistent bibliographic identifier;
2. the adsorbent and adsorbate fall inside the selected domain;
3. the adsorption experiment is aqueous unless another medium is explicitly part of the selected domain;
4. `qe` can be represented in mg/g without ambiguous conversion;
5. enough experimental conditions are reported to interpret each observation;
6. the reported adsorbent is experimentally distinct and traceable to the paper;
7. the record can be assigned a deterministic `primary_study_id`;
8. the source is not merely a review-derived summary value when primary evidence is available;
9. duplicate publication of the same experiment can be ruled out or flagged;
10. extraction confidence is recorded.

## 7. Record-level exclusion criteria

Exclude from the primary modelling population when any applies:

- unresolved primary-study provenance;
- ambiguous target semantics;
- unit conversion cannot be verified;
- `qe` is missing;
- the value is a model prediction rather than an experimental observation;
- an observation is duplicated across tables/publications and cannot be uniquely reconciled;
- critical feature values were inferred without primary-source evidence;
- column/batch/kinetic/intermediate values are mixed with equilibrium batch capacity without a declared analysis stratum;
- material or pollutant identity cannot be mapped to the selected domain.

Excluded rows remain in an audit ledger with a reason code.

## 8. V3 data schema philosophy

The schema separates four layers:

1. **Provenance metadata** — identifiers needed for audit and grouped validation.
2. **Adsorbent descriptors** — material chemistry, texture and preparation.
3. **Adsorbate descriptors** — pollutant physicochemical representation.
4. **Process/experimental descriptors** — operating conditions associated with each observation.

The full field-level schema is stored in `DATASET_SCHEMA_V3.csv`.

## 9. Descriptor priorities

### 9.1 Adsorbent

High-priority descriptors include:

- precursor/feedstock class;
- biochar/activated-carbon/material class;
- activation type and activation agent;
- pyrolysis/carbonisation temperature;
- residence time where reported;
- BET surface area;
- total pore volume;
- average/median pore size where semantically compatible;
- pHpzc where available;
- ash content;
- elemental C/H/N/O where available;
- surface functional-group descriptors where reported.

### 9.2 Adsorbate

Where obtainable from authoritative chemical databases or the primary paper:

- molecular weight;
- charge class / ionic state under relevant conditions;
- pKa values;
- logP/logKow where meaningful;
- aromatic ring count;
- heteroatom count;
- polar surface area;
- hydrogen-bond donor/acceptor counts;
- pollutant class.

Computed molecular descriptors must be generated reproducibly from a canonical identifier such as SMILES/InChI and versioned.

### 9.3 Process conditions

Core variables include:

- initial concentration;
- adsorbent dose;
- pH;
- temperature;
- contact time;
- solution volume where available;
- agitation rate where available;
- ionic strength/co-solutes where available;
- equilibrium criterion or endpoint time where reported.

## 10. Missing-data policy

Missingness is treated as scientific information rather than silently hidden.

- Every descriptor has an explicit raw-missing flag.
- No global imputation before splitting.
- Imputation is fitted within training folds.
- Variables with extreme missingness may be excluded from the primary feature set and retained for richer-data sensitivities.
- Missingness-indicator features may be evaluated, but only if they do not operate as source identifiers.
- Feature availability by study must be reported.

## 11. Leakage and proxy audit

Before modelling, every candidate feature is classified as:

- safe predictor;
- possible target proxy;
- post-outcome variable;
- provenance/source identifier;
- ambiguous.

`removal_percent` is not a default predictor of `qe` because it can be algebraically coupled to adsorption capacity through concentration, solution volume and adsorbent mass.

Variables derived directly from the target are prohibited from the primary model.

## 12. Duplicate and lineage audit

V3 must detect and document:

- exact duplicate rows;
- near-duplicate experimental conditions;
- same experiment copied through secondary compilations;
- overlapping datasets across papers from the same research group;
- re-publication of the same experimental series.

A `lineage_cluster_id` may be used for audit and sensitivity splitting, but never as a predictor.

## 13. Data-freeze gates

### Gate A — domain freeze

Before modelling:

- selected domain documented;
- inclusion/exclusion criteria locked;
- candidate primary-study list frozen for the first development cycle.

### Gate B — provenance freeze

Before train/test analysis:

- every primary row has verified `primary_study_id`;
- unresolved rows separated;
- duplicate/lineage audit complete;
- study-size distribution reported.

### Gate C — feature freeze

Before model comparison:

- primary target fixed;
- primary feature set fixed;
- allowed transformations documented;
- external validation dataset(s) locked.

## 14. Validation design

### 14.1 Primary evaluation

Primary result: **primary-study GroupKFold**.

All rows from a primary study must remain in one fold.

### 14.2 Robustness evaluation

- Leave-One-Study-Out (LOSO) when computationally feasible.
- Repeated GroupKFold with multiple deterministic group allocations where study count permits.
- Equal-study summaries in addition to pooled row-level metrics.
- Dominant-study removal sensitivity when one source contributes >20% of rows.

### 14.3 Diagnostic random evaluation

Shuffled row-random CV will be retained only to quantify the interpolation/generalisation gap established in Paper 1. It is not the success gate for Paper 2.

### 14.4 External validation

At least one external corpus should be locked before final model selection when feasible.

External evidence hierarchy:

1. primary-study-disjoint corpus with row-level provenance;
2. publication-level disjoint corpus with defensible feature mapping;
3. experimental prospective validation;
4. external filename/dataset without proven source independence — contextual only.

## 15. Baselines and model-development hierarchy

Models are introduced in the following order:

1. naive global mean/median predictor;
2. training-study mean-aware diagnostic baseline where scientifically appropriate, never using held-out study information;
3. linear regression / regularised linear model;
4. SVR;
5. Random Forest;
6. XGBoost;
7. ExtraTrees;
8. CatBoost;
9. hierarchical/mixed-effects or domain-aware approaches if the data structure supports them;
10. stacking/ensembling only if it improves group-aware validation beyond the strongest base learner.

Neural networks are not prioritised unless the independent-study count and descriptor dimensionality justify them.

## 16. Hyperparameter tuning policy

- Nested or training-only group-aware tuning for the primary analysis.
- No tuning on external validation outcomes.
- No post-hoc switch of success metric after results are observed.
- Search space and objective metric documented before the final tuning cycle.
- Simpler model preferred when study-aware performance is statistically indistinguishable.

## 17. Primary metrics

Report at minimum:

- pooled GroupKFold R²;
- pooled GroupKFold RMSE;
- pooled GroupKFold MAE;
- LOSO R²/RMSE/MAE where feasible;
- median per-study MAE;
- interquartile range of per-study MAE;
- equal-study mean MAE;
- random-vs-grouped ΔR² as a diagnostic;
- calibration/residual diagnostics;
- prediction interval or uncertainty coverage if an uncertainty method is claimed.

## 18. Predeclared development success levels

These are project decision thresholds, not universal claims.

### Level 0 — unsuccessful transferable model

- primary-study GroupKFold R² <= 0, or
- performance is dominated by one or two studies, or
- external transfer is clearly non-generalising.

### Level 1 — weak transferable signal

- GroupKFold R² > 0 but < 0.30;
- materially better than naive baselines;
- performance remains unstable across held-out studies.

### Level 2 — useful research predictor

Target criteria:

- GroupKFold R² >= 0.50;
- LOSO or repeated-group validation remains clearly positive;
- no single study determines the result;
- per-study error distribution is acceptable for the declared domain;
- at least one external test is positive or otherwise scientifically interpretable.

### Level 3 — strong transferable predictor

A stronger claim requires substantially higher and stable study-held-out performance, robust external validation, calibrated uncertainty, and a well-defined applicability domain. Deployment or inverse-design claims require additional prospective evidence and are not implied by Level 2 alone.

## 19. Interpretation guardrails

Paper 2 will not claim:

- universal adsorption prediction outside the selected domain;
- deployment readiness based only on cross-validation;
- inverse-design validity merely because numerical optimisation can be performed;
- physical constraints as universal laws unless independently justified;
- superiority of an ensemble unless it survives group-aware evaluation;
- causality from feature importance alone.

## 20. Planned outputs

V3 development will produce:

- `adsorption_v3_raw_provenance.csv` — immutable extraction ledger;
- `adsorption_v3_curated.csv` — cleaned modelling dataset;
- `v3_study_registry.csv` — one row per primary study;
- `v3_exclusion_log.csv` — excluded records and reasons;
- `v3_feature_dictionary.csv` — semantics, units and allowed transformations;
- reproducible source-verification notes;
- deterministic validation scripts;
- CI-locked metrics and figures;
- a final numerical source-of-truth document before manuscript drafting.

## 21. Immediate next phase

No predictive model is to be trained yet.

The next controlled phase is **Domain Feasibility Audit**:

1. enumerate candidate primary studies for dyes, heavy metals, ammonia-N and emerging organics;
2. deduplicate source lineage;
3. estimate independent-study counts and descriptor coverage;
4. score domains using the predeclared matrix;
5. select the V3 modelling domain before extracting the full dataset.
