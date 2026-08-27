"""Build a conservative primary-study provenance ledger for Liu et al. 2025.

The public workbook lists 20 source DOIs but does not retain a row-level study ID.
This reconstruction uses (a) the workbook's listed-source order, (b) contiguous row
blocks in the logical 668-row adsorption table, and (c) source-specific dye/material
fingerprints checked against the primary literature. It deliberately distinguishes a
strict high-confidence population from an extended source-order sensitivity set.

No model is fitted in this script.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "Biochar_dye_filtered.xlsx"
OUT = Path(__file__).resolve().parent / "outputs" / "multidataset" / "liu2025_primary_provenance"
OUT.mkdir(parents=True, exist_ok=True)

# Excel row numbers include the header in row 1. The logical adsorption table occupies
# rows 2-669 = 668 observations. DOI 12 has no confidently retained logical rows.
SOURCES = [
    dict(source_order=1, doi="10.1007/s42773-022-00140-7", title="Comparative assessment for removal of anionic dye from water by different waste-derived biochar vis a vis reusability of generated sludge", start=2, end=61, confidence="high", evidence="RBBR-only block; four crop-residue biochars; source-specific four-material structure matches primary paper."),
    dict(source_order=2, doi="10.1016/j.biortech.2018.02.094", title="Highly efficient adsorption of dyes by biochar derived from pigments-extracted macroalgae pyrolyzed at different temperature", start=62, end=85, confidence="medium", evidence="Contiguous MG/CV/CR block occurs in listed-source position and matches source dye scope; some material descriptors appear imputed/reused, so retained as extended sensitivity rather than strict primary set."),
    dict(source_order=3, doi="10.1016/j.envpol.2022.120271", title="Adsorption performance and mechanism of cationic and anionic dyes by KOH activated biochar derived from medical waste pyrolysis", start=86, end=117, confidence="high", evidence="Single BET=1379 activated medical-waste biochar block; MB and Reactive Yellow block matches primary paper."),
    dict(source_order=4, doi="10.1016/j.jhazmat.2020.122441", title="Activated biochar derived from Opuntia ficus-indica for the efficient adsorption of malachite green dye, Cu2+ and Ni2+ from water", start=118, end=131, confidence="high", evidence="Malachite-green-only dye subset and Opuntia biochar block in exact listed-source order."),
    dict(source_order=5, doi="10.1016/j.colsurfa.2023.131493", title="Preparation of highly porous nitrogen-doped biochar derived from birch tree wastes with superior dye removal performance", start=132, end=141, confidence="high", evidence="Acid Red 18-only block; two high-surface-area birch-derived materials match primary source scope."),
    dict(source_order=6, doi="10.1007/s13399-022-03546-2", title="The efficiency of aquatic weed-derived biochar in enhanced removal of cationic dyes from aqueous medium", start=142, end=167, confidence="high", evidence="Eichhornia/water-hyacinth biochar block; MB/CV dye scope and C=53.4 fingerprint match primary source."),
    dict(source_order=7, doi="10.1016/j.biortech.2016.11.009", title="Highly efficient adsorption of cationic dye by biochar produced with Korean cabbage waste", start=168, end=203, confidence="high", evidence="Three-biochar block; Congo red and crystal violet exactly match primary paper dye scope."),
    dict(source_order=8, doi="10.1016/j.jenvman.2016.03.043", title="One-step synthesis of a novel N-doped microporous biochar derived from crop straws with high dye adsorption capacity", start=204, end=294, confidence="high", evidence="Seven-material N-doped crop-straw block; Acid Orange 7 and methylene-blue descriptor block matches source scope."),
    dict(source_order=9, doi="10.1016/j.eti.2020.100872", title="One-stage preparation of palm petiole-derived biochar: Characterization and application for adsorption of crystal violet dye in water", start=295, end=321, confidence="high", evidence="Crystal-violet-only block with BET=640 and carbon ~87%, matching primary source fingerprint."),
    dict(source_order=10, doi="10.1016/j.cej.2013.09.074", title="Synthesis, characterization, and dye sorption ability of carbon nanotube-biochar nanocomposites", start=322, end=337, confidence="high", evidence="Four CNT-biochar material block and methylene-blue dye scope match primary source."),
    dict(source_order=11, doi="10.1016/j.seppur.2023.125542", title="High-efficient removal and adsorption mechanism of organic dyes in wastewater by KOH-activated biochar from phenol-formaldehyde resin modified wood", start=338, end=447, confidence="high", evidence="Two KOH/PF-wood biochars with BET=1522.14 and 2301.61; Congo red/MB scope exactly matches primary source."),
    dict(source_order=12, doi="10.1002/sia.6575", title="Corncob-to-xylose residue (CCXR) derived porous biochar as an excellent adsorbent to remove organic dyes from wastewater", start=None, end=None, confidence="unresolved_zero_retained", evidence="Listed source is bibliographically verified, but no retained logical-row interval can be assigned without guessing. It contributes zero rows to grouped analyses."),
    dict(source_order=13, doi="10.1007/s11814-020-0727-7", title="Decolorization of triarylmethane dyes, malachite green, and crystal violet, by sewage sludge biochar: Isotherm, kinetics, and adsorption mechanism comparison", start=448, end=457, confidence="high", evidence="MG/CV sewage-sludge biochar block in exact source-order position."),
    dict(source_order=14, doi="10.1016/j.biortech.2020.124082", title="An abundant porous biochar material derived from wakame (Undaria pinnatifida) with high adsorption performance for three organic dyes", start=458, end=471, confidence="high", evidence="Wakame-derived block with BET=1156.25; retained MB/Rhodamine-B rows fit primary source scope. High-capacity MG observations may not survive the published Q<4 gate; no missing rows are reconstructed."),
    dict(source_order=15, doi="10.1016/j.jclepro.2022.135527", title="Nitrogen-doped magnetic biochar made with K3[Fe(C2O4)3] to adsorb dyes: Experimental approach and density functional theory modeling", start=472, end=491, confidence="medium", evidence="Single BET=1034 magnetic N-doped biochar block; 18/20 decoded rows are Congo red or Rhodamine B as in primary source, while two descriptor-coded rows map to MB. Kept only in extended sensitivity."),
    dict(source_order=16, doi="10.1016/j.envpol.2020.115986", title="Adsorptive removal of cationic methylene blue and anionic Congo red dyes using wet-torrefied microalgal biochar: Equilibrium, kinetic and mechanism modeling", start=492, end=501, confidence="high", evidence="MB/CR wet-torrefied microalgal biochar block matches source dye scope and reported low-capacity range."),
    dict(source_order=17, doi="10.1007/s11356-023-31489-2", title="New and effective cassava bagasse-modified biochar to adsorb Food Red 17 and Acid Blue 9 dyes in a binary mixture", start=502, end=557, confidence="high", evidence="Food Red 17/Acid Blue 9 block with CWb/MCWb BET=136.2/120.6 and PV=0.084/0.076 fingerprints matching primary paper."),
    dict(source_order=18, doi="10.2166/wst.2021.222", title="Activated biochar derived from spent Auricularia auricula substrate for the efficient adsorption of cationic azo dyes from single and binary adsorptive systems", start=558, end=647, confidence="high", evidence="Three Auricularia-substrate biochars with BET=9.123/21.772/89.393; MB/RhB/CV block matches primary source."),
    dict(source_order=19, doi="10.1016/j.arabjc.2023.105080", title="Facile preparation of micro-porous biochar from Bangladeshi sprouted agricultural waste (corncob) via in-house built heating chamber for cationic dye removal", start=648, end=657, confidence="high", evidence="Corncob-biochar MB block; C=78.05 and BET=435.15 fingerprint matches primary source."),
    dict(source_order=20, doi="10.1016/j.ces.2023.119129", title="Synthesis of novel mesoporous selenium-doped biochar with high-performance sodium diclofenac and reactive orange 16 dye removals", start=658, end=669, confidence="high", evidence="Reactive Orange 16 block with Se-doped biochars BET=1207/1300, matching primary source."),
]

MODEL_DESC = ["E", "S", "A", "B", "V"]
LOOKUP_DESC = ["E.1", "S.1", "A.1", "B.1", "V.1"]


def canonical_dye(s):
    if pd.isna(s): return None
    return re.sub(r"\s+", " ", str(s).strip()).lower()


def decode_dyes(orig):
    lookup = {}
    for _, r in orig.iterrows():
        if pd.notna(r.get("TypeDye")) and all(pd.notna(r[c]) for c in LOOKUP_DESC):
            key = tuple(round(float(r[c]), 8) for c in LOOKUP_DESC)
            lookup.setdefault(key, set()).add(canonical_dye(r["TypeDye"]))
    out=[]
    for _, r in orig.iterrows():
        if not all(pd.notna(r[c]) for c in MODEL_DESC):
            out.append(None); continue
        try: key=tuple(round(float(r[c]), 8) for c in MODEL_DESC)
        except Exception:
            out.append(None); continue
        vals=lookup.get(key)
        out.append("|".join(sorted(vals)) if vals else None)
    return out


def main():
    raw=BOOK.read_bytes()
    original=pd.read_excel(BOOK, sheet_name="original")
    processed=pd.read_excel(BOOK, sheet_name="After preprocessing")
    literature=pd.read_excel(BOOK, sheet_name="literature collection", header=None)
    original=original.copy(); processed=processed.copy()
    original.insert(0, "excel_row_1based", range(2,len(original)+2))
    processed.insert(0, "excel_row_1based", range(2,len(processed)+2))
    original["decoded_dye"] = decode_dyes(original)

    # Verify the 20 DOI list exactly in the workbook order.
    listed=[]
    for val in literature.iloc[:,0].dropna().astype(str):
        m=re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", val, re.I)
        if m: listed.append(m.group(0).rstrip(".)]").lower())
    expected=[s["doi"] for s in SOURCES]
    if listed != expected:
        raise ValueError(f"Literature DOI order differs from frozen reconstruction. Listed={listed}")

    # Verify source intervals cover the logical table exactly once, excluding DOI12 zero-row source.
    assigned_rows=[]
    for s in SOURCES:
        if s["start"] is not None:
            assigned_rows.extend(range(s["start"], s["end"]+1))
    if assigned_rows != list(range(2,670)):
        raise ValueError("Source intervals do not provide exact one-to-one coverage of Excel rows 2-669.")

    rows=[]
    for s in SOURCES:
        if s["start"] is None: continue
        for erow in range(s["start"], s["end"]+1):
            i=erow-2
            r=original.iloc[i]
            rows.append({
                "excel_row_1based": erow,
                "logical_row_id": erow-1,
                "source_order": s["source_order"],
                "primary_doi": s["doi"],
                "primary_title": s["title"],
                "mapping_confidence": s["confidence"],
                "mapping_evidence": s["evidence"],
                "decoded_dye": r["decoded_dye"],
                "BET_original": r.get("BET"),
                "C_original": r.get("C"),
                "pH_pzc_original": r.get("pH_pzc"),
                "Q_mmol_g": r.get("Q"),
                "strict_grouped_eligible": s["confidence"] == "high",
                "extended_grouped_eligible": s["confidence"] in {"high","medium"},
            })
    prov=pd.DataFrame(rows)
    prov.to_csv(OUT / "liu2025_primary_study_provenance.csv", index=False)

    ledger=pd.DataFrame(SOURCES)
    ledger["n_retained_rows"]=[0 if s["start"] is None else s["end"]-s["start"]+1 for s in SOURCES]
    ledger.to_csv(OUT / "liu2025_primary_source_ledger.csv", index=False)

    # Explicitly quarantine the malformed/nonlogical spreadsheet tail.
    tail=original[original["excel_row_1based"]>=670].copy()
    tail["exclusion_reason"]="Outside logical 668-row adsorption table; dye descriptor tuple cannot be matched to the workbook dye lookup and raw row structure is malformed/shifted. Not the article's unrecoverable Q>4 source observations."
    tail.to_csv(OUT / "liu2025_quarantined_tail_rows_670_686.csv", index=False)

    # Save exact postprocessed populations used by downstream validation.
    post668=processed.iloc[:668].copy()
    post668["primary_doi"] = prov["primary_doi"].to_numpy()
    post668["mapping_confidence"] = prov["mapping_confidence"].to_numpy()
    post668.to_csv(OUT / "liu2025_model_population_extended_668.csv", index=False)
    post_strict=post668[post668["mapping_confidence"]=="high"].copy()
    post_strict.to_csv(OUT / "liu2025_model_population_strict.csv", index=False)

    group_counts=prov.groupby(["primary_doi","mapping_confidence"]).size().reset_index(name="n_rows")
    group_counts.to_csv(OUT / "liu2025_group_counts.csv", index=False)

    summary={
        "workbook_sha256": hashlib.sha256(raw).hexdigest(),
        "article_claimed_collected_rows":685,
        "article_claimed_model_rows_after_q_gate":668,
        "public_sheet_pandas_rows":len(processed),
        "logical_rows_mapped":len(prov),
        "extended_primary_study_groups":int(prov.primary_doi.nunique()),
        "strict_high_confidence_rows":int(prov.strict_grouped_eligible.sum()),
        "strict_high_confidence_groups":int(prov.loc[prov.strict_grouped_eligible,"primary_doi"].nunique()),
        "medium_confidence_rows":int((prov.mapping_confidence=="medium").sum()),
        "listed_source_with_zero_retained_rows":"10.1002/sia.6575",
        "quarantined_public_tail_rows":len(tail),
        "quarantined_excel_rows":[670,686],
        "q_max_logical_668":float(pd.to_numeric(processed.iloc[:668]["Q"]).max()),
        "model_run":False,
        "primary_analysis_gate":"Use strict high-confidence population; extended 668-row source-order population is a declared sensitivity analysis.",
    }
    (OUT / "liu2025_primary_provenance_summary.json").write_text(json.dumps(summary,indent=2), encoding="utf-8")
    print(json.dumps(summary,indent=2))
    print("\nSource ledger:\n", ledger[["source_order","doi","start","end","confidence","n_retained_rows"]].to_string(index=False))

if __name__=="__main__":
    main()
