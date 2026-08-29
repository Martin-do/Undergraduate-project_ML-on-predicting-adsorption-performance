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
| `10.1039/c8ra10400j` | Zhong et al. (2019) | Open RSC article/PMC | Two exact primary-text equilibrium capacities, with complete kinetic conditions and deterministic P→PO4 harmonisation | **PRIMARY-VERIFIED STAGING: 2 Class A rows** |
| `10.3390/ijerph19127227` | Feng et al. (2022) | Open primary article | Secondary packet values conflict materially with primary-text pH response | **BLOCKED — discrepancy reconciliation required** |
| `10.3390/ma13040816` | Tao et al. (2020) | Open primary article/PMC | Direct experimental equilibrium capacities identified, but required condition fields are incomplete for Figure 9 experiment | **BLOCKED — condition matching required** |

## 1. Son et al. 2021 — VERIFIED PRIMARY STAGING

**DOI:** `10.3390/separations8030032`

**Title:** *Adsorption Characteristics of Phosphate Ions by Pristine, CaCl2 and FeCl3-Activated Biochars Originated from Tangerine Peels*

The primary article explicitly treats the adsorbate and test concentration as `PO4^3-` and reports the following in Table 3 as experimental equilibrium adsorption capacities (`Qe,exp`):

- TB: `0.104 ± 0.004 mg/g`
- CTB: `0.354 ± 0.002 mg/g`
- FTB: `1.655 ± 0.001 mg/g`

These are observed experimental values, not pseudo-order fitted `Qe,cal` and not Langmuir `Qmax`, so they satisfy **Evidence Class A**.

Associated Figure 6 conditions are dose `0.6 g/L`, initial `PO4^3- = 1 mg/L`, pH `7`, temperature `25 °C`, agitation `150 rpm`, and a 24 h experimental endpoint. Text reports equilibrium after approximately 2 h for TB/CTB and 18 h for FTB; the staging rows retain the reported 24 h endpoint and preserve the plateau times in notes.

Material preparation is primary-verified at 800 °C for 1 h. CTB and FTB use CaCl2 and FeCl3 activation, respectively. Exact elemental/BET/pore values from Table 1 are retained.

Three rows are staged. The remaining 213 candidate rows from the secondary DOI block remain unadmitted.

## 2. Qin et al. 2023 — VERIFIED CLASS B PRIMARY STAGING

**DOI:** `10.3390/ijerph20010326`

**Title:** *Phosphate Removal Mechanisms in Aqueous Solutions by Three Different Fe-Modified Biochars*

The primary paper reports a phosphorus-basis experiment at `15 mg P/L`, `5 g/L` adsorbent, pH `6`, `25 ± 1 °C`, `30 rpm`, `0.01 M NaNO3`, and a 24 h Figure 9 adsorption step. Exact first-cycle/baseline removal efficiencies are `68.62%` for GBC and `96.52%` for ZBC. Independent text establishes equilibrium by approximately 240 and 120 min, respectively.

Mass-balance derivation gives:

- GBC: `(0.6862 × 15) / 5 = 2.0586 mg P/g`
- ZBC: `(0.9652 × 15) / 5 = 2.8956 mg P/g`

Both concentration and capacity are harmonised to PO4 mass using `M(PO4)/M(P)=3.06613585`:

- initial concentration: `45.992038 mg PO4/L`
- GBC: `6.311947 mg PO4/g`
- ZBC: `8.878303 mg PO4/g`

These are **Evidence Class B — reproducibly derived primary values**. The original P basis, equation and conversion are preserved. Two rows are staged; the other 118 secondary packet rows remain unadmitted.

## 3. Zhong et al. 2019 — VERIFIED CLASS A PRIMARY STAGING

**DOI:** `10.1039/c8ra10400j`

**Title:** *Enhanced phosphate sequestration by Fe(III) modified biochar derived from coconut shell*

### Primary observed values

Section 3.2 of the primary RSC article explicitly states the observed kinetic equilibrium capacities:

- CSB: `2.2 mg P/g`
- Fe-CSB: `4.2 mg P/g`

The article separately prints fitted kinetic `qe` values in Table 3; those fitted values are **not** used. The two staging targets are the direct experimental equilibrium values stated in the primary prose and shown by Figure 3(a). Under the source-neutral 2026-08-29 clarification to the verification standard, an exact observed value explicitly stated in primary article prose is Class A evidence.

### Experimental conditions

Section 2.3 establishes:

