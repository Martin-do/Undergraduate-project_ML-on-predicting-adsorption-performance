# ID-SEAD OAU V3 — Final Manuscript Audit

**Audit status:** **PASS for scientific consistency and internal cross-reference.**  
**Scope:** V3 submission-facing manuscript generated from `MANUSCRIPT_RECONSTRUCTION_V3.md` after the targeted supervisor computational revision.  
**Inverse-design status:** **BLOCKED**; no optimisation recommendation table is restored.

## 1. Frozen evidence used

### Main supervisor gate
- run `33403675876`
- head `53c1b2855c48c2b543e9a8a0f71f938d32526ea8`
- conclusion `success`
- artifact `9762524495`
- artifact SHA-256 `79e0efea856970dde6c8f9bb0cb6f75b78f9b260b17f61c49399cd6e33b69a2c`

### Pollutant-representation forensic gate
- run `33406030847`
- head `124499bf71b4f6d902fbedcaa3547a8895c35e1b`
- conclusion `success`
- artifact `9763213724`
- artifact SHA-256 `9179599248d676fc3ea583c775da55275f8c64e4bf02f6c478c86bb7a3abff7e`

The frozen V2.1 baseline is retained separately and is not overwritten.

## 2. Cited ↔ listed reference audit

Submission-facing V3 bibliography: **14 entries**.  
In-text references resolved: **14/14**.  
Listed references not cited: **0**.  
In-text numeric references without a listed entry: **0**.

Claim-fit disposition:

- [1] Qiu et al. — field-level contaminant-removal/biochar background: appropriate.
- [2] Zhang et al. — review of ML synthesis optimisation/adsorption modelling: appropriate as field background, not described as one new experimental optimiser.
- [3] Wei et al. — perspective/background on ML and biochar: retained with article-type guardrail.
- [4] Ge et al. — systematic review of ML-aided engineered biochar: retained; published funding-statement correction recorded.
- [5] Jaffari et al. — direct aqueous adsorption-capacity ML prediction/optimisation example: appropriate.
- [6] Yu et al. — Pb(II)/Cd(II) biochar adsorption ML optimisation example: wording kept narrower than an equivalence claim to ID-SEAD inverse search.
- [7] Rabbi — broader activated-biochar process optimisation using ML/evolutionary algorithms: explicitly separated from direct aqueous-adsorption examples.
- [8] Roberts et al. — hierarchical/structured cross-validation principle: appropriate; not used as proof of an ID-SEAD-specific leakage mechanism.
- [9] Kapoor & Narayanan — general scientific-ML leakage/reproducibility warning: appropriate; not used as numerical evidence for ID-SEAD.
- [10] Varoquaux — small-sample/CV uncertainty background: appropriate; ID-SEAD numerical intervals come from the V3 study-cluster bootstrap.
- [11] Breiman — RF algorithm source: appropriate.
- [12] Chen & Guestrin — XGBoost algorithm source: appropriate.
- [13] Storn & Price — DE algorithm source: appropriate; does not resolve the conflicted legacy ID-SEAD optimisation lineage.
- [14] Li et al. — primary adsorption source for the high-capacity activated-carbon/methylene-blue lineage: appropriate. DOI `10.1016/j.biortech.2020.124540`; the paper reports maximum adsorption capacity about 2251 mg/g.

## 3. Numerical consistency audit

The following submission-facing statements were checked against the frozen V3 outputs and historical V2.1 baseline.

### Population/provenance
- 322 usable-target observations — PASS.
- 307 primary-confirmed observations / 29 studies — PASS.
- 273 strict comparable observations / 24 studies — PASS.
- strict agricultural 65/4; broad biogenic 92/6; waste-derived carbon 138/7 — PASS.
- five largest studies 196/273 = 71.8%; 8 singletons; median study size 5; Kish effective studies 7.62 — PASS.

### Legacy-compatible representation
- RF row-random/grouped/LOSO R2 = 0.9042 / 0.0265 / 0.0085 — PASS.
- XGB = 0.8936 / 0.1929 / 0.1624 — PASS.
- grouped fold ranges RF -20.59 to 0.46; XGB -13.54 to 0.44 — PASS.
- Ridge mean grouped outer-fold R2 -39.84; minimum -103.29 — PASS.

