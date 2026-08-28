"""Deep source/provenance feasibility audit for Paper 2 V3 candidates.

No predictive model is trained. The script checks whether scientific study groups can
be reconstructed and whether the exact published modelling population retains enough
independent studies and descriptor coverage.
"""
from __future__ import annotations
from pathlib import Path
from io import BytesIO
import json, re, zipfile
import requests
import pandas as pd

OUT = Path("paper2_v3/outputs/domain_provenance_depth")
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 V3-provenance-audit/1.0"}

PHOS_URL = "https://raw.githubusercontent.com/Sara-Iftikhar/po4_removal_ml/main/scripts/master_sheet_0802.xlsx"
DYE_URL = "https://raw.githubusercontent.com/17609858895/ML-predict-biochar-adsorb-dye/main/Biochar_dye_filtered.xlsx"
MDPI_CANDIDATES = [
    "https://mdpi-res.com/d_attachment/water/water-18-01416/article_deploy/water-18-01416-s001.xlsx",
    "https://mdpi-res.com/d_attachment/water/water-18-01416/article_deploy/water-18-01416-s001.zip",
    "https://mdpi-res.com/d_attachment/water/water-18-01416/article_deploy/water-18-01416-s001.pdf",
    "https://www.mdpi.com/article/10.3390/w18121416/s1",
]


def get_bytes(url):
    return requests.get(url, timeout=60, headers=UA, allow_redirects=True)


def norm_doi(v):
    if pd.isna(v):
        return None
    s = str(v).strip().lower()
    s = s.replace("https://doi.org/", "").replace("http://doi.org/", "").replace("doi:", "").strip()
    return s or None


def unwrap_excel_payload(payload: bytes):
    """Return XLSX bytes from either a direct XLSX or an outer ZIP containing XLSX."""
    if payload[:2] != b"PK":
        return None, "not_zip_or_xlsx"
    z = zipfile.ZipFile(BytesIO(payload))
    names = z.namelist()
    # An XLSX is itself a ZIP with xl/ and [Content_Types].xml.
    if "[Content_Types].xml" in names and any(n.startswith("xl/") for n in names):
        return payload, "direct_xlsx"
    xlsx_names = [n for n in names if n.lower().endswith((".xlsx", ".xlsm")) and not n.startswith("__MACOSX/")]
    if xlsx_names:
        # Prefer the largest workbook when a supplement bundle contains multiple files.
        chosen = max(xlsx_names, key=lambda n: z.getinfo(n).file_size)
        return z.read(chosen), f"outer_zip:{chosen}"
    return None, "zip_without_excel"

# ---------------- phosphate ----------------
r = get_bytes(PHOS_URL); r.raise_for_status()
raw = pd.read_excel(BytesIO(r.content), sheet_name=0)
raw = raw.dropna(how="all").reset_index(drop=True)

for c in ["doi", "ref"]:
    if c not in raw.columns:
        raise RuntimeError(f"Expected phosphate source column {c!r} not present")

# Source markers are intentionally sparse: they appear at source-block boundaries.
raw["doi_marker_norm"] = raw["doi"].map(norm_doi)
raw["doi_ffill"] = raw["doi_marker_norm"].ffill()
raw["ref_ffill"] = raw["ref"].ffill()

marker = raw[raw["doi_marker_norm"].notna()][["doi_marker_norm", "ref"]].copy()
marker.to_csv(OUT / "phosphate_source_markers.csv", index=False)

# Reproduce the public code's default complete-case modelling gate, without model fitting.
features = ['Adsorbent', 'Feedstock', 'Pyrolysis_temp', 'Heating rate (oC)',
            'Pyrolysis_time (min)', 'C', 'O', 'Surface area',
            'Adsorption_time (min)', 'Ci_ppm', 'solution pH', 'rpm',
            'Volume (L)', 'loading (g)', 'adsorption_temp',
            'Ion Concentration (mM)', 'ion_type']
model_cols = features + ['qe']
model_mask = raw[model_cols].notna().all(axis=1) & (pd.to_numeric(raw['qe'], errors='coerce') > 0)
model = raw.loc[model_mask].copy()
model["primary_study_id"] = model["doi_ffill"]

gs = model.groupby("primary_study_id", dropna=False).size().sort_values(ascending=False).rename("rows").reset_index()
gs["share"] = gs["rows"] / len(model)
gs.to_csv(OUT / "phosphate_model_group_sizes.csv", index=False)

