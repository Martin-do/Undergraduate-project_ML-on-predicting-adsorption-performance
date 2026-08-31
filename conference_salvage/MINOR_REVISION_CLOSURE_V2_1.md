# ID-SEAD Conference Salvage — Minor Revision Closure V2.1

Status: **scientifically defensible / independent re-review = minor revisions / required minor items closed**

Date: 2026-08-31

## Independent re-review disposition

The corrected V2 technical evidence was independently checked at pooled, per-study and row-prediction level. The re-review upgraded the work from **Defensible with major revisions** to **Defensible with minor revisions** and identified four submission-facing items plus one optional analysis.

## Required items closed

### 1. Literal source files attached

A dedicated GitHub Actions source-bundle workflow now packages the actual modelling/rebuild/post-review `.py` files rather than only pointing to a commit.

Source-bundle workflow run: `33358745197`

Source-bundle commit: `c6475c4cad9628a1bb94db6d4ffa2e90e8a4f1e9`

Artifact: `id-sead-v2-source-bundle`

Artifact ID: `9745979596`

Artifact SHA-256: `19aedb61cfcd252e703acd0b8eb597aeb1b5e6abde5f476d34a3763e4cfd208d`

The bundle includes at minimum:

- `validation_v2/final_validation_v21.py`
- `validation_v2/robustness_validation_v21.py`
- `validation_v2/build_dataset_v21.py`
- `validation_v2/study_aware_validation.py`
- `validation_v2/feature_parity_validation.py`
- `validation_v2/feature_parity_validation_fixed.py`
- `validation_v2/external_validation_v2.py`
- `conference_salvage/reviewer_revision_gate_v2/run_reviewer_revision_gate_v2.py`
- `conference_salvage/reviewer_revision_gate_v2/run_identity_loso_followup.py`
- `conference_salvage/reviewer_revision_gate_v2/run_crossed_missingness_sensitivity.py`

### 2. Equal-study-weighted error added to Table II

The V2.1 manuscript reports equal-study mean MAE/RMSE alongside pooled LOSO R2 for the No-ID domain analyses:

- strict agricultural RF: 780.8 / 818.2 mg/g
- strict agricultural XGB: 767.5 / 801.6 mg/g
- broad biogenic RF: 515.2 / 558.9 mg/g
- broad biogenic XGB: 481.6 / 523.8 mg/g
- waste-derived carbon RF: 443.5 / 486.2 mg/g
- waste-derived carbon XGB: 486.1 / 525.6 mg/g

### 3. Representation recovery quantified

For RF, removing identity-adjacent categories raises grouped R2 from 0.0265 to 0.6370. Relative to the full-representation row-random-to-grouped gap, this recovers **69.6%** of that gap.

### 4. Missingness-only negative control disclosed

Removing dose and contact time from the **full identity-bearing representation** raises grouped RF R2 only from 0.0265 to 0.0806; XGB changes from 0.1929 to 0.1909. Thus missingness alone does not explain the original full-representation transfer failure. The much larger recovery occurs only after identity-adjacent categories are removed.

## Deliberately not added

A per-category identity ablation was labelled by the independent reviewer as **nice-to-have**, not a required submission fix. It is not added at this stage to avoid indefinite post hoc analysis once the core mechanism, robustness and missingness sensitivities are already established. It may be run later if specifically requested by the supervisor or conference reviewers.

## Frozen interpretation

- The full-engineered study-aware collapse remains a reproducible baseline result.
- The extreme collapse is partly feature-representation dependent.
- Category stripping recovers meaningful forward transfer.
- This does **not** validate inverse design.
- The strict agricultural-waste domain remains only 65 rows / 4 studies and fails LOSO.
- A broader biogenic domain retains a catastrophic complete-study failure despite close RF-XGB agreement.
- Legacy R2=0.847, QMAX=624, Table III and deployment-readiness claims remain disabled.

No modelling code or dataset values were changed to close these minor revisions; this closure updates reporting, packaging and interpretation only.
