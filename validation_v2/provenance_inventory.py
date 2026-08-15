"""Inventory rows currently attributed to the Moosavi secondary compilation.

This does not assign primary provenance. It emits deterministic signatures used
for manual/source-assisted reconstruction of the original primary studies.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "final_final_adsorption_done_dataset.csv"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def clean(s):
    return s.astype("string").fillna("").str.strip()


def main():
    df = pd.read_csv(DATA, encoding="utf-8-sig")
    src = clean(df["source_link"]).str.lower()
    m = df[src.str.contains("moosavi", na=False)].copy()
    m.insert(0, "dataset_row", m.index + 2)  # +2 for CSV header / 1-based line convention

    cols = [
        "dataset_row", "adsorbent", "pollutant", "method_processing",
        "surface_area_m2g", "particle_size_mm", "pore_volume_cm3g",
        "initial_concentration_mgL", "temperature_c", "contact_time_min",
        "qe_mg_g", "removal_percent", "ph", "dose_gL", "source_link"
    ]
    m[cols].to_csv(OUT / "moosavi_rows_inventory.csv", index=False)

    signatures = (
        m.groupby(["adsorbent", "pollutant", "method_processing"], dropna=False)
         .agg(
             rows=("adsorbent", "size"),
             qe_min=("qe_mg_g", "min"),
             qe_max=("qe_mg_g", "max"),
             surface_area=("surface_area_m2g", "first"),
             pore_volume=("pore_volume_cm3g", "first"),
             particle_size=("particle_size_mm", "first"),
         )
         .reset_index()
         .sort_values(["adsorbent", "pollutant", "method_processing"])
    )
    signatures.to_csv(OUT / "moosavi_system_signatures.csv", index=False)

    ads = (
        m.groupby("adsorbent", dropna=False)
         .agg(
             rows=("adsorbent", "size"),
             pollutants=("pollutant", lambda s: " | ".join(sorted(set(clean(s))))),
             processing=("method_processing", lambda s: " | ".join(sorted(set(clean(s))))),
             qe_min=("qe_mg_g", "min"),
             qe_max=("qe_mg_g", "max"),
         )
         .reset_index()
         .sort_values(["rows", "adsorbent"], ascending=[False, True])
    )
    ads.to_csv(OUT / "moosavi_adsorbent_inventory.csv", index=False)

    print("=== MOOSAVI ADSORBENT INVENTORY ===")
    print(ads.to_string(index=False))
    print("\n=== SYSTEM SIGNATURES ===")
    print(signatures.to_string(index=False))
    print(f"\nRows: {len(m)}; adsorbents: {m['adsorbent'].nunique()}; systems: {len(signatures)}")


if __name__ == "__main__":
    main()
