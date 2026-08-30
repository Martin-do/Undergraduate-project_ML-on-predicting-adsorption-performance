# ID-SEAD Conference Restructure Blueprint V2

Status: **post-independent-review manuscript architecture**

## Preferred title

**ID-SEAD Revisited: Study-Aware Validation, Feature-Representation Sensitivity and Reliability Limits in Adsorption Inverse Design**

Alternative:

**From Apparent Accuracy to Reliable Inverse Design: A Provenance- and Feature-Robustness Audit of ID-SEAD**

## Central research question

**When a literature-derived adsorption surrogate is evaluated by complete primary study rather than by random rows, how much of its apparent performance is genuine transfer and how much depends on the chosen feature representation—and what does that imply for inverse design?**

## Contribution statement

The paper is no longer simply a demonstration that random row splits overestimate transfer. The ID-SEAD-specific contribution is:

1. forensic reconstruction of a real inverse-design pipeline whose legacy claim was stronger than its computational evidence;
2. a matched row-random versus study-aware evaluation showing severe negative transfer for the original full-engineered representation;
3. a reviewer-triggered feature-representation ablation showing that the extreme collapse is partly caused by study-correlated material/pollutant/context categories;
4. recovery of meaningful forward transfer after removing those categories, including in n>=5-study sensitivity analyses;
5. demonstration that predictive recovery still does not establish safe inverse design because the intended agricultural domain fails, catastrophic complete-study errors persist, and model agreement does not reliably flag them.

## Required transparency

The feature-representation ablation, n>=5 sensitivity and crossed missingness sensitivity were performed **after independent review**. They must be labelled as reviewer-triggered/post-review sensitivity analyses, not predeclared confirmatory tests.

## Manuscript structure

### 1. Introduction

- adsorption ML and inverse design;
- inverse design is higher-risk than ordinary forward prediction;
- literature-derived rows are clustered within studies;
- conventional validation can also reward study-correlated feature representations;
- introduce ID-SEAD as the concrete engineering case;
- narrow novelty: not “first ML optimization,” but representation-aware study validation and inverse-design reliability.

### 2. Legacy ID-SEAD and forensic reconstruction

- LR/SVR/RF/XGB → Ridge stack architecture;
- legacy constraint/optimization concept;
- numerical-lineage defects:
  - 0.847 not frozen/reproduced;
  - test-informed constraint selection;
  - QMAX=624 invalid;
  - Table III optimizer/target conflict;
- these findings motivate corrected evaluation, but the paper avoids misconduct language.

### 3. Data and validation protocol

- V2.1: 322 usable; 307/29 primary-confirmed; strict 273/24;
- grouped by `primary_study_id_v21`;
- fold-safe preprocessing;
- exclusion of `removal_percent`, source/study identifiers;
- disclose missingness:
  - dose 61.5%; contact time 38.1%; SA/PV 10.6%;
- disclose study imbalance:
  - top 5=71.8%; 8 singletons; Kish effective studies 7.62;
- full-engineered baseline remains the pre-review corrected representation.

### 4. Post-review representation sensitivity

Explicitly label as reviewer-triggered.

Representations:
1. full engineered;
2. no identity-adjacent categories;
3. physical numeric only.

Validation:
- matched row-random 5-fold;
- GroupKFold by primary study;
- strict LOSO;
- n>=5-study LOSO robustness;
- crossed missingness sensitivity by removing dose/contact time.

### 5. Results

#### 5.1 Full representation reproduces apparent accuracy / transfer failure

- RF .9042 random → .0265 grouped → .0085 LOSO;
- XGB .8936 → .1929 → .1624;
- stack grouped -0.5566;
- report grouped fold dispersion and avoid treating pooled R² as a stable per-fold estimate.

#### 5.2 Feature representation changes the engineering conclusion

Primary table:

| Representation | Model | Random R² | Grouped R² | LOSO R² |
|---|---|---:|---:|---:|
| Full | RF | .904 | .027 | .008 |
| Full | XGB | .894 | .193 | .162 |
| No identity categories | RF | .825 | .637 | .628 |
| No identity categories | XGB | .821 | .481 | .457 |
| Physical numeric | RF | .825 | .580 | .573 |
| Physical numeric | XGB | .820 | .496 | .469 |

Interpretation: study-aware validation diagnosed harmful context representation, rather than proving the corpus has zero transferable signal.

#### 5.3 Improvements survive cluster and missingness sensitivity

- n>=5 studies: no-id RF LOSO ≈.616;
- large-only population: no-id RF ≈.615;
- remove dose+contact:
  - no-id RF grouped .652 / LOSO .655;
  - physical RF grouped .682 / LOSO .673.

Therefore neither singleton studies nor heavily imputed dose/contact variables explain the recovered transfer.

#### 5.4 Domain qualification still blocks inverse design

- strict agricultural 65/4: negative LOSO R² under all representations;
- broad biogenic XGB ~.642 after category removal, but catastrophic Alshabib remains;
- waste-carbon ~.52–.57 diagnostic;
- present pooled results with equal-study error context.

#### 5.5 Agreement does not imply correctness

Broad-biogenic Alshabib after category removal:
- RF MAE 1529.66;
- XGB MAE 1489.39;
- RF-XGB mean disagreement 40.27 mg/g.

This is the sharper inverse-design warning.

### 6. Discussion

#### 6.1 Study-aware validation as feature-representation diagnostic

Full context categories help row-random prediction but harm transfer. A high random-split score can therefore hide not just dependency leakage but a scientifically unstable representation.

#### 6.2 Why deleting context is not itself an inverse-design solution

A forward predictor may transfer better after dropping material/pollutant categories, but a prescriptive adsorbent-process optimizer still requires explicit material and adsorbate context. The next system must encode context in a representation that generalises rather than silently omit it.

#### 6.3 Dataset limits

- high process-variable missingness;
- limited effective study count;
- intended agricultural domain extremely thin;
- heterogeneous study protocols.

#### 6.4 Reliability gate

No renewed inverse-design recommendation until:
- fit-for-purpose domain;
- many independent primary studies;
- representation chosen using study-aware/nested validation;
- explicit immutable material/pollutant context;
- justified constraints;
- target-matching objective;
- uncertainty/applicability gate that catches complete-study failures;
- external/lab validation.

### 7. Conclusion

The corrected lesson is not “study-aware validation always destroys performance.” It is:

> **Study-aware validation changed the model-development decision. It exposed that the original feature representation transferred poorly, identified a representation correction that restored forward predictive transfer, and simultaneously showed that the evidence is still insufficient for reliable adsorption inverse design.**

## Primary figure

One grouped-bar figure showing R² by representation and validation regime:
- Full engineered;
- No identity-adjacent categories;
- Physical numeric only;
for RF and XGB across:
- row-random;
- primary-study-grouped;
- LOSO.

This replaces the old simple random-vs-grouped figure.

## Main tables

1. **Table I:** representation × validation R² (RF/XGB, random/grouped/LOSO).
2. **Table II:** domain-qualified LOSO + catastrophic-study diagnostic.

Missingness/study-size diagnostics should be compact prose or supplementary table if page-constrained.

## Claims to avoid

- “Study-aware validation proves the corpus cannot generalise.”
- “The corrected model is now ready for inverse design.”
- “Removing material categories solves the engineering problem.”
- “The post-review ablation was predeclared.”
- “24 studies means 24 equally informative independent domains.”
- “Broad-biogenic R²=.642 validates deployment.”
