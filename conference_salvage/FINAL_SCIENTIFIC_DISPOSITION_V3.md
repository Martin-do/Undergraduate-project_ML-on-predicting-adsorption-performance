# ID-SEAD Conference Salvage — Final Scientific Disposition V3

**Status:** targeted supervisor computational revision **PASS**; V3 manuscript reconstruction and final editorial audit remain open.  
**Branch:** `conference/id-sead-oau-v3-supervisor-revision`  
**Purpose:** record the post-supervisor V3 scientific state without overwriting the frozen V2.1 record.

## 1. Evidence hierarchy

1. Primary: leave-one-primary-study-out (LOSO) transfer.
2. Secondary: five-fold primary-study GroupKFold.
3. Diagnostic only: shuffled row-random cross-validation.

The frozen V2.1 numerical record remains historical and reproducible. V3 changes the interpretation of the representation mechanism because a more specific, target-blind pollutant-encoding defect was identified and tested.

## 2. Frozen corpus and guardrails

- Reconstructed corpus: 322 usable-target observations.
- Primary-confirmed: 307 observations / 29 studies.
- Strict comparable: 273 observations / 24 primary studies.
- `removal_percent` is excluded from predictors.
- Source/study identifiers are excluded from predictors.
- The legacy `Q_MAX = 624 mg/g` rule is disabled.
- Preprocessing is fitted within training folds only.
- No external target is used for tuning.
- No V3 inverse-design recommendation table is permitted unless a separate reliability gate passes.

## 3. V2.1 baseline retained, not overwritten

On the identical strict 273-row / 24-study population, the legacy-compatible full engineered representation produced:

| Model | Row-random R2 | Study-grouped R2 | LOSO R2 |
|---|---:|---:|---:|
| RF | 0.9042 | 0.0265 | 0.0085 |
| XGB | 0.8936 | 0.1929 | 0.1624 |

Earlier V2.1 post-hoc category stripping recovered meaningful forward transfer (RF LOSO 0.6278; XGB 0.4574), establishing representation sensitivity. V3 determines the dominant representation defect more specifically.

## 4. Study association is real but is not equivalent to harmfulness

All four engineered context families are strongly associated with primary study:

| Family | NMI with study | Cramer's V | Row-weighted within-study modal share |
|---|---:|---:|---:|
| activation_agent | 0.1861 | 0.9201 | 0.9927 |
| base_material | 0.4145 | 0.9586 | 0.9963 |
| material_class | 0.3414 | 0.8305 | 0.9927 |
| pollutant_class | 0.4246 | 0.7727 | 0.8498 |

Among the 12 studies with at least five rows (253 observations), the four context families predict study identity with logistic-regression accuracy 0.6482 versus a 0.2648 majority-class reference and 0.0833 balanced-chance reference; permutation p = 0.0196 for accuracy, balanced accuracy and macro-F1.

This does **not** establish causal identity leakage. Individual-family ablation shows why association alone cannot be equated with negative transfer: removal of highly study-associated base-material or material-class families barely changes LOSO performance, whereas pollutant-class removal changes it substantially.

## 5. Pollutant-class representation is the dominant V3 defect

The reconstructed legacy feature engineering used unbounded substring matching for pollutant classes. Tokens such as `as` and `cr` can match unrelated text, while several abbreviated dye labels are not recognized by the dye regex. Examples include:

- `Basic Violet 10`: `as` occurs inside `Basic`;
- `Congo Red (CR)`: `cr` is interpreted by the heavy-metal pattern;
- `Oil & Grease`: `as` occurs inside `Grease`.

A target-blind exact-label mapping was therefore reconstructed from pollutant identity and recovered primary-study provenance before model fitting. No `qe` target or validation score was used to assign the corrected class.

Integrity audit on the strict population:

- 29 unique pollutant labels;
- 122/273 rows (44.69%) disagree between the legacy derived class and the curated exact-label class;
- 14/29 unique labels are affected;
- legacy derived counts: 141 organic_dye, 87 other_organic, 45 heavy_metal;
- corrected counts: 254 dye, 10 metal_ion, 9 bulk_organic.

## 6. Correcting pollutant representation restores meaningful average cross-study transfer

Only the derived `pollutant_class` representation was corrected; pollutant context was retained and all other modelling settings were preserved.

| Model | Scheme | R2 | RMSE (mg/g) | MAE (mg/g) |
|---|---|---:|---:|---:|
| RF | row-random | 0.8241 | 295.03 | 166.61 |
| XGB | row-random | 0.8228 | 296.07 | 174.90 |
| RF | study-grouped | 0.5912 | 449.72 | 328.00 |
| XGB | study-grouped | 0.4846 | 504.93 | 346.41 |
| RF | LOSO | **0.5960** | 447.08 | 326.03 |
| XGB | LOSO | **0.4645** | 514.69 | 352.12 |

For comparison, removing pollutant class entirely gives LOSO R2 0.5802 (RF) and 0.4625 (XGB), while removing all four context families gives 0.6278 and 0.4574. Thus pollutant context is not shown to be intrinsically harmful: **the dominant defect is the legacy pollutant encoding, and a target-blind repair recovers most or all of the transfer gain while retaining pollutant information.**

## 7. Study-level uncertainty remains large

Study-cluster bootstrap uncertainty for the corrected pollutant representation is wide:

