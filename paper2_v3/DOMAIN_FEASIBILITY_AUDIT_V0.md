# Paper 2 / V3 Domain Feasibility Audit — V0

Status: **SCREENING ONLY — NO DOMAIN SELECTED AND NO V3 MODEL TRAINED**

This document records the first candidate-domain screen after the V3 research protocol was frozen. It is intentionally based on study coverage, provenance feasibility, descriptor coherence and external-validation potential rather than preliminary model scores.

## 1. Current shortlist

The first screen leaves three serious candidates:

1. **Dye adsorption on biomass-derived biochar/activated carbon**
2. **Phosphate/phosphorus adsorption on biochar**
3. **Heavy-metal adsorption on biochar/activated carbon**

Ammonia-N remains a useful pilot domain but currently fails the V3 independent-study development target. Emerging organics remain uncertain because the public modelling matrix does not yet provide a defensible multi-primary-study grouping structure.

## 2. Dye adsorption

### Existing evidence

- Liu et al. 2025, *Carbon Research*, DOI `10.1007/s44246-025-00213-9`: 685 reported literature-derived dye adsorption observations. The Paper 1 provenance reconstruction produced a strict 624-row population mapped to 17 high-confidence primary studies and an extended 668-row/19-study sensitivity.
- Moosavi et al. 2021, *Nanomaterials*, DOI `10.3390/nano11102734`: 350 published observations with multiple explicitly referenced primary studies; 344 rows were directly recoverable in the official supplement.
- Liu et al. 2024, *Journal of Hazardous Materials*, DOI `10.1016/j.jhazmat.2024.135853`: 628 hydrochar-dye observations from 35 hydrochar types.
- Yadav et al. 2025, *Carbon Research*, DOI `10.1007/s44246-024-00168-3`: literature-derived Congo Red/biochar dataset with high random-split performance; raw dataset currently reported as available on request.
- Rajput et al. 2025, *Journal of Water Process Engineering*, DOI `10.1016/j.jwpe.2024.106749`: 199 literature-derived methylene-blue/biochar observations.

### Strengths

- Substantial prior provenance work already exists.
- Multiple public or partially public datasets can seed study discovery.
- Adsorbate molecular descriptors are feasible and scientifically relevant because the domain contains multiple dyes.
- External/prospective dye datasets exist.

### Risks

- Strong source-lineage overlap exists between several published compilations.
- Combining many dye classes may still be chemically heterogeneous.
- Some datasets omit row-level study IDs and would require reconstruction.
- A single-dye subdomain such as methylene blue or Congo Red may become too small in independent-study count after deduplication.

### Current decision

**Retain as high-priority candidate.** The next feasibility question is whether deduplicating the literature lineages still yields at least 30, preferably 50+, independent primary studies with sufficient descriptor coverage.

## 3. Phosphate/phosphorus adsorption

### Existing evidence

- Iftikhar et al. 2025, *Chemosphere*, DOI `10.1016/j.chemosphere.2024.144031`: literature search from 2000–2024 initially identified more than 227 works and shortlisted 71 relevant articles. The modelling corpus contains approximately 2,959 observations from 132 unique adsorbents. The published split was by adsorbent type rather than by primary publication.
- 2025 *Separation and Purification Technology* systematic review/ML study, DOI `10.1016/j.seppur.2025.132066`: more than 50 studies were evaluated and 532 unique data points were used for ML.
- 2024 *Journal of Environmental Management* phosphorus-adsorption ML study, DOI `10.1016/j.jenvman.2024.122405`: literature-derived phosphorus/biochar dataset covering 190 biochar types and 17 variables.

### Strengths

- Independent-study coverage appears capable of exceeding the V3 30-study gate and possibly the preferred 50-study target.
- The adsorbate is chemically much more coherent than a mixed-dye or mixed-metal corpus.
- Multiple independent literature compilations exist, providing opportunities for cross-corpus reconciliation and external validation.
- Core process variables such as pH, initial concentration, dose, contact time and temperature are frequently reported.

### Risks

