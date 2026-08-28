"""Evidence-only domain selection gate for Paper 2 V3.

Evaluates source-group retention and descriptor completeness for candidate domains.
No predictive model is fitted and no domain is selected by model score.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import json, zipfile
import requests
import pandas as pd

OUT = Path("paper2_v3/outputs/domain_selection_gate")
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 Paper2-V3-domain-gate/1.0"}
PHOS = "https://raw.githubusercontent.com/Sara-Iftikhar/po4_removal_ml/main/scripts/master_sheet_0802.xlsx"
HEAVY_ZIP = "https://mdpi-res.com/d_attachment/water/water-18-01416/article_deploy/water-18-01416-s001.zip"
DYE = "https://raw.githubusercontent.com/17609858895/ML-predict-biochar-adsorb-dye/main/Biochar_dye_filtered.xlsx"


def get(url):
    r = requests.get(url, headers=UA, timeout=90, allow_redirects=True)
    r.raise_for_status()
    return r.content


def norm_doi(v):
    if pd.isna(v): return None
    s = str(v).strip().lower()
    for p in ["https://doi.org/", "http://doi.org/", "http://dx.doi.org/", "https://dx.doi.org/", "doi:"]:
        s = s.replace(p, "")
    return s.strip() or None


def stats(df, study_col, mask, tier, domain):
    d = df.loc[mask].copy()
    g = d.groupby(study_col).size().sort_values(ascending=False)
    return {
        "domain": domain, "tier": tier, "rows": int(len(d)),
        "studies": int(g.shape[0]),
        "largest_study_rows": int(g.iloc[0]) if len(g) else None,
        "largest_study_share": float(g.iloc[0] / len(d)) if len(g) and len(d) else None,
        "median_rows_per_study": float(g.median()) if len(g) else None,
        "studies_with_ge_10_rows": int((g >= 10).sum()) if len(g) else 0,
        "studies_with_ge_20_rows": int((g >= 20).sum()) if len(g) else 0,
    }

# ---------------- phosphate ----------------
ph = pd.read_excel(BytesIO(get(PHOS)), sheet_name=0).dropna(how="all").reset_index(drop=True)
ph["study_id"] = ph["doi"].map(norm_doi).ffill()
ph["qe_num"] = pd.to_numeric(ph["qe"], errors="coerce")
base = ph["study_id"].notna() & ph["qe_num"].gt(0)

tiers_ph = {
    "P0_source_target_only": [],
    "P1_core_process": ["Feedstock", "Adsorption_time (min)", "Ci_ppm", "solution pH", "loading (g)", "adsorption_temp"],
    "P2_plus_basic_material": ["Feedstock", "Pyrolysis_temp", "Surface area", "Adsorption_time (min)", "Ci_ppm", "solution pH", "loading (g)", "adsorption_temp"],
    "P3_plus_elemental_CO": ["Feedstock", "Pyrolysis_temp", "C", "O", "Surface area", "Adsorption_time (min)", "Ci_ppm", "solution pH", "loading (g)", "adsorption_temp"],
    "P4_published_complete_case": ["Adsorbent", "Feedstock", "Pyrolysis_temp", "Heating rate (oC)", "Pyrolysis_time (min)", "C", "O", "Surface area", "Adsorption_time (min)", "Ci_ppm", "solution pH", "rpm", "Volume (L)", "loading (g)", "adsorption_temp", "Ion Concentration (mM)", "ion_type"],
}
rows = []
for tier, req in tiers_ph.items():
    mask = base.copy()
    if req:
        mask &= ph[req].notna().all(axis=1)
    rows.append(stats(ph, "study_id", mask, tier, "PHOSPHATE_BIOCHAR"))

# Per-study field coverage for source-target eligible rows.
ph_base = ph.loc[base].copy()
ph_fields = ["Feedstock","Pyrolysis_temp","Pyrolysis_time (min)","C","H","O","N","Ash","Surface area","Pore volume","Average pore size","Adsorption_time (min)","Ci_ppm","solution pH","loading (g)","adsorption_temp","Ion Concentration (mM)","ion_type"]
per_study_cov = []
for sid, g in ph_base.groupby("study_id"):
    rec = {"study_id": sid, "rows": len(g)}
    for c in ph_fields:
        rec[c] = float(g[c].notna().mean())
    per_study_cov.append(rec)
pd.DataFrame(per_study_cov).to_csv(OUT / "phosphate_per_study_coverage.csv", index=False)

# Source-block consistency checks.
marker_mask = ph["doi"].notna()
marker_indices = list(ph.index[marker_mask])
block_lengths = []
for i, start in enumerate(marker_indices):
    end = marker_indices[i+1] if i+1 < len(marker_indices) else len(ph)
    block_lengths.append(end-start)
ph_source_checks = {
    "raw_rows": len(ph),
    "doi_marker_rows": int(marker_mask.sum()),
    "unique_normalized_dois": int(ph.loc[marker_mask, "doi"].map(norm_doi).nunique()),
    "ref_nonnull_on_doi_marker_rows": int(ph.loc[marker_mask, "ref"].notna().sum()),
    "first_doi_marker_row_index": int(marker_indices[0]) if marker_indices else None,
    "blocks": len(block_lengths),
    "block_len_min": int(min(block_lengths)), "block_len_median": float(pd.Series(block_lengths).median()), "block_len_max": int(max(block_lengths)),
    "all_rows_mapped_by_forward_fill": bool(ph["study_id"].notna().all()),
}
(OUT / "phosphate_source_block_checks.json").write_text(json.dumps(ph_source_checks, indent=2), encoding="utf-8")

# ---------------- heavy metal Pb/Cd ----------------
zbytes = get(HEAVY_ZIP)
z = zipfile.ZipFile(BytesIO(zbytes))
xlsx = max([n for n in z.namelist() if n.lower().endswith(".xlsx")], key=lambda n: z.getinfo(n).file_size)
hv = pd.read_excel(BytesIO(z.read(xlsx)), sheet_name="Table S1 Original_data").dropna(how="all").reset_index(drop=True)
hv["study_id"] = hv["reference"].astype(str).str.strip().replace({"nan": None})
hv["qe_num"] = pd.to_numeric(hv["qe(mg/g)"], errors="coerce")
hbase = hv["study_id"].notna() & hv["qe_num"].gt(0)

tiers_h = {
    "H0_source_target_only": [],
    "H1_core_process": ["Adsorbent", "Contact time(min）", "Initial concentration(mg/L)", "Solution pH", "Solid–liquid ratio(g/L)", "Adsorption temperature(min)"],
    "H2_plus_basic_material": ["Adsorbent", "Pyrolysis temperature(℃）", "Surface area(m2/g）", "Contact time(min）", "Initial concentration(mg/L)", "Solution pH", "Solid–liquid ratio(g/L)", "Adsorption temperature(min)"],
    "H3_plus_elemental_CO": ["Adsorbent", "Pyrolysis temperature(℃）", "C", "O", "Surface area(m2/g）", "Contact time(min）", "Initial concentration(mg/L)", "Solution pH", "Solid–liquid ratio(g/L)", "Adsorption temperature(min)"],
}
for tier, req in tiers_h.items():
    mask = hbase.copy()
    if req:
        mask &= hv[req].notna().all(axis=1)
    rows.append(stats(hv, "study_id", mask, tier, "HEAVY_METAL_BIOCHAR"))

# Heavy reference audit and coverage.
hg = hv.loc[hbase].groupby("study_id").size().sort_values(ascending=False).rename("rows").reset_index()
hg["share"] = hg["rows"] / int(hbase.sum())
hg.to_csv(OUT / "heavy_metal_reference_group_sizes.csv", index=False)

heavy_fields = ["Adsorbent","Pyrolysis temperature(℃）","Pyrolysis time(min)","C","H","O","N","Ash","Surface area(m2/g）","Pore volume(cm3/g)","Average pore size(nm)","Electronegativity","Ionic Radius","Hydrated Radius","Atomic Weight","Contact time(min）","Initial concentration(mg/L)","Solution pH","Solid–liquid ratio(g/L)","Adsorption temperature(min)","Adsorption type"]
hcov = []
for c in heavy_fields:
    hcov.append({"field": c, "nonnull_fraction": float(hv.loc[hbase, c].notna().mean())})
pd.DataFrame(hcov).to_csv(OUT / "heavy_metal_descriptor_coverage.csv", index=False)

# ---------------- dye public-workbook provenance ----------------
dxls = pd.ExcelFile(BytesIO(get(DYE)))
dye_inventory = []
for sheet in dxls.sheet_names:
    d = pd.read_excel(BytesIO(get(DYE)), sheet_name=sheet).dropna(how="all")
    cols = list(map(str, d.columns))
    source_cols = [c for c in cols if any(k in c.lower() for k in ["ref","doi","source","paper","literature"])]
    dye_inventory.append({"sheet": sheet,"rows":len(d),"columns":len(cols),"source_columns":" | ".join(source_cols)})
pd.DataFrame(dye_inventory).to_csv(OUT / "dye_provenance_inventory.csv", index=False)

# ---------------- comparative gate ----------------
gate = pd.DataFrame(rows)
gate.to_csv(OUT / "domain_tier_retention.csv", index=False)

summary = {
    "phosphate_source_checks": ph_source_checks,
    "phosphate_source_target_studies": int(gate[(gate.domain=="PHOSPHATE_BIOCHAR") & (gate.tier=="P0_source_target_only")].iloc[0].studies),
    "phosphate_core_process_studies": int(gate[(gate.domain=="PHOSPHATE_BIOCHAR") & (gate.tier=="P1_core_process")].iloc[0].studies),
    "heavy_source_target_studies": int(gate[(gate.domain=="HEAVY_METAL_BIOCHAR") & (gate.tier=="H0_source_target_only")].iloc[0].studies),
    "heavy_core_process_studies": int(gate[(gate.domain=="HEAVY_METAL_BIOCHAR") & (gate.tier=="H1_core_process")].iloc[0].studies),
    "dye_workbook_has_row_level_source_column": any(bool(x["source_columns"]) and x["sheet"] != "literature collection" for x in dye_inventory),
    "selection_rule": "No model scores used; compare provenance mapping, independent-study retention, descriptor coherence and external-validation prospects."
}
(OUT / "domain_gate_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

print(gate.to_string(index=False))
print("\n", json.dumps(summary, indent=2))
