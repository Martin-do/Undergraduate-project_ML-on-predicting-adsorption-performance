# ID-SEAD Conference Salvage — Numerical Lineage Audit

Status: forensic freeze for conference salvage.

Purpose: determine whether the material numerical claims in the legacy ID-SEAD manuscript can be traced to executed repository outputs, and separate (a) a number occurring in a legacy notebook from (b) a scientifically defensible performance claim.

## Decision rule

A legacy number is **not** submission-ready merely because it can be found in an executed notebook. It must also survive the corrected evidence standard: provenance-controlled data, fold-safe preprocessing/tuning, no final-test-set model selection, study-aware validation, justified constraints, and traceable optimisation artifacts.

## Authoritative legacy artifacts inspected

- `ID_SEAD_Complete.ipynb`
- `ID_SEAD_SectionF_v2.ipynb`
- `ID_SEAD_Validation_v2.ipynb`
- dedicated Table-III / inverse-design notebook(s) already mapped in `FORENSIC_RECONCILIATION.md`
- current V2/V2.1 study-aware audit outputs for corrected comparison

## Numerical findings

| Claim / metric | Manuscript value | Executed repository evidence | Lineage verdict | Conference action |
|---|---:|---|---|---|
| Final ID-SEAD R² | 0.847 | `ID_SEAD_Complete.ipynb` contains executed final/table outputs at **0.8069**, not 0.847. Another legacy variant is ~0.807. The manuscript value has not been located in the inspected authoritative notebooks. | **UNREPRODUCED / RED** | Do not reuse 0.847. Preserve only as a manuscript-era claim. Any new performance number must come from corrected validation. |
| Final ID-SEAD RMSE | 254.1 mg/g | Executed Table-I output paired with R²=0.8069 gives **286.29 mg/g**. | **UNREPRODUCED / RED** | Replace; do not mix manuscript R²/RMSE with notebook outputs. |
| 95% CI for R² | [0.811, 0.879] | Executed Table-I output paired with R²=0.8069 gives **[0.7578, 0.8407]**. Bootstrap is also downstream of the legacy selection design. | **UNREPRODUCED + methodologically contaminated / RED** | Remove manuscript CI. Regenerate only under corrected validation. |
| CV R² | 0.789 ± 0.031 | Current executed legacy notebook does not yield this reported value. Lambda-CV output includes **0.7664** for the selected/leading candidate; a later CV sweep is around the mid-0.76 range. | **UNREPRODUCED / RED** | Do not report 0.789 ± 0.031. Recompute with grouped, fold-safe CV if a CV summary is retained. |
| Baseline violation rate | 49.2% | Executed output contains **49.23%** for the unconstrained meta-learner. | **TRACEABLE LEGACY VALUE / AMBER** | May be described only as a legacy random-split diagnostic, not as generalisation evidence. |
| ID-SEAD violation rate | 33.9% | Executed outputs contain **33.85%** in one legacy variant, and **32.31%** in another variant. Constraint selection is test-informed and the violation definition uses the retired Q_MAX=624 ceiling. | **NUMERICALLY TRACEABLE BUT SCIENTIFICALLY INVALID / RED** | Do not use 33.9% as validated feasibility improvement. Redefine constraints and rerun prospectively. |
| Perturbation sensitivity | 8.73 mg/g | The reported 8.73 value was not located. Executed legacy variants include sensitivity around **10.01–10.31 mg/g** for ID-SEAD; other runs differ. | **UNREPRODUCED / RED** | Remove 8.73. Freeze a perturbation protocol and rerun. |
| Lipschitz contribution | claimed beneficial | Stored ablation output gives **No Lipschitz: 33.85% violation, 10.0119 mg/g sensitivity, cv_std 0.0469** and **ID-SEAD: 33.85%, 10.0119 mg/g, 0.0469** — numerically identical in that executed table. | **NOT SUPPORTED / RED** | Withdraw claim that the stored ablation establishes a distinct Lipschitz benefit. Investigate implementation before any future claim. |
| Upper-bound ablation | claimed meaningful constraint effect | Stored ablation output gives `No UpperBound` about **46.15% violation** and **16.9429 mg/g sensitivity**, but the bound is Q_MAX=624, which the corrected corpus invalidates as a universal physical ceiling. | **LEGACY EFFECT ON INVALID CONSTRAINT / RED** | Do not interpret as physical-feasibility evidence. |
| Q_MAX physical ceiling | 624 mg/g | Legacy notebook explicitly configures Q_MAX=624, while the reconstructed corpus contains valid observations above that value. | **INVALID ASSUMPTION / RED** | Retire. Any future bound must be domain-specific and independently justified. |
| Table III optimiser | Differential Evolution | Repository lineage conflicts: the dedicated robust Table-III implementation uses a large Monte-Carlo candidate search plus L-BFGS-B polishing rather than the manuscript's claimed DE path. | **PROVENANCE CONFLICT / RED** | No Table-III recommendation survives until one authoritative optimisation implementation is frozen and logged. |
| Table III targets | 100, 200, 350 mg/g | Dedicated reconstruction uses **100, 250, 400 mg/g**; legacy notebook history also contains other target sets. | **PROVENANCE CONFLICT / RED** | Do not reproduce manuscript table as if computationally verified. |
| 100% robustness/consistency | 100% | Robustness depends on a specific perturbation count, relative ±1% perturbations and an explicit target-error tolerance; manuscript does not freeze these sufficiently. | **UNDER-SPECIFIED / AMBER-RED** | Replace with explicitly defined empirical robustness if recomputed. |
| Runtime <3 min | <3 min | Legacy/reconstruction runs have materially different elapsed times depending on optimiser and run; no single frozen hardware/environment benchmark currently supports a deployment claim. | **UNSTABLE / AMBER** | If retained, report only as a reproducibility benchmark with hardware, software, optimiser, seed and run definition. |
| SHAP interpretation | supports design interpretation | No clear `TreeExplainer`/equivalent executed SHAP lineage was identified in the principal complete notebook during this pass; manuscript-level interpretation is therefore not currently tied to a frozen artifact. | **LINEAGE INCOMPLETE / AMBER-RED** | Locate a dedicated artifact or regenerate under the corrected model; otherwise remove SHAP-dependent claims. |