- Public row-level primary-study identifiers have not yet been confirmed for the large Chemosphere corpus.
- Multiple phosphate compilations may share the same underlying primary studies, so publication count cannot be added naively.
- Pristine and metal-modified biochars may represent materially different mechanisms and may require stratification.
- Reported phosphorus targets may mix phosphate species, equilibrium capacity, maximum fitted capacity or removal outcomes unless carefully harmonised.

### Current decision

**Promote to very-high-priority candidate.** It currently has the strongest apparent independent-study coverage, but provenance access must be demonstrated before selection.

## 4. Heavy-metal adsorption

### Existing evidence

- Huang et al. 2026, *Forests*, DOI `10.3390/f17030326`: 452 adsorption records compiled from independent literature sources. The study explicitly separates publications between training and testing and reports strong source-held-out XGB performance. Raw modelling rows are available from authors on request.
- Yu et al. 2026, *Water*, DOI `10.3390/w18121416`: 781 literature-derived Pb(II)/Cd(II) observations (304 Pb, 477 Cd) with 23 physicochemical/environmental variables plus 11 binary inorganic-element indicators. The published supplementary material includes `Table S1 Original_data`.
- Abu-Shareha et al. 2026, *Journal of Hazardous Materials Advances*, DOI `10.1016/j.hazadv.2026.101004`: 1,150 Cd(II) observations derived from five cited source papers; useful as a dataset but insufficient alone for the V3 independent-study target.

### Strengths

- Strong mechanistic descriptor opportunities: ionic/hydrated radius, atomic weight, electronegativity and hydrolysis-related properties can represent metal identity more meaningfully than a nominal label.
- Recent work already demonstrates leakage-aware preprocessing and source-level validation.
- A public supplementary original-data table exists for the Pb/Cd dataset and may accelerate feasibility assessment.
- Multiple metal ions could allow descriptor-based transfer experiments if sufficient studies are available.

### Risks

- Combining metals may introduce ion-specific mechanisms and experimental regimes.
- Exact source-study counts and row-level provenance still need reconstruction for the 781-row Pb/Cd corpus.
- Modified biochars may carry highly study-specific mineral compositions.
- The 1,150-row Cd dataset illustrates the high-row/low-study problem: only five cited source papers cannot satisfy the V3 independence target by itself.

### Current decision

**Retain as high-priority candidate**, with a likely focus on a carefully specified set such as Pb/Cd rather than all metals indiscriminately.

## 5. Ammonia-N

Paper 1 reconstructed 409 matched modelling rows from seven primary studies in the public ammonia-N lineage. The domain is chemically coherent and operational variables are available, but seven studies are far below the V3 development gate.

**Current decision: pilot/sensitivity domain only unless a new search identifies a much broader independent literature base.**

## 6. Emerging organic contaminants

The Jaffari et al. 2023 corpus contains 3,757 observations and rich descriptors, but a defensible primary-publication grouping has not yet been established from the public modelling matrix. A large row count does not establish a large independent-study count.

**Current decision: medium-low priority pending provenance evidence.**

## 7. Selection gate to run next

Before choosing between dyes, phosphate and heavy metals, each candidate must pass the same source-level feasibility test:

1. build a deduplicated bibliography of candidate primary studies;
2. identify whether row-level or deterministic block-to-study mapping is feasible;
3. estimate usable primary-study count after duplicate/lineage removal;
4. estimate median and maximum rows per study;
5. quantify availability of core V3 fields;
6. identify at least one external validation corpus that can be kept locked;
7. classify major target-semantic conflicts;
8. identify whether one mechanism/material subclass dominates the literature.

No predictive model is permitted before this gate is completed and the domain is formally frozen.

## 8. Provisional ordering after V0 screen

This is **not a final domain choice**:

- **Phosphate:** strongest apparent independent-study coverage; provenance accessibility unresolved.
- **Dyes:** strongest existing provenance infrastructure and multiple datasets; chemical/source heterogeneity is the main risk.
- **Heavy metals:** strong descriptors and contemporary source-aware precedent; exact independent-study coverage needs reconstruction.
- **Ammonia-N:** currently too few studies.
- **Emerging organics:** source grouping currently unresolved.

The next V3 task is therefore a **source-bibliography and descriptor-coverage audit of phosphate, dyes and heavy metals**, not model training.
