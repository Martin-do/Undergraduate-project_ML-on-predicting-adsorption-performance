# Paper 2 / V3 Phosphate Primary-Source Verification Standard

Status: **LOCKED BEFORE ANY COMPILATION ROW IS ADMITTED TO V3**

Clarification recorded 2026-08-29, before predictive modelling: an experimentally observed numerical value stated explicitly and unambiguously in the primary article prose is treated as Class A evidence alongside exact primary tables/machine-readable values. This clarification is source-neutral and does not relax any source-, condition-, target-, unit-, species- or lineage-verification requirement.

## 1. Purpose

The public phosphate master workbook is a discovery and extraction aid, not an authoritative primary dataset. A DOI block is not admitted merely because its metadata resolve or because its values look plausible.

**Every admitted V3 numerical row must be traceable to the corresponding primary article/supplement and independently checked.**

## 2. Source-level gates

A primary study must pass all of the following before any of its rows can be marked `include`:

1. DOI/reference resolves to the intended primary experimental paper.
2. The primary paper concerns aqueous phosphate/phosphorus adsorption using a material within the locked biochar-based scope.
3. The primary article or supplementary information is available for verification; abstract-only access is insufficient for row admission.
4. Material preparation and modification are understood well enough to populate the V3 schema without guessing.
5. The target quantity represented by candidate `qe` rows is confirmed from the primary source.
6. The concentration species/basis is known: e.g. P, PO4-P, or PO4^3−, with any conversion documented.
7. Duplicate inheritance across compilations or multiple papers is assessed.

## 3. Row-level numerical verification

Each proposed V3 row must use one of these evidence classes.

### A — exact primary numerical value

Preferred. The experimentally observed value is stated explicitly and unambiguously in the primary source, including:
- a primary supplementary spreadsheet/CSV;
- an HTML/XML table;
- a primary article table with unambiguous row/column coordinates;
- primary article prose that directly states the observed experimental value and makes its measured quantity/units unambiguous.

A value is not Class A merely because a fitted/model parameter is printed exactly. Fitted kinetic `qe`, Langmuir `qmax`, optimisation predictions or other model-derived response values remain ineligible for the observed V3 `qe` target unless separately analysed under a different target definition.

Record exact source location and retain original units/basis.

### B — reproducibly derived primary value

Permitted where `qe` is calculated from primary reported quantities using a documented equation and all required quantities are explicitly reported. Store the formula and inputs in the extraction record.

### C — figure-digitized primary value

Permitted only when the primary source reports the experimental series graphically and no exact table/text value is available.

Requirements:
- the figure/panel/series must be identified;
- digitization/reconstruction method must be recorded;
- axes, units and series labels must be independently checked;
- the reconstructed value must be compared with any textual/table anchors available in the primary paper;
- extraction uncertainty must be retained;
- figure-derived rows can be excluded in a prespecified sensitivity analysis.

A secondary compilation's digitized value may be used as a candidate coordinate, but it is not accepted without comparison to the primary figure.

### D — unverifiable

If the value cannot be traced to an exact primary value, reproducible derivation or primary figure with sufficient clarity, it is not admitted to the primary V3 population.

## 4. No spot-check admission

Checking a few values from a study does not authorize all rows from that study. Verification is row-level. Source-level verification establishes eligibility; numerical evidence establishes row admission.

## 5. Unit and species rules

Store the primary reported value and unit before transformation.

`qe_mg_g` is created only after confirming:
- mass numerator species/basis;
- adsorbent mass denominator;
- whether reported concentration is P, PO4-P or PO4^3−;
- whether dry-mass basis is implied/explicit;
- whether the value is observed equilibrium/terminal uptake rather than fitted `qmax`.

Any stoichiometric/unit conversion must be deterministic and recorded in `unit_conversion_note`.

## 6. Target-proxy exclusion

Removal efficiency/percentage is not used as a predictor of `qe`. Residual concentration may only be used where scientifically justified and predeclared; it must not become a direct mass-balance target proxy that trivializes prediction.

## 7. Verification records

For every admitted row retain:
- `primary_study_id`;
- DOI;
- source title/year;
- figure/table/supplement/text location;
- original row/series label where available;
- extraction evidence class A/B/C;
- original units;
- conversion note;
- verification status;
- verifier/date/version;
- duplicate/lineage status.

## 8. Batch workflow

Verification proceeds source by source. Large source blocks are not automatically prioritized over sources with cleaner primary evidence. Studies with machine-readable, clear tabular or explicit primary-text observations should generally be admitted first because they provide lower extraction uncertainty.

## 9. Modelling gate

No model may consume a row with `v3_admission_status=PENDING_PRIMARY_SOURCE_VERIFICATION` or equivalent unresolved verification state.
