# Validation-Unit Sensitivity in Literature-Derived Adsorption Machine Learning: A Multi-Dataset Study-Aware Reanalysis

**Manuscript status:** Draft V2 — scientific/editorial refinement of the numerically reconciled frozen-evidence draft

**Authors:** To be finalized before submission

**Affiliations:** To be finalized before submission

## Abstract

Machine-learning models trained on literature-derived adsorption datasets are commonly evaluated at the observation level, even when many observations originate from the same publication or experimental campaign. Such validation can answer an interpolation question while being interpreted as evidence of transfer to an unseen study. We investigated the sensitivity of adsorption-model performance to this distinction using a protocol frozen before the grouped-validation outcomes of external benchmark datasets were examined. Three primary matched corpora were analysed with identical observations, predictors and model specifications under shuffled row-random cross-validation and primary-study GroupKFold validation, with leave-one-study-out (LOSO) analysis where feasible. In a reconstructed heterogeneous adsorption-capacity corpus (273 observations, 24 studies), XGBoost decreased from row-random R² = 0.8936 to study-grouped R² = 0.1929 and LOSO R² = 0.1624. In a primary-study-disjoint biochar–dye corpus (624 observations, 17 studies), CatBoost decreased from R² = 0.9360 to 0.1096 (LOSO R² = 0.0594). In a second primary-study-disjoint corpus of ammonia-N adsorption on biochar (409 observations, 7 studies), CatBoost decreased from R² = 0.8837 to −0.0581 (LOSO R² = −0.0547). The two Liu corpora had non-overlapping contributing primary-study DOI sets but shared a broader data-curation/author-team lineage. Reproduction diagnostics recovered the high conventional random-performance regimes of the public benchmark workflows before changing the validation unit, reducing the likelihood that the grouped-performance decreases were caused by failed model reconstruction. A lineage-overlapping sensitivity dataset showed a smaller reduction, while independently published evidence on methylene-blue adsorption onto clays reported conventional-to-grouped performance of approximately 0.79 to 0.66. Conversely, a publication-separated biochar–heavy-metal study retained test R² = 0.99, demonstrating that source-aware evaluation does not necessarily imply poor performance. These results show that the scientific unit of validation can materially change the estimated generalisation performance of literature-derived adsorption models. We recommend reporting both observation count and independent-study count, preserving row-level provenance, fitting preprocessing within validation folds, and explicitly aligning the validation unit with the intended prediction claim.

**Keywords:** adsorption; machine learning; cross-validation; data leakage; group cross-validation; domain shift; biochar; provenance; reproducibility; generalisation

---

## 1. Introduction

Machine learning (ML) has become increasingly common in adsorption research because it can represent nonlinear relationships among adsorbent properties, pollutant characteristics and operating conditions without requiring a single mechanistic equation to describe every interaction. Literature-derived datasets are particularly attractive: a single modelling table can contain hundreds or thousands of adsorption observations assembled from multiple publications, substantially increasing the apparent sample size available for model development. Recent adsorption studies have reported strong predictive performance using tree ensembles, boosting methods, neural networks and related algorithms, often with coefficient-of-determination values above 0.90.

The statistical meaning of those performance estimates depends, however, on what constitutes an independent prediction unit. Literature-derived adsorption tables are usually hierarchical. Multiple rows may originate from the same paper, adsorbent batch, material preparation, laboratory protocol or experimental campaign. Rows from a common study can share material-specific fingerprints, measurement procedures, target ranges and unreported laboratory effects. Consequently, randomly assigning individual rows to training and validation sets can place observations from the same scientific source in both partitions. The resulting estimate can be entirely relevant when the intended task is interpolation to additional observations from systems already represented in the training mixture. It does not, by itself, estimate the stronger task of predicting a completely unseen primary study.

This issue is not unique to adsorption ML. Cross-validation literature has long shown that hierarchical dependence must be considered when the prediction target concerns new groups rather than new observations from existing groups. Blocking or grouping should therefore be chosen according to the intended prediction task rather than treated as a universally superior replacement for random cross-validation. Recent methodological discussion in biochar ML has likewise identified data leakage and inadequate splitting as threats to generalisability. The unresolved question for literature-derived adsorption modelling is therefore not whether grouped validation exists, but how strongly performance estimates change when the scientific unit of validation is altered while the modelling problem itself is held fixed.

