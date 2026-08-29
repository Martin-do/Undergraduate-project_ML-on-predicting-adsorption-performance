# Paper 2 / V3 Phosphate Primary Verification Log V1

Status: **ACTIVE CURATION LOG — NO MODEL TRAINED**

Branch: `paper2/v3-provenance-aware-model-development`

Verification date: 2026-08-29

This log applies the locked `PHOSPHATE_PRIMARY_SOURCE_VERIFICATION_STANDARD.md`. The public Iftikhar phosphate workbook remains a discovery/extraction aid only. Verification is row-level; checking one or more rows never authorizes an entire DOI block.

## Decision summary

| DOI | Study | Primary access | Row decision | V3 status |
|---|---|---|---|---|
| `10.3390/separations8030032` | Son et al. (2021) | Open primary article | Three exact experimental equilibrium capacities verified from Table 3 | **PRIMARY-VERIFIED STAGING: 3 Class A rows** |
| `10.3390/ijerph20010326` | Qin et al. (2023) | Open primary article/PMC | Two equilibrium capacities reproducibly derived from exact primary first-cycle removal values and harmonized from P to PO4 mass basis | **PRIMARY-VERIFIED STAGING: 2 Class B rows** |
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

## 2. Qin et al. 2023 — VERIFIED CLASS B PRIMARY STAGING

**DOI:** `10.3390/ijerph20010326`

**Title:** *Phosphate Removal Mechanisms in Aqueous Solutions by Three Different Fe-Modified Biochars*

### Primary-source evidence

The paper reports its working concentration on a phosphorus basis (`15 mg P/L`) and states that the default batch system uses a biochar-to-solution ratio of `1:200 g:mL`, equivalent to `5 g/L`, at `25 ± 1 °C`, `30 rpm`, pH `6`, with `0.01 M NaNO3` background electrolyte. Figure 9 specifies a 24 h adsorption step.

The primary text reports exact first-cycle/baseline removal efficiencies:

- GBC: `68.62%` before the first NaOH-regeneration loss;
- ZBC: `96.52%` for the first adsorption/washing cycle.

The same paper independently reports that GBC and ZBC reach adsorption equilibrium after approximately `240 min` and `120 min`, respectively. Therefore the 24 h Figure 9 observations qualify as terminal/equilibrium observations for these two materials. CSBC is not included because its equilibrium requires approximately 10 days and its exact first-cycle baseline is not reported in the text with the same clarity.

### Reproducible qe derivation

For an adsorption experiment reported on a P mass basis:

`qe_P = (removal_fraction × initial_P_concentration) / adsorbent_dose`

Thus:

- GBC: `(0.6862 × 15) / 5 = 2.0586 mg P/g`;
- ZBC: `(0.9652 × 15) / 5 = 2.8956 mg P/g`.

To prevent mixing P-mass and PO4-mass targets, both the initial concentration and `qe` are harmonized to the PO4 mass basis using the deterministic stoichiometric ratio:

`M(PO4) / M(P) = 3.06613585`.

Resulting V3 staging values:

- GBC: `6.311947 mg PO4/g`; initial concentration `45.992038 mg PO4/L`;
- ZBC: `8.878303 mg PO4/g`; initial concentration `45.992038 mg PO4/L`.

The original P basis, equation, inputs, conversion factor and converted outputs are all retained in `unit_conversion_note`. These observations therefore satisfy **Evidence Class B — reproducibly derived primary value**.

### Material descriptors

The primary article verifies lychee twig as the feedstock. GBC is goethite-modified biochar prepared from the 600 °C pristine biochar, while ZBC is Fe/ZVI-modified material subjected to a 900 °C secondary pyrolysis. Table 1 provides BET surface area and elemental composition used in the staging rows.

The Table 1 field labelled as pore volume is presented with units of `nm`; because that combination is semantically inconsistent with the V3 `total_pore_volume_cm3_g` field, no pore-volume or pore-size value is silently reinterpreted in these two rows.

### Admission decision

Two Qin observations are added to `PHOSPHATE_V3_PRIMARY_VERIFIED_STAGING.csv` as primary-verified staging rows. Like Son, they remain `sensitivity/possible_lineage` until the duplicate/lineage reconciliation and population freeze are complete.

The other 118 rows in the secondary Qin packet remain unadmitted.

## 3. Feng et al. 2022 — PRIMARY/SECONDARY DISCREPANCY

**DOI:** `10.3390/ijerph19127227`

**Title:** *Oyster Shell Modified Tobacco Straw Biochar: Efficient Phosphate Adsorption at Wide Range of pH Values*

The primary article verifies the material preparation and experimental design, including tobacco-straw biochar prepared at 500 °C and phosphate batch experiments across concentration and pH ranges.

However, the candidate secondary packet reports approximately `38–49 mg/g` across pH 3–11 at `150 mg/L`, whereas the primary article states substantially higher adsorption in that pH range (approximately `75–96 mg P/g`, with acidic conditions around `93–96 mg P/g`). This difference is too large to treat as ordinary digitization noise.

**Decision:** no Feng packet row is admitted. The DOI block remains blocked until species basis, mass-balance conversion, figure extraction and any P-versus-PO4 transformation are reconciled directly against the primary figure/data.

The primary article also reports a fitted Langmuir maximum near `88.64 mg P/g`. That fitted `Qmax` is explicitly excluded from the V3 `qe_mg_g` target.

## 4. Tao et al. 2020 — DIRECT QE VALUES FOUND, CONDITIONS INCOMPLETE

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

## 5. Current staging count

- primary-verified staging rows: **5**
- primary studies represented: **2**
- Evidence Class A rows: **3**
- Evidence Class B rows: **2**
- rows released for modelling: **0**
- model training performed: **none**

The staging population now spans two independent primary studies, but a final V3 data-gate release remains inappropriate because duplicate/lineage reconciliation and the prespecified multi-study corpus build are incomplete.

## 6. Next verification priority

1. Continue through the remaining open-access packets, prioritizing exact table values and reproducibly derived primary values.
2. Build independent-study depth rather than accumulating many rows from Son or Qin.
3. Keep Tao and Feng blocked until their specific unresolved issues are closed.
4. Do not authorize wholesale secondary-compilation rows after a few successful anchors.
5. Do not train any predictive model until the predeclared curation, lineage and population-freeze gates are satisfied.
