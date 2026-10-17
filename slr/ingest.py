"""Step 13/14 input: parse database exports into one raw-records table.

Supported exports (Document 09):
  data/raw/scopus/*.csv          Scopus CSV export
  data/raw/wos/*.txt             Web of Science tab-delimited or plain-text (tagged) export
  data/raw/ieee/*.csv            IEEE Xplore CSV export
  data/raw/other/*.csv | *.ris   Unified CSV (Document 12) or RIS, for citation chaining etc.
Files whose name starts with "pilot_" are ignored (pilot exports are not evidence).
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path

import pandas as pd

from .project import Project, normalize_doi, normalize_title, read_csv, short_hash, to_int, write_csv

RAW_COLUMNS = [
    "raw_id", "source", "wave", "raw_file", "native_id", "title", "authors", "year", "venue",
    "doi", "abstract", "keywords", "doc_type", "doc_type_raw", "language", "affiliations", "url",
]


def _decode(path: Path) -> str:
    data = path.read_bytes()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16")
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _wave_from_name(name: str) -> int:
    m = re.search(r"wave[_-]?(\d+)", name, re.I)
    return int(m.group(1)) if m else 1


def _col(df: pd.DataFrame, *names: str) -> pd.Series:
    for n in names:
        if n in df.columns:
            return df[n].fillna("").astype(str).str.strip()
    return pd.Series([""] * len(df), index=df.index)


# ------------------------------------------------------------------ Scopus

def _scopus_doc_type(raw: str) -> str:
    r = raw.lower()
    if r == "article" or r == "article in press":
        return "article"
    if r == "conference paper":
        return "conference_paper"
    if r == "review":
        return "review"
    if r == "book chapter":
        return "book_chapter"
    return "other"


def parse_scopus(path: Path) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(_decode(path)), dtype=str, keep_default_na=False)
    out = pd.DataFrame({
        "native_id": _col(df, "EID"),
        "title": _col(df, "Title"),
        "authors": _col(df, "Authors", "Author full names"),
        "year": _col(df, "Year"),
        "venue": _col(df, "Source title"),
        "doi": _col(df, "DOI"),
        "abstract": _col(df, "Abstract"),
        "keywords": (_col(df, "Author Keywords") + "; " + _col(df, "Index Keywords")).str.strip("; "),
        "doc_type_raw": _col(df, "Document Type"),
        "language": _col(df, "Language of Original Document"),
        "affiliations": _col(df, "Affiliations"),
        "url": _col(df, "Link"),
    })
    out["doc_type"] = out["doc_type_raw"].map(_scopus_doc_type)
    out.loc[out["abstract"].str.contains(r"^\[no abstract available\]$", case=False), "abstract"] = ""
    return out


# ------------------------------------------------------------------ Web of Science

WOS_FIELDS = {
    "TI": "title", "AU": "authors", "PY": "year", "SO": "venue", "DI": "doi", "AB": "abstract",
    "DE": "keywords_de", "ID": "keywords_id", "DT": "doc_type_raw", "LA": "language",
    "UT": "native_id", "EA": "early_access", "C1": "affiliations",
}


def _wos_doc_type(raw: str) -> str:
    r = raw.lower()
    if "review" in r:
        return "review"
    if "article" in r:
        return "article"
    if "proceedings paper" in r:
        return "conference_paper"
    if "book chapter" in r:
        return "book_chapter"
    return "other"


def _parse_wos_tagged(text: str) -> pd.DataFrame:
    rows, rec, tag = [], {}, None
    for line in text.splitlines():
        if line.startswith("ER"):
            rows.append(rec)
            rec, tag = {}, None
            continue
        if len(line) >= 2 and line[:2].strip() and (len(line) == 2 or line[2] == " "):
            tag = line[:2]
            value = line[3:].strip()
            rec[tag] = value if tag not in rec else rec[tag] + "; " + value
        elif tag and line.startswith("   "):
            sep = "; " if tag in ("AU", "AF", "C1", "CR") else " "
            rec[tag] = rec.get(tag, "") + sep + line.strip()
    return pd.DataFrame(rows)


def parse_wos(path: Path) -> pd.DataFrame:
    text = _decode(path)
    if text.lstrip().startswith("FN "):
        df = _parse_wos_tagged(text).fillna("")
    else:
        df = pd.read_csv(io.StringIO(text), sep="\t", dtype=str, keep_default_na=False,
                         quoting=csv.QUOTE_NONE, index_col=False)
    df = df.rename(columns=lambda c: c.strip())
    out = pd.DataFrame({dst: _col(df, src) for src, dst in WOS_FIELDS.items()})
    year_from_ea = out["early_access"].str.extract(r"(\d{4})")[0].fillna("")
    out["year"] = out["year"].where(out["year"] != "", year_from_ea)
    out["keywords"] = (out["keywords_de"] + "; " + out["keywords_id"]).str.strip("; ")
    out["doc_type"] = out["doc_type_raw"].map(_wos_doc_type)
    out["url"] = ""
    return out.drop(columns=["keywords_de", "keywords_id", "early_access"])


# ------------------------------------------------------------------ IEEE Xplore

def _ieee_doc_type(raw: str) -> str:
    r = raw.lower()
    if "conference" in r:
        return "conference_paper"
    if "journal" in r or "early access" in r or "magazine" in r:
        return "article"
    return "other"


def parse_ieee(path: Path) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(_decode(path)), dtype=str, keep_default_na=False)
    pdf = _col(df, "PDF Link")
    out = pd.DataFrame({
        "native_id": pdf.str.extract(r"arnumber=(\d+)")[0].fillna(""),
        "title": _col(df, "Document Title"),
        "authors": _col(df, "Authors"),
        "year": _col(df, "Publication Year", "Publication_Year"),
        "venue": _col(df, "Publication Title"),
        "doi": _col(df, "DOI"),
        "abstract": _col(df, "Abstract"),
        "keywords": (_col(df, "Author Keywords") + "; " + _col(df, "IEEE Terms")).str.strip("; "),
        "doc_type_raw": _col(df, "Document Identifier"),
        "language": "English",
        "affiliations": _col(df, "Author Affiliations"),
        "url": pdf,
    })
    out["doc_type"] = out["doc_type_raw"].map(_ieee_doc_type)
    return out


# ------------------------------------------------------------------ Other (unified CSV / RIS)

RIS_TYPES = {"JOUR": "article", "JFULL": "article", "EJOUR": "article",
             "CONF": "conference_paper", "CPAPER": "conference_paper",
             "CHAP": "book_chapter", "BOOK": "other", "THES": "other", "RPRT": "other"}


def parse_ris(path: Path) -> pd.DataFrame:
    rows, rec = [], {}
    for line in _decode(path).splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line)
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "ER":
            rows.append(rec)
            rec = {}
            continue
        if tag in ("AU", "A1", "KW"):
            rec.setdefault(tag[:1] + "_list", []).append(val)
        else:
            rec.setdefault(tag, val)
    out = []
    for r in rows:
        ty = r.get("TY", "")
        out.append({
            "native_id": r.get("ID", ""),
            "title": r.get("TI", r.get("T1", "")),
            "authors": "; ".join(r.get("A_list", [])),
            "year": (re.findall(r"\d{4}", r.get("PY", r.get("Y1", ""))) or [""])[0],
            "venue": r.get("T2", r.get("JO", r.get("JF", ""))),
            "doi": r.get("DO", ""),
            "abstract": r.get("AB", ""),
            "keywords": "; ".join(r.get("K_list", [])),
            "doc_type_raw": ty,
            "doc_type": RIS_TYPES.get(ty, "other"),
            "language": r.get("LA", "English"),
            "affiliations": r.get("AD", ""),
            "url": r.get("UR", ""),
        })
    return pd.DataFrame(out)


def parse_other_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(_decode(path)), dtype=str, keep_default_na=False)
    out = pd.DataFrame({c: _col(df, c) for c in
                        ["title", "authors", "year", "venue", "doi", "abstract", "keywords",
                         "language", "url"]})
    out["native_id"] = ""
    out["doc_type_raw"] = _col(df, "doc_type")
    out["doc_type"] = out["doc_type_raw"].str.lower().replace({"journal": "article", "conference": "conference_paper"})
    out["affiliations"] = ""
    out.loc[out["language"] == "", "language"] = "English"
    return out


PARSERS = {
    "scopus": {".csv": parse_scopus},
    "wos": {".txt": parse_wos, ".tsv": parse_wos},
    "ieee": {".csv": parse_ieee},
    "other": {".csv": parse_other_csv, ".ris": parse_ris},
}


def find_exports(project: Project) -> list[tuple[str, Path]]:
    found = []
    for source, by_ext in PARSERS.items():
        folder = project.raw_dir / source
        if not folder.exists():
            continue
        for f in sorted(folder.iterdir()):
            if f.is_file() and f.suffix.lower() in by_ext and not f.name.lower().startswith("pilot_"):
                found.append((source, f))
    return found


def parse_file(source: str, path: Path) -> pd.DataFrame:
    df = PARSERS[source][path.suffix.lower()](path)
    df["source"] = source
    df["wave"] = str(_wave_from_name(path.name))
    df["raw_file"] = path.name
    df["doi"] = df["doi"].map(normalize_doi)
    df["year"] = df["year"].map(lambda y: str(to_int(y, "")) if to_int(y) else "")
    df = df[df["title"].str.strip() != ""].copy()
    return df


def assign_raw_ids(df: pd.DataFrame) -> pd.DataFrame:
    keys = []
    for _, r in df.iterrows():
        base = r["native_id"] or r["doi"] or (normalize_title(r["title"]) + r["year"])
        keys.append(f"{r['source']}-{short_hash(base)}")
    df["raw_id"] = keys
    # identical records exported twice by the same database get a suffix, they stay countable
    dup_n = df.groupby("raw_id").cumcount()
    df.loc[dup_n > 0, "raw_id"] = df.loc[dup_n > 0, "raw_id"] + "-" + dup_n[dup_n > 0].astype(str)
    return df


def check_search_log(project: Project, raw: pd.DataFrame) -> list[str]:
    """Compare parsed record counts with records_retrieved in the PRISMA-S search log."""
    log = read_csv(project.search_log)
    msgs = []
    if log.empty or "export_file" not in log.columns:
        return ["search_log.csv missing or empty - record every executed search (PRISMA-S)."]
    for _, row in log.iterrows():
        files = [Path(f.strip()).name for f in str(row.get("export_file", "")).split(";") if f.strip()]
        expected = to_int(row.get("records_retrieved"))
        if not files or expected is None:
            continue
        got = int(raw["raw_file"].isin(files).sum())
        if got != expected:
            msgs.append(f"{row.get('search_id')}: search log says {expected} records, "
                        f"exports contain {got} - check export completeness.")
    return msgs


def ingest(project: Project) -> pd.DataFrame:
    frames = [parse_file(src, f) for src, f in find_exports(project)]
    raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=RAW_COLUMNS)
    raw = assign_raw_ids(raw) if not raw.empty else raw
    raw = raw.reindex(columns=RAW_COLUMNS).fillna("")
    write_csv(raw, project.raw_records)
    return raw
