from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from contextlib import contextmanager

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    normalized_mutual_info_score,
    r2_score,
)
from sklearn.model_selection import GroupKFold, KFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VALIDATION = REPO / 'validation_v2'
OUT = HERE / 'outputs'
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(VALIDATION))
import build_dataset_v21  # noqa: E402
import study_aware_validation as base  # noqa: E402
import feature_parity_validation as fp  # noqa: E402
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor  # noqa: E402

fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor
RAW_MODEL_COLS = base.RAW_FEATURES + ['removal_percent', 'source_link']
RANDOM_STATE = 42
IDENTITY_PREFIXES = ('base_material_', 'material_class_', 'pollutant_class_', 'activation_agent_')
FAMILIES = ['activation_agent', 'base_material', 'material_class', 'pollutant_class']


def metric(y, p):
    return {
        'r2': float(r2_score(y, p)),
        'rmse_mg_g': float(np.sqrt(mean_squared_error(y, p))),
        'mae_mg_g': float(mean_absolute_error(y, p)),
        'median_ae_mg_g': float(np.median(np.abs(np.asarray(y)-np.asarray(p)))),
    }


def safe_study_metric(y, p):
    y = np.asarray(y, float); p = np.asarray(p, float)
    out = {
        'r2': np.nan,
        'rmse_mg_g': float(np.sqrt(mean_squared_error(y,p))),
        'mae_mg_g': float(mean_absolute_error(y,p)),
        'median_ae_mg_g': float(np.median(np.abs(y-p))),
    }
    if len(y) >= 2 and np.nanstd(y) > 0:
        out['r2'] = float(r2_score(y,p))
    return out


def load_strict():
    build_dataset_v21.main()
    data_path = VALIDATION / 'outputs' / 'adsorption_dataset_v2_1.csv'
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    for col in base.NUMERIC_FEATURES + [base.TARGET]:
        df[col] = df[col].map(base.parse_numeric)
    for col in base.CATEGORICAL_FEATURES:
        df[col] = df[col].astype('string').fillna('Unknown')
    strict = df[df['analysis_eligible_strict_comparable_v21'].astype(bool)].copy().reset_index(drop=True)
    assert len(strict) == 273
    assert strict.primary_study_id_v21.nunique() == 24
    return df, strict


