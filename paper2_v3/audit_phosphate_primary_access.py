"""Audit public primary-source access for the 70 phosphate discovery DOIs.

Uses public scholarly metadata APIs only. This does not admit any dataset row.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import json, time, urllib.parse
import requests
import pandas as pd

OUT = Path('paper2_v3/outputs/phosphate_primary_access')
OUT.mkdir(parents=True, exist_ok=True)
MASTER='https://raw.githubusercontent.com/Sara-Iftikhar/po4_removal_ml/main/scripts/master_sheet_0802.xlsx'
UA={'User-Agent':'Paper2-V3-access-audit/1.0 (research reproducibility)'}


def norm_doi(v):
    if pd.isna(v): return None
    s=str(v).strip().lower()
    for p in ['https://doi.org/','http://doi.org/','https://dx.doi.org/','http://dx.doi.org/','doi:']:
        s=s.replace(p,'')
    return s.strip() or None


def get_json(url):
    r=requests.get(url,headers=UA,timeout=45)
    if r.status_code!=200:
        return None, r.status_code
    try:return r.json(),200
    except Exception:return None,200

r=requests.get(MASTER,headers=UA,timeout=90); r.raise_for_status()
df=pd.read_excel(BytesIO(r.content),sheet_name=0).dropna(how='all').reset_index(drop=True)
df['doi_norm']=df['doi'].map(norm_doi)
markers=df[df['doi_norm'].notna()][['doi_norm','ref']].drop_duplicates('doi_norm').reset_index(drop=True)
if len(markers)!=70: raise RuntimeError(f'Expected 70 DOI markers, got {len(markers)}')

rows=[]
for i,row in markers.iterrows():
    doi=row.doi_norm
    rec={'primary_doi':doi,'compilation_ref':row.ref}

    # Crossref metadata
    cr,cs=get_json('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''))
    if cr and cr.get('message'):
        m=cr['message']
        rec['title_crossref']=(m.get('title') or [''])[0]
        rec['publisher']=m.get('publisher','')
        rec['type']=m.get('type','')
        rec['crossref_url']=m.get('URL','')
        date=(m.get('published-print') or m.get('published-online') or m.get('issued') or {}).get('date-parts',[[None]])
        rec['year_crossref']=date[0][0] if date and date[0] else None
        rec['license_urls']=' | '.join(x.get('URL','') for x in (m.get('license') or []))
    rec['crossref_status']=cs

    # OpenAlex: OA and best public location
    oa,os=get_json('https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(doi,safe=''))
    if oa:
        rec['openalex_id']=oa.get('id','')
        rec['is_oa']=bool((oa.get('open_access') or {}).get('is_oa',False))
        rec['oa_status']=(oa.get('open_access') or {}).get('oa_status','')
        rec['oa_url']=(oa.get('open_access') or {}).get('oa_url','') or ''
        best=oa.get('best_oa_location') or {}
        rec['best_oa_landing']=best.get('landing_page_url','') or ''
        rec['best_oa_pdf']=best.get('pdf_url','') or ''
        rec['has_fulltext']=bool(best.get('pdf_url') or best.get('landing_page_url'))
    rec['openalex_status']=os

    # Europe PMC: PMCID/PMC fulltext where present
    ep_query=urllib.parse.quote(f'DOI:{doi}')
    ep,es=get_json(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={ep_query}&format=json&pageSize=5')
    pmcid=''; ep_open=False
    if ep:
        result=(ep.get('resultList') or {}).get('result') or []
        if result:
            hit=result[0]
            pmcid=hit.get('pmcid','') or ''
            ep_open=str(hit.get('isOpenAccess','')).upper()=='Y'
            rec['epmc_title']=hit.get('title','')
            rec['epmc_year']=hit.get('pubYear','')
    rec['pmcid']=pmcid
    rec['europepmc_open_access']=ep_open
    rec['europepmc_status']=es

    # Triage—not verification. OA/PMC sources are prioritized for row verification.
    if pmcid:
        priority='A_PMC_FULLTEXT'
    elif rec.get('best_oa_pdf'):
        priority='B_OA_PDF'
    elif rec.get('is_oa'):
        priority='C_OA_LANDING'
    else:
        priority='D_ACCESS_TO_RESOLVE'
    rec['access_priority']=priority
    rows.append(rec)
    time.sleep(0.05)

out=pd.DataFrame(rows)
out.to_csv(OUT/'PHOSPHATE_PRIMARY_ACCESS_AUDIT_V0.csv',index=False)
summary={
    'dois':len(out),
    'pmcid_count':int(out['pmcid'].fillna('').astype(str).str.len().gt(0).sum()),
    'openalex_oa_count':int(out['is_oa'].fillna(False).astype(bool).sum()),
    'best_oa_pdf_count':int(out['best_oa_pdf'].fillna('').astype(str).str.len().gt(0).sum()),
    'access_priority_counts':out['access_priority'].value_counts().to_dict(),
    'note':'Access classification is triage only. Primary article/supplement inspection remains mandatory before row admission.'
}
(OUT/'phosphate_primary_access_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
print(out[['primary_doi','year_crossref','access_priority','pmcid','title_crossref']].to_string(index=False))
