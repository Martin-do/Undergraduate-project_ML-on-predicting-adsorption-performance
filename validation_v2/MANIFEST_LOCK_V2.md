# Deterministic V2 evidence manifest — LOCK

Status: **LOCKED for manuscript reconstruction**

Latest successful complete regeneration:

- workflow: `Deterministic result manifest V2`
- run ID: **31880489382**
- scientific/source commit regenerated: **9dc1931720f2163ee32a13aca7ef675ea51d6fea**
- artifact: `deterministic-result-manifest-v2`
- artifact ID: **9245906667**
- artifact SHA-256 digest: **c2fbfdaa1549bdb9655ae9fa1f6647e18625fb99a3d084028e4e2303a87a1a85**
- manifest rows: **331**
- manuscript-eligible rows: **279**

A previous complete run (`31880398376`) had already passed with the same result counts. The second run reproduced the evidence after the revised-scope draft was added, confirming that the documentation change did not alter scientific outputs.

## Locked input hashes

- `final_final_adsorption_done_dataset.csv`
  - `0c071858d6e69ce9b282f0259b4946b9c3d80e307b937b975c529baee629816e`
- `Biochar_dye_filtered.xlsx`
  - `2a7219c309fe09187e4c3e4ef7f55794051643570fe612fd7c2241a4cd16de11`
- `Raw_data.xlsx`
  - `bbcb3e6b89b5186770a25cc89479a819680200895412f52694bc1de13f19a115`
- `validation_v2/primary_study_map.csv`
  - `8d71f187cdcde94aca78849517e131700cc8ff38ad0dfae76553a3db4365e332`
- `validation_v2/adsorbent_domain_map.csv`
  - `f262f94d71e84672b71476e068059c708c71e5b5ed7e93b232aaaf70a120693c`

## Manifest rules

1. Manuscript numerical results must come from the deterministic artifact, not memory/manual transcription.
2. Historical/superseded values may be discussed only as audit history and must not be substituted for V2 results.
3. Inverse-design and universal-QMAX outputs are not manuscript-eligible predictive results.
4. If any scientific script, source dataset, provenance map or domain map changes, the manifest must be regenerated before manuscript numbers are updated.
5. Documentation-only edits do not require a full scientific rerun; CI path filters have been narrowed accordingly.

## Manuscript phase handoff

Scientific validation is now sufficiently locked to begin:

- final table construction;
- figure construction;
- manuscript rewrite under `REVISED_PAPER_SCOPE.md`;
- manuscript-to-manifest reconciliation.
