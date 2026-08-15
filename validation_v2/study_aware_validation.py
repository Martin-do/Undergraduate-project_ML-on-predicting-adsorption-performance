"""Study-aware validation harness for ID-SEAD V2.

Purpose
-------
Quantify how much the apparent predictive performance changes when rows from the
same literature source are prevented from appearing in both training and
validation folds.

This script intentionally starts with a transparent baseline feature set and
fold-safe sklearn Pipelines. It does NOT alter the original ID-SEAD notebooks.

Outputs are written to validation_v2/outputs/.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover - optional dependency
    XGBRegressor = None

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "final_final_adsorption_done_dataset.csv"
OUT_DIR = Path(__file__).resolve().parent / "outputs"
RANDOM_STATE = 42
N_SPLITS = 5

TARGET = "qe_mg_g"
GROUP_COL = "source_link"

# Deliberately exclude removal_percent because it is often mathematically linked
# to qe and may encode target information. source_link is used only as a group ID.
RAW_FEATURES = [
    "adsorbent",
    "method_processing",
    "surface_area_m2g",
    "particle_size_mm",
    "pore_volume_cm3g",
    "pollutant",
    "initial_concentration_mgL",
    "temperature_c",
    "contact_time_min",
    "ph",
    "dose_gL",
]

NUMERIC_FEATURES = [
    "surface_area_m2g",
    "particle_size_mm",
    "pore_volume_cm3g",
    "initial_concentration_mgL",
    "temperature_c",
    "contact_time_min",
    "ph",
    "dose_gL",
]
CATEGORICAL_FEATURES = ["adsorbent", "method_processing", "pollutant"]

MISSING_TOKENS = {
    "": np.nan,
    "n/a": np.nan,
    "na": np.nan,
    "n/p": np.nan,
    "np": np.nan,
    "not provided": np.nan,
    "none": np.nan,
    "nan": np.nan,
}


def parse_numeric(value):
    """Conservatively coerce heterogeneous literature-table values to float.

    Handles values such as '~25', '0.063-0.125', and textual missing markers.
    For a numeric range, use its midpoint and record only the transformed value;
    this script is a validation diagnostic, not the final scientific parser.
    """
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.number)):
        return float(value)

    s = str(value).strip().lower().replace("−", "-").replace("–", "-")
    if s in MISSING_TOKENS:
        return np.nan
    s = s.replace(",", "")

    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if not nums:
        return np.nan
    vals = [float(x) for x in nums]
    if len(vals) >= 2 and "-" in s and not s.lstrip().startswith("-"):
        return float(np.mean(vals[:2]))
    return vals[0]


def normalize_source(value: object) -> str:
    """Normalize source strings so superficial formatting does not split studies."""
    if pd.isna(value):
        return "unknown-source"
    s = str(value).strip().lower()
    s = re.sub(r"https?://(?:dx\.)?doi\.org/", "", s)
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\u00a0", " ").strip()
    return s or "unknown-source"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    required = set(RAW_FEATURES + [TARGET, GROUP_COL])
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    for col in NUMERIC_FEATURES + [TARGET]:
        df[col] = df[col].map(parse_numeric)

    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype("string").fillna("Unknown")

    df["study_group"] = df[GROUP_COL].map(normalize_source)
    df = df.dropna(subset=[TARGET]).reset_index(drop=True)
    return df


def make_preprocessor() -> ColumnTransformer:
    num = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    cat = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=2)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", num, NUMERIC_FEATURES),
            ("cat", cat, CATEGORICAL_FEATURES),
        ]
    )


def make_models():
    models = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(
            n_estimators=500,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }
    if XGBRegressor is not None:
        models["XGBoost"] = XGBRegressor(
            n_estimators=500,
            max_depth=4,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    return models


def metrics(y_true, y_pred):
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def cluster_bootstrap_ci(y_true, y_pred, groups, n_boot=2000, seed=42):
    """95% CIs by resampling whole studies, preserving within-study dependence."""
    frame = pd.DataFrame({"y": y_true, "p": y_pred, "g": groups}).reset_index(drop=True)
    unique = frame["g"].unique()
    rng = np.random.default_rng(seed)
    out = {"r2": [], "rmse": [], "mae": []}

    for _ in range(n_boot):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        parts = []
        # give duplicate sampled studies independent bootstrap identities by concat
        for g in sampled:
            parts.append(frame.loc[frame["g"] == g, ["y", "p"]])
        boot = pd.concat(parts, ignore_index=True)
        if boot["y"].nunique() < 2:
            continue
        m = metrics(boot["y"].to_numpy(), boot["p"].to_numpy())
        for key in out:
            out[key].append(m[key])

    return {
        key: [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]
        for key, vals in out.items()
        if vals
    }


def random_split_overlap_audit(df: pd.DataFrame) -> dict:
    """Measure source leakage under the legacy-style random row partition."""
    rng = np.random.default_rng(RANDOM_STATE)
    idx = np.arange(len(df))
    rng.shuffle(idx)
    cut = int(round(len(df) * 0.8))
    tr, te = idx[:cut], idx[cut:]
    train_groups = set(df.loc[tr, "study_group"])
    test_groups = set(df.loc[te, "study_group"])
    overlap = train_groups.intersection(test_groups)
    test_rows_seen_source = df.loc[te, "study_group"].isin(train_groups).sum()
    return {
        "train_rows": int(len(tr)),
        "test_rows": int(len(te)),
        "train_unique_sources": int(len(train_groups)),
        "test_unique_sources": int(len(test_groups)),
        "overlapping_sources": int(len(overlap)),
        "test_rows_whose_source_is_also_in_train": int(test_rows_seen_source),
        "test_rows_source_overlap_percent": float(100 * test_rows_seen_source / max(len(te), 1)),
        "overlap_source_examples": sorted(overlap)[:20],
    }


def evaluate(df: pd.DataFrame):
    X = df[RAW_FEATURES].copy()
    y = df[TARGET].to_numpy(dtype=float)
    groups = df["study_group"].to_numpy()

    n_groups = len(np.unique(groups))
    if n_groups < 2:
        raise ValueError("Need at least two independent source groups for grouped validation.")
    n_splits = min(N_SPLITS, n_groups)

    splitters = {
        "random_kfold": KFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE),
        "study_grouped": GroupKFold(n_splits=n_splits),
    }

    rows = []
    predictions = []

    for model_name, estimator in make_models().items():
        for validation_name, cv in splitters.items():
            pipe = Pipeline([("prep", make_preprocessor()), ("model", estimator)])
            kwargs = {"groups": groups} if validation_name == "study_grouped" else {}
            pred = cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1, **kwargs)
            m = metrics(y, pred)
            ci = cluster_bootstrap_ci(y, pred, groups)
            rows.append(
                {
                    "model": model_name,
                    "validation": validation_name,
                    "n_rows": len(df),
                    "n_studies": n_groups,
                    **m,
                    "r2_ci_low": ci.get("r2", [np.nan, np.nan])[0],
                    "r2_ci_high": ci.get("r2", [np.nan, np.nan])[1],
                    "rmse_ci_low": ci.get("rmse", [np.nan, np.nan])[0],
                    "rmse_ci_high": ci.get("rmse", [np.nan, np.nan])[1],
                }
            )
            predictions.append(
                pd.DataFrame(
                    {
                        "row_id": np.arange(len(df)),
                        "study_group": groups,
                        "actual_qe_mg_g": y,
                        "prediction_qe_mg_g": pred,
                        "model": model_name,
                        "validation": validation_name,
                    }
                )
            )

    return pd.DataFrame(rows), pd.concat(predictions, ignore_index=True)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()

    group_counts = (
        df.groupby("study_group", dropna=False)
        .size()
        .sort_values(ascending=False)
        .rename("rows")
        .reset_index()
    )
    group_counts.to_csv(OUT_DIR / "study_group_counts.csv", index=False)

    audit = {
        "dataset_rows_with_target": int(len(df)),
        "unique_study_groups": int(df["study_group"].nunique()),
        "largest_study_group_rows": int(group_counts["rows"].max()),
        "median_rows_per_study": float(group_counts["rows"].median()),
        "legacy_random_partition_overlap": random_split_overlap_audit(df),
        "notes": [
            "source_link is used only to define study groups and is excluded from model features.",
            "removal_percent is excluded because it may be algebraically related to qe and could leak target information.",
            "all imputation, scaling and one-hot encoding occur inside each CV training fold.",
            "grouped confidence intervals resample whole studies rather than individual rows.",
        ],
    }
    (OUT_DIR / "dataset_leakage_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    results, preds = evaluate(df)
    results.to_csv(OUT_DIR / "random_vs_grouped_cv.csv", index=False)
    preds.to_csv(OUT_DIR / "cross_validated_predictions.csv", index=False)

    print("\n=== DATASET / LEAKAGE AUDIT ===")
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    print("\n=== RANDOM VS STUDY-GROUPED VALIDATION ===")
    print(results.to_string(index=False))
    print(f"\nOutputs written to: {OUT_DIR}")


if __name__ == "__main__":
    main()