## Critical methodological finding: final-test-set contamination

The legacy Section-F path is not a clean held-out evaluation. Candidate constraint settings are evaluated using the objects representing the final test responses/predictions (`yte_np`, `test_base_norm`) and the preferred setting is selected using resulting test-set performance/violation/sensitivity. The same test data are then used to report final performance. Therefore the reported final-test metrics are not estimates from an untouched holdout.

This defect is independent of the dataset-provenance problem. Fixing only the 322-row dataset does not repair it.

## Internal inconsistency finding

`ID_SEAD_Complete.ipynb` contains multiple sequential variants/re-runs that do not produce one unique, immutable Table-I/Table-II state. Examples include:

- final/table R² = 0.8069, RMSE = 286.29 mg/g, CI R² = [0.7578, 0.8407];
- unconstrained violation = 49.23%;
- constrained violation appearing as 33.85% in one output and 32.31% in another;
- ID-SEAD sensitivity around 10 mg/g rather than the manuscript's 8.73 mg/g;
- a Lipschitz ablation in which `No Lipschitz` and `ID-SEAD` are numerically identical.

Accordingly, the repository does not presently support treating the legacy manuscript table as a frozen computational result.

## What survives from legacy ID-SEAD

### Retainable as historical/system description

- The stacked architecture was implemented.
- A constraint-aware training/optimisation concept was implemented.
- The legacy experiments provide a useful case study of how conventional row-wise validation and weak provenance can create apparently persuasive engineering performance.

### Not retainable as validated engineering evidence

- R²=0.847 / RMSE=254.1 as a defensible untouched-test result.
- CI [0.811,0.879] as a defensible generalisation interval.
- CV R²=0.789±0.031 as currently stated.
- 33.9% violation and 8.73 mg/g sensitivity as validated improvements.
- Q_MAX=624 as a physical feasibility ceiling.
- the claimed Lipschitz ablation benefit.
- Table III as a computationally verified DE result for 100/200/350 mg/g.
- deployment/procurement/commissioning readiness.

## Corrected evidence hierarchy for the conference paper

1. **Legacy ID-SEAD result** — shown explicitly as the historical apparent result, for forensic context only.
2. **Forensic reconstruction** — demonstrate the numerical/provenance inconsistencies and test-selection defect.
3. **Corrected V2.1 study-aware evidence** — use as the scientific evaluation of generalisation.
4. **Inverse-design reliability gate** — explain why the present corpus does not support engineering recommendation claims.
5. **Prospective rebuild** — position Paper 2/V3 as the methodology required before inverse design is tested again.

## Stop condition

No manuscript rewrite may present a legacy number as a corrected result unless that number is regenerated from a frozen, provenance-controlled dataset and a leakage-free, study-aware pipeline. The old values remain useful only as forensic/historical comparators.
