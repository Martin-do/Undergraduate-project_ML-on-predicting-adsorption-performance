"""Map phosphate discovery rows to their reported extraction/evidence labels.

This script is workload planning only. It does not verify or admit any V3 row and
trains no predictive model.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import json, re
import requests
import pandas as pd

OUT = Path('paper2_v3/outputs/phosphate_extraction_map')
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://raw.githubusercontent.com/Sara-Iftikhar/po4_removal_ml/main/scripts/master_sheet_0802.xlsx'
UA = {'User-Agent': 'Mozilla/5.0 Paper2-V3-extraction-map/1.0'}


def norm_doi(v):
    if pd.isna(v): return None
    s = str(v).strip().lower()
    for p in ['https://doi.org/','http://doi.org/','https://dx.doi.org/','http://dx.doi.org/','doi:']:
        s = s.replace(p,'')
    return s.strip() or None

r = requests.get(URL, headers=UA, timeout=90); r.raise_for_status()
df = pd.read_excel(BytesIO(r.content), sheet_name=0).dropna(how='all').reset_index(drop=True)
df['primary_doi'] = df['doi'].map(norm_doi).ffill()
df['source_ref'] = df['ref'].ffill()

# Identify likely evidence-location columns without assuming their exact names.
evidence_cols = [c for c in df.columns if any(k in str(c).lower() for k in ['fig','table','supp','source','sheet','data from'])]
known = [c for c in ['fig_num','data from', 'data_from', 'source_type', 'sheet'] if c in df.columns]
for c in known:
    if c not in evidence_cols:
        evidence_cols.append(c)

# Preserve raw distinct evidence labels and classify conservatively from text.
def evidence_class(row):
    text = ' | '.join(str(row[c]) for c in evidence_cols if c in row.index and pd.notna(row[c])).lower()
    if not text.strip(): return 'UNSPECIFIED'
    if re.search(r'\btable\b|supp|support|spreadsheet|excel|csv', text): return 'TABLE_OR_SUPPLEMENT_CANDIDATE'
    if re.search(r'\bfig(?:ure)?\b|fig\.|panel|plot|graph', text): return 'FIGURE_CANDIDATE'
    return 'OTHER_OR_UNCLEAR'

df['evidence_class_screen'] = df.apply(evidence_class, axis=1)
if evidence_cols:
    def join_evidence(row):
        return ' | '.join(str(v) for v in row.tolist() if pd.notna(v) and str(v).strip())
    df['evidence_label'] = df[evidence_cols].apply(join_evidence, axis=1)
else:
    df['evidence_label'] = ''

per_source = []
for doi, g in df.groupby('primary_doi', sort=False):
    counts = g['evidence_class_screen'].value_counts().to_dict()
    labels = sorted({x for x in g['evidence_label'].astype(str) if x and x.lower() != 'nan'})
    rec = {
        'primary_doi': doi,
        'source_ref': str(g['source_ref'].iloc[0]),
        'rows': int(len(g)),
        'rows_with_any_evidence_location': int(g[evidence_cols].notna().any(axis=1).sum()) if evidence_cols else 0,
        'figure_candidate_rows': int(counts.get('FIGURE_CANDIDATE',0)),
        'table_or_supp_candidate_rows': int(counts.get('TABLE_OR_SUPPLEMENT_CANDIDATE',0)),
        'other_or_unclear_rows': int(counts.get('OTHER_OR_UNCLEAR',0)),
        'unspecified_rows': int(counts.get('UNSPECIFIED',0)),
        'distinct_evidence_labels': len(labels),
        'evidence_labels_sample': ' || '.join(labels[:15]),
    }
    per_source.append(rec)

pd.DataFrame(per_source).to_csv(OUT/'PHOSPHATE_SOURCE_EXTRACTION_EVIDENCE_MAP.csv', index=False)
summary = {
    'rows': len(df),
    'studies': int(df['primary_doi'].nunique()),
    'evidence_location_columns': list(map(str,evidence_cols)),
    'row_evidence_classes': df['evidence_class_screen'].value_counts().to_dict(),
    'sources_with_any_table_or_supp_candidate': int(sum(x['table_or_supp_candidate_rows']>0 for x in per_source)),
    'sources_with_any_figure_candidate': int(sum(x['figure_candidate_rows']>0 for x in per_source)),
    'sources_with_all_rows_unspecified': int(sum(x['unspecified_rows']==x['rows'] for x in per_source)),
    'warning': 'Classification is workload triage only; primary-source inspection determines final A/B/C/D evidence class.'
}
(OUT/'phosphate_extraction_map_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
print(pd.DataFrame(per_source).sort_values(['table_or_supp_candidate_rows','rows'],ascending=False).head(25).to_string(index=False))
