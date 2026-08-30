# ID-SEAD Conference Defence Dossier — V0

Purpose: private preparation material for oral presentation/defence. This is not manuscript text.

## Core rule for the presenter

Do not defend a legacy number merely because it appeared in the original manuscript. Defend only the reconstructed evidence and clearly distinguish historical apparent performance from corrected study-aware evidence.

## Likely high-pressure questions and defensible answers

### Q1. Your original model reported R²=0.847. Are you now saying that result was wrong?

**Answer:** The original manuscript reported 0.847 under the legacy workflow. During computational reconstruction, the inspected executed final notebook state produced R²=0.8069 rather than 0.847, and the constraint-selection procedure was found to use final-test information. Therefore we no longer treat 0.847 as an independently validated generalisation estimate. The important scientific finding is that once source provenance and study independence are enforced, performance is substantially lower.

### Q2. Does this mean the ID-SEAD algorithm itself is invalid?

**Answer:** No. The architecture and constraint-aware concept were implemented. What the audit invalidates is the strength of the original evidence for reliable unseen-study inverse design. The current work separates the algorithmic concept from the validation claim.

### Q3. Why is random train/test splitting inappropriate here?

**Answer:** Literature-derived datasets contain clusters of observations from the same primary study, often sharing material preparation, pollutant system, instrumentation and experimental protocol. A random row split can place observations from the same study in both training and test sets. That estimates interpolation among familiar study contexts, not generalisation to an independent study. The corrected evaluation therefore groups by primary study and uses study-aware/leave-one-study-out testing.

### Q4. How large is the reconstructed evidence base?

**Answer:** The reconstructed corpus contains 322 usable-target observations. Primary-study provenance is confirmed for 307 of those rows across 29 reconstructed studies. A stricter comparable modelling population contains 273 observations from 24 studies.

### Q5. But your manuscript calls all 322 rows agricultural waste. Is that true?

**Answer:** No, and the revised paper corrects that description. The provenance/domain audit shows that the full corpus contains multiple precursor domains. Under a strict agricultural-waste definition, only 65 rows from four independent primary studies remain. We now report domain membership explicitly rather than extending the agricultural-waste label to the complete corpus.

### Q6. What happens when the model is tested on genuinely unseen studies?

**Answer:** For XGBoost on the corrected general corpus, the contrast is large: row-random R² is about 0.894, grouped-study R² about 0.193, and strict leave-one-study-out R² about 0.162. This demonstrates that row-random accuracy substantially overstates the evidence for independent-study generalisation.

### Q7. Does restricting the domain solve the problem?

**Answer:** It helps clarify the question but does not automatically solve reliability. The strict agricultural-waste subset is too small and heterogeneous to support the old claim, with XGBoost LOSO R² around -2.04 across four studies. A broader biogenic subset has pooled LOSO R² around 0.62 across six studies, but one completely held-out study has an MAE of roughly 1533 mg/g. Therefore pooled performance alone is insufficient for inverse-design reliability.

### Q8. Why is inverse design more demanding than ordinary prediction?

**Answer:** A forward model predicts at a supplied point. An optimiser actively searches the input space for points that maximise or target the model output. If the surrogate is unreliable or extrapolating, the optimiser can preferentially exploit those errors. Therefore inverse design requires applicability-domain and uncertainty/reliability gates beyond ordinary prediction metrics.

### Q9. You imposed an upper bound of 624 mg/g. Why was that removed?

**Answer:** The legacy workflow treated 624 mg/g as an upper feasibility bound based on the earlier dataset. The provenance-reconstructed corpus contains valid observations above 624 mg/g, showing that it is not a universal physical limit. We therefore retired it. Any future physical constraint must be justified for the specific adsorbent/pollutant domain rather than inferred from one dataset maximum.

### Q10. Did the constraints actually improve robustness?

**Answer:** The stored ablation evidence does not justify that broad conclusion. In one executed table, the `No Lipschitz` and full `ID-SEAD` rows have identical violation rate, sensitivity and CV spread. The upper-bound ablation is also tied to the now-retired 624 mg/g ceiling. We therefore do not claim that the legacy ablation establishes the independent contribution of each constraint.

