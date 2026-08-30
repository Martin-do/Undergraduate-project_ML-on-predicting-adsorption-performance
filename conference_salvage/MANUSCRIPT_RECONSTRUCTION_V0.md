# From Apparent Accuracy to Reliable Inverse Design: A Study-Aware Audit of ID-SEAD for Adsorption-System Optimisation

**Working conference-manuscript reconstruction — V0**  
**Status:** evidence-aligned scientific draft; bibliography and final figure/table formatting still to be completed.  
**Authors:** M. Jaiyeola; Oladeji O. Ige; Oludolapo A. Olanrewaju  

## Abstract

Machine-learning surrogates are increasingly used to predict adsorption performance and, when embedded in optimisation algorithms, may also be used to propose operating conditions for a desired adsorption target. Inverse design imposes a stronger reliability requirement than ordinary forward prediction because an optimiser can actively search regions in which a surrogate is poorly supported by training evidence. This study re-evaluates ID-SEAD, a previously developed constraint-aware stacked-ensemble framework for adsorption-system optimisation, using reconstructed primary-study provenance and study-aware validation. The reconstructed corpus contains 322 usable-target observations, of which 307 are traceable to 29 primary studies; a strict comparable population contains 273 observations from 24 primary studies. On the same 273 observations, conventional shuffled five-fold validation produced high performance for Random Forest (R² = 0.9042), XGBoost (R² = 0.8936), and an unconstrained Ridge stack (R² = 0.9027). When complete primary studies were kept separate using five-fold GroupKFold, performance fell to R² = 0.0265 for Random Forest, 0.1929 for XGBoost, and −0.5566 for the stack. Leave-one-primary-study-out evaluation gave R² = 0.0085 for Random Forest and 0.1624 for XGBoost. A computational-lineage audit further identified final-test-informed legacy constraint selection, an unsupported 624 mg/g universal upper bound, and conflicts between the reported and stored inverse-design implementations. The findings do not invalidate constraint-aware inverse design as a research concept; rather, they show that strong row-wise predictive accuracy is insufficient evidence for reliable transfer to unseen studies and therefore insufficient to justify engineering inverse-design claims. We propose a provenance-aware reliability gate requiring study-independent validation, fold-safe tuning, explicitly justified constraints, auditable optimisation, and external or experimental confirmation before adsorption inverse-design recommendations are treated as actionable.

**Keywords:** adsorption; inverse design; study-aware validation; stacked ensemble; provenance; machine learning; generalisation; wastewater treatment.

---

## 1. Introduction

Adsorption remains an important approach for removing dissolved contaminants from water and wastewater, and low-cost waste-derived adsorbents continue to attract interest because of their potential environmental and economic benefits. Machine learning (ML) offers a complementary route to classical adsorption modelling by learning nonlinear associations among material properties, adsorbate context and process conditions. However, a predictive model and an engineering design model answer different questions. Forward prediction asks what response is expected for a supplied experimental configuration. Inverse design asks which configuration should be selected to achieve a desired response. The latter is inherently more demanding because optimisation may deliberately search toward combinations that are sparsely represented, extrapolative, or otherwise unreliable for the surrogate.

ID-SEAD was developed as a constraint-aware stacked-ensemble concept combining Linear Regression (LR), Support Vector Regression (SVR), Random Forest (RF) and XGBoost (XGB) base learners with a Ridge meta-learner and a surrogate-guided optimisation stage. The original conference formulation reported strong apparent predictive performance and framed the system as a prescriptive adsorption-design tool. Subsequent reconstruction of the underlying literature-derived corpus, however, raised a more fundamental question: were the held-out observations genuinely independent of the studies represented during model development?

This distinction matters for literature-derived adsorption datasets. A single primary paper can contribute many observations measured with the same adsorbent preparation, characterisation workflow, pollutant system and laboratory protocol. Randomly distributing rows from such a study across training and test partitions allows study-specific signatures to appear on both sides of the split. A model may then achieve high test performance while remaining weak when faced with an entirely unseen experimental study. For an inverse-design system, this form of optimism is especially consequential because the optimiser can exploit surrogate errors rather than merely encounter them passively.

