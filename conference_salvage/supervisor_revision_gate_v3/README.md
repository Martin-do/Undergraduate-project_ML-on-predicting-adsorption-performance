# ID-SEAD OAU V3 — Supervisor Revision Gate

This branch contains the targeted revisions requested after supervisor audit. It does not overwrite the frozen V2.1 baseline.

## Evidence hierarchy

1. **Primary:** leave-one-primary-study-out (LOSO) transfer.
2. **Secondary:** five-fold primary-study GroupKFold.
3. **Reference diagnostic only:** row-random cross-validation.

## Completed supervisor revisions

- quantified study association of engineered context categories;
- completed category-family-by-category-family ablation;
- reported study-by-study LOSO reliability and study-cluster uncertainty;
- documented fold-local preprocessing, encoding, imputation, hyperparameters and model feature dictionary;
- audited Ridge-stack behaviour under study-aware validation;
- verified provenance/comparability of the 2239 mg/g reconstructed observation;
- defined the evidence gate required before inverse-design claims can be enabled;
- distinguished whole-corpus study transfer from numerical/material/pollutant-domain extrapolation;
- completed the reference/claim and numerical manuscript audits.

## V3 scientific outcome

The targeted computational gate and submission-facing manuscript audit are **PASS / CLOSED**.

The main supervisor gate and the pollutant-representation forensic gate completed successfully in the pinned environment. The dominant V3 representation defect is the legacy derived `pollutant_class`, whose unbounded substring and abbreviation rules disagree with a target-blind exact-label/provenance classification in 122/273 strict rows (44.7%). Correcting only pollutant class while retaining pollutant context restores meaningful study-aware forward transfer (RF LOSO R2 0.5960; XGB 0.4645).

This does **not** re-enable inverse design. Study-cluster uncertainty remains wide, the intended strict agricultural-waste domain contains only 65 rows from four studies and remains strongly negative under LOSO, domain-restricted catastrophic failures persist, the Ridge stack is unstable under grouped validation, and applicability-distance diagnostics are not dependable safety gates.

## Frozen records

- complete V3 disposition: `conference_salvage/FINAL_SCIENTIFIC_DISPOSITION_V3.md`
- canonical V3 manuscript source: `conference_salvage/MANUSCRIPT_RECONSTRUCTION_V3.md`
- final reference/numerical/layout audit: `conference_salvage/supervisor_revision_gate_v3/FINAL_MANUSCRIPT_AUDIT_V3.md`
- final closure marker: `conference_salvage/FINAL_SCIENTIFIC_FREEZE_V3.md`

Submission-facing artifacts at the freeze are a four-page DOCX/PDF pair. All four rendered pages passed visual inspection, all 14 bibliography entries resolve to in-text citations, and key abstract/results/table/conclusion values were cross-checked against the frozen outputs.

## Interpretation guardrails

- Do not claim the whole dataset cannot generalize.
- Do not claim pollutant context is intrinsically harmful.
- Do not infer causal study-identity leakage from association alone.
- Do not present deletion of context as the final representation solution.
- Do not use model agreement as proof of correctness.
- Do not treat positive pooled LOSO as deployment or inverse-design validation.
- Do not generate a new optimisation recommendation table from the present evidence.

## Remaining work

Only operational/co-authorial submission actions remain unless a reviewer identifies a concrete new scientific defect: supervisor/co-author approval, official IEEM template/metadata check, similarity screening, IEEE PDF eXpress compliance, copyright/registration and final upload.
