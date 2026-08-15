"""Compatibility fix for feature_parity_validation.py.

The first feature-parity CI run exposed a pandas nullable-Int64 assignment error
when StandardScaler float outputs were assigned back into integer-typed columns.
This wrapper preserves the original forensic script and replaces only the
preprocessor's fit/transform methods with dtype-safe equivalents.
"""
from __future__ import annotations

import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import feature_parity_validation as fp


class DtypeSafeParityPreprocessor(fp.FoldSafeParityPreprocessor):
    def fit(self, raw: pd.DataFrame):
        x = fp.engineer_deterministic(raw).copy()

        for col in fp.GROUP_IMPUTE:
            med = x.groupby("material_class", dropna=False)[col].median()
            self.group_medians[col] = med.to_dict()
            self.global_medians[col] = float(pd.to_numeric(x[col], errors="coerce").median())
            x[col] = x[col].fillna(x["material_class"].map(self.group_medians[col]))
            x[col] = x[col].fillna(self.global_medians[col])

        for col in fp.GLOBAL_IMPUTE:
            self.global_medians[col] = float(pd.to_numeric(x[col], errors="coerce").median())
            x[col] = x[col].fillna(self.global_medians[col])

        x = self._add_interactions(x)

        self.encoder = OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False)
        enc = self.encoder.fit_transform(x[fp.CAT_COLS])
        self.encoded_cols = self.encoder.get_feature_names_out(fp.CAT_COLS).tolist()
        enc_df = pd.DataFrame(enc, columns=self.encoded_cols, index=x.index)
        x_num = pd.concat([x.drop(columns=fp.CAT_COLS), enc_df], axis=1)

        # Force the scale block to ordinary floating dtypes before assigning
        # StandardScaler outputs. This is the only behavioral change from the
        # original feature-parity script.
        scale_input = x_num[fp.SCALE_COLS].astype("float64")
        self.scaler = StandardScaler().fit(scale_input)
        scaled = self.scaler.transform(scale_input)
        for j, col in enumerate(fp.SCALE_COLS):
            x_num[col] = scaled[:, j]

        self.output_cols = x_num.columns.tolist()
        return self

    def transform(self, raw: pd.DataFrame):
        x = fp.engineer_deterministic(raw).copy()

        for col in fp.GROUP_IMPUTE:
            x[col] = x[col].fillna(x["material_class"].map(self.group_medians[col]))
            x[col] = x[col].fillna(self.global_medians[col])
        for col in fp.GLOBAL_IMPUTE:
            x[col] = x[col].fillna(self.global_medians[col])

        x = self._add_interactions(x)
        enc = self.encoder.transform(x[fp.CAT_COLS])
        enc_df = pd.DataFrame(enc, columns=self.encoded_cols, index=x.index)
        x_num = pd.concat([x.drop(columns=fp.CAT_COLS), enc_df], axis=1)
        x_num = x_num.reindex(columns=self.output_cols, fill_value=0.0)

        scale_input = x_num[fp.SCALE_COLS].astype("float64")
        scaled = self.scaler.transform(scale_input)
        for j, col in enumerate(fp.SCALE_COLS):
            x_num[col] = scaled[:, j]

        return x_num.to_numpy(dtype=float)


fp.FoldSafeParityPreprocessor = DtypeSafeParityPreprocessor


if __name__ == "__main__":
    fp.main()