The present study therefore re-evaluates ID-SEAD as an engineering case study. The research question is: **can the apparent engineering performance of a constraint-aware adsorption inverse-design framework survive reconstruction of primary-source provenance and validation on genuinely unseen studies?** The contributions are fourfold. First, the original modelling corpus and numerical lineage are reconstructed. Second, conventional row-random validation is compared directly with primary-study-aware validation on the same observations. Third, the implications of the resulting generalisation gap for inverse design are examined. Fourth, a reproducible reliability gate is proposed for future adsorption inverse-design systems.

The aim is not to allege misconduct or to argue that inverse design is intrinsically unsuitable for adsorption engineering. Rather, the aim is to establish what the available evidence can and cannot support, and to convert the lessons from the legacy implementation into a more defensible prospective methodology.

---

## 2. Legacy ID-SEAD Formulation and Audit Target

### 2.1 Legacy stacked-ensemble architecture

The legacy ID-SEAD implementation used four base regressors: LR, SVR, RF and XGB. Out-of-fold predictions from the base learners were supplied to a Ridge meta-learner. The conceptual objective was to combine predictive diversity across models while adding penalties intended to discourage negative predictions, predictions exceeding a specified upper capacity, and excessive local sensitivity to perturbed inputs.

This architecture is retained here as a historical and methodological component. However, the existence of an implemented architecture is separated from the question of whether its reported performance estimates constitute evidence of unseen-study generalisation.

### 2.2 Legacy inverse-design concept

The original formulation embedded the fitted surrogate inside a numerical optimiser so that operating conditions could be searched for a target adsorption response. The manuscript described Differential Evolution (DE) over pH, temperature, adsorbent dosage and initial concentration. That concept remains scientifically interesting, but the audit identified two prerequisites that must precede any renewed engineering recommendation: the surrogate must demonstrate reliable study-independent transfer, and the optimisation problem must be fully specified with all material and adsorbate context required by the forward model.

### 2.3 Why the legacy headline metrics are treated as apparent performance

The original manuscript reported ID-SEAD R² = 0.847, RMSE = 254.1 mg/g, CV R² = 0.789 ± 0.031, a constraint-violation reduction from 49.2% to 33.9%, perturbation sensitivity of 8.73 mg/g, and inverse-designed configurations for target capacities of 100, 200 and 350 mg/g. During computational-lineage reconstruction, these values did not resolve to one immutable executed notebook state. An executed complete-notebook state instead reported R² = 0.8069, RMSE = 286.29 mg/g and a bootstrap R² interval of [0.7578, 0.8407]; additional stored variants also differed in violation and perturbation metrics. Consequently, the legacy headline numbers are not used as current performance evidence in this study.

More importantly, inspection of the legacy constraint-selection path showed that candidate settings were evaluated using objects representing the final test responses/predictions before the preferred setting was chosen. Thus the nominal final test set was not untouched by model selection. This defect is independent of the later provenance reconstruction and is sufficient to prevent the legacy final-test metrics from being interpreted as an unbiased holdout estimate.

---

## 3. Data and Computational Reconstruction

### 3.1 Provenance reconstruction

The reconstructed Dataset V2.1 contains 322 usable-target observations. Primary-study provenance was confirmed for 307 observations distributed across 29 reconstructed primary studies. Fifteen observations remain unresolved at the primary-study level. To minimise target and record-type incompatibilities, a stricter comparable population of 273 observations from 24 primary studies was frozen for the principal matched validation analysis.

Every validation comparison reported in Section 5 uses the same strict 273-row population when contrasting shuffled row-random and study-grouped evaluation. This design prevents changes in sample composition from being mistaken for an effect of the split strategy.

### 3.2 Correction of the agricultural-waste scope

The original manuscript characterised all 322 observations as agricultural-waste-derived adsorption experiments. The domain audit does not support that description. When source lineage and precursor domain were explicitly audited, the strict agricultural-waste subset contained only 65 observations from four independent primary studies. Broader predeclared domains contained 92 observations from six studies for a biogenic-waste scope and 138 observations from seven studies for a waste-derived-carbon scope.

Accordingly, the present paper describes the 322-row resource as a heterogeneous literature-derived adsorption corpus rather than relabelling the complete dataset as agricultural waste. Domain-specific results are interpreted separately from the principal strict-comparable generalisation analysis.

### 3.3 Predictor and preprocessing controls

The corrected validation excludes `removal_percent` from the predictor set because it can act as a direct target proxy for adsorption capacity under common mass-balance formulations. Source links and primary-study identifiers are also excluded as predictors. Missing-value handling, encoding, scaling and model-selection operations are fitted within the relevant training folds rather than on the complete dataset before splitting.

