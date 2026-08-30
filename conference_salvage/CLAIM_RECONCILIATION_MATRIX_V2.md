# ID-SEAD Conference Salvage — Claim Reconciliation Matrix V2

Status: **post-independent-review authority for conference reconstruction**  
Supersedes the interpretation layer of `CLAIM_RECONCILIATION_MATRIX.md`; legacy numerical forensic details remain in `NUMERICAL_LINEAGE_AUDIT.md`.

## Status key

- **GREEN** — retainable with ordinary qualification.
- **AMBER** — useful but must be framed as sensitivity/diagnostic evidence.
- **RED** — withdraw as a current scientific claim.

| ID | Claim | Post-review evidence | Status | Conference action |
|---|---|---|---|---|
| C01 | ID-SEAD stacked architecture was implemented | LR/SVR/RF/XGB + Ridge code exists | GREEN | Retain historical architecture |
| C02 | Legacy ID-SEAD R²=0.847 / RMSE=254.1 | Not reproduced; executed state 0.8069/286.29; test-informed selection | RED | Historical claim only |
| C03 | Legacy CI [0.811,0.879] | Not reproduced; stored CI differs and is downstream of selection | RED | Remove |
| C04 | Legacy CV 0.789±0.031 | Not reproduced in inspected executed state | RED | Remove |
| C05 | Violations 49.2→33.9% validate feasibility | Numerical variants exist but depend on test-informed selection and invalid QMAX | RED | Forensic diagnostic only |
| C06 | Sensitivity 8.73 mg/g is validated | Not reproduced; stored variants ~10 mg/g | RED | Remove |
| C07 | QMAX=624 mg/g is universal physical ceiling | 115/322 reconstructed rows exceed it; max 2239 mg/g | RED | Retire |
| C08 | Current corpus validates agricultural-waste inverse design | Strict agri 65 rows / 4 studies; LOSO remains strongly negative under every representation | RED | Do not claim |
| C09 | All 322 rows are agricultural-waste-derived | Provenance/domain audit contradicts | RED | Use heterogeneous literature-derived corpus description |
| C10 | High row-random performance proves unseen-study transfer | Full engineered representation RF .904→group .027/LOSO .008; but category removal recovers transfer | RED as generalisation claim | Row-random remains diagnostic only; interpretation must be representation-aware |
| C11 | Stacking is superior / uniquely robust | Stack underperforms best tree models under grouped/domain evaluations | RED | Historical comparator only |
| C12 | DE generated original Table III 100/200/350 | Dedicated reconstruction uses different optimizer path and targets | RED | Do not defend legacy Table III |
| C13 | `argmax f(x)` implements target matching | Mathematical objective mismatch | RED | Future work must minimise target error or equivalent |
| C14 | Legacy optimizer recommends complete adsorbent-process configurations | Process variables optimized while required material/pollutant context is hidden/under-specified | RED | Future inverse design must specify immutable context or valid decision variables |
| C15 | Pollutant-independent inverse design is supported | Heterogeneous pollutant context; representation sensitivity shows context treatment matters | RED | Restrict/encode context prospectively |
| C16 | 100% robustness validates optima | Protocol under-specified; optimizer lineage unresolved | RED/AMBER | No current engineering robustness claim |
| C17 | Runtime <3 min demonstrates deployment | Runtime is implementation/hardware dependent and not validity evidence | AMBER | Benchmark only if fully specified |
| C18 | Deployment readiness | Reliability/domain/lineage gates fail | RED | No deployment/procurement/commissioning wording |
| C19 | Provenance-controlled V2.1 corpus exists | 307/322 primary-confirmed; strict 273/24 | GREEN | Use as current corpus source of truth |
| C20 | Corrected preprocessing is fold-safe | Current V2.1 preprocessor fits imputation/encoding/scaling in training folds | GREEN | Retain corrected method; do not retroactively apply to legacy run |
| C21 | Legacy SHAP supports design interpretation | Frozen executed lineage incomplete | RED/AMBER | Remove or regenerate under a future declared model |
| C22 | Legacy ablation proves Lipschitz contribution | Stored No-Lipschitz and full ID-SEAD rows identical | RED | Withdraw causal claim |
| C23 | Optimization logs validate Table III | Authoritative logs absent/conflicted | RED | Require logged future optimizer runs |
| C24 | Broad-biogenic XGB may show useful forward prediction | Full XGB LOSO .619; no-identity/physical .642, but one 2-row study remains catastrophic | AMBER | Restricted-domain diagnostic only; pair pooled metric with study-level failure |
| C25 | Training-only uncertainty reliably gates inverse design | Full-engineered Phase 6 intervals extremely wide and still miss catastrophe; model agreement fails | RED | No current uncertainty safety gate |
| C26 | Severe grouped/LOSO collapse is representation-independent | Reviewer-triggered ablation disproves this: removing context categories markedly improves transfer | RED | Explicitly retract/replace any universal-collapse wording |
| C27 | Category-stripped/physical representations support meaningful strict-corpus forward transfer | RF grouped .637 / LOSO .628 after category removal; physical RF grouped .580 / LOSO .573; n>=5 sensitivity preserves improvement | GREEN for forward-prediction sensitivity finding | Retain as post-review sensitivity result, clearly labelled non-predeclared |
| C28 | Heavy dose/contact missingness drives the recovered transfer result | Dose 61.5%, contact 38.1%; removing both preserves/improves no-identity and physical study-aware performance | GREEN as sensitivity result | Disclose missingness; do not claim missingness is harmless beyond tested sensitivity |
| C29 | Full-engineered failure is an artifact of singleton/tiny studies | 8 singleton studies; top 5=71.8% of rows; however n>=5-only LOSO still shows full representation weak and category-stripped representation strong | GREEN diagnostic | Report imbalance/effective study depth and n>=5 robustness |
| C30 | Model agreement implies safety after feature correction | Broad-biogenic Alshabib: no-identity RF/XGB mean disagreement ~40 mg/g while both errors ~1.5 g/g | RED | Promote “agreement ≠ correctness” as inverse-design reliability warning |

## Post-review central claim

The conference paper may defensibly claim:

> In ID-SEAD, conventional row-wise validation concealed both study dependence and a harmful feature-representation effect. Study-aware evaluation showed that engineered material/pollutant/context categories that appeared useful under random splitting induced substantial negative transfer; removing those categories recovered meaningful forward-prediction performance on the broad strict corpus. However, the original agricultural-waste inverse-design domain still fails, catastrophic complete-study errors persist in the more promising restricted domain, and the legacy optimization/constraint lineage remains invalid. Therefore representation-aware study validation is necessary but not sufficient for reliable adsorption inverse design.

## Claims that remain prohibited

- legacy R²=0.847 / RMSE=254.1 / associated CI/CV as current evidence;
- QMAX=624 as a universal physical limit;
- validated original Table III recommendations;
- stacking superiority;
- universal agricultural-waste generalisation from the current corpus;
- deployment/procurement/commissioning readiness;
- any statement that the full-engineered collapse is representation-independent;
- any statement that the post-review ablation was predeclared confirmatory analysis.
