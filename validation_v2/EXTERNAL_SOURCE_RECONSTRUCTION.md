# External-validation source reconstruction — V2

Status: **source/implementation audit locked before new external metrics**

The legacy notebooks used two published datasets for external testing. Before rerunning them, V2 reconstructed the exact workbook mappings and checked the cited publications.

## Dataset A — legacy label was wrong

Legacy notebook label:

- `Shen et al. 2024`
- DOI `10.1007/s44246-025-00213-9`

Verified source:

- **Liu et al. (2025)**, *Enhanced machine learning prediction of biochar adsorption for dyes: Parameter optimization and experimental validation*, **Carbon Research 4, 46 (2025)**;
- DOI: `10.1007/s44246-025-00213-9`;
- source workbook in this repository: `Biochar_dye_filtered.xlsx`;
- workbook contains 685 data rows in the relevant sheets.

The source article reports 43 biochars, 15 dye categories and 685 collected experimental observations. It also reports a source-paper preprocessing step that removed 17 high-Q observations (>4 mmol/g) for its own model, leaving 668 observations. That source-defined target rule is distinct from the project's invalid `Q_MAX=624 mg/g` rule and must not be conflated with it.

### Legacy project transformation

The old notebook:

1. loaded `After preprocessing` and `original` sheets;
2. attached dye identity from `TypeDye`;
3. converted Q from mmol/g to mg/g and C0 from mmol/L to mg/L using a hard-coded dye molecular-weight map;
4. dropped unmapped/invalid rows;
5. **then deleted every row with converted qe > 624 mg/g**;
6. supplied only BET, pore volume, solution pH, adsorption temperature and C0 to the trained feature template;
7. filled all other model inputs from project-training template values.

That produced the legacy N=525 result. Because step 5 uses the invalid project QMAX to censor the external target, the legacy N=525 evaluation is not an uncensored external test.

### V2 correction

- preserve the source unit conversion;
- do **not** apply project QMAX target truncation;
- do not invent particle size, contact time, dose or pyrolysis temperature when the relevant sheet does not preserve a valid cross-dataset equivalent;
- let the training-fitted V2 preprocessor handle missing external features;
- report feature coverage explicitly;
- do not use external target values for tuning.

A sensitivity analysis may separately report the source paper's own 668-row Q<=4 mmol/g preprocessing rule because that rule predates this project model, but it must be labelled as source-defined preprocessing rather than a V2 optimization choice.

## Dataset B — Jaffari et al. 2023

Legacy notebook citation:

- Jaffari et al. 2023;
- DOI stated as `10.1016/j.cej.2023.144684`.

Verified source:

- Zeeshan Haider Jaffari et al., *Machine-learning-based prediction and optimization of emerging contaminants' adsorption capacity on biochar materials*, **Chemical Engineering Journal 466 (2023) 143073**;
- correct DOI: **`10.1016/j.cej.2023.143073`**;
- published June 2023;
- source paper reports 3,757 data points, 18 biochar materials and 12 emerging contaminants;
- repository source workbook: `Raw_data.xlsx`, 3,757 rows.

### Legacy project transformation defects

The old notebook intended to map:

- surface area;
- pore volume;
- solution pH;
- adsorption temperature;
- initial concentration;
- pyrolysis temperature;
- particle size;
- capacity;
- dose from adsorbent dosage / volume.

Two implementation problems are now confirmed from the workbook schema/code:

1. **Pyrolysis-temperature header mismatch.** The workbook header contains trailing whitespace (`Pyrolysis temperature  `). The old rename key omitted it, so `pyrolysis_temp_c` was not actually created. The generic external-prediction function therefore silently retained the training-template pyrolysis value instead of using the Jaffari observation.
2. **Average pore size was mapped to adsorbent particle size.** These are not the same physical variable. V2 leaves `particle_size_mm` missing rather than substituting pore diameter.

The legacy notebook also removed rows with qe > 624 mg/g before evaluation and then imposed the same invalid upper bound when judging prediction violations.

### V2 correction

- strip source-column whitespace explicitly;
- build `method_processing` from the actual pyrolysis temperature/time so the original feature parser receives the source value;
- use adsorption contact time directly;
- calculate dose as source dosage / volume where finite;
- keep `Average pore size` separate and do not map it to particle size;
- retain all positive finite targets without project-QMAX censoring;
- use fold-safe/full-training V2 preprocessing and unconstrained base models;
- preserve pollutant/adsorbent identity where available;
- report engineered-category novelty and missing-feature burden.

## Statistical caution

These datasets are separate published compilations, but **complete primary-study disjointness from the project training corpus has not yet been proven**. Therefore the revised paper should call them external published datasets/compilations, not claim guaranteed source-independent validation unless row-level/source-level overlap is audited.

Row-level bootstrap confidence intervals are also not appropriate when the external compilation contains many observations from the same materials/studies but row-level provenance is unavailable. V2 therefore reports deterministic external metrics and domain diagnostics rather than pretending every row is an independent bootstrap unit.
