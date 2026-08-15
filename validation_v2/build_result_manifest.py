"""Build the single source-of-truth manifest for manuscript-eligible V2 results.

This script only consumes outputs regenerated earlier in the SAME CI job. It never
retypes scientific metric values. Every row records source output, script, commit
SHA, role/status and whether it is eligible for manuscript use.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

COMMIT = os.environ.get("GITHUB_SHA", "local_or_unknown")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "local_or_unknown")

rows: list[dict[str, Any]] = []
_counter = 0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add(*, phase: str, role: str, status: str, eligible: bool, dataset: str,
        scope: str = "", validation: str = "", model: str = "", metric: str,
        value: Any, unit: str = "", n_rows: Any = "", n_groups: Any = "",
        source_output: str, script: str, notes: str = "") -> None:
    global _counter
    _counter += 1
    if isinstance(value, (np.floating, np.integer)):
        value = value.item()
    rows.append({
        "result_id": f"V2R{_counter:04d}",
        "phase": phase,
        "role": role,
        "status": status,
        "manuscript_eligible": bool(eligible),
        "dataset": dataset,
        "training_scope": scope,
        "validation_scheme": validation,
        "model": model,
        "metric": metric,
        "value": value,
        "unit": unit,
        "n_rows": n_rows,
        "n_groups": n_groups,
        "source_output": source_output,
        "script": script,
        "commit_sha": COMMIT,
        "workflow_run_id": RUN_ID,
        "notes": notes,
    })


def load_json(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def add_metric_table(path_name: str, phase: str, role: str, status: str, eligible: bool,
                     dataset: str, script: str, scheme_col: str = "scheme",
                     scope_col: str | None = None) -> None:
    path = OUT / path_name
    df = pd.read_csv(path)
    for _, r in df.iterrows():
        scheme = str(r.get(scheme_col, "")) if scheme_col in df.columns else ""
        scope = str(r.get(scope_col, "")) if scope_col and scope_col in df.columns else ""
        if not scope and scheme.startswith("loso_"):
            scope = scheme.removeprefix("loso_")
        model = str(r.get("model", ""))
        n_rows = r.get("n_rows", "")
        n_groups = r.get("n_groups", r.get("n_primary_studies", ""))
        for col, unit in [
            ("r2", "dimensionless"),
            ("rmse_mg_g", "mg/g"),
            ("mae_mg_g", "mg/g"),
            ("median_ae_mg_g", "mg/g"),
        ]:
            if col in df.columns and pd.notna(r.get(col)):
                add(phase=phase, role=role, status=status, eligible=eligible,
                    dataset=dataset, scope=scope, validation=scheme, model=model,
                    metric=col, value=float(r[col]), unit=unit, n_rows=n_rows,
                    n_groups=n_groups, source_output=path_name, script=script)


def main() -> None:
    # Phase 1: leakage and physical-bound facts.
    leak = load_json("manifest_leakage_audit.json")
    ov = leak["legacy_style_random_partition_overlap"]
    add(phase="P1", role="primary", status="confirmed", eligible=True,
        dataset="project_corpus", validation="legacy_style_random_80_20",
        metric="test_rows_source_overlap", value=ov["test_rows_whose_source_is_also_in_train"],
        unit="rows", n_rows=ov["test_rows"], n_groups=ov["overlapping_sources"],
        source_output="manifest_leakage_audit.json", script="leakage_manifest_audit.py",
        notes="Legacy source-label overlap diagnostic; primary-study IDs supersede source labels where reconstructed.")
    add(phase="P1", role="primary", status="confirmed", eligible=True,
        dataset="project_corpus", validation="legacy_style_random_80_20",
        metric="test_rows_source_overlap_percent", value=ov["test_rows_source_overlap_percent"],
        unit="percent", n_rows=ov["test_rows"], source_output="manifest_leakage_audit.json",
        script="leakage_manifest_audit.py")

    bound = load_json("physical_bound_audit.json")
    for metric, unit in [
        ("observed_max_mg_g", "mg/g"),
        ("rows_above_legacy_qmax", "rows"),
        ("percent_rows_above_legacy_qmax", "percent"),
    ]:
        add(phase="P1", role="primary", status="confirmed", eligible=True,
            dataset="project_corpus", metric=metric, value=bound[metric], unit=unit,
            n_rows=bound["observed_rows"], source_output="physical_bound_audit.json",
            script="physical_bound_audit.py",
            notes="Legacy universal QMAX=624 mg/g is invalid for the full corpus.")

    # Diagnostic feature-parity comparators. Only row_random is useful as the
    # leakage-prone comparator; the proxy groupings are retained in the manifest as diagnostics.
    fp_path = "feature_parity_model_family_comparison.csv"
    fp_df = pd.read_csv(OUT / fp_path)
    for _, r in fp_df.iterrows():
        role = "diagnostic"
        eligible = str(r["scheme"]) == "row_random"
        for col, unit in [("r2", "dimensionless"), ("rmse_mg_g", "mg/g"), ("mae_mg_g", "mg/g")]:
            add(phase="P2", role=role, status="confirmed", eligible=eligible,
                dataset="project_corpus", validation=str(r["scheme"]), model=str(r["model"]),
                metric=col, value=float(r[col]), unit=unit, n_rows=int(r["n_rows"]),
                n_groups="" if pd.isna(r.get("n_groups")) else r.get("n_groups"),
                source_output=fp_path, script="feature_parity_validation_fixed.py",
                notes="QMAX and removal_percent excluded; row_random is leakage-prone comparator, not generalization evidence.")

    # Phase 3: strict confirmed-primary-study holdout.
    p3audit = load_json("primary_study_holdout_audit.json")
    add(phase="P3", role="primary", status="confirmed", eligible=True,
        dataset="confirmed_iftikhar_primary_rows", validation="primary_study_holdout",
        metric="confirmed_primary_rows", value=p3audit["strict_confirmed_primary_rows"], unit="rows",
        n_rows=p3audit["iftikhar_inherited_usable_rows"], n_groups=p3audit["strict_confirmed_primary_studies"],
        source_output="primary_study_holdout_audit.json", script="primary_study_holdout_validation.py")
    add_metric_table("primary_study_holdout_metrics.csv", "P3", "primary", "confirmed", True,
                     "confirmed_iftikhar_primary_rows", "primary_study_holdout_validation.py")

    # Phase 4: domain composition + LOSO.
    subsets = pd.read_csv(OUT / "precursor_domain_candidate_subsets.csv")
    for _, r in subsets.iterrows():
        add(phase="P4", role="primary", status="confirmed", eligible=True,
            dataset="confirmed_iftikhar_primary_rows", scope=str(r["subset"]),
            metric="subset_rows", value=int(r["rows"]), unit="rows", n_rows=int(r["rows"]),
            n_groups=int(r["primary_studies"]), source_output="precursor_domain_candidate_subsets.csv",
            script="precursor_domain_audit.py")
        add(phase="P4", role="primary", status="confirmed", eligible=True,
            dataset="confirmed_iftikhar_primary_rows", scope=str(r["subset"]),
            metric="primary_studies", value=int(r["primary_studies"]), unit="studies",
            n_rows=int(r["rows"]), n_groups=int(r["primary_studies"]),
            source_output="precursor_domain_candidate_subsets.csv", script="precursor_domain_audit.py")
    add_metric_table("domain_restricted_loso_metrics.csv", "P4", "primary", "confirmed", True,
                     "confirmed_primary_domain_subset", "domain_restricted_validation.py")

    # Phase 5: AD diagnostics. Diagnostic only, not a deployment gate.
    adperf = pd.read_csv(OUT / "applicability_domain_performance_by_support.csv")
    for _, r in adperf.iterrows():
        for col, unit in [("coverage_fraction", "fraction"), ("r2", "dimensionless"),
                          ("rmse_mg_g", "mg/g"), ("mae_mg_g", "mg/g")]:
            if pd.notna(r[col]):
                add(phase="P5", role="diagnostic", status="confirmed", eligible=True,
                    dataset="confirmed_primary_domain_subset", scope=str(r["subset"]),
                    validation=str(r["support_rule"]), model=str(r["model"]), metric=col,
                    value=float(r[col]), unit=unit, n_rows=int(r["n_rows"]),
                    source_output="applicability_domain_performance_by_support.csv",
                    script="applicability_domain_validation.py",
                    notes="Corrected fold-constant-feature handling; AD failed as reliability gate.")
    adc = pd.read_csv(OUT / "applicability_domain_error_distance_correlation.csv")
    for _, r in adc.iterrows():
        add(phase="P5", role="diagnostic", status="confirmed", eligible=True,
            dataset="confirmed_primary_domain_subset", scope=str(r["subset"]), model=str(r["model"]),
            metric="spearman_distance_vs_abs_error", value=float(r["spearman_distance_vs_abs_error"]),
            unit="correlation", source_output="applicability_domain_error_distance_correlation.csv",
            script="applicability_domain_validation.py")

    # Phase 6 uncertainty: manuscript-eligible as a negative reliability result.
    unc = pd.read_csv(OUT / "group_aware_uncertainty_summary.csv")
    for _, r in unc.iterrows():
        for col, unit in [
            ("row_weighted_coverage", "fraction"),
            ("equal_study_mean_coverage", "fraction"),
            ("studies_with_zero_coverage", "studies"),
            ("mean_interval_width_mg_g", "mg/g"),
        ]:
            add(phase="P6", role="diagnostic", status="confirmed", eligible=True,
                dataset="confirmed_primary_domain_subset", scope=str(r["subset"]),
                validation=f"{r['interval_type']}@{float(r['level']):.2f}", model="XGB",
                metric=col, value=float(r[col]), unit=unit, n_rows=int(r["rows"]),
                n_groups=int(r["studies"]), source_output="group_aware_uncertainty_summary.csv",
                script="group_aware_uncertainty.py",
                notes="Empirical study-aware residual intervals; no formal conformal guarantee claimed.")

    # Phase 7 clean external transfer.
    ext = pd.read_csv(OUT / "external_v2_metrics.csv")
    for _, r in ext.iterrows():
        for col, unit in [("r2", "dimensionless"), ("rmse_mg_g", "mg/g"),
                          ("mae_mg_g", "mg/g"), ("median_ae_mg_g", "mg/g")]:
            add(phase="P7", role="primary", status="confirmed", eligible=True,
                dataset=str(r["dataset"]), scope=str(r["training_scope"]),
                validation="external_transfer", model=str(r["model"]), metric=col,
                value=float(r[col]), unit=unit, n_rows=int(r["n_external"]),
                n_groups="" if pd.isna(r.get("n_training_primary_studies")) else r.get("n_training_primary_studies"),
                source_output="external_v2_metrics.csv", script="external_validation_v2.py",
                notes="No project QMAX censoring; external targets not used for tuning; source-disjointness not fully proven.")

    # Historical/superseded values remain machine-visible but manuscript-ineligible
    # except when explicitly discussed as reproducibility artifacts.
    legacy_ext = pd.read_csv(OUT / "external_v2_legacy_reference_metrics.csv")
    for _, r in legacy_ext.iterrows():
        for col, unit in [("r2", "dimensionless"), ("rmse_mg_g", "mg/g"),
                          ("legacy_qmax_violation_percent", "percent")]:
            add(phase="LEGACY", role="historical", status="superseded", eligible=False,
                dataset=str(r["correct_dataset"]), validation="legacy_saved_notebook_execution",
                model="legacy_ID_SEAD", metric=col, value=float(r[col]), unit=unit,
                n_rows=int(r["n"]), source_output="external_v2_legacy_reference_metrics.csv",
                script="external_validation_v2.py",
                notes=f"Saved notebook artifact under legacy label {r['legacy_dataset_label']}; not a reproducible V2 benchmark.")

    recon = load_json("legacy_liu_rowcount_reconciliation.json")
    add(phase="LEGACY", role="historical", status="superseded", eligible=False,
        dataset="liu_2025_dyes", validation="exact_replay_current_notebook_and_workbook",
        metric="legacy_qmax_replay_rows", value=recon["exact_replay_counts"]["after_c0_filter_exact_legacy"],
        unit="rows", source_output="legacy_liu_rowcount_reconciliation.json",
        script="reconcile_legacy_liu_rowcount.py",
        notes=f"Saved notebook output was {recon['saved_notebook_output_rows']} rows; exact current replay differs, so saved output is stale.")

    manifest = pd.DataFrame(rows)
    manifest.to_csv(OUT / "result_manifest_v2.csv", index=False)
    (OUT / "result_manifest_v2.json").write_text(
        json.dumps(manifest.to_dict("records"), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    input_files = [
        ROOT / "final_final_adsorption_done_dataset.csv",
        ROOT / "Biochar_dye_filtered.xlsx",
        ROOT / "Raw_data.xlsx",
        HERE / "primary_study_map.csv",
        HERE / "adsorbent_domain_map.csv",
    ]
    metadata = {
        "manifest_version": "v2",
        "commit_sha": COMMIT,
        "workflow_run_id": RUN_ID,
        "result_rows": int(len(manifest)),
        "manuscript_eligible_rows": int(manifest["manuscript_eligible"].sum()),
        "input_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in input_files},
        "rules": [
            "Only outputs regenerated in the same workflow job are ingested.",
            "Historical/superseded rows are machine-visible but manuscript-ineligible unless explicitly discussed as audit artifacts.",
            "No manuscript table value should be hand-entered after manifest generation.",
            "Inverse-design and universal-QMAX outputs are intentionally absent from eligible V2 predictive results.",
        ],
    }
    (OUT / "result_manifest_v2_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Compact human-readable summary generated from the manifest, not from typed values.
    eligible = manifest[manifest["manuscript_eligible"]].copy()
    lines = [
        "# V2 deterministic result manifest summary",
        "",
        f"Commit: `{COMMIT}`",
        f"Workflow run: `{RUN_ID}`",
        f"Total manifest rows: {len(manifest)}; manuscript-eligible: {len(eligible)}",
        "",
        "## Primary/diagnostic phases",
        "",
    ]
    for phase, g in eligible.groupby("phase", sort=False):
        lines.append(f"### {phase}")
        lines.append("")
        for _, r in g.head(40).iterrows():
            model = f" / {r['model']}" if r['model'] else ""
            scope = f" / {r['training_scope']}" if r['training_scope'] else ""
            lines.append(f"- `{r['dataset']}{scope}{model}` — {r['metric']} = {r['value']} {r['unit']}")
        if len(g) > 40:
            lines.append(f"- … {len(g)-40} additional rows in CSV/JSON manifest")
        lines.append("")
    (OUT / "RESULT_MANIFEST_V2_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")

    print("=== RESULT MANIFEST METADATA ===")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    print("\n=== MANUSCRIPT-ELIGIBLE RESULT COUNTS BY PHASE ===")
    print(eligible.groupby("phase").size().to_string())


if __name__ == "__main__":
    main()
