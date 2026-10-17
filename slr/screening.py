"""Steps 15-16: title/abstract screening and full-text eligibility.

The pipeline (re)generates the screening sheets and never overwrites reviewer input:
reviewer columns are carried over by record_id, and rows that disappear (e.g. after a
manual duplicate merge) are written to an *_orphans.csv file instead of being dropped.
"""

from __future__ import annotations

import random

import pandas as pd

from . import config
from .project import Project, merge_reviewer_columns, read_csv, short_hash, write_csv

TA_REVIEWER_COLS = ["r1_decision", "r1_confidence", "r1_note", "r2_decision", "r2_confidence",
                    "r2_note", "override_decision", "override_note"]
FT_REVIEWER_COLS = ["retrieved", "retrieval_note", "r1_decision", "r1_reason", "r2_decision",
                    "r2_reason", "consensus_decision", "consensus_reason", "notes"]


# ------------------------------------------------------------------ agreement

def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    pairs = [(x, y) for x, y in zip(a, b) if x and y]
    n = len(pairs)
    if n == 0:
        return None
    cats = sorted({x for p in pairs for x in p})
    po = sum(x == y for x, y in pairs) / n
    pe = sum((sum(x == c for x, _ in pairs) / n) * (sum(y == c for _, y in pairs) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def weighted_kappa(a: list[int], b: list[int], k: int = 3) -> float | None:
    """Linear-weighted kappa for ordinal QA scores 0..k-1."""
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    n = len(pairs)
    if n == 0:
        return None
    w = lambda i, j: 1 - abs(i - j) / (k - 1)
    po = sum(w(x, y) for x, y in pairs) / n
    pa = [sum(x == i for x, _ in pairs) / n for i in range(k)]
    pb = [sum(y == i for _, y in pairs) / n for i in range(k)]
    pe = sum(w(i, j) * pa[i] * pb[j] for i in range(k) for j in range(k))
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


# ------------------------------------------------------------------ title / abstract

def _norm_ta(value: str) -> str:
    v = (value or "").strip().lower()
    v = config.TA_DECISION_ALIASES.get(v, v)
    return v if v in config.TA_DECISIONS else ""


def relevance_score(title: str, abstract: str, keywords: str) -> int:
    """Sorting aid only. Never used to include or exclude a record."""
    t, rest = title.lower(), f"{abstract} {keywords}".lower()
    score = 0
    for terms, w in ((config.RELEVANCE_TERMS_A, 1), (config.RELEVANCE_TERMS_B, 1)):
        score += sum(2 * w for term in terms if term in t) + sum(w for term in terms if term in rest)
    score -= sum(3 for term in config.RELEVANCE_NEGATIVE if term in t or term in rest)
    return score


def ta_final(row) -> str:
    """Conservative rule (Protocol §6): include/uncertain from either reviewer -> full text."""
    override = _norm_ta(row.get("override_decision", ""))
    if override:
        return override
    d1, d2 = _norm_ta(row.get("r1_decision", "")), _norm_ta(row.get("r2_decision", ""))
    assigned = row.get("assigned_to", "")
    if assigned == "R1+R2":
        if not d1 or not d2:
            return "pending"
    decisions = [d for d in (d1, d2) if d]
    if not decisions:
        return "pending"
    if any(d in ("include", "uncertain") for d in decisions):
        return "include" if "include" in decisions else "uncertain"
    low_conf = any((row.get(f"{r}_confidence", "") or "").strip().lower() == "low" for r in ("r1", "r2"))
    if low_conf and len(decisions) < 2:
        return "pending (low-confidence exclusion needs 2nd reviewer)"
    return "exclude"


def build_ta_sheet(project: Project) -> dict:
    master = read_csv(project.master_records)
    if master.empty:
        raise SystemExit("No master records - run `python -m slr dedup` first.")
    pool = master[master["eligible_for_screening"] == "Y"].copy()
    pool["relevance_score"] = [relevance_score(t, a, k) for t, a, k in
                               zip(pool["title"], pool["abstract"], pool["keywords"])]

    old = read_csv(project.ta_sheet)
    if not old.empty and "assigned_to" in old.columns:
        prev_assign = dict(zip(old["record_id"], old["assigned_to"]))
    else:
        prev_assign = {}
    new_ids = [r for r in pool["record_id"] if r not in prev_assign]
    rng = random.Random(config.RANDOM_SEED)
    n_cal_target = max(config.CALIBRATION_MIN, round(config.CALIBRATION_FRACTION * len(pool)))
    n_cal_have = sum(v == "R1+R2" for v in prev_assign.values())
    n_cal_new = min(len(new_ids), max(0, n_cal_target - n_cal_have)) if not prev_assign else 0
    calib = set(rng.sample(sorted(new_ids), n_cal_new)) if n_cal_new else set()
    assign = {}
    for rid in pool["record_id"]:
        if rid in prev_assign:
            assign[rid] = prev_assign[rid]
        elif rid in calib:
            assign[rid] = "R1+R2"
        else:  # deterministic, balanced split
            assign[rid] = "R1" if int(short_hash(rid), 16) % 2 == 0 else "R2"
    pool["assigned_to"] = pool["record_id"].map(assign)
    pool["calibration_sample"] = (pool["assigned_to"] == "R1+R2").map({True: "Y", False: "N"})

    cols = ["record_id", "relevance_score", "assigned_to", "calibration_sample", "title", "authors",
            "year", "venue", "doc_type", "doi", "sources", "abstract", "keywords"]
    sheet = pool[cols].sort_values(["calibration_sample", "relevance_score", "record_id"],
                                   ascending=[False, False, True])
    sheet, orphans = merge_reviewer_columns(sheet, old, "record_id", TA_REVIEWER_COLS)
    sheet["final_decision"] = sheet.apply(ta_final, axis=1)
    write_csv(sheet, project.ta_sheet)
    if not orphans.empty:
        write_csv(orphans, project.path("data", "screening", "title_abstract_orphans.csv"))
    return ta_stats(sheet)


def ta_stats(sheet: pd.DataFrame | None = None, project: Project | None = None) -> dict:
    if sheet is None:
        sheet = read_csv(project.ta_sheet)
    cal = sheet[sheet["assigned_to"] == "R1+R2"]
    d1 = [_norm_ta(x) for x in cal["r1_decision"]]
    d2 = [_norm_ta(x) for x in cal["r2_decision"]]
    binary = lambda xs: ["exclude" if x == "exclude" else ("pass" if x else "") for x in xs]
    final = sheet["final_decision"].value_counts().to_dict()
    return {
        "records": len(sheet),
        "calibration_records": len(cal),
        "calibration_double_screened": sum(1 for x, y in zip(d1, d2) if x and y),
        "kappa_3class": cohen_kappa(d1, d2),
        "kappa_binary": cohen_kappa(binary(d1), binary(d2)),
        "kappa_target": config.KAPPA_TARGET,
        "final_decisions": final,
    }


# ------------------------------------------------------------------ full text

def _norm_ft(value: str) -> str:
    v = (value or "").strip().lower()
    v = {"i": "include", "e": "exclude"}.get(v, v)
    return v if v in config.FT_DECISIONS else ""


def _norm_reason(value: str) -> str:
    v = (value or "").strip().upper()
    return v if v in config.EXCLUSION_REASONS else ""


def ft_final(row) -> tuple[str, str, str]:
    """Returns (final_decision, final_reason, problem)."""
    if (row.get("retrieved", "") or "").strip().upper() == "N":
        return "not_retrieved", "", ""
    if (row.get("retrieved", "") or "").strip().upper() != "Y":
        return "pending", "", ""
    cd = _norm_ft(row.get("consensus_decision", ""))
    if cd:
        reason = _norm_reason(row.get("consensus_reason", ""))
        if cd == "exclude" and not reason:
            return "pending", "", "consensus exclusion without a valid reason code (E1-E10)"
        return cd, reason if cd == "exclude" else "", ""
    d1, d2 = _norm_ft(row.get("r1_decision", "")), _norm_ft(row.get("r2_decision", ""))
    if not d1 or not d2:
        return "pending", "", ""
    r1, r2 = _norm_reason(row.get("r1_reason", "")), _norm_reason(row.get("r2_reason", ""))
    for d, r, who in ((d1, r1, "R1"), (d2, r2, "R2")):
        if d == "exclude" and not r:
            return "pending", "", f"{who} exclusion without a valid reason code (E1-E10)"
    if d1 != d2:
        return "conflict", "", "reviewers disagree - fill consensus_decision"
    if d1 == "exclude" and r1 != r2:
        # same decision, different reason: hierarchy (E1 first) decides, recorded transparently
        order = list(config.EXCLUSION_REASONS)
        return "exclude", min(r1, r2, key=order.index), ""
    return d1, r1 if d1 == "exclude" else "", ""


def build_ft_sheet(project: Project) -> dict:
    ta = read_csv(project.ta_sheet)
    if ta.empty:
        raise SystemExit("No title/abstract sheet - run `python -m slr screen-ta` first.")
    ta["final_decision"] = ta.apply(ta_final, axis=1)
    sought = ta[ta["final_decision"].isin(["include", "uncertain"])]
    master = read_csv(project.master_records).set_index("record_id")
    sheet = sought[["record_id", "title", "authors", "year", "venue", "doi"]].copy()
    sheet["origin"] = sheet["record_id"].map(master["origin"])
    sheet["url"] = sheet["record_id"].map(master["url"])
    sheet["ta_decision"] = sought["final_decision"].values
    old = read_csv(project.ft_sheet)
    sheet, orphans = merge_reviewer_columns(sheet, old, "record_id", FT_REVIEWER_COLS)
    results = sheet.apply(ft_final, axis=1, result_type="expand")
    sheet["final_decision"], sheet["final_reason"], sheet["problem"] = results[0], results[1], results[2]
    write_csv(sheet, project.ft_sheet)
    if not orphans.empty:
        write_csv(orphans, project.path("data", "screening", "full_text_orphans.csv"))
    _update_included(project, sheet)

    assessed = sheet[sheet["retrieved"].str.upper() == "Y"]
    d1 = [_norm_ft(x) for x in assessed["r1_decision"]]
    d2 = [_norm_ft(x) for x in assessed["r2_decision"]]
    return {
        "reports_sought": len(sheet),
        "final_decisions": sheet["final_decision"].value_counts().to_dict(),
        "exclusion_reasons": sheet.loc[sheet["final_decision"] == "exclude", "final_reason"].value_counts().to_dict(),
        "kappa_full_text": cohen_kappa(d1, d2),
        "problems": sheet.loc[sheet["problem"] != "", ["record_id", "problem"]].values.tolist(),
    }


def _update_included(project: Project, ft: pd.DataFrame) -> None:
    """Stable paper IDs P001, P002, ... in order of inclusion; never renumbered."""
    old = read_csv(project.included)
    ids = dict(zip(old["record_id"], old["paper_id"])) if not old.empty else {}
    inc = ft[ft["final_decision"] == "include"].copy()
    next_n = max([int(p[1:]) for p in ids.values()] or [0]) + 1
    for rid in inc.sort_values(["year", "record_id"])["record_id"]:
        if rid not in ids:
            ids[rid] = f"P{next_n:03d}"
            next_n += 1
    inc["paper_id"] = inc["record_id"].map(ids)
    master = read_csv(project.master_records).set_index("record_id")
    inc["sources"] = inc["record_id"].map(master["sources"])
    inc["doc_type"] = inc["record_id"].map(master["doc_type"])
    inc["affiliations"] = inc["record_id"].map(master["affiliations"])
    inc["keywords"] = inc["record_id"].map(master["keywords"])
    cols = ["paper_id", "record_id", "title", "authors", "year", "venue", "doc_type", "doi",
            "origin", "sources", "affiliations", "keywords"]
    write_csv(inc[cols].sort_values("paper_id"), project.included)
    dropped = old[~old["record_id"].isin(inc["record_id"])] if not old.empty else old
    if not dropped.empty:
        write_csv(dropped, project.path("data", "screening", "included_studies_withdrawn.csv"))
