# ID-SEAD Revisited: Study-Aware Validation, Pollutant-Representation Repair and Reliability Limits in Adsorption Inverse Design

**Working conference-manuscript reconstruction — V3**  
**Status:** targeted supervisor-revision evidence aligned; final template rendering and final cross-reference audit pending.  
**Authors:** M. Jaiyeola; Oladeji O. Ige; Oludolapo A. Olanrewaju

## Abstract

Machine-learning surrogates can support adsorption modelling and optimisation, but inverse design requires evidence that predictions remain reliable when the model encounters genuinely unseen experimental studies. This work re-evaluates ID-SEAD, a stacked-ensemble adsorption optimisation concept, using reconstructed primary-study provenance, fold-safe preprocessing and study-aware validation. The reconstructed corpus contains 322 usable-target observations, including 307 observations from 29 confirmed primary studies; a strict comparable population contains 273 observations from 24 studies. In the legacy-compatible engineered representation, shuffled five-fold R² was 0.904 for Random Forest (RF) and 0.894 for XGBoost (XGB), whereas leave-one-primary-study-out (LOSO) R² fell to 0.008 and 0.162. A post hoc family-by-family audit localized most of this transfer loss to the derived pollutant-class feature. The legacy class used unbounded substring rules; a target-blind exact-label/provenance audit found class disagreement in 122/273 strict rows (44.7%). Correcting only pollutant class while retaining pollutant context reduced row-random R² to 0.824/0.823 but increased study-grouped R² to 0.591/0.485 and LOSO R² to 0.596/0.465 for RF/XGB. However, study-cluster uncertainty remained wide, and the intended agricultural-waste domain contained only 65 observations from four studies and remained strongly negative under LOSO (RF -1.741; XGB -2.047). Broader restricted domains retained catastrophic complete-study errors of approximately 1.5 g/g despite close RF/XGB agreement. The legacy audit also identified test-informed constraint selection, an unsupported universal 624 mg/g ceiling and conflicting optimisation lineage. Thus study-aware validation exposed a correctable pollutant-representation defect and restored meaningful average forward transfer, but current evidence remains insufficient for reliable inverse design without deeper domain-specific evidence, validated failure detection and external or experimental confirmation.

**Keywords:** adsorption; inverse design; study-aware validation; pollutant representation; provenance; machine learning; generalisation; reliability.

---

## 1. Introduction

Waste-derived sorbents and biochars are widely investigated for removal of contaminants from water, with performance governed jointly by material properties, pollutant identity and operating variables such as pH, dose, concentration and temperature [1]–[4]. Machine learning (ML) has been used both for adsorption-capacity prediction and for optimisation of adsorption or biochar design variables. Direct aqueous-adsorption examples include Jaffari et al. [5] and Yu et al. [6], while related work has coupled ML surrogates with evolutionary optimisation for broader activated-biochar process objectives [7]. These studies establish the relevance of predictive and optimisation models but do not remove the need to validate the transfer conditions under which a surrogate is used prescriptively.

ID-SEAD was developed as a constraint-aware stacked-ensemble concept combining Linear Regression (LR), Support Vector Regression (SVR), Random Forest (RF) and XGBoost (XGB) base learners with a Ridge meta-learner and a surrogate-guided optimisation stage. The legacy formulation reported strong apparent performance and described the framework as a prescriptive adsorption-design system. Reconstruction of the literature-derived corpus raised two engineering questions: whether validation rows were genuinely independent of the primary studies used for training, and whether the engineered material/pollutant representation itself remained valid on unseen studies.

This distinction matters because literature-pooled datasets are hierarchical: many observations from one paper share adsorbent preparation, pollutant system, laboratory protocol and characterization workflow. Randomly splitting rows can therefore underestimate transfer error when the intended deployment unit is a new study [8]–[10]. Study-correlated categories can also be useful within represented papers yet fail under study transfer if the categories are too coarse, incorrectly encoded or unsupported in new domains. Association with study identity alone is not proof of leakage; the representation must be tested directly.

The present work treats ID-SEAD as a forensic engineering case study. It reconstructs computational and provenance lineage, compares row-random with study-aware validation on identical observations, audits the engineered context families, repairs a target-blind pollutant-class encoding defect, and asks whether the resulting forward model satisfies the reliability conditions needed before inverse-design recommendations can be considered actionable.