| Model | Pooled LOSO R2 | 95% study-cluster R2 interval | Median study MAE (mg/g) | Mean study MAE (mg/g) |
|---|---:|---:|---:|---:|
| RF | 0.5960 | [-3.7727, 0.8238] | 97.10 | 176.65 |
| XGB | 0.4645 | [-3.3860, 0.7988] | 86.45 | 180.08 |

The pooled R2 therefore demonstrates meaningful average transfer on this reconstructed population, not stable universal generalisation across literature studies.

## 8. Domain-restricted results still block the original inverse-design claim

Using the corrected pollutant representation:

| Domain | Rows / studies | RF LOSO R2 | XGB LOSO R2 | Equal-study RF MAE/RMSE | Equal-study XGB MAE/RMSE |
|---|---:|---:|---:|---:|---:|
| Strict agricultural waste | 65 / 4 | **-1.7407** | **-2.0465** | 780.8 / 818.2 | 767.5 / 801.6 |
| Broad biogenic waste | 92 / 6 | 0.3106 | **0.6422** | 533.3 / 575.4 | 481.6 / 523.8 |
| Waste-derived carbon | 138 / 7 | 0.5449 | 0.5197 | 448.1 / 489.6 | 486.1 / 525.6 |

The intended strict agricultural-waste domain remains too shallow and fails strongly. Positive pooled R2 in broader domains is diagnostic, not deployment evidence.

## 9. Catastrophic domain-specific failure survives the repair

The corrected full-corpus model can predict the Alshabib observations substantially better when trained on the broad 273-row population, but that does not resolve the intended deployment question. Under domain-restricted LOSO, the same held-out study remains catastrophically wrong:

- observed `qe`: 270.27 and 199.76 mg/g;
- broad-biogenic RF: 1777.18 and 1755.03 mg/g;
- broad-biogenic XGB: 1724.41 and 1724.41 mg/g;
- waste-derived-carbon RF: 1795.89 and 1773.50 mg/g;
- waste-derived-carbon XGB: 1755.91 and 1755.91 mg/g.

Thus global study-aware improvement does not guarantee reliability inside a narrower scientific deployment domain, and close agreement between models is not evidence of correctness.

## 10. Ridge stacking and simple applicability-domain gates remain disabled

The Ridge stack is unstable under study-aware validation. In the V3 audit, mean outer-fold R2 under primary-study GroupKFold is -39.84 (minimum -103.29), with highly unstable meta-weights. The legacy stacking-superiority claim is therefore withdrawn.

The corrected training-only distance/applicability-domain analyses remain explanatory diagnostics only. Support status does not reliably separate low-error from catastrophic held-out studies and can worsen predictive error after filtering. It is not an engineering safety gate.

## 11. Legacy forensic disposition remains unchanged

The following historical claims remain disabled:

- submitted headline R2/RMSE/CI as current validated performance evidence;
- random-row performance as evidence of unseen-study transfer;
- universal `Q_MAX = 624 mg/g`;
- stacking superiority;
- legacy constraint-violation and sensitivity numbers where lineage is unreconciled;
- Table-III optimizer/target lineage as a reproducible engineering recommendation table;
- deployment readiness and inverse-design recommendations.

The 2239 mg/g reconstructed maximum is traceable to Li et al. (2021), *Bioresource Technology* 322:124540, DOI 10.1016/j.biortech.2020.124540; the primary-study evidence reports adsorption capacity approaching approximately 2251 mg/g, independently defeating the legacy universal 624 mg/g ceiling.

## 12. V3 scientific conclusion

**Study-aware validation exposed a defective pollutant representation. A target-blind exact-label repair restored meaningful average cross-study forward transfer while preserving pollutant context, but study-level uncertainty, a four-study intended agricultural domain, domain-restricted catastrophic failures, unstable stacking and inadequate reliability detection still block inverse design.**

A future ID-SEAD can only re-enable prescriptive claims after demonstrating adequate independent-study depth in the exact material-pollutant domain, scientifically valid context descriptors, study-aware/nested model development, justified feasibility constraints, a target-consistent optimisation objective, reliable failure/applicability detection, machine-readable optimisation lineage, and external or experimental confirmation.

## 13. Frozen V3 computational evidence

### Main supervisor revision gate
- workflow: `ID-SEAD OAU V3 supervisor revision gate`
- run: `33403675876`
- head: `53c1b2855c48c2b543e9a8a0f71f938d32526ea8`
- conclusion: success
- artifact: `9762524495`
- artifact SHA-256: `79e0efea856970dde6c8f9bb0cb6f75b78f9b260b17f61c49399cd6e33b69a2c`

### Pollutant-representation forensic gate
- workflow: `ID-SEAD OAU V3 pollutant representation forensic`
- run: `33406030847`
- head: `124499bf71b4f6d902fbedcaa3547a8895c35e1b`
- conclusion: success
- artifact: `9763213724`
- artifact SHA-256: `9179599248d676fc3ea583c775da55275f8c64e4bf02f6c478c86bb7a3abff7e`

## 14. Remaining closure actions

Computational targeted revision: **CLOSED / PASS**.  
Scientific interpretation for V3 manuscript: **FROZEN at this checkpoint**.  
Still required before submission: rebuild the V3 manuscript, run final sentence-level reference/claim and numerical consistency audits, render/inspect the official-template DOCX/PDF, and obtain co-author approval.
