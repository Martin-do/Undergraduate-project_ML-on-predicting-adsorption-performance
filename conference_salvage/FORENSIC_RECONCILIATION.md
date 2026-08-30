# ID-SEAD Conference Salvage — Forensic Reconciliation

Status: active working branch. **The legacy inverse-design engineering claim is currently a failed scientific gate, not a submission-ready result.**

## Purpose

Reconstruct the original ID-SEAD computational lineage, identify which manuscript claims are reproducible, and determine what can be retained for an urgent conference submission without changing or contradicting the locked Paper 1 evidence.

## Stop condition established by the current evidence

The existing V2 Phase 6 audit already tested whether the original inverse-design framing could be restored after study-aware validation and uncertainty analysis. Its explicit conclusion is: **inverse-design framing FAIL for this dataset and current scientific evidence**. This is not an editorial defect that can be repaired by rewriting the original manuscript. Retracing can recover the historical algorithm and reproduce old calculations, but a scientifically defensible engineering inverse-design claim requires new validation evidence beyond the present corpus.

Accordingly, this branch has two separate goals:

1. **Legacy replication** — recover exactly how the original ID-SEAD numbers and tables were produced, for provenance and accountability only.
2. **Conference salvage** — preserve only defensible elements of ID-SEAD (architecture, constrained-surrogate concept, failure analysis, and methodological lessons) and rebuild the conference contribution around what the corrected evidence supports. No reliable deployment/inverse-design claim will be reinstated unless a new predeclared validation gate passes.

## Confirmed findings from legacy artifacts

### F1 — Test-set use during constraint-weight selection (critical)
`ID_SEAD_SectionF_v2.ipynb` sweeps `alpha_constraint`, evaluates each candidate using `test_base_norm` and `yte_np`, and selects the candidate based on test-set violation/R²/sensitivity. Therefore the held-out test set participates in model selection. Legacy ID-SEAD headline test metrics must not be treated as untouched holdout estimates.

Required remediation for any future model: choose all penalty weights and model hyperparameters strictly inside training data (nested/grouped CV as applicable), then evaluate once on untouched holdout/grouped folds.

### F2 — Table III computational lineage does not match manuscript (critical)
The manuscript describes Differential Evolution and targets 100/200/350 mg/g. `ID_SEAD_TableIII_Robust.ipynb` instead uses 200,000 Monte-Carlo candidates plus L-BFGS-B local refinement and targets 100/250/400 mg/g. It applies 50 relative ±1% perturbations and defines robustness as the fraction within ±15 mg/g.

Required remediation: the historical manuscript Table III cannot be claimed as reproduced by this notebook. Any future numerical demonstration must use one authoritative optimizer implementation and save deterministic logs.

### F3 — Universal Q_MAX=624 mg/g is unsupported (critical)
The V2.1 source corpus contains observations above 624 mg/g. The current Paper 1 evidence freeze explicitly retires the legacy universal Q_MAX constraint.

Required remediation: do not use 624 mg/g as a universal physical ceiling.

### F4 — Inverse-design decision vector is under-specified (critical)
Legacy Table III optimizes pH, temperature, dose, and initial concentration while the forward model also depends on material descriptors such as surface area/pore volume and material class. A process vector alone is not an adsorbent recommendation.

### F5 — Objective mismatch (critical)
The manuscript states an `argmax f(x)` optimization but Table III reports exact matching to specified target capacities. These are different optimization problems.

### F6 — Pollutant context is omitted from the legacy forward model (high)
The archived data contain pollutant identity, while the legacy seven-feature ID-SEAD model omits pollutant identity/chemistry. A single surrogate spanning distinct adsorbates without contextualization is not a defensible prescriptive model.

### F7 — Submitted agricultural-waste scope does not match the audited corpus (critical)
V2 Phase 6 records that the original agricultural-waste-only scope does not match the actual dataset. In the current strict-comparable V2.1 population, only a minority of rows are classified as strict agricultural waste, and the strict agricultural subset contains only four primary studies. The original 322-row corpus therefore cannot be described wholesale as 322 agricultural-waste adsorption experiments.

