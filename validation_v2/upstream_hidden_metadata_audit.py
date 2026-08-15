"""Inspect discarded/unnamed columns and workbook metadata in the upstream source.

The Iftikhar loader drops Unnamed:16..23 from the first workbook. Before doing
manual literature reconstruction, check whether those cells, hyperlinks,
comments, or external relationships preserve source citations.
"""
from __future__ import annotations

import io
import json
import re
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

import upstream_workbook_inventory as inv

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
URL = inv.FILES["adsorption_regeneration"]


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "ID-SEAD-provenance-audit"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        blob = resp.read()

    rows = inv.parse_xlsx(blob)
    headers = list(rows[0]) if rows else []
    unnamed = [h for h in headers if h.lower().startswith("unnamed_")]

    col_summary = {}
    for col in unnamed:
        vals = [str(r.get(col, "")).strip() for r in rows if str(r.get(col, "")).strip()]
        counts = Counter(vals)
        col_summary[col] = {
            "nonempty_rows": len(vals),
            "unique_values": len(counts),
            "top_values": counts.most_common(80),
        }

    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        names = zf.namelist()
        metadata_files = [
            n for n in names
            if any(k in n.lower() for k in ["comment", "hyperlink", "external", "threadedcomment", "person"])
        ]
        relationship_files = [n for n in names if n.endswith(".rels")]
        relationship_text = {}
        for name in relationship_files:
            text = zf.read(name).decode("utf-8", errors="replace")
            interesting = [
                line.strip() for line in text.splitlines()
                if re.search(r"https?://|doi|external|hyperlink|comment", line, re.I)
            ]
            if interesting:
                relationship_text[name] = interesting[:100]

        # Search all XML-ish workbook parts for DOI/URL/citation-like strings.
        text_hits = {}
        patterns = re.compile(r"doi|https?://|10\.\d{4,9}/|reference|ref\.?|et al\.", re.I)
        for name in names:
            if not name.lower().endswith((".xml", ".rels", ".txt")):
                continue
            try:
                text = zf.read(name).decode("utf-8", errors="replace")
            except Exception:
                continue
            if patterns.search(text):
                snippets = []
                for m in patterns.finditer(text):
                    a = max(0, m.start() - 120); b = min(len(text), m.start() + 500)
                    snippets.append(re.sub(r"\s+", " ", text[a:b]))
                    if len(snippets) >= 40:
                        break
                text_hits[name] = snippets

    result = {
        "workbook_url": URL,
        "unnamed_columns": col_summary,
        "metadata_files": metadata_files,
        "interesting_relationships": relationship_text,
        "citation_like_xml_hits": text_hits,
    }
    (OUT / "upstream_hidden_metadata_audit.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=== DISCARDED UNNAMED COLUMNS ===")
    print(json.dumps(col_summary, indent=2, ensure_ascii=False))
    print("\n=== WORKBOOK METADATA FILES ===")
    print(json.dumps(metadata_files, indent=2, ensure_ascii=False))
    print("\n=== INTERESTING RELATIONSHIPS ===")
    print(json.dumps(relationship_text, indent=2, ensure_ascii=False))
    print("\n=== CITATION-LIKE XML HITS ===")
    print(json.dumps(text_hits, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
