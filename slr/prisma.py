"""Step 17: PRISMA 2020 counts and flow diagram, computed only from the records.

Nothing is estimated: a count that cannot be derived yet is shown as "pending" and the
diagram is watermarked DRAFT until every stage is complete.
"""

from __future__ import annotations

import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import pandas as pd

from . import config
from .project import Project, read_csv, write_csv
from .screening import ft_final, ta_final


def compute_counts(project: Project) -> dict:
    raw = read_csv(project.raw_records)
    log = read_csv(project.dedup_log)
    master = read_csv(project.master_records)
    if raw.empty or master.empty:
        raise SystemExit("Run ingest and dedup first.")
    ta = read_csv(project.ta_sheet)
    ft = read_csv(project.ft_sheet)
    tech = read_csv(project.technical)

    c: dict = {"pending": []}
    is_db = raw["source"].isin(config.DATABASE_SOURCES)
    c["db_by_source"] = {config.SOURCE_LABELS[s]: int((raw["source"] == s).sum())
                         for s in config.DATABASE_SOURCES}
    c["db_by_wave"] = raw[is_db].groupby("wave").size().to_dict()
    c["db_identified"] = int(is_db.sum())
    c["other_identified"] = int((~is_db).sum())
    other_files = raw.loc[~is_db, "raw_file"].value_counts().to_dict()
    c["other_by_file"] = {k: int(v) for k, v in other_files.items()}

    dup = log[log["status"] == "duplicate_removed"]
    c["db_duplicates"] = int(dup["source"].isin(config.DATABASE_SOURCES).sum())
    c["other_duplicates"] = int((~dup["source"].isin(config.DATABASE_SOURCES)).sum())

    for stream in ("database", "other"):
        m = master[master["origin"] == stream]
        removed = m[m["eligible_for_screening"] == "N"]
        c[f"{stream}_removed_other"] = int(len(removed))
        c[f"{stream}_removed_by_reason"] = removed["removed_reason"].value_counts().to_dict()
        c[f"{stream}_screened"] = int((m["eligible_for_screening"] == "Y").sum())

    if ta.empty:
        c["pending"].append("title/abstract screening not started")
        return c
    ta["final_decision"] = ta.apply(ta_final, axis=1)
    ta["origin"] = ta["record_id"].map(master.set_index("record_id")["origin"])
    n_pending = int(ta["final_decision"].str.startswith("pending").sum())
    if n_pending:
        c["pending"].append(f"{n_pending} records still pending at title/abstract stage")
    for stream in ("database", "other"):
        t = ta[ta["origin"] == stream]
        c[f"{stream}_ta_excluded"] = int((t["final_decision"] == "exclude").sum())
        c[f"{stream}_sought"] = int(t["final_decision"].isin(["include", "uncertain"]).sum())

    if ft.empty:
        c["pending"].append("full-text screening not started")
        return c
    res = ft.apply(ft_final, axis=1, result_type="expand")
    ft["final_decision"], ft["final_reason"] = res[0], res[1]
    n_pending = int(ft["final_decision"].isin(["pending", "conflict"]).sum())
    if n_pending:
        c["pending"].append(f"{n_pending} reports pending/conflicting at full-text stage")
    for stream in ("database", "other"):
        f = ft[ft["origin"] == stream]
        c[f"{stream}_not_retrieved"] = int((f["final_decision"] == "not_retrieved").sum())
        c[f"{stream}_assessed"] = int((f["retrieved"].str.strip().str.upper() == "Y").sum())
        exc = f[f["final_decision"] == "exclude"]
        order = list(config.EXCLUSION_REASONS)
        by = exc["final_reason"].value_counts().to_dict()
        c[f"{stream}_excluded_by_reason"] = {k: int(by[k]) for k in order if k in by}
        c[f"{stream}_ft_excluded"] = int(len(exc))
    inc = ft[ft["final_decision"] == "include"]
    c["reports_included"] = int(len(inc))
    c["reports_included_db"] = int((inc["origin"] == "database").sum())
    c["reports_included_other"] = int((inc["origin"] == "other").sum())
    if not tech.empty and "study_family_id" in tech.columns:
        c["studies_included"] = int(tech["study_family_id"].replace("", pd.NA).dropna().nunique())
    else:
        c["studies_included"] = c["reports_included"]
        c["pending"].append("study families not assigned yet (studies = reports)")
    return c


