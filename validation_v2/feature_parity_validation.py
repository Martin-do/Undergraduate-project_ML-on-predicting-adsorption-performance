"""Fold-safe validation using the original ID-SEAD engineered feature design.

This reproduces the submitted notebook's deterministic feature engineering as
closely as possible while fixing the validation leakage:
- processing-derived pyrolysis/activation features;
- hierarchical base-material/material/pollutant classes;
- training-fold material-class median imputation;
- original three interaction features;
- drop-first one-hot encoding of engineered categorical features;
- original selected numeric scaling columns.

`removal_percent` remains excluded because it can encode qe through mass balance.
The legacy physical Q_MAX constraint remains excluded pending domain repair.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR

from xgboost import XGBRegressor

import grouping_sensitivity as grouping
import study_aware_validation as base

OUT_DIR = Path(__file__).resolve().parent / "outputs"
N_SPLITS = 5
ALPHAS = [0.01, 0.05, 0.1, 0.5, 1.0]

GROUP_IMPUTE = ["surface_area_m2g", "pore_volume_cm3g", "pyrolysis_temp_c"]
GLOBAL_IMPUTE = [
    "particle_size_mm",
    "initial_concentration_mgL",
    "temperature_c",
    "contact_time_min",
    "ph",
    "dose_gL",
]
CAT_COLS = ["activation_agent", "base_material", "material_class", "pollutant_class"]
SCALE_COLS = [
    "surface_area_m2g",
    "particle_size_mm",
    "pore_volume_cm3g",
    "initial_concentration_mgL",
    "temperature_c",
    "ph",
    "pyrolysis_temp_c",
    "conc_dose_ratio",
    "surface_area_x_pore_vol",
    "ph_x_temperature",
]


def engineer_deterministic(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    proc_raw = d["method_processing"].astype("string").fillna("")
    proc = proc_raw.str.lower()
    ads = d["adsorbent"].astype("string").str.lower().fillna("")
    poll = d["pollutant"].astype("string").str.lower().fillna("")

    # Submitted notebook processing features.
    d["pyrolysis_temp_c"] = pd.to_numeric(
        proc_raw.str.extract(r"(\d{3,4})\s?°?[cC]", expand=False), errors="coerce"
    )
    agents = {
        "koh": "KOH",
        "naoh": "NaOH",
        "h3po4": "H3PO4",
        "hcl": "HCl",
        "h2so4": "H2SO4",
        "zncl2": "ZnCl2",
        "citric acid": "CitricAcid",
    }
    d["activation_agent"] = "None"
    for key, name in agents.items():
        d.loc[proc.str.contains(key, na=False), "activation_agent"] = name
    d["is_activated"] = (d["activation_agent"] != "None").astype(int)
    d["is_modified_acid"] = proc.str.contains(r"acid|hcl|h2so4|h3po4", regex=True, na=False).astype(int)
    d["is_modified_base"] = proc.str.contains(r"base|naoh|koh", regex=True, na=False).astype(int)
    d["is_raw_natural"] = proc.str.contains(r"raw|natural|unmodified|untreated", regex=True, na=False).astype(int)

    mat_cond = [
        ads.str.contains(r"rice|rh|oryza|bran", regex=True, na=False),
        ads.str.contains(r"coconut|cs", regex=True, na=False),
        ads.str.contains("banana", regex=False, na=False),
        ads.str.contains(r"corn|maize|cc", regex=True, na=False),
        ads.str.contains(r"sugarcane|bagasse", regex=True, na=False),
        ads.str.contains(r"wood|pine|sawdust", regex=True, na=False),
        ads.str.contains("bamboo", regex=False, na=False),
        ads.str.contains("straw", regex=False, na=False),
        ads.str.contains(r"orange|mandarin", regex=True, na=False),
        ads.str.contains("palm", regex=False, na=False),
    ]
    mat_choices = [
        "rice_based",
        "coconut_based",
        "banana_based",
        "corn_based",
        "sugarcane_based",
        "wood_based",
        "bamboo_based",
        "straw_based",
        "orange_peel",
        "palm_waste",
    ]
    d["base_material"] = np.select(mat_cond, mat_choices, default="other")

    cls_cond = [
        ads.str.contains(r"composite|coated", regex=True, na=False),
        ads.str.contains("hydrochar", regex=False, na=False),
        ads.str.contains(r"activated carbon|ac|activated charcoal", regex=True, na=False),
        ads.str.contains(r"biochar|char", regex=True, na=False),
        d["is_raw_natural"].eq(1),
    ]
    cls_choices = ["composite", "hydrochar", "activated_carbon", "biochar", "raw_biomass"]
    d["material_class"] = np.select(cls_cond, cls_choices, default="unknown_class")

    poll_cond = [
        poll.str.contains(
            r"pb|lead|cd|cadmium|cu|copper|zn|zinc|ni|nickel|cr|chromium|hg|mercury|as|arsenic",
            regex=True,
            na=False,
        ),
        poll.str.contains(r"dye|blue|red|violet|green|yellow", regex=True, na=False),
        poll.str.contains(r"antibiotic|tetracycline|norfloxacin|pharmaceutical", regex=True, na=False),
        poll.str.contains("phenol", regex=False, na=False),
    ]
    poll_choices = ["heavy_metal", "organic_dye", "pharmaceutical", "phenol"]
    d["pollutant_class"] = np.select(poll_cond, poll_choices, default="other_organic")

    d["is_acid_treated"] = proc.str.contains("acid", regex=False, na=False).astype(int)
    d["is_base_treated"] = proc.str.contains(r"naoh|koh", regex=True, na=False).astype(int)
    d["is_chitosan_modified"] = proc.str.contains("chitosan", regex=False, na=False).astype(int)

    # Raw high-cardinality/source columns were dropped in the submitted notebook.
    keep_drop = ["adsorbent", "pollutant", "method_processing", "source_link", "removal_percent"]
    return d.drop(columns=[c for c in keep_drop if c in d.columns])


class FoldSafeParityPreprocessor:
    def __init__(self):
        self.group_medians = {}
        self.global_medians = {}
        self.encoder = None
        self.scaler = None
        self.encoded_cols = None
        self.output_cols = None

    def fit(self, raw: pd.DataFrame):
        x = engineer_deterministic(raw).copy()

        for col in GROUP_IMPUTE:
            med = x.groupby("material_class", dropna=False)[col].median()
            self.group_medians[col] = med.to_dict()
            self.global_medians[col] = float(pd.to_numeric(x[col], errors="coerce").median())
            x[col] = x[col].fillna(x["material_class"].map(self.group_medians[col]))
            x[col] = x[col].fillna(self.global_medians[col])

        for col in GLOBAL_IMPUTE:
            self.global_medians[col] = float(pd.to_numeric(x[col], errors="coerce").median())
            x[col] = x[col].fillna(self.global_medians[col])

        x = self._add_interactions(x)

        self.encoder = OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False)
        enc = self.encoder.fit_transform(x[CAT_COLS])
        self.encoded_cols = self.encoder.get_feature_names_out(CAT_COLS).tolist()
        enc_df = pd.DataFrame(enc, columns=self.encoded_cols, index=x.index)
        x_num = pd.concat([x.drop(columns=CAT_COLS), enc_df], axis=1)

        self.scaler = StandardScaler()
        self.scaler.fit(x_num[SCALE_COLS])
        x_num.loc[:, SCALE_COLS] = self.scaler.transform(x_num[SCALE_COLS])
        self.output_cols = x_num.columns.tolist()
        return self

    @staticmethod
    def _add_interactions(x):
        x = x.copy()
        x["conc_dose_ratio"] = x["initial_concentration_mgL"] / (x["dose_gL"] + 1e-6)
        x["surface_area_x_pore_vol"] = x["surface_area_m2g"] * x["pore_volume_cm3g"]
        x["ph_x_temperature"] = x["ph"] * x["temperature_c"]
        return x

    def transform(self, raw: pd.DataFrame) -> np.ndarray:
        x = engineer_deterministic(raw).copy()

        for col in GROUP_IMPUTE:
            x[col] = x[col].fillna(x["material_class"].map(self.group_medians[col]))
            x[col] = x[col].fillna(self.global_medians[col])
        for col in GLOBAL_IMPUTE:
            x[col] = x[col].fillna(self.global_medians[col])

        x = self._add_interactions(x)
        enc = self.encoder.transform(x[CAT_COLS])
        enc_df = pd.DataFrame(enc, columns=self.encoded_cols, index=x.index)
        x_num = pd.concat([x.drop(columns=CAT_COLS), enc_df], axis=1)
        x_num = x_num.reindex(columns=self.output_cols, fill_value=0.0)
        x_num.loc[:, SCALE_COLS] = self.scaler.transform(x_num[SCALE_COLS])
        return x_num.to_numpy(dtype=float)

    def fit_transform(self, raw):
        return self.fit(raw).transform(raw)


def models():
    return {
        "LR": LinearRegression(),
        "SVR": SVR(kernel="rbf", C=10, epsilon=0.1),
        "RF": RandomForestRegressor(
            n_estimators=200,
            max_depth=None,
            min_samples_split=3,
            random_state=base.RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGB": XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            objective="reg:squarederror",
            random_state=base.RANDOM_STATE,
            verbosity=0,
            n_jobs=-1,
        ),
    }


def splitter(groups, seed_offset=0):
    if groups is None:
        return KFold(n_splits=N_SPLITS, shuffle=True, random_state=base.RANDOM_STATE + seed_offset)
    return GroupKFold(n_splits=min(N_SPLITS, len(np.unique(groups))))


def iter_splits(cv, n, y, groups):
    dummy = np.arange(n)
    return cv.split(dummy, y) if groups is None else cv.split(dummy, y, groups)


def oof_meta(raw_train, y, groups):
    meta = np.empty((len(raw_train), len(models())), dtype=float)
    cv = splitter(groups, seed_offset=31)
    names = list(models().keys())
    for tr, va in iter_splits(cv, len(raw_train), y, groups):
        prep = FoldSafeParityPreprocessor().fit(raw_train.iloc[tr])
        xt = prep.transform(raw_train.iloc[tr])
        xv = prep.transform(raw_train.iloc[va])
        for j, (name, est) in enumerate(models().items()):
            m = clone(est)
            m.fit(xt, y[tr])
            meta[va, j] = m.predict(xv)
    return meta, names


def choose_alpha(meta, y, groups):
    cv = splitter(groups, seed_offset=17)
    scored = []
    for a in ALPHAS:
        vals = []
        for tr, va in iter_splits(cv, len(y), y, groups):
            m = Ridge(alpha=a).fit(meta[tr], y[tr])
            vals.append(r2_score(y[va], m.predict(meta[va])))
        scored.append((float(np.mean(vals)), a))
    return max(scored, key=lambda z: z[0])[1]


def metric(y, p):
    return {
        "r2": float(r2_score(y, p)),
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, p))),
        "mae_mg_g": float(mean_absolute_error(y, p)),
        "median_ae_mg_g": float(np.median(np.abs(y - p))),
    }


def evaluate_scheme(df, scheme_name, groups):
    y = df[base.TARGET].to_numpy(float)
    raw = df[base.RAW_FEATURES + ["removal_percent", "source_link"]].copy()
    cv = splitter(groups)
    names = list(models().keys())
    pred = {n: np.empty(len(df)) for n in names + ["STACK_RIDGE_UNCONSTRAINED"]}
    fold_records, alpha_records, feature_counts = [], [], []

    for fold, (tr, te) in enumerate(iter_splits(cv, len(df), y, groups), start=1):
        prep = FoldSafeParityPreprocessor().fit(raw.iloc[tr])
        xtr = prep.transform(raw.iloc[tr])
        xte = prep.transform(raw.iloc[te])
        feature_counts.append({"scheme": scheme_name, "fold": fold, "feature_count": xtr.shape[1]})

        fitted = {}
        for name, est in models().items():
            m = clone(est).fit(xtr, y[tr])
            pred[name][te] = m.predict(xte)
            fitted[name] = m

        gtr = None if groups is None else groups[tr]
        meta_train, meta_names = oof_meta(raw.iloc[tr].reset_index(drop=True), y[tr], gtr)
        alpha = choose_alpha(meta_train, y[tr], gtr)
        meta_model = Ridge(alpha=alpha).fit(meta_train, y[tr])
        meta_test = np.column_stack([fitted[n].predict(xte) for n in meta_names])
        pred["STACK_RIDGE_UNCONSTRAINED"][te] = meta_model.predict(meta_test)
        alpha_records.append({"scheme": scheme_name, "fold": fold, "ridge_alpha": alpha})

        overlap = None if groups is None else len(set(groups[tr]).intersection(set(groups[te])))
        fold_records.append(
            {"scheme": scheme_name, "fold": fold, "train_rows": len(tr), "test_rows": len(te), "group_overlap": overlap}
        )

    results = []
    pred_frames = []
    for name, p in pred.items():
        results.append(
            {
                "scheme": scheme_name,
                "model": name,
                "n_rows": len(df),
                "n_groups": None if groups is None else len(np.unique(groups)),
                **metric(y, p),
            }
        )
        pred_frames.append(
            pd.DataFrame(
                {
                    "row_id": np.arange(len(df)),
                    "actual_qe_mg_g": y,
                    "predicted_qe_mg_g": p,
                    "model": name,
                    "scheme": scheme_name,
                }
            )
        )
    return results, pred_frames, fold_records, alpha_records, feature_counts


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = base.load_data()
    # Re-add removal_percent as raw context only; transformer drops it before modelling.
    original = pd.read_csv(base.DATA_PATH, encoding="utf-8-sig")
    for col in base.NUMERIC_FEATURES + [base.TARGET]:
        original[col] = original[col].map(base.parse_numeric)
    original = original.dropna(subset=[base.TARGET]).reset_index(drop=True)
    # keep cleaned grouping from base loader while retaining original columns
    for c in original.columns:
        if c not in df.columns:
            df[c] = original[c]
    if "removal_percent" not in df.columns:
        df["removal_percent"] = original["removal_percent"]

    groups = grouping.build_groups(df)
    results, preds, folds, alphas, counts = [], [], [], [], []
    for scheme in ["row_random", "citation_strict", "secondary_system_proxy", "adsorbent_holdout"]:
        r, p, f, a, c = evaluate_scheme(df, scheme, groups[scheme])
        results.extend(r); preds.extend(p); folds.extend(f); alphas.extend(a); counts.extend(c)

    res = pd.DataFrame(results)
    res.to_csv(OUT_DIR / "feature_parity_model_family_comparison.csv", index=False)
    pd.concat(preds, ignore_index=True).to_csv(OUT_DIR / "feature_parity_oof_predictions.csv", index=False)
    pd.DataFrame(folds).to_csv(OUT_DIR / "feature_parity_fold_integrity.csv", index=False)
    pd.DataFrame(alphas).to_csv(OUT_DIR / "feature_parity_stack_alpha.csv", index=False)
    pd.DataFrame(counts).to_csv(OUT_DIR / "feature_parity_feature_counts.csv", index=False)

    print("=== ORIGINAL-FEATURE PARITY / LEAKAGE-AWARE VALIDATION ===")
    print(res.to_string(index=False))
    print("\nFeature counts by fold:")
    print(pd.DataFrame(counts).to_string(index=False))
    print("\nGuardrail: Q_MAX constraint and removal_percent remain excluded from predictive fitting.")


if __name__ == "__main__":
    main()
