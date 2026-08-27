"""Deterministically reconstruct Moosavi et al. 2021 Table S1 from the official PMC supplement.

Source
------
Moosavi et al. (2021), Nanomaterials 11, 2734, DOI 10.3390/nano11102734.
Official PMC Article Datasets object:
  s3://pmc-oa-opendata/PMC8540925.1/nanomaterials-11-02734-s001.zip

Important integrity rule
------------------------
The published supplementary PDF visibly jumps from row 339 to row 346. Therefore
rows 340-345 (all expected between Reference 11 and Reference 13) are absent from
the distributed PDF itself; they are not fabricated or imputed here. Boundary rows
that are present in PDF text but missed by table-line detection are recovered only
from the page's embedded text layer.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import io
import json
import re
import zipfile

import numpy as np
import pandas as pd
import pdfplumber
import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "multidataset" / "moosavi2021_table_s1"
OUT.mkdir(parents=True, exist_ok=True)

SUPP_URL = "https://pmc-oa-opendata.s3.amazonaws.com/PMC8540925.1/nanomaterials-11-02734-s001.zip"
EXPECTED_ZIP_SHA256 = "f4e7e58f84bdb4f24fd6a8f570ffb3cecb4c71454a7b6c1d601f43fb480b250d"
EXPECTED_PDF_MEMBER = "nanomaterials-1380363-supplementary.pdf"
EXPECTED_PDF_SHA256 = "e63ceb0e981177d9b283219d9b2383535fac5eae968cdd40cdccf68e21ad4beb"
EXPECTED_SOURCE_ROW_IDS = set(range(1, 351))
SOURCE_PDF_MISSING_IDS = {340, 341, 342, 343, 344, 345}

COLS = [
    "row_id",
    "adsorbent",
    "pyrolysis_temp_c",
    "agrowaste_ph",
    "particle_size_mm",
    "surface_area_m2g",
    "pore_volume_cm3g",
    "adsorption_temp_c",
    "adsorption_ph",
    "dye_type",
    "c0_mgL",
    "qe_mg_g",
    "reference_id",
]
NUMERIC = [c for c in COLS if c not in {"adsorbent", "dye_type"}]

# The 14 bibliography items printed in the source supplement. Table S1's recoverable
# rows use 1-11 and 13. Reference 12's six rows are precisely the source-PDF omission;
# reference 14 is listed in the supplementary bibliography but not used by visible rows.
REFERENCE_CITATIONS = {
    1: "Lu P-J, Lin H-C, Yu W-T, Chern J-M. Chemical regeneration of activated carbon used for dye adsorption. Journal of the Taiwan Institute of Chemical Engineers. 2011;42(2):305-311.",
    2: "Li L, Wu M, Song C, Liu L, Gong W, Ding Y, et al. Efficient removal of cationic dyes via activated carbon with ultrahigh specific surface derived from vinasse wastes. Bioresource Technology. 2020:124540.",
    3: "Wang H, Li Z, Yahyaoui S, Hanafy H, Seliem MK, Bonilla-Petriciolet A, et al. Effective adsorption of dyes on an activated carbon prepared from carboxymethyl cellulose: Experiments, characterization and advanced modelling. Chemical Engineering Journal. 2020:128116.",
    4: "Gao Y, Xu S, Yue Q, Wu Y, Gao B. Chemical preparation of crab shell-based activated carbon with superior adsorption performance for dye removal from wastewater. Journal of the Taiwan Institute of Chemical Engineers. 2016;61:327-335.",
    5: "Wong S, Yac'cob NAN, Ngadi N, Hassan O, Inuwa IM. From pollutant to solution of wastewater pollution: Synthesis of activated carbon from textile sludge for dye adsorption. Chinese Journal of Chemical Engineering. 2018;26(4):870-878.",
    6: "Shokry H, Elkady M, Hamad H. Nano activated carbon from industrial mine coal as adsorbents for removal of dye from simulated textile wastewater: Operational parameters and mechanism study. Journal of Materials Research and Technology. 2019;8(5):4477-4488.",
    7: "Alshabib M, Oluwadamilare MA, Tanimu A, Abdulazeez I, Alhooshani K, Gamal SA. Experimental and DFT investigation of ceria-nanocomposite decorated AC derived from groundnut shell for efficient removal of methylene-blue from wastewater effluent. Applied Surface Science. 2021;536:147749.",
    8: "Mei S, Gu J, Ma T, Li X, Hu Y, Li W, et al. N-doped activated carbon from used dyeing wastewater adsorbent as a metal-free catalyst for acetylene hydrochlorination. Chemical Engineering Journal. 2019;371:118-129.",
    9: "Ravenni G, Cafaggi G, Sarossy Z, Nielsen KR, Ahrenfeldt J, Henriksen U. Waste chars from wood gasification and wastewater sludge pyrolysis compared to commercial activated carbon for the removal of cationic and anionic dyes from aqueous solution. Bioresource Technology Reports. 2020;10:100421.",
    10: "Archin S, Sharifi SH, Asadpour G. Optimization and modeling of simultaneous ultrasound-assisted adsorption of binary dyes using activated carbon from tobacco residues: response surface methodology. Journal of Cleaner Production. 2019;239:118136.",
    11: "Gupta K, Gupta D, Khatri OP. Graphene-like porous carbon nanostructure from Bengal gram bean husk and its application for fast and efficient adsorption of organic dyes. Applied Surface Science. 2019;476:647-657.",
    12: "Rani KM, Palanisamy P, Gayathri S, Tamilselvi S. Adsorptive removal of basic violet dye from aqueous solution by activated carbon prepared from tea dust material. The International Journal of Innovative Research in Science, Engineering and Technology. 2015;4(8):6845-6853.",
    13: "Xiao W, Garba ZN, Sun S, Lawan I, Wang L, Lin M, et al. Preparation and evaluation of an effective activated carbon from white sugar for the adsorption of rhodamine B dye. Journal of Cleaner Production. 2020;253:119989.",
    14: "Mudyawabikwa B, Mungondori HH, Tichagwa L, Katwire DM. Methylene blue removal using a low-cost activated carbon adsorbent from tobacco stems: kinetic and equilibrium studies. Water Science and Technology. 2017;75(10):2390-2402.",
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def download_source() -> tuple[bytes, bytes]:
    r = requests.get(SUPP_URL, timeout=90)
    r.raise_for_status()
    zip_bytes = r.content
    zip_sha = sha256_bytes(zip_bytes)
    if zip_sha != EXPECTED_ZIP_SHA256:
        raise AssertionError(f"Supplement ZIP hash changed: {zip_sha}")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        if EXPECTED_PDF_MEMBER not in zf.namelist():
            raise AssertionError(f"Expected PDF member absent. Members={zf.namelist()}")
        pdf_bytes = zf.read(EXPECTED_PDF_MEMBER)
    pdf_sha = sha256_bytes(pdf_bytes)
    if pdf_sha != EXPECTED_PDF_SHA256:
        raise AssertionError(f"Supplement PDF hash changed: {pdf_sha}")
    return zip_bytes, pdf_bytes


def parse_table_row(row) -> list[str] | None:
    if not row or len(row) < 13 or row[0] is None:
        return None
    if not re.fullmatch(r"\s*\d+\s*", str(row[0])):
        return None
    return ["" if x is None else str(x).strip().replace("\n", " ") for x in row[:13]]


def parse_text_row(line: str) -> list[str] | None:
    """Recover a body row present in the PDF text layer but missed by table extraction.

    The source table has two text fields (adsorbent and dye type). Adsorbent labels
    contain no spaces. Dye labels are one or two tokens (e.g. 'Rhd B'). All other
    fields have fixed numeric positions, so parsing from both ends is deterministic.
    """
    tokens = line.split()
    if len(tokens) < 12 or not tokens[0].isdigit():
        return None
    rid = int(tokens[0])
    if rid < 1 or rid > 350:
        return None
    # id, adsorbent, seven numeric predictors, dye label, C0, qe, reference
    if len(tokens[2:9]) != 7:
        return None
    dye_tokens = tokens[9:-3]
    if not dye_tokens:
        return None
    return [tokens[0], tokens[1], *tokens[2:9], " ".join(dye_tokens), *tokens[-3:]]


def extract_rows(pdf_bytes: bytes) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: dict[int, list[str]] = {}
    provenance = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            # Preferred route: explicit ruled table extraction.
            for table in page.extract_tables():
                for raw_row in table:
                    parsed = parse_table_row(raw_row)
                    if parsed is None:
                        continue
                    rid = int(parsed[0])
                    rows[rid] = parsed
                    provenance.append({"row_id": rid, "page": page_idx, "extraction_route": "pdf_table"})
            # Fallback for the first row after many PDF page boundaries.
            for line in (page.extract_text(x_tolerance=2, y_tolerance=2) or "").splitlines():
                parsed = parse_text_row(line)
                if parsed is None:
                    continue
                rid = int(parsed[0])
                if rid not in rows:
                    rows[rid] = parsed
                    provenance.append({"row_id": rid, "page": page_idx, "extraction_route": "pdf_text_fallback"})

    ordered = [rows[k] for k in sorted(rows)]
    df = pd.DataFrame(ordered, columns=COLS)
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="raise")
    df["row_id"] = df["row_id"].astype(int)
    df["reference_id"] = df["reference_id"].astype(int)
    prov = pd.DataFrame(provenance).sort_values("row_id").drop_duplicates("row_id", keep="first")
    return df, prov


def main():
    zip_bytes, pdf_bytes = download_source()
    (OUT / "nanomaterials-11-02734-s001.zip").write_bytes(zip_bytes)
    (OUT / EXPECTED_PDF_MEMBER).write_bytes(pdf_bytes)

    df, prov = extract_rows(pdf_bytes)
    recovered_ids = set(df["row_id"].tolist())
    missing_ids = EXPECTED_SOURCE_ROW_IDS - recovered_ids
    extras = recovered_ids - EXPECTED_SOURCE_ROW_IDS

    if extras:
        raise AssertionError(f"Unexpected row ids: {sorted(extras)}")
    if missing_ids != SOURCE_PDF_MISSING_IDS:
        raise AssertionError(
            f"Unexpected source-row recovery. Missing={sorted(missing_ids)} expected={sorted(SOURCE_PDF_MISSING_IDS)}"
        )
    if df["row_id"].duplicated().any():
        raise AssertionError("Duplicate recovered row IDs")
    if df.isna().any().any():
        raise AssertionError(f"Missing values in recovered rows: {df.columns[df.isna().any()].tolist()}")

    # Reference 12 is exactly the source-PDF pagination omission. Reference 14 is
    # bibliography-only in the visible table. The recovered table should therefore
    # contain references 1-11 and 13.
    expected_recovered_refs = set(range(1, 12)) | {13}
    recovered_refs = set(df["reference_id"].unique().tolist())
    if recovered_refs != expected_recovered_refs:
        raise AssertionError(f"Unexpected recovered reference IDs: {sorted(recovered_refs)}")

    df.to_csv(OUT / "moosavi2021_table_s1_recovered.csv", index=False)
    prov.to_csv(OUT / "moosavi2021_table_s1_extraction_provenance.csv", index=False)

    ref_counts = (df.groupby("reference_id")
                  .agg(n_rows=("row_id", "size"), first_row=("row_id", "min"), last_row=("row_id", "max"))
                  .reset_index())
    all_refs = pd.DataFrame({
        "reference_id": sorted(REFERENCE_CITATIONS),
        "citation": [REFERENCE_CITATIONS[k] for k in sorted(REFERENCE_CITATIONS)],
    }).merge(ref_counts, on="reference_id", how="left")
    all_refs["n_rows"] = all_refs["n_rows"].fillna(0).astype(int)
    all_refs["source_pdf_status"] = np.where(
        all_refs["reference_id"].eq(12),
        "six numbered rows 340-345 absent from distributed PDF",
        np.where(all_refs["n_rows"].gt(0), "rows recovered", "bibliography entry unused by visible Table S1")
    )
    all_refs.to_csv(OUT / "moosavi2021_reference_map.csv", index=False)

    route_counts = prov.groupby("extraction_route").size().to_dict()
    summary = {
        "doi": "10.3390/nano11102734",
        "official_supplement_url": SUPP_URL,
        "supplement_zip_sha256": sha256_bytes(zip_bytes),
        "supplement_pdf_sha256": sha256_bytes(pdf_bytes),
        "published_claimed_rows": 350,
        "recovered_rows": int(len(df)),
        "source_pdf_missing_row_ids": sorted(missing_ids),
        "source_pdf_missing_count": len(missing_ids),
        "recovered_reference_ids": sorted(recovered_refs),
        "recovered_primary_study_groups": len(recovered_refs),
        "missing_reference_group": 12,
        "reference_14_visible_rows": 0,
        "extraction_routes": {str(k): int(v) for k, v in route_counts.items()},
        "grouping_ready_for_recovered_subset": True,
        "full_350_replication_ready": False,
        "model_run": False,
        "interpretation": "344/350 numbered rows are recoverable from the official distributed supplement. Rows 340-345 are absent from the PDF itself and correspond to the only missing Table-S1 reference group (Reference 12). No values are imputed or invented.",
    }
    (OUT / "moosavi2021_table_s1_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("\nReference counts:\n", all_refs[["reference_id", "n_rows", "first_row", "last_row", "source_pdf_status"]].to_string(index=False))


if __name__ == "__main__":
    main()
