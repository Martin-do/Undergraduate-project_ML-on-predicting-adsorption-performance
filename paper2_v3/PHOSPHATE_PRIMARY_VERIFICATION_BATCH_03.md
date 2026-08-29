# Paper 2 / V3 — Phosphate Primary Verification Batch 03

Date: 2026-08-29
Branch: `paper2/v3-provenance-aware-model-development`
Status: **CURATION ONLY — NO MODEL TRAINING**

## Purpose

Batch 03 extends primary-source verification beyond the first five open-access packets. It does **not** authorize any row for modelling unless the exact observed target and all mandatory V3 conditions can be reconciled to the primary source.

## 1. Park et al. (2015)

DOI: `10.1007/s10653-015-9709-9`

Title: *Evaluation of phosphorus adsorption capacity of sesame straw biochar on aqueous solution: influence of activation methods and pyrolysis temperatures*

Primary full-text evidence is available. The paper reports direct experimental amounts of P adsorbed for the activation-agent comparison, including ZnCl2-activated biochar at 9.39 mg P/g and MgO-activated biochar at 8.42 mg P/g after 24 h with 0.1 g activated biochar and 50 mL of 20 mg P/L solution. The article also reports the corresponding treatment efficiencies and separately reports a Langmuir apparent maximum of 15.46 mg/g.

Important V3 decision: the 9.39 and 8.42 mg P/g values are observed batch amounts and are therefore potentially admissible targets; the 15.46 mg/g Langmuir maximum is **not** an observed target and remains excluded.

However, the activation-agent experiment does not yet provide an unambiguous primary-source value for the initial solution pH in the exact comparison. The 600 °C heating step is also an activation step for KOH/MgO/ZnCl2/K2SO4 treatments and must not be silently encoded as the parent biochar pyrolysis temperature. Therefore **no Park rows are admitted yet**. The study is marked `PRIMARY-VERIFIED — CONDITION RECONCILIATION PENDING`.

Primary evidence supports the study identity, feedstock, activation agents, direct observed adsorption amounts, 24 h contact time, 20 mg P/L initial concentration, 0.1 g/50 mL solid-liquid setup, and the separate fitted Langmuir maximum. citeturn11search0turn8search0

## 2. Cui et al. (2019)

DOI: `10.1039/C9RA02052G`

Title: *Synthesis of a novel magnetic Caragana korshinskii biochar/Mg–Al layered double hydroxide composite and its strong adsorption of phosphate in aqueous solutions*

The RSC article is open access and includes supplementary information. The primary paper explicitly reports a kinetic experimental point of 40.1 mg/g after 2 h and states that this corresponds to approximately 80% of the equilibrium adsorption capacity. It also reports the isotherm conditions and a fitted maximum phosphate sorption capacity of 252.88 mg/g.

V3 decision: the 252.88 mg/g value is a fitted maximum and is excluded. The 40.1 mg/g kinetic observation is a valid primary experimental observation, but it belongs to a kinetic trajectory rather than an explicitly verified equilibrium endpoint. Because the V3 target is canonical equilibrium adsorption capacity, it is **not admitted as q_e**. The study remains `PRIMARY-VERIFIED METADATA — TARGET SEMANTICS BLOCKED` pending identification of an exact experimental equilibrium point in the primary isotherm data.

The primary article provides exact pH, temperature, agitation, dose, solution volume and concentration conditions for the pH, kinetic and isotherm experiments. The isotherm experiment uses 0.05 g FCB/MAC in 50 mL at pH 3 and 25 ± 1 °C for 12 h, with initial concentrations from 5 to 500 mg P/L. citeturn4search0turn4search16

## 3. Xiao et al. (2020)

DOI: `10.1007/s11356-019-07355-5`

Title: *Enhanced removal of phosphate and ammonium by MgO-biochar composites with NH3·H2O hydrolysis pretreatment*

