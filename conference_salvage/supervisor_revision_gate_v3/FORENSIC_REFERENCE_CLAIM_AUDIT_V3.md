# ID-SEAD OAU V3 — Forensic Reference and Claim Audit

Status: **working audit for V3 reconstruction**. This file audits the current corrected manuscript before it is rebuilt in the official OAU template. It must be rerun against the final V3 text because citations and wording may change.

## Audit rules

1. Every bibliography item must appear in the text and every in-text citation must resolve to a bibliography item.
2. DOI/title/authors/year/journal/article metadata must be independently resolvable.
3. A real paper is not automatically a valid citation: the source must support the precise sentence in which it appears.
4. Reviews/perspectives must not be described as though they performed experiments they merely summarize.
5. Corrections, errata, expressions of concern and retractions are recorded explicitly.
6. Claims about the present ID-SEAD data/code must be substantiated from the frozen dataset/code/output lineage, not from external citations.
7. Any unsupported or over-broad wording is narrowed or removed rather than defended rhetorically.

## Cross-reference completeness — current pre-V3 manuscript

- Bibliography entries: **13**.
- Bibliography entries observed as cited in the current manuscript: **13/13**.
- In-text cited author/year groups observed without a corresponding bibliography entry: **none identified in the current manuscript extraction**.
- This is a pre-V3 check only; repeat after final OAU-template reconstruction.

## Reference-by-reference audit

| Ref | Bibliographic identity | Metadata status | Current manuscript use | Claim-fit audit | Disposition |
|---|---|---|---|---|---|
| Breiman (2001) | *Random Forests*, Machine Learning 45, 5–32. DOI 10.1023/A:1010933404324 | VERIFIED | Supports RF as a nonlinear tree-ensemble baseline | Direct algorithm source; appropriate | KEEP |
| Chen & Guestrin (2016) | *XGBoost: A Scalable Tree Boosting System*, KDD 2016, 785–794. DOI 10.1145/2939672.2939785 | VERIFIED | Supports XGBoost algorithm description | Direct algorithm source; appropriate | KEEP |
| Ge et al. (2025) | *A systematic review on machine learning-aided design of engineered biochar for soil and water contaminant removal*, Frontiers in Soil Science 5:1623083. DOI 10.3389/fsoil.2025.1623083 | VERIFIED; CORRECTION APPLIED | Supports recent ML-aided engineered-biochar design/remediation context | Scientific scope fits. Published correction concerns the funding statement, not the scientific results. Record correction DOI 10.3389/fsoil.2025.1659154 | KEEP WITH CORRECTION RECORDED |
| Jaffari et al. (2023) | *Machine-learning-based prediction and optimization of emerging contaminants' adsorption capacity on biochar materials*, Chemical Engineering Journal 466:143073. DOI 10.1016/j.cej.2023.143073 | VERIFIED | Supports adsorption-capacity ML prediction/optimization on biochar | Directly aligned with aqueous contaminant adsorption and optimisation | KEEP |
| Kapoor & Narayanan (2023) | *Leakage and the reproducibility crisis in machine-learning-based science*, Patterns 4(9):100804. DOI 10.1016/j.patter.2023.100804 | VERIFIED | Supports leakage/reproducibility warning in scientific ML | Appropriate for the general leakage/reproducibility statement; do not use as evidence of a specific ID-SEAD leakage mechanism | KEEP WITH SCOPE GUARDRAIL |
| Qiu et al. (2022) | *Biochar for the removal of contaminants from soil and water: a review*, Biochar 4:19. DOI 10.1007/s42773-022-00146-1 | VERIFIED | Supports biochar contaminant-removal context and the importance of feedstock/pore/surface properties | Review directly supports these background statements | KEEP |
| Rabbi (2026) | *Computational framework for multi-objective optimization of activated biochar properties using machine learning and evolutionary algorithms*, Scientific Reports 16:22466. DOI 10.1038/s41598-026-50569-0 | VERIFIED | Current manuscript groups it with emerging prescriptive/optimisation applications | Real ML-surrogate + differential-evolution optimisation work, but its objectives are mainly activated-biochar process design for CO2 adsorption/carbon stability/electrochemical properties, not aqueous contaminant adsorption. Current wording must not imply that it is direct wastewater-adsorption inverse design | KEEP, BUT QUALIFY/SEPARATE FROM AQUEOUS ADSORPTION EXAMPLES |
| Roberts et al. (2017) | *Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure*, Ecography 40:913–929. DOI 10.1111/ecog.02881 | VERIFIED | Supports study/hierarchy-aware partitioning rather than naive random CV | Directly supports the principle that ignoring hierarchical dependence can seriously underestimate predictive error | KEEP |
| Storn & Price (1997) | *Differential Evolution – A Simple and Efficient Heuristic for Global Optimization over Continuous Spaces*, Journal of Global Optimization 11:341–359. DOI 10.1023/A:1008202821328 | VERIFIED | Supports DE as a population-based global optimisation method | Direct algorithm source; appropriate. Does not prove that the legacy ID-SEAD Table III was generated by DE | KEEP WITH LINEAGE GUARDRAIL |
| Varoquaux (2018) | *Cross-validation failure: Small sample sizes lead to large error bars*, NeuroImage 180:68–77. DOI 10.1016/j.neuroimage.2017.06.061 | VERIFIED | Supports uncertainty/instability concerns with small effective samples | Directly supports the general warning. It does not supply the ID-SEAD study-cluster CI; that comes from the V3 bootstrap | KEEP |
| Wei et al. (2024) | *Machine learning insights in predicting heavy metals interaction with biochar*, Biochar 6:10. DOI 10.1007/s42773-024-00304-7 | VERIFIED | Supports recent ML/biochar prediction context and importance of data quality/representation | Perspective article, not a new adsorption experiment; current background use is appropriate if phrased as literature perspective | KEEP WITH ARTICLE-TYPE GUARDRAIL |
| Yu et al. (2026) | *Machine Learning-Driven Optimization for Predicting Biochar Adsorption Performance Toward Pb(II) and Cd(II)*, Water 18(12):1416. DOI 10.3390/w18121416 | VERIFIED | Current manuscript cites it as an emerging ML optimisation application in Pb/Cd adsorption | Directly about Pb/Cd biochar adsorption, descriptor-based ML, Optuna model optimisation and uncertainty quantification. Avoid implying that it demonstrates the same inverse-design search problem as ID-SEAD unless the exact optimisation claim is sourced from the full text | KEEP, NARROW WORDING |
| Zhang et al. (2023) | *Synthesis optimization and adsorption modeling of biochar for pollutant removal via machine learning*, Biochar 5:25. DOI 10.1007/s42773-023-00225-x | VERIFIED | Supports ML in biochar synthesis optimisation and adsorption modelling | Review article; strong fit for field-level background, not direct evidence of one experimental optimiser | KEEP WITH ARTICLE-TYPE GUARDRAIL |

## Current sentence-level claim corrections required

### 1. Prior optimisation literature
Current wording groups Jaffari, Yu and Rabbi too tightly as though all three address the same aqueous adsorption optimisation task.

**V3 rule:** separate direct aqueous adsorption examples (Jaffari; Yu) from broader activated-biochar process optimisation (Rabbi). Do not claim first ML inverse design/first adsorption optimisation.

### 2. Hierarchical validation
Roberts et al. supports the general need to respect hierarchical dependence. It does **not** prove that every ID-SEAD context category is leakage. The ID-SEAD-specific mechanism must come from the V3 ablation/association/permutation evidence.

### 3. Representation mechanism
External leakage literature may motivate scrutiny, but the V3 manuscript must say the data establish **representation sensitivity / study-correlated predictive behaviour / negative transfer associated especially with pollutant-class encoding**, not causal identity leakage unless directly demonstrated.

### 4. Small-study uncertainty
Varoquaux supports the general warning that CV uncertainty can be large with small samples. The numerical uncertainty reported for ID-SEAD must be attributed to the V3 study-cluster bootstrap and per-study LOSO outputs, not to Varoquaux.

### 5. Algorithm sources versus legacy lineage
Storn & Price validates DE as an algorithm. It cannot resolve whether the legacy ID-SEAD recommendation table was generated by DE. That is a repository-lineage question and remains unresolved/conflicted.

## Forensic data/claim checkpoints already substantiated

- Strict matched validation population: 273 observations / 24 primary studies — checked in the V3 executable gate.
- V3 individual family ablation identifies pollutant-class removal as the dominant single-family improvement; this is exploratory/post-hoc and must remain labelled as such.
- Study association of a feature is not equivalent to harmfulness: base-material categories are highly study-associated but their removal does not materially improve transfer.
- Study-cluster bootstrap intervals are extremely wide; pooled LOSO R2 must not be described as stable general-purpose generalisation.
- The 2239 mg/g reconstructed observation traces to Li et al. (2021), Bioresource Technology 322:124540, DOI 10.1016/j.biortech.2020.124540. The primary paper reports adsorption capacity approaching/up to about 2251 mg/g. This independently defeats a universal QMAX=624 ceiling, subject to the manuscript clearly describing the comparison as adsorption-capacity evidence rather than a universal material law.
- The Alshabib failure demonstrates that aggregate LOSO/model agreement does not guarantee protection against severe single-study failure. It must not be generalized into a claim that every study in the broader biogenic domain is unreliable.

## Final-gate actions still required

- Re-run cited↔listed completeness after the V3 manuscript is rebuilt.
- Verify every newly added citation and every changed claim against the exact source passage.
- Record any correction/erratum/retraction status as of the final audit date.
- Run a final numerical cross-check: Abstract ↔ Results ↔ tables ↔ figures ↔ conclusion ↔ frozen CSV outputs.
- Run a final data-lineage check for every manuscript number that is not a literature citation.
- Do not mark this forensic audit CLOSED until the final OAU-template DOCX has passed those checks.
