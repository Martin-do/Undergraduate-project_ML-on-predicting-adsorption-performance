"""One-command reproducibility runner for the ID-SEAD conference salvage.

This executes the corrected V2.1 evidence path, verifies anti-leakage rules and
checks the regenerated numerical results against the historical successful V2.1
GitHub Actions runs. It does NOT reproduce or reinstate the legacy ID-SEAD
manuscript claim.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VALIDATION = REPO / "validation_v2"
OUT = HERE / "outputs"
CONFIG = HERE / "config.json"
BASELINE = HERE / "baseline_expectations.json"

sys.path.insert(0, str(VALIDATION))
import final_validation_v21  # noqa: E402
import robustness_validation_v21  # noqa: E402

SOURCE_FILES = [
    "Biochar_dye_filtered.xlsx",
    "Raw_data.xlsx",
    "validation_v2/adsorption_dataset_v2.csv",
    "validation_v2/primary_study_map.csv",
    "validation_v2/non_iftikhar_primary_source_map_v21.csv",
    "validation_v2/adsorbent_domain_map.csv",
    "validation_v2/build_dataset_v21.py",
    "validation_v2/final_validation_v21.py",
    "validation_v2/robustness_validation_v21.py",
    "validation_v2/external_validation_v2.py",
    "validation_v2/feature_parity_validation.py",
    "validation_v2/feature_parity_validation_fixed.py",
    "validation_v2/study_aware_validation.py",
    "conference_salvage/reproducibility/config.json",
    "conference_salvage/reproducibility/baseline_expectations.json",
    "conference_salvage/reproducibility/requirements.txt",
]

COPY_NAMES = [
    "adsorption_dataset_v2_1.csv",
    "adsorption_dataset_v2_1_summary.json",
    "non_iftikhar_v21_match_audit.csv",
    "final_validation_v21_metrics.csv",
    "final_validation_v21_folds.csv",
    "final_validation_v21_stack_alphas.csv",
    "final_validation_v21_predictions.csv",
    "final_validation_v21_feature_counts.csv",
    "final_validation_v21_audit.json",
    "robustness_v21_loso_pooled.csv",
    "robustness_v21_loso_per_study.csv",
    "robustness_v21_loso_equal_study.csv",
    "robustness_v21_loso_predictions.csv",
    "robustness_v21_condition_only_metrics.csv",
    "robustness_v21_condition_only_folds.csv",
    "robustness_v21_conventional_only_metrics.csv",
    "robustness_v21_conventional_only_folds.csv",
    "robustness_v21_external_metrics.csv",
    "robustness_v21_external_predictions.csv",
    "robustness_v21_audit.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:
        return "unavailable"


def package_versions() -> dict[str, str]:
    names = ["numpy", "pandas", "scipy", "scikit-learn", "xgboost", "openpyxl"]
    return {name: importlib.metadata.version(name) for name in names}


def verify_contract(validation_out: Path) -> dict[str, bool]:
    final_audit = json.loads((validation_out / "final_validation_v21_audit.json").read_text())
    robust_audit = json.loads((validation_out / "robustness_v21_audit.json").read_text())
    folds = pd.read_csv(validation_out / "final_validation_v21_folds.csv")
    metrics = pd.read_csv(validation_out / "final_validation_v21_metrics.csv")
    loso = pd.read_csv(validation_out / "robustness_v21_loso_pooled.csv")

    grouped = folds[folds["scheme"].str.contains("primary_group_5fold", na=False)]
    strict_group = metrics[metrics["scheme"].eq("strict_comparable_273__primary_group_5fold")]
    strict_random = metrics[metrics["scheme"].eq("strict_comparable_273__row_random_5fold")]
    strict_loso = loso[loso["scope"].eq("strict_comparable_273")]

    checks = {
        "grouped_folds_exist": not grouped.empty,
        "zero_primary_study_overlap_in_grouped_folds": bool(not grouped.empty and grouped["group_overlap"].fillna(-1).eq(0).all()),
        "same_rows_random_vs_grouped_strict": bool(set(strict_group["n_rows"].astype(int)) == {273} and set(strict_random["n_rows"].astype(int)) == {273}),
        "strict_group_has_24_primary_studies": bool(set(strict_group["n_groups"].dropna().astype(int)) == {24}),
        "loso_strict_has_rf_and_xgb": set(strict_loso["model"]) == {"RF", "XGB"},
        "legacy_qmax_disabled_final": final_audit.get("qmax_624_used") is False,
        "removal_percent_disabled_final": final_audit.get("removal_percent_used_as_predictor") is False,
        "fold_safe_preprocessing_declared": "fold" in final_audit.get("preprocessing", "").lower(),
        "legacy_qmax_disabled_robustness": robust_audit.get("qmax_624_used") is False,
        "removal_percent_disabled_robustness": robust_audit.get("removal_percent_used_as_predictor") is False,
        "external_targets_not_used_for_tuning": robust_audit.get("external_targets_used_for_tuning") is False,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("Reproducibility contract failed: " + ", ".join(failed))
    return checks


def verify_historical_baseline(validation_out: Path) -> dict:
    expected = json.loads(BASELINE.read_text(encoding="utf-8"))
    tol = float(expected["numeric_tolerance"])
    actual_packages = package_versions()
    expected_packages = expected["environment"]["packages"]
    package_checks = {name: actual_packages.get(name) == version for name, version in expected_packages.items()}
    python_check = platform.python_version() == expected["environment"]["python"]

    metrics = pd.read_csv(validation_out / "final_validation_v21_metrics.csv")
    loso = pd.read_csv(validation_out / "robustness_v21_loso_pooled.csv")
    summary = json.loads((validation_out / "adsorption_dataset_v2_1_summary.json").read_text())

    scope_expected = expected["scope"]
    scope_checks = {
        "usable_rows": int(summary["rows"]) == int(scope_expected["usable_rows"]),
        "primary_confirmed_rows": int(summary["primary_confirmed_rows"]) == int(scope_expected["primary_confirmed_rows"]),
        "primary_confirmed_studies": int(summary["primary_confirmed_studies"]) == int(scope_expected["primary_confirmed_studies"]),
        "strict_comparable_rows": int(summary["strict_comparable_rows"]) == int(scope_expected["strict_comparable_rows"]),
        "strict_comparable_studies": int(summary["strict_comparable_studies"]) == int(scope_expected["strict_comparable_studies"]),
    }

    numeric_checks: dict[str, bool] = {}
    scheme_map = {
        "row_random_5fold": "strict_comparable_273__row_random_5fold",
        "primary_group_5fold": "strict_comparable_273__primary_group_5fold",
    }
    for short_scheme, scheme in scheme_map.items():
        for model, vals in expected["strict_comparable_273"][short_scheme].items():
            row = metrics[(metrics["scheme"] == scheme) & (metrics["model"] == model)]
            if len(row) != 1:
                numeric_checks[f"{short_scheme}.{model}.row_exists"] = False
                continue
            r = row.iloc[0]
            for key in ["r2", "rmse_mg_g", "mae_mg_g"]:
                numeric_checks[f"{short_scheme}.{model}.{key}"] = math.isclose(float(r[key]), float(vals[key]), rel_tol=0.0, abs_tol=tol)

    for model, vals in expected["strict_comparable_273"]["loso"].items():
        row = loso[(loso["scope"] == "strict_comparable_273") & (loso["model"] == model)]
        if len(row) != 1:
            numeric_checks[f"loso.{model}.row_exists"] = False
            continue
        r = row.iloc[0]
        for key in ["r2", "rmse_mg_g", "mae_mg_g", "median_ae_mg_g"]:
            numeric_checks[f"loso.{model}.{key}"] = math.isclose(float(r[key]), float(vals[key]), rel_tol=0.0, abs_tol=tol)

    verification = {
        "historical_reference": expected["historical_reference"],
        "python_exact_match": python_check,
        "package_exact_match": package_checks,
        "scope_exact_match": scope_checks,
        "numeric_exact_within_tolerance": numeric_checks,
        "numeric_tolerance": tol,
    }
    failed = []
    if not python_check:
        failed.append("python")
    failed.extend([f"package:{k}" for k, ok in package_checks.items() if not ok])
    failed.extend([f"scope:{k}" for k, ok in scope_checks.items() if not ok])
    failed.extend([f"metric:{k}" for k, ok in numeric_checks.items() if not ok])
    if failed:
        raise RuntimeError("Historical V2.1 baseline mismatch: " + ", ".join(failed))
    return verification


def build_snapshot(validation_out: Path) -> dict:
    metrics = pd.read_csv(validation_out / "final_validation_v21_metrics.csv")
    loso = pd.read_csv(validation_out / "robustness_v21_loso_pooled.csv")

    def metric_row(scheme: str, model: str) -> dict:
        row = metrics[(metrics.scheme == scheme) & (metrics.model == model)]
        if len(row) != 1:
            raise RuntimeError(f"Expected one metric row for {scheme}/{model}, found {len(row)}")
        r = row.iloc[0]
        return {"r2": float(r.r2), "rmse_mg_g": float(r.rmse_mg_g), "mae_mg_g": float(r.mae_mg_g), "median_ae_mg_g": float(r.median_ae_mg_g)}

    snapshot = {
        "scientific_scope": "strict_comparable_273",
        "rows": 273,
        "primary_studies": 24,
        "row_random_is_diagnostic_only": True,
        "row_random_5fold": {m: metric_row("strict_comparable_273__row_random_5fold", m) for m in ["RF", "XGB", "STACK_RIDGE_UNCONSTRAINED"]},
        "primary_group_5fold": {m: metric_row("strict_comparable_273__primary_group_5fold", m) for m in ["RF", "XGB", "STACK_RIDGE_UNCONSTRAINED"]},
        "loso": {},
        "inverse_design_claim_enabled": False,
        "deployment_claim_enabled": False,
    }
    for model in ["RF", "XGB"]:
        row = loso[(loso.scope == "strict_comparable_273") & (loso.model == model)]
        if len(row) != 1:
            raise RuntimeError(f"Expected one strict LOSO row for {model}")
        r = row.iloc[0]
        snapshot["loso"][model] = {"r2": float(r.r2), "rmse_mg_g": float(r.rmse_mg_g), "mae_mg_g": float(r.mae_mg_g), "median_ae_mg_g": float(r.median_ae_mg_g)}
    return snapshot


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.iterdir():
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)

    final_validation_v21.main()
    robustness_validation_v21.main()

    validation_out = VALIDATION / "outputs"
    checks = verify_contract(validation_out)
    baseline_verification = verify_historical_baseline(validation_out)

    for name in COPY_NAMES:
        src = validation_out / name
        if not src.exists():
            raise FileNotFoundError(f"Required evidence artifact missing: {src}")
        shutil.copy2(src, OUT / name)

    snapshot = build_snapshot(validation_out)
    (OUT / "conference_metrics_snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    (OUT / "contract_checks.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    (OUT / "baseline_verification.json").write_text(json.dumps(baseline_verification, indent=2), encoding="utf-8")

    freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    (OUT / "environment_freeze.txt").write_text(freeze, encoding="utf-8")

    input_hashes = {}
    for rel in SOURCE_FILES:
        p = REPO / rel
        if not p.exists():
            raise FileNotFoundError(f"Input/source file missing: {rel}")
        input_hashes[rel] = sha256(p)

    output_hashes = {p.name: sha256(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "run_manifest.json"}
    manifest = {
        "analysis_id": config["analysis_id"],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_sha(),
        "python": sys.version,
        "platform": platform.platform(),
        "packages": package_versions(),
        "config": config,
        "historical_baseline_matched": True,
        "historical_reference": baseline_verification["historical_reference"],
        "input_sha256": input_hashes,
        "output_sha256": output_hashes,
        "contract_checks_passed": True,
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Conference salvage corrected validation complete.")
    print("Historical V2.1 baseline match: PASS")
    print(json.dumps(snapshot, indent=2))
    print(f"Evidence directory: {OUT}")


if __name__ == "__main__":
    main()
