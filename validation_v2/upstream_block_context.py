"""Audit contiguous source-workbook blocks around unresolved adsorbent families.

This is a provenance aid only. It does not assign primary-study IDs.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pandas as pd

import upstream_workbook_inventory as inv

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
URL = inv.FILES["adsorption_regeneration"]
TARGETS = {"CS", "MC350", "MC400", "MC450", "MC500", "MC550", "MC600"}


def clean(v: object) -> str:
    s = str(v).strip()
    return "" if s.lower() == "nan" else s


def unique_text(series: pd.Series, limit: int = 12) -> str:
    vals = []
    for v in series:
        s = clean(v)
        if s and s not in vals:
            vals.append(s)
    return " | ".join(vals[:limit])


def main() -> None:
    req = urllib.request.Request(URL, headers={"User-Agent": "ID-SEAD-provenance-audit"})
    with urllib.request.urlopen(req, timeout=30) as response:
        df = pd.DataFrame(inv.parse_xlsx(response.read()))

    ads = inv.detect_col(df.columns.tolist(), ["adsorbent"])
    dye = inv.detect_col(df.columns.tolist(), ["dye"])
    pyro = inv.detect_col(df.columns.tolist(), ["calcination_temperature"])
    bet = inv.detect_col(df.columns.tolist(), ["surface area"])
    pore = inv.detect_col(df.columns.tolist(), ["pore volume"])
    qe = inv.detect_col(df.columns.tolist(), ["qe"])
    if not ads:
        raise RuntimeError("Adsorbent column not found")

    # Preserve source row order. Workbook data rows are approximately dataframe index + 2
    # (header occupies the first worksheet row); keep both indices explicit rather than
    # pretending the workbook row is a primary-study identifier.
    df = df.reset_index(drop=True)
    df["source_data_index"] = df.index
    df["approx_excel_row"] = df.index + 2

    run_id = (df[ads].astype(str) != df[ads].astype(str).shift()).cumsum()
    runs = []
    for rid, g in df.groupby(run_id, sort=False):
        runs.append({
            "run_id": int(rid),
            "start_data_index": int(g.index.min()),
            "end_data_index": int(g.index.max()),
            "start_approx_excel_row": int(g["approx_excel_row"].min()),
            "end_approx_excel_row": int(g["approx_excel_row"].max()),
            "adsorbent": clean(g.iloc[0][ads]),
            "rows": int(len(g)),
            "dyes": unique_text(g[dye]) if dye else "",
            "pyrolysis_temperatures": unique_text(g[pyro]) if pyro else "",
            "surface_areas": unique_text(g[bet]) if bet else "",
            "pore_volumes": unique_text(g[pore]) if pore else "",
            "qe_values_preview": unique_text(g[qe], limit=8) if qe else "",
        })
    runs_df = pd.DataFrame(runs)
    runs_df.to_csv(OUT / "upstream_contiguous_adsorbent_runs.csv", index=False)

    target_run_positions = runs_df.index[runs_df["adsorbent"].isin(TARGETS)].tolist()
    context_positions = set()
    for p in target_run_positions:
        context_positions.update(range(max(0, p - 2), min(len(runs_df), p + 3)))
    context = runs_df.iloc[sorted(context_positions)].copy()
    context.to_csv(OUT / "unresolved_block_neighbor_context.csv", index=False)

    target_mask = df[ads].astype(str).isin(TARGETS) | df[ads].astype(str).str.startswith("MC", na=False)
    target_rows = df.loc[target_mask].copy()
    target_rows.to_csv(OUT / "unresolved_mc_cs_block_rows.csv", index=False)

    # Compact family summary includes all MC variants, which can reveal whether the
    # temperature-series rows are part of one larger synthesis/optimization experiment.
    family = []
    fam_df = df[df[ads].astype(str).eq("CS") | df[ads].astype(str).str.startswith("MC", na=False)]
    for name, g in fam_df.groupby(ads, sort=False):
        family.append({
            "adsorbent": str(name),
            "rows": int(len(g)),
            "first_data_index": int(g.index.min()),
            "last_data_index": int(g.index.max()),
            "dyes": unique_text(g[dye]) if dye else "",
            "pyrolysis_temperatures": unique_text(g[pyro]) if pyro else "",
            "surface_areas": unique_text(g[bet]) if bet else "",
            "pore_volumes": unique_text(g[pore]) if pore else "",
            "qe_values_preview": unique_text(g[qe], limit=10) if qe else "",
        })
    family_df = pd.DataFrame(family)
    family_df.to_csv(OUT / "mc_cs_family_context.csv", index=False)

    payload = {
        "target_runs": runs_df[runs_df["adsorbent"].isin(TARGETS)].to_dict("records"),
        "neighbor_context": context.to_dict("records"),
        "mc_cs_family": family_df.to_dict("records"),
        "guardrail": "Row adjacency is provenance evidence only and is never used alone to assign a primary study.",
    }
    (OUT / "upstream_block_context.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("=== UNRESOLVED BLOCK NEIGHBOR CONTEXT ===")
    print(context.to_string(index=False))
    print("\n=== MC + CS FAMILY CONTEXT ===")
    print(family_df.to_string(index=False))


if __name__ == "__main__":
    main()