A related reproducibility issue is that a low score under study-aware validation can be dismissed if the original high-performance pipeline cannot first be reproduced. A stronger test is a matched reanalysis: recover the original or public modelling population, reconstruct source provenance, reproduce the conventional random-performance regime where executable evidence permits, and then alter only the validation unit while holding observations, predictors and model specification constant. This design distinguishes a validation-unit effect from a general failure to reconstruct the published model.

The present study applies that approach across multiple literature-derived adsorption corpora. The analysis was governed by a protocol frozen before external grouped-validation outcomes were inspected. The primary evidence comprises (i) a deeply reconstructed adsorption-capacity corpus with 24 primary studies, (ii) a public biochar–dye corpus reconstructed to 17 high-confidence primary sources, and (iii) an ammonia-N/biochar corpus recovered from historical repository data and reconstructed to seven contributing primary studies. A fourth, lineage-overlapping dye/activated-carbon dataset is retained as a sensitivity analysis but is not counted as an independent replication. We further compare our results with an independently published random-versus-grouped adsorption study and with a positive publication-separated study in which strong predictive performance survives source-aware validation.

The central research question is:

> **How sensitive are performance estimates in literature-derived adsorption machine learning to the scientific unit at which observations are separated for validation, and when does row-level interpolation fail to represent transfer to an unseen primary study?**

We test four propositions. First, row count and independent-study count represent different sample-size concepts in literature-derived data. Second, row-random and study-aware validation estimate different generalisation targets. Third, matched experiments can reveal large differences between these targets without changing the modelling population. Fourth, the magnitude of this difference is dataset-dependent rather than universal. The contribution is therefore a reproducible assessment of **claim–validation alignment**, supported by provenance reconstruction, source-independence audits, matched validation, executable-pipeline reproduction, and explicit counterevidence.

---

## 2. Materials and methods

### 2.1 Study design and frozen protocol

The study was designed as a multi-dataset reanalysis rather than a model-development competition. Before the grouped-validation outcomes of the external benchmark datasets were examined, a protocol was frozen specifying dataset eligibility, grouping hierarchy, matched-validation rules, preprocessing requirements, model policy, metrics and outcome-neutral reporting. Eligible matched datasets had to contain observations from at least two scientifically defensible higher-level groups, provide or permit lawful recovery of the modelling data, and retain or permit defensible reconstruction of the grouping variable. Datasets were not removed because grouped performance remained high, decreased only modestly, or contradicted the expected direction.

The analysis distinguishes three levels of independence: observation-level independence, primary-study or campaign independence, and corpus-curation or research-team independence. Two datasets can therefore contain disjoint primary studies while still sharing a broader author or data-curation lineage. This distinction was used explicitly when classifying the evidence.

The primary comparison was always matched. Within a dataset/model pair, the random and grouped arms used the same observations, predictor definitions and fixed model specification. No model was separately retuned to improve one validation arm. Data-dependent preprocessing was fitted only on the training portion of each fold for the matched analyses. Where a published or public workflow had fitted transformations globally, that pipeline was reproduced separately as a **published-pipeline diagnostic** and was not mixed with the fold-safe matched comparison.

### 2.2 Evidence hierarchy and corpora

#### 2.2.1 Dataset A: reconstructed heterogeneous adsorption-capacity corpus (V2.1)

The first corpus originated from a literature-derived adsorption dataset that underwent a dedicated provenance audit. The archived source contained 325 rows, of which 322 had usable targets. Primary-study provenance was confirmed for 307 rows spanning 29 reconstructed studies. Fifteen rows remained unresolved and were not assigned guessed study identifiers. A strict comparability gate retained **273 observations from 24 primary studies** for the main validation analysis. The gate excluded target-incompatible or data-quality-flagged rows independently of model residuals.

The same 273 observations were used for shuffled five-fold and primary-study GroupKFold validation. Linear regression, support-vector regression, random forest (RF), XGBoost (XGB) and a historical ridge-stacked ensemble were evaluated. Because the present paper concerns validation-unit sensitivity rather than a novel model, XGB and RF are emphasized as representative tree models, while the stack is retained only as a historical diagnostic comparator.

#### 2.2.2 Dataset B: Liu et al. biochar–dye corpus

The second corpus was derived from the public workbook associated with Liu et al. (2025), which reported 685 collected literature observations, removal of 17 high-capacity observations, and 668 observations used for modelling. The workbook included a literature-source sheet containing 20 DOIs but did not retain an explicit row-level source identifier in the modelling table.

