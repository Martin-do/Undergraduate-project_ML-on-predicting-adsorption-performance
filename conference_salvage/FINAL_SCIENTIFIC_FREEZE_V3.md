# ID-SEAD Conference Salvage — Final Scientific Freeze V3

**Final status:** **CLOSED / PASS for targeted V3 science and submission-facing manuscript consistency.**

This file supersedes the workflow-status wording in `FINAL_SCIENTIFIC_DISPOSITION_V3.md` that still described manuscript reconstruction as pending. It does not replace or modify the historical V2.1 freeze.

## Frozen scientific interpretation

Study-aware validation exposed a defective derived pollutant representation. The legacy `pollutant_class` used unbounded substring matching and disagreed with a target-blind exact-label/provenance classification in 122/273 strict rows (44.7%; 14/29 pollutant labels). Correcting only this derived class while retaining pollutant context restored meaningful average study-aware forward transfer:

- corrected-pollutant RF: row-random R2 0.8241; study-grouped 0.5912; LOSO 0.5960;
- corrected-pollutant XGB: row-random 0.8228; study-grouped 0.4846; LOSO 0.4645.

The mechanism is **representation repair**, not a claim that pollutant/material context should be removed and not proof of causal study-identity leakage.

## Reliability disposition

Inverse design remains **BLOCKED** because:

- primary-study cluster-bootstrap R2 intervals remain very wide (RF [-3.77, 0.824]; XGB [-3.39, 0.799]);
- the intended strict agricultural-waste domain contains only 65 observations from four studies and remains strongly negative under LOSO (RF -1.741; XGB -2.047);
- broader restricted domains retain catastrophic complete-study failures, including Alshabib predictions approximately 1.5 g/g above observed values despite close RF/XGB agreement;
- the Ridge stack is unstable under grouped validation (mean outer-fold R2 -39.84; minimum -103.29);
- available training-only applicability-distance diagnostics are explanatory, not validated safety gates;
- the legacy constraint/optimizer lineage is unsuitable for a reproducible recommendation table.

No V3 optimisation recommendation table is generated.

## Final computational evidence

Main supervisor gate:
- run `33403675876`
- head `53c1b2855c48c2b543e9a8a0f71f938d32526ea8`
- result `success`
- artifact `9762524495`
- digest `79e0efea856970dde6c8f9bb0cb6f75b78f9b260b17f61c49399cd6e33b69a2c`

Pollutant-representation forensic gate:
- run `33406030847`
- head `124499bf71b4f6d902fbedcaa3547a8895c35e1b`
- result `success`
- artifact `9763213724`
- digest `9179599248d676fc3ea583c775da55275f8c64e4bf02f6c478c86bb7a3abff7e`

## Final manuscript state

Canonical V3 source:
- `conference_salvage/MANUSCRIPT_RECONSTRUCTION_V3.md`

Final audit:
- `conference_salvage/supervisor_revision_gate_v3/FINAL_MANUSCRIPT_AUDIT_V3.md`

Submission-facing generated files at this freeze:
- `ID-SEAD_Conference_Reconstruction_V3.docx`
- SHA-256 `3fd457e794dea72673f4ef20cc238ec630ddc782ab0522080ac0324823847698`
- `ID-SEAD_Conference_Reconstruction_V3.pdf`
- SHA-256 `6dcbbb3b7040e005d22e67011d9289600dc98c86cf07275e1bb691778a4dd82e`
- rendered page count: 4
- visual render QA: PASS on all four pages
- bibliography: 14/14 cited/listed match
- numerical abstract/results/tables/conclusion cross-check: PASS

## What remains outside the scientific freeze

Only operational/co-authorial submission work should follow unless a supervisor/reviewer identifies a concrete new scientific error:

1. supervisor/co-author approval;
2. confirm the final paper metadata in EMSY matches title/authors/affiliations/abstract;
3. confirm exact official IEEM template equivalence;
4. run similarity screening and keep the score below the conference threshold;
5. run the final PDF through IEEE PDF eXpress and use the compliant output;
6. complete copyright/registration/final upload requirements.

Further post hoc modelling is stopped unless specifically requested by a reviewer or needed to correct a real defect.