def cramers_v(x, y):
    tab = pd.crosstab(pd.Series(x), pd.Series(y))
    if tab.empty:
        return np.nan
    chi2 = chi2_contingency(tab, correction=False)[0]
    n = tab.to_numpy().sum()
    phi2 = chi2 / n
    r, k = tab.shape
    if n <= 1:
        return np.nan
    phi2corr = max(0.0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    denom = min(kcorr-1, rcorr-1)
    return float(np.sqrt(phi2corr/denom)) if denom > 0 else np.nan


def modal_consistency(feature, study):
    tmp = pd.DataFrame({'f': feature.astype(str), 's': study.astype(str)})
    vals = []
    for _, g in tmp.groupby('s'):
        vals.append(g['f'].value_counts(normalize=True).iloc[0])
    row_weighted = sum(len(g)*g['f'].value_counts(normalize=True).iloc[0] for _, g in tmp.groupby('s')) / len(tmp)
    return float(np.mean(vals)), float(np.median(vals)), float(row_weighted)


def cv_classifier_scores(X, y, cols, model_name, splits):
    pre = ColumnTransformer([('cat', OneHotEncoder(handle_unknown='ignore'), cols)])
    if model_name == 'LogisticRegression':
        clf = LogisticRegression(max_iter=5000, class_weight='balanced', random_state=RANDOM_STATE)
    else:
        clf = RandomForestClassifier(
            n_estimators=200, random_state=RANDOM_STATE,
            class_weight='balanced_subsample', n_jobs=-1
        )
    pred = np.empty(len(y), dtype=object)
    for tr, te in splits:
        pipe = Pipeline([('pre', clone(pre)), ('clf', clone(clf))])
        pipe.fit(X.iloc[tr], y.iloc[tr])
        pred[te] = pipe.predict(X.iloc[te])
    return {
        'accuracy': float(accuracy_score(y, pred)),
        'balanced_accuracy': float(balanced_accuracy_score(y, pred)),
        'macro_f1': float(f1_score(y, pred, average='macro', zero_division=0)),
    }


def study_association_analysis(strict):
    raw = strict[RAW_MODEL_COLS].copy()
    eng = fp.engineer_deterministic(raw)
    study = strict['primary_study_id_v21'].astype(str).reset_index(drop=True)
    cats = eng[FAMILIES].astype(str).reset_index(drop=True)

    assoc_rows = []
    for c in FAMILIES:
        mean_modal, median_modal, row_modal = modal_consistency(cats[c], study)
        assoc_rows.append({
            'feature_family': c,
            'n_categories': int(cats[c].nunique()),
            'normalized_mutual_information_with_study': float(normalized_mutual_info_score(study, cats[c])),
            'cramers_v_with_study': cramers_v(cats[c], study),
            'mean_within_study_modal_share': mean_modal,
            'median_within_study_modal_share': median_modal,
            'row_weighted_within_study_modal_share': row_modal,
        })
    pd.DataFrame(assoc_rows).to_csv(OUT/'study_category_association.csv', index=False)

    counts = study.value_counts()
    eligible = counts[counts >= 5].index
    use = study.isin(eligible).to_numpy()
    X = cats.loc[use].reset_index(drop=True)
    y = study.loc[use].reset_index(drop=True)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    splits = list(cv.split(X, y))

    predictor_sets = {
        'all_four_context_families': FAMILIES,
        **{f'{c}_only':[c] for c in FAMILIES},
    }
    class_rows = []
    for label, cols in predictor_sets.items():
        for model in ['LogisticRegression','RandomForestClassifier']:
            scores = cv_classifier_scores(X[cols], y, cols, model, splits)
            class_rows.append({
                'predictor_set': label,
                'classifier': model,
                'n_rows': len(y),
                'n_studies': y.nunique(),
                'majority_class_accuracy': float(y.value_counts(normalize=True).iloc[0]),
                'balanced_chance_reference': float(1.0/y.nunique()),
                **scores,
            })
    class_df = pd.DataFrame(class_rows)
    class_df.to_csv(OUT/'study_id_predictability_cv.csv', index=False)

    obs = class_df.query("predictor_set=='all_four_context_families' and classifier=='LogisticRegression'").iloc[0]
    rng = np.random.default_rng(RANDOM_STATE)
    null_rows = []
    for b in range(50):
        yp = pd.Series(rng.permutation(y.to_numpy()), index=y.index)
        try:
            s = cv_classifier_scores(X[FAMILIES], yp, FAMILIES, 'LogisticRegression', splits)
        except Exception:
            continue
        null_rows.append({'replicate':b, **s})
    null = pd.DataFrame(null_rows)
    null.to_csv(OUT/'study_id_predictability_label_permutation_null.csv', index=False)
    pvals = {}
    for key in ['accuracy','balanced_accuracy','macro_f1']:
        pvals[key] = float((1 + (null[key] >= float(obs[key])).sum()) / (1 + len(null)))
    summary = {
        'classification_population': 'strict studies with n>=5 to permit 5-fold stratified assessment',
        'n_rows': int(len(y)), 'n_studies': int(y.nunique()),
        'observed_logistic_all_four': {k:float(obs[k]) for k in ['accuracy','balanced_accuracy','macro_f1']},
        'permutation_replicates': int(len(null)),
        'permutation_p_values': pvals,
    }
    (OUT/'study_id_predictability_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return eng


def mask_variant(cols, variant):
    cols = list(cols)
    if variant == 'full_engineered':
        keep = np.ones(len(cols), dtype=bool)
    elif variant == 'remove_activation_agent':
        keep = np.array([not c.startswith('activation_agent_') for c in cols])
    elif variant == 'remove_base_material':
        keep = np.array([not c.startswith('base_material_') for c in cols])
    elif variant == 'remove_material_class':
        keep = np.array([not c.startswith('material_class_') for c in cols])
    elif variant == 'remove_pollutant_class':
        keep = np.array([not c.startswith('pollutant_class_') for c in cols])
    elif variant == 'remove_base_and_material_class':
        keep = np.array([not (c.startswith('base_material_') or c.startswith('material_class_')) for c in cols])
    elif variant == 'remove_all_four_context_families':
        keep = np.array([not c.startswith(IDENTITY_PREFIXES) for c in cols])
    elif variant == 'physical_numeric_only':
        allowed = {
            'surface_area_m2g','particle_size_mm','pore_volume_cm3g','initial_concentration_mgL',
            'temperature_c','contact_time_min','ph','dose_gL','pyrolysis_temp_c','conc_dose_ratio',
            'surface_area_x_pore_vol','ph_x_temperature',
        }
        keep = np.array([c in allowed for c in cols])
    else:
        raise ValueError(variant)
    idx = np.flatnonzero(keep)
    return idx, [cols[i] for i in idx]


def split_list(y, groups, scheme):
    n=len(y); dummy=np.arange(n)
    if scheme == 'row_random_5fold':
        return list(KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE).split(dummy,y))
    if scheme == 'primary_group_5fold':
        return list(GroupKFold(n_splits=5).split(dummy,y,groups))
    raise ValueError(scheme)


def evaluate_variants_cv(strict, variants):
    y = strict[base.TARGET].to_numpy(float)
    groups = strict['primary_study_id_v21'].astype(str).to_numpy()
    raw = strict[RAW_MODEL_COLS].copy()
    bank = fp.models()
    pooled_rows=[]; fold_rows=[]
    for scheme in ['primary_group_5fold']:
        splits=split_list(y, groups, scheme)
        for variant in variants:
            preds={m:np.empty(len(strict),float) for m in ['RF','XGB']}
            for fold,(tr,te) in enumerate(splits,1):
                prep=DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
                xtrf=prep.transform(raw.iloc[tr]); xtef=prep.transform(raw.iloc[te])
                idx, kept=mask_variant(prep.output_cols, variant)
                xtr=xtrf[:,idx]; xte=xtef[:,idx]
                for model in ['RF','XGB']:
                    p=clone(bank[model]).fit(xtr,y[tr]).predict(xte)
                    preds[model][te]=p
                    fold_rows.append({
                        'scheme':scheme,'variant':variant,'fold':fold,'model':model,
                        'n_features':len(idx),'test_rows':len(te), **metric(y[te],p)
                    })
            for model,p in preds.items():
                pooled_rows.append({
                    'scheme':scheme,'variant':variant,'model':model,'n_rows':len(strict),'n_studies':len(np.unique(groups)),
                    **metric(y,p)
                })
    pooled=pd.DataFrame(pooled_rows); folds=pd.DataFrame(fold_rows)
    pooled.to_csv(OUT/'category_family_ablation_cv_pooled.csv',index=False)
    folds.to_csv(OUT/'category_family_ablation_cv_per_fold.csv',index=False)
    return pooled, folds


def evaluate_variants_loso(strict, variants):
    y = strict[base.TARGET].to_numpy(float)
    groups = strict['primary_study_id_v21'].astype(str).to_numpy()
    raw = strict[RAW_MODEL_COLS].copy()
    bank=fp.models(); pred_rows=[]; study_rows=[]; pooled_rows=[]
    for variant in variants:
        all_pred={m:np.empty(len(strict),float) for m in ['RF','XGB']}
        for study in sorted(np.unique(groups)):
            te=np.flatnonzero(groups==study); tr=np.flatnonzero(groups!=study)
            prep=DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
            xtrf=prep.transform(raw.iloc[tr]); xtef=prep.transform(raw.iloc[te])
            idx,kept=mask_variant(prep.output_cols,variant)
            for model in ['RF','XGB']:
                p=clone(bank[model]).fit(xtrf[:,idx],y[tr]).predict(xtef[:,idx])
                all_pred[model][te]=p
                sm=safe_study_metric(y[te],p)
                study_rows.append({
                    'variant':variant,'held_out_primary_study':study,'model':model,'n_test_rows':len(te),
                    'n_features':len(idx),**sm
                })
                for pos,pp in zip(te,p):
                    pred_rows.append({
                        'variant':variant,'held_out_primary_study':study,'model':model,'row_index':int(pos),
                        'actual_qe_mg_g':float(y[pos]),'predicted_qe_mg_g':float(pp),'abs_error_mg_g':float(abs(y[pos]-pp))
                    })
        for model,p in all_pred.items():
            pooled_rows.append({'variant':variant,'model':model,'n_rows':len(strict),'n_studies':len(np.unique(groups)),**metric(y,p)})
    pooled=pd.DataFrame(pooled_rows); studies=pd.DataFrame(study_rows); preds=pd.DataFrame(pred_rows)
    pooled.to_csv(OUT/'category_family_ablation_loso_pooled.csv',index=False)
    studies.to_csv(OUT/'category_family_ablation_loso_per_study.csv',index=False)
    preds.to_csv(OUT/'category_family_ablation_loso_predictions.csv',index=False)
    return pooled,studies,preds


def study_cluster_bootstrap(preds, study_metrics, variants, n_boot=5000):
    rng=np.random.default_rng(RANDOM_STATE)
    summary=[]; bootrows=[]
    for variant in variants:
        gpred=preds[preds.variant.eq(variant)].copy()
        gsm=study_metrics[study_metrics.variant.eq(variant)].copy()
        for model in ['RF','XGB']:
            pdat=gpred[gpred.model.eq(model)]
            studies=sorted(pdat.held_out_primary_study.unique())
            blocks={s:pdat[pdat.held_out_primary_study.eq(s)] for s in studies}
            local=[]
            for b in range(n_boot):
                sampled=rng.choice(studies,size=len(studies),replace=True)
                y=[]; p=[]
                for s in sampled:
                    block=blocks[s]
                    y.extend(block.actual_qe_mg_g.to_numpy(float)); p.extend(block.predicted_qe_mg_g.to_numpy(float))
                m=metric(np.array(y),np.array(p))
                rec={'variant':variant,'model':model,'replicate':b,**m}
                bootrows.append(rec); local.append(rec)
            bdf=pd.DataFrame(local)
            sm=gsm[gsm.model.eq(model)]
            r2valid=sm.r2.dropna()
            obs=metric(pdat.actual_qe_mg_g.to_numpy(float),pdat.predicted_qe_mg_g.to_numpy(float))
            row={
                'variant':variant,'model':model,'n_studies':len(studies),'pooled_r2':obs['r2'],'pooled_mae_mg_g':obs['mae_mg_g'],'pooled_rmse_mg_g':obs['rmse_mg_g'],
                'study_mae_median':float(sm.mae_mg_g.median()),'study_mae_iqr_low':float(sm.mae_mg_g.quantile(.25)),'study_mae_iqr_high':float(sm.mae_mg_g.quantile(.75)),
                'study_mae_mean':float(sm.mae_mg_g.mean()),'study_mae_sd':float(sm.mae_mg_g.std(ddof=1)),
                'study_rmse_median':float(sm.rmse_mg_g.median()),'study_rmse_iqr_low':float(sm.rmse_mg_g.quantile(.25)),'study_rmse_iqr_high':float(sm.rmse_mg_g.quantile(.75)),
                'valid_study_r2_count':int(len(r2valid)),
                'study_r2_median':float(r2valid.median()) if len(r2valid) else np.nan,
                'study_r2_iqr_low':float(r2valid.quantile(.25)) if len(r2valid) else np.nan,
                'study_r2_iqr_high':float(r2valid.quantile(.75)) if len(r2valid) else np.nan,
            }
            for met in ['r2','mae_mg_g','rmse_mg_g']:
                row[f'cluster_bootstrap_{met}_ci_low']=float(bdf[met].quantile(.025))
                row[f'cluster_bootstrap_{met}_ci_high']=float(bdf[met].quantile(.975))
            summary.append(row)
    pd.DataFrame(bootrows).to_csv(OUT/'loso_study_cluster_bootstrap_replicates.csv',index=False)
    summ=pd.DataFrame(summary)
    summ.to_csv(OUT/'loso_study_uncertainty_summary.csv',index=False)
    return summ


class PermutedCategoryPreprocessor:
    """Use original material_class for imputation, then replace only categorical predictor labels.

    This isolates the encoded category block from the material-class imputation route.
    The permutation table preserves the joint four-family category distribution globally.
    """
    def __init__(self, label_map):
        self.label_map=label_map
        self.group_medians={}; self.global_medians={}; self.inactive_training_features=set()
        self.encoder=None; self.scaler=None; self.encoded_cols=None; self.output_cols=None

    def _prepare_before_encoding(self, raw, fit=False):
        x=fp.engineer_deterministic(raw).copy()
        original_material_class=x['material_class'].copy()
        for col in fp.GROUP_IMPUTE:
            numeric=pd.to_numeric(x[col],errors='coerce')
            if fit:
                med=pd.DataFrame({'v':numeric,'mc':original_material_class}).groupby('mc',dropna=False)['v'].median()
                self.group_medians[col]=med.to_dict()
                gm=numeric.median()
                if pd.isna(gm):
                    self.inactive_training_features.add(col); self.global_medians[col]=0.0; x[col]=0.0; continue
                self.global_medians[col]=float(gm)
            if col in self.inactive_training_features:
                x[col]=0.0
            else:
                x[col]=numeric.fillna(original_material_class.map(self.group_medians[col])).fillna(self.global_medians[col])
        for col in fp.GLOBAL_IMPUTE:
            numeric=pd.to_numeric(x[col],errors='coerce')
            if fit:
                gm=numeric.median()
                if pd.isna(gm):
                    self.inactive_training_features.add(col); self.global_medians[col]=0.0; x[col]=0.0; continue
                self.global_medians[col]=float(gm)
            if col in self.inactive_training_features: x[col]=0.0
            else: x[col]=numeric.fillna(self.global_medians[col])
        x=fp.FoldSafeParityPreprocessor._add_interactions(x)
        lab=self.label_map.loc[x.index, fp.CAT_COLS]
        for c in fp.CAT_COLS: x[c]=lab[c].to_numpy()
        return x

    def fit(self, raw):
        x=self._prepare_before_encoding(raw,fit=True)
        self.encoder=OneHotEncoder(drop='first',handle_unknown='ignore',sparse_output=False)
        enc=self.encoder.fit_transform(x[fp.CAT_COLS]); self.encoded_cols=self.encoder.get_feature_names_out(fp.CAT_COLS).tolist()
        enc_df=pd.DataFrame(enc,columns=self.encoded_cols,index=x.index)
        x_num=pd.concat([x.drop(columns=fp.CAT_COLS),enc_df],axis=1)
        self.scaler=StandardScaler().fit(x_num[fp.SCALE_COLS].astype(float))
        scaled=self.scaler.transform(x_num[fp.SCALE_COLS].astype(float))
        for j,c in enumerate(fp.SCALE_COLS): x_num[c]=scaled[:,j]
        self.output_cols=x_num.columns.tolist(); return self

    def transform(self, raw):
        x=self._prepare_before_encoding(raw,fit=False)
        enc=self.encoder.transform(x[fp.CAT_COLS]); enc_df=pd.DataFrame(enc,columns=self.encoded_cols,index=x.index)
        x_num=pd.concat([x.drop(columns=fp.CAT_COLS),enc_df],axis=1).reindex(columns=self.output_cols,fill_value=0.0)
        scaled=self.scaler.transform(x_num[fp.SCALE_COLS].astype(float))
        for j,c in enumerate(fp.SCALE_COLS): x_num[c]=scaled[:,j]
        return x_num.to_numpy(float)


def permutation_representation_test(strict, n_perm=10):
    y=strict[base.TARGET].to_numpy(float); groups=strict.primary_study_id_v21.astype(str).to_numpy(); raw=strict[RAW_MODEL_COLS].copy(); bank=fp.models()
    original_labels=fp.engineer_deterministic(raw)[fp.CAT_COLS].copy()
    rng=np.random.default_rng(RANDOM_STATE)
    rows=[]
    for b in range(n_perm):
        perm=rng.permutation(len(strict))
        lab=pd.DataFrame(original_labels.iloc[perm].to_numpy(),columns=fp.CAT_COLS,index=raw.index)
        for scheme in ['row_random_5fold','primary_group_5fold']:
            pred={m:np.empty(len(strict),float) for m in ['RF','XGB']}
            for tr,te in split_list(y,groups,scheme):
                prep=PermutedCategoryPreprocessor(lab).fit(raw.iloc[tr])
                xtr=prep.transform(raw.iloc[tr]); xte=prep.transform(raw.iloc[te])
                for m in ['RF','XGB']:
                    pred[m][te]=clone(bank[m]).fit(xtr,y[tr]).predict(xte)
            for m in ['RF','XGB']:
                rows.append({'replicate':b,'scheme':scheme,'model':m,**metric(y,pred[m])})
        pred={m:np.empty(len(strict),float) for m in ['RF','XGB']}
        for s in np.unique(groups):
            te=np.flatnonzero(groups==s); tr=np.flatnonzero(groups!=s)
            prep=PermutedCategoryPreprocessor(lab).fit(raw.iloc[tr])
            xtr=prep.transform(raw.iloc[tr]); xte=prep.transform(raw.iloc[te])
            for m in ['RF','XGB']:
                pred[m][te]=clone(bank[m]).fit(xtr,y[tr]).predict(xte)
        for m in ['RF','XGB']:
            rows.append({'replicate':b,'scheme':'LOSO','model':m,**metric(y,pred[m])})
    res=pd.DataFrame(rows); res.to_csv(OUT/'context_block_permutation_results.csv',index=False)
    summ=res.groupby(['scheme','model']).agg(
        n_replicates=('replicate','nunique'),mean_r2=('r2','mean'),sd_r2=('r2','std'),median_r2=('r2','median'),
        min_r2=('r2','min'),max_r2=('r2','max'),mean_mae=('mae_mg_g','mean'),mean_rmse=('rmse_mg_g','mean')
    ).reset_index()
    summ.to_csv(OUT/'context_block_permutation_summary.csv',index=False)
    return summ


def ridge_stack_audit(strict):
    y=strict[base.TARGET].to_numpy(float); groups=strict.primary_study_id_v21.astype(str).to_numpy(); raw=strict[RAW_MODEL_COLS].copy(); bank=fp.models()
    rows=[]
    for scheme,scheme_groups in [('row_random_5fold',None),('primary_group_5fold',groups)]:
        splits=split_list(y,groups,scheme)
        for fold,(tr,te) in enumerate(splits,1):
            prep=DtypeSafeParityPreprocessor().fit(raw.iloc[tr]); xtr=prep.transform(raw.iloc[tr]); xte=prep.transform(raw.iloc[te])
            fitted={n:clone(est).fit(xtr,y[tr]) for n,est in bank.items()}
            gtr=None if scheme_groups is None else groups[tr]
            meta_train,meta_names=fp.oof_meta(raw.iloc[tr].reset_index(drop=True),y[tr],gtr)
            alpha=fp.choose_alpha(meta_train,y[tr],gtr)
            mm=Ridge(alpha=alpha).fit(meta_train,y[tr])
            meta_test=np.column_stack([fitted[n].predict(xte) for n in meta_names])
            p=mm.predict(meta_test)
            rec={'scheme':scheme,'fold':fold,'alpha':alpha,'intercept':float(mm.intercept_),'test_rows':len(te),**metric(y[te],p)}
            for name,coef in zip(meta_names,mm.coef_): rec[f'weight_{name}']=float(coef)
            rows.append(rec)
    rdf=pd.DataFrame(rows); rdf.to_csv(OUT/'ridge_stack_outer_fold_weights_and_metrics.csv',index=False)
    summary=rdf.groupby('scheme').agg(
        mean_r2=('r2','mean'),min_r2=('r2','min'),max_r2=('r2','max'),
        alpha_min=('alpha','min'),alpha_max=('alpha','max'),
        weight_LR_mean=('weight_LR','mean'),weight_LR_sd=('weight_LR','std'),
        weight_SVR_mean=('weight_SVR','mean'),weight_SVR_sd=('weight_SVR','std'),
        weight_RF_mean=('weight_RF','mean'),weight_RF_sd=('weight_RF','std'),
        weight_XGB_mean=('weight_XGB','mean'),weight_XGB_sd=('weight_XGB','std'),
    ).reset_index()
    summary.to_csv(OUT/'ridge_stack_audit_summary.csv',index=False)
    return summary


def feature_dictionary(strict):
    raw=strict[RAW_MODEL_COLS].copy(); prep=DtypeSafeParityPreprocessor().fit(raw)
    rows=[]
    raw_defs={
        'surface_area_m2g':'Raw literature field; numeric; group-median imputation by material_class in corrected parity pipeline.',
        'particle_size_mm':'Raw literature field; numeric; global training-fold median imputation.',
        'pore_volume_cm3g':'Raw literature field; numeric; group-median imputation by material_class.',
        'initial_concentration_mgL':'Raw literature field; numeric; global training-fold median imputation.',
        'temperature_c':'Raw literature field; numeric; global training-fold median imputation.',
        'contact_time_min':'Raw literature field; numeric; global training-fold median imputation.',
        'ph':'Raw literature field; numeric; global training-fold median imputation.',
        'dose_gL':'Raw literature field; numeric; global training-fold median imputation.',
        'pyrolysis_temp_c':'Regex-extracted from method_processing; group-median imputation by material_class.',
        'is_activated':'Binary derived from activation-agent parse.',
        'is_modified_acid':'Binary regex-derived from method_processing.',
        'is_modified_base':'Binary regex-derived from method_processing.',
        'is_raw_natural':'Binary regex-derived from method_processing.',
        'is_acid_treated':'Binary regex-derived from method_processing.',
        'is_base_treated':'Binary regex-derived from method_processing.',
        'is_chitosan_modified':'Binary regex-derived from method_processing.',
        'conc_dose_ratio':'Engineered interaction: initial_concentration_mgL / (dose_gL + 1e-6).',
        'surface_area_x_pore_vol':'Engineered interaction: surface_area_m2g * pore_volume_cm3g.',
        'ph_x_temperature':'Engineered interaction: ph * temperature_c.',
    }
    for c in prep.output_cols:
        fam='numeric_or_binary'
        desc=raw_defs.get(c,'')
        source='raw/engineered numeric'
        for prefix in IDENTITY_PREFIXES:
            if c.startswith(prefix):
                fam=prefix.rstrip('_'); source='one-hot encoded engineered categorical family'; desc=f'Drop-first one-hot indicator derived deterministically from raw text; family={fam}.'
                break
        rows.append({'model_feature':c,'feature_family':fam,'source_or_transformation':source,'description':desc,'target_derived':'no','study_identifier_used':'no'})
    pd.DataFrame(rows).to_csv(OUT/'complete_model_feature_dictionary.csv',index=False)


def main():
    all_df, strict=load_strict()
    study_association_analysis(strict)
    variants=[
        'full_engineered','remove_activation_agent','remove_base_material','remove_material_class','remove_pollutant_class',
        'remove_base_and_material_class','remove_all_four_context_families','physical_numeric_only'
    ]
    cv_pooled, cv_folds=evaluate_variants_cv(strict,variants)
    loso_pooled,loso_studies,loso_preds=evaluate_variants_loso(strict,variants)
    uncertainty=study_cluster_bootstrap(
        loso_preds, loso_studies,
        ['full_engineered','remove_pollutant_class','remove_all_four_context_families','physical_numeric_only'],
        5000,
    )
    perm=permutation_representation_test(strict, n_perm=10)
    ridge=ridge_stack_audit(strict)
    feature_dictionary(strict)

    maxrow=all_df.loc[pd.to_numeric(all_df[base.TARGET],errors='coerce').idxmax()].to_frame().T
    maxrow.to_csv(OUT/'max_target_2239_provenance_row.csv',index=False)

    import sklearn, xgboost, scipy
    summary={
        'python_version':sys.version,
        'numpy_version':np.__version__,
        'pandas_version':pd.__version__,
        'scipy_version':scipy.__version__,
        'sklearn_version':sklearn.__version__,
        'xgboost_version':xgboost.__version__,
        'status':'V3 targeted supervisor revision gate - pinned workflow candidate; manuscript values freeze only after CI pass',
        'strict_rows':len(strict),'strict_studies':strict.primary_study_id_v21.nunique(),
        'category_ablation_loso':loso_pooled.to_dict(orient='records'),
        'category_ablation_grouped':cv_pooled[cv_pooled.scheme.eq('primary_group_5fold')].to_dict(orient='records'),
        'loso_uncertainty':uncertainty.to_dict(orient='records'),
        'permutation_summary':perm.to_dict(orient='records'),
        'ridge_summary':ridge.to_dict(orient='records'),
    }
    (OUT/'V3_SUPERVISOR_GATE_SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('=== CATEGORY ABLATION LOSO ===')
    print(loso_pooled.to_string(index=False))
    print('\n=== CATEGORY ABLATION GROUPED ===')
    print(cv_pooled[cv_pooled.scheme.eq('primary_group_5fold')].to_string(index=False))
    print('\n=== STUDY UNCERTAINTY ===')
    print(uncertainty.to_string(index=False))
    print('\n=== CONTEXT-BLOCK PERMUTATION ===')
    print(perm.to_string(index=False))
    print('\n=== RIDGE STACK ===')
    print(ridge.to_string(index=False))
    print('\nOUTPUT',OUT)

if __name__=='__main__':
    main()
