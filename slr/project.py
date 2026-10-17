"""File layout of an SLR project and small shared helpers."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

import pandas as pd


class Project:
    """All paths are relative to the project root so tests can use a temp dir."""

    def __init__(self, root: str | Path = "."):
        self.root = Path(root).resolve()

    # inputs
    @property
    def raw_dir(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def protocol_dir(self) -> Path:
        return self.root / "data" / "protocol"

    # working files (pipeline-generated, reviewer-edited)
    @property
    def records_dir(self) -> Path:
        return self.root / "data" / "records"

    @property
    def screening_dir(self) -> Path:
        return self.root / "data" / "screening"

    @property
    def quality_dir(self) -> Path:
        return self.root / "data" / "quality"

    @property
    def extraction_dir(self) -> Path:
        return self.root / "data" / "extraction"

    @property
    def synthesis_input_dir(self) -> Path:
        return self.root / "data" / "synthesis"

    # outputs (fully regenerated)
    @property
    def outputs_dir(self) -> Path:
        return self.root / "outputs"

    def path(self, *parts: str) -> Path:
        p = self.root.joinpath(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    # named files
    raw_records = property(lambda self: self.path("data", "records", "raw_records.csv"))
    master_records = property(lambda self: self.path("data", "records", "master_records.csv"))
    dedup_log = property(lambda self: self.path("data", "records", "dedup_log.csv"))
    dedup_candidates = property(lambda self: self.path("data", "records", "dedup_candidates.csv"))
    ta_sheet = property(lambda self: self.path("data", "screening", "title_abstract.csv"))
    ft_sheet = property(lambda self: self.path("data", "screening", "full_text.csv"))
    included = property(lambda self: self.path("data", "screening", "included_studies.csv"))
    qa_sheet = property(lambda self: self.path("data", "quality", "quality_assessment.csv"))
    technical = property(lambda self: self.path("data", "extraction", "technical_extraction.csv"))
    quantitative = property(lambda self: self.path("data", "extraction", "quantitative_extraction.csv"))
    rq_evidence = property(lambda self: self.path("data", "synthesis", "rq_evidence.csv"))
    research_gaps = property(lambda self: self.path("data", "synthesis", "research_gaps.csv"))
    search_log = property(lambda self: self.path("data", "protocol", "search_log.csv"))


# ---------------------------------------------------------------- CSV helpers

def read_csv(path: Path) -> pd.DataFrame:
    """Read a working CSV as strings (empty cells -> "")."""
    if not Path(path).exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig so Excel opens non-ASCII author names correctly
    df.to_csv(path, index=False, encoding="utf-8-sig")


def merge_reviewer_columns(new: pd.DataFrame, old: pd.DataFrame, key: str,
                           keep_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carry reviewer-entered columns from an existing sheet into a regenerated one.

    Returns (merged, orphans) where orphans are old rows whose key no longer exists
    but which contained reviewer input, so no decision is ever silently lost.
    """
    for c in keep_cols:
        if c not in new.columns:
            new[c] = ""
    if old.empty or key not in old.columns:
        return new, pd.DataFrame()
    cols = [c for c in keep_cols if c in old.columns]
    old_idx = old.set_index(key)
    for c in cols:
        mapped = new[key].map(old_idx[c])
        new[c] = mapped.where(mapped.notna() & (mapped != ""), new[c])
    has_input = old[cols].apply(lambda r: any(str(v).strip() for v in r), axis=1) if cols else []
    orphans = old[~old[key].isin(new[key]) & has_input] if cols else pd.DataFrame()
    return new, orphans


# ---------------------------------------------------------------- normalisers

def normalize_doi(doi: str) -> str:
    d = (doi or "").strip().lower()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d.strip().rstrip(".")


def normalize_title(title: str) -> str:
    t = re.sub(r"<[^>]+>", " ", title or "")  # html tags in IEEE titles
    t = unicodedata.normalize("NFKD", t)
    # unicode punctuation/symbols (e.g. em dash) separate words; accents are dropped below
    t = "".join(" " if unicodedata.category(ch)[0] in "PSZ" else ch for ch in t)
    t = t.encode("ascii", "ignore").decode("ascii").lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


_INITIALS = re.compile(r"^([A-Z]\.?-?)+\.?$")


def first_author_surname(authors: str) -> str:
    """Handles 'Wei H.; Chen C.' (Scopus), 'Wei, H; Chen, C' (WoS), 'H. Wei; C. Chen' (IEEE)."""
    if not authors:
        return ""
    first = re.split(r";", authors)[0].strip()
    if "," in first:
        surname = first.split(",")[0]
    else:
        tokens = first.split()
        if len(tokens) > 1 and _INITIALS.match(tokens[-1]):
            surname = " ".join(tokens[:-1])
        else:
            surname = tokens[-1] if tokens else ""
    return normalize_title(surname)


def short_hash(text: str, n: int = 8) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def to_int(value, default=None):
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def to_float(value, default=None):
    try:
        s = str(value).strip().replace(",", ".").rstrip("%")
        return float(s) if s else default
    except (TypeError, ValueError):
        return default


def split_multi(value: str) -> list[str]:
    return [v.strip().lower() for v in re.split(r"[;|]", value or "") if v.strip()]
