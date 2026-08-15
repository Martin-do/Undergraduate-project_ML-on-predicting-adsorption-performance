# ID-SEAD V2 — Source Dependence and Novelty Guardrails

Status: **active scientific safeguard; not a manuscript claim lock**

## Provenance correction

The current 322-row modelling corpus contains 251 rows (77.95%) whose CSV `source_link` is labelled `Moosavi et al., 2023`. The V2 provenance audit now shows that this label is misleading.

The adsorbent vocabulary and source-workbook counts correspond to the public reproducibility dataset for:

> Iftikhar, S., Zahra, N., Rubab, F., Sumra, R. A., Khan, M. B., Abbas, A., & Jaffari, Z. H. (2023). *Artificial neural networks for insights into adsorption capacity of industrial dyes using carbon-based materials*. Separation and Purification Technology, 326, 124891. DOI: 10.1016/j.seppur.2023.124891.

The authors' public `ai4adsorption` code concatenates two upstream Excel workbooks. The dominant ID-SEAD codes occur in the first workbook, `Adsorption and regeneration data_1007c.xlsx`:

- 23 of the 24 short adsorbent labels in the current 251-row block occur directly in that workbook;
- the remaining current label, `CS-AC`, appears to collapse the upstream `CS-AC-KOH`, `CS-AC-NaOH`, `CS-AC-H3PO4`, and `CS-AC-H4P2O7` variants;
- characteristic upstream counts reproduce the same families seen in the ID-SEAD subset (for example CMCAC, TSAC, AC600/700/800/900, MC350--600, CAC/CBAC/HAC, SAC, VAC, TRAC, BGBHAC and WSAC);
- the second workbook, `Dyes data.xlsx`, contains a `Ref` field but none of the 24 dominant ID-SEAD short codes;
- the first workbook contains no explicit reference column, so primary-study provenance must be reconstructed from material/experimental signatures and the source literature.

The original CSV is retained unchanged as historical input. A corrected secondary-source field will be added only in the derived canonical dataset.

## Why this matters

Iftikhar et al. compiled a large carbon-based-material/dye adsorption dataset from published literature together with additional experimental data and developed ANN-based forward prediction, benchmarking and feature-importance analyses. Therefore, reusing a subset of that corpus does **not by itself make ID-SEAD a replication**, but a revised paper that merely reruns alternative regressors on the same records would be too incremental.

The source-dependency ablation confirms that this is not a cosmetic issue. Random-CV performance remains high inside the dominant block, while transfer between the dominant block and the other 71 rows fails strongly. The final study must therefore establish what generalises beyond the inherited Iftikhar-derived data rather than treating the full 322 rows as one homogeneous population.

## Novelty line that must be preserved

The revised study should only claim novelty where the evidence supports a genuinely different research question, such as:

1. primary-study-aware / leakage-resistant validation rather than row-random validation;
2. explicit source-dependence and domain-shift analysis;
3. applicability-domain and predictive-uncertainty diagnostics;
4. external-transfer testing on genuinely independent data;
5. inverse design framed as candidate generation under uncertainty and domain constraints, not as experimentally validated optimum discovery;
6. physically/domain-qualified constraints, replacing the invalid universal `Q_MAX=624 mg/g` assumption.

If these contributions do not survive validation, the manuscript must be reframed rather than preserving the original title by force.

## Required anti-replication tests

Before journal submission, the evidence package must contain all of the following:

- **Primary provenance reconstruction** for the Iftikhar-derived rows, so records from the same underlying paper cannot leak across folds.
- **Dominant-source ablation:** report model behavior on the inherited Iftikhar-derived subset, on independently collected ID-SEAD rows, and transfer in both directions.
- **Leave-primary-study-out validation:** final grouped CV after provenance reconstruction.
- **Source-balanced reporting:** include study-level/equal-study summaries, not only row-weighted metrics.
- **Independent external validation:** data not used in the Iftikhar source corpus and not represented in model fitting.
- **Novelty comparison table:** explicitly distinguish the Iftikhar objective/method/data from the revised ID-SEAD objective/method/data.

## Publication positioning

Do **not** claim:

> First use of machine learning to predict adsorption performance of agricultural-waste adsorbents or carbon-based materials.

That ground is already covered by Iftikhar et al. and other earlier studies.

A defensible future claim, if supported by the completed experiments, would be closer to:

> A provenance-aware, domain-qualified framework for evaluating and inversely designing literature-derived adsorption systems under study-level and domain-shift constraints.

The exact material/pollutant scope will be locked only after the canonical-domain audit.

## Dataset-diversification recommendation

The present corpus is too dependent on one secondary compilation for a strong general-purpose claim. Provenance reconstruction is necessary but not sufficient. After reconstruction, the next data-curation phase should deliberately add independent primary studies from the final defined modelling domain, with source IDs retained at row level. The objective is not an arbitrary row count; it is broader independent-study coverage and reduced dependence on any one compiled source.
