# V2 numerical source-of-truth clarification

Status: **authoritative for manuscript reconstruction**

The deterministic CI artifact from run **31880489382** is the sole numerical source of truth for the revised manuscript. It contains **331 result rows**, of which **279 are manuscript-eligible**, and records the locked input hashes.

## External-data correction

Some earlier intermediate Markdown notes recorded a Liu external-analysis size of 578 rows. That value is **superseded**.

Direct local reconciliation against the exported source workbook used by the locked CI run confirms:

- `Biochar_dye_filtered.xlsx` SHA-256: `2a7219c309fe09187e4c3e4ef7f55794051643570fe612fd7c2241a4cd16de11`;
- workbook rows: 685;
- all 685 dye labels map under the V2 molecular-weight dictionary;
- positive finite convertible rows retained by V2: **676**;
- converted-qe rows at or below the retired 624 mg/g legacy threshold: 548;
- V2 applies **no** 624 mg/g target truncation.

The locked external metrics therefore use **N=676 for Liu 2025** and **N=3673 for Jaffari 2023**.

Any earlier Markdown narrative that states N=578 for Liu is historical/intermediate and must not be copied into the manuscript.

## Rule

When a narrative note and `deterministic-result-manifest-v2` disagree, the deterministic manifest plus its locked input hashes takes precedence. Manuscript tables, figures and numerical prose must be generated from that artifact, not from earlier narrative files.
