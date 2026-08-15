"""Reconcile the legacy notebook's saved Liu/Shen row count (525) against the
currently committed workbook and the notebook's own executable source.

This script intentionally parses Q_MAX and DYE_MW from ID_SEAD_Master.ipynb rather
than retyping them, then replays the exact external Dataset-A filtering sequence.
It is a forensic reproducibility audit; it does not change V2 preprocessing.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
NB = ROOT / "ID_SEAD_Master.ipynb"
BOOK = ROOT / "Biochar_dye_filtered.xlsx"


def source_text(cell: dict) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else str(src)


def find_cell(nb: dict, needle: str) -> str:
    for cell in nb.get("cells", []):
        src = source_text(cell)
        if needle in src:
            return src
    raise RuntimeError(f"Notebook source cell containing {needle!r} not found")


def literal_assignment(source: str, name: str):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise RuntimeError(f"Literal assignment {name} not found")


def saved_output_count(nb: dict) -> int | None:
    for cell in nb.get("cells", []):
        for output in cell.get("outputs", []) or []:
            txt = output.get("text", "")
            txt = "".join(txt) if isinstance(txt, list) else str(txt)
            marker = "Dataset A loaded: "
            if marker in txt and " rows after filtering" in txt:
                frag = txt.split(marker, 1)[1].split(" rows", 1)[0].strip()
                try:
                    return int(frag)
                except ValueError:
                    pass
    return None


def step_counts(df_pre: pd.DataFrame, df_orig: pd.DataFrame, dye_mw: dict, q_max: float) -> tuple[pd.DataFrame, dict]:
    df = df_pre.copy()
    counts = {"start_rows": int(len(df))}
    df["TypeDye"] = df_orig["TypeDye"].str.lower().str.strip()
    df["dye_mw"] = df["TypeDye"].map(dye_mw)
    counts["mapped_mw_rows"] = int(df["dye_mw"].notna().sum())
    counts["unmapped_mw_rows"] = int(df["dye_mw"].isna().sum())
    counts["unmapped_labels"] = sorted(df.loc[df["dye_mw"].isna(), "TypeDye"].dropna().astype(str).unique().tolist())

    # Exact legacy arithmetic: no custom numeric parser.
    df["qe_mg_g"] = df["Q"] * df["dye_mw"]
    df["c0_mg_L"] = df["C0"] * df["dye_mw"]
    counts["finite_qe_before_dropna"] = int(pd.to_numeric(df["qe_mg_g"], errors="coerce").notna().sum())
    counts["finite_c0_before_dropna"] = int(pd.to_numeric(df["c0_mg_L"], errors="coerce").notna().sum())

    df = df.dropna(subset=["qe_mg_g", "c0_mg_L"])
    counts["after_dropna_qe_c0"] = int(len(df))
    counts["positive_qe_before_qmax"] = int((df["qe_mg_g"] > 0).sum())
    counts[f"positive_qe_le_{q_max:g}"] = int(((df["qe_mg_g"] > 0) & (df["qe_mg_g"] <= q_max)).sum())
    counts["positive_c0_before_qmax"] = int((df["c0_mg_L"] > 0).sum())

    df = df[(df["qe_mg_g"] > 0) & (df["qe_mg_g"] <= q_max)]
    counts["after_qe_filter"] = int(len(df))
    df = df[df["c0_mg_L"] > 0]
    counts["after_c0_filter_exact_legacy"] = int(len(df))
    return df, counts


def threshold_for_count(df_pre: pd.DataFrame, df_orig: pd.DataFrame, dye_mw: dict, target_n: int) -> dict:
    df = df_pre.copy()
    df["TypeDye"] = df_orig["TypeDye"].str.lower().str.strip()
    df["dye_mw"] = df["TypeDye"].map(dye_mw)
    df["qe_mg_g"] = df["Q"] * df["dye_mw"]
    df["c0_mg_L"] = df["C0"] * df["dye_mw"]
    df = df.dropna(subset=["qe_mg_g", "c0_mg_L"])
    df = df[(df["qe_mg_g"] > 0) & (df["c0_mg_L"] > 0)].copy()
    vals = np.sort(df["qe_mg_g"].to_numpy(float))
    out = {"positive_convertible_rows": int(len(vals)), "target_n": int(target_n)}
    if 0 < target_n <= len(vals):
        out["qe_at_target_rank"] = float(vals[target_n - 1])
        out["next_qe_after_target_rank"] = float(vals[target_n]) if target_n < len(vals) else None
        # Count at a few historically plausible round thresholds.
    for threshold in [500, 550, 575, 600, 610, 620, 624, 625, 650, 700]:
        out[f"n_le_{threshold}"] = int(np.sum(vals <= threshold))
    return out


def main() -> None:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    config_cell = find_cell(nb, "Q_MAX")
    mw_cell = find_cell(nb, "DYE_MW =")
    q_max = float(literal_assignment(config_cell, "Q_MAX"))
    dye_mw = literal_assignment(mw_cell, "DYE_MW")
    saved_n = saved_output_count(nb)

    df_pre = pd.read_excel(BOOK, sheet_name="After preprocessing")
    df_orig = pd.read_excel(BOOK, sheet_name="original")
    exact, counts = step_counts(df_pre, df_orig, dye_mw, q_max)
    rank_diag = threshold_for_count(df_pre, df_orig, dye_mw, saved_n or 525)

    # Inspect duplicate/alias keys after the notebook's own strip operation.
    normalized_map = {}
    collisions = {}
    for k, v in dye_mw.items():
        nk = str(k).lower().strip()
        if nk in normalized_map and normalized_map[nk] != v:
            collisions.setdefault(nk, []).append((k, v))
        normalized_map[nk] = v

    audit = {
        "saved_notebook_output_rows": saved_n,
        "parsed_notebook_qmax": q_max,
        "parsed_notebook_mw_key_count": len(dye_mw),
        "normalized_notebook_mw_key_count": len(normalized_map),
        "conflicting_normalized_mw_aliases": collisions,
        "current_committed_workbook_rows": int(len(df_pre)),
        "exact_replay_counts": counts,
        "rank_threshold_diagnostic": rank_diag,
        "exact_replay_matches_saved_output": bool(saved_n == len(exact)),
        "interpretation_if_mismatch": "If the exact currently committed notebook source and workbook do not reproduce the saved output, the output is stale relative to at least one saved input/state. Treat legacy N as an execution artifact rather than a reproducible dataset definition.",
    }

    (OUT / "legacy_liu_rowcount_reconciliation.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    exact[["TypeDye", "Q", "C0", "dye_mw", "qe_mg_g", "c0_mg_L"]].to_csv(
        OUT / "legacy_liu_exact_replay_rows.csv", index=False
    )

    print("=== LEGACY LIU/SHEN ROW-COUNT RECONCILIATION ===")
    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