A deterministic provenance reconstruction used the ordered source list, contiguous row blocks, decoded dye descriptors, material fingerprints, and primary-paper material/dye scope. A malformed 17-row spreadsheet tail exposed by a plain pandas read was quarantined because it could not be reconciled with the logical adsorption table. The primary strict population retained **624 observations from 17 high-confidence primary studies**. An extended sensitivity population retained 668 observations from 19 studies by additionally including 44 medium-confidence rows. One listed source was assigned zero rows rather than inferred without evidence. The largest strict-set study contributed 110/624 observations (17.63%).

The original paper identified CatBoost as its strongest model family. The matched analysis therefore included fixed RF500, XGB500 and CatBoost500 models. The public feature representation was followed after excluding O/C, PV and E as in the reconstructed model pipeline. Training-fold preprocessing was applied within each random or grouped fold.

#### 2.2.3 Dataset C: Liu et al. ammonia-N/biochar corpus

The third corpus corresponded to Liu et al. (2025), which reported 417 literature-derived observations and an ordinary random 80:20 split. The repository currently linked by the article no longer contains its raw modelling workbook. Git history showed, however, that `Original.xlsx` had been explicitly deleted in December 2024, and the exact pre-deletion workbook remained recoverable from the parent commit. The recovered workbook contained a `Full` sheet with **417 rows**, matching the article’s reported collected population.

The public CatBoost notebook applies a `Q <= 10` target gate. Reconciliation of the historical workbook and executable code produced a final **409-row** modelling population. Primary provenance was reconstructed to **seven contributing studies** using the ordered literature ledger and source-specific material/feedstock blocks. The largest study contributed 180/409 observations (44.01%), highlighting the difference between row count and independent-study count. Three listed bibliography entries were assigned zero model rows, and a source present in an earlier raw sheet but absent from the executable model population was likewise not forced into the final mapping.

The seven contributing primary-study DOIs do not overlap the 29-study Dataset A bibliography or the contributing primary sources of Dataset B. Datasets B and C are thus independent at the underlying primary-study level, although they share a broader dataset-curation/author-team lineage. This limitation is explicitly retained in the interpretation.

Matched models were RF500, XGB500 and CatBoost500. K-nearest-neighbour imputation, Box–Cox transformation and scaling were fitted within each training fold. The same 409 rows and predictor definition were used in both validation arms.

#### 2.2.4 Moosavi et al. lineage sensitivity

Moosavi et al. (2021) compiled 350 dye-adsorption observations on agricultural-waste activated carbon. From the official distributed supplement, 344 numbered rows could be recovered directly; six rows were absent from the source PDF and were not imputed. Twelve source-study groups were recoverable.

Although this dataset permits a clean random-versus-grouped comparison, a later source-lineage audit showed that all 344 recoverable observations arise from primary-study lineage already represented in the historical lineage of Dataset A. It is therefore retained only as a **lineage-overlapping sensitivity analysis** and is excluded from the independent-replication count.

### 2.3 Literature comparators

Two external studies were retained to contextualise the matched reanalyses without selectively focusing on performance collapse.

Aguiar and Kasemodel (2026) independently compiled 1,098 methylene-blue/clay adsorption experiments from 38 studies and directly compared conventional validation with GroupKFold by source study. Their largest model used 726 observations from 23 studies and retained grouped R² of approximately 0.66 from conventional R² of approximately 0.79. Because these are the authors’ published results rather than our rerun, this study is classified as **independent cross-team published corroboration**, not as a primary matched replication generated in the present work.

Huang et al. (2026) compiled 452 adsorption-capacity records for primarily Cu(II) and Pb(II) adsorption by biochar. Their train/test partition was performed at the literature-source level, all samples from a publication were kept exclusively in train or test, and preprocessing parameters were derived from the training data. XGBoost achieved test R² = 0.99 with training five-fold CV R² = 0.92 ± 0.04. The raw modelling table is available only on request, so the result was not independently rerun. This study serves as a deliberately positive source-aware comparator.

### 2.4 Provenance reconstruction and grouping rules

Study identifiers were never assigned from model performance. The preferred provenance hierarchy was: (1) explicit row-level primary-study identifier; (2) explicit bibliographic/reference field; (3) deterministic experimental block or campaign mapping supported by source metadata; and (4) reconstructed study mapping supported jointly by material, pollutant, processing and experimental signatures plus primary bibliographic evidence. Ambiguous rows were excluded from primary grouped claims or retained only in a declared sensitivity set.

