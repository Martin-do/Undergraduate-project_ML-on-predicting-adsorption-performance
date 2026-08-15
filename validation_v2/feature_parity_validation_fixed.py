"""Compatibility fixes for feature_parity_validation.py.

The forensic feature-parity implementation is kept intact while this wrapper
addresses two runtime/data-boundary issues exposed by stricter validation:

1. pandas nullable-Int64 columns cannot receive StandardScaler float outputs;
2. under primary-study holdout, a numeric feature can be entirely missing from
   an outer/inner training fold, so a training-fold median does not exist.

For (2), an all-missing training feature is marked inactive for that fitted
preprocessor and set to 0.0 in BOTH training and held-out data. This is not an
imputation from the test fold: the held-out observations are deliberately
ignored because the training studies contain no information from which that
feature's effect could be learned.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import feature_parity_validation as fp


class DtypeSafeParityPreprocessor(fp.FoldSafeParityPreprocessor):
    def fit(self, raw: pd.DataFrame):
        x = fp.engineer_deterministic(raw).copy()
        self.inactive_training_features = set()

        for col in fp.GROUP_IMPUTE:
            numeric = pd.to_numeric(x[col], errors="coerce")
            global_median = numeric.median()
            if pd.isna(global_median):
                # No training-fold information exists for this variable. Never
                # inspect the held-out fold to manufacture an imputation value.
                self.inactive_training_features.add(col)
                self.group_medians[col] = {}
                self.global_medians[col] = 0.0
                x[col] = 0.0
                continue

            med = x.assign(**{col: numeric}).groupby("material_class", dropna=False)[col].median()
            self.group_medians[col] = med.to_dict()
            self.global_medians[col] = float(global_median)
            x[col] = numeric.fillna(x["material_class"].map(self.group_medians[col]))
            x[col] = x[col].fillna(self.global_medians[col])

        for col in fp.GLOBAL_IMPUTE:
            numeric = pd.to_numeric(x[col], errors="coerce")
            global_median = numeric.median()
            if pd.isna(global_median):
                self.inactive_training_features.add(col)
                self.global_medians[col] = 0.0
                x[col] = 0.0
                continue
            self.global_medians[col] = float(global_median)
            x[col] = numeric.fillna(self.global_medians[col])

        x = self._add_interactions(x)

        self.encoder = OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False)
        enc = self.encoder.fit_transform(x[fp.CAT_COLS])
        self.encoded_cols = self.encoder.get_feature_names_out(fp.CAT_COLS).tolist()
        enc_df = pd.DataFrame(enc, columns=self.encoded_cols, index=x.index)
        x_num = pd.concat([x.drop(columns=fp.CAT_COLS), enc_df], axis=1)

        # Ordinary floating dtypes are required before assigning scaler output.
        scale_input = x_num[fp.SCALE_COLS].astype("float64")
        if not np.isfinite(scale_input.to_numpy()).all():
            bad = scale_input.columns[~np.isfinite(scale_input.to_numpy()).all(axis=0)].tolist()
            raise ValueError(f"Non-finite training values remain after fold-safe preprocessing: {bad}")

        self.scaler = StandardScaler().fit(scale_input)
        scaled = self.scaler.transform(scale_input)
        for j, col in enumerate(fp.SCALE_COLS):
            x_num[col] = scaled[:, j]

        if not np.isfinite(x_num.to_numpy(dtype=float)).all():
            bad = x_num.columns[~np.isfinite(x_num.to_numpy(dtype=float)).all(axis=0)].tolist()
            raise ValueError(f"Non-finite training features remain after preprocessing: {bad}")

        self.output_cols = x_num.columns.tolist()
        return self

    def transform(self, raw: pd.DataFrame):
        x = fp.engineer_deterministic(raw).copy()

        for col in fp.GROUP_IMPUTE:
            if col in self.inactive_training_features:
                # Ignore held-out values for a feature that had no observations
                # in the training fold; otherwise preprocessing would use a
                # variable whose relationship to the target could not be learned.
                x[col] = 0.0
                continue
            x[col] = pd.to_numeric(x[col], errors="coerce")
            x[col] = x[col].fillna(x["material_class"].map(self.group_medians[col]))
            x[col] = x[col].fillna(self.global_medians[col])

        for col in fp.GLOBAL_IMPUTE:
            if col in self.inactive_training_features:
                x[col] = 0.0
                continue
            x[col] = pd.to_numeric(x[col], errors="coerce").fillna(self.global_medians[col])

        x = self._add_interactions(x)
        enc = self.encoder.transform(x[fp.CAT_COLS])
        enc_df = pd.DataFrame(enc, columns=self.encoded_cols, index=x.index)
        x_num = pd.concat([x.drop(columns=fp.CAT_COLS), enc_df], axis=1)
        x_num = x_num.reindex(columns=self.output_cols, fill_value=0.0)

        scale_input = x_num[fp.SCALE_COLS].astype("float64")
        if not np.isfinite(scale_input.to_numpy()).all():
            bad = scale_input.columns[~np.isfinite(scale_input.to_numpy()).all(axis=0)].tolist()
            raise ValueError(f"Non-finite held-out values remain after fold-safe preprocessing: {bad}")

        scaled = self.scaler.transform(scale_input)
        for j, col in enumerate(fp.SCALE_COLS):
            x_num[col] = scaled[:, j]

        arr = x_num.to_numpy(dtype=float)
        if not np.isfinite(arr).all():
            bad = x_num.columns[~np.isfinite(arr).all(axis=0)].tolist()
            raise ValueError(f"Non-finite held-out features remain after preprocessing: {bad}")
        return arr


fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor


if __name__ == "__main__":
    fp.main()