---

## 2. Data and Methods

### 2.1 Legacy ID-SEAD and computational audit

The legacy architecture used LR, SVR, RF and XGB [11], [12] to generate base predictions for a Ridge meta-learner. Constraint terms were intended to discourage negative predictions, predictions above an empirical capacity ceiling and excessive local sensitivity, and the manuscript described Differential Evolution (DE) [13] for target-oriented search.

Legacy headline numbers are not reused as current validation evidence. The submitted manuscript reported R²=0.847, RMSE=254.1 mg/g and a 95% R² interval of [0.811, 0.879], whereas an executed complete-notebook state produced R²=0.8069, RMSE=286.29 mg/g and [0.7578, 0.8407]. Candidate constraint settings also accessed nominal final-test objects before the preferred setting was selected. The stored optimisation lineage differs in optimiser path and target set, so historical optimisation recommendations are not treated as reproducible engineering outputs.

### 2.2 Provenance-controlled corpus

Dataset V2.1 contains 322 observations with usable adsorption-capacity targets. Primary-study provenance is confirmed for 307 observations from 29 studies; 15 observations remain unresolved. A strict comparable population of 273 observations from 24 primary studies was frozen for matched validation. The corpus is described as heterogeneous literature-derived adsorption data rather than uniformly agricultural-waste-derived. Predefined domain subsets contain 65 observations/4 studies for strict agricultural waste, 92/6 for broad biogenic waste and 138/7 for waste-derived carbon.

Study sizes are highly unequal: the five largest studies contribute 196/273 observations (71.8%), eight studies are singletons, median study size is five rows, and the row-weighted Kish effective study count is 7.62. The reconstructed maximum target is 2239 mg/g and traces to the Li et al. activated-carbon/methylene-blue study [14], which reports maximum adsorption capacity of about 2251 mg/g. The legacy universal `Q_MAX=624 mg/g` rule is therefore disabled.

### 2.3 Fold-safe representation and model specifications

Raw predictors comprise adsorbent and processing text, surface area, particle size, pore volume, pollutant, initial concentration, temperature, contact time, pH and dose. `removal_percent` is excluded because it can encode adsorption capacity through mass balance; source links and study identifiers are never predictors. Deterministic engineering derives pyrolysis temperature, activation/treatment indicators, base-material class, material class, pollutant class, activation agent, concentration/dose ratio, surface-area×pore-volume and pH×temperature. Raw high-cardinality adsorbent, pollutant and processing strings are then removed.

All learned preprocessing is fitted inside the training portion of each fold. Surface area, pore volume and pyrolysis temperature use training-fold material-class medians followed by a training global median; remaining numeric variables use training global medians. If a variable is entirely missing in a training fold it is made inactive and fixed to zero in both training and held-out transformations rather than borrowing held-out information. Engineered categorical variables are drop-first one-hot encoded with unseen levels ignored, and the selected continuous variables are standardized using training statistics only.

The fixed model specifications are LR; RBF-SVR (`C=10`, `epsilon=0.1`); RF (200 trees, `min_samples_split=3`, unrestricted depth, random state 42); and XGB (100 trees, learning rate 0.1, maximum depth 3, squared-error objective, random state 42). The Ridge stack is audited separately using fold-local out-of-fold base predictions and training-only alpha selection.

### 2.4 Study-aware validation and V3 representation audit

Two matched five-fold designs use the identical 273 rows: shuffled KFold (random state 42) and primary-study GroupKFold. Complete leave-one-primary-study-out (LOSO) evaluation is the primary transfer test; row-random performance is retained only as a reference diagnostic.

The post hoc V3 representation audit first quantified association between the four engineered context families—activation agent, base material, material class and pollutant class—and primary study using normalized mutual information, Cramér's V and study-ID classification. Each category family was then removed separately under the identical grouped and LOSO folds. Joint category permutation was used as a target-blind diagnostic. These analyses are exploratory/mechanistic rather than predeclared confirmatory tests.

Family ablation localized the dominant transfer sensitivity to `pollutant_class`, prompting a source-code integrity audit. The legacy class used unbounded substring matching, so strings such as `Basic Violet 10`, `Congo Red (CR)` and `Oil & Grease` could collide with metal tokens such as `as` or `cr`, while several dye abbreviations were missed. A replacement exact-label map was constructed before model fitting from the pollutant labels and recovered primary-study context; neither `qe` nor validation performance was used to assign classes. The corrected representation changes only the derived pollutant class and retains all other context and model settings.