Cross-corpus source overlap was audited to avoid double counting. This procedure led to reclassification of the Moosavi dataset from an apparent independent replication to a lineage sensitivity. It also established that the two Liu-derived matched corpora contain disjoint contributing primary-study DOI sets despite their shared broader research-team lineage.

### 2.5 Validation designs

#### 2.5.1 Row-random comparator

The common comparator was shuffled five-fold cross-validation with a fixed seed. This validation allows rows from a primary study to occur in both training and validation folds. It therefore estimates predictive performance for additional observations drawn from the row-level mixture represented in the corpus.

#### 2.5.2 Primary-study GroupKFold

The study-aware comparator used GroupKFold with reconstructed primary study as the grouping variable. No primary study contributed rows to both training and validation within a fold. The resulting estimate targets transfer to an unseen study under the empirical domain represented by the remaining training studies.

#### 2.5.3 Leave-one-study-out robustness

Where group counts permitted, Leave-One-Group-Out validation was used as a robustness analysis. Predictions from held-out studies were pooled to compute R², RMSE and MAE, while study-level errors were retained where available because pooled scores can be disproportionately influenced by large or high-capacity studies.

### 2.6 Reproduction of conventional random-performance regimes

Before interpreting study-aware degradation, we tested whether the high conventional performance associated with public benchmark workflows could be recovered.

For the Liu biochar–dye corpus, an optimized-style reconstruction following the executable random pipeline achieved R² = 0.978611 on the 685-row executable sheet and R² = 0.966277 on the logical 668-row population, approaching the published CatBoost R² = 0.9880. These diagnostic scores are not the matched comparison and include the preprocessing behaviour of the public workflow.

For the ammonia-N corpus, a deliberately public-style reconstruction applied global KNN imputation, Box–Cox transformation and standardisation before the random 80:20 split. Fixed CatBoost500 achieved test R² = 0.932643 and RMSE = 0.538641, nearly identical to the article’s reported R² = 0.9329 and RMSE = 0.5378. The fold-safe matched analysis was performed separately.

For the Moosavi lineage sensitivity, the reconstructed five-variable RF random-CV result (R² = 0.8081) closely matched the paper’s reported test R² of approximately 0.81. Together, these checks provide evidence that the grouped-performance changes are not simply artefacts of failing to reconstruct a high-performing random-validation regime.

### 2.7 Performance metrics and interpretation

For each matched dataset/model pair, we report row-random R², study-grouped R², ΔR² = R²_random − R²_grouped, RMSE and MAE for both arms, and LOSO R² where available. Observation count, study count and largest-study share are reported as corpus-structure descriptors.

R² differences are treated descriptively rather than as a formal cross-dataset meta-analysis because target scales, feature spaces, study counts and experimental domains differ. Negative grouped R² indicates performance below the fold-level or pooled mean-reference benchmark under the corresponding held-out-study task; it is not interpreted as evidence that adsorption is intrinsically unpredictable.

The term **validation gap** refers to the within-corpus difference between matched row-random and study-aware estimates. It should not be read as a causal estimate of “leakage” alone: domain shift, study imbalance, omitted descriptors and laboratory-specific effects may all contribute.

### 2.8 Reproducibility and evidence locking

All primary numerical claims are generated from deterministic registry files and CI-verified workflows. The multi-dataset protocol and evidence freeze are versioned in the repository. After the evidence freeze, additional datasets are not added to the primary analysis merely because they might strengthen the observed direction. Any post-freeze addition requires a documented methodological reason before its grouped result is inspected. Figure 1 summarizes the resulting provenance and evidence hierarchy used for interpretation.

---

## 3. Results

### 3.1 Row count and independent-study count differ substantially

The three primary matched corpora contained 273, 624 and 409 observations, respectively, but only 24, 17 and 7 contributing primary studies. This difference was most pronounced in the ammonia-N corpus, where one primary study contributed 44.01% of all modelled observations. The largest study in the strict Liu dye corpus contributed 17.63% of observations. Dataset A contained more independent studies (24) despite having fewer rows than either external matched corpus.

This structure demonstrates why literature-derived row count is not equivalent to the number of independent experimental systems. A 409-row table can effectively contain only seven higher-level units for the prediction question “how well does the model transfer to a study not represented during training?” Conversely, row-level validation can still be informative when the target is additional observations from the mixture of studies already represented.

Provenance reconstruction also changed the evidentiary classification of one dataset. The 344 recoverable Moosavi observations could be grouped into 12 source references, but all recoverable rows were traced to source-study lineage already represented in Dataset A’s historical lineage. Treating Moosavi as a fourth independent replication would therefore have double counted primary evidence.