def counts_table(c: dict) -> pd.DataFrame:
    rows = []
    add = lambda stage, stream, label, n: rows.append({"stage": stage, "stream": stream, "item": label, "n": n})
    for k, v in c["db_by_source"].items():
        add("Identification", "databases", f"Records from {k}", v)
    add("Identification", "databases", "Records from databases (total)", c["db_identified"])
    add("Identification", "databases", "Registers", 0)
    for k, v in c["other_by_file"].items():
        add("Identification", "other methods", f"Records from {k}", v)
    add("Identification", "databases", "Duplicate records removed", c["db_duplicates"])
    add("Identification", "other methods", "Duplicate records removed", c["other_duplicates"])
    for stream, label in (("database", "databases"), ("other", "other methods")):
        for reason, n in c.get(f"{stream}_removed_by_reason", {}).items():
            add("Identification", label, f"Removed for other reasons: {reason}", n)
        add("Screening", label, "Records screened", c.get(f"{stream}_screened"))
        add("Screening", label, "Records excluded (title/abstract)", c.get(f"{stream}_ta_excluded", "pending"))
        add("Screening", label, "Reports sought for retrieval", c.get(f"{stream}_sought", "pending"))
        add("Screening", label, "Reports not retrieved", c.get(f"{stream}_not_retrieved", "pending"))
        add("Eligibility", label, "Reports assessed for eligibility", c.get(f"{stream}_assessed", "pending"))
        for code, n in c.get(f"{stream}_excluded_by_reason", {}).items():
            add("Eligibility", label, f"Reports excluded: {code} {config.EXCLUSION_REASONS[code]}", n)
    add("Included", "all", "Studies included in review", c.get("studies_included", "pending"))
    add("Included", "all", "Reports of included studies", c.get("reports_included", "pending"))
    return pd.DataFrame(rows)


def _box(ax, x, y, w, h, text, face="#ffffff", size=7.2, bold_first=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=0.8",
                                linewidth=0.9, edgecolor="#333333", facecolor=face))
    width = max(18, int(w * 1.55 * 7.2 / size))
    lines = []
    for i, para in enumerate(text.split("\n")):
        wrapped = textwrap.wrap(para, width=width, subsequent_indent="   ") or [""]
        lines.extend(wrapped)
    ax.text(x + 1.0, y + h - 1.0, "\n".join(lines), va="top", ha="left", fontsize=size,
            family="DejaVu Sans", linespacing=1.25)


def _arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=0.9))


def _n(c, key):
    v = c.get(key)
    return "pending" if v is None else str(v)


