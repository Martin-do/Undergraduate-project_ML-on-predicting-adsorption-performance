# ID-SEAD Conference Salvage — Claim Reconciliation Matrix

Status: active forensic working document on `conference/id-sead-salvage`.

Purpose: map each material claim in the rejected/original ID-SEAD manuscript to the exact computational or provenance evidence, classify whether it can be retained, corrected, downgraded or withdrawn, and prevent legacy numbers from being reused without traceable support.

Detailed numerical evidence is frozen in `conference_salvage/NUMERICAL_LINEAGE_AUDIT.md`.

## Status key

- **GREEN — retainable**: claim is supported by traceable evidence and can survive with normal editorial revision.
- **AMBER — rerun/rewrite**: concept may survive, but the reported value, wording or validation design must be replaced.
- **RED — withdraw/replace**: current evidence contradicts the claim or the required computational lineage is absent.
- **PENDING — forensic check required**: evidence mapping is not yet complete.

## Current matrix

| ID | Legacy claim | Legacy evidence/source | Forensic finding | Status | Conference disposition |
|---|---|---|---|---|---|
| C01 | A constraint-aware stacked ensemble architecture (LR, SVR, RF, XGB -> Ridge meta-learner) was implemented | `ID_SEAD_Complete.ipynb`; manuscript Methods | Architecture and executable implementation exist | GREEN | Retain as the historical/proposed architecture, but separate architecture existence from performance validity |
| C02 | ID-SEAD test R2 = 0.847 and RMSE = 254.1 mg/g | manuscript Table I; legacy notebooks | Executed `ID_SEAD_Complete.ipynb` gives a final/Table-I state of **R2=0.8069, RMSE=286.29 mg/g**, not the manuscript pair. 0.847 has not been located in the inspected authoritative notebooks. In addition, Section-F constraint selection evaluates candidate settings on the final test objects. | RED | Do not reuse 0.847/254.1. Preserve as manuscript-era claims only; corrected submission performance must be regenerated under leakage-free study-aware validation. |
| C03 | ID-SEAD 95% CI R2 = [0.811, 0.879] | manuscript Table I | Executed Table-I state paired with R2=0.8069 gives **[0.7578, 0.8407]**. Bootstrap is downstream of test-informed model selection. | RED | Remove manuscript CI; regenerate only under corrected validation. |
| C04 | CV R2 = 0.789 ± 0.031 | manuscript Table I | Reported value was not located in the inspected authoritative executed notebook. Legacy lambda-CV output includes **0.7664** for the leading/selected candidate and other mid-0.76 results. | RED | Do not report 0.789 ± 0.031. If CV is retained, recompute with grouped, fold-safe CV and freeze fold assignments. |
| C05 | Constraint violations fall from 49.2% to 33.9% | manuscript Table II; `ID_SEAD_Complete.ipynb`; Section-F | **49.23%** unconstrained and **33.85%** constrained occur in executed output, but another constrained variant gives **32.31%**. More importantly, candidate constraint selection uses final-test metrics and the violation definition relies on retired Q_MAX=624. | RED for scientific claim | Legacy values may be shown only as forensic diagnostics. Redefine feasibility constraints and rerun prospectively. |
| C06 | Perturbation sensitivity = 8.73 mg/g | manuscript Table II | 8.73 was not located in the inspected authoritative outputs. Executed ID-SEAD variants are around **10.01–10.31 mg/g**, and candidate selection is test-informed. | RED | Remove 8.73; predeclare perturbation variables, relative scale, seed and metric, then rerun. |
| C07 | Q_MAX = 624 mg/g is a physical/training maximum and valid universal upper constraint | manuscript Methods | V2.1 corpus contains observations above 624 mg/g; locked audit retires this ceiling | RED | Remove completely unless a narrowly defined, independently justified domain-specific bound is introduced |
| C08 | ID-SEAD supports physically feasible inverse design for the agricultural-waste corpus | manuscript Abstract/Discussion | Only 65 rows from 4 confirmed primary studies satisfy strict agricultural-waste scope; LOSO performance fails badly | RED in current corpus | Do not claim validated agricultural-waste inverse design from the current dataset |
| C09 | The 322-row dataset represents agricultural-waste-derived adsorbents | manuscript Abstract/Methods | Provenance/domain audit shows the 322-row corpus contains multiple non-agricultural precursor domains | RED | Replace with provenance-correct corpus description; do not relabel all rows as agricultural waste |
| C10 | Row-random test performance demonstrates useful generalisation | manuscript Results | V2.1 shows extensive source overlap; 62/64 legacy-style test rows have source labels represented in training | RED as unseen-study claim | Use row-random result only as a diagnostic comparator; primary result must be study-aware |
| C11 | Stacking is superior/uniquely suitable | manuscript Abstract/Discussion | Study-aware validation and restricted-domain audits show base tree models outperform the Ridge stack | RED | Remove superiority claim; stack may remain as a historical component or comparator |
| C12 | Differential Evolution generated Table III recommendations for targets 100/200/350 mg/g | manuscript Table III | Dedicated reconstruction uses 200,000 Monte-Carlo candidates + L-BFGS-B refinement and targets 100/250/400; legacy history contains additional target variants | RED | Do not defend the manuscript Table III as computationally verified. Freeze one authoritative optimiser before any future recommendation table. |
| C13 | Exact target matching follows from an argmax objective | manuscript Methods/Table III | `argmax f(x)` and target matching are different optimisation problems | RED as written | Reformulate as target-matching minimisation, e.g. minimise target error plus predeclared penalties |
| C14 | The framework recommends an adsorbent-process configuration | manuscript Abstract/Table III | Legacy decision vector optimises only pH, temperature, dose and C0 while the forward model depends on material/context variables | RED as written | Reframe as conditional process optimisation with fixed, explicitly reported adsorbent/material and pollutant context, or expand decision variables defensibly |
| C15 | Pollutant-independent inverse design is supported | legacy model formulation | Pollutant identity/context is heterogeneous in the corpus and is not adequately represented in the legacy inverse-design decision problem | RED/PENDING | Restrict to a defined pollutant domain or include immutable pollutant identity/class/descriptors in the forward model and validation |
| C16 | 100% perturbation consistency/robustness validates the optima | manuscript Table III | Robustness definition is implementation-dependent; dedicated reconstruction uses 50 relative ±1% perturbations and a ±15 mg/g tolerance, while manuscript wording is not sufficiently specified | AMBER/RED | Freeze perturbation count, variables, distribution, tolerance and seed before rerun; report empirical robustness only |
| C17 | Runtime under 3 minutes demonstrates deployability | manuscript Methods/Discussion | Legacy/reconstruction runs have materially different elapsed times; runtime is also hardware/optimiser-dependent and not evidence of engineering validity | AMBER | May report only a frozen benchmark with hardware/software/seed/optimiser after deterministic rerun |
| C18 | Laboratory/engineering deployment readiness | manuscript Abstract/Discussion | Study-aware generalisation, uncertainty and inverse-design gates fail for the current evidence | RED | Downgrade to methodological/proof-of-concept or forensic engineering case study; no procurement/commissioning claim |
| C19 | The dataset can be made provenance-controlled | V2/V2.1 reconstruction | 307/322 usable rows have confirmed primary-study provenance across 29 studies; 273 rows/24 studies form the strict comparable set | GREEN | Use V2.1 as the forensic source of truth for the current corpus |
| C20 | Missing-value/preprocessing handling is leakage-free | legacy manuscript vs V2.1 corrected workflow | Corrected V2.1 pipeline fits preprocessing inside training folds; legacy fold safety is not established as a submission-ready pipeline | AMBER for legacy; GREEN for V2.1 method | Do not retrospectively claim the legacy run was fold-safe; use corrected fold-safe implementation going forward |
| C21 | SHAP supports the claimed design variables and interpretation | manuscript SHAP interpretation | No clear executed SHAP explainer/output lineage was identified in the principal complete notebook during the numerical pass | AMBER/RED | Locate a dedicated frozen SHAP artifact or regenerate under the corrected model; otherwise remove SHAP-dependent claims |
| C22 | Ablation results establish the contribution of each constraint | executed legacy ablation | Stored table gives **No Lipschitz = 33.85% violation, 10.0119 sensitivity, cv_std 0.0469** and **ID-SEAD = exactly the same values**. Therefore the saved ablation does not demonstrate a distinct Lipschitz contribution. Upper-bound ablation is also tied to invalid Q_MAX=624. | RED | Withdraw the claimed per-constraint causal interpretation. Redesign ablation prospectively on corrected objective/splits. |
| C23 | Optimisation logs verify Table III | manuscript states logs verified | Claimed logs were not supplied; current Table-III lineage conflicts with manuscript | RED until artifact exists | Generate machine-readable per-run logs, seeds, bounds, objective values, convergence status and final candidates |
| C24 | Broad biogenic restriction may support useful prediction | V2 Phase 4 | XGB pooled LOSO R2 ≈ 0.619 across 6 studies, but one complete held-out study fails catastrophically | AMBER | Useful diagnostic result, not sufficient for reliable inverse design/deployment |
| C25 | Training-only uncertainty can reliably gate inverse design in the current corpus | V2 Phase 6 | Study-balanced residual intervals are extremely wide and still miss the catastrophic held-out study; RF-XGB agreement can coexist with large error | RED for current evidence | Do not restore inverse-design reliability claim from current corpus |