### 3.2 High conventional random-performance regimes were reproducible

The public-pipeline diagnostics reproduced strong random-validation performance before the validation unit was changed. For the Liu dye corpus, the optimized-style public reconstruction reached R² = 0.9786 on the executable 685-row sheet and 0.9663 on the logical 668-row population, compared with the published CatBoost R² = 0.9880. For the ammonia-N corpus, the public-style random holdout achieved R² = 0.932643 and RMSE = 0.538641, nearly reproducing the published R² = 0.9329 and RMSE = 0.5378. The Moosavi five-variable RF reconstruction produced random-CV R² = 0.8081, closely matching the reported R² ≈ 0.81.

These diagnostics establish an important sequence: the public/random performance regimes were recoverable first; the scientific grouping unit was then altered in matched, fold-safe comparisons. The subsequent grouped decreases therefore cannot be attributed simply to an inability to reproduce the original model family or data population.

### 3.3 Matched study-aware validation materially reduced performance in all three primary reanalyses

Table 3 and Figure 2 summarize the representative fixed-model comparisons. In Dataset A, XGB decreased from row-random R² = **0.8936** to primary-study GroupKFold R² = **0.1929**, a difference of **0.7007**. Pooled study-LOSO R² was **0.1624**. RF decreased from 0.9042 to 0.0265, while the historical ridge stack decreased from 0.9027 to −0.5566. Thus, the stacked model’s strong row-random score did not translate into superior unseen-study performance.

In the strict Liu dye corpus, CatBoost500 decreased from **0.935977** under row-random five-fold validation to **0.109642** under primary-study GroupKFold, giving ΔR² = **0.826335** and LOSO R² = **0.059409**. The same qualitative finding was observed for RF500 (0.930377 to −0.339908) and XGB500 (0.938244 to −0.036089). In the extended 668-row provenance sensitivity, CatBoost remained stable at 0.939852 random versus 0.105311 grouped, while XGB was more sensitive to inclusion of the medium-confidence blocks.

In the ammonia-N corpus, CatBoost500 decreased from **0.883650** to **−0.058128**, ΔR² = **0.941778**, with LOSO R² = **−0.054673**. RF500 decreased from 0.837380 to −0.420734, and XGB500 from 0.851681 to −0.640524. CatBoost random RMSE increased from 0.674666 to 2.034582 under study grouping, and MAE increased from 0.423072 to 1.417852.

The magnitude of the validation gap differed across models and datasets, but in all three primary matched corpora the estimate obtained after withholding entire primary studies was substantially lower than the row-random estimate.

### 3.4 Study-aware performance was heterogeneous rather than uniformly absent

Figures 3 and 4 place the representative validation gaps and LOSO results alongside corpus structure. Dataset A retained weak positive unseen-study signal under its strongest grouped tree model: XGB GroupKFold R² = 0.1929 and LOSO R² = 0.1624. Pre-specified Dataset A sensitivities were similar: condition-level-only grouped XGB R² = 0.1377; conventional aqueous-capacity-only grouped XGB R² = 0.1329 and LOSO R² = 0.1851. These values are substantially below the corresponding row-random values near 0.89, but they are not equivalent to zero predictive structure in every held-out study.

The Liu dye corpus also showed model-dependent grouped signal. Strict XGB500 grouped R² was −0.0361 while CatBoost500 reached 0.1096; in the extended provenance sensitivity, XGB500 reached 0.3414 but CatBoost remained approximately 0.105. This sensitivity to provenance boundaries reinforces the need to report source-reconstruction decisions rather than presenting a single grouped score without context.

The ammonia-N corpus produced the weakest grouped results and also had the fewest independent studies and the greatest study imbalance. With only seven contributing primary studies and 44% of rows from one source, each group holdout constitutes a substantial domain perturbation. This association is descriptive; the present number of corpora is insufficient to attribute the magnitude of ΔR² causally to study count or imbalance.

### 3.5 The lineage sensitivity showed a smaller validation gap

Using Moosavi et al.’s recoverable 344-row supplementary dataset and the published-style nine-variable RF specification, row-random R² was 0.8931 and primary-reference GroupKFold R² was 0.4665, with LOSO R² = 0.4629. The five-selected-variable model changed from 0.8081 to 0.4810. These grouped values are markedly higher than those of the three primary representative cases.

