from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "outputs"


class ReproducibilityContractTests(unittest.TestCase):
    def test_required_artifacts_exist(self):
        required = [
            "final_validation_v21_metrics.csv",
            "final_validation_v21_folds.csv",
            "robustness_v21_loso_pooled.csv",
            "conference_metrics_snapshot.json",
            "contract_checks.json",
            "environment_freeze.txt",
            "run_manifest.json",
        ]
        missing = [name for name in required if not (OUT / name).exists()]
        self.assertEqual(missing, [], f"Missing artifacts: {missing}")

    def test_grouped_folds_have_zero_study_overlap(self):
        folds = pd.read_csv(OUT / "final_validation_v21_folds.csv")
        grouped = folds[folds.scheme.str.contains("primary_group_5fold", na=False)]
        self.assertFalse(grouped.empty)
        self.assertTrue(grouped.group_overlap.fillna(-1).eq(0).all())

    def test_strict_scope_counts_are_frozen(self):
        metrics = pd.read_csv(OUT / "final_validation_v21_metrics.csv")
        grouped = metrics[metrics.scheme.eq("strict_comparable_273__primary_group_5fold")]
        self.assertEqual(set(grouped.n_rows.astype(int)), {273})
        self.assertEqual(set(grouped.n_groups.dropna().astype(int)), {24})

    def test_loso_is_primary_study_holdout(self):
        loso = pd.read_csv(OUT / "robustness_v21_loso_pooled.csv")
        strict = loso[loso.scope.eq("strict_comparable_273")]
        self.assertEqual(set(strict.model), {"RF", "XGB"})
        self.assertEqual(set(strict.n_studies.astype(int)), {24})

    def test_legacy_claims_are_disabled(self):
        snapshot = json.loads((OUT / "conference_metrics_snapshot.json").read_text())
        self.assertTrue(snapshot["row_random_is_diagnostic_only"])
        self.assertFalse(snapshot["inverse_design_claim_enabled"])
        self.assertFalse(snapshot["deployment_claim_enabled"])

    def test_all_runtime_contract_checks_pass(self):
        checks = json.loads((OUT / "contract_checks.json").read_text())
        self.assertTrue(checks)
        self.assertTrue(all(checks.values()), checks)


if __name__ == "__main__":
    unittest.main()
