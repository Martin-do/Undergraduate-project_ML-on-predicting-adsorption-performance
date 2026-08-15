# ID-SEAD V2 — Phase 2 Model-Family Findings

Status: **confirmed diagnostic findings; feature-parity validation still pending**

This phase asks a narrower question than the submitted manuscript: does the original model family (LR, SVR, RF, XGB and Ridge stacking) retain value when all models use identical leakage-resistant outer folds and fold-safe preprocessing?

The legacy physical constraint is deliberately excluded because the preceding audit showed that the hard-coded `Q_MAX = 624 mg/g` is contradicted by 115 observed target rows.

## Results

| Validation scheme | LR R² | SVR R² | RF R² | XGB R² | Unconstrained Ridge stack R² |
|---|---:|---:|---:|---:|---:|
| Row-random | 0.849 | 0.006 | 0.907 | **0.917** | 0.910 |
| Strict citation | -4.041 | -0.641 | **-0.507** | -0.584 | -0.634 |
| Secondary-system proxy | -1.342 | -0.111 | **0.679** | 0.652 | 0.619 |
| Adsorbent holdout | -3.355 | -0.175 | **0.740** | 0.514 | 0.680 |

On the two provisional but more scientifically informative transfer views, Random Forest is the strongest model:

### Secondary-system proxy

- RF: R² = 0.6790, RMSE = 386.30 mg/g, MAE = 257.95 mg/g
- XGB: R² = 0.6524, RMSE = 401.99 mg/g, MAE = 268.63 mg/g
- Ridge stack: R² = 0.6192, RMSE = 420.74 mg/g, MAE = 329.99 mg/g

### Adsorbent holdout

- RF: R² = 0.7405, RMSE = 347.34 mg/g, MAE = 225.19 mg/g
- XGB: R² = 0.5144, RMSE = 475.16 mg/g, MAE = 281.44 mg/g
- Ridge stack: R² = 0.6802, RMSE = 385.58 mg/g, MAE = 279.47 mg/g

## Interpretation

1. **The stack is not currently the best predictor.** It does not beat the strongest base learner under any of the four validation schemes.
2. The row-random result reproduces the familiar optimistic pattern: tree models and stacking all look strong when closely related rows can cross folds.
3. The strict citation result remains an intentionally over-conservative bound because the 251-row Moosavi-labelled source is a secondary compilation rather than one primary experiment.
4. The provisional secondary-system and adsorbent holdouts retain meaningful predictive structure, but Random Forest—not stacking—is currently strongest.
5. The poor SVR and weaker LR predictions can make an all-model Ridge stack less useful; however, we will **not** delete weak learners merely to manufacture a stacking win.

## What this does and does not prove

This phase uses a clean raw/OHE representation to isolate validation and model-family effects. It does **not yet reproduce every engineered feature from the submitted notebook**. Therefore the correct conclusion is:

> Under a controlled fold-safe baseline representation, the proposed stacking architecture has not yet demonstrated incremental predictive value over Random Forest.

It is premature to conclude that the manuscript's exact feature-engineered stack can never add value. The next required experiment is feature-parity validation: reproduce the original processing features, hierarchical material/pollutant classes, group-aware imputation and interaction features inside each fold, then repeat the same model-family comparison.

## Decision gate

If the feature-parity experiment still shows RF/XGB outperforming the stack under leakage-resistant folds, the revised paper should **not** retain “stacked ensemble” as a claimed source of predictive superiority. At that point we should either:

- reposition the contribution around physically/domain-aware prediction and inverse design using the strongest validated surrogate; or
- justify stacking for another measured property (e.g. constraint/stability trade-off) only if new evidence actually demonstrates that benefit.

No model will be selected because it preserves the original paper title. Model selection will follow the validation evidence.
