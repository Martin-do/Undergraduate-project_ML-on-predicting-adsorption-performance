"""Acquire and inspect the open Moosavi et al. 2021 supplementary dataset.

The script retrieves only openly linked supplementary material and records the exact
source URL and SHA-256. It does not yet run any model. The purpose is to determine
whether Table S1 preserves defensible row-to-primary-study provenance.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin
import hashlib
import io
import json
import re
import zipfile

import pandas as pd
import requests
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "multidataset" / "moosavi2021_supplement"
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC8540925/",
    "https://www.mdpi.com/2079-4991/11/10/2734",
    "https://www.mdpi.com/article/10.3390/nano11102734/s1",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; reproducibility-audit/1.0; +https://github.com/)"}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def candidate_links(page_url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"])
        text = " ".join(a.stripped_strings)
        hay = (href + " " + text).lower()
        if any(k in hay for k in ["supp", "additional data", "s001", ".zip", ".xlsx", ".xls", "nanomaterials-11-02734"]):
            rows.append({"page": page_url, "text": text, "href": href})
    return rows


def inspect_tabular_bytes(name: str, b: bytes):
    records = []
    low = name.lower()
    try:
        if low.endswith((".xlsx", ".xls")):
            xl = pd.ExcelFile(io.BytesIO(b))
            for s in xl.sheet_names:
                df = pd.read_excel(io.BytesIO(b), sheet_name=s)
                records.append({"file": name, "sheet": s, "rows": len(df), "columns": "|".join(map(str, df.columns))})
        elif low.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(b))
            records.append({"file": name, "sheet": "", "rows": len(df), "columns": "|".join(map(str, df.columns))})
    except Exception as e:
        records.append({"file": name, "sheet": "<inspection_error>", "rows": None, "columns": repr(e)})
    return records


def main():
    session = requests.Session()
    session.headers.update(HEADERS)
    page_status = []
    links = []
    for page in PAGES:
        try:
            r = session.get(page, timeout=30, allow_redirects=True)
            page_status.append({"url": page, "final_url": r.url, "status": r.status_code, "content_type": r.headers.get("content-type", ""), "bytes": len(r.content)})
            if "html" in r.headers.get("content-type", "").lower():
                links.extend(candidate_links(r.url, r.text))
            # If /s1 itself is the binary file, retain it as a candidate.
            if r.ok and "html" not in r.headers.get("content-type", "").lower():
                links.append({"page": page, "text": "direct supplementary response", "href": r.url})
        except Exception as e:
            page_status.append({"url": page, "final_url": "", "status": "ERROR", "content_type": "", "bytes": 0, "error": repr(e)})

    pd.DataFrame(page_status).to_csv(OUT / "moosavi2021_page_status.csv", index=False)
    links_df = pd.DataFrame(links).drop_duplicates(subset=["href"]) if links else pd.DataFrame(columns=["page","text","href"])
    links_df.to_csv(OUT / "moosavi2021_candidate_links.csv", index=False)

    downloads = []
    tabular = []
    archive_members = []
    for _, row in links_df.iterrows():
        url = row["href"]
        try:
            r = session.get(url, timeout=60, allow_redirects=True)
            ctype = r.headers.get("content-type", "")
            b = r.content
            # Keep only plausible supplementary binary resources.
            is_zip = b[:4] == b"PK\x03\x04"
            is_excel = is_zip and ("xlsx" in url.lower() or "spreadsheet" in ctype.lower())
            plausible = is_zip or any(x in ctype.lower() for x in ["excel", "zip", "octet-stream"])
            downloads.append({"url": url, "final_url": r.url, "status": r.status_code, "content_type": ctype, "bytes": len(b), "sha256": sha256_bytes(b) if r.ok else "", "plausible_binary": plausible})
            if not r.ok or not plausible:
                continue
            safe = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(r.url.split("?")[0]).name or "supplement.bin")
            path = OUT / safe
            path.write_bytes(b)
            if zipfile.is_zipfile(io.BytesIO(b)):
                with zipfile.ZipFile(io.BytesIO(b)) as z:
                    for member in z.infolist():
                        archive_members.append({"archive": safe, "member": member.filename, "bytes": member.file_size})
                        if member.is_dir():
                            continue
                        mb = z.read(member.filename)
                        tabular.extend(inspect_tabular_bytes(member.filename, mb))
                        # save small/medium tabular files for downstream deterministic audit
                        if len(mb) <= 10_000_000 and member.filename.lower().endswith((".xlsx", ".xls", ".csv")):
                            outname = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(member.filename).name)
                            (OUT / outname).write_bytes(mb)
            else:
                tabular.extend(inspect_tabular_bytes(safe, b))
        except Exception as e:
            downloads.append({"url": url, "final_url": "", "status": "ERROR", "content_type": "", "bytes": 0, "sha256": "", "plausible_binary": False, "error": repr(e)})

    pd.DataFrame(downloads).to_csv(OUT / "moosavi2021_download_manifest.csv", index=False)
    pd.DataFrame(archive_members).to_csv(OUT / "moosavi2021_archive_members.csv", index=False)
    pd.DataFrame(tabular).to_csv(OUT / "moosavi2021_tabular_inventory.csv", index=False)

    summary = {
        "candidate_links": len(links_df),
        "successful_plausible_downloads": sum(bool(x.get("plausible_binary")) and x.get("status") == 200 for x in downloads),
        "archive_members": len(archive_members),
        "tabular_objects": len(tabular),
        "model_run": False,
        "grouping_ready": False,
        "next_gate": "Inspect recovered Table S1 for explicit reference/source columns or reconstructible source blocks before assigning groups.",
    }
    (OUT / "moosavi2021_acquisition_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not links_df.empty:
        print("\nCandidate links:\n", links_df.to_string(index=False))
    if tabular:
        print("\nTabular inventory:\n", pd.DataFrame(tabular).to_string(index=False))


if __name__ == "__main__":
    main()
