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

- Representation sensitivity is established by the existing ablation; a causal `identity proxy` mechanism is **not assumed** and must be tested.
- Post-hoc representation analyses remain explicitly exploratory.
- A representation that improves pooled LOSO is not automatically a validated inverse-design solution.
- Single-study catastrophic failures demonstrate that aggregate transfer metrics do not guarantee protection against domain-specific failure; they must not be generalized to the entire domain without evidence.
- No new optimisation recommendation table is to be generated unless a separate reliability analysis justifies it.

## Status

Scientific freeze: **reopened for targeted V3 revision**.

Local exploratory checks are not to be cited as frozen manuscript values until reproduced in the pinned repository workflow.
