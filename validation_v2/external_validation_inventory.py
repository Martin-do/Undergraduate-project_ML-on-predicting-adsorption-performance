"""Forensic inventory of legacy external-validation assets and notebook code.

The purpose is source reconstruction, not model evaluation. It scans repository
notebooks for external-validation code/URLs/filenames and summarizes workbook
schemas so Shen/Jaffari assets are identified from evidence rather than guessed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

TERMS = [
    "external", "shen", "jaffari", "biochar", "validation", "read_excel",
    "read_csv", "http", "drive.google", "github", "dataset", "525", "3673",
    "-18.785", "-16.097", "696.09", "303.55",
]
FILE_RE = re.compile(r"[^\s'\"]+\.(?:csv|xlsx|xls|json|pkl|joblib)", re.I)
URL_RE = re.compile(r"https?://[^\s'\"<>]+", re.I)


def cell_source(cell: dict) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else str(src)


def output_text(cell: dict) -> str:
    parts = []
    for out in cell.get("outputs", []) or []:
        txt = out.get("text")
        if txt:
            parts.append("".join(txt) if isinstance(txt, list) else str(txt))
        data = out.get("data") or {}
        for key in ("text/plain", "text/html"):
            if key in data:
                val = data[key]
                parts.append("".join(val) if isinstance(val, list) else str(val))
    return "\n".join(parts)


def notebook_inventory() -> tuple[pd.DataFrame, dict]:
    rows = []
    assets = {"urls": set(), "files": set()}
    for nb_path in sorted(ROOT.glob("*.ipynb")):
        try:
            nb = json.loads(nb_path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({"notebook": nb_path.name, "cell_index": -1, "cell_type": "ERROR", "matched_terms": "", "source": str(exc), "output": ""})
            continue
        for idx, cell in enumerate(nb.get("cells", [])):
            src = cell_source(cell)
            out = output_text(cell)
            blob = f"{src}\n{out}"
            lower = blob.lower()
            matched = [t for t in TERMS if t.lower() in lower]
            urls = URL_RE.findall(blob)
            files = FILE_RE.findall(blob)
            assets["urls"].update(urls)
            assets["files"].update(files)
            # Capture context if explicitly external/source-related or if it contains
            # one of the legacy numerical fingerprints.
            if matched and any(t in matched for t in [
                "external", "shen", "jaffari", "525", "3673", "-18.785",
                "-16.097", "696.09", "303.55", "read_excel", "read_csv", "http"
            ]):
                rows.append({
                    "notebook": nb_path.name,
                    "cell_index": idx,
                    "cell_type": cell.get("cell_type", ""),
                    "matched_terms": " | ".join(matched),
                    "source": src[:12000],
                    "output": out[:12000],
                })
    return pd.DataFrame(rows), {k: sorted(v) for k, v in assets.items()}


def workbook_inventory() -> pd.DataFrame:
    rows = []
    paths = sorted(list(ROOT.glob("*.xlsx")) + list(ROOT.glob("*.xls")) + list(ROOT.glob("*.csv")))
    for path in paths:
        if path.name == "final_final_adsorption_done_dataset.csv":
            # Include schema/count but avoid dumping project-data values.
            try:
                df = pd.read_csv(path)
                rows.append({
                    "file": path.name, "sheet": "csv", "rows": len(df), "columns": len(df.columns),
                    "column_names": " | ".join(map(str, df.columns)), "error": "",
                })
            except Exception as exc:
                rows.append({"file": path.name, "sheet": "csv", "rows": None, "columns": None, "column_names": "", "error": str(exc)})
            continue
        try:
            if path.suffix.lower() == ".csv":
                df = pd.read_csv(path)
                rows.append({
                    "file": path.name, "sheet": "csv", "rows": len(df), "columns": len(df.columns),
                    "column_names": " | ".join(map(str, df.columns)), "error": "",
                })
            else:
                book = pd.ExcelFile(path)
                for sheet in book.sheet_names:
                    try:
                        df = pd.read_excel(path, sheet_name=sheet)
                        rows.append({
                            "file": path.name, "sheet": sheet, "rows": len(df), "columns": len(df.columns),
                            "column_names": " | ".join(map(str, df.columns)), "error": "",
                        })
                    except Exception as exc:
                        rows.append({"file": path.name, "sheet": sheet, "rows": None, "columns": None, "column_names": "", "error": str(exc)})
        except Exception as exc:
            rows.append({"file": path.name, "sheet": "", "rows": None, "columns": None, "column_names": "", "error": str(exc)})
    return pd.DataFrame(rows)


def main() -> None:
    notebook_rows, assets = notebook_inventory()
    workbooks = workbook_inventory()
    notebook_rows.to_csv(OUT / "external_validation_notebook_cells.csv", index=False)
    workbooks.to_csv(OUT / "external_validation_repo_data_inventory.csv", index=False)
    (OUT / "external_validation_referenced_assets.json").write_text(
        json.dumps(assets, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=== REFERENCED ASSETS ===")
    print(json.dumps(assets, indent=2, ensure_ascii=False))
    print("\n=== REPOSITORY DATA INVENTORY ===")
    print(workbooks.to_string(index=False))
    print("\n=== EXTERNAL-RELATED NOTEBOOK CELLS ===")
    if notebook_rows.empty:
        print("None found")
    else:
        for _, row in notebook_rows.iterrows():
            print(f"\n--- {row['notebook']} cell {row['cell_index']} [{row['matched_terms']}] ---")
            print(row["source"])
            if row["output"]:
                print("OUTPUT:")
                print(row["output"])


if __name__ == "__main__":
    main()
