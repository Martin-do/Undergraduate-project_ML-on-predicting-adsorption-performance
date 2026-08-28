"""Reconcile Paper 1 Draft V2 numerical and key wording claims against frozen evidence.

This is a manuscript-integrity gate, not a scientific re-analysis. It checks that
headline project-generated values appearing in the current working manuscript/tables
agree with the machine-readable registry, verifies key independence/reference wording,
and confirms that known prohibited legacy claim strings are absent.

Run from repository root:
    python paper1/manuscript/reconcile_manuscript_numbers.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "validation_v2" / "MULTIDATASET_RESULTS_REGISTRY.csv"
MANUSCRIPT = Path(__file__).resolve().parent / "PAPER1_MANUSCRIPT_DRAFT_V2.md"
TABLES = Path(__file__).resolve().parent / "TABLES_V1.md"
OUT = Path(__file__).resolve().parent / "reconciliation"
OUT.mkdir(parents=True, exist_ok=True)


def get_row(df: pd.DataFrame, dataset_id: str, model: str, feature_contains: str | None = None):
    hit = df[(df.dataset_id == dataset_id) & (df.model == model)]
    if feature_contains:
        hit = hit[hit.feature_set.astype(str).str.contains(feature_contains, regex=False)]
    if len(hit) != 1:
        raise RuntimeError(f"Expected one registry row for {dataset_id}/{model}; found {len(hit)}")
    return hit.iloc[0]


def token_variants(value: float, decimals: tuple[int, ...]) -> set[str]:
    return {f"{float(value):.{d}f}" for d in decimals}


def require_any(text: str, label: str, variants: set[str], results: list[dict]):
    found = sorted(v for v in variants if v in text)
    results.append(
        {
            "check": label,
            "status": "PASS" if found else "FAIL",
            "found": found,
            "expected_any": sorted(variants),
        }
    )


def phrase_present(text: str, phrase: str) -> bool:
    return phrase.lower() in text.lower()


def add_phrase_check(checks: list[dict], combined: str, label: str, phrases: list[str]) -> None:
    ok = all(phrase_present(combined, p) for p in phrases)
    checks.append(
        {
            "check": label,
            "status": "PASS" if ok else "FAIL",
            "required_phrases": " + ".join(phrases),
        }
    )


def figure_callout_present(text: str, fig_num: int) -> bool:
    """Recognize singular or compound callouts such as 'Figure 2' or 'Figures 3 and 4'."""
    pattern = rf"\bFigures?\b[^.\n]{{0,40}}\b{fig_num}\b"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def main():
    df = pd.read_csv(REGISTRY)
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    tables = TABLES.read_text(encoding="utf-8")
    combined = manuscript + "\n" + tables

    a = get_row(df, "martin_v21_strict", "XGB")
    b = get_row(df, "liu_2025_strict", "CatBoost500")
    c = get_row(df, "liu_2025_ammonia", "CatBoost500")
    m = get_row(df, "moosavi_2021_recoverable", "RF", "published nine-variable feature set")

    checks = []
    required = [
        ("Dataset A random R2", a.random_r2, (4,)),
        ("Dataset A grouped R2", a.grouped_r2, (4,)),
        ("Dataset A delta R2", a.delta_r2_random_minus_grouped, (4,)),
        ("Dataset A LOSO R2", a.loso_r2, (4,)),
        ("Liu dye random R2", b.random_r2, (4, 6)),
        ("Liu dye grouped R2", b.grouped_r2, (4, 6)),
        ("Liu dye delta R2", b.delta_r2_random_minus_grouped, (4, 6)),
        ("Liu dye LOSO R2", b.loso_r2, (4, 6)),
        ("Liu ammonia random R2", c.random_r2, (4, 6)),
        ("Liu ammonia grouped R2", c.grouped_r2, (4, 6)),
        ("Liu ammonia delta R2", c.delta_r2_random_minus_grouped, (4, 6)),
        ("Liu ammonia LOSO R2", c.loso_r2, (4, 6)),
        ("Moosavi random R2", m.random_r2, (4, 6)),
        ("Moosavi grouped R2", m.grouped_r2, (4, 6)),
    ]
    for label, value, decimals in required:
        require_any(combined, label, token_variants(value, decimals), checks)

    moosavi_lineage = phrase_present(combined, "lineage-overlapping")
    moosavi_nonindependent = any(
        phrase_present(combined, p)
        for p in [
            "not counted as independent",
            "excluded from the independent-replication count",
            "excluded from the independent replication count",
            "not independent",
        ]
    )
    checks.append(
        {
            "check": "Moosavi non-independence disclosed",
            "status": "PASS" if (moosavi_lineage and moosavi_nonindependent) else "FAIL",
            "required_phrases": "lineage-overlapping + an explicit non-independent/exclusion statement",
        }
    )

    add_phrase_check(
        checks,
        combined,
        "Liu shared curation lineage disclosed",
        ["shared a broader data-curation/author-team lineage"],
    )
    add_phrase_check(
        checks,
        combined,
        "Primary-study-disjoint Liu wording present",
        ["primary-study-disjoint"],
    )
    add_phrase_check(
        checks,
        combined,
        "Outcome-neutral boundary stated",
        ["does not necessarily", "source-aware"],
    )
    add_phrase_check(
        checks,
        combined,
        "Verified Liu ammonia author list present",
        ["Liu, C., Balasubramanian, P., An, J., & Li, F. (2025)"],
    )
    add_phrase_check(
        checks,
        combined,
        "Verified Moosavi full author list present",
        ["Moosavi, S., Manta, O., El-Badry, Y. A."],
    )

    for fig_num in range(1, 6):
        checks.append(
            {
                "check": f"Figure {fig_num} callout present",
                "status": "PASS" if figure_callout_present(manuscript, fig_num) else "FAIL",
            }
        )

    prohibited = [
        "QMAX = 624",
        "Q_MAX = 624",
        "Q_MAX=624",
        "validated inverse design",
        "stacked-ensemble superiority",
        "~0.90 unseen-study generalisation",
    ]
    for phrase in prohibited:
        present = phrase_present(combined, phrase)
        checks.append(
            {
                "check": f"Prohibited legacy claim absent: {phrase}",
                "status": "FAIL" if present else "PASS",
            }
        )

    population_strings = ["273", "24", "624", "17", "409", "7"]
    for token in population_strings:
        checks.append(
            {
                "check": f"Core population token present: {token}",
                "status": "PASS" if token in combined else "FAIL",
            }
        )

    report = pd.DataFrame(checks)
    report.to_csv(OUT / "manuscript_numeric_reconciliation.csv", index=False)

    failures = report[report.status == "FAIL"]
    summary = {
        "checks": int(len(report)),
        "passes": int((report.status == "PASS").sum()),
        "failures": int(len(failures)),
        "manuscript": str(MANUSCRIPT.relative_to(ROOT)),
        "tables": str(TABLES.relative_to(ROOT)),
        "registry": str(REGISTRY.relative_to(ROOT)),
        "status": "PASS" if failures.empty else "FAIL",
    }
    (OUT / "manuscript_numeric_reconciliation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print(report.to_string(index=False))
    print("\n", json.dumps(summary, indent=2))
    if not failures.empty:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
