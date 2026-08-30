# ID-SEAD Conference Salvage — Forensic Reconciliation

Status: active working branch. Do not use legacy manuscript headline values as submission-ready evidence until all gates below pass.

## Purpose

Reconstruct the original ID-SEAD computational lineage, identify which manuscript claims are reproducible, remove leakage/unsupported constraints, and rerun a defensible inverse-design proof-of-concept without changing the locked Paper 1 conclusions.

## Confirmed findings from legacy artifacts

### F1 — Test-set use during constraint-weight selection (critical)
`ID_SEAD_SectionF_v2.ipynb` sweeps `alpha_constraint`, evaluates each candidate using `test_base_norm` and `yte_np`, and selects the candidate based on test-set violation/R²/sensitivity. Therefore the held-out test set participates in model selection. Legacy ID-SEAD headline test metrics must not be treated as untouched holdout estimates.

Required remediation: choose all penalty weights and model hyperparameters strictly inside training data (nested/grouped CV as applicable), then evaluate once on untouched holdout/grouped folds.

### F2 — Table III computational lineage does not match manuscript (critical)
The manuscript describes Differential Evolution and targets 100/200/350 mg/g. `ID_SEAD_TableIII_Robust.ipynb` instead uses 200,000 Monte-Carlo candidates plus L-BFGS-B local refinement and targets 100/250/400 mg/g. It applies 50 relative ±1% perturbations and defines robustness as the fraction within ±15 mg/g.

Required remediation: select one authoritative inverse-design algorithm and regenerate all table values/logs from it. If the manuscript retains DE, the final implementation must actually use DE for the reported outputs.

### F3 — Universal Q_MAX=624 mg/g is unsupported (critical)
The V2.1 source corpus contains observations above 624 mg/g. The current Paper 1 evidence freeze explicitly retires the legacy universal Q_MAX constraint.

Required remediation: do not use 624 mg/g as a universal physical ceiling. Retain only constraints justified for the defined design context (e.g., non-negativity, observed/declared decision-variable domain, material/pollutant-specific constraints where independently supported).

### F4 — Inverse-design decision vector is under-specified (critical)
Legacy Table III optimizes pH, temperature, dose, and initial concentration while the forward model also depends on material descriptors such as surface area/pore volume and material class. A process vector alone is not an adsorbent recommendation.

Required remediation: formulate inverse design as conditional process optimization: hold adsorbent/material descriptors and pollutant context fixed and report them explicitly, or expand the decision problem to include defensible material variables. Do not claim a specific adsorbent is selected unless the model actually selects one.

### F5 — Objective mismatch (critical)
The manuscript states an `argmax f(x)` optimization but Table III reports exact matching to specified target capacities. These are different optimization problems.

Required remediation: use a target-matching objective such as `min |f(x)-q_target|` (plus predeclared robustness/domain penalties), or change the manuscript claim. For the conference paper, target matching is the intended task.

### F6 — Pollutant context must be explicit (high)
The archived data contain pollutant identity, while the legacy seven-feature ID-SEAD model omits pollutant identity/chemistry. A single surrogate spanning distinct adsorbates without contextualization is difficult to defend for prescriptive design.

Required remediation: include pollutant identity/class/defensible descriptors as immutable context, or restrict the inverse-design demonstration to a clearly defined pollutant domain.

## V2.1 evidence that must be preserved

- Canonical usable-target corpus: 322 rows.
- Primary-study provenance confirmed for 307/322 rows, representing 29 reconstructed studies.
- Strict comparable set: 273 rows from 24 primary studies.
- Legacy-style random splitting produces extensive source overlap.
- Study-grouped performance is much lower than row-random performance; inverse-design/deployment claims therefore require new validation and cannot inherit legacy random-split metrics.
- Paper 1 findings remain locked and must not be weakened to rescue the conference paper.

## Salvage strategy

Two outputs will be maintained separately:

1. **Legacy replication track** — reproduce the old pipeline as faithfully as possible and map every manuscript number to code/output. Purpose: forensic lineage only, not final scientific validation.
2. **Corrected conference track** — leakage-free, provenance-aware rerun. Hyperparameters/constraints selected within training folds; study-aware evaluation reported; inverse design conditioned on material/pollutant context; one authoritative optimizer; deterministic seeds/logs; no universal 624 mg/g ceiling.

## Claim status

| Manuscript claim | Current status | Action |
|---|---|---|
| ID-SEAD architecture exists | salvageable | reconstruct and document |
| R²=0.847 / CI / CV values | untrusted pending replication | reproduce, then replace with corrected results |
| violation 49.2% → 33.9% | untrusted pending replication | reproduce with exact definition; rerun leakage-free |
| sensitivity 8.73 mg/g | untrusted pending replication | reproduce with exact perturbation protocol; rerun |
| Q_MAX=624 is physical/training maximum | retired | remove |
| DE generated Table III 100/200/350 | not supported by current Table-III notebook | regenerate from authoritative code |
| exact target matching | potentially salvageable as surrogate optimization | use target-matching objective and report tolerance |
| 100% robustness/consistency | definition-dependent | predeclare tolerance, perturbation count and seed |
| adsorbent–process recommendation | unsupported as currently parameterized | condition on explicit material descriptors or expand design variables |
| deployment/procurement readiness | unsupported | downgrade to computational proof-of-concept pending laboratory/external validation |

## Required gates before manuscript rewriting

- G1: exact legacy dataset row count/target filtering reconciled.
- G2: every headline Table I/II metric mapped to executable code/output.
- G3: constraint/hyperparameter tuning removed from final test data.
- G4: row-random and primary-study-aware evaluations generated on matched populations.
- G5: Q_MAX=624 removed from corrected scientific constraints.
- G6: inverse-design context variables (material/pollutant/SA/PV) made explicit.
- G7: target-matching objective and bounds predeclared.
- G8: one optimizer implementation produces final Table III and saved logs.
- G9: robustness definition/tolerance/seed/number of perturbations frozen before results.
- G10: references and claims independently checked.
- G11: conference abstract/results rewritten only from frozen corrected outputs.

No gate may be marked passed by editorial wording alone; each requires an executable artifact or traceable source record.
