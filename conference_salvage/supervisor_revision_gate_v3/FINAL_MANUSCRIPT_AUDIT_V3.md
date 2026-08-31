# ID-SEAD OAU TekCONF V3 — Final Manuscript Audit

**Audit status:** **PASS for scientific consistency, reference integrity, internal cross-reference, and OAU-template reconstruction.**  
**Target venue:** OAU TekCONF 2026, Faculty of Technology, Obafemi Awolowo University.  
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

## 2. Reference and citation forensic audit

Submission-facing V3 bibliography: **14 entries**.  
In-text references resolved: **14/14**.  
Listed references not cited: **0**.  
In-text citations without a listed entry: **0**.

The final manuscript uses the OAU Faculty of Technology **author-date** citation system and an alphabetically ordered reference list. Claim-fit checks were applied so that algorithm references support algorithms, review/perspective articles are not described as primary experiments, and ID-SEAD-specific numerical claims are grounded in the frozen dataset/code/output lineage rather than external citations.

Specific guardrails retained:
- Qiu et al. — field-level biochar/remediation background only.
- Zhang et al. — review of ML synthesis optimisation/adsorption modelling; not presented as one new experimental optimiser.
- Wei et al. — perspective/background article, not a primary adsorption experiment.
- Ge et al. — systematic review; published funding-statement correction recorded.
- Jaffari et al. — direct aqueous adsorption-capacity ML prediction/optimisation example.
- Yu et al. — Pb(II)/Cd(II) biochar adsorption ML optimisation example; wording remains narrower than equivalence to ID-SEAD inverse search.
- Rabbi — broader activated-biochar process optimisation and explicitly separated from direct aqueous-adsorption examples.
- Roberts et al. — structured/hierarchical validation principle, not proof of an ID-SEAD-specific leakage mechanism.
- Kapoor & Narayanan — general scientific-ML leakage/reproducibility warning, not numerical evidence for ID-SEAD.
- Varoquaux — general small-sample/CV uncertainty warning; ID-SEAD numerical intervals come from the V3 study-cluster bootstrap.
- Breiman and Chen & Guestrin — direct RF/XGBoost algorithm sources.
- Storn & Price — DE algorithm source; does not resolve the conflicted legacy ID-SEAD optimisation lineage.
- Li et al. — primary adsorption source for the high-capacity activated-carbon/methylene-blue lineage; DOI `10.1016/j.biortech.2020.124540`, reporting maximum adsorption capacity about 2251 mg/g.

## 3. Numerical consistency audit

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

### Pollutant-representation forensic result
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
- equal-study MAE/RMSE values in the final domain table match the frozen outputs — PASS.

### Alshabib restricted-domain failure
- observed 270.27 / 199.76 mg/g — PASS.
- broad-biogenic RF 1777.18 / 1755.03 mg/g — PASS.
- broad-biogenic XGB 1724.41 / 1724.41 mg/g — PASS.
- wording remains restricted to a domain-specific complete-study failure and is not generalized to every study — PASS.

### QMAX lineage
- reconstructed maximum 2239 mg/g traces to the Li et al. lineage and is strict-comparable — PASS.
- primary paper reports maximum adsorption about 2251 mg/g — PASS.
- manuscript disables, rather than substitutes another universal ceiling for, legacy `Q_MAX=624 mg/g` — PASS.

## 4. Mechanism/causality wording audit

The final V3 text does **not** claim that:
- the entire dataset cannot generalize;
- pollutant context is intrinsically harmful;
- study association proves causal identity leakage;
- deleting all material/pollutant categories is the final ID-SEAD solution;
- model agreement proves reliability;
- positive pooled LOSO validates deployment or inverse design.

Accepted mechanism:

> Study-aware validation exposed a defective derived pollutant representation. A target-blind exact-label repair restored meaningful average cross-study forward transfer while preserving pollutant context, but study-level uncertainty and domain-specific reliability failures still block inverse design.

## 5. Reliability/inverse-design disposition

The final text preserves all required barriers:
- study-aware transfer is primary;
- the intended agricultural domain contains only four studies and fails strongly;
- positive pooled R2 is qualified by wide study-cluster uncertainty;
- catastrophic restricted-domain complete-study error remains visible;
- Ridge stacking superiority is disabled;
- simple applicability-distance diagnostics are not presented as a validated safety gate;
- legacy constraint/optimiser lineage is not used to generate recommendations;
- no new optimisation table is produced.

**Inverse design remains BLOCKED.**

## 6. OAU TekCONF official-template document QA

Final submission-facing Word document:
- `ID-SEAD_OAUTekCONF2026_V3_Official_Template.docx`
- SHA-256 `30709a03c98209618812aec9ba2221ae48047769a9039f692ed2b09b98bf000e`

Proof PDF:
- `ID-SEAD_OAUTekCONF2026_V3_Official_Template.pdf`
- SHA-256 `d12740528cc32e2e1ca029963d9c3f89e96b03bff8bb834f572c98ad031006ec`

The document was rebuilt **inside the supervisor-supplied `paper_template.docx`**, rather than merely imitating its appearance.

Template compliance checks:
- single-column OAU Faculty of Technology template retained;
- native custom Word styles used for title, author names, affiliations, abstract, `1_maintext`, section/subsection numbering, figure caption, table captions and references;
- relevant custom-style XML definitions are semantically identical to the supplied template;
- no manual page breaks inserted;
- main headings use the native numbered section style and uppercase titles;
- second-level headings use the native subsection style;
- abstract = **237 words**, below the template's 250-word expectation;
- keywords = **6**, within the template range;
- one PNG figure inserted after first textual mention with caption below;
- two genuine Microsoft Word tables, each with caption above;
- SI units retained;
- references use OAU Faculty of Technology author-date form and alphabetical ordering;
- final length = **5 pages**, within the published OAU TekCONF maximum of 12 pages;
- all five DOCX-rendered pages visually inspected;
- the PDF was independently rendered and all five pages visually inspected;
- no clipping, overlapping objects, missing glyphs, broken table rows or orphaned split rows observed.

## 7. Final closure state

Targeted V3 computational revision: **CLOSED / PASS**.  
V3 scientific interpretation: **FROZEN**.  
Reference/citation completeness: **PASS (14/14)**.  
Claim-to-source forensic audit: **PASS for the current final text**.  
Numerical manuscript consistency: **PASS**.  
OAU official-template reconstruction: **PASS**.  
Rendered DOCX/PDF layout QA: **PASS**.  
Inverse-design/deployment recommendation claim: **DISABLED**.

No further post-hoc modelling is indicated at this stage. Remaining actions are supervisor/co-author review, confirmation of final author/affiliation/sub-theme/portal metadata, and OAU TekCONF submission.