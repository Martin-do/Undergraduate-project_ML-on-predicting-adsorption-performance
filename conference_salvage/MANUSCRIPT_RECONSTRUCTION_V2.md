# ID-SEAD Revisited: Study-Aware Validation, Feature-Representation Sensitivity and Reliability Limits in Adsorption Inverse Design

**Working conference-manuscript reconstruction — V2**  
**Status:** post-independent-review evidence-aligned draft; final template formatting and author statements pending.  
**Authors:** M. Jaiyeola; Oladeji O. Ige; Oludolapo A. Olanrewaju

## Abstract

Machine-learning surrogates can accelerate adsorption modelling and can be embedded in optimisation algorithms to propose operating conditions, but inverse design requires stronger evidence than ordinary forward prediction because an optimiser can exploit unsupported regions of a surrogate. This study re-evaluates ID-SEAD, a constraint-aware stacked-ensemble concept for adsorption-system optimisation, using reconstructed primary-study provenance, fold-safe validation and feature-representation sensitivity analysis. The reconstructed corpus contains 322 usable-target observations, including 307 observations from 29 confirmed primary studies; a strict comparable population contains 273 observations from 24 studies. With the corrected full-engineered representation, shuffled five-fold validation gave R²=0.904 for Random Forest (RF) and 0.894 for XGBoost (XGB), but primary-study-grouped R² fell to 0.027 and 0.193, and leave-one-study-out (LOSO) R² to 0.008 and 0.162. A post hoc representation-sensitivity analysis then showed that this extreme transfer loss was not representation-independent: removing engineered material/pollutant/context categories increased grouped R² to 0.637 for RF and 0.481 for XGB, with LOSO R² of 0.628 and 0.457; numeric-only representations produced similar recovery. The improvement persisted when analysis was restricted to studies with at least five rows and when the two most incomplete process variables were removed. Nevertheless, the original agricultural-waste domain contains only 65 rows from four studies and remains strongly negative under LOSO, while a broader biogenic domain retains a catastrophic held-out study: after category removal, RF and XGB are both approximately 1.5 g/g wrong while disagreeing by only 40 mg/g on average. The legacy computational audit also identified test-informed constraint selection, an unsupported 624 mg/g universal ceiling and conflicting inverse-design lineage. These results show that study-aware validation is not merely a harsher test; it can diagnose harmful feature representations. Improved forward transfer, however, remains insufficient evidence for reliable inverse design without context-complete representation, domain depth, failure detection and external or experimental confirmation.

**Keywords:** adsorption; inverse design; study-aware validation; feature representation; provenance; machine learning; generalisation; reliability.

---

## 1. Introduction

Waste-derived sorbents and biochars are widely investigated for removal of dissolved contaminants from water, with performance governed jointly by material properties, pollutant context and operating variables such as pH, dose, concentration and temperature [1]–[4]. Machine learning (ML) can model nonlinear relationships within these systems and has increasingly been coupled with optimisation to search experimental or operating-condition spaces [2], [5]–[7]. The engineering evidentiary requirement, however, changes when a predictive surrogate is used prescriptively. A forward model predicts a response at a supplied point; an inverse-design system searches many candidate points and can preferentially select regions in which surrogate error is favourable to the objective.

ID-SEAD was developed as a constraint-aware stacked-ensemble concept combining Linear Regression (LR), Support Vector Regression (SVR), Random Forest (RF) and XGBoost (XGB) base learners with a Ridge meta-learner and a surrogate-guided optimisation stage. The legacy formulation reported strong apparent performance and described the framework as a prescriptive adsorption-design system. Before conference defence, reconstruction of the underlying literature-derived corpus raised two related questions: were held-out rows genuinely independent of the studies used for training, and did the selected feature representation generalise beyond the studies in which those features were observed?

These questions are important for literature-pooled datasets because many rows can originate from a single primary paper and share the same adsorbent preparation, pollutant system, laboratory protocol and characterisation workflow. Random row partitioning can therefore underestimate transfer error when the intended use concerns an unseen study [8]–[10]. A second, less obvious risk is feature-mediated study recognition: material or process categories can be genuinely predictive within represented studies yet act as unstable proxies when the model encounters a new experimental domain.

The present work re-evaluates ID-SEAD as a forensic engineering case study. The principal question is: **when evaluation is performed on complete primary studies, how much of ID-SEAD’s apparent predictive performance is genuine transfer and how much depends on the selected feature representation, and what does that imply for inverse design?** The contribution is fourfold: computational and provenance lineage are reconstructed; row-random and study-aware validation are matched on identical observations; feature representation is stress-tested under grouped and LOSO evaluation; and the resulting evidence is used to define the reliability conditions required before adsorption inverse-design recommendations can be considered actionable.

---

## 2. Data and Methods

### 2.1 Legacy ID-SEAD and computational audit

The legacy architecture used LR, SVR, RF and XGB [11], [12] to generate base predictions for a Ridge meta-learner. Constraint terms were intended to discourage negative predictions, predictions above an empirical capacity ceiling and excessive local sensitivity. The manuscript further described Differential Evolution (DE) [13] for target-oriented inverse design.

The legacy headline results are not reused as current performance evidence. The submitted manuscript reported R²=0.847, RMSE=254.1 mg/g and a 95% R² interval of [0.811,0.879], whereas an executed complete-notebook state produced R²=0.8069, RMSE=286.29 mg/g and [0.7578,0.8407]. More importantly, candidate constraint settings were evaluated using nominal final-test objects before the preferred setting was selected. The legacy 624 mg/g ceiling is also contradicted by the reconstructed corpus, and the stored Table-III optimisation lineage differs in both optimiser path and target set. The architecture is therefore retained as the audit target, while its legacy engineering-performance claims are treated as historical apparent results.

### 2.2 Provenance-controlled corpus

Dataset V2.1 contains 322 observations with usable adsorption-capacity targets. Primary-study provenance is confirmed for 307 observations from 29 studies; 15 remain unresolved. A strict comparable population of 273 observations from 24 primary studies was frozen for the principal matched analysis. The complete corpus is described as heterogeneous literature-derived adsorption data rather than as uniformly agricultural-waste-derived. A strict agricultural-waste subset contains 65 observations from four primary studies; broader biogenic-waste and waste-derived-carbon subsets contain 92 observations from six studies and 138 observations from seven studies, respectively.

The 24 studies are not equally represented. The five largest studies contribute 196/273 observations (71.8%), eight studies are singletons, the median study size is five rows, and the row-weighted Kish effective study count is 7.62. These diagnostics are reported because nominal study count alone overstates the balance of independent evidence.

### 2.3 Missingness and fold-safe preprocessing

In the strict 273-row population, parsed missingness is substantial for some process variables: adsorbent dose is missing in 168 rows (61.5%), contact time in 104 (38.1%), and surface area and pore volume in 29 rows each (10.6%). Imputation, encoding and scaling are fitted inside training folds. `removal_percent` is excluded because it can encode adsorption capacity through mass-balance relationships; source links and primary-study identifiers are excluded as predictors. The legacy `Q_MAX=624 mg/g` layer is disabled.

### 2.4 Validation designs

The full-engineered baseline uses the corrected feature-parity representation reconstructed from the legacy modelling design. Raw high-cardinality adsorbent, pollutant and processing strings are dropped after deterministic engineering, but derived context variables include base-material class, material class, pollutant class, activation agent, treatment indicators, pyrolysis temperature and interaction features.

Two matched five-fold schemes use the same 273 observations: shuffled KFold with random state 42, and GroupKFold with `primary_study_id_v21` as the grouping variable. Complete leave-one-primary-study-out (LOSO) evaluation provides a stricter robustness test. Row-random validation is retained only as a comparator; transfer claims are based on study-aware evaluation.

### 2.5 Post hoc feature-representation sensitivity

Following the initial forensic audit, a **post hoc sensitivity analysis** examined whether the severe full-engineered transfer loss depended on study-correlated contextual categories. This analysis was not predeclared as a confirmatory test and is interpreted as a robustness/diagnostic result.

Three representations were compared with identical folds and RF/XGB model specifications:

1. **Full engineered:** the corrected feature-parity representation.
2. **No identity-adjacent categories:** removes encoded base-material, material-class, pollutant-class and activation-agent categories while retaining measured/process variables, deterministic interactions and binary treatment indicators.
3. **Physical numeric only:** retains measured and derived numeric variables only.

Additional sensitivities evaluated LOSO only among studies with at least five rows and repeated the category-stripped analyses after removing dose and contact time, the two most incomplete process variables.

---

## 3. Results

### 3.1 Study-aware validation changes the assessment of the full representation

For the full-engineered representation, the conventional row-random results are strong: RF R²=0.9042 and XGB R²=0.8936. When complete primary studies are separated, pooled five-fold R² falls to 0.0265 for RF and 0.1929 for XGB; the Ridge stack falls from 0.9027 to -0.5566. Strict LOSO gives R²=0.0085 for RF and 0.1624 for XGB.

Grouped-fold difficulty is highly heterogeneous: RF fold R² ranges from -20.59 to 0.46 and XGB from -13.54 to 0.44. Consequently, pooled grouped R² is interpreted as a matched whole-population summary rather than a stable per-fold estimate.

### 3.2 The severe transfer loss is partly feature-representation dependent

Table I shows the principal post hoc sensitivity result. Removing identity-adjacent context categories lowers row-random accuracy modestly but substantially improves study-aware transfer. RF grouped R² rises from 0.0265 to 0.6370 and LOSO R² from 0.0085 to 0.6278. The numeric-only RF representation gives grouped R²=0.5796 and LOSO R²=0.5734. XGB shows the same qualitative pattern, although RF is stronger after category removal.

**Table I. Representation sensitivity on the identical strict 273-row / 24-study population.**

| Representation | Model | Row-random R² | Study-grouped R² | LOSO R² |
|---|---|---:|---:|---:|
| Full engineered | RF | 0.9042 | 0.0265 | 0.0085 |
| Full engineered | XGB | 0.8936 | 0.1929 | 0.1624 |
| No identity-adjacent categories | RF | 0.8250 | **0.6370** | **0.6278** |
| No identity-adjacent categories | XGB | 0.8214 | 0.4807 | 0.4574 |
| Physical numeric only | RF | 0.8252 | 0.5796 | 0.5734 |
| Physical numeric only | XGB | 0.8201 | 0.4964 | 0.4692 |

The result changes the mechanism implied by the first audit. The corpus contains transferable predictive signal, but the original engineered categorical representation appears to exploit contextual patterns that do not transfer reliably across primary studies. Study-aware validation therefore diagnoses a representation problem rather than merely producing a lower score.

### 3.3 Recovery persists under study-size and missingness sensitivity

Twelve primary studies contain at least five strict-comparable observations, representing 253 rows. When only these studies are used as held-out LOSO domains while all other strict studies remain available for training, RF R² remains 0.6163 after category removal. When the modelling population itself is restricted to the 12 studies with at least five rows, RF R² remains 0.6150. The corresponding numeric-only RF values are 0.5592 and 0.5870. Thus the recovered transfer is not driven by singleton studies.

The high missingness of dose and contact time also does not explain the recovery. After removing both variables and the dose-derived concentration/dose interaction, the category-stripped RF produces grouped R²=0.6522 and LOSO R²=0.6549; the numeric-only RF produces grouped R²=0.6819 and LOSO R²=0.6725. Missingness remains a major dataset limitation, but the representation-sensitivity conclusion survives this test.

### 3.4 Domain restriction still blocks the original inverse-design claim

Representation correction does not restore the original agricultural-waste engineering claim. The strict agricultural-waste subset contains only 65 observations from four studies and remains strongly negative under LOSO for every tested representation (RF approximately -1.74 to -1.76; XGB approximately -2.04 to -2.05).

The broader biogenic-waste subset is more encouraging at the pooled level: after category removal, XGB LOSO R² is approximately 0.642 across six studies. However, the pooled result conceals a severe complete-study failure. For the held-out Alshabib groundnut-shell study, the two observed capacities are 270.27 and 199.76 mg/g. The category-stripped RF predicts 1775.47 and 1753.89 mg/g, while XGB predicts 1724.41 mg/g for both rows. Their mean absolute errors are 1529.66 and 1489.39 mg/g, respectively, although the two models disagree by only 40.27 mg/g on average.

The waste-derived-carbon subset also improves modestly after category removal (RF LOSO R²=0.574; XGB=0.520 across seven studies), but remains a restricted-domain diagnostic rather than deployment evidence.

### 3.5 Predictive recovery does not equal inverse-design reliability

The Alshabib result preserves the key reliability warning after feature correction: two independently fitted tree models can agree closely while both are catastrophically wrong. The earlier full-engineered uncertainty audit reached the same qualitative conclusion using study-balanced residual intervals: very wide intervals still missed the severe held-out study. The corrected forward representation therefore improves average cross-study prediction but does not provide a dependable failure detector for prescriptive optimisation.

---

## 4. Discussion

### 4.1 Study-aware validation can diagnose harmful feature representations

The first corrected analysis showed a dramatic random-versus-grouped performance gap. The post hoc ablation demonstrates that this gap should not be attributed solely to an intrinsically non-generalising dataset. Derived material, pollutant and activation categories improve apparent within-corpus prediction but create substantial negative transfer when complete studies are withheld. Removing them reduces random-split R² from approximately 0.90 to 0.82, yet markedly improves grouped and LOSO performance.

This is an important modelling distinction. A feature can be statistically useful under random partitioning and still be harmful for the intended deployment unit. In literature-derived ML, validation design therefore participates in feature selection: the representation should be judged by its ability to transfer across the experimental unit relevant to the scientific claim, not only by row-wise accuracy.

### 4.2 Dropping context is not itself an inverse-design solution

The improved category-stripped predictor cannot simply be relabelled as a repaired ID-SEAD inverse-design system. A prescriptive adsorbent-process recommendation must specify the material and pollutant context under which process conditions are being optimised. Removing unstable categorical context may improve forward transfer, but an inverse-design framework ultimately needs a scientifically meaningful context representation that generalises rather than silently omitting the design domain.

A future ID-SEAD should therefore treat material and pollutant context as explicit immutable conditions or validated design variables, represented using descriptors or controlled domain definitions that survive study-aware nested validation. The target-matching objective, feasibility constraints and optimiser logs must also be predeclared and auditable.

### 4.3 Independent-study depth and missingness remain limiting

The nominal 24-study strict population is highly imbalanced, with 71.8% of rows contributed by five studies and a Kish effective study count of 7.62. The n>=5 sensitivity confirms that category-stripped transfer is not a singleton artifact, but it does not create new independent experimental domains. Likewise, removing dose and contact time shows that heavy imputation does not drive the recovered transfer, yet 61.5% missingness in dose is unacceptable to ignore for a future process-optimisation dataset.

These limitations are particularly acute for the intended agricultural-waste domain, where only four primary studies are available and transfer remains poor irrespective of representation.

### 4.4 Reliability requirements for future inverse design

The evidence supports a sharper reliability gate. Before a future adsorption surrogate is used for inverse design, it should demonstrate: primary-study provenance; a feature representation selected using study-aware/nested validation; adequate independent-study coverage in the exact material-pollutant domain; fold-local preprocessing and training-only tuning; explicit context variables required by the forward model; independently justified feasibility constraints; a target-consistent optimisation objective; machine-readable optimisation logs; an applicability/uncertainty procedure capable of identifying catastrophic study-level failures; and external or experimental confirmation of final recommendations.

Constraint compliance cannot substitute for transfer evidence. Similarly, agreement between two models cannot be treated as a safety signal when both models can be jointly wrong by approximately 1.5 g/g on an unseen study.

---

## 5. Conclusion

Re-evaluation of ID-SEAD shows that validation design can change not only the estimated performance of an adsorption ML model but also the model-development decision itself. The corrected full-engineered representation produces high row-random accuracy but transfers poorly to unseen primary studies. A post hoc representation-sensitivity analysis demonstrates that much of this extreme transfer loss is associated with engineered material/pollutant/context categories: removing them recovers substantial grouped and LOSO performance, and the improvement survives study-size and high-missingness sensitivity analyses.

This finding does not restore the legacy inverse-design claim. The strict agricultural-waste domain remains too small and performs poorly, a broader apparently successful domain retains a catastrophic unseen-study failure, model agreement does not reliably signal that failure, and the legacy constraint/optimisation lineage remains unsuitable for engineering validation. The defensible contribution is therefore representation-aware and reliability focused: **study-aware validation should be used to identify feature representations that genuinely transfer, and successful forward transfer must still pass domain, uncertainty and external-verification gates before adsorption inverse-design recommendations are treated as actionable.**

## Data and Code Availability — working wording

The reconstructed V2.1 dataset, provenance maps, current modelling/preprocessing scripts, row-level predictions, fold manifests, software environment, post-review sensitivity scripts and GitHub Actions evidence are versioned in the project repository. The frozen baseline and independent-review revision gate are retained as separate workflows so that post hoc sensitivity results cannot silently overwrite the pre-review numerical record.

## References

[1] M. Qiu et al., “Biochar for the removal of contaminants from soil and water: A review,” *Biochar*, vol. 4, art. no. 19, 2022, doi: 10.1007/s42773-022-00146-1.

[2] W. Zhang et al., “Synthesis optimization and adsorption modeling of biochar for pollutant removal via machine learning,” *Biochar*, vol. 5, art. no. 25, 2023, doi: 10.1007/s42773-023-00225-x.

[3] X. Wei et al., “Machine learning insights in predicting heavy metals interaction with biochar,” *Biochar*, vol. 6, art. no. 10, 2024, doi: 10.1007/s42773-024-00304-7.

[4] Y. Ge et al., “A systematic review on machine learning-aided design of engineered biochar for soil and water contaminant removal,” *Front. Soil Sci.*, vol. 5, art. 1623083, 2025, doi: 10.3389/fsoil.2025.1623083.

[5] Z. H. Jaffari et al., “Machine-learning-based prediction and optimization of emerging contaminants’ adsorption capacity on biochar materials,” *Chem. Eng. J.*, vol. 466, art. 143073, 2023, doi: 10.1016/j.cej.2023.143073.

[6] P. Yu, Z. Huang, and W. Xie, “Machine Learning-Driven Optimization for Predicting Biochar Adsorption Performance Toward Pb(II) and Cd(II),” *Water*, vol. 18, no. 12, art. 1416, 2026, doi: 10.3390/w18121416.

[7] M. F. Rabbi, “Computational framework for multi-objective optimization of activated biochar properties using machine learning and evolutionary algorithms,” *Sci. Rep.*, vol. 16, art. 22466, 2026, doi: 10.1038/s41598-026-50569-0.

[8] D. R. Roberts et al., “Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure,” *Ecography*, vol. 40, no. 8, pp. 913–929, 2017, doi: 10.1111/ecog.02881.

[9] S. Kapoor and A. Narayanan, “Leakage and the reproducibility crisis in machine-learning-based science,” *Patterns*, vol. 4, no. 9, art. 100804, 2023, doi: 10.1016/j.patter.2023.100804.

[10] G. Varoquaux, “Cross-validation failure: Small sample sizes lead to large error bars,” *NeuroImage*, vol. 180, pp. 68–77, 2018, doi: 10.1016/j.neuroimage.2017.06.061.

[11] L. Breiman, “Random forests,” *Mach. Learn.*, vol. 45, pp. 5–32, 2001, doi: 10.1023/A:1010933404324.

[12] T. Chen and C. Guestrin, “XGBoost: A scalable tree boosting system,” in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, 2016, pp. 785–794, doi: 10.1145/2939672.2939785.

[13] R. Storn and K. Price, “Differential evolution—A simple and efficient heuristic for global optimization over continuous spaces,” *J. Global Optim.*, vol. 11, pp. 341–359, 1997, doi: 10.1023/A:1008202821328.
