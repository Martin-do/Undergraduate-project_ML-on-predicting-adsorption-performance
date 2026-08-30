# ID-SEAD Conference Salvage — Restructure Blueprint

Status: drafting blueprint after numerical-lineage closure.

## Proposed scientific position

The conference paper should no longer claim that the legacy ID-SEAD implementation has established reliable, deployment-ready inverse design. Instead, it should use ID-SEAD as a concrete engineering case study showing how apparently strong literature-derived adsorption-ML performance can fail when provenance, study independence, validation design and inverse-design reliability are examined rigorously.

This preserves the ID-SEAD contribution while bringing the conference paper into alignment with the locked Paper-1 evidence and the prospective Paper-2/V3 rebuild.

## Working title options

### Preferred
**From Apparent Accuracy to Reliable Inverse Design: A Study-Aware Audit of ID-SEAD for Adsorption-System Optimisation**

### Alternative 1
**When Random-Split Accuracy Is Not Enough: Re-Evaluating Constraint-Aware Inverse Design for Literature-Derived Adsorption Data**

### Alternative 2
**ID-SEAD Revisited: Provenance-Aware Validation and Reliability Limits in Adsorption-System Inverse Design**

## Central research question

Can the engineering claims of a constraint-aware adsorption inverse-design framework survive reconstruction of source provenance and validation on genuinely unseen primary studies?

## Contribution statement

The paper contributes:

1. a forensic reconstruction of the original ID-SEAD modelling corpus and computational claims;
2. a direct comparison between conventional row-random validation and primary-study-aware validation;
3. an empirical demonstration that strong row-random performance does not imply reliable unseen-study generalisation;
4. a reliability gate for determining whether a literature-trained surrogate is fit for inverse-design use;
5. practical requirements for future provenance-aware adsorption inverse-design datasets and pipelines.

## Proposed paper architecture

### 1. Introduction

- Motivate adsorption-process optimisation and the appeal of ML surrogate models.
- Introduce inverse design as a higher-risk use of ML than ordinary forward prediction: the optimiser can deliberately search regions where the surrogate is least reliable.
- Introduce ID-SEAD as the motivating constraint-aware framework.
- State the methodological concern: literature rows are clustered within primary studies and cannot automatically be treated as independent experimental observations.
- State the research question above.
- Do **not** claim deployment readiness in the Introduction.

### 2. Legacy ID-SEAD formulation

Describe, factually and without endorsement:

- LR, SVR, RF and XGBoost base learners;
- out-of-fold stacking into a Ridge meta-learner;
- legacy constraint-aware objective;
- legacy random/stratified row split;
- legacy inverse-design concept.

Report legacy headline numbers only as historical results being audited, with explicit language such as:

> Under the original row-wise evaluation, the framework appeared to achieve high predictive performance and lower constraint-violation rates. These values are treated here as legacy apparent-performance estimates rather than as independent-study generalisation estimates.

Do not present 0.847/254.1/8.73 as reproduced values.

### 3. Forensic data and computational reconstruction

#### 3.1 Primary-source provenance reconstruction

Report the verified reconstruction state:

- 322 usable-target observations in the reconstructed corpus;
- 307/322 with confirmed primary-study provenance;
- 29 reconstructed primary studies;
- strict comparable modelling population: 273 observations from 24 studies.

Explain why `study_id`/primary-source grouping changes the evaluation question.

#### 3.2 Domain audit

Explicitly correct the legacy agricultural-waste framing.

Report the predeclared audited subsets, including:

- strict agricultural waste: 65 rows / 4 studies;
- broader biogenic-waste domain: 92 rows / 6 studies;
- waste-derived-carbon domain: 138 rows / 7 studies.

Do not imply that all 322 observations are agricultural-waste-derived.

#### 3.3 Computational-lineage audit

Summarise the numerical discrepancies:

- manuscript R²=0.847 / RMSE=254.1 not reproduced in the inspected executed final notebook state;
- executed Table-I state R²=0.8069 / RMSE=286.29 / CI=[0.7578,0.8407];
- manuscript CV 0.789±0.031 not recovered; stored CV results are around the mid-0.76 range;
- manuscript sensitivity 8.73 not recovered; stored variants are around 10 mg/g;
- saved `No Lipschitz` and `ID-SEAD` ablation rows are numerically identical;
- Table-III optimiser/target lineage conflicts.

#### 3.4 Validation-design audit

State clearly that the legacy constraint-selection path evaluates candidate settings on final-test objects and therefore the final test is not untouched.

This is a methodological defect, not an allegation of misconduct.