## Numerical-lineage closure status

The headline manuscript metrics are now sufficiently resolved to make a framing decision:

- **0.847 / 254.1** — not reproduced by the inspected executed final notebook state.
- **[0.811, 0.879]** — not reproduced; stored Table-I CI differs and is downstream of test-informed selection.
- **0.789 ± 0.031** — not reproduced by inspected executed CV output.
- **49.2% baseline violation** — traceable as ~49.23%, but only a legacy random-split diagnostic.
- **33.9% constrained violation** — numerically occurs as ~33.85% in one legacy variant, but is not scientifically valid as a held-out feasibility result.
- **8.73 mg/g sensitivity** — not reproduced; stored outputs are around 10 mg/g.
- **Lipschitz ablation** — stored `No Lipschitz` and `ID-SEAD` rows are numerically identical.
- **Table III** — optimiser/target provenance conflicts remain and the manuscript table cannot be defended as a frozen computation.

## Next work queue

1. Freeze the conference framing around **ID-SEAD as a forensic engineering case study**, not a validated deployment-ready inverse-design system.
2. Build the revised manuscript outline from the closed red/amber/green claim map.
3. Draft replacement Results/Discussion language using only V2.1 study-aware evidence and explicitly labelled legacy comparators.
4. Build the private defence dossier: likely hostile reviewer question -> evidence-backed answer -> repository artifact.
5. Keep Paper 2/V3 separate as the prospective, provenance-first rebuild; do not use its incomplete phosphate staging as evidence for the conference paper.

## Non-negotiable rule

A cleaner or newly reconstructed dataset does not automatically restore any legacy performance, robustness, inverse-design or deployment claim. Every such claim must be regenerated prospectively under corrected data lineage, fold-safe tuning, study-aware validation and explicitly justified design constraints.