### 2.5 Reliability and domain gates

LOSO predictions are summarized both row-pooled and study-by-study. Study-level uncertainty is assessed by 5000-replicate cluster bootstrap resampling of primary studies. Domain-restricted LOSO is repeated on the three predefined material domains. Training-only support-distance diagnostics are treated as explanatory applicability-domain checks, not as validated safety gates. No inverse-design recommendation table is generated unless the forward surrogate demonstrates adequate domain depth, stable study-level transfer, a dependable failure-detection rule, justified constraints and external or experimental confirmation.

---

## 3. Results

### 3.1 The legacy-compatible representation does not transfer under study separation

The legacy-compatible engineered representation produces strong row-random performance (RF R²=0.9042; XGB=0.8936) but poor study transfer. Primary-study-grouped R² falls to 0.0265 and 0.1929, and LOSO R² to 0.0085 and 0.1624 for RF and XGB, respectively. Grouped fold R² ranges from -20.59 to 0.46 for RF and -13.54 to 0.44 for XGB, showing severe study-to-study instability. The Ridge stack is also unstable: its mean grouped outer-fold R² is -39.84, with a minimum of -103.29 and strongly variable meta-weights. Consequently, row-random and stacked results are not interpreted as unseen-study generalisation.

### 3.2 The dominant transfer defect is pollutant-class representation

