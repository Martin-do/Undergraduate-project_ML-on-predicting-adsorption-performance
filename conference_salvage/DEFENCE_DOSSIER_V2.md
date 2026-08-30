# ID-SEAD Conference Defence Dossier V2

Status: **post-independent-review defence authority**

## Thirty-second defence

ID-SEAD is no longer presented as a validated deployment-ready inverse-design system. The original computational and provenance audit showed that its legacy headline metrics, physical ceiling and recommendation table could not support that claim. The corrected study-aware analysis initially showed severe transfer loss for the reconstructed full-engineered representation. An independent reviewer then challenged whether this was partly caused by study-correlated feature categories. That challenge was correct: removing engineered material/pollutant/context categories substantially improves grouped and LOSO forward prediction. The important result is therefore not simply that grouped validation lowers R²; it is that **study-aware validation exposed a harmful representation choice and changed model development**. Even after that correction, inverse design remains unsupported because the intended agricultural domain is only four studies and fails badly, while a broader promising domain still contains a complete held-out study where RF and XGB are both about 1.5 g/g wrong despite agreeing within about 40 mg/g.

## Numbers to know

- usable target rows: **322**
- primary-confirmed: **307 / 29 studies**
- strict comparable: **273 / 24 studies**
- top 5 studies: **196/273 = 71.8%**
- singleton studies: **8**, not 10
- Kish effective studies by row weight: **7.62**
- dose missing: **61.5%**
- contact time missing: **38.1%**

### Full engineered
- RF random/group/LOSO: **0.904 / 0.027 / 0.008**
- XGB random/group/LOSO: **0.894 / 0.193 / 0.162**

### No identity-adjacent categories
- RF random/group/LOSO: **0.825 / 0.637 / 0.628**
- XGB random/group/LOSO: **0.821 / 0.481 / 0.457**

### Physical numeric only
- RF random/group/LOSO: **0.825 / 0.580 / 0.573**
- XGB random/group/LOSO: **0.820 / 0.496 / 0.469**

### n>=5 study robustness
- category-stripped RF LOSO: **0.616** when holding out only n>=5 studies while training on all other strict studies;
- **0.615** when the entire modelling population is restricted to n>=5 studies.

### Missingness-crossed robustness
Removing dose and contact time:
- no-ID RF grouped/LOSO: **0.652 / 0.655**
- physical RF grouped/LOSO: **0.682 / 0.673**

### Domain gate
- strict agricultural: **65 rows / 4 studies**, RF LOSO about **-1.74**, XGB about **-2.05** under all representations.
- broad biogenic no-ID XGB pooled LOSO: **0.642**, but Alshabib XGB MAE **1489 mg/g**.
- no-ID Alshabib mean RF-XGB disagreement: **40.27 mg/g**, while both models are roughly **1500 mg/g wrong**.

## Likely questions and answers

### 1. Did the independent review invalidate your revised paper?
No. It independently reproduced the qualitative random-versus-grouped effect and agreed that the legacy inverse-design claim should not be defended. It did, however, identify a mechanistic gap: our full engineered representation contained study-correlated context categories. We tested that criticism and changed the manuscript when the evidence showed those categories were harmful to transfer.

### 2. So was your first corrected conclusion also wrong?
It was incomplete. The full-engineered numerical results remain reproducible, but we initially interpreted the extreme transfer loss too broadly. Post-review ablation shows that the corpus contains meaningful transferable signal after representation correction. The V2 manuscript explicitly reports this change rather than hiding it.

### 3. Are you cherry-picking a better feature set after seeing bad results?
The representation ablation is explicitly labelled **post hoc / reviewer-triggered**, not predeclared confirmatory analysis. We report all three representations and do not replace the original corrected baseline. Its purpose is diagnostic: to understand why the full representation failed and whether the conclusion is robust.

### 4. Why does removing material/pollutant categories improve transfer?
Those categories appear useful for distinguishing observations within studies but are correlated with study-specific experimental regimes. Under random splitting, that can improve apparent prediction. Under complete-study holdout, the same representation can produce negative transfer. The result shows why feature selection should be evaluated against the intended independent unit.

### 5. Does that mean material and pollutant context should be removed permanently?
No. That would be an unacceptable inverse-design conclusion. A prescriptive system must specify material and pollutant context. The lesson is that context must be represented in a form that generalises—through controlled domain definitions or validated descriptors—not silently discarded.

### 6. Why is study-aware validation still needed if the corrected representation performs well?
Because we only discovered the harmful representation by evaluating complete studies. Row-random R² remained high for both good and bad representations. The grouped/LOSO test changed which feature representation we would choose.

### 7. Is RF LOSO R²=0.628 now enough for inverse design?
No. It is encouraging forward-prediction evidence on the broad strict corpus, not evidence of safe inverse design. The actual agricultural-waste target domain remains only four studies and fails badly. A broader biogenic domain still has a catastrophic complete-study failure, and no reliability mechanism reliably detects it.

### 8. Why not use the broad-biogenic XGB R²=0.642 for inverse design?
Because it is pooled across only six studies and includes a held-out study with MAE about 1489 mg/g after category removal. A prescriptive optimiser cannot be justified by an average score that hides a catastrophic unseen domain.