### Q11. What happened to the reported sensitivity of 8.73 mg/g?

**Answer:** That exact value was not recovered from the inspected authoritative executed notebook outputs. Stored ID-SEAD variants are around 10 mg/g, and the legacy constraint selection used final-test metrics. The revised work does not use 8.73 as a validated result.

### Q12. What about the 95% confidence interval [0.811,0.879]?

**Answer:** The inspected executed Table-I state gives a different interval, [0.7578,0.8407], paired with R²=0.8069. More importantly, bootstrap resampling downstream of test-informed model selection does not restore independence to the test estimate. The manuscript interval is therefore not retained as corrected evidence.

### Q13. Was there data leakage?

**Answer:** There are two distinct issues. First, random row splitting allows source/study overlap between training and test observations. Second, in the legacy Section-F path, candidate constraint settings are evaluated using final-test objects and the preferred setting is selected from those test metrics. The revised analysis treats both as methodological defects and removes them through study-aware splitting and training-only tuning.

### Q14. Are you accusing the original authors/researchers of misconduct?

**Answer:** No. This is a methodological and reproducibility audit. The findings concern validation design, provenance reconstruction, numerical lineage and claim strength. They do not establish fabrication or falsification.

### Q15. Why not simply rebuild the dataset and rerun the same ID-SEAD pipeline?

**Answer:** Because the dataset is only one source of the problem. The old pipeline also contains test-informed model selection, a non-general physical ceiling, an under-specified inverse-design context and conflicting optimisation lineage. A future ID-SEAD test therefore needs both a fit-for-purpose dataset and a corrected prospective pipeline.

### Q16. So can ID-SEAD ever support inverse design?

**Answer:** Potentially. The present evidence does not disprove the concept universally. A prospective test should use a provenance-controlled domain with repeated operating-condition observations in comparable material-pollutant systems, explicit context variables, study-aware nested validation, training-only tuning, a predeclared optimisation objective, reliability gating and external/laboratory validation.

### Q17. Why should this be considered a contribution rather than simply a failed model?

**Answer:** Because the audit demonstrates a general engineering risk: an apparently strong literature-trained surrogate can look suitable for optimisation under row-wise evaluation while failing on independent studies. ID-SEAD provides a concrete case through which we establish the validation requirements needed before adsorption ML can be trusted for inverse design.

### Q18. What is the relationship between this conference paper, Paper 1 and Paper 2?

**Answer:** Paper 1 establishes the broader methodological problem of optimistic generalisation under conventional literature-data validation. The conference paper presents ID-SEAD as the concrete engineering case study and shows how that problem affects inverse-design claims. Paper 2/V3 is the prospective provenance-first rebuild designed to test modelling correctly from the outset.

## Statements to avoid during oral defence

Do not say:

- "ID-SEAD has been proven to work for agricultural-waste adsorbents."
- "The model predicts unseen systems with R²=0.847."
- "624 mg/g is the physical maximum adsorption capacity."
- "The Lipschitz constraint was proven to improve stability."
- "Table III gives experimentally validated adsorbent recommendations."
- "The system is ready for plant deployment/procurement."

Prefer:

- "The original row-wise workflow produced apparently strong performance; the current audit tests whether that evidence survives study-aware evaluation."
- "The algorithmic concept remains testable, but the current corpus does not pass the reliability gate required for inverse-design claims."
- "The revised contribution is methodological and engineering-reliability focused."

## Evidence artifacts to have available before presentation

- `conference_salvage/NUMERICAL_LINEAGE_AUDIT.md`
- `conference_salvage/CLAIM_RECONCILIATION_MATRIX.md`
- `conference_salvage/FORENSIC_RECONCILIATION.md`
- locked V2.1 provenance/source-of-truth outputs
- row-random vs grouped-study vs LOSO comparison output
- domain-audit output
- study-wise LOSO failure table
- inverse-design reliability-gate output

## Next dossier revision

V1 should attach exact figure/table numbers from the revised manuscript and repository paths for each answer, so every oral response can be traced to a frozen artifact in seconds.
