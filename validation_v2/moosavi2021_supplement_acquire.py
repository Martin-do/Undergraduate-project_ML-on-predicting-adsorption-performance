"""Acquire and inspect the open Moosavi et al. 2021 supplementary dataset.

PMC retired its legacy OA package API in August 2026. This script therefore uses
the current world-readable PMC Article Datasets bucket on AWS, while retaining the
article-page supplementary link as provenance evidence.

No model is run here. Primary-study grouping remains blocked until the recovered
supplement itself or primary evidence supports a defensible mapping.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote, urljoin
import hashlib
import io
import json
import re
import tarfile
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
import requests
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "multidataset" / "moosavi2021_supplement"
OUT.mkdir(parents=True, exist_ok=True)

PMCID = "PMC8540925"
ARTICLE_PAGE = f"https://pmc.ncbi.nlm.nih.gov/articles/{PMCID}/"
KNOWN_SUPPLEMENT_URL = "https://pmc.ncbi.nlm.nih.gov/articles/instance/8540925/bin/nanomaterials-11-02734-s001.zip"
S3_ROOT = "https://pmc-oa-opendata.s3.amazonaws.com"
S3_LIST_URL = S3_ROOT + "/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; adsorption-reproducibility-audit/1.0; +https://github.com/Martin-do/)"
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name or "resource.bin")


def request_record(session: requests.Session, url: str, label: str, params=None):
    try:
        r = session.get(url, params=params, timeout=90, allow_redirects=True)
        b = r.content
        return {
            "label": label,
            "url": r.request.url,
            "final_url": r.url,
            "status": r.status_code,
            "content_type": r.headers.get("content-type", ""),
            "content_disposition": r.headers.get("content-disposition", ""),
            "bytes": len(b),
            "sha256": sha256_bytes(b) if r.ok else "",
            "prefix_hex": b[:16].hex(),
        }, r
    except Exception as exc:
        return {
            "label": label,
            "url": url,
            "final_url": "",
            "status": "ERROR",
            "content_type": "",
            "content_disposition": "",
            "bytes": 0,
            "sha256": "",
            "prefix_hex": "",
            "error": repr(exc),
        }, None


def inspect_tabular_bytes(name: str, b: bytes):
    inventory, samples = [], []
    low = name.lower()
    try:
        if low.endswith((".xlsx", ".xls")):
            xl = pd.ExcelFile(io.BytesIO(b))
            for sheet in xl.sheet_names:
                df = pd.read_excel(io.BytesIO(b), sheet_name=sheet)
                inventory.append({
                    "file": name,
                    "sheet": sheet,
                    "rows": len(df),
                    "columns": "|".join(map(str, df.columns)),
                })
                preview = df.head(12).copy()
                preview.insert(0, "__file", name)
                preview.insert(1, "__sheet", sheet)
                samples.append(preview)
        elif low.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(b))
            inventory.append({
                "file": name,
                "sheet": "",
                "rows": len(df),
                "columns": "|".join(map(str, df.columns)),
            })
            preview = df.head(12).copy()
            preview.insert(0, "__file", name)
            preview.insert(1, "__sheet", "")
            samples.append(preview)
    except Exception as exc:
        inventory.append({
            "file": name,
            "sheet": "<inspection_error>",
            "rows": None,
            "columns": repr(exc),
        })
    return inventory, samples


def persist_payload(name: str, b: bytes, inventory: list, sample_frames: list, members: list, parent: str):
    members.append({"archive": parent, "member": name, "bytes": len(b), "sha256": sha256_bytes(b)})
    low = name.lower()
    if low.endswith((".xlsx", ".xls", ".csv")):
        inv, previews = inspect_tabular_bytes(name, b)
        inventory.extend(inv)
        sample_frames.extend(previews)
        if len(b) <= 25_000_000:
            (OUT / safe_name(name)).write_bytes(b)
    elif any(tag in low for tag in ["s001", "supp", "table_s"]):
        if len(b) <= 25_000_000:
            (OUT / safe_name(name)).write_bytes(b)


def inspect_archive(label: str, b: bytes, inventory: list, sample_frames: list, members: list):
    if zipfile.is_zipfile(io.BytesIO(b)):
        with zipfile.ZipFile(io.BytesIO(b)) as zf:
            for item in zf.infolist():
                if item.is_dir():
                    continue
                mb = zf.read(item.filename)
                persist_payload(item.filename, mb, inventory, sample_frames, members, label)
        return True
    try:
        with tarfile.open(fileobj=io.BytesIO(b), mode="r:*") as tf:
            for item in tf.getmembers():
                if not item.isfile():
                    continue
                fh = tf.extractfile(item)
                if fh is None:
                    continue
                persist_payload(item.name, fh.read(), inventory, sample_frames, members, label)
        return True
    except tarfile.TarError:
        return False


def list_current_pmc_objects(session: requests.Session, manifest: list):
    """List current article-version objects from PMC's public AWS bucket."""
    rec, resp = request_record(
        session,
        S3_LIST_URL,
        "pmc_aws_list",
        params={"list-type": "2", "prefix": f"{PMCID}."},
    )
    manifest.append(rec)
    if resp is None or not resp.ok:
        return []
    (OUT / "pmc_aws_list_response.xml").write_bytes(resp.content)
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        return []
    keys = []
    for elem in root.iter():
        if elem.tag.split("}")[-1] == "Key" and elem.text:
            keys.append(elem.text)
    return sorted(set(keys))


def s3_object_url(key: str) -> str:
    return S3_ROOT + "/" + quote(key, safe="/")


