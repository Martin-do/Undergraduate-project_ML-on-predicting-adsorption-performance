"""Matched random-vs-primary-study validation for Liu et al. 2025.

Primary analysis: strict high-confidence provenance population (624 rows / 17 studies).
Sensitivity: extended source-order provenance population (668 rows / 19 studies).

The same rows, features and fixed model specification are used for row-random and
study-aware validation. No model is retuned separately by validation arm. All
preprocessing is fold-safe. The public 685-row sheet is evaluated only as a declared
reproducibility diagnostic because 17 spreadsheet-tail rows are outside the logical
668-row adsorption table.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import KFold, GroupKFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT / "Biochar_dye_filtered.xlsx"
HERE=Path(__file__).resolve().parent
PROV_DIR=HERE / "outputs" / "multidataset" / "liu2025_primary_provenance"
OUT=HERE / "outputs" / "multidataset" / "liu2025_matched_validation"
OUT.mkdir(parents=True, exist_ok=True)

FEATURES=["pH_pzc","C","H/C","(O+N)/C","BET","D","T","pH_sol","C0","S","A","B","V"]
TARGET="Q"
SEED=1

MODELS={
    "RF500": RandomForestRegressor(n_estimators=500, random_state=SEED, n_jobs=-1),
    "XGB500": XGBRegressor(n_estimators=500, max_depth=5, learning_rate=0.05,
                           subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
                           objective="reg:squarederror", random_state=SEED, n_jobs=2),
    "CatBoost500": CatBoostRegressor(iterations=500, depth=6, learning_rate=0.05,
                                     loss_function="RMSE", random_seed=SEED,
                                     verbose=0, allow_writing_files=False, thread_count=2),
}


def pipe(model):
    # Standardisation is retained because the public paper code scales all features,
    # but here it is fitted inside each training fold rather than globally.
    return Pipeline([("scale", StandardScaler()), ("model", model)])


def metrics(y, p):
    return {
        "r2": float(r2_score(y,p)),
        "rmse": float(mean_squared_error(y,p)**0.5),
        "mae": float(mean_absolute_error(y,p)),
    }


def crossval_predictions(X,y,splitter,model,groups=None):
    pred=np.full(len(y), np.nan, dtype=float)
    folds=[]
    split_iter=splitter.split(X,y,groups) if groups is not None else splitter.split(X,y)
    for fold,(tr,te) in enumerate(split_iter, start=1):
        est=pipe(clone(model))
        est.fit(X.iloc[tr], y.iloc[tr])
        pp=est.predict(X.iloc[te])
        pred[te]=pp
        fm=metrics(y.iloc[te],pp)
        folds.append({"fold":fold,"n_train":len(tr),"n_test":len(te),**fm})
    if np.isnan(pred).any():
        raise RuntimeError("Cross-validation did not generate exactly one prediction per row.")
    return pred,pd.DataFrame(folds)


def run_population(name, df, groups, model_name, model):
    X=df[FEATURES].astype(float).reset_index(drop=True)
    y=df[TARGET].astype(float).reset_index(drop=True)
    g=pd.Series(groups).reset_index(drop=True).astype(str)
    n_groups=g.nunique()
    if n_groups < 5:
        raise ValueError("At least five groups required for common GroupKFold comparator.")

    rand=KFold(n_splits=5, shuffle=True, random_state=SEED)
    group=GroupKFold(n_splits=5)
    logo=LeaveOneGroupOut()

    pr,fr=crossval_predictions(X,y,rand,model)
    pg,fg=crossval_predictions(X,y,group,model,groups=g)
    pl,fl=crossval_predictions(X,y,logo,model,groups=g)
    mr,mg,ml=metrics(y,pr),metrics(y,pg),metrics(y,pl)

    predictions=pd.DataFrame({
        "population":name,
        "model":model_name,
        "primary_doi":g,
        "y_true":y,
        "pred_random5":pr,
        "pred_group5":pg,
        "pred_logo":pl,
    })
    summary={
        "population":name,
        "model":model_name,
        "rows":len(df),
        "groups":int(n_groups),
        "largest_group_rows":int(g.value_counts().max()),
        "largest_group_share":float(g.value_counts(normalize=True).max()),
        "random_r2":mr["r2"],"random_rmse":mr["rmse"],"random_mae":mr["mae"],
        "grouped_r2":mg["r2"],"grouped_rmse":mg["rmse"],"grouped_mae":mg["mae"],
        "delta_r2_random_minus_grouped":mr["r2"]-mg["r2"],
        "delta_rmse_grouped_minus_random":mg["rmse"]-mr["rmse"],
        "delta_mae_grouped_minus_random":mg["mae"]-mr["mae"],
        "logo_r2":ml["r2"],"logo_rmse":ml["rmse"],"logo_mae":ml["mae"],
    }
    fr.insert(0,"validation","random5"); fg.insert(0,"validation","group5"); fl.insert(0,"validation","logo")
    fold=pd.concat([fr,fg,fl],ignore_index=True)
    fold.insert(0,"model",model_name); fold.insert(0,"population",name)
    return summary,predictions,fold


def random_only_diagnostic(name, df, model_name, model):
    X=df[FEATURES].astype(float).reset_index(drop=True)
    y=df[TARGET].astype(float).reset_index(drop=True)
    pred,fold=crossval_predictions(X,y,KFold(n_splits=5,shuffle=True,random_state=SEED),model)
    m=metrics(y,pred)
    return {"population":name,"model":model_name,"rows":len(df),"random_r2":m["r2"],"random_rmse":m["rmse"],"random_mae":m["mae"]}


def main():
    # Rebuild provenance evidence when run standalone/CI.
    if not (PROV_DIR / "liu2025_primary_study_provenance.csv").exists():
        import subprocess,sys
        subprocess.run([sys.executable, str(HERE/"liu2025_primary_study_provenance.py")], check=True)

    prov=pd.read_csv(PROV_DIR / "liu2025_primary_study_provenance.csv")
    processed=pd.read_excel(BOOK, sheet_name="After preprocessing")
    logical=processed.iloc[:668].copy().reset_index(drop=True)
    if not np.allclose(logical[TARGET].astype(float).to_numpy(), prov["Q_mmol_g"].astype(float).to_numpy()):
        raise ValueError("Logical 668-row processed target order does not match provenance ledger.")
    logical["primary_doi"]=prov["primary_doi"].to_numpy()
    logical["mapping_confidence"]=prov["mapping_confidence"].to_numpy()

    strict=logical[logical.mapping_confidence=="high"].reset_index(drop=True)
    extended=logical[logical.mapping_confidence.isin(["high","medium"])].reset_index(drop=True)
    if len(strict)!=624 or strict.primary_doi.nunique()!=17:
        raise ValueError("Strict provenance gate changed unexpectedly.")
    if len(extended)!=668 or extended.primary_doi.nunique()!=19:
        raise ValueError("Extended provenance gate changed unexpectedly.")

    summaries=[]; preds=[]; folds=[]
    for pop_name,df in [("strict_high_confidence",strict),("extended_source_order",extended)]:
        for model_name,model in MODELS.items():
            s,p,f=run_population(pop_name,df,df.primary_doi,model_name,model)
            summaries.append(s); preds.append(p); folds.append(f)

    summary_df=pd.DataFrame(summaries)
    summary_df.to_csv(OUT/"liu2025_matched_metrics.csv",index=False)
    pd.concat(preds,ignore_index=True).to_csv(OUT/"liu2025_matched_predictions.csv",index=False)
    pd.concat(folds,ignore_index=True).to_csv(OUT/"liu2025_fold_metrics.csv",index=False)

    # Public-workbook diagnostic: quantify the consequence of plain pd.read_excel
    # loading the 17 quarantined tail rows. This is NOT part of the grouped analysis.
    diag=[]
    public685=processed.copy().reset_index(drop=True)
    for model_name,model in MODELS.items():
        diag.append(random_only_diagnostic("public_sheet_685_diagnostic",public685,model_name,model))
        diag.append(random_only_diagnostic("logical_668_diagnostic",logical,model_name,model))
    pd.DataFrame(diag).to_csv(OUT/"liu2025_public685_random_diagnostic.csv",index=False)

    group_counts=(strict.primary_doi.value_counts().rename_axis("primary_doi").reset_index(name="n_rows"))
    group_counts.to_csv(OUT/"liu2025_strict_group_sizes.csv",index=False)

    result={
        "dataset":"Liu et al. 2025 public workbook",
        "doi":"10.1007/s44246-025-00213-9",
        "workbook_sha256":hashlib.sha256(BOOK.read_bytes()).hexdigest(),
        "feature_policy":"Public-paper feature set after dropping O/C, PV and E; StandardScaler fitted inside each fold.",
        "model_policy":"Fixed model specifications; identical between random/grouped/LOSO; no outcome-driven retuning.",
        "strict_rows":624,"strict_groups":17,
        "extended_rows":668,"extended_groups":19,
        "public_sheet_rows":685,
        "quarantined_tail_rows":17,
        "primary_metrics":summary_df.to_dict(orient="records"),
        "interpretation_gate":"Primary claim uses strict high-confidence provenance. Extended source-order results are sensitivity only. Public 685-row random results are reproducibility diagnostics only.",
    }
    (OUT/"liu2025_matched_validation_summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(summary_df.to_string(index=False))
    print("\nPublic 685-vs-logical-668 random diagnostic:\n",pd.DataFrame(diag).to_string(index=False))

if __name__=="__main__":
    main()
