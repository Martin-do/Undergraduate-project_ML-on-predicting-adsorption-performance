"""Inventory both public upstream workbooks used by Iftikhar et al.

The authors' loader concatenates `Adsorption and regeneration data_1007c.xlsx`
and `Dyes data.xlsx`. This script identifies where the 24 adsorbent codes in our
dominant block actually occur and whether row-level references are available.
"""
from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "final_final_adsorption_done_dataset.csv"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    "adsorption_regeneration": "https://raw.githubusercontent.com/Sara-Iftikhar/ai4adsorption/main/scripts/Adsorption%20and%20regeneration%20data_1007c.xlsx",
    "dyes": "https://raw.githubusercontent.com/Sara-Iftikhar/ai4adsorption/main/scripts/Dyes%20data.xlsx",
}

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def col_index(ref: str) -> int:
    m = re.match(r"[A-Z]+", ref or "A1")
    n = 0
    for ch in (m.group(0) if m else "A"):
        n = n * 26 + ord(ch) - 64
    return n - 1


def parse_xlsx(blob: bytes) -> list[dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall(f"{{{NS_MAIN}}}si"):
                strings.append("".join(t.text or "" for t in si.iter(f"{{{NS_MAIN}}}t")))

        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        sheets = wb.find(f"{{{NS_MAIN}}}sheets")
        rid = sheets[0].attrib[f"{{{NS_REL}}}id"]
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        target = next(
            r.attrib["Target"] for r in rels.findall(f"{{{NS_PKG_REL}}}Relationship")
            if r.attrib.get("Id") == rid
        )
        sheet_path = target.lstrip("/") if target.startswith("/") else "xl/" + target.lstrip("/")
        root = ET.fromstring(zf.read(sheet_path))

        row_maps = []
        max_idx = 0
        for row in root.iter(f"{{{NS_MAIN}}}row"):
            cells = {}
            for c in row.findall(f"{{{NS_MAIN}}}c"):
                idx = col_index(c.attrib.get("r", "A1")); max_idx = max(max_idx, idx)
                typ = c.attrib.get("t"); val = ""
                if typ == "inlineStr":
                    node = c.find(f"{{{NS_MAIN}}}is")
                    if node is not None:
                        val = "".join(t.text or "" for t in node.iter(f"{{{NS_MAIN}}}t"))
                else:
                    v = c.find(f"{{{NS_MAIN}}}v")
                    if v is not None and v.text is not None:
                        if typ == "s":
                            try: val = strings[int(v.text)]
                            except Exception: val = v.text
                        else: val = v.text
                cells[idx] = val.strip()
            if cells:
                row_maps.append(cells)

    width = max(max(r.keys()) for r in row_maps) + 1
    matrix = [[r.get(i, "") for i in range(width)] for r in row_maps]
    headers = [h.strip() or f"unnamed_{i}" for i, h in enumerate(matrix[0])]
    return [dict(zip(headers, r)) for r in matrix[1:] if any(str(v).strip() for v in r)]


def project_codes() -> set[str]:
    codes = set()
    with DATA.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if "moosavi" in (row.get("source_link") or "").lower():
                if (a := (row.get("adsorbent") or "").strip()): codes.add(a)
    return codes


def detect_col(headers, needles):
    for h in headers:
        n = re.sub(r"[^a-z0-9]+", " ", h.lower()).strip()
        if any(x in n for x in needles): return h
    return None


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", str(s or "").lower())


def main():
    codes = project_codes()
    code_norm = {norm(c): c for c in codes}
    overall = {"project_codes": sorted(codes), "workbooks": {}}

    for name, url in FILES.items():
        req = urllib.request.Request(url, headers={"User-Agent": "ID-SEAD-provenance-audit"})
        with urllib.request.urlopen(req, timeout=30) as resp: blob = resp.read()
        rows = parse_xlsx(blob)
        headers = list(rows[0]) if rows else []
        ads_col = detect_col(headers, ["adsorbent"])
        dye_col = detect_col(headers, ["dye"])
        ref_col = detect_col(headers, ["ref", "reference"])
        values = Counter((r.get(ads_col) or "").strip() for r in rows) if ads_col else Counter()
        exact = {code_norm[norm(v)]: count for v, count in values.items() if norm(v) in code_norm}

        info = {
            "url": url,
            "bytes": len(blob),
            "rows": len(rows),
            "headers": headers,
            "adsorbent_column": ads_col,
            "dye_column": dye_col,
            "reference_column": ref_col,
            "unique_adsorbents": len([v for v in values if v]),
            "matched_project_codes": exact,
            "top_adsorbent_values": values.most_common(80),
        }
        overall["workbooks"][name] = info
        print(f"\n=== {name.upper()} ===")
        print(json.dumps(info, indent=2, ensure_ascii=False))

    (OUT / "upstream_workbook_inventory.json").write_text(
        json.dumps(overall, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
