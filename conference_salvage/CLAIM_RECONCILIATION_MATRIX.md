# ID-SEAD Conference Salvage — Claim Reconciliation Matrix

Status: active forensic working document on `conference/id-sead-salvage`.

Purpose: map each material claim in the rejected/original ID-SEAD manuscript to the exact computational or provenance evidence, classify whether it can be retained, corrected, downgraded or withdrawn, and prevent legacy numbers from being reused without traceable support.

## Status key

- **GREEN — retainable**: claim is supported by traceable evidence and can survive with normal editorial revision.
- **AMBER — rerun/rewrite**: concept may survive, but the reported value, wording or validation design must be replaced.
- **RED — withdraw/replace**: current evidence contradicts the claim or the required computational lineage is absent.
- **PENDING — forensic check required**: evidence mapping is not yet complete.

## Current matrix

| ID | Legacy claim | Legacy evidence/source | Forensic finding | Status | Conference disposition |
|---|---|---|---|---|---|
| C01 | A constraint-aware stacked ensemble architecture (LR, SVR, RF, XGB -> Ridge meta-learner) was implemented | `ID_SEAD_Complete.ipynb`; manuscript Methods | Architecture and executable implementation exist | GREEN | Retain as the historical/proposed architecture, but separate architecture existence from performance validity |
| C02 | ID-SEAD test R2 = 0.847 and RMSE = 254.1 mg/g | manuscript Table I / `ID_SEAD_SectionF_v2.ipynb` lineage | Constraint weight selection evaluates candidate settings on `test_base_norm` and `yte_np`; final holdout is therefore not untouched | AMBER | Reproduce legacy number for lineage only; replace submission claim with leakage-free study-aware result |
| C03 | ID-SEAD 95% CI R2 = [0.811, 0.879] | bootstrap over selected test predictions | Bootstrap is downstream of test-informed model selection and does not repair selection bias | AMBER | Do not report as independent generalisation CI; regenerate under corrected validation |
| C04 | CV R2 = 0.789 ± 0.031 | manuscript Table I | Exact fold construction and relationship to tuning require complete mapping | PENDING | Trace exact generating cell/output; replace if folds are row-random or preprocessing/tuning is not fold-safe |
| C05 | Constraint violations fall from 49.2% to 33.9% | manuscript Table II / Section F notebook | Reported constrained model is selected using test-set violation/R2/sensitivity; definition also depends on retired Q_MAX=624 | RED for numerical claim | Retain only as legacy forensic result; redefine feasibility constraints and rerun |
| C06 | Perturbation sensitivity = 8.73 mg/g | manuscript Table II / Section F notebook | Candidate penalty selection uses test-set sensitivity; perturbation protocol requires exact freeze | AMBER | Predeclare perturbation variables, scale, seed and metric; rerun without test-informed selection |
| C07 | Q_MAX = 624 mg/g is a physical/training maximum and valid universal upper constraint | manuscript Methods | V2.1 corpus contains observations above 624 mg/g; locked audit retires this ceiling | RED | Remove completely from corrected scientific claim unless a narrowly defined, independently justified domain-specific bound is introduced |
| C08 | ID-SEAD supports physically feasible inverse design for the agricultural-waste corpus | manuscript Abstract/Discussion | Only 65 rows from 4 confirmed primary studies satisfy the strict agricultural-waste scope; LOSO performance fails badly | RED in current corpus | Do not claim validated agricultural-waste inverse design from the current dataset |
| C09 | The 322-row dataset represents agricultural-waste-derived adsorbents | manuscript Abstract/Methods | Provenance/domain audit shows the 322-row corpus contains multiple non-agricultural precursor domains | RED | Replace with provenance-correct corpus description; do not relabel all rows as agricultural waste |
| C10 | Row-random test performance demonstrates useful generalisation | manuscript Results | V2.1 shows extensive source overlap; 62/64 legacy-style test rows have source labels represented in training | RED as unseen-study claim | Use row-random result only as a diagnostic comparator; primary result must be study-aware |
| C11 | Stacking is superior/uniquely suitable | manuscript Abstract/Discussion | Study-aware validation and restricted-domain audits show base tree models outperform the Ridge stack | RED | Remove superiority claim; stack may remain as a historical component or comparator |
| C12 | Differential Evolution generated Table III recommendations for targets 100/200/350 mg/g | manuscript Table III | Dedicated robust Table-III notebook uses 200,000 Monte-Carlo candidates + L-BFGS-B refinement and targets 100/250/400 | RED until regenerated | Choose one authoritative optimiser; if DE is retained, regenerate Table III and save deterministic logs |
| C13 | Exact target matching follows from an argmax objective | manuscript Methods/Table III | `argmax f(x)` and target matching are different optimisation problems | RED as written | Reformulate as target-matching minimisation, e.g. minimise target error plus predeclared penalties |
| C14 | The framework recommends an adsorbent-process configuration | manuscript Abstract/Table III | Legacy decision vector optimises only pH, temperature, dose and C0 while the forward model depends on material/context variables | RED as written | Reframe as conditional process optimisation with fixed, explicitly reported adsorbent/material and pollutant context, or expand decision variables defensibly |
| C15 | Pollutant-independent inverse design is supported | legacy model formulation | Pollutant identity/context is heterogeneous in the corpus and is not adequately represented in the legacy inverse-design decision problem | RED/PENDING | Restrict to a defined pollutant domain or include immutable pollutant identity/class/descriptors in the forward model and validation |
| C16 | 100% perturbation consistency/robustness validates the optima | manuscript Table III | Robustness definition is implementation-dependent; dedicated notebook uses 50 ±1% perturbations and a ±15 mg/g tolerance, while manuscript wording is not sufficiently specified | AMBER | Freeze perturbation count, variables, distribution, tolerance and seed before rerun; report empirical robustness only |
| C17 | Runtime under 3 minutes demonstrates deployability | manuscript Methods/Discussion | Runtime alone is computational, not evidence of predictive or engineering validity | AMBER | May report benchmark hardware/runtime after deterministic rerun, but not as deployment validation |
| C18 | Laboratory/engineering deployment readiness | manuscript Abstract/Discussion | Study-aware generalisation, uncertainty and inverse-design gates fail for the current evidence | RED | Downgrade to methodological/proof-of-concept or forensic engineering case study; no procurement/commissioning claim |
| C19 | The dataset can be made provenance-controlled | V2/V2.1 reconstruction | 307/322 usable rows have confirmed primary-study provenance across 29 studies; 273 rows/24 studies form the strict comparable set | GREEN | Use V2.1 as the forensic source of truth for the current corpus |
| C20 | Missing-value/preprocessing handling is leakage-free | legacy manuscript vs V2.1 corrected workflow | Corrected V2.1 pipeline fits preprocessing inside training folds, but legacy pipeline requires exact reconstruction | PENDING for legacy; GREEN for V2.1 method | Do not retrospectively claim the legacy run was fold-safe unless code proves it; use corrected fold-safe implementation going forward |
| C21 | SHAP supports the claimed design variables and interpretation | manuscript references SHAP but supporting result lineage is incomplete | Audit flagged supporting SHAP results as absent/incomplete | PENDING | Locate exact generating notebook/output; otherwise remove numerical/causal SHAP claims or regenerate under corrected model |
| C22 | Ablation results establish the contribution of each constraint | manuscript claims ablations | Audit found insufficient experimental detail; current reported values inherit test-informed selection/Q_MAX issue | AMBER/RED | Redesign ablation prospectively on corrected objective with identical splits and no test-set selection |
| C23 | Optimisation logs verify Table III | manuscript states logs verified | Audit found claimed logs were not supplied; current Table-III lineage conflicts with manuscript | RED until artifact exists | Generate machine-readable per-run logs, seeds, bounds, objective values, convergence status and final candidates |
| C24 | Broad biogenic restriction may support useful prediction | V2 Phase 4 | XGB pooled LOSO R2 ≈ 0.619 across 6 studies, but one complete held-out study fails catastrophically | AMBER | Useful diagnostic result, not sufficient for reliable inverse design/deployment |
| C25 | Training-only uncertainty can reliably gate inverse design in the current corpus | V2 Phase 6 | Study-balanced residual intervals are extremely wide and still miss the catastrophic held-out study; RF-XGB agreement can coexist with large error | RED for current evidence | Do not restore inverse-design reliability claim from current corpus |

## Immediate forensic work queue

1. Locate the exact generating cells/output for C04 (CV R2), C21 (SHAP), C22 (ablation) and all runtime claims.
2. Reproduce the legacy Table I/II values in a frozen environment for lineage only; label outputs `legacy_replication`, never `corrected_validation`.
3. Build a leakage-free corrected training/evaluation script from V2.1 with matched row-random and primary-study-aware arms.
4. Decide the conference-paper framing after the full claim matrix is closed. Current default: ID-SEAD as an engineering case study showing why literature-derived inverse design requires provenance-aware validation and reliability gates.
5. Build a separate defence dossier from the final matrix: likely reviewer question -> evidence-backed answer -> exact repository artifact.

## Non-negotiable rule

A cleaner or newly reconstructed dataset does not automatically restore any legacy performance, robustness, inverse-design or deployment claim. Every such claim must be regenerated prospectively under the corrected data lineage, fold-safe tuning, study-aware validation and explicitly justified design constraints.