def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    manifest, members, tabular_inventory, sample_frames = [], [], [], []

    # 1. Retain the publisher/PMC linkage evidence.
    page_rec, page_resp = request_record(session, ARTICLE_PAGE, "pmc_article_page")
    manifest.append(page_rec)
    discovered_links = []
    if page_resp is not None and page_resp.ok and "html" in page_resp.headers.get("content-type", "").lower():
        soup = BeautifulSoup(page_resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = urljoin(page_resp.url, a["href"])
            text = " ".join(a.stripped_strings)
            if "s001" in href.lower() or "additional data file" in text.lower():
                discovered_links.append({"text": text, "href": href})
    pd.DataFrame(discovered_links).drop_duplicates().to_csv(
        OUT / "moosavi2021_discovered_supplement_links.csv", index=False
    )

    # 2. Record legacy/direct behavior, but do not depend on it.
    direct_rec, direct_resp = request_record(session, KNOWN_SUPPLEMENT_URL, "pmc_direct_s001")
    manifest.append(direct_rec)
    direct_acquired = False
    if direct_resp is not None and direct_resp.ok:
        db = direct_resp.content
        if zipfile.is_zipfile(io.BytesIO(db)):
            (OUT / "nanomaterials-11-02734-s001.zip").write_bytes(db)
            direct_acquired = inspect_archive(
                "nanomaterials-11-02734-s001.zip", db, tabular_inventory, sample_frames, members
            )
        elif "html" in direct_resp.headers.get("content-type", "").lower():
            (OUT / "pmc_direct_s001_interstitial.html").write_bytes(db)

    # 3. Current PMC distribution mechanism (post-August-2026): AWS article-version objects.
    keys = list_current_pmc_objects(session, manifest)
    pd.DataFrame({"key": keys}).to_csv(OUT / "moosavi2021_pmc_aws_objects.csv", index=False)

    # Download supplement/media/tabular objects. XML/JSON are retained as metadata evidence
    # if small, but PDFs/images are not necessary for the grouping gate.
    selected_keys = []
    for key in keys:
        low = key.lower()
        base = Path(key).name.lower()
        if (
            "s001" in low
            or "supp" in low
            or low.endswith((".xlsx", ".xls", ".csv", ".zip", ".tgz", ".tar.gz"))
            or base == f"{PMCID.lower()}.1.json"
            or base == f"{PMCID.lower()}.1.xml"
        ):
            selected_keys.append(key)

    object_rows = []
    for key in selected_keys:
        rec, resp = request_record(session, s3_object_url(key), f"pmc_aws_object:{Path(key).name}")
        manifest.append(rec)
        object_rows.append({"key": key, **{k: rec.get(k) for k in ["status", "content_type", "bytes", "sha256"]}})
        if resp is None or not resp.ok:
            continue
        b = resp.content
        name = Path(key).name
        low = name.lower()
        if low.endswith((".zip", ".tgz", ".tar.gz")) or zipfile.is_zipfile(io.BytesIO(b)):
            (OUT / safe_name(name)).write_bytes(b)
            inspect_archive(name, b, tabular_inventory, sample_frames, members)
        elif low.endswith((".xlsx", ".xls", ".csv")):
            persist_payload(name, b, tabular_inventory, sample_frames, members, "pmc_aws")
        elif low.endswith((".xml", ".json")) and len(b) <= 5_000_000:
            (OUT / safe_name(name)).write_bytes(b)

    pd.DataFrame(object_rows).to_csv(OUT / "moosavi2021_pmc_aws_selected_objects.csv", index=False)
    pd.DataFrame(manifest).to_csv(OUT / "moosavi2021_download_manifest.csv", index=False)
    pd.DataFrame(members).to_csv(OUT / "moosavi2021_archive_members.csv", index=False)
    pd.DataFrame(tabular_inventory).to_csv(OUT / "moosavi2021_tabular_inventory.csv", index=False)
    if sample_frames:
        pd.concat(sample_frames, ignore_index=True, sort=False).to_csv(
            OUT / "moosavi2021_tabular_previews.csv", index=False
        )
    else:
        pd.DataFrame().to_csv(OUT / "moosavi2021_tabular_previews.csv", index=False)

    sourceish_columns = []
    for inv in tabular_inventory:
        for col in str(inv.get("columns", "")).split("|"):
            low = col.lower().strip()
            if any(token in low for token in ["ref", "reference", "source", "study", "doi", "author", "literature"]):
                sourceish_columns.append(col)

    supplement_keys = [k for k in keys if "s001" in k.lower() or "supp" in k.lower()]
    summary = {
        "pmcid": PMCID,
        "article_page_supplement_link_found": bool(discovered_links),
        "known_supplement_url": KNOWN_SUPPLEMENT_URL,
        "direct_supplement_acquired": direct_acquired,
        "pmc_aws_objects_found": len(keys),
        "pmc_aws_supplement_objects": supplement_keys,
        "pmc_aws_selected_objects": len(selected_keys),
        "tabular_objects": len(tabular_inventory),
        "candidate_source_columns": sorted(set(sourceish_columns)),
        "model_run": False,
        "grouping_ready": bool(tabular_inventory and sourceish_columns),
        "next_gate": (
            "Validate the explicit source/reference field against the cited primary studies before grouped CV."
            if tabular_inventory and sourceish_columns
            else "Inspect the recovered supplementary content and reconstruct row groups only with bibliographic evidence."
        ),
    }
    (OUT / "moosavi2021_acquisition_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if keys:
        print("\nPMC AWS objects:")
        print("\n".join(keys))
    if tabular_inventory:
        print("\nTabular inventory:")
        print(pd.DataFrame(tabular_inventory).to_string(index=False))


if __name__ == "__main__":
    main()
