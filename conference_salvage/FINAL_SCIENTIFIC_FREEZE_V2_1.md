# ID-SEAD Conference Salvage — Final Scientific Freeze V2.1

Status: **SCIENTIFICALLY CLOSED / DEFENSIBLE AS-IS**

Date: 2026-08-31
Branch: `conference/id-sead-salvage`

## Frozen research identity

Framework/project name: **ID-SEAD**

Conference paper title:

**ID-SEAD Revisited: Study-Aware Validation, Feature-Representation Sensitivity and Reliability Limits in Adsorption Inverse Design**

ID-SEAD remains the framework and engineering case study. What changed is the evidentiary claim: the conference paper no longer presents the legacy implementation as a validated deployment-ready inverse-design system.

## Frozen scientific position

1. The legacy ID-SEAD architecture exists and remains the historical engineering target of the re-evaluation.
2. The legacy headline performance/constraint/recommendation claims are not used as current validation evidence.
3. The corrected full-engineered representation shows strong row-random performance but poor unseen-primary-study transfer.
4. Reviewer-triggered post hoc sensitivity analysis shows that this extreme transfer loss is partly feature-representation dependent: removing engineered material/pollutant/context categories substantially improves grouped and LOSO forward prediction.
5. The recovered forward transfer survives n>=5-study and missingness sensitivities.
6. The current evidence still does **not** support validated inverse design or deployment because the strict agricultural-waste domain contains only 65 rows from four studies and fails LOSO, while a broader biogenic domain retains a catastrophic complete-study failure that is not reliably signalled by model agreement.
7. The legacy `Q_MAX=624 mg/g`, test-informed selection path, and conflicting inverse-design/Table-III lineage remain retired from current engineering claims.

## Independent-review closure

The final independent re-review verdict was:

**DEFENSIBLE AS-IS**

The reviewer independently executed `final_validation_v21.py` with the supplied source files and frozen reconstructed dataset and reproduced the manuscript’s headline pattern. They also verified Table-II equal-study metrics, the 69.6% RF representation-gap recovery calculation, the missingness-only negative control, and the row-level Alshabib failure evidence.

Scientific review is therefore closed unless a supervisor, conference reviewer, or new factual discrepancy requires reopening.

## Final submission-facing artifacts

Final manuscript DOCX SHA-256:
`5ed9d85f62b558ac1884859ac5068025d1d2b0a792106345745ce762a133b6d0`

Final manuscript PDF SHA-256:
`88fe2f93b69a28ad5a34a1c502367308ee604388e5c69fd7a94db445b05573d9`

Source-inclusive V2.1 technical evidence ZIP SHA-256:
`ba218b5581cf58739557a85167c9f4feb32f545e49da274ac70d72e0e9ebac18`

## Reproducibility lineage

Frozen corrected baseline workflow:
- run ID `33329803087`
- artifact ID `9737327504`

Post-review revision-gate workflow:
- run ID `33338908933`
- analysis commit `6e048d106a33f241c3a2161ae9f2827cf05f653b`
- artifact ID `9739944134`

Source-inclusive bundle workflow:
- run ID `33358745197`
- workflow commit `c6475c4cad9628a1bb94db6d4ffa2e90e8a4f1e9`
- artifact ID `9745979596`

No modelling/preprocessing/reviewer-gate `.py` files changed between the successful post-review analysis commit and the source-bundle commit.

## Data/code transparency note

The raw literature-extraction spreadsheets and provenance-reconstruction source mappings underlying Dataset V2.1 are maintained separately from the submission-facing validation and modelling package. The frozen reconstructed dataset, provenance audit, modelling code, validation outputs and reproducibility artifacts are version-controlled in the project repository.

## Stop rule

Do not add further post hoc modelling or optional ablations merely to strengthen the conference paper. Reopen the scientific analysis only if:

- a factual inconsistency is discovered;
- the supervisor or conference reviewer requests a specific analysis;
- dataset/provenance lineage changes;
- modelling or validation code changes;
- a submission claim is materially altered.

Paper 1 and Paper 2 remain separate research works and must not be weakened, merged, or repurposed to preserve the conference claim.
