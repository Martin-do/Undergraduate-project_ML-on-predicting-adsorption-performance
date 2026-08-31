from __future__ import annotations

"""Forensic audit of the legacy engineered pollutant_class representation.

The original feature engineering uses substring regexes such as ``cr`` and ``as``
without token boundaries and also fails to expand several dye abbreviations. This
script performs a TARGET-BLIND representation audit:

1. enumerate every pollutant label in the strict 273-row population;
2. compare the legacy deterministic class to an exact-label class reconstructed
   from chemical names and the already-recovered primary-study provenance;
3. quantify row-level label disagreement;
4. rerun matched row-random, study-grouped and LOSO RF/XGB using the corrected
   pollutant class while leaving all other preprocessing/model settings intact;
5. compare corrected-full performance with the existing remove-pollutant-class
   sensitivity.

The corrected mapping is frozen below before model fitting. No target value or
model score is used to assign a pollutant class.
"""

import json
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VALIDATION = REPO / "validation_v2"
GATE_DIR = REPO / "conference_salvage" / "supervisor_revision_gate_v3"
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(VALIDATION))
sys.path.insert(0, str(GATE_DIR))

import feature_parity_validation as fp  # noqa: E402
from feature_parity_validation_fixed import DtypeSafeParityPreprocessor  # noqa: E402
import run_supervisor_revision_gate_v3 as gate  # noqa: E402

fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor
RANDOM_STATE = 42

# Exact-label map derived from pollutant identity and recovered primary-study
# evidence, never from qe or validation performance.
CURATED_CLASS = {
    # Metal ions
    "Cd²⁺": "metal_ion",
    "Cr(VI)": "metal_ion",
    "Cu²⁺": "metal_ion",
    "Pb²⁺": "metal_ion",
    "Zn²⁺": "metal_ion",

    # Dyes / colorants. Ambiguous abbreviations are resolved by the recovered
    # primary-study context (e.g. Ravenni: amaranth; Wong: MB/RB5; Mei: Neutral
    # Red; Gao: acid brilliant scarlet; Li: cationic dye set).
    "AB25": "dye",
    "AM": "dye",
    "Alizarin Red (AR)": "dye",
    "Basic Violet 10": "dye",
    "C-Red": "dye",
    "C-Yellow": "dye",
    "CBlue": "dye",
    "CCB": "dye",
    "CCR": "dye",
    "CCY": "dye",
    "Congo Red (CR)": "dye",
    "GR": "dye",
    "MB": "dye",
    "MO": "dye",
    "Malachite Green": "dye",
    "Methyl Violet (MV)": "dye",
    "Methylene Blue": "dye",
    "Methylene Blue (MB)": "dye",
    "NR": "dye",
    "Phenol Red": "dye",
    "RB5": "dye",
    "Remazol Brilliant Blue R": "dye",
    "Rhd B": "dye",

    # Non-dye bulk organic water-quality target retained in the strict corpus.
    "Oil & Grease": "bulk_organic",
}

EVIDENCE_NOTE = {
    "AB25": "Archin et al. 2019 primary study explicitly identifies Acid Blue 25 as an anionic dye.",
    "AM": "Ravenni et al. 2020 primary study explicitly uses amaranth as the anionic dye.",
    "Basic Violet 10": "Chemical/paper label is Basic Violet 10, a dye; legacy regex matches 'as' inside 'Basic'.",
    "Congo Red (CR)": "Chemical/paper label is Congo Red dye; legacy regex matches the abbreviation 'CR' as chromium substring.",
    "GR": "Gao et al. 2016 primary study is dye adsorption and identifies acid brilliant scarlet as model pollutant.",
    "MB": "Wong et al. 2018 primary study explicitly identifies MB as methylene blue dye.",
    "RB5": "Wong et al. 2018 primary study explicitly identifies RB5 as Reactive Black 5 dye.",
    "MO": "Gupta et al. 2019 primary study concerns adsorption of organic dyes; MO is treated as a dye label.",
    "NR": "Recovered Mei et al. provenance explicitly identifies Neutral Red adsorption.",
    "Rhd B": "Xiao et al. 2020 primary study explicitly identifies rhodamine B dye.",
    "CCB": "Li et al. 2021 primary study reports a cationic-dye panel.",
    "CCR": "Li et al. 2021 primary study reports a cationic-dye panel; legacy substring 'cr' maps this label to heavy_metal.",
    "CCY": "Li et al. 2021 primary study reports a cationic-dye panel.",
    "C-Red": "Li et al. 2021 primary study reports a cationic-dye panel.",
    "C-Yellow": "Li et al. 2021 primary study reports a cationic-dye panel.",
    "CBlue": "Li et al. 2021 primary study reports a cationic-dye panel.",
    "Oil & Grease": "Igwegbe et al. 2021 target is oil and grease; legacy regex matches 'as' within 'grease' and wrongly labels heavy_metal.",
}


def metric(y, p):
    return {
        "r2": float(r2_score(y, p)),
        "rmse_mg_g": float(np.sqrt(mean_squared_error(y, p))),
        "mae_mg_g": float(mean_absolute_error(y, p)),
        "median_ae_mg_g": float(np.median(np.abs(np.asarray(y) - np.asarray(p)))),
    }


def normalized_legacy(v):
    return {"heavy_metal":"metal_ion", "organic_dye":"dye", "pharmaceutical":"pharmaceutical", "phenol":"phenol", "other_organic":"other_organic"}.get(str(v), str(v))