### Pollutant representation forensic result
- 122/273 row disagreements = 44.7% — PASS.
- 14/29 unique pollutant labels affected — PASS.
- remove-pollutant grouped/LOSO R2: RF 0.5861/0.5802; XGB 0.4818/0.4625 — PASS.
- corrected-pollutant row-random/grouped/LOSO R2: RF 0.8241/0.5912/0.5960; XGB 0.8228/0.4846/0.4645 — PASS.
- remove-all-four grouped/LOSO: RF 0.6370/0.6278; XGB 0.4807/0.4574 — PASS.

### Corrected-pollutant study uncertainty
- RF pooled LOSO R2 0.5960, RMSE 447.1, MAE 326.0 mg/g — PASS.
- XGB pooled LOSO R2 0.4645, RMSE 514.7, MAE 352.1 mg/g — PASS.
- study-cluster 95% R2 intervals RF [-3.77, 0.824], XGB [-3.39, 0.799] — PASS.
- median study MAE RF 97.1 mg/g, XGB 86.4 mg/g — PASS.

### Corrected-pollutant domains
- strict agricultural RF/XGB R2 -1.741 / -2.047 — PASS.
- broad biogenic RF/XGB 0.311 / 0.642 — PASS.
- waste-derived carbon RF/XGB 0.545 / 0.520 — PASS.
- all equal-study MAE/RMSE values in Table II match the frozen domain output — PASS.

### Alshabib restricted-domain failure
- observed 270.27 / 199.76 mg/g — PASS.
- broad-biogenic RF 1777.18 / 1755.03 mg/g — PASS.
- broad-biogenic XGB 1724.41 / 1724.41 mg/g — PASS.
- wording is restricted to domain-specific failure; manuscript does not generalize this single study to all studies — PASS.

### QMAX lineage
- reconstructed maximum 2239 mg/g traces to the Li et al. family and is strict-comparable — PASS.
- primary paper reports maximum adsorption about 2251 mg/g — PASS.
- manuscript disables, rather than replaces with another universal ceiling, the legacy `Q_MAX=624 mg/g` rule — PASS.

## 4. Mechanism/causality wording audit

The final V3 text does **not** claim that:

- the entire dataset cannot generalize;
- pollutant context is intrinsically harmful;
- study association proves causal identity leakage;
- deleting all material/pollutant categories is the final ID-SEAD solution;
- model agreement proves reliability;
- positive pooled LOSO validates deployment or inverse design.

The accepted mechanism is narrower:

> Study-aware validation exposed a defective derived pollutant representation. A target-blind exact-label repair restored meaningful average cross-study forward transfer while preserving pollutant context, but study-level uncertainty and domain-specific reliability failures still block inverse design.

## 5. Reliability/inverse-design disposition

The final text preserves all required barriers:

- study-aware transfer is primary;
- the four-study intended agricultural domain fails strongly;
- pooled positive R2 is qualified by wide study-cluster uncertainty;
- catastrophic restricted-domain complete-study error remains visible;
- Ridge stacking superiority is disabled;
- simple applicability-distance diagnostics are not presented as a validated safety gate;
- legacy constraint/optimiser lineage is not used to generate recommendations;
- no new optimisation table is produced.

**Inverse design remains BLOCKED.**

## 6. Submission-facing document QA

Generated V3 document:
- `ID-SEAD_Conference_Reconstruction_V3.docx`
- SHA-256 `3fd457e794dea72673f4ef20cc238ec630ddc782ab0522080ac0324823847698`

Generated PDF:
- `ID-SEAD_Conference_Reconstruction_V3.pdf`
- SHA-256 `6dcbbb3b7040e005d22e67011d9289600dc98c86cf07275e1bb691778a4dd82e`

Layout:
- A4;
- 0.75-inch margins inherited from the supplied conference-style manuscript;
- 4 pages, below the five-page conference maximum previously recorded;
- all four rendered pages visually inspected;
- no clipping, table overflow, overlapping objects or missing-glyph defects observed;
- title/authors/affiliations retained from the supplied manuscript lineage;
- Figure 1 updated to the V3 pollutant-repair result;
- Tables I-II updated to V3 values.

## 7. Closure state

Targeted V3 computational revision: **CLOSED / PASS**.  
V3 scientific interpretation: **FROZEN**.  
Reference/citation completeness: **PASS**.  
Numerical manuscript consistency: **PASS**.  
Rendered DOCX/PDF layout QA: **PASS**.  
Inverse-design/deployment recommendation claim: **DISABLED**.

Remaining actions are operational/co-authorial rather than new post hoc modelling: supervisor/co-author review, official portal metadata/template compliance, similarity check and IEEE PDF eXpress where required.
