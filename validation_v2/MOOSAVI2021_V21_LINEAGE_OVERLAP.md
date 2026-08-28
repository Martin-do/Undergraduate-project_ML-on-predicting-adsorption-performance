# Moosavi 2021 ↔ Dataset V2.1 Lineage-Overlap Audit

Status: **COMPLETE — MOOSAVI IS NOT AN INDEPENDENT EXTERNAL REPLICATION**

## Purpose

The Moosavi et al. 2021 matched random-versus-study-aware analysis was initially treated as a possible independent replication. Before freezing Paper 1's evidence base, its 12 recoverable primary-study groups were compared against the reconstructed primary-study bibliography of Dataset V2.1.

## Result

All **344/344 recoverable Moosavi Table S1 rows** belong to primary-study lineage already represented in the historical V2.1 corpus.

### References already explicitly reconstructed in V2.1

Moosavi Table S1 References **2–11 and 13** map to primary papers already present in the V2.1 bibliography:

| Moosavi ref. | Primary study | Moosavi recoverable rows | V2.1 lineage status |
|---:|---|---:|---|
| 2 | Li et al., vinasse-waste activated carbon | 65 | reconstructed in V2.1 |
| 3 | Wang et al., CMC-derived activated carbon | 56 | reconstructed in V2.1 |
| 4 | Gao et al., crab-shell activated carbon | 26 | reconstructed in V2.1 |
| 5 | Wong et al., textile-sludge activated carbon | 39 | reconstructed in V2.1 |
| 6 | Hassan/Shokry et al., mine-coal activated carbon | 104 | reconstructed in V2.1 |
| 7 | Alshabib et al., groundnut-shell AC | 2 | reconstructed in V2.1 |
| 8 | Mei et al., used dye-adsorbent carbon | 6 | reconstructed in V2.1 |
| 9 | Ravenni et al., waste chars | 14 | reconstructed in V2.1 |
| 10 | Archin et al., tobacco-residue AC | 4 | reconstructed in V2.1 |
| 11 | Gupta et al., Bengal-gram-husk carbon | 10 | reconstructed in V2.1 |
| 13 | Xiao et al., white-sugar-derived AC | 5 | reconstructed in V2.1 |

These groups account for **331/344 recoverable Moosavi rows**.

### Reference 1 and the former CS ambiguity

Moosavi Reference 1 contributes the remaining **13 rows** and is:

Lu P-J, Lin H-C, Yu W-T, Chern J-M. *Chemical regeneration of activated carbon used for dye adsorption*. Journal of the Taiwan Institute of Chemical Engineers 42(2), 305–311 (2011), DOI `10.1016/j.jtice.2010.06.001`.

These 13 rows match the historical `CS` block that Dataset V2.1 deliberately left unresolved. The Moosavi supplement establishes that `CS` denotes coconut-shell granular activated carbon in this lineage. Because V2.1 was frozen before this recovery, the 13 rows remain unresolved in the locked V2.1 source of truth and are not retroactively inserted into its strict analysis.

## Independence disposition

The Moosavi matched result remains scientifically useful because it:

- independently reconstructs the validation gap directly from the official Moosavi supplementary table;
- verifies that the same primary-study hierarchy can materially affect validation performance;
- provides a clean lineage sensitivity with explicit reference groups.

However, it **must not be counted as an independent external confirmation of V2.1**, because the underlying source-study population overlaps completely with the historical V2.1/Iftikhar lineage.

Paper 1 evidence counting therefore treats Moosavi as:

**CI-verified lineage-overlapping matched sensitivity / source-lineage reproduction**

and not as an independent matched benchmark.

## Existing numerical result retained

The previously CI-verified matched metrics are unchanged. For the published nine-variable RF-style specification:

- random five-fold R² = **0.893093**
- primary-study GroupKFold R² = **0.466536**
- ΔR² = **0.426557**
- LOSO R² = **0.462893**

CI run: `33064499878`  
Artifact: `9643154388`  
Artifact SHA-256: `0cb4020bf60eadbf987ba384296a9346298a085352d3885af10d1f5ce83d01a2`

## Integrity rule

This overlap finding changes only the **independence classification**, not the numerical output and not the frozen V2.1 dataset.