### 9. What is the strongest evidence against using model agreement as uncertainty?
In the category-stripped broad-biogenic Alshabib holdout, RF and XGB differ by only about 40 mg/g on average while both are roughly 1.5 g/g wrong. Agreement is therefore not a dependable safety signal.

### 10. Is the 624 mg/g ceiling still invalid after all these changes?
Yes. Its invalidity is independent of the feature-representation question. The reconstructed corpus contains many valid targets above 624 mg/g, with a maximum of 2239 mg/g. It cannot be defended as a universal physical bound.

### 11. Why did you withdraw R²=0.847?
It did not resolve to the inspected authoritative executed notebook state; a stored complete state gives 0.8069/286.29 rather than 0.847/254.1, and the associated constraint selection used nominal final-test information. It is therefore neither a clean frozen result nor an unbiased holdout estimate.

### 12. What about the original Table III?
Its computational lineage is conflicted. The manuscript describes DE and targets 100/200/350 mg/g, while a dedicated reconstruction uses a Monte-Carlo candidate search plus L-BFGS-B and 100/250/400. A recommendation table cannot be defended when its generating procedure is not uniquely traceable.

### 13. Doesn't 61.5% missing dose make the current forward results unreliable?
It is a serious limitation and is now disclosed. However, when dose and contact time are removed entirely, the category-stripped and numeric-only study-aware performance remains similar or improves. That sensitivity means the recovered transfer result is not being created by imputation of those two variables. It does not make the missingness scientifically unimportant for future inverse design.

### 14. Are 24 studies really enough?
They are not 24 equally informative domains. Eight are singletons, the top five contain 71.8% of rows, and the row-weighted Kish effective count is 7.62. We therefore report that imbalance and ran a robustness analysis using only the 12 studies with at least five rows. The category-stripped improvement persists, but more independent studies remain necessary for a mature engineering claim.

### 15. Why not remove the catastrophic Alshabib study?
Because it is exactly the kind of unseen-domain failure that a reliable inverse-design system must survive or reliably flag. Removing it after seeing the error would be post hoc cherry-picking.

### 16. Is stacking still the novelty?
No. Under study-aware validation the Ridge stack is inferior to the strongest tree learners. Stacking is retained only as part of the historical ID-SEAD architecture, not as a validated superiority claim.

### 17. What is the novelty now if grouped CV is already known?
The contribution is not that GroupKFold exists. It is the ID-SEAD case study showing that study-aware evaluation changes the engineering conclusion twice: first by exposing false confidence in the full representation, and then by identifying a representation correction that recovers forward transfer. The work further shows that even the improved predictor fails an inverse-design reliability test because catastrophic complete-study error can coexist with strong model agreement.

### 18. Is this merely a failed-model report?
No. A failed-model report would stop at poor grouped R². This work reconstructs why the original engineering claim was overstated, identifies a concrete feature-representation mechanism, demonstrates a reproducible correction for forward prediction, and then separates that recovery from the stronger evidence required for inverse design.

### 19. Can the corrected results be reproduced?
Yes. The full baseline and post-review revision gate are separate GitHub Actions workflows under pinned environments. The V2 reviewer pack includes the actual modelling/preprocessing source scripts, not only the orchestration wrapper, plus row-level outputs and workflow artifacts.

### 20. What would allow ID-SEAD inverse design to return in a future paper?
A fit-for-purpose, provenance-controlled domain with many independent studies; repeated process-condition variation within comparable material-pollutant systems; context features that survive nested study-aware validation; justified constraints; a target-matching objective; failure-detection/uncertainty procedures that catch complete-study shifts; and independent or laboratory verification of recommended conditions.

## Phrases to avoid

Avoid: “The dataset cannot generalise.”  
Use: “The full engineered representation transferred poorly; representation correction recovered meaningful forward transfer, but domain-specific reliability remains insufficient for inverse design.”

Avoid: “Grouped validation proved the model wrong.”  
Use: “Study-aware validation exposed a feature representation that was not stable across primary studies.”

Avoid: “We fixed ID-SEAD by removing material categories.”  
Use: “Removing unstable categories is a diagnostic correction for forward prediction; future inverse design must reintroduce material/pollutant context in a representation that generalises.”

Avoid: “R²=0.642 means the broad-biogenic model works.”  
Use: “The pooled result is encouraging, but a complete held-out study still fails catastrophically.”

Avoid: “The post-review ablation confirms our original hypothesis.”  
Use: “The ablation was a post hoc reviewer-triggered sensitivity analysis that changed our interpretation.”

## Repository anchors

- `conference_salvage/POST_REVIEW_NUMERIC_SOURCE_OF_TRUTH.md`
- `conference_salvage/INDEPENDENT_REVIEW_RESPONSE_V2.md`
- `conference_salvage/CLAIM_RECONCILIATION_MATRIX_V2.md`
- `conference_salvage/MANUSCRIPT_RECONSTRUCTION_V2.md`
- `conference_salvage/reviewer_revision_gate_v2/`
- `conference_salvage/reproducibility/`
- `validation_v2/PHASE4_DOMAIN_RESTRICTION_FINDINGS.md`
- `validation_v2/PHASE6_UNCERTAINTY_AND_INVERSE_DESIGN_DISPOSITION.md`

## Final defence sentence

**The central engineering lesson is not that study-aware validation always lowers accuracy; it is that study-aware validation reveals which features genuinely transfer, and even a transferable forward predictor is not automatically a reliable inverse-design engine.**
