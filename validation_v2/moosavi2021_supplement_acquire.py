"""Acquire and inspect the open Moosavi et al. 2021 supplementary dataset.

The script retrieves only openly distributed PMC/MDPI resources, records the exact
source URL and SHA-256, and inspects tabular supplementary files. It does not run
any model. Primary-study grouping is blocked until the recovered table itself or
primary evidence supports row-level/block-level provenance.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin, urlparse
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
KNOWN_SUPPLEMENT_URL = "https://pmc.ncbi.nlm.nih.gov/articles/instance/8540925/bin/nanomaterials-11-02734-s001.zip"
OA_API = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={PMCID}"
ARTICLE_PAGE = f"https://pmc.ncbi.nlm.nih.gov/articles/{PMCID}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; adsorption-reproducibility-audit/1.0; +https://github.com/Martin-do/)"
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name or "resource.bin")


def inspect_tabular_bytes(name: str, b: bytes):
    """Return structural inventory and a small header/sample record for tabular bytes."""
    inventory = []
    samples = []
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
                preview = df.head(10).copy()
                preview.insert(0, "__sheet", sheet)
                samples.append(preview)
        elif low.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(b))
            inventory.append({
                "file": name,
                "sheet": "",
                "rows": len(df),
                "columns": "|".join(map(str, df.columns)),
            })
            preview = df.head(10).copy()
            preview.insert(0, "__sheet", "")
            samples.append(preview)
    except Exception as exc:
        inventory.append({
            "file": name,
            "sheet": "<inspection_error>",
            "rows": None,
            "columns": repr(exc),
        })
    return inventory, samples


def persist_member(name: str, b: bytes, inventory: list, sample_frames: list, members: list, parent: str):
    members.append({"archive": parent, "member": name, "bytes": len(b), "sha256": sha256_bytes(b)})
    low = name.lower()
    if low.endswith((".xlsx", ".xls", ".csv")):
        inv, previews = inspect_tabular_bytes(name, b)
        inventory.extend(inv)
        sample_frames.extend(previews)
        if len(b) <= 20_000_000:
            (OUT / safe_name(name)).write_bytes(b)
    elif "s001" in low and len(b) <= 20_000_000:
        # Preserve the exact supplementary payload even if it is not tabular.
        (OUT / safe_name(name)).write_bytes(b)


def inspect_archive(label: str, b: bytes, inventory: list, sample_frames: list, members: list):
    """Inspect zip or tar/tgz bytes recursively enough to expose supplementary tables."""
    bio = io.BytesIO(b)
    if zipfile.is_zipfile(bio):
        with zipfile.ZipFile(io.BytesIO(b)) as zf:
            for member in zf.infolist():
                if member.is_dir():
                    continue
                mb = zf.read(member.filename)
                persist_member(member.filename, mb, inventory, sample_frames, members, label)
        return True
    try:
        with tarfile.open(fileobj=io.BytesIO(b), mode="r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                f = tf.extractfile(member)
                if f is None:
                    continue
                mb = f.read()
                persist_member(member.name, mb, inventory, sample_frames, members, label)
        return True
    except tarfile.TarError:
        return False


def request_record(session: requests.Session, url: str, label: str):
    try:
        r = session.get(url, timeout=60, allow_redirects=True)
        b = r.content
        return {
            "label": label,
            "url": url,
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


def oa_package_url(session: requests.Session, manifest: list):
    rec, response = request_record(session, OA_API, "pmc_oa_api")
    manifest.append(rec)
    if response is None or not response.ok:
        return None
    (OUT / "pmc_oa_api_response.xml").write_bytes(response.content)
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        return None
    for link in root.findall(".//link"):
        fmt = (link.attrib.get("format") or "").lower()
        href = link.attrib.get("href")
        if href and fmt in {"tgz", "tar.gz"}:
            if href.startswith("ftp://"):
                href = "https://" + href[len("ftp://"):]
            return href
    return None


def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    manifest = []
    archive_members = []
    tabular_inventory = []
    sample_frames = []

    # 1. Verify the public article page and exact supplementary link retained by PMC.
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
    pd.DataFrame(discovered_links).to_csv(OUT / "moosavi2021_discovered_supplement_links.csv", index=False)

    # 2. Try the exact supplementary URL. PMC sometimes returns an HTML browser
    # interstitial; this attempt is recorded but is not the only acquisition route.
    direct_rec, direct_resp = request_record(session, KNOWN_SUPPLEMENT_URL, "pmc_direct_s001")
    manifest.append(direct_rec)
    direct_acquired = False
    if direct_resp is not None and direct_resp.ok:
        b = direct_resp.content
        if zipfile.is_zipfile(io.BytesIO(b)) or tarfile.is_tarfile(fileobj := None) if False else False:
            pass
        if zipfile.is_zipfile(io.BytesIO(b)):
            (OUT / "nanomaterials-11-02734-s001.zip").write_bytes(b)
            direct_acquired = inspect_archive("nanomaterials-11-02734-s001.zip", b, tabular_inventory, sample_frames, archive_members)
        elif "html" in direct_resp.headers.get("content-type", "").lower():
            (OUT / "pmc_direct_s001_interstitial.html").write_bytes(b)

    # 3. Canonical fallback: PMC Open Access package API. This returns a stable OA
    # archival package containing manuscript and supplementary files for CC-BY articles.
    package_url = oa_package_url(session, manifest)
    package_acquired = False
    package_sha = None
    if package_url:
        package_rec, package_resp = request_record(session, package_url, "pmc_oa_package")
        manifest.append(package_rec)
        if package_resp is not None and package_resp.ok:
            pb = package_resp.content
            package_sha = sha256_bytes(pb)
            (OUT / "pmc_oa_package.tar.gz").write_bytes(pb)
            package_acquired = inspect_archive("pmc_oa_package.tar.gz", pb, tabular_inventory, sample_frames, archive_members)

    pd.DataFrame(manifest).to_csv(OUT / "moosavi2021_download_manifest.csv", index=False)
    pd.DataFrame(archive_members).to_csv(OUT / "moosavi2021_archive_members.csv", index=False)
    pd.DataFrame(tabular_inventory).to_csv(OUT / "moosavi2021_tabular_inventory.csv", index=False)
    if sample_frames:
        pd.concat(sample_frames, ignore_index=True, sort=False).to_csv(OUT / "moosavi2021_tabular_previews.csv", index=False)
    else:
        pd.DataFrame().to_csv(OUT / "moosavi2021_tabular_previews.csv", index=False)

    s001_members = [m for m in archive_members if "s001" in m["member"].lower()]
    sourceish_columns = []
    for inv in tabular_inventory:
        cols = str(inv.get("columns", "")).split("|")
        for col in cols:
            low = col.lower().strip()
            if any(k in low for k in ["ref", "reference", "source", "study", "doi", "author", "literature"]):
                sourceish_columns.append(col)

    summary = {
        "pmcid": PMCID,
        "known_supplement_url": KNOWN_SUPPLEMENT_URL,
        "oa_package_url": package_url,
        "direct_supplement_acquired": direct_acquired,
        "oa_package_acquired": package_acquired,
        "oa_package_sha256": package_sha,
        "archive_members": len(archive_members),
        "s001_members": len(s001_members),
        "tabular_objects": len(tabular_inventory),
        "candidate_source_columns": sorted(set(sourceish_columns)),
        "model_run": False,
        "grouping_ready": bool(tabular_inventory and sourceish_columns),
        "next_gate": (
            "Inspect explicit source/reference column and validate mapping against cited primary studies before grouped CV."
            if tabular_inventory and sourceish_columns
            else "Use recovered supplementary table plus cited primary studies to reconstruct provenance; do not infer study IDs from material names alone."
        ),
    }
    (OUT / "moosavi2021_acquisition_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if archive_members:
        print("\nSupplement-related members:")
        print(pd.DataFrame(s001_members if s001_members else archive_members).head(100).to_string(index=False))
    if tabular_inventory:
        print("\nTabular inventory:")
        print(pd.DataFrame(tabular_inventory).to_string(index=False))


if __name__ == "__main__":
    main()