However, this result cannot be counted as independent replication because the underlying primary sources overlap Dataset A’s lineage. Its value is instead methodological: it demonstrates that the same study-aware procedure can retain moderate cross-study performance in a more restricted, lineage-related dataset. This again argues against treating grouped validation as a mechanism that automatically produces low R².

### 3.6 Independent published evidence supports both a validation gap and its boundary conditions

Aguiar and Kasemodel (2026) provide cross-team corroboration in a different adsorbent domain. Their largest random-forest model, containing 726 methylene-blue/clay experiments from 23 studies, decreased from conventional cross-validation R² ≈ 0.79 to study-grouped R² ≈ 0.66. Smaller or more feature-restricted models showed larger reductions, including negative grouped values in some cases. The retained R² ≈ 0.66 is scientifically important: study-aware evaluation can reduce optimistic interpolation estimates while still preserving useful transferable signal.

Huang et al. (2026) provide a stronger positive boundary condition. Their 452-record biochar/heavy-metal dataset was separated at the publication level before modelling, with preprocessing derived from the training partition. XGB achieved test R² = 0.99 and training five-fold CV R² = 0.92 ± 0.04. Although the raw modelling table was not publicly available for an independent rerun, the published method and result show that strong adsorption prediction can survive source-aware separation in a coherent dataset.

Together, the matched reanalyses and comparators support a conditional conclusion rather than a universal one: the validation unit can have a large effect, but the magnitude depends on the corpus and prediction domain.

---

## 4. Discussion

### 4.1 Row-random interpolation and unseen-study transfer are different estimands

Figure 5 summarizes the claim–validation distinction. The main finding is not that random cross-validation is intrinsically invalid. It is that its interpretation must match the unit being randomized. When individual rows are randomized, validation observations can share a primary publication, material family, preparation route, measurement protocol or other study-level characteristics with training observations. This design can provide a legitimate estimate for predicting additional rows drawn from the same empirical mixture. It does not isolate the question of whether a model will transfer to an unseen primary study.

Across the three primary matched corpora, changing only the validation unit produced large decreases in R² for representative models. The effect was observed even after public high-performance regimes were independently recovered. This sequence matters because it directly addresses a common alternative explanation: the grouped model did not perform poorly merely because the published random model could not be reconstructed.

The distinction is especially relevant when manuscript language moves from “the model predicts held-out observations” to stronger claims such as robustness across materials, broad generalisation, or applicability to new adsorption systems. Those stronger claims imply a higher-level prediction target and therefore require a validation design in which the corresponding higher-level units are genuinely withheld.

### 4.2 Why can the validation gap be large?

Several non-exclusive mechanisms can generate the observed gaps. First, repeated rows from the same study may share material descriptors and preparation conditions that make nearby observations easier to interpolate. Second, source studies often occupy characteristic target ranges; a random split preserves portions of those ranges in both training and validation. Third, laboratory and protocol effects can be encoded indirectly through measured descriptors or remain completely unmeasured. Fourth, adsorption datasets frequently omit potentially important physicochemical variables, so a flexible model may rely more heavily on source-specific combinations of the available features. Fifth, study imbalance means a small number of large studies can dominate row-level fitting and evaluation.

The present analyses do not isolate these mechanisms causally, and the term “leakage” should therefore be used carefully. The matched ΔR² quantifies **validation-unit sensitivity**, not the proportion of performance caused by any single dependence mechanism. Study-aware validation also creates a harder extrapolation problem when a held-out study occupies a part of predictor space that is poorly represented elsewhere. That difficulty is scientifically relevant if unseen-study transfer is the intended task, but it should not be confused with an error in GroupKFold itself.

### 4.3 Provenance is part of the modelling method

A central practical lesson from this work is that provenance cannot be treated as optional spreadsheet metadata. The original row count of Dataset A did not reveal how many independent primary studies were represented. The Liu dye workbook listed source DOIs but did not preserve row-level study identity, requiring substantial reconstruction. The ammonia-N raw workbook had been removed from the current repository and was recoverable only from Git history. Moosavi initially appeared to provide an additional replication until a source-lineage audit showed that its observations substantially duplicated Dataset A’s historical evidence base.

These examples show that a literature-derived ML dataset should retain a source hierarchy from the moment of curation. At minimum, each observation should be traceable to a primary publication and, where relevant, to an experimental campaign, material batch or other higher-level grouping unit. Provenance supports not only citation integrity but also validation design, duplicate detection, external-validation independence and reproducibility.