phos_summary = {
    "raw_rows": int(len(raw)),
    "raw_columns": int(raw.shape[1]),
    "doi_markers_nonnull": int(raw["doi_marker_norm"].notna().sum()),
    "unique_doi_markers": int(raw["doi_marker_norm"].dropna().nunique()),
    "unique_ref_markers": int(raw["ref"].dropna().astype(str).nunique()),
    "raw_rows_mapped_after_ffill": int(raw["doi_ffill"].notna().sum()),
    "raw_mapping_fraction_after_ffill": float(raw["doi_ffill"].notna().mean()),
    "published_code_complete_case_rows": int(len(model)),
    "model_rows_with_source": int(model["primary_study_id"].notna().sum()),
    "model_source_mapping_fraction": float(model["primary_study_id"].notna().mean()),
    "model_unique_primary_studies": int(model["primary_study_id"].dropna().nunique()),
    "largest_study_rows": int(gs.iloc[0]["rows"]) if len(gs) else None,
    "largest_study_share": float(gs.iloc[0]["share"]) if len(gs) else None,
    "median_rows_per_study": float(gs["rows"].median()) if len(gs) else None,
    "source_mapping_method": "forward-fill sparse DOI block markers in official public master workbook",
}
(OUT / "phosphate_provenance_summary.json").write_text(json.dumps(phos_summary, indent=2), encoding="utf-8")

optional = {
    "H": "H", "N": "N", "S": "S", "Ca": "Ca", "Ash": "Ash",
    "pore_volume": "Pore volume", "pore_size": "Average pore size",
    "efficiency": "efficiency", "final_concentration": "Cf",
}
coverage = []
for logical, col in {**{c:c for c in model_cols}, **optional}.items():
    if col in raw:
        coverage.append({"field": logical, "column": col,
                         "raw_nonnull_fraction": float(raw[col].notna().mean()),
                         "model_subset_nonnull_fraction": float(model[col].notna().mean())})
pd.DataFrame(coverage).to_csv(OUT / "phosphate_descriptor_coverage.csv", index=False)

# ---------------- dye: inspect every sheet for source metadata ----------------
r = get_bytes(DYE_URL); r.raise_for_status()
xls = pd.ExcelFile(BytesIO(r.content))
sheet_rows = []
source_patterns = re.compile(r"ref|reference|doi|source|paper|literature", re.I)
for name in xls.sheet_names:
    d = pd.read_excel(BytesIO(r.content), sheet_name=name)
    d = d.dropna(how="all")
    cols = list(map(str, d.columns))
    source_cols = [c for c in cols if source_patterns.search(c)]
    sheet_rows.append({
        "sheet": name, "rows": int(len(d)), "columns": int(len(cols)),
        "source_candidate_columns": " | ".join(source_cols),
        "all_columns": " | ".join(cols),
    })
pd.DataFrame(sheet_rows).to_csv(OUT / "dye_all_sheet_inventory.csv", index=False)

# ---------------- heavy metal: discover static supplementary payload ----------------
mdpi_log = []
heavy_excel = None
heavy_url = None
heavy_mode = None
for url in MDPI_CANDIDATES:
    try:
        rr = get_bytes(url)
        excel_bytes, mode = unwrap_excel_payload(rr.content) if rr.status_code == 200 else (None, "http_error")
        rec = {"url": url, "status": rr.status_code, "final_url": rr.url,
               "content_type": rr.headers.get("content-type", ""), "bytes": len(rr.content),
               "starts_pk": rr.content[:2] == b"PK", "payload_mode": mode}
        mdpi_log.append(rec)
        if excel_bytes is not None:
            heavy_excel, heavy_url, heavy_mode = excel_bytes, url, mode
            break
    except Exception as e:
        mdpi_log.append({"url": url, "error": repr(e)})

(OUT / "heavy_metal_acquisition_log.json").write_text(json.dumps(mdpi_log, indent=2), encoding="utf-8")

if heavy_excel is not None:
    hx = pd.ExcelFile(BytesIO(heavy_excel))
    inv = []
    for name in hx.sheet_names:
        h = pd.read_excel(BytesIO(heavy_excel), sheet_name=name)
        h = h.dropna(how="all")
        cols = list(map(str, h.columns))
        source_cols = [c for c in cols if source_patterns.search(c)]
        inv.append({"sheet": name, "rows": int(len(h)), "columns": int(len(cols)),
                    "source_candidate_columns": " | ".join(source_cols),
                    "all_columns": " | ".join(cols)})
    pd.DataFrame(inv).to_csv(OUT / "heavy_metal_sheet_inventory.csv", index=False)
    (OUT / "heavy_metal_acquisition_success.json").write_text(
        json.dumps({"url": heavy_url, "mode": heavy_mode}, indent=2), encoding="utf-8")

print(json.dumps(phos_summary, indent=2))
print("\nDye sheets:")
print(pd.DataFrame(sheet_rows)[["sheet","rows","columns","source_candidate_columns"]].to_string(index=False))
print("\nMDPI acquisition attempts:")
print(json.dumps(mdpi_log, indent=2))