All four engineered context families are study-associated (Cramér's V 0.77–0.96). On the 12 studies with at least five observations, the four families jointly predict study identity with logistic-regression accuracy 0.648, compared with a 0.265 majority-class reference. However, association alone does not identify the harmful feature: removing base material or material class changes RF LOSO R² only from 0.0085 to 0.0084 or 0.0242, whereas removing pollutant class raises RF LOSO R² to 0.5802 and XGB to 0.4625.

The code audit then identified why. The target-blind exact-label pollutant audit disagrees with the legacy derived class for 122/273 rows (44.7%) spanning 14/29 unique pollutant labels. Correcting pollutant class while preserving pollutant context recovers nearly the same transfer as deleting the category, and for XGB slightly exceeds the earlier four-category deletion in LOSO.

**Table I. Representation audit on the identical 273-row / 24-study population.**

| Representation | Model | Row-random R² | Study-grouped R² | LOSO R² |
|---|---|---:|---:|---:|
| Legacy-compatible engineered | RF | 0.9042 | 0.0265 | 0.0085 |
| Legacy-compatible engineered | XGB | 0.8936 | 0.1929 | 0.1624 |
| Remove pollutant class | RF | — | 0.5861 | 0.5802 |
| Remove pollutant class | XGB | — | 0.4818 | 0.4625 |
| **Corrected pollutant class; context retained** | **RF** | **0.8241** | **0.5912** | **0.5960** |
| **Corrected pollutant class; context retained** | **XGB** | **0.8228** | **0.4846** | **0.4645** |
| Remove all four context families | RF | 0.8250 | 0.6370 | 0.6278 |
| Remove all four context families | XGB | 0.8214 | 0.4807 | 0.4574 |

The defensible mechanism is therefore narrower than the earlier category-removal interpretation: study-aware validation exposed a defective pollutant encoding, not evidence that pollutant or material context should generally be discarded.

### 3.3 Improved pooled transfer remains statistically fragile at study level

For the corrected pollutant representation, RF LOSO R²=0.5960 (RMSE 447.1; MAE 326.0 mg/g) and XGB LOSO R²=0.4645 (RMSE 514.7; MAE 352.1 mg/g). Yet the 95% study-cluster bootstrap R² intervals are [-3.77, 0.824] for RF and [-3.39, 0.799] for XGB. Median per-study MAE is 97.1 mg/g for RF and 86.4 mg/g for XGB, while the valid-study median R² values are negative. The positive pooled R² therefore represents meaningful average transfer across the reconstructed population, not stable universal generalisation across studies.

### 3.4 Domain restriction still blocks the intended engineering claim

Correcting pollutant class does not rescue the original agricultural-waste deployment claim. The strict agricultural subset remains strongly negative under LOSO: RF R²=-1.7407 and XGB=-2.0465 across only four studies. Broader domains have positive pooled performance, but the result is domain-dependent.

**Table II. Corrected-pollutant LOSO by predefined material domain.**

| Domain | Rows / studies | RF R² | XGB R² | Equal-study RF MAE / RMSE | Equal-study XGB MAE / RMSE |
|---|---:|---:|---:|---:|---:|
| Strict agricultural waste | 65 / 4 | **-1.741** | **-2.047** | 780.8 / 818.2 | 767.5 / 801.6 |
| Broad biogenic waste | 92 / 6 | 0.311 | **0.642** | 533.3 / 575.4 | 481.6 / 523.8 |
| Waste-derived carbon | 138 / 7 | 0.545 | 0.520 | 448.1 / 489.6 | 486.1 / 525.6 |

The domain-specific reliability problem is visible in the held-out Alshabib study. Its observed capacities are 270.27 and 199.76 mg/g. In broad-biogenic LOSO, corrected-pollutant RF predicts 1777.18 and 1755.03 mg/g, while XGB predicts 1724.41 mg/g for both observations. Comparable errors persist in the waste-derived-carbon restriction. Thus a globally improved representation can still fail catastrophically when training evidence is narrowed to the intended scientific domain, and close model agreement does not establish correctness.

### 3.5 Reliability diagnostics do not yet justify inverse design

Training-only applicability-distance checks can improve aggregate retained-set metrics under some thresholds, but support status does not consistently order study-level error and remains domain-sensitive. They are therefore retained as domain-shift diagnostics rather than deployment gates. Combined with wide study-cluster uncertainty, catastrophic restricted-domain failures and unstable stacking, the evidence does not support re-enabling the legacy optimisation recommendations.

---

## 4. Discussion

### 4.1 Study-aware validation changed the model-development diagnosis

The first forensic analysis established a severe random-versus-study-aware gap. V3 shows that the gap is not simply evidence that the corpus contains no transferable signal. Family-wise ablation and direct code inspection localized most of the avoidable negative transfer to a faulty derived pollutant class. A target-blind correction preserves pollutant information yet changes RF LOSO R² from 0.0085 to 0.5960 and XGB from 0.1624 to 0.4645. This is a substantive model-development result: the appropriate response to study-aware failure was to repair the representation rather than to defend the random split or indiscriminately delete scientific context.

The study-association diagnostics provide an additional caution. Base-material categories are highly study-associated but their removal barely changes transfer. Therefore high association, high study-ID predictability and poor transfer should not be collapsed into an unsupported causal statement that a feature is a study-identity leak. Harm must be demonstrated through controlled representation tests.

### 4.2 Forward repair is not inverse-design validation

The corrected pollutant representation improves average forward transfer, but inverse design is a stronger claim. An optimiser searches the surrogate and can exploit poorly supported regions; a prescriptive recommendation must also specify the material and pollutant context in which process variables are being optimized. The four-study agricultural domain and the Alshabib restricted-domain failure show that global performance cannot substitute for domain-specific evidence.

A future ID-SEAD should therefore retain scientifically meaningful material/pollutant context using validated descriptors or controlled domain definitions, select representations under study-aware nested validation, and predeclare target-matching objectives and feasibility constraints. Constraint compliance cannot substitute for predictive transfer, and agreement between two models cannot be treated as a safety signal when both can be wrong by approximately 1.5 g/g on a held-out domain.

### 4.3 Evidence required before prescriptive use

Before inverse-design claims are re-enabled, the forward model should demonstrate adequate independent-study depth in the exact deployment domain; stable study-level transfer with uncertainty reported at the study level; fold-local preprocessing and training-only model selection; scientifically valid context descriptors; a reliability/applicability procedure that detects severe held-out failures; independently justified physical constraints; a target-consistent optimisation objective; machine-readable optimisation lineage; and external or experimental confirmation of proposed conditions. The present corpus does not satisfy that gate.

---

## 5. Conclusion

Re-evaluation of ID-SEAD shows that study-aware validation can change not only the estimated performance of a literature-derived ML model but the diagnosis of what should be repaired. The legacy-compatible engineered representation transfers poorly to unseen primary studies. Post hoc family ablation and direct feature audit localize the dominant avoidable loss to a faulty pollutant-class encoding; correcting that encoding without removing pollutant context restores meaningful average study-aware forward performance.

That repair does not validate inverse design. Study-cluster uncertainty remains wide, the intended agricultural-waste domain contains only four independent studies and fails strongly, broader restricted domains retain catastrophic complete-study errors, the Ridge stack is unstable under grouped validation, and available applicability diagnostics are not dependable safety gates. The defensible contribution is therefore a reliability-focused reconstruction: **study-aware validation exposed a correctable pollutant-representation defect, while domain-specific evidence and reliability requirements remain the limiting conditions for any future ID-SEAD inverse-design claim.**

## Data and Code Availability

The reconstructed dataset, provenance maps, modelling/preprocessing scripts, exact-label pollutant audit, row-level predictions, fold manifests, feature dictionary, pinned software environments and V3 GitHub Actions evidence are versioned in the project repository. Frozen V2.1 baseline and V3 post hoc forensic workflows are retained separately so later sensitivity analyses cannot silently overwrite the historical numerical record. The raw literature-extraction spreadsheets and provenance-reconstruction source mappings underlying Dataset V2.1 are maintained separately from the submission-facing validation package.

## References

[1] M. Qiu et al., “Biochar for the removal of contaminants from soil and water: A review,” *Biochar*, vol. 4, art. no. 19, 2022, doi: 10.1007/s42773-022-00146-1.

[2] W. Zhang et al., “Synthesis optimization and adsorption modeling of biochar for pollutant removal via machine learning,” *Biochar*, vol. 5, art. no. 25, 2023, doi: 10.1007/s42773-023-00225-x.

[3] X. Wei et al., “Machine learning insights in predicting heavy metals interaction with biochar,” *Biochar*, vol. 6, art. no. 10, 2024, doi: 10.1007/s42773-024-00304-7.

[4] Y. Ge et al., “A systematic review on machine learning-aided design of engineered biochar for soil and water contaminant removal,” *Front. Soil Sci.*, vol. 5, art. 1623083, 2025, doi: 10.3389/fsoil.2025.1623083. Published correction: doi: 10.3389/fsoil.2025.1659154.

[5] Z. H. Jaffari et al., “Machine-learning-based prediction and optimization of emerging contaminants’ adsorption capacity on biochar materials,” *Chem. Eng. J.*, vol. 466, art. 143073, 2023, doi: 10.1016/j.cej.2023.143073.

[6] P. Yu, Z. Huang, and W. Xie, “Machine Learning-Driven Optimization for Predicting Biochar Adsorption Performance Toward Pb(II) and Cd(II),” *Water*, vol. 18, no. 12, art. 1416, 2026, doi: 10.3390/w18121416.

[7] M. F. Rabbi, “Computational framework for multi-objective optimization of activated biochar properties using machine learning and evolutionary algorithms,” *Sci. Rep.*, vol. 16, art. 22466, 2026, doi: 10.1038/s41598-026-50569-0.

[8] D. R. Roberts et al., “Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure,” *Ecography*, vol. 40, no. 8, pp. 913–929, 2017, doi: 10.1111/ecog.02881.

[9] S. Kapoor and A. Narayanan, “Leakage and the reproducibility crisis in machine-learning-based science,” *Patterns*, vol. 4, no. 9, art. 100804, 2023, doi: 10.1016/j.patter.2023.100804.

[10] G. Varoquaux, “Cross-validation failure: Small sample sizes lead to large error bars,” *NeuroImage*, vol. 180, pp. 68–77, 2018, doi: 10.1016/j.neuroimage.2017.06.061.

[11] L. Breiman, “Random forests,” *Mach. Learn.*, vol. 45, pp. 5–32, 2001, doi: 10.1023/A:1010933404324.

[12] T. Chen and C. Guestrin, “XGBoost: A scalable tree boosting system,” in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, 2016, pp. 785–794, doi: 10.1145/2939672.2939785.

[13] R. Storn and K. Price, “Differential evolution—A simple and efficient heuristic for global optimization over continuous spaces,” *J. Global Optim.*, vol. 11, pp. 341–359, 1997, doi: 10.1023/A:1008202821328.

[14] L. Li, M. Wu, C. Song, L. Liu, W. Gong, Y. Ding, and J. Yao, “Efficient removal of cationic dyes via activated carbon with ultrahigh specific surface derived from vinasse wastes,” *Bioresour. Technol.*, vol. 322, art. 124540, 2021, doi: 10.1016/j.biortech.2020.124540.
