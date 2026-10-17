"""Step 10: pilot the search - recall against the known-relevant set and a precision sample."""

from __future__ import annotations

import random
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

from . import config
from .ingest import PARSERS, parse_file
from .project import Project, normalize_doi, normalize_title, read_csv, write_csv


def load_pilot_exports(project: Project) -> pd.DataFrame:
    frames = []
    for source, by_ext in PARSERS.items():
        folder = project.raw_dir / source
        if not folder.exists():
            continue
        for f in sorted(folder.iterdir()):
            if f.name.lower().startswith("pilot_") and f.suffix.lower() in by_ext:
                frames.append(parse_file(source, f))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _matches(gold_title: str, gold_doi: str, recs: pd.DataFrame) -> bool:
    if gold_doi and (recs["doi"] == gold_doi).any():
        return True
    nt = normalize_title(gold_title)
    if (recs["_nt"] == nt).any():
        return True
    return any(SequenceMatcher(None, nt, t).ratio() >= config.FUZZY_TITLE_THRESHOLD
               for t in recs["_nt"] if abs(len(t) - len(nt)) < 25)


def run(project: Project, precision_sample: int = 100) -> dict:
    gold = read_csv(project.protocol_dir / "known_relevant_papers.csv")
    recs = load_pilot_exports(project)
    if recs.empty:
        raise SystemExit("No pilot exports found (data/raw/<db>/pilot_*.csv|txt).")
    recs["_nt"] = recs["title"].map(normalize_title)
    rows = []
    for _, g in gold.iterrows():
        doi = normalize_doi(g.get("doi", ""))
        row = {"gold_id": g["gold_id"], "title": g["title"], "year": g["year"]}
        for src in config.DATABASE_SOURCES:
            sub = recs[recs["source"] == src]
            row[f"found_{src}"] = "Y" if not sub.empty and _matches(g["title"], doi, sub) else "N"
        row["found_any"] = "Y" if any(row[f"found_{s}"] == "Y" for s in config.DATABASE_SOURCES) else "N"
        row["miss_reason"] = ""
        rows.append(row)
    res = pd.DataFrame(rows)
    out = project.outputs_dir / "pilot"
    out.mkdir(parents=True, exist_ok=True)
    write_csv(res, out / "pilot_recall.csv")

    uniq = recs.drop_duplicates("_nt")
    rng = random.Random(config.RANDOM_SEED)
    idx = rng.sample(list(uniq.index), min(precision_sample, len(uniq)))
    sample = uniq.loc[idx, ["source", "title", "year", "venue"]].assign(plausibly_relevant="")
    write_csv(sample, out / "precision_sample.csv")

    summary = {"gold": len(res), "retrieved_any": int((res["found_any"] == "Y").sum()),
               "recall_any": round((res["found_any"] == "Y").mean(), 3) if len(res) else None,
               "records_in_pilot": len(recs), "unique_titles": len(uniq)}
    for s in config.DATABASE_SOURCES:
        summary[f"recall_{s}"] = round((res[f"found_{s}"] == "Y").mean(), 3) if len(res) else None
    return summary
