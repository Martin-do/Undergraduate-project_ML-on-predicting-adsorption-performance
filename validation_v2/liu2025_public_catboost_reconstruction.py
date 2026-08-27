"""Deterministic reconstruction of the public Liu et al. 2025 CatBoost pipeline.

This is a reproducibility diagnostic, not the primary matched study-aware analysis.
It mirrors the public notebook's global scaling, random 80:20 split and 32-iteration
Bayesian CatBoost tuning. The only deliberate stabilization is random_state=1 on
BayesSearchCV, which the public notebook leaves implicit.

Two populations are run:
1) the full 685 rows loaded by plain pd.read_excel, matching executable public code;
2) the logical first 668 rows consistent with the article's stated modelling count.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from skopt import BayesSearchCV
from skopt.space import Real, Integer

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/"Biochar_dye_filtered.xlsx"
OUT=Path(__file__).resolve().parent/"outputs"/"multidataset"/"liu2025_public_catboost_reconstruction"
OUT.mkdir(parents=True,exist_ok=True)


def run(name,df):
    X=df.iloc[:,:-1].copy()
    y=df.iloc[:,-1].astype(float).copy()
    X=X.drop(columns=["O/C","PV","E"])
    scaler=StandardScaler()
    X_scaled=scaler.fit_transform(X)  # deliberate public-pipeline replication
    Xtr,Xte,ytr,yte=train_test_split(X_scaled,y,test_size=0.2,random_state=1)
    base=CatBoostRegressor(verbose=0,random_state=1,allow_writing_files=False,thread_count=2)
    spaces={
        "learning_rate":Real(0.01,1.0),
        "depth":Integer(1,10),
        "l2_leaf_reg":Real(0.1,10),
        "rsm":Real(0.5,1.0),
    }
    opt=BayesSearchCV(base,spaces,n_iter=32,scoring="neg_mean_squared_error",cv=5,random_state=1,n_jobs=1)
    opt.fit(Xtr,ytr)
    best=dict(opt.best_params_)
    model=CatBoostRegressor(**best,random_state=1,verbose=0,allow_writing_files=False,thread_count=2)
    model.fit(Xtr,ytr)
    pred=model.predict(Xte)
    return {
        "population":name,"rows":len(df),"train_rows":len(ytr),"test_rows":len(yte),
        "test_r2":float(r2_score(yte,pred)),
        "test_rmse":float(mean_squared_error(yte,pred)**0.5),
        "test_mae":float(mean_absolute_error(yte,pred)),
        "best_cv_neg_mse":float(opt.best_score_),
        "best_params":json.dumps({k:(int(v) if isinstance(v,(np.integer,)) else float(v) if isinstance(v,(np.floating,)) else v) for k,v in best.items()},sort_keys=True),
    }


def main():
    df=pd.read_excel(BOOK,sheet_name="After preprocessing")
    results=[run("public_code_plain_read_685",df),run("logical_article_count_668",df.iloc[:668].copy())]
    out=pd.DataFrame(results)
    out.to_csv(OUT/"liu2025_public_catboost_reconstruction.csv",index=False)
    summary={
        "doi":"10.1007/s44246-025-00213-9",
        "workbook_sha256":hashlib.sha256(BOOK.read_bytes()).hexdigest(),
        "published_catboost_r2":0.9880,
        "public_notebook_pipeline":"global StandardScaler -> random 80:20 random_state=1 -> BayesSearchCV 32 iterations ordinary cv=5",
        "stabilization":"BayesSearchCV random_state fixed to 1 for deterministic CI; public notebook leaves this implicit.",
        "results":results,
        "role":"reproducibility diagnostic only; does not replace matched fold-safe grouped analysis",
    }
    (OUT/"liu2025_public_catboost_reconstruction_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(out.to_string(index=False))

if __name__=="__main__":
    main()