The legacy empirical upper limit of 624 mg/g is not used. Reconstruction demonstrated valid target observations above that value; therefore, the former ceiling cannot be defended as a universal physical law. Any future physical or domain constraint must be independently justified for the particular material–pollutant domain in which inverse design is attempted.

### 3.4 Validation protocol

Two matched five-fold evaluation schemes were applied to the strict 273-row population.

**Diagnostic row-random validation.** A shuffled five-fold KFold split with random state 42 was retained to quantify the apparent performance obtainable when observations, rather than studies, are treated as independent.

**Primary study-aware validation.** Five-fold GroupKFold used reconstructed primary-study identity as the grouping variable. No primary study was allowed to contribute observations to both the training and held-out portion of the same fold.

A second robustness analysis used leave-one-primary-study-out (LOSO) evaluation for RF and XGB. Each primary study was held out in turn and predicted using a model trained without observations from that study.

Row-random performance is treated only as a diagnostic comparator. Scientific claims about transfer beyond represented experiments are based on study-aware analyses.

### 3.5 Reproducibility controls

The corrected validation is executable through a pinned GitHub Actions workflow using Python 3.11.15, NumPy 2.4.6, pandas 3.0.5, SciPy 1.17.1, scikit-learn 1.9.0, XGBoost 3.2.0 and openpyxl 3.1.5. A machine-readable baseline freezes the expected dataset counts and numerical outputs. The workflow fails if study-overlap checks, forbidden-predictor checks, scope counts, package versions or frozen metrics do not match the declared baseline. The successful conference-salvage run passed all eight reproducibility tests and regenerated the historical corrected V2.1 evidence within the declared numerical tolerance.

---

## 4. Reliability Requirements for Inverse Design

For this study, successful forward-prediction metrics are not treated as sufficient evidence for inverse design. A surrogate is considered eligible for inverse-design interpretation only if it satisfies a prospective reliability gate comprising the following conditions:

1. primary-study provenance is sufficiently resolved to define independent groups;
2. preprocessing and all model/constraint tuning are confined to training information;
3. performance remains useful under study-independent validation;
4. catastrophic held-out-study failures are either absent or reliably identified by a predeclared applicability/uncertainty mechanism;
5. optimisation variables and immutable material/pollutant context are completely specified;
6. feasibility constraints are domain-justified rather than inferred from an arbitrary global training maximum;
7. optimisation objectives, seeds, bounds, convergence status and final candidates are archived in machine-readable form; and
8. strong engineering recommendations are externally and preferably experimentally verified before deployment claims are made.

Under this gate, a constraint cannot compensate for missing scientific knowledge. Bounding a surrogate prediction can prevent a numerically forbidden output, but it does not demonstrate that the recommendation generalises to a new experimental system.

---

## 5. Results

### 5.1 Row-random validation gives an optimistic view of performance

Table 1 compares matched row-random and primary-study-grouped performance on the identical 273-row strict-comparable population.

**Table 1. Matched validation on the strict-comparable corpus (273 observations, 24 primary studies).**

| Model | Row-random R² | Row-random RMSE (mg/g) | Study-grouped R² | Study-grouped RMSE (mg/g) |
|---|---:|---:|---:|---:|
| LR | 0.5913 | 449.64 | -3.9785 | 1569.38 |
| SVR | -0.2511 | 786.71 | -0.6490 | 903.22 |
| RF | 0.9042 | 217.70 | 0.0265 | 693.96 |
| XGB | 0.8936 | 229.44 | 0.1929 | 631.90 |
| Unconstrained Ridge stack | 0.9027 | 219.35 | -0.5566 | 877.53 |

The contrast is substantial for all high-performing row-random models. RF falls from R² = 0.9042 under shuffled row-wise validation to R² = 0.0265 when complete primary studies are withheld. XGB falls from 0.8936 to 0.1929. The unconstrained stack falls from 0.9027 to −0.5566. Thus the apparent row-random advantage does not translate into comparable performance on unseen studies.

The result also challenges the legacy assumption that stacking itself confers reliable engineering robustness. Under primary-study-grouped validation, the Ridge stack performs worse than RF and XGB and yields a negative pooled R².

### 5.2 Leave-one-study-out robustness confirms weak transfer

LOSO evaluation gives a stricter view of study transfer because every primary study serves once as the unseen test domain.