- adsorbent mass: `0.05 g`
- solution volume: `20 mL` → `2.5 g/L`
- initial analytical phosphorus/phosphate concentration: `20 mg/L`
- background electrolyte: `0.02 M KCl`
- pH: `7.0`
- temperature: `25 ± 1 °C`
- agitation: `150 rpm`

Section 3.2 reports equilibrium after `5 h` for CSB and `24 h` for Fe-CSB. Thus the staging contact times are 300 and 1440 min.

The primary response is explicitly described as the **amount of P adsorbed**, and filtrates are analysed for P. To keep the canonical V3 target on one phosphate mass basis, the primary P-basis concentration/capacities are converted using `M(PO4)/M(P)=3.06613585`:

- initial concentration: `20 mg P/L → 61.322717 mg PO4/L`
- CSB: `2.2 mg P/g → 6.745499 mg PO4/g`
- Fe-CSB: `4.2 mg P/g → 12.877771 mg PO4/g`

The original P values and conversion are retained in each `unit_conversion_note`.

### Material descriptors and an important correction

The primary paper states that the coconut-shell biochar was **purchased** and subsequently washed, oven-dried at `70 °C`, sieved and used. It does not report the manufacturing pyrolysis temperature or residence time of that purchased biochar. Therefore V3 leaves both pyrolysis fields missing. The `70 °C` value appearing in the secondary compilation is **not** treated as a pyrolysis temperature.

Exact primary Table 2 descriptors are:

- CSB: BET `760.5 m2/g`, pore volume `0.40 cm3/g`, mean pore diameter `2.1 nm`
- Fe-CSB: BET `547.0 m2/g`, pore volume `0.32 cm3/g`, mean pore diameter `2.3 nm`

Table 1 supplies exact elemental composition used in staging. Fe-CSB was prepared by immersing pretreated CSB in `0.5 M FeCl3` at 80 °C for 6 h, followed by washing/drying; this modification is recorded without inventing the unknown parent-biochar pyrolysis conditions.

Two Zhong rows are staged. The other 73 secondary packet rows remain unadmitted.

## 4. Feng et al. 2022 — PRIMARY/SECONDARY DISCREPANCY

**DOI:** `10.3390/ijerph19127227`

**Title:** *Oyster Shell Modified Tobacco Straw Biochar: Efficient Phosphate Adsorption at Wide Range of pH Values*

The candidate secondary packet reports approximately `38–49 mg/g` across pH 3–11 at `150 mg/L`, while the primary article states substantially higher adsorption in the same pH range (approximately `75–96 mg P/g`, with acidic conditions around `93–96 mg P/g`). This difference is too large to treat as ordinary digitization noise.

No Feng packet row is admitted until species basis, mass-balance conversion and primary-figure extraction are reconciled. The fitted Langmuir maximum near `88.64 mg P/g` remains excluded as a V3 observed target.

## 5. Tao et al. 2020 — DIRECT QE VALUES FOUND, CONDITIONS INCOMPLETE

**DOI:** `10.3390/ma13040816`

**Title:** *Synthesis of Fe/Mg-Biochar Nanocomposites for Phosphate Removal*

The primary article directly states no-coexisting-anion Figure 9 equilibrium capacities of `0.45`, `0.75`, and `2.12 mg/g` for WBC10, WBC11, and WBC12. It verifies `50 mg/L` phosphate, `0.05 g` in `25 mL` (`2 g/L`), `30 °C`, and `120 rpm`. However, the specific pH and final contact time of that Figure 9 experiment are not explicitly reported. Those mandatory fields are not borrowed from neighbouring experiments or the secondary compilation.

No Tao row is staged. Table 2 fitted kinetic `qe` and Table 3 `qmax` remain excluded targets.

## 6. Current staging count

- primary-verified staging rows: **7**
- independent primary studies represented: **3**
- Evidence Class A rows: **5**
- Evidence Class B rows: **2**
- rows released for modelling: **0**
- model training performed: **none**

Study shares in the seven-row staging pilot are Son `3/7 = 42.86%`, Qin `2/7 = 28.57%`, and Zhong `2/7 = 28.57%`. These are not modelling proportions; they simply reflect the small verified pilot. The predeclared development target of at least 30 independent verified studies remains unchanged.

## 7. Next verification priority

1. Continue through the remaining open-access packets and increase independent-study depth.
2. Prefer exact observed primary values and deterministic Class B derivations over secondary digitization.
3. Keep Tao and Feng blocked until their specific unresolved issues are closed.
4. Preserve missing primary descriptors rather than borrowing values from secondary compilations.
5. Run a staging-only integrity gate now that three independent verified studies exist.
6. Do not train any predictive model until the full curation, lineage and population-freeze gates are satisfied.
