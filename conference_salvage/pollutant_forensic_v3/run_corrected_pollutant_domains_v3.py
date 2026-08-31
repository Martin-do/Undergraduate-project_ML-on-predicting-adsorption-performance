from __future__ import annotations

"""Domain-qualified LOSO after target-blind pollutant-class correction.

This determines whether repairing the pollutant representation changes the prior
strict-agricultural / broad-biogenic / waste-derived-carbon conclusions. Each
scope is fixed by provenance/domain flags created before the model fitting.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone

import run_pollutant_representation_forensic_v3 as forensic

fp = forensic.fp
gate = forensic.gate
DtypeSafeParityPreprocessor = forensic.DtypeSafeParityPreprocessor
OUT = Path(__file__).resolve().parent / "outputs"

SCOPES = {
    "strict_agricultural_waste": ("strict_agricultural_waste_v2", 65, 4),
    "broad_biogenic_waste": ("broad_biogenic_waste_v2", 92, 6),
    "waste_derived_carbon": ("waste_derived_carbon_v2", 138, 7),
}


def main():
    _, strict = gate.load_strict()
    bank = fp.models()
    pooled_rows=[]; study_rows=[]; pred_rows=[]; equal_rows=[]

    with forensic.corrected_pollutant_engineering():
        for scope,(flag,expected_rows,expected_studies) in SCOPES.items():
            data = strict[strict[flag].astype(bool)].copy().reset_index(drop=True)
            nstud = data.primary_study_id_v21.nunique()
            if len(data)!=expected_rows or nstud!=expected_studies:
                raise RuntimeError(f"{scope}: expected {expected_rows}/{expected_studies}, got {len(data)}/{nstud}")
            y=data[gate.base.TARGET].to_numpy(float)
            groups=data.primary_study_id_v21.astype(str).to_numpy()
            raw=data[gate.RAW_MODEL_COLS].copy()
            allpred={m:np.empty(len(data),float) for m in ["RF","XGB"]}
            for study in sorted(np.unique(groups)):
                te=np.flatnonzero(groups==study); tr=np.flatnonzero(groups!=study)
                prep=DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
                xtr=prep.transform(raw.iloc[tr]); xte=prep.transform(raw.iloc[te])
                for model in ["RF","XGB"]:
                    p=clone(bank[model]).fit(xtr,y[tr]).predict(xte)
                    allpred[model][te]=p
                    sm=gate.safe_study_metric(y[te],p)
                    study_rows.append({"scope":scope,"held_out_primary_study":study,"model":model,"n_rows":len(te),**sm})
                    for pos,pp in zip(te,p):
                        pred_rows.append({"scope":scope,"held_out_primary_study":study,"model":model,"row_index":int(pos),"actual_qe_mg_g":float(y[pos]),"predicted_qe_mg_g":float(pp),"abs_error_mg_g":float(abs(y[pos]-pp))})
            for model,p in allpred.items():
                pooled_rows.append({"scope":scope,"model":model,"n_rows":len(data),"n_studies":nstud,**forensic.metric(y,p)})
                ps=pd.DataFrame(study_rows)
                ps=ps[(ps.scope==scope)&(ps.model==model)]
                equal_rows.append({
                    "scope":scope,"model":model,"n_studies":nstud,
                    "mean_study_mae_mg_g":float(ps.mae_mg_g.mean()),
                    "median_study_mae_mg_g":float(ps.mae_mg_g.median()),
                    "mean_study_rmse_mg_g":float(ps.rmse_mg_g.mean()),
                    "median_study_rmse_mg_g":float(ps.rmse_mg_g.median()),
                })

    pooled=pd.DataFrame(pooled_rows); studies=pd.DataFrame(study_rows); preds=pd.DataFrame(pred_rows); equal=pd.DataFrame(equal_rows)
    pooled.to_csv(OUT/"corrected_pollutant_domain_loso_pooled.csv",index=False)
    studies.to_csv(OUT/"corrected_pollutant_domain_loso_per_study.csv",index=False)
    preds.to_csv(OUT/"corrected_pollutant_domain_loso_predictions.csv",index=False)
    equal.to_csv(OUT/"corrected_pollutant_domain_loso_equal_study.csv",index=False)

    alsh=preds[preds.held_out_primary_study.str.contains("Alshabib",case=False,na=False)].copy()
    alsh.to_csv(OUT/"corrected_pollutant_alshabib_domain_predictions.csv",index=False)
    audit={
        "representation":"full engineered pipeline with target-blind corrected exact-label pollutant_class",
        "scopes":{k:{"flag":v[0],"expected_rows":v[1],"expected_studies":v[2]} for k,v in SCOPES.items()},
        "scope_flags_selected_before_model_fitting":True,
        "target_used_to_correct_pollutant_class":False,
        "qmax_624_used":False,
        "alshabib":alsh.to_dict(orient="records"),
    }
    (OUT/"corrected_pollutant_domain_audit.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
    print("=== CORRECTED POLLUTANT DOMAIN LOSO ===")
    print(pooled.to_string(index=False))
    print("\n=== EQUAL-STUDY ===")
    print(equal.to_string(index=False))
    print("\n=== ALSHABIB ===")
    print(alsh.to_string(index=False))


if __name__=="__main__":
    main()