### 4. Corrected validation protocol

Primary arm:

- provenance-controlled V2.1 population;
- preprocessing fitted only inside training folds;
- study-grouped evaluation;
- strict leave-one-study-out evaluation where appropriate;
- no final-test information used for hyperparameter/constraint selection;
- row-random evaluation retained only as a comparator demonstrating optimism.

### 5. Results

#### 5.1 Apparent row-wise performance versus study-aware performance

Use the locked Paper-1 source-of-truth values, including the major XGB contrast:

- row-random R² ≈ 0.8936;
- grouped-study R² ≈ 0.1929;
- strict LOSO R² ≈ 0.1624.

This becomes the central result.

#### 5.2 Domain-specific generalisation

Report the domain audit rather than forcing the legacy scope:

- strict agricultural-waste subset: XGB LOSO R² ≈ -2.038 across 4 independent studies;
- broad biogenic subset: pooled LOSO XGB R² ≈ 0.619 across 6 studies, but with severe held-out-study instability;
- waste-derived-carbon subset: pooled LOSO XGB R² ≈ 0.495 across 7 studies.

#### 5.3 Failure heterogeneity

Emphasise that pooled metrics are not sufficient. In the broad-biogenic analysis, at least one complete held-out study exhibits catastrophic error (MAE ≈ 1532.57 mg/g).

#### 5.4 Reliability / inverse-design gate

Show that uncertainty and model-agreement diagnostics do not reliably identify the catastrophic failure. Therefore, the current corpus fails the gate required for trustworthy inverse design.

### 6. Discussion

Core interpretation:

- The original ID-SEAD idea is not disproved in general.
- The current heterogeneous literature corpus cannot support the strength of the original inverse-design claim.
- Conventional row-random evaluation answers an easier question because study-specific signatures can be shared between training and test rows.
- Constraints imposed on a surrogate cannot create reliable extrapolative knowledge that is absent from the training evidence.
- Physical-feasibility claims require independently justified domain constraints; an empirical maximum such as 624 mg/g is not a universal physical law.
- Inverse design needs stronger validation than forward prediction because optimisation can exploit surrogate error.

### 7. Prospective framework for a rebuilt ID-SEAD

Connect to Paper 2/V3 without using incomplete V3 phosphate staging as evidence.

Requirements:

- verified primary-source lineage;
- explicit material/precursor and pollutant context;
- repeated operating-condition observations within comparable systems;
- study-aware nested validation;
- fold-safe preprocessing;
- training-only hyperparameter/constraint tuning;
- predeclared inverse-design objective;
- applicability-domain/reliability gate;
- machine-readable optimiser logs;
- external and preferably laboratory validation before engineering recommendation claims.

### 8. Conclusion

The defensible conclusion is not that ID-SEAD has already solved adsorption inverse design. It is that the forensic reconstruction demonstrates why apparently strong predictive performance is insufficient evidence for inverse-design reliability, and establishes a reproducible validation framework for testing future ID-SEAD versions.

## Legacy claims that must not reappear as current evidence

- R² = 0.847 as a reproduced untouched-test result;
- RMSE = 254.1 mg/g as its paired reproduced value;
- CI [0.811,0.879] as a validated generalisation interval;
- CV R² = 0.789±0.031 without new grouped fold-safe computation;
- 33.9% violation reduction as validated physical-feasibility evidence;
- sensitivity = 8.73 mg/g;
- Q_MAX = 624 mg/g as a universal physical limit;
- a demonstrated Lipschitz ablation benefit from the stored table;
- Table III as a verified DE result for 100/200/350 mg/g;
- procurement, commissioning or deployment readiness.

## Figures/tables to build

1. **Fig. 1 — ID-SEAD and audit workflow:** legacy pipeline -> provenance reconstruction -> study-aware validation -> reliability gate.
2. **Fig. 2 — Validation contrast:** row-random vs grouped-study vs LOSO performance.
3. **Fig. 3 — Study-wise LOSO errors:** expose heterogeneity hidden by pooled metrics.
4. **Table I — Corpus reconstruction and domain subsets.**
5. **Table II — Legacy claim versus reproduced legacy output versus corrected disposition.**
6. **Table III — Corrected study-aware predictive results (no inverse-design recommendation table unless a new prospective experiment passes the gate).**

## Conference defence position in one sentence

**ID-SEAD remains a viable research concept, but this audit shows that the legacy literature corpus and validation design were insufficient to establish reliable inverse-design generalisation; the contribution of the present paper is the evidence-backed correction and the validation framework required before such a claim can be made.**
