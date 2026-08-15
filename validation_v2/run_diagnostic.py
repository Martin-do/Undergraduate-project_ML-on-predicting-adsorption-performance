"""Fast diagnostic entrypoint for CI.

Runs the same study-aware harness with 500 study-cluster bootstrap replicates.
The full harness retains 2,000 replicates for the locked analysis stage.
"""
import study_aware_validation as validation

_original_bootstrap = validation.cluster_bootstrap_ci


def diagnostic_bootstrap(y_true, y_pred, groups, n_boot=500, seed=42):
    return _original_bootstrap(y_true, y_pred, groups, n_boot=500, seed=seed)


validation.cluster_bootstrap_ci = diagnostic_bootstrap

if __name__ == "__main__":
    validation.main()
