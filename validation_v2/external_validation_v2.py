"""Clean V2 external-validation rerun for the two legacy external datasets.

Key corrections relative to the submitted/legacy notebook
----------------------------------------------------------
1. No Q_MAX=624 target truncation or prediction constraint is used.
2. Dataset A is identified as Liu et al. 2025 (Carbon Research), not "Shen 2024".
3. Jaffari et al. DOI is 10.1016/j.cej.2023.143073, not the legacy 144684 value.
4. Jaffari `Average pore size` is NOT mapped to adsorbent particle size. Those are
   different physical quantities; particle_size_mm remains missing and is imputed
   from training only.
5. Jaffari pyrolysis temperature is actually used. The legacy rename key omitted
   trailing whitespace in the workbook header, silently causing the feature to be
   ignored and replaced by the training template value.
6. External missing features are handled by the same training-fitted V2 parity
   preprocessor rather than by an already-engineered median template.
7. `removal_percent` is never used.

This is an external transfer diagnostic, not model selection: no external target is
used to tune preprocessing, hyperparameters, domain definitions, or thresholds.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

import applicability_domain_validation as ad
import feature_parity_validation as fp
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor
import primary_study_holdout_validation as psh
import study_aware_validation as base

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

LIU_FILE = ROOT / "Biochar_dye_filtered.xlsx"
JAFFARI_FILE = ROOT / "Raw_data.xlsx"
DOMAIN_MAP = HERE / "adsorbent_domain_map.csv"

RAW_MODEL_COLS = base.RAW_FEATURES + ["removal_percent", "source_link"]
MODELS = ["LR", "RF", "XGB"]
TRAINING_SCOPES = ["full_corpus", "broad_biogenic_waste", "waste_derived_carbon"]

# Molecular weights preserved from the legacy notebook's explicit conversion map.
# They are used only to convert the source dataset's Q (mmol/g) and C0 (mmol/L)
# into the project's mg/g and mg/L target/input units.
DYE_MW = {
    "methylene blue": 319.85,
    "malachite green": 364.91,
    "crystal violet": 407.99,
    "rhodamine b": 479.02,
    "congo red": 696.66,
    "remazol brilliant blue r": 626.54,
    "reactive orange 16": 617.54,
    "reactive yellow": 991.82,
    "acid blue 9": 792.85,
    "acid blue9": 792.85,
    "acid red-18": 604.47,
    "acid orange 7": 350.32,
    "food red 17": 496.42,
}

SOURCE_META = {
    "liu_2025_dyes": {
        "correct_name": "Liu et al. 2025 — biochar/dye literature dataset",
        "doi": "10.1007/s44246-025-00213-9",
        "legacy_label": "Shen et al. 2024",
        "source_file": LIU_FILE.name,
    },
    "jaffari_2023_ec": {
        "correct_name": "Jaffari et al. 2023 — emerging contaminants on biochar",
        "doi": "10.1016/j.cej.2023.143073",
        "legacy_doi": "10.1016/j.cej.2023.144684",
        "source_file": JAFFARI_FILE.name,
    },
}


def numeric(s: pd.Series) -> pd.Series:
    return s.map(base.parse_numeric).astype(float)


def empty_raw(n: int) -> pd.DataFrame:
    d = pd.DataFrame(index=np.arange(n))
    d["adsorbent"] = pd.Series([pd.NA] * n, dtype="string")
    d["method_processing"] = pd.Series([pd.NA] * n, dtype="string")
    d["surface_area_m2g"] = np.nan
    d["particle_size_mm"] = np.nan
    d["pore_volume_cm3g"] = np.nan
    d["pollutant"] = pd.Series([pd.NA] * n, dtype="string")
    d["initial_concentration_mgL"] = np.nan
    d["temperature_c"] = np.nan
    d["contact_time_min"] = np.nan
    d["qe_mg_g"] = np.nan
    d["removal_percent"] = np.nan
    d["ph"] = np.nan
    d["dose_gL"] = np.nan
    d["source_link"] = pd.Series([pd.NA] * n, dtype="string")
    return d


def load_liu() -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    pre = pd.read_excel(LIU_FILE, sheet_name="After preprocessing")
    orig = pd.read_excel(LIU_FILE, sheet_name="original")
    if len(pre) != len(orig):
        raise ValueError("Liu workbook preprocessing/original sheets have different row counts")

    dye_raw = orig["TypeDye"].astype("string")
    dye_key = dye_raw.str.strip().str.lower()
    mw = dye_key.map(DYE_MW)
    q_mmol = numeric(pre["Q"])
    c0_mmol = numeric(pre["C0"])
    qe = q_mmol * mw
    c0 = c0_mmol * mw

    raw = empty_raw(len(pre))
    # Source workbook contains biochar experiments but the preprocessed sheet does
    # not preserve a row-level biochar name. Use an honest generic material label;
    # never manufacture a base-material identity.
    raw["adsorbent"] = "biochar_external_unspecified"
    raw["method_processing"] = pd.NA
    raw["surface_area_m2g"] = numeric(pre["BET"])
    raw["pore_volume_cm3g"] = numeric(pre["PV"])
    raw["pollutant"] = dye_raw.fillna("Unknown")
    raw["initial_concentration_mgL"] = c0
    raw["temperature_c"] = numeric(pre["T"])
    raw["ph"] = numeric(pre["pH_sol"])
    # No valid cross-dataset equivalents are supplied for particle size, contact
    # time, dose, or pyrolysis temperature in this sheet. D is not repurposed as
    # particle size: the source paper derives D from PV and BET.
    raw["qe_mg_g"] = qe
    raw["source_link"] = "liu_2025_external"

    valid_mw = mw.notna()
    valid_target = raw["qe_mg_g"].notna() & np.isfinite(raw["qe_mg_g"]) & (raw["qe_mg_g"] > 0)
    valid_c0 = raw["initial_concentration_mgL"].notna() & np.isfinite(raw["initial_concentration_mgL"]) & (raw["initial_concentration_mgL"] > 0)
    keep = valid_mw & valid_target & valid_c0

    # Reproduce legacy selection only for audit counts; do not use it for V2.
    legacy_qmax_keep = keep & (raw["qe_mg_g"] <= 624.0)
    audit = {
        "dataset": "liu_2025_dyes",
        "raw_rows": int(len(raw)),
        "rows_with_mapped_dye_mw": int(valid_mw.sum()),
        "positive_convertible_rows_v2": int(keep.sum()),
        "legacy_rows_if_qmax_624_filter_applied": int(legacy_qmax_keep.sum()),
        "rows_removed_by_legacy_qmax_only": int((keep & ~legacy_qmax_keep).sum()),
        "v2_qe_min_mg_g": float(raw.loc[keep, "qe_mg_g"].min()),
        "v2_qe_max_mg_g": float(raw.loc[keep, "qe_mg_g"].max()),
        "v2_c0_min_mgL": float(raw.loc[keep, "initial_concentration_mgL"].min()),
        "v2_c0_max_mgL": float(raw.loc[keep, "initial_concentration_mgL"].max()),
        "unmapped_dye_labels": sorted(dye_key[mw.isna() & dye_key.notna()].dropna().unique().tolist()),
        "target_upper_filter_applied_v2": False,
        "missing_cross_dataset_fields": ["particle_size_mm", "contact_time_min", "dose_gL", "pyrolysis_temp_c"],
    }

    literature = pd.read_excel(LIU_FILE, sheet_name="literature collection", header=None)
    literature.columns = ["literature_entry"] + [f"extra_{i}" for i in range(1, literature.shape[1])]
    return raw.loc[keep].reset_index(drop=True), audit, literature


def strip_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    return out


def build_processing(temp: pd.Series, minutes: pd.Series) -> pd.Series:
    vals = []
    for t, m in zip(temp, minutes):
        if pd.notna(t) and np.isfinite(t):
            if pd.notna(m) and np.isfinite(m):
                vals.append(f"Pyrolysis at {t:g}°C for {m:g} min")
            else:
                vals.append(f"Pyrolysis at {t:g}°C")
        else:
            vals.append(pd.NA)
    return pd.Series(vals, dtype="string")


def load_jaffari() -> tuple[pd.DataFrame, dict]:
    src = strip_columns(pd.read_excel(JAFFARI_FILE, sheet_name="Sheet1"))
    n = len(src)
    raw = empty_raw(n)

    pyro = numeric(src["Pyrolysis temperature"])
    pyro_time = numeric(src["Pyrolysis time"])
    volume = numeric(src["Volume"])
    dosage = numeric(src["Adsorbent dosage"])
    dose_gl = dosage / volume.replace(0, np.nan)

    raw["adsorbent"] = src["Adsorbent"].astype("string").fillna("Unknown")
    raw["method_processing"] = build_processing(pyro, pyro_time)
    raw["surface_area_m2g"] = numeric(src["Surface area"])
    raw["particle_size_mm"] = np.nan  # Average pore size is not particle size.
    raw["pore_volume_cm3g"] = numeric(src["Pore volume"])
    raw["pollutant"] = src["Pollutant"].astype("string").fillna("Unknown")
    raw["initial_concentration_mgL"] = numeric(src["Initial concentration"])
    raw["temperature_c"] = numeric(src["Adsorption temperature"])
    raw["contact_time_min"] = numeric(src["Adsorption time"])
    raw["qe_mg_g"] = numeric(src["Capacity"])
    raw["ph"] = numeric(src["Solution pH"])
    raw["dose_gL"] = dose_gl
    raw["source_link"] = "jaffari_2023_external"

    keep = raw["qe_mg_g"].notna() & np.isfinite(raw["qe_mg_g"]) & (raw["qe_mg_g"] > 0)
    legacy_qmax_keep = keep & (raw["qe_mg_g"] <= 624.0)

    audit = {
        "dataset": "jaffari_2023_ec",
        "raw_rows": int(n),
        "positive_target_rows_v2": int(keep.sum()),
        "legacy_rows_if_qmax_624_filter_applied_before_feature_complete_case": int(legacy_qmax_keep.sum()),
        "rows_removed_by_legacy_qmax_only": int((keep & ~legacy_qmax_keep).sum()),
        "v2_qe_min_mg_g": float(raw.loc[keep, "qe_mg_g"].min()),
        "v2_qe_max_mg_g": float(raw.loc[keep, "qe_mg_g"].max()),
        "unique_pollutants": int(raw.loc[keep, "pollutant"].nunique()),
        "unique_adsorbents": int(raw.loc[keep, "adsorbent"].nunique()),
        "target_upper_filter_applied_v2": False,
        "average_pore_size_mapped_to_particle_size_v2": False,
        "pyrolysis_temperature_used_v2": True,
        "legacy_pyrolysis_header_bug": "legacy rename key omitted trailing spaces from workbook header, so pyrolysis_temp_c was silently left at template value",
    }
    return raw.loc[keep].reset_index(drop=True), audit


def build_training_scopes() -> dict[str, pd.DataFrame]:
    full = base.load_data().copy().reset_index(drop=True)
    confirmed, _, _ = psh.build_strict_dataset()
    dmap = pd.read_csv(DOMAIN_MAP, keep_default_na=False)
    confirmed = confirmed.merge(
        dmap[["project_adsorbent", "broad_biogenic_waste", "waste_derived_carbon"]].rename(columns={"project_adsorbent": "adsorbent"}),
        on="adsorbent", how="left", validate="many_to_one"
    )
    return {
        "full_corpus": full,
        "broad_biogenic_waste": confirmed[confirmed["broad_biogenic_waste"].eq("yes")].copy().reset_index(drop=True),
        "waste_derived_carbon": confirmed[confirmed["waste_derived_carbon"].eq("yes")].copy().reset_index(drop=True),
    }


def feature_coverage(raw_ext: pd.DataFrame, dataset: str) -> pd.DataFrame:
    rows = []
    for col in [
        "surface_area_m2g", "particle_size_mm", "pore_volume_cm3g",
        "initial_concentration_mgL", "temperature_c", "contact_time_min",
        "ph", "dose_gL", "method_processing", "adsorbent", "pollutant",
    ]:
        s = raw_ext[col]
        if col in base.NUMERIC_FEATURES:
            available = pd.to_numeric(s, errors="coerce").notna()
        else:
            available = s.astype("string").notna() & s.astype("string").str.strip().ne("")
        rows.append({
            "dataset": dataset,
            "feature": col,
            "available_rows": int(available.sum()),
            "total_rows": int(len(raw_ext)),
            "available_fraction": float(available.mean()),
        })
    return pd.DataFrame(rows)


def category_novelty(prep: DtypeSafeParityPreprocessor, raw_ext: pd.DataFrame) -> pd.DataFrame:
    engineered = fp.engineer_deterministic(raw_ext).reset_index(drop=True)
    rows = []
    for j, col in enumerate(fp.CAT_COLS):
        known = {str(v) for v in prep.encoder.categories_[j]}
        vals = engineered[col].astype(str)
        novel = ~vals.isin(known)
        rows.append({
            "engineered_category": col,
            "novel_rows": int(novel.sum()),
            "total_rows": int(len(vals)),
            "novel_fraction": float(novel.mean()),
            "novel_values": " | ".join(sorted(vals[novel].unique().tolist())),
        })
    return pd.DataFrame(rows)


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    return {
        "r2": float(r2_score(y, p)),
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, p))),
        "mae_mg_g": float(mean_absolute_error(y, p)),
        "median_ae_mg_g": float(np.median(np.abs(y - p))),
        "prediction_min_mg_g": float(np.min(p)),
        "prediction_max_mg_g": float(np.max(p)),
    }


def cross_study_support(training: pd.DataFrame, prep: DtypeSafeParityPreprocessor, xtr: np.ndarray, xext: np.ndarray):
    """Corrected training-only support descriptor when primary groups are available."""
    if "primary_study_id" not in training.columns or training["primary_study_id"].eq("").any():
        return None, None
    names = list(prep.output_cols)
    features, idx, excluded = ad.select_variable_support_features(xtr, names)
    if len(features) < 5:
        return None, {"reason": "fewer_than_5_variable_support_features", "excluded": excluded}
    scaler = StandardScaler().fit(xtr[:, idx])
    ztr = scaler.transform(xtr[:, idx])
    zext = scaler.transform(xext[:, idx])
    groups = training["primary_study_id"].to_numpy(str)
    train_dist = ad.cross_study_knn_distance(ztr, groups, ad.K_NEIGHBORS)
    ext_dist = ad.test_knn_distance(ztr, zext, ad.K_NEIGHBORS)
    q95 = float(np.quantile(train_dist, 0.95))
    return ext_dist, {
        "active_features": features,
        "excluded_training_constant_features": excluded,
        "train_cross_study_q95": q95,
        "external_mean_distance": float(np.mean(ext_dist)),
        "external_median_distance": float(np.median(ext_dist)),
        "external_q95_supported_fraction": float(np.mean(ext_dist <= q95)),
    }


def evaluate_dataset(dataset_name: str, ext: pd.DataFrame, scopes: dict[str, pd.DataFrame]):
    metric_rows = []
    prediction_frames = []
    novelty_frames = []
    support_records = []
    bank = fp.models()
    yext = ext[base.TARGET].to_numpy(float)

    for scope_name, training in scopes.items():
        raw_train = training[RAW_MODEL_COLS].copy()
        ytrain = training[base.TARGET].to_numpy(float)
        raw_ext = ext[RAW_MODEL_COLS].copy()
        prep = DtypeSafeParityPreprocessor().fit(raw_train)
        xtr = prep.transform(raw_train)
        xext = prep.transform(raw_ext)

        novelty = category_novelty(prep, raw_ext)
        novelty.insert(0, "training_scope", scope_name)
        novelty.insert(0, "dataset", dataset_name)
        novelty_frames.append(novelty)

        ext_dist, support = cross_study_support(training, prep, xtr, xext)
        support_records.append({
            "dataset": dataset_name,
            "training_scope": scope_name,
            "support_available": bool(support and "train_cross_study_q95" in support),
            "support_detail": json.dumps(support, ensure_ascii=False) if support else "",
        })

        for model_name in MODELS:
            model = clone(bank[model_name]).fit(xtr, ytrain)
            pred = model.predict(xext)
            m = metrics(yext, pred)
            metric_rows.append({
                "dataset": dataset_name,
                "training_scope": scope_name,
                "model": model_name,
                "n_external": int(len(ext)),
                "n_training": int(len(training)),
                "n_training_primary_studies": int(training["primary_study_id"].nunique()) if "primary_study_id" in training.columns else np.nan,
                **m,
            })
            pf = pd.DataFrame({
                "dataset": dataset_name,
                "training_scope": scope_name,
                "model": model_name,
                "external_row_id": np.arange(len(ext)),
                "actual_qe_mg_g": yext,
                "predicted_qe_mg_g": pred,
                "abs_error_mg_g": np.abs(yext - pred),
            })
            if ext_dist is not None:
                pf["training_support_distance"] = ext_dist
                pf["training_q95_supported"] = ext_dist <= json.loads(support_records[-1]["support_detail"])["train_cross_study_q95"]
            prediction_frames.append(pf)

    return (
        pd.DataFrame(metric_rows),
        pd.concat(prediction_frames, ignore_index=True),
        pd.concat(novelty_frames, ignore_index=True),
        pd.DataFrame(support_records),
    )


def primary_doi_overlap_with_liu_literature(literature: pd.DataFrame) -> dict:
    pmap = pd.read_csv(HERE / "primary_study_map.csv", keep_default_na=False)
    dois = sorted({d.strip().lower() for d in pmap["doi"] if d.strip()})
    blob = "\n".join(literature.astype(str).fillna("").agg(" ".join, axis=1).tolist()).lower()
    matches = [d for d in dois if d in blob]
    return {
        "training_primary_dois_checked": len(dois),
        "literal_doi_matches_in_liu_literature_sheet": matches,
        "literal_overlap_count": len(matches),
        "limitation": "A zero literal DOI match is not proof of study-disjointness because citations may omit DOIs or use different formatting.",
    }


def main() -> None:
    liu, liu_audit, literature = load_liu()
    jaffari, jaffari_audit = load_jaffari()
    scopes = build_training_scopes()

    coverage = pd.concat([
        feature_coverage(liu, "liu_2025_dyes"),
        feature_coverage(jaffari, "jaffari_2023_ec"),
    ], ignore_index=True)

    all_metrics = []
    all_preds = []
    all_novelty = []
    all_support = []
    for name, ext in [("liu_2025_dyes", liu), ("jaffari_2023_ec", jaffari)]:
        m, p, n, s = evaluate_dataset(name, ext, scopes)
        all_metrics.append(m); all_preds.append(p); all_novelty.append(n); all_support.append(s)

    metrics_df = pd.concat(all_metrics, ignore_index=True)
    predictions_df = pd.concat(all_preds, ignore_index=True)
    novelty_df = pd.concat(all_novelty, ignore_index=True)
    support_df = pd.concat(all_support, ignore_index=True)

    metrics_df.to_csv(OUT / "external_v2_metrics.csv", index=False)
    predictions_df.to_csv(OUT / "external_v2_predictions.csv", index=False)
    novelty_df.to_csv(OUT / "external_v2_category_novelty.csv", index=False)
    support_df.to_csv(OUT / "external_v2_support_diagnostics.csv", index=False)
    coverage.to_csv(OUT / "external_v2_feature_coverage.csv", index=False)
    liu.to_csv(OUT / "external_v2_liu_prepared.csv", index=False)
    jaffari.to_csv(OUT / "external_v2_jaffari_prepared.csv", index=False)

    legacy_reference = pd.DataFrame([
        {"legacy_dataset_label": "Shen 2024", "correct_dataset": "liu_2025_dyes", "n": 525, "r2": -18.7858, "rmse_mg_g": 696.09, "legacy_qmax_violation_percent": 45.71},
        {"legacy_dataset_label": "Jaffari 2023", "correct_dataset": "jaffari_2023_ec", "n": 3673, "r2": -16.0973, "rmse_mg_g": 303.55, "legacy_qmax_violation_percent": 61.75},
    ])
    legacy_reference.to_csv(OUT / "external_v2_legacy_reference_metrics.csv", index=False)

    audit = {
        "sources": SOURCE_META,
        "liu_preparation": liu_audit,
        "jaffari_preparation": jaffari_audit,
        "liu_training_doi_overlap_literal_audit": primary_doi_overlap_with_liu_literature(literature),
        "training_scopes": {
            k: {
                "rows": int(len(v)),
                "primary_studies": int(v["primary_study_id"].nunique()) if "primary_study_id" in v.columns else None,
            }
            for k, v in scopes.items()
        },
        "models": MODELS,
        "external_target_used_for_tuning": False,
        "qmax_used": False,
        "removal_percent_used": False,
        "row_bootstrap_ci_reported": False,
        "reason_no_external_ci": "row-level provenance/group IDs are unavailable or incomplete for these external compilations; a naive row bootstrap would overstate independence",
        "external_independence_claim": "separate published compilations; complete primary-study overlap with project training data has not been proven absent",
    }
    (OUT / "external_v2_audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== EXTERNAL V2 AUDIT ===")
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    print("\n=== FEATURE COVERAGE ===")
    print(coverage.to_string(index=False))
    print("\n=== CLEAN EXTERNAL METRICS ===")
    print(metrics_df.to_string(index=False))
    print("\n=== ENGINEERED CATEGORY NOVELTY ===")
    print(novelty_df.to_string(index=False))
    print("\n=== SUPPORT DIAGNOSTICS ===")
    print(support_df.to_string(index=False))


if __name__ == "__main__":
    main()
