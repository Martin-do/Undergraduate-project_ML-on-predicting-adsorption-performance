# Paper 2 / V3 Phosphate Primary Verification Log V1

Status: **ACTIVE CURATION LOG — NO MODEL TRAINED**

Branch: `paper2/v3-provenance-aware-model-development`

Verification date: 2026-08-29

This log applies the locked `PHOSPHATE_PRIMARY_SOURCE_VERIFICATION_STANDARD.md`. The public Iftikhar phosphate workbook remains a discovery/extraction aid only. Verification is row-level; checking one or more rows never authorizes an entire DOI block.

## Decision summary

| DOI | Study | Primary access | Row decision | V3 status |
|---|---|---|---|---|
| `10.3390/separations8030032` | Son et al. (2021) | Open primary article | Three exact experimental equilibrium capacities verified from Table 3 | **PRIMARY-VERIFIED STAGING: 3 rows** |
| `10.3390/ijerph19127227` | Feng et al. (2022) | Open primary article | Secondary packet values conflict materially with primary-text pH response | **BLOCKED — discrepancy reconciliation required** |
| `10.3390/ma13040816` | Tao et al. (2020) | Open primary article/PMC | Direct experimental equilibrium capacities identified, but required condition fields are incomplete for Figure 9 experiment | **BLOCKED — condition matching required** |

## 1. Son et al. 2021 — VERIFIED PRIMARY STAGING

**DOI:** `10.3390/separations8030032`

**Title:** *Adsorption Characteristics of Phosphate Ions by Pristine, CaCl2 and FeCl3-Activated Biochars Originated from Tangerine Peels*

### Primary-source verification

The article reports the following directly in **Table 3** as experimental equilibrium adsorption capacities (`Qe,exp`):

- TB: `0.104 ± 0.004 mg/g`
- CTB: `0.354 ± 0.002 mg/g`
- FTB: `1.655 ± 0.001 mg/g`

These are experimental `Qe,exp` values, not pseudo-order fitted `Qe,cal` and not Langmuir `Qmax`. Therefore they satisfy **Evidence Class A — exact primary table value**.

The kinetic experiment and Figure 6 establish the associated experimental conditions:

- adsorbent dose: `0.6 g/L`;
- initial phosphate concentration: `1 mg/L`;
- pH: `7`;
- temperature: `25 °C`;
- agitation: `150 rpm`;
- solution volume: `25 mL`;
- kinetic observation window: `0.5–48 h`;
- Figure 6 reports the experiment with a `24 h` contact-time condition.

The paper states that adsorption equilibrium was reached after approximately 2 h for TB and CTB and 18 h for FTB. The staging records retain `contact_time_min=1440` because the reported Figure 6 experimental condition is 24 h; the earlier plateau times are retained in the row notes rather than silently substituted for the reported test condition.

Material preparation is also primary-verified:

- precursor: tangerine peel;
- pyrolysis temperature: `800 °C`;
- pyrolysis residence time: `1 h`;
- CTB activation: `CaCl2`;
- FTB activation: `FeCl3`.

Table 1 supplies exact C/H/O/N/ash, BET surface area, pore volume and pore-size values for all three adsorbents. These values are copied into the staging records because they are exact primary table values.

### Admission decision

Three rows are written to `PHOSPHATE_V3_PRIMARY_VERIFIED_STAGING.csv`.

They are **not yet released to model development**. Their row-level numerical provenance is high confidence, but the final duplicate/lineage sweep and multi-study population freeze have not yet occurred. Consequently the staging file uses `duplicate_status=possible_lineage` and `inclusion_status=sensitivity` until the final corpus reconciliation changes them, if warranted, to primary `include` rows.

The remaining 213 candidate rows from the 216-row secondary DOI block remain **unadmitted**. No spot-check propagation is permitted.

## 2. Feng et al. 2022 — PRIMARY/SECONDARY DISCREPANCY

**DOI:** `10.3390/ijerph19127227`

**Title:** *Oyster Shell Modified Tobacco Straw Biochar: Efficient Phosphate Adsorption at Wide Range of pH Values*

The primary article verifies the material preparation and experimental design, including tobacco-straw biochar prepared at 500 °C and phosphate batch experiments across concentration and pH ranges.

However, the candidate secondary packet reports approximately `38–49 mg/g` across pH 3–11 at `150 mg/L`, whereas the primary article states substantially higher adsorption in that pH range (approximately `75–96 mg P/g`, with acidic conditions around `93–96 mg P/g`). This difference is too large to treat as ordinary digitization noise.

**Decision:** no Feng packet row is admitted. The DOI block remains blocked until species basis, mass-balance conversion, figure extraction and any P-versus-PO4 transformation are reconciled directly against the primary figure/data.

The primary article also reports a fitted Langmuir maximum near `88.64 mg P/g`. That fitted `Qmax` is explicitly excluded from the V3 `qe_mg_g` target.

## 3. Tao et al. 2020 — DIRECT QE VALUES FOUND, CONDITIONS INCOMPLETE

**DOI:** `10.3390/ma13040816`

**Title:** *Synthesis of Fe/Mg-Biochar Nanocomposites for Phosphate Removal*

The primary article directly states, for the no-coexisting-anion condition in the Figure 9 experiment:

- WBC10: `0.45 mg/g`
- WBC11: `0.75 mg/g`
- WBC12: `2.12 mg/g`

These are described as equilibrium adsorption capacities and therefore are qualitatively preferable to the model-derived kinetic `qe` parameters in Table 2 or fitted `qmax` values in Table 3. The Table 2 kinetic `qe` values and Table 3 `qmax` values are **not eligible V3 observed targets**.

The primary batch-method section verifies for the coexisting-anion experiment:

- phosphate concentration: `50 mg/L`;
- WBC1x mass: `0.05 g`;
- solution volume: `25 mL`, equivalent to `2 g/L` dose;
- temperature: `30 °C`;
- agitation: `120 rpm`.

However, that method states that samples were taken at a preset time and does not explicitly give the required final contact time for the Figure 9 coexisting-anion experiment. It also does not explicitly state a controlled pH for that experiment. Because `contact_time_min` and `ph` are mandatory V3 primary fields, neither value will be inferred from a neighbouring experiment, the secondary compilation or model output.

**Decision:** the three Tao capacities remain primary-verified *candidates* but are not added to the V3 staging CSV until the missing condition fields can be established from primary evidence or the feature/eligibility protocol is formally revised before modelling.

## 4. Current staging count

- primary-verified staging rows: **3**
- primary studies represented: **1**
- rows released for modelling: **0**
- model training performed: **none**

A final V3 data-gate run is intentionally deferred because the staging population currently contains only one independent study and has not completed lineage reconciliation.

## 5. Next verification priority

1. Continue with open-access studies whose primary figures/tables expose exact experimental `qe` plus all mandatory process conditions.
2. Prefer Evidence Class A/B rows before any Class C figure digitization.
3. Use Qin et al. 2023 and the remaining open-access verification packets as the next candidates for a second independently verified study.
4. Keep Tao and Feng blocked until their specific unresolved issues are closed.
5. Do not train any predictive model until the predeclared multi-study curation and freeze gates are satisfied.
