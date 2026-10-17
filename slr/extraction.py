"""Steps 19-21: technical and quantitative extraction sheets + traceable evidence register."""

from __future__ import annotations

import re

import pandas as pd

from . import config
from .codebook import QUANTITATIVE, TECHNICAL, codebook_frame, validate
from .project import Project, read_csv, to_float, to_int, write_csv

TECH_FIELDS = [f[0] for f in TECHNICAL]
QUANT_FIELDS = [f[0] for f in QUANTITATIVE]
PREFILLED = ["authors", "year", "title", "venue", "doi"]


def _guess_country(affiliations: str) -> str:
    first = re.split(r";", affiliations or "")[0]
    parts = [p.strip(" .") for p in first.split(",") if p.strip()]
    return parts[-1] if parts else ""


def build_technical_sheet(project: Project) -> list[str]:
    inc = read_csv(project.included)
    if inc.empty:
        raise SystemExit("No included studies yet.")
    old = read_csv(project.technical)
    old_idx = old.set_index("paper_id") if not old.empty else None
    rows = []
    for _, s in inc.iterrows():
        row = {f: "" for f in TECH_FIELDS}
        row.update({f: s[f] for f in PREFILLED})
        row["paper_id"] = s["paper_id"]
        row["venue_type"] = {"article": "journal", "conference_paper": "conference"}.get(s["doc_type"], "")
        row["country_first_author"] = _guess_country(s.get("affiliations", ""))
        if old_idx is not None and s["paper_id"] in old_idx.index:
            prev = old_idx.loc[s["paper_id"]]
            for f in TECH_FIELDS:
                if f in prev.index and str(prev[f]).strip():
                    row[f] = prev[f]
        if not row["study_family_id"]:
            row["study_family_id"] = s["paper_id"]
        rows.append(row)
    sheet = pd.DataFrame(rows, columns=TECH_FIELDS)
    write_csv(sheet, project.technical)
    write_csv(codebook_frame(), project.path("data", "protocol", "codebook.csv"))
    return validate(sheet, TECHNICAL)


def relative_improvement(metric: str, rl, base, reported) -> float | None:
    """Positive = RL better. Lower-is-better: (B - RL) / B; higher-is-better: (RL - B) / B."""
    rl, base, reported = to_float(rl), to_float(base), to_float(reported)
    direction = config.METRIC_DIRECTION.get(metric)
    if rl is not None and base not in (None, 0) and direction:
        ri = (base - rl) / abs(base) if direction == "lower" else (rl - base) / abs(base)
        return round(100 * ri, 3)
    return reported


def build_quantitative_sheet(project: Project) -> list[str]:
    q = read_csv(project.quantitative)
    tech = read_csv(project.technical)
    if q.empty:
        q = pd.DataFrame(columns=QUANT_FIELDS)
    for f in QUANT_FIELDS:
        if f not in q.columns:
            q[f] = ""
    # auto-number new entries
    used = [to_int(e[1:]) for e in q["entry_id"] if e.startswith("Q") and to_int(e[1:])]
    n = max(used or [0])
    for idx in q.index:
        if not q.at[idx, "entry_id"]:
            n += 1
            q.at[idx, "entry_id"] = f"Q{n:04d}"
    problems = validate(q[QUANT_FIELDS], QUANTITATIVE)
    if not tech.empty:
        t = tech.set_index("paper_id")
        known = set(t.index)
        for idx, r in q.iterrows():
            if r["paper_id"] and r["paper_id"] not in known:
                problems.append(f"{r['entry_id']}: paper_id {r['paper_id']} is not an included study")
        q["study_family_id"] = q["paper_id"].map(t["study_family_id"]).fillna("")
        q.loc[q["study_family_id"] == "", "study_family_id"] = q["paper_id"]
        paper_vrl = q["paper_id"].map(t["vrl"]).fillna("")
        q["vrl_effective"] = q["vrl"].where(q["vrl"] != "", paper_vrl)
    else:
        q["study_family_id"] = q["paper_id"]
        q["vrl_effective"] = q["vrl"]
    q["direction"] = q["metric"].map(config.METRIC_DIRECTION).fillna("")
    q["relative_improvement_pct"] = [
        "" if (v := relative_improvement(m, a, b, r)) is None else f"{v:g}"
        for m, a, b, r in zip(q["metric"], q["rl_value"], q["baseline_value"], q["reported_improvement_pct"])
    ]
    for idx, r in q.iterrows():
        if not r["source_location"] and (r["rl_value"] or r["reported_improvement_pct"]):
            problems.append(f"{r['entry_id']}: source_location missing (every number must be traceable)")
    computed = ["study_family_id", "vrl_effective", "direction", "relative_improvement_pct"]
    write_csv(q[QUANT_FIELDS + computed], project.quantitative)
    return problems