**Table 2. Strict LOSO performance.**

| Model | R² | RMSE (mg/g) | MAE (mg/g) | Median AE (mg/g) |
|---|---:|---:|---:|---:|
| RF | 0.0085 | 700.37 | 476.24 | 215.87 |
| XGB | 0.1624 | 643.73 | 447.46 | 257.24 |

The LOSO results are consistent with the grouped five-fold analysis: performance on unseen primary studies is much weaker than the row-random results imply. XGB remains the stronger of the two tree models under LOSO, but R² = 0.1624 is not sufficient evidence for reliable prescriptive optimisation across unseen adsorption studies.

### 5.3 Domain restriction does not recover the original agricultural-waste claim

The strict agricultural-waste subset contains only 65 observations from four independent primary studies. Under LOSO, XGB performance on this subset is strongly negative (R² approximately −2.04). The small number of independent studies and poor study-transfer result mean that the original agricultural-waste-only inverse-design claim cannot be restored using the present corpus.

A broader biogenic-waste subset shows better pooled LOSO performance (XGB R² approximately 0.619 across six studies), while the waste-derived-carbon subset gives approximately 0.495 across seven studies. These pooled values nevertheless conceal substantial between-study instability. In the broader biogenic analysis, one complete held-out study produces an MAE of approximately 1532.6 mg/g. Such a failure is particularly important for inverse design because a pooled average can appear useful while an individual unseen experimental domain remains catastrophically mispredicted.

### 5.4 Why the present corpus fails the inverse-design reliability gate

The study-aware results establish three linked findings. First, strong row-random predictive accuracy does not imply transfer to unseen studies. Second, restricting the corpus to apparently more coherent domains does not yet provide enough independent-study depth and stability to establish reliable inverse design. Third, retrospective uncertainty/model-agreement diagnostics did not reliably identify the worst held-out-study failure during the broader audit.

The current evidence therefore fails the predeclared inverse-design reliability gate. This does not imply that numerical optimisation cannot be run. It means that the resulting optimum would be an optimum of a surrogate whose reliability at an unseen study is not adequately established. Such a recommendation cannot responsibly be presented as an actionable engineering specification.

---

## 6. Discussion

### 6.1 The main problem is independence, not merely model choice

The most important lesson from the re-evaluation is that the validation unit must reflect the intended claim. If the intended use is to interpolate among additional measurements from studies already represented in the training corpus, row-random validation may describe that limited task. If the intended claim is that a model can support decisions for a new material, pollutant system or experimental study, rows from the same primary study cannot be treated as independent train/test evidence.

The sharp fall in RF and XGB performance under GroupKFold and LOSO indicates that the legacy random evaluation benefited substantially from within-study information sharing. The result is not unique to one algorithm and is not repaired by stacking. A more sophisticated learner cannot, by itself, create independent evidence that the dataset does not contain.

### 6.2 Constraint compliance is not equivalent to physical validity

The legacy ID-SEAD formulation attempted to enforce non-negativity, a 624 mg/g upper limit and local perturbation stability. The audit demonstrates why these properties must be described carefully. Non-negativity is a defensible numerical constraint for adsorption capacity. In contrast, 624 mg/g was the empirical maximum assumed by the legacy implementation, not a universal adsorption law. Valid observations above this value exist in the reconstructed evidence base.

More generally, a prediction can satisfy numerical bounds and still be scientifically wrong for a new study. Constraint compliance should therefore be distinguished from validated physical feasibility. Future ID-SEAD versions should use domain-specific constraints derived from material chemistry, mass balance, experimental operating ranges or other independently justified information rather than a global empirical maximum.

### 6.3 Inverse design requires stronger evidence than forward prediction

Ordinary prediction evaluates a supplied point. Optimisation searches over many points and can therefore favour regions where model error is systematically advantageous to the objective. This creates an optimiser–surrogate interaction: even modest predictive defects can become amplified when the optimiser deliberately exploits the surrogate surface.

For this reason, an adsorption inverse-design framework should not be advanced to prescriptive engineering use solely because a forward model has a high random-split R². Study-independent transfer, applicability-domain diagnostics and optimisation auditing are prerequisites. Where possible, the final recommendation should be tested experimentally before claims of engineering readiness are made.

### 6.4 What remains scientifically valuable in ID-SEAD