### F8 — Study-aware reliability is insufficient for inverse optimisation (critical)
V2 Phase 6 found that restricted-domain cross-study uncertainty intervals were extremely wide yet still missed a catastrophic held-out study; RF–XGB agreement also coexisted with errors above 1500 mg/g. This is the failure mode that makes optimisation over the surrogate unsafe: the optimiser can exploit a region where the model appears confident but is jointly wrong.

## V2.1 evidence that must be preserved

- Canonical usable-target corpus: 322 rows.
- Primary-study provenance confirmed for 307/322 rows, representing 29 reconstructed studies.
- Strict comparable set: 273 rows from 24 primary studies.
- Legacy-style random splitting produces extensive source overlap.
- Study-grouped performance is much lower than row-random performance.
- The strict agricultural subset has only four primary studies and fails leave-one-study-out reliability.
- Paper 1 findings remain locked and must not be weakened to rescue the conference paper.

## What is and is not salvageable

| Component / claim | Status | Conference use |
|---|---|---|
| ID-SEAD stacked/constrained architecture | **salvageable historically/methodologically** | describe/reconstruct with exact code lineage |
| Differential-evolution inverse-design idea | **salvageable as an algorithmic concept** | may be described or demonstrated numerically, but not presented as validated engineering design |
| R²=0.847 / CI / CV values | **not trusted as final validation** | legacy replication only |
| violation 49.2% → 33.9% | **not trusted as final validation** | legacy replication only |
| sensitivity 8.73 mg/g | **not trusted as final validation** | legacy replication only |
| Q_MAX=624 physical/training ceiling | **retired** | remove |
| DE produced submitted Table III 100/200/350 | **not supported by current Table-III artifact** | do not claim without recovering exact generating artifact |
| 100% robustness/consistency | **unsupported as an engineering-reliability claim** | remove or confine to clearly defined numerical perturbation demonstration |
| 322-row agricultural-waste dataset | **false as stated under current provenance audit** | change scope or rebuild a genuinely agricultural dataset |
| reliable adsorbent–process recommendation | **failed current scientific gate** | do not claim |
| procurement/commissioning/deployment readiness | **unsupported** | remove |

## Conference salvage routes

### Route A — Recommended: ID-SEAD as a forensic/methodological case study
Retain the ID-SEAD architecture as the motivating case, then present how provenance reconstruction, study-aware validation, constraint auditing, and uncertainty testing change the apparent conclusion. This is directly supported by the current evidence and naturally connects Paper 1 to the new conference submission without pretending the original inverse-design result survived.

### Route B — New inverse-design paper only with new evidence
A genuine inverse-design conference paper would require new validation evidence, not merely retracing the old 322 rows. At minimum: a defensibly scoped material/pollutant domain, enough independent primary studies, leakage-free grouped model selection, a predictive surrogate that passes predeclared unseen-study performance/reliability thresholds, explicit immutable context variables, a target-matching objective, an applicability-domain/reliability gate, and preferably laboratory or genuinely external validation. Until those conditions are met, Route B is blocked.

## Required gates before manuscript rewriting

- G1: exact legacy dataset row count/target filtering reconciled.
- G2: every submitted Table I/II/III number mapped to its generating artifact or marked unrecoverable.
- G3: legacy test-set tuning documented explicitly.
- G4: submitted agricultural-waste scope reconciled against V2.1 provenance/domain labels.
- G5: reference list independently repaired.
- G6: select Route A unless new evidence sufficient for Route B is obtained.
- G7: rewrite abstract/results only from frozen traceable outputs.
- G8: prepare a defence sheet separating legacy calculations, corrected evidence, limitations, and claims that were intentionally withdrawn.

No gate may be marked passed by editorial wording alone; each requires an executable artifact or traceable source record.
