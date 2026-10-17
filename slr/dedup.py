"""Step 14: deduplicate records across databases and waves.

Automatic merges (safe):
  1. identical normalised DOI;
  2. identical normalised title + |year difference| <= 1 + same first-author surname,
     provided the merged group would not contain two different DOIs
     (a conference paper and its journal extension often share a title but are different reports).
Fuzzy title matches (similarity >= FUZZY_TITLE_THRESHOLD) are never merged automatically:
they are written to dedup_candidates.csv and merged only when a reviewer sets is_duplicate = Y.
Protocol filters (year, document type, language) are then applied to the unique records and
counted as "records removed for other reasons" in PRISMA.
"""

from __future__ import annotations

from difflib import SequenceMatcher

import pandas as pd

from . import config
from .project import (Project, first_author_surname, normalize_title, read_csv, short_hash,
                      to_int, write_csv)

MERGE_FIELDS = ["title", "authors", "year", "venue", "doi", "abstract", "keywords",
                "doc_type", "language", "affiliations", "url"]


class _UnionFind:
    def __init__(self, items, dois):
        self.parent = {i: i for i in items}
        self.dois = {i: ({dois[i]} if dois[i] else set()) for i in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b, force=False) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if not force and len(self.dois[ra] | self.dois[rb]) > 1:
            return False
        self.parent[rb] = ra
        self.dois[ra] |= self.dois.pop(rb)
        return True


def _pair_id(a: str, b: str) -> str:
    return "D" + short_hash("|".join(sorted([a, b])))


def _fuzzy_pairs(raw: pd.DataFrame, uf: _UnionFind) -> list[dict]:
    reps = {}
    for _, r in raw.iterrows():
        reps.setdefault(uf.find(r["raw_id"]), r)
    by_year: dict[int, list] = {}
    for root, r in reps.items():
        y = to_int(r["year"])
        if y is not None:
            by_year.setdefault(y, []).append((root, r, set(r["_nt"].split())))

    def candidates():
        for y, items in by_year.items():
            nxt = by_year.get(y + 1, [])
            for i, a in enumerate(items):
                for b in items[i + 1:] + nxt:
                    yield a, b

    pairs = []
    for (ra, a, ta), (rb, b, tb) in candidates():
        if ra == rb or not ta or not tb:
            continue
        if len(ta & tb) / len(ta | tb) < 0.6:
            continue
        sim = SequenceMatcher(None, a["_nt"], b["_nt"]).ratio()
        if sim >= config.FUZZY_TITLE_THRESHOLD:
            pairs.append({
                "pair_id": _pair_id(a["raw_id"], b["raw_id"]),
                "raw_id_a": a["raw_id"], "raw_id_b": b["raw_id"],
                "similarity": f"{sim:.3f}",
                "title_a": a["title"], "title_b": b["title"],
                "year_a": a["year"], "year_b": b["year"],
                "doi_a": a["doi"], "doi_b": b["doi"],
                "authors_a": a["authors"][:120], "authors_b": b["authors"][:120],
                "venue_a": a["venue"], "venue_b": b["venue"],
            })
    return pairs


def _protocol_filter(rec: dict) -> str:
    y = to_int(rec["year"])
    if y is None or y < config.YEAR_MIN or y > config.YEAR_MAX:
        return "Outside date range (protocol filter)"
    if rec["doc_type"] not in config.ALLOWED_DOC_TYPES:
        return "Document type not eligible (protocol filter)"
    if rec["language"] and rec["language"].strip().lower() not in config.ALLOWED_LANGUAGES:
        return "Not in English (protocol filter)"
    return ""


