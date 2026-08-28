"""Build source-specific candidate-row packets for primary verification.

Packets are extracted from the public secondary master workbook only to organize
verification. They are NOT V3 data and carry PENDING status throughout.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import re
import requests
import pandas as pd

MASTER='https://raw.githubusercontent.com/Sara-Iftikhar/po4_removal_ml/main/scripts/master_sheet_0802.xlsx'
BATCH=Path('paper2_v3/PHOSPHATE_SOURCE_VERIFICATION_BATCH02_OPEN_ACCESS.csv')
OUT=Path('paper2_v3/outputs/phosphate_verification_packets')
OUT.mkdir(parents=True,exist_ok=True)
UA={'User-Agent':'Paper2-V3-verification-packets/1.0'}


def norm_doi(v):
    if pd.isna(v): return None
    s=str(v).strip().lower()
    for p in ['https://doi.org/','http://doi.org/','https://dx.doi.org/','http://dx.doi.org/','doi:']:
        s=s.replace(p,'')
    return s.strip() or None

r=requests.get(MASTER,headers=UA,timeout=90); r.raise_for_status()
df=pd.read_excel(BytesIO(r.content),sheet_name=0).dropna(how='all').reset_index(drop=True)
df['primary_doi']=df['doi'].map(norm_doi).ffill()
df['source_ref']=df['ref'].ffill()
df['secondary_master_row_index']=df.index
batch=pd.read_csv(BATCH)

# Preserve all original columns. Add audit-only fields first.
manifest=[]
for _,b in batch.iterrows():
    doi=norm_doi(b['primary_doi'])
    g=df[df['primary_doi']==doi].copy()
    if len(g)!=int(b['raw_block_rows']):
        raise RuntimeError(f'{doi}: expected {b.raw_block_rows} rows, got {len(g)}')
    g.insert(0,'v3_admission_status','PENDING_PRIMARY_SOURCE_VERIFICATION')
    g.insert(1,'primary_row_verification_status','NOT_VERIFIED')
    g.insert(2,'verification_evidence_class','')
    g.insert(3,'primary_source_location','')
    g.insert(4,'verification_notes','')
    safe=re.sub(r'[^a-zA-Z0-9]+','_',doi).strip('_')
    fn=f'{safe}.csv'
    g.to_csv(OUT/fn,index=False)
    manifest.append({
        'primary_doi':doi,
        'candidate_rows':len(g),
        'positive_qe_rows':int(pd.to_numeric(g['qe'],errors='coerce').gt(0).sum()),
        'rows_with_fig_num':int(g['fig_num'].notna().sum()) if 'fig_num' in g else 0,
        'packet_file':fn,
        'admission_status':'PENDING_PRIMARY_SOURCE_VERIFICATION',
    })

m=pd.DataFrame(manifest)
m.to_csv(OUT/'verification_packet_manifest.csv',index=False)
print(m.to_string(index=False))
print(f'Total candidate rows organized: {m.candidate_rows.sum()} across {len(m)} studies; admitted rows: 0')
