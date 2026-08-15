"""Recover row-level literature references from the upstream Iftikhar et al. dataset.

The published ai4adsorption loader drops the `Ref` column from `Dyes data.xlsx`
before modelling. This audit downloads the original workbook from the authors'
public GitHub repository, parses the first XLSX worksheet using only Python's
standard library, and emits the reference values associated with the adsorbent
codes present in this project's dominant 251-row block.

This is provenance evidence only. It does not modify the modelling dataset.
"""
from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "final_final_adsorption_done_dataset.csv"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

UPSTREAM_URL = (
    "https://raw.githubusercontent.com/Sara-Iftikhar/ai4adsorption/"
    "main/scripts/Dyes%20data.xlsx"
)

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def col_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref)
    if not letters:
        return 0
    n = 0
    for ch in letters.group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def shared_strings(zf: zipfile.ZipFile) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in zf.namelist():
        return []
    root = ET.fromstring(zf.read(name))
    out = []
    for si in root.findall(f"{{{NS_MAIN}}}si"):
        parts = [t.text or "" for t in si.iter(f"{{{NS_MAIN}}}t")]
        out.append("".join(parts))
    return out


def first_sheet_path(zf: zipfile.ZipFile) -> str:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    sheets = wb.find(f"{{{NS_MAIN}}}sheets")
    if sheets is None or len(sheets) == 0:
        raise RuntimeError("No worksheets found in upstream workbook")
    first = sheets[0]
    rel_id = first.attrib[f"{{{NS_REL}}}id"]

    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    target = None
    for rel in rels.findall(f"{{{NS_PKG_REL}}}Relationship"):
        if rel.attrib.get("Id") == rel_id:
            target = rel.attrib["Target"]
            break
    if not target:
        raise RuntimeError("Could not resolve first worksheet relationship")
    if target.startswith("/"):
        return target.lstrip("/")
    return "xl/" + target.lstrip("/")


def parse_sheet(blob: bytes) -> list[dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        strings = shared_strings(zf)
        sheet_path = first_sheet_path(zf)
        root = ET.fromstring(zf.read(sheet_path))

        rows_raw: list[list[str]] = []
        max_col = 0
        for row in root.iter(f"{{{NS_MAIN}}}row"):
            cells: dict[int, str] = {}
            for c in row.findall(f"{{{NS_MAIN}}}c"):
                idx = col_index(c.attrib.get("r", "A1"))
                max_col = max(max_col, idx)
                typ = c.attrib.get("t")
                value = ""
                if typ == "inlineStr":
                    is_node = c.find(f"{{{NS_MAIN}}}is")
                    if is_node is not None:
                        value = "".join(t.text or "" for t in is_node.iter(f"{{{NS_MAIN}}}t"))
                else:
                    v = c.find(f"{{{NS_MAIN}}}v")
                    if v is not None and v.text is not None:
                        if typ == "s":
                            try:
                                value = strings[int(v.text)]
                            except (ValueError, IndexError):
                                value = v.text
                        else:
                            value = v.text
                cells[idx] = value.strip()
            if cells:
                arr = [""] * (max_col + 1)
                for i, val in cells.items():
                    if i >= len(arr):
                        arr.extend([""] * (i + 1 - len(arr)))
                    arr[i] = val
                rows_raw.append(arr)

    if not rows_raw:
        return []
    width = max(len(r) for r in rows_raw)
    rows_raw = [r + [""] * (width - len(r)) for r in rows_raw]
    headers = [h.strip() or f"unnamed_{i}" for i, h in enumerate(rows_raw[0])]
    return [dict(zip(headers, r)) for r in rows_raw[1:] if any(str(v).strip() for v in r)]


def pick_key(headers: list[str], candidates: list[str]) -> str | None:
    normalized = {re.sub(r"\s+", " ", h.strip().lower()): h for h in headers}
    for c in candidates:
        if c in normalized:
            return normalized[c]
    for norm, original in normalized.items():
        if any(c in norm for c in candidates):
            return original
    return None


def dominant_codes() -> set[str]:
    out = set()
    with DATA.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if "moosavi" in (row.get("source_link") or "").lower():
                code = (row.get("adsorbent") or "").strip()
                if code:
                    out.add(code)
    return out


def main():
    print(f"Downloading upstream workbook: {UPSTREAM_URL}")
    req = urllib.request.Request(UPSTREAM_URL, headers={"User-Agent": "ID-SEAD-provenance-audit"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        blob = resp.read()
    print(f"Downloaded {len(blob)} bytes")

    rows = parse_sheet(blob)
    if not rows:
        raise RuntimeError("Upstream workbook parsed but produced no rows")

    headers = list(rows[0].keys())
    print("Upstream headers:")
    print(json.dumps(headers, indent=2, ensure_ascii=False))

    ads_key = pick_key(headers, ["adsorbent"])
    dye_key = pick_key(headers, ["dye"])
    ref_key = pick_key(headers, ["ref", "reference"])
    adsorption_key = pick_key(headers, ["adsorption", "adsorption capacity"])
    if not ads_key or not ref_key:
        raise RuntimeError(f"Required columns not found. ads={ads_key!r}, ref={ref_key!r}")

    codes = dominant_codes()
    selected = [r for r in rows if (r.get(ads_key) or "").strip() in codes]

    # Preserve all original upstream columns for forensic traceability.
    with (OUT / "iftikhar_upstream_rows_for_dominant_codes.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(selected)

    grouped: dict[tuple[str, str, str], int] = Counter()
    refs_by_ads: dict[str, set[str]] = defaultdict(set)
    for r in selected:
        ads = (r.get(ads_key) or "").strip()
        dye = (r.get(dye_key) or "").strip() if dye_key else ""
        ref = (r.get(ref_key) or "").strip()
        grouped[(ads, dye, ref)] += 1
        if ref:
            refs_by_ads[ads].add(ref)

    summary_rows = [
        {"adsorbent": ads, "dye": dye, "upstream_ref": ref, "rows": n}
        for (ads, dye, ref), n in sorted(grouped.items())
    ]
    with (OUT / "iftikhar_adsorbent_dye_ref_map.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["adsorbent", "dye", "upstream_ref", "rows"])
        w.writeheader()
        w.writerows(summary_rows)

    coverage = {
        "upstream_total_rows": len(rows),
        "project_dominant_codes": len(codes),
        "matched_upstream_rows": len(selected),
        "matched_adsorbent_codes": len({(r.get(ads_key) or "").strip() for r in selected}),
        "adsorbent_key": ads_key,
        "dye_key": dye_key,
        "ref_key": ref_key,
        "adsorption_key": adsorption_key,
        "refs_per_adsorbent": {k: sorted(v) for k, v in sorted(refs_by_ads.items())},
    }
    (OUT / "iftikhar_upstream_ref_coverage.json").write_text(
        json.dumps(coverage, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\n=== UPSTREAM REFERENCE COVERAGE ===")
    print(json.dumps(coverage, indent=2, ensure_ascii=False))
    print("\n=== ADSORBENT / DYE / REF MAP ===")
    for r in summary_rows:
        print(f"{r['adsorbent']:12s} | {r['dye']:18s} | {r['upstream_ref']:20s} | n={r['rows']}")


if __name__ == "__main__":
    main()