def draw_diagram(c: dict, out_base) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 12))
    ax.set_xlim(0, 104)
    ax.set_ylim(0, 128)
    ax.axis("off")
    hdr = "#cfe2f3"
    _box(ax, 6, 121, 61, 5, "Identification of studies via databases and registers", face=hdr, size=9)
    _box(ax, 71, 121, 31, 5, "Identification of studies via other methods", face="#e6e6e6", size=8.5)
    for y, h, lab in ((95, 24, "Identification"), (40, 53, "Screening"), (2, 36, "Included")):
        ax.add_patch(FancyBboxPatch((0.3, y), 3.6, h, boxstyle="round,pad=0.2", facecolor=hdr,
                                    edgecolor="#333333", lw=0.9))
        ax.text(2.1, y + h / 2, lab, rotation=90, va="center", ha="center", fontsize=9, weight="bold")

    # left: databases
    src = "\n".join(f"  {k} (n = {v})" for k, v in c["db_by_source"].items())
    _box(ax, 6, 97, 28, 21, f"Records identified from:\nDatabases (n = {c['db_identified']})\n{src}\nRegisters (n = 0)")
    removed = "\n".join(f"  {k.replace(' (protocol filter)', '')} (n = {v})"
                        for k, v in c.get("database_removed_by_reason", {}).items()) or "  none"
    _box(ax, 39, 97, 28, 21, f"Records removed before screening:\nDuplicate records removed (n = {c['db_duplicates']})\n"
                             f"Records marked as ineligible by automation tools (n = 0)\n"
                             f"Records removed for other reasons (n = {c['database_removed_other']}):\n{removed}")
    _arrow(ax, 34, 107, 39, 107)

    _box(ax, 6, 80, 28, 8, f"Records screened\n(n = {_n(c, 'database_screened')})")
    _box(ax, 39, 80, 28, 8, f"Records excluded\n(n = {_n(c, 'database_ta_excluded')})")
    _arrow(ax, 20, 97, 20, 88.6)
    _arrow(ax, 34, 84, 39, 84)

    _box(ax, 6, 66, 28, 8, f"Reports sought for retrieval\n(n = {_n(c, 'database_sought')})")
    _box(ax, 39, 66, 28, 8, f"Reports not retrieved\n(n = {_n(c, 'database_not_retrieved')})")
    _arrow(ax, 20, 80, 20, 74.6)
    _arrow(ax, 34, 70, 39, 70)

    _box(ax, 6, 44, 28, 16, f"Reports assessed for eligibility\n(n = {_n(c, 'database_assessed')})")
    exc = "\n".join(f"  {k}: {config.EXCLUSION_REASONS[k]} (n = {v})"
                    for k, v in c.get("database_excluded_by_reason", {}).items()) or "  pending"
    _box(ax, 39, 40, 28, 24, f"Reports excluded (n = {_n(c, 'database_ft_excluded')}):\n{exc}", size=6.4)
    _arrow(ax, 20, 66, 20, 60.6)
    _arrow(ax, 34, 52, 39, 52)

    # right: other methods
    oth = "\n".join(f"  {k} (n = {v})" for k, v in c["other_by_file"].items()) or "  none"
    _box(ax, 71, 97, 31, 21, f"Records identified from:\nCitation searching / other (n = {c['other_identified']})\n{oth}\n"
                             f"Duplicates of database records removed (n = {c['other_duplicates']})\n"
                             f"Removed for other reasons (n = {c.get('other_removed_other', 0)})\n"
                             f"Excluded on title/abstract (n = {_n(c, 'other_ta_excluded')})", size=6.6)
    _box(ax, 71, 80, 31, 8, f"Reports sought for retrieval\n(n = {_n(c, 'other_sought')})")
    _box(ax, 71, 66, 31, 8, f"Reports not retrieved\n(n = {_n(c, 'other_not_retrieved')})")
    _box(ax, 71, 53, 31, 7, f"Reports assessed for eligibility\n(n = {_n(c, 'other_assessed')})")
    exc_o = "\n".join(f"  {k} (n = {v})" for k, v in c.get("other_excluded_by_reason", {}).items()) or "  none/pending"
    _box(ax, 71, 40, 31, 10, f"Reports excluded (n = {_n(c, 'other_ft_excluded')}):\n{exc_o}", size=6.6)
    _arrow(ax, 86.5, 97, 86.5, 88.6)
    _arrow(ax, 86.5, 80, 86.5, 74.6)
    _arrow(ax, 86.5, 66, 86.5, 60.6)
    _arrow(ax, 86.5, 52, 86.5, 50.6)

    _box(ax, 6, 14, 28, 14, f"Studies included in review\n(n = {_n(c, 'studies_included')})\n"
                            f"Reports of included studies\n(n = {_n(c, 'reports_included')})", face="#e2f0d9", size=8)
    _arrow(ax, 20, 44, 20, 28.6)
    ax.annotate("", xy=(34, 22), xytext=(86.5, 39.4),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=0.9, connectionstyle="angle,angleA=-90,angleB=0"))

    ax.text(52, 6, "PRISMA 2020 flow diagram (new systematic review; databases, registers and other sources).\n"
                   "Counts generated automatically from data/records and data/screening by `python -m slr prisma`.",
            fontsize=7, ha="center", va="center", color="#444444")
    if c["pending"]:
        ax.text(52, 64, "DRAFT — " + "; ".join(c["pending"]), fontsize=9, color="#c00000", alpha=0.85,
                ha="center", va="center", rotation=0,
                bbox=dict(facecolor="white", edgecolor="#c00000", alpha=0.9))
    fig.savefig(f"{out_base}.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{out_base}.svg", bbox_inches="tight")
    plt.close(fig)


def run(project: Project) -> dict:
    c = compute_counts(project)
    out = project.outputs_dir / "prisma"
    out.mkdir(parents=True, exist_ok=True)
    write_csv(counts_table(c), out / "prisma_counts.csv")
    draw_diagram(c, out / "prisma_flow")
    return c
