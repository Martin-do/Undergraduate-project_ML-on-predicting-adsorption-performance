"""Lightweight smoke test for random-vs-study-grouped validation.

This is not the final uncertainty analysis. It removes XGBoost and bootstrap CIs
so CI can quickly verify the central leakage question using LR and RF.
"""
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

import study_aware_validation as validation


def smoke_models():
    return {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(
            n_estimators=200,
            min_samples_leaf=2,
            random_state=validation.RANDOM_STATE,
            n_jobs=1,
        ),
    }


def no_bootstrap(*args, **kwargs):
    return {}


validation.make_models = smoke_models
validation.cluster_bootstrap_ci = no_bootstrap

if __name__ == "__main__":
    validation.main()