def corrected_engineer_factory(original):
    def corrected_engineer(df):
        out = original(df)
        labels = df["pollutant"].astype("string").fillna("").str.strip()
        unknown = sorted(set(labels) - set(CURATED_CLASS))
        if unknown:
            raise RuntimeError(f"Unmapped strict pollutant labels encountered: {unknown}")
        out["pollutant_class"] = labels.map(CURATED_CLASS).to_numpy()
        return out
    return corrected_engineer


@contextmanager
def corrected_pollutant_engineering():
    old = fp.engineer_deterministic
    fp.engineer_deterministic = corrected_engineer_factory(old)
    try:
        yield
    finally:
        fp.engineer_deterministic = old


def audit_mapping(strict):
    raw = strict[gate.RAW_MODEL_COLS].copy()
    legacy = fp.engineer_deterministic(raw)["pollutant_class"].astype(str)
    curated = strict["pollutant"].astype(str).str.strip().map(CURATED_CLASS)
    if curated.isna().any():
        raise RuntimeError("Curated pollutant mapping incomplete")

    detail = strict[["pollutant", "primary_study_id_v21", "primary_study_doi_v21"]].copy()
    detail["legacy_pollutant_class"] = legacy.to_numpy()
    detail["legacy_normalized_class"] = detail["legacy_pollutant_class"].map(normalized_legacy)
    detail["curated_pollutant_class"] = curated.to_numpy()
    detail["class_disagreement"] = detail["legacy_normalized_class"] != detail["curated_pollutant_class"]
    detail["evidence_note"] = detail["pollutant"].map(EVIDENCE_NOTE).fillna("Class is explicit from chemical name / recovered primary-study pollutant identity.")
    detail.to_csv(OUT / "pollutant_class_row_audit.csv", index=False)

    mapping = detail.groupby(["pollutant","legacy_pollutant_class","legacy_normalized_class","curated_pollutant_class","evidence_note"], dropna=False).agg(
        n_rows=("pollutant","size"), n_studies=("primary_study_id_v21","nunique")
    ).reset_index()
    mapping["class_disagreement"] = mapping["legacy_normalized_class"] != mapping["curated_pollutant_class"]
    mapping.to_csv(OUT / "pollutant_class_exact_label_map.csv", index=False)

    summary = {
        "strict_rows": int(len(detail)),
        "unique_pollutant_labels": int(detail.pollutant.nunique()),
        "disagreement_rows": int(detail.class_disagreement.sum()),
        "disagreement_fraction": float(detail.class_disagreement.mean()),
        "disagreement_unique_labels": int(mapping.class_disagreement.sum()),
        "legacy_class_counts": detail.legacy_pollutant_class.value_counts().to_dict(),
        "curated_class_counts": detail.curated_pollutant_class.value_counts().to_dict(),
        "target_used_to_construct_mapping": False,
        "performance_used_to_construct_mapping": False,
    }
    (OUT / "pollutant_class_integrity_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def evaluate(strict):
    y = strict[gate.base.TARGET].to_numpy(float)
    groups = strict["primary_study_id_v21"].astype(str).to_numpy()
    raw = strict[gate.RAW_MODEL_COLS].copy()
    bank = fp.models()
    rows = []
    study_rows = []

    with corrected_pollutant_engineering():
        for scheme in ["row_random_5fold", "primary_group_5fold"]:
            preds = {m: np.empty(len(strict), float) for m in ["RF","XGB"]}
            for tr, te in gate.split_list(y, groups, scheme):
                prep = DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
                xtr = prep.transform(raw.iloc[tr]); xte = prep.transform(raw.iloc[te])
                for model in ["RF","XGB"]:
                    preds[model][te] = clone(bank[model]).fit(xtr, y[tr]).predict(xte)
            for model, p in preds.items():
                rows.append({"representation":"corrected_pollutant_class_full","scheme":scheme,"model":model,"n_rows":len(strict),"n_studies":len(np.unique(groups)),**metric(y,p)})

        preds = {m: np.empty(len(strict), float) for m in ["RF","XGB"]}
        for study in sorted(np.unique(groups)):
            te = np.flatnonzero(groups == study); tr = np.flatnonzero(groups != study)
            prep = DtypeSafeParityPreprocessor().fit(raw.iloc[tr])
            xtr = prep.transform(raw.iloc[tr]); xte = prep.transform(raw.iloc[te])
            for model in ["RF","XGB"]:
                p = clone(bank[model]).fit(xtr, y[tr]).predict(xte)
                preds[model][te] = p
                study_rows.append({"representation":"corrected_pollutant_class_full","held_out_primary_study":study,"model":model,"n_test_rows":len(te),**gate.safe_study_metric(y[te],p)})
        for model,p in preds.items():
            rows.append({"representation":"corrected_pollutant_class_full","scheme":"LOSO","model":model,"n_rows":len(strict),"n_studies":len(np.unique(groups)),**metric(y,p)})

    pd.DataFrame(rows).to_csv(OUT / "corrected_pollutant_class_validation.csv", index=False)
    pd.DataFrame(study_rows).to_csv(OUT / "corrected_pollutant_class_loso_per_study.csv", index=False)
    return pd.DataFrame(rows)


def main():
    _, strict = gate.load_strict()
    summary = audit_mapping(strict)
    metrics = evaluate(strict)
    report = {"mapping":summary, "validation":metrics.to_dict(orient="records")}
    (OUT / "POLLUTANT_REPRESENTATION_FORENSIC_SUMMARY.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("=== POLLUTANT CLASS INTEGRITY ===")
    print(json.dumps(summary, indent=2))
    print("\n=== CORRECTED POLLUTANT-CLASS VALIDATION ===")
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