The audit does not make the ID-SEAD research direction valueless. The architecture provides a concrete framework in which prediction, constraints and optimisation can be studied together. More importantly, its reconstruction exposes a general problem that is easy to miss when literature-derived ML datasets are evaluated row by row.

The appropriate conclusion is therefore narrower but stronger: **ID-SEAD remains a viable inverse-design research concept, but the legacy heterogeneous corpus and validation design were insufficient to establish reliable engineering generalisation.** The corrected study-aware pipeline provides the evidence standard against which a future rebuilt ID-SEAD should be tested.

---

## 7. Prospective Requirements for a Rebuilt ID-SEAD

A future ID-SEAD dataset should be constructed for inverse design rather than assembled only for predictive row count. In particular, it should preserve exact primary-source lineage; explicitly encode or restrict material/precursor and pollutant context; and contain repeated process-condition observations within comparable material–pollutant systems across many independent studies. This structure is needed to distinguish changes caused by operating variables from differences caused by the material, adsorbate or laboratory itself.

The modelling pipeline should use nested study-aware validation, fold-local preprocessing and training-only tuning. The inverse objective should be predeclared. If target matching is intended, the optimiser should minimise a target-error objective subject to justified feasibility constraints rather than maximise predicted capacity while describing the outcome as target matching. Material variables required by the forward model must either be fixed and reported as immutable context or included in a scientifically meaningful design space.

Every optimisation run should archive the random seed, algorithm, variable bounds, objective formulation, penalties, convergence history and final candidate. Applicability-domain and uncertainty procedures should be selected before evaluating the external test domain. Only after a model passes this reliability gate should independent external data—and ultimately laboratory verification—be used to support a prescriptive engineering claim.

---

## 8. Conclusion

This study re-evaluated ID-SEAD using reconstructed primary-study provenance and a reproducible study-aware validation framework. The principal finding is that strong row-random performance on a heterogeneous literature-derived adsorption corpus does not translate into reliable performance on unseen primary studies. On the same 273 observations, RF changed from R² = 0.9042 under row-random validation to 0.0265 under primary-study-grouped validation, while XGB changed from 0.8936 to 0.1929. Strict LOSO performance remained weak (R² = 0.0085 for RF and 0.1624 for XGB). The stacked model did not provide a study-transfer advantage.

The computational-lineage audit also showed that legacy inverse-design claims relied on an invalid universal 624 mg/g ceiling, test-informed constraint selection and non-unique optimisation-result lineage. Consequently, the present corpus cannot support a validated deployment-ready inverse-design claim.

The contribution of the re-evaluated ID-SEAD study is therefore methodological and engineering-reliability focused: it demonstrates why inverse design requires provenance-aware, study-independent validation beyond conventional predictive accuracy and establishes a reproducible gate for future adsorption optimisation systems. The original inverse-design proposition remains testable, but it should be retested prospectively on a purpose-built, provenance-controlled dataset and followed by independent or experimental verification before actionable engineering recommendations are claimed.

---

## Data and Code Availability — working wording

The reconstructed provenance-controlled dataset, validation code, fold audit, row-level predictions, software environment, machine-readable run manifest and reproducibility checks are versioned in the project repository. The conference-salvage reproducibility workflow regenerates the corrected V2.1 evidence under a pinned software environment and verifies it against a frozen numerical baseline. Source-paper access restrictions, if any, should be stated explicitly in the final submission rather than replacing the reproducibility package with an “available on request” statement.

## Reproducibility statement — working wording

The principal validation results were regenerated in GitHub Actions using Python 3.11.15, NumPy 2.4.6, pandas 3.0.5, SciPy 1.17.1, scikit-learn 1.9.0 and XGBoost 3.2.0. All eight reproducibility-contract tests passed, including zero primary-study overlap in grouped folds and exact reproduction of the frozen corrected V2.1 numerical baseline within the declared tolerance. Row-random results are reported only as diagnostic comparators; study-aware validation is the basis of the scientific generalisation claim.

## Author-contribution / conflict / AI-policy notes

These statements must be completed factually by the authors before submission. Do not infer contribution roles, competing-interest status or generative-AI disclosure requirements from the computational record.

## References

**REFERENCE AUDIT REQUIRED BEFORE SUBMISSION.** The legacy bibliography contains multiple bibliographic mismatches. No unverified legacy citation should be carried into the submission merely to preserve numbering. Rebuild the reference list from verified publisher/Crossref/primary records and cite only sources that support the rewritten claims.
