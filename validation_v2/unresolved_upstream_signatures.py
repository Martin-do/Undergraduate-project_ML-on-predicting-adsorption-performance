"""Print full upstream fingerprints for unresolved inherited adsorbent families."""
from __future__ import annotations
import json, urllib.request
from pathlib import Path
import pandas as pd
import upstream_workbook_inventory as inv

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
MAP = Path(__file__).resolve().parent / "primary_study_map.csv"
URL = inv.FILES["adsorption_regeneration"]


def main():
    mapping = pd.read_csv(MAP, keep_default_na=False)
    unresolved = set(mapping.loc[mapping['status'].eq('unresolved'), 'project_adsorbent'])
    req = urllib.request.Request(URL, headers={'User-Agent':'ID-SEAD-provenance-audit'})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = inv.parse_xlsx(r.read())
    df = pd.DataFrame(rows)
    ads_col = inv.detect_col(df.columns.tolist(), ['adsorbent'])
    dye_col = inv.detect_col(df.columns.tolist(), ['dye'])
    if not ads_col:
        raise RuntimeError('Adsorbent column not found')

    # Include collapsed crab-shell aliases only for context; unresolved families use exact names.
    x = df[df[ads_col].astype(str).isin(unresolved)].copy()
    x.to_csv(OUT / 'unresolved_upstream_rows.csv', index=False)

    summary = {}
    for ads, g in x.groupby(ads_col, sort=True):
        fields = {}
        for c in df.columns:
            vals = [str(v).strip() for v in g[c].tolist() if str(v).strip() and str(v).strip().lower() != 'nan']
            uniq = list(dict.fromkeys(vals))
            if uniq:
                fields[c] = uniq[:30]
        summary[str(ads)] = {'rows': int(len(g)), 'fields': fields}

    (OUT / 'unresolved_upstream_fingerprints.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8'
    )
    print('=== UNRESOLVED UPSTREAM FINGERPRINTS ===')
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
