# ID-SEAD OAU V3 — Supervisor Revision Gate

This branch reopens the conference scientific freeze only for the targeted revisions requested after supervisor audit. It does not overwrite the frozen V2.1 baseline.

## Evidence hierarchy

1. **Primary:** leave-one-primary-study-out (LOSO) transfer.
2. **Secondary:** five-fold primary-study GroupKFold.
3. **Reference diagnostic only:** row-random cross-validation.

## Required supervisor revisions

- quantify study association of engineered context categories;
- run category-family-by-category-family ablation;
- report study-by-study LOSO reliability and study-cluster uncertainty;
- fully document fold-local preprocessing, encoding, imputation, hyperparameters and feature dictionary;
- audit Ridge-stack behaviour under study-aware validation;
- verify the provenance/comparability of the 2239 mg/g reconstructed observation;
- define the evidence gate required before inverse-design claims can be enabled;
- distinguish study transfer from numerical/material/pollutant extrapolation;
- perform a complete reference/claim forensic audit before submission.

## Interpretation guardrails

- Representation sensitivity is established; a causal `identity proxy` mechanism is **not assumed** from study association alone.
- Post-hoc representation analyses remain explicitly exploratory/forensic.
- A representation that improves pooled LOSO is not automatically a validated inverse-design solution.
- Single-study catastrophic failures demonstrate that aggregate transfer metrics do not guarantee protection against domain-specific failure; they must not be generalized to the entire domain without evidence.
- No new optimisation recommendation table is to be generated unless a separate reliability analysis justifies it.

## V3 computational outcome

The targeted computational gate is **PASS / CLOSED**.

The main supervisor gate and the subsequent pollutant-representation forensic gate both completed successfully in the pinned environment. The V3 analysis identifies a more specific mechanism than the earlier category-removal sensitivity: the legacy derived `pollutant_class` contains substring-collision and abbreviation errors. A target-blind exact-label correction changes 122/273 strict rows and restores meaningful study-aware forward transfer while retaining pollutant context (RF LOSO R2 0.5960; XGB 0.4645).

This does **not** re-enable inverse design. Study-cluster uncertainty remains wide, the intended strict agricultural-waste domain contains only 65 rows from four studies and remains strongly negative under LOSO, domain-restricted catastrophic failures persist, the Ridge stack is unstable under grouped validation, and the current applicability-domain diagnostics do not provide a dependable safety gate.

The complete disposition and frozen V3 computational identifiers are recorded in `conference_salvage/FINAL_SCIENTIFIC_DISPOSITION_V3.md`.

## Remaining closure work

- rebuild the conference manuscript around the corrected pollutant-representation result;
- repeat the sentence-level reference/claim audit against the exact V3 manuscript;
- repeat the numerical consistency audit across abstract, results, tables, figures and conclusion;
- render and inspect the final conference-template DOCX/PDF;
- obtain co-author approval.

**Manuscript-level V3 freeze remains open until those editorial and consistency checks pass.**