### 4.4 What the results do not establish

Several overstatements should be avoided.

First, the results do not show that all published adsorption ML models are invalid. The Huang comparator and Aguiar’s grouped results demonstrate that useful or excellent source-aware performance can occur.

Second, the results do not show that random splitting is always inappropriate. For interpolation among represented systems, it may be the relevant estimand. The methodological problem arises when a row-random estimate is used to support a claim about unseen studies or new scientific systems without corresponding group separation.

Third, negative GroupKFold or LOSO R² values do not prove that the underlying adsorption process is unpredictable. They show that, given the available predictors, data coverage, corpus structure and training studies, the fitted model does not outperform the reference prediction for the corresponding held-out-study task.

Fourth, the present study does not establish that one algorithm family is universally more transferable. Model rankings changed across corpora and validation designs. The historical stacked model in Dataset A is particularly instructive: its row-random R² of 0.9027 was comparable with RF and XGB, yet its grouped R² was −0.5566. Complexity or ensembling therefore cannot substitute for validation matched to the scientific claim.

Finally, GroupKFold is not itself a guarantee of deployment validity. A study-held-out model can still fail under new pollutant chemistry, new adsorbent classes, different water matrices, scale-up conditions or other shifts not represented by the grouping variable. Validation should be hierarchical and task-specific.

### 4.5 Reporting recommendations for literature-derived adsorption ML

Based on the empirical findings and provenance audits, we recommend that literature-derived adsorption-ML studies report the following alongside conventional performance metrics:

1. **Observation count and independent-group count.** Report both total rows and the number of primary studies, campaigns or other scientific groups relevant to the prediction claim.
2. **Row-level provenance.** Preserve primary-source identifiers in the modelling table or a one-to-one provenance ledger.
3. **Group-size distribution.** Report at least the largest-group share and preferably the full rows-per-study distribution.
4. **Claim–validation alignment.** State whether the intended task is interpolation among represented systems, transfer to an unseen study, transfer to a new material/pollutant class, or another target.
5. **Fold-safe preprocessing.** Fit imputation, scaling, transformation and data-dependent feature selection only on training data within each validation fold.
6. **Matched validation when multiple estimands matter.** Where scientifically useful, report both row-random and group-aware performance using the same observations, predictors and model specification.
7. **LOSO or per-study diagnostics.** Pooled metrics should be complemented by study-level errors because large studies can dominate pooled statistics.
8. **External-source independence.** An external dataset should be checked for shared primary studies or curation lineage before being described as independent validation.
9. **Reproducible source mapping.** If study IDs must be reconstructed, the mapping rules and unresolved cases should be published rather than silently inferred.
10. **Bounded generalisation language.** Performance should be described for the validation task actually tested; deployment or universal claims require evidence beyond a high row-random R².

These recommendations are intended to improve interpretability of performance claims rather than prescribe a single validation scheme for every adsorption study.

---

## 5. Limitations

The study has several limitations. First, the primary matched evidence contains three corpora rather than a large systematic sample of all adsorption-ML datasets. The work should therefore be interpreted as a multi-dataset empirical reanalysis, not as a meta-analytic estimate of the average validation gap across the field.

Second, although the two external Liu corpora contain disjoint primary-study DOI sets, they share a broader data-curation and author-team lineage. This reduces their independence at the research-practice level. The Aguiar study provides cross-team corroboration, but its raw matrix was not independently rerun in this project.

Third, source identity had to be reconstructed for parts of the external matched datasets. The Liu dye primary analysis deliberately uses only 624 high-confidence mapped rows; the 668-row population is reported as a sensitivity analysis. Such reconstruction is necessarily weaker than source IDs preserved prospectively by the original data curators.

Fourth, the ammonia-N corpus contains only seven model-contributing studies and is strongly imbalanced. Its negative grouped scores therefore describe a particularly demanding unseen-study task and should not be generalized to better-covered ammonia-N datasets.

Fifth, the corpora differ in target units, feature spaces, adsorbent/pollutant domains and model pipelines. Within-corpus paired differences are therefore the primary evidence; absolute RMSE and MAE are not directly comparable across all datasets, and the small number of corpora does not support causal regression of ΔR² against corpus descriptors.

Sixth, publication-level grouping is only one level of the data hierarchy. Multiple materials or campaigns may exist within one publication, and different publications may originate from the same laboratory or research programme. Conversely, withholding an entire paper may produce predictor-space extrapolation beyond the intended deployment setting. The correct grouping unit must therefore follow the scientific claim.

