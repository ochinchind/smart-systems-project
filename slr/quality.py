"""Step 18: quality assessment of included studies (QA1-QA5, 0/1/2, max 10)."""

from __future__ import annotations

import pandas as pd

from . import config
from .project import Project, merge_reviewer_columns, read_csv, to_int, write_csv
from .screening import weighted_kappa

ITEMS = list(config.QA_ITEMS)
REVIEWER_COLS = ([f"r1_{q}" for q in ITEMS] + [f"r2_{q}" for q in ITEMS]
                 + [f"consensus_{q}" for q in ITEMS] + ["qa_notes"])


def _score(v):
    s = to_int(v)
    return s if s in config.QA_SCORES else None


def qa_class(total: int | None) -> str:
    if total is None:
        return ""
    for lo, hi, label in config.QA_CLASSES:
        if lo <= total <= hi:
            return label
    return ""


def resolve(row) -> dict:
    out, conflicts = {}, []
    for q in ITEMS:
        c = _score(row.get(f"consensus_{q}"))
        a, b = _score(row.get(f"r1_{q}")), _score(row.get(f"r2_{q}"))
        if c is not None:
            out[q] = c
        elif a is not None and b is not None and a == b:
            out[q] = a
        else:
            out[q] = None
            if a is not None and b is not None:
                conflicts.append(q)
    complete = all(v is not None for v in out.values())
    total = sum(out.values()) if complete else None
    return {**{f"final_{q}": ("" if v is None else str(v)) for q, v in out.items()},
            "qa_total": "" if total is None else str(total),
            "qa_class": qa_class(total),
            "qa_conflicts": ";".join(conflicts)}


def build_qa_sheet(project: Project) -> dict:
    inc = read_csv(project.included)
    if inc.empty:
        raise SystemExit("No included studies yet - finish full-text screening first.")
    sheet = inc[["paper_id", "title", "year", "venue"]].copy()
    old = read_csv(project.qa_sheet)
    sheet, orphans = merge_reviewer_columns(sheet, old, "paper_id", REVIEWER_COLS)
    res = sheet.apply(resolve, axis=1, result_type="expand")
    for c in res.columns:
        sheet[c] = res[c]
    write_csv(sheet, project.qa_sheet)
    if not orphans.empty:
        write_csv(orphans, project.path("data", "quality", "quality_assessment_orphans.csv"))
    kappas = {q: weighted_kappa([_score(x) for x in sheet[f"r1_{q}"]],
                                [_score(x) for x in sheet[f"r2_{q}"]]) for q in ITEMS}
    return {
        "studies": len(sheet),
        "complete": int((sheet["qa_total"] != "").sum()),
        "classes": sheet.loc[sheet["qa_class"] != "", "qa_class"].value_counts().to_dict(),
        "conflicts": sheet.loc[sheet["qa_conflicts"] != "", ["paper_id", "qa_conflicts"]].values.tolist(),
        "weighted_kappa": kappas,
    }


def load_final_qa(project: Project) -> pd.DataFrame:
    qa = read_csv(project.qa_sheet)
    if qa.empty:
        return pd.DataFrame(columns=["paper_id", "qa_total", "qa_class"])
    return qa