def deduplicate(project: Project) -> dict:
    raw = read_csv(project.raw_records)
    if raw.empty:
        raise SystemExit("No raw records - run `python -m slr ingest` first.")
    raw["_nt"] = raw["title"].map(normalize_title)
    raw["_sn"] = raw["authors"].map(first_author_surname)
    raw["_prio"] = raw["source"].map(config.SOURCE_PRIORITY).fillna(9)
    raw = raw.sort_values(["_prio", "raw_file", "raw_id"]).reset_index(drop=True)

    uf = _UnionFind(raw["raw_id"], dict(zip(raw["raw_id"], raw["doi"])))
    rule = {rid: "unique" for rid in raw["raw_id"]}

    for doi, grp in raw[raw["doi"] != ""].groupby("doi"):
        ids = list(grp["raw_id"])
        for other in ids[1:]:
            if uf.union(ids[0], other):
                rule[other] = "doi"

    for nt, grp in raw[raw["_nt"].str.len() >= 15].groupby("_nt"):
        rows = grp.to_dict("records")
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                ya, yb = to_int(a["year"]), to_int(b["year"])
                if ya is not None and yb is not None and abs(ya - yb) > 1:
                    continue
                if a["_sn"] and b["_sn"] and a["_sn"] != b["_sn"]:
                    continue
                if uf.union(a["raw_id"], b["raw_id"]):
                    rule[b["raw_id"]] = "exact_title"

    # manual decisions on fuzzy candidates
    old = read_csv(project.dedup_candidates)
    decided = {}
    if not old.empty and "is_duplicate" in old.columns:
        decided = dict(zip(old["pair_id"], old["is_duplicate"].str.strip().str.upper()))
    for pid, dec in decided.items():
        if dec == "Y":
            row = old[old["pair_id"] == pid].iloc[0]
            if row["raw_id_a"] in uf.parent and row["raw_id_b"] in uf.parent:
                if uf.union(row["raw_id_a"], row["raw_id_b"], force=True):
                    rule[row["raw_id_b"]] = "manual_fuzzy"

    pairs = _fuzzy_pairs(raw, uf)
    cand = pd.DataFrame(pairs, columns=["pair_id", "raw_id_a", "raw_id_b", "similarity", "title_a",
                                        "title_b", "year_a", "year_b", "doi_a", "doi_b", "authors_a",
                                        "authors_b", "venue_a", "venue_b"])
    # keep pairs that were already decided (even once merged) so the decision stays visible
    if not old.empty:
        kept = old[old["pair_id"].isin(decided) & ~old["pair_id"].isin(cand["pair_id"])]
        cand = pd.concat([cand, kept.drop(columns=["is_duplicate"], errors="ignore")], ignore_index=True)
    cand["is_duplicate"] = cand["pair_id"].map(decided).fillna("")
    write_csv(cand, project.dedup_candidates)

    raw["cluster"] = raw["raw_id"].map(uf.find)
    masters, log_rows = [], []
    for root, grp in raw.groupby("cluster", sort=False):
        grp = grp.sort_values("_prio")
        best = grp.iloc[0].to_dict()
        rec = {f: best[f] for f in MERGE_FIELDS}
        for f in MERGE_FIELDS:
            if not rec[f]:
                vals = [v for v in grp[f] if v]
                rec[f] = vals[0] if vals else ""
        dois = sorted(d for d in grp["doi"] if d)
        key = dois[0] if dois else normalize_title(best["title"]) + "|" + best["year"]
        rec["record_id"] = "R" + short_hash(key)
        sources = sorted(set(grp["source"]), key=lambda s: config.SOURCE_PRIORITY.get(s, 9))
        rec["sources"] = "; ".join(sources)
        rec["origin"] = "database" if any(s in config.DATABASE_SOURCES for s in sources) else "other"
        rec["first_wave"] = str(min(to_int(w, 1) for w in grp["wave"]))
        rec["n_raw_records"] = str(len(grp))
        rec["raw_ids"] = "; ".join(grp["raw_id"])
        rec["removed_reason"] = _protocol_filter(rec)
        rec["eligible_for_screening"] = "N" if rec["removed_reason"] else "Y"
        masters.append(rec)
        for i, r in enumerate(grp.itertuples()):
            log_rows.append({"raw_id": r.raw_id, "source": r.source, "wave": r.wave,
                             "record_id": rec["record_id"],
                             "status": "kept" if i == 0 else "duplicate_removed",
                             "merge_rule": "" if i == 0 else rule.get(r.raw_id, "doi/title chain")})

    master = pd.DataFrame(masters)
    cols = ["record_id", "title", "authors", "year", "venue", "doi", "doc_type", "language",
            "sources", "origin", "first_wave", "n_raw_records", "eligible_for_screening",
            "removed_reason", "abstract", "keywords", "affiliations", "url", "raw_ids"]
    master = master[cols].sort_values("record_id").reset_index(drop=True)
    if master["record_id"].duplicated().any():  # vanishingly rare hash/key collision
        n = master.groupby("record_id").cumcount()
        master.loc[n > 0, "record_id"] += "-" + n[n > 0].astype(str)
    write_csv(master, project.master_records)
    write_csv(pd.DataFrame(log_rows), project.dedup_log)

    return {
        "raw": len(raw),
        "unique": len(master),
        "duplicates_removed": len(raw) - len(master),
        "pending_fuzzy_pairs": int((cand["is_duplicate"] == "").sum()),
        "removed_protocol_filter": int((master["eligible_for_screening"] == "N").sum()),
        "eligible_for_screening": int((master["eligible_for_screening"] == "Y").sum()),
    }