Primary bibliographic identity and study scope are verified. The primary/publicly indexed record reports maximum adsorption capacities of 1.57, 21.8 and 31.3 mg/g for the three phosphate-related material configurations, respectively.

V3 decision: these values are presented as **maximum adsorption capacities**, not automatically as observed equilibrium records. They are therefore excluded from the target staging until the underlying experimental observations and exact conditions are reconciled. Study status: `PRIMARY-VERIFIED METADATA — TARGET SEMANTICS BLOCKED`.

The study is useful for later row-level verification because it reports material properties including pH, CEC, pHpzc, magnesium content, surface area and total pore volume. citeturn7search5turn7search6

## 4. Tang et al. (2019)

DOI: `10.1016/j.scitotenv.2019.01.159`

Title: *Preferable phosphate removal by nano-La(III) hydroxides modified mesoporous rice husk biochars: Role of the host pore structure and point of zero charge*

Primary bibliographic identity and experimental scope are verified. The study concerns La(OH)3-modified mesoporous rice-husk biochars and explicitly evaluates phosphate capture over pH 3–10 and the influence of coexisting Ca2+ and Mg2+.

V3 decision: no target row is admitted in Batch 03 because the accessible search record does not yet expose an exact observed equilibrium q_e together with a complete row-level condition set. Status: `PRIMARY-VERIFIED METADATA — ROW EXTRACTION PENDING`.

The study remains a high-priority verification candidate because its domain and material descriptors are directly relevant to the locked V3 schema. citeturn7search0turn1search6

## 5. Ajmal et al. (2020)

DOI: `10.1016/j.jenvman.2019.109730`

Title: *Probing the efficiency of magnetically modified biomass-derived biochar for effective phosphate removal*

Primary bibliographic identity and scope are verified. The study compares raw and magnetically modified biochars made from local agricultural biomass including wood and rice husks, and reports that magnetic modification increased adsorption while decreasing surface area. The study also reports mechanistic and regeneration experiments.

V3 decision: no row is admitted in Batch 03 because the accessible primary/indexed material does not yet provide a sufficiently precise observed equilibrium target plus complete row-level condition tuple for deterministic staging. Status: `PRIMARY-VERIFIED METADATA — ROW EXTRACTION PENDING`.

The study is retained as a priority candidate for direct full-text extraction. citeturn7search3turn7search4

## Batch 03 decision summary

| Study | DOI | Primary status | V3 row decision |
|---|---|---|---|
| Park et al. 2015 | 10.1007/s10653-015-9709-9 | Full primary text verified | Blocked pending exact pH/condition reconciliation |
| Cui et al. 2019 | 10.1039/C9RA02052G | Full primary text + supplement route verified | Blocked on canonical q_e target semantics |
| Xiao et al. 2020 | 10.1007/s11356-019-07355-5 | Primary bibliographic/abstract evidence verified | Blocked pending observed-row extraction |
| Tang et al. 2019 | 10.1016/j.scitotenv.2019.01.159 | Primary bibliographic/abstract evidence verified | Row extraction pending |
| Ajmal et al. 2020 | 10.1016/j.jenvman.2019.109730 | Primary bibliographic/abstract evidence verified | Row extraction pending |

## Current modelling gate

- Primary-verified staging rows remain: **7**
- Independent primary studies represented in staging: **3**
- Rows released for modelling: **0**
- Model training performed: **none**
- Park: potentially admissible observed targets identified, but blocked on missing/uncertain mandatory condition
- Cui: strong primary source, but fitted q_max and non-equilibrium kinetic points are excluded from q_e
- Xiao/Tang/Ajmal: retained for further row-level extraction

## Next action

Continue primary verification with the highest-yield open/full-text studies, prioritising exact observed equilibrium values with complete condition tuples. Do not increase the staging count merely because a paper reports a fitted maximum adsorption capacity or a kinetic value. The V3 target remains the experimentally observed equilibrium adsorption capacity on the harmonised phosphate mass basis.