Finally, the positive Huang comparator could not be independently rerun because the 452-row modelling dataset is available only on request. It is retained as published methodological counterevidence rather than computational replication.

---

## 6. Conclusions

Literature-derived adsorption datasets can contain hundreds of observations while representing far fewer independent scientific studies. Across three matched corpora, strong row-random performance decreased substantially when entire primary studies were withheld, even though high conventional random-performance regimes could first be reproduced from public or recoverable workflows. The representative changes were XGB R² 0.8936→0.1929 in a 273-row/24-study heterogeneous corpus, CatBoost R² 0.9360→0.1096 in a 624-row/17-study biochar–dye corpus, and CatBoost R² 0.8837→−0.0581 in a 409-row/7-study ammonia-N/biochar corpus.

These results do not imply that adsorption ML cannot generalise or that random validation is inherently wrong. Independent published evidence shows both moderate performance reduction under study grouping and excellent performance under publication-level separation. The central conclusion is instead that **validation design defines the generalisation claim that a performance metric can support**.

For literature-derived adsorption ML, provenance should therefore be considered part of the modelling method. Preserving primary-source identity, reporting independent-study counts, applying fold-safe preprocessing, and matching the validation unit to the intended prediction target are necessary for distinguishing interpolation within represented systems from transfer to genuinely unseen studies. Future model development should prioritize broader independent-study coverage, coherent domain definition and informative physicochemical descriptors before interpreting improvements in row-random R² as evidence of transferable engineering performance.

---


> **Figure-caption source:** Final Draft V2 figure captions are maintained in `paper1/manuscript/FIGURE_CAPTIONS_V1.md` and correspond to deterministic CI-rendered figures.

## Data and code availability

The reconstructed datasets, provenance ledgers, validation scripts, deterministic result registries and CI workflow records used for the present analysis are maintained in the project repository. The submission version will provide a persistent archived release and a machine-readable mapping from each manuscript table/figure to its numerical source-of-truth file. Third-party datasets are redistributed only where permitted; otherwise, retrieval instructions, hashes and source references are provided.

## Author contributions

To be completed after authorship is finalized.

## Funding

To be completed before submission.

## Competing interests

To be completed before submission.

## Acknowledgements

To be completed before submission.

---

## References — verified core set for Draft V2

Aguiar, L. G., & Kasemodel, M. C. (2026). Application of random forest regression in modeling the adsorption of methylene blue onto clays. *Neural Computing and Applications, 38*, 496. https://doi.org/10.1007/s00521-026-12200-1

Cahyana, D., & Jang, H. J. (2025). Addressing data handling shortcomings in machine learning studies on biochar for heavy metal remediation. *Journal of Hazardous Materials, 491*, 137887. https://doi.org/10.1016/j.jhazmat.2025.137887

Huang, X., Bai, X., Yang, Y., Li, W., & Xu, D. (2026). Machine Learning-Based Prediction and Optimization of Heavy Metal Adsorption Performance of Biochar. *Forests, 17*(3), 326. https://doi.org/10.3390/f17030326

Liu, C., Balasubramanian, P., Nguyen, X. C., An, J., Praneeth, S., Zhang, P., & Huang, H. (2025). Enhanced machine learning prediction of biochar adsorption for dyes: Parameter optimization and experimental validation. *Carbon Research, 4*, 46. https://doi.org/10.1007/s44246-025-00213-9

Liu, C., Balasubramanian, P., An, J., & Li, F. (2025). Machine learning prediction of ammonia nitrogen adsorption on biochar with model evaluation and optimization. *npj Clean Water, 8*, 13. https://doi.org/10.1038/s41545-024-00429-z

Moosavi, S., Manta, O., El-Badry, Y. A., Hussein, E. E., El-Bahy, Z. M., Mohd Fawzi, N. F. B., Urbonavičius, J., & Moosavi, S. M. H. (2021). A Study on Machine Learning Methods’ Application for Dye Adsorption Prediction onto Agricultural Waste Activated Carbon. *Nanomaterials, 11*(10), 2734. https://doi.org/10.3390/nano11102734

Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*, 913–929. https://doi.org/10.1111/ecog.02881

> **Draft-reference note:** The full submission bibliography will additionally include all primary studies used in provenance reconstruction and any adsorption-ML papers cited in the finalized literature-practice context. Those entries will be imported only after DOI/publisher verification; Draft V2 intentionally does not invent incomplete bibliographic metadata.
