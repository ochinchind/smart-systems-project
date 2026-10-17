"""Command-line entry point: python -m slr <command> [--root DIR]

Typical order (Documents 13-27):
  pilot        Step 10   recall/precision of pilot exports
  ingest       Step 13   parse database exports -> data/records/raw_records.csv
  dedup        Step 14   deduplicate -> master_records.csv (+ fuzzy candidates to confirm)
  screen-ta    Step 15   build/update title-abstract sheet, report agreement
  screen-ft    Step 16   build/update full-text sheet, included studies
  prisma       Step 17   counts + PRISMA 2020 flow diagram
  qa           Step 18   quality assessment sheet
  extract      Steps 19-21 extraction sheets, validation, relative improvement
  synthesis    Steps 22-27 taxonomy, comparisons, statistics, figures, report
  workbook     Step 13   master evidence register (.xlsx)
  all          everything from ingest to workbook, skipping stages without input
"""

from __future__ import annotations

import argparse
import json
import sys

from . import dedup, extraction, ingest, pilot, prisma, quality, screening, synthesis, workbook
from .project import Project


def _print(title: str, obj) -> None:
    print(f"== {title}")
    print(json.dumps(obj, indent=2, default=str, ensure_ascii=False) if not isinstance(obj, str) else obj)


def _problems(title: str, problems: list[str]) -> None:
    if problems:
        print(f"!! {title}: {len(problems)} problem(s)")
        for p in problems[:50]:
            print("   -", p)
        if len(problems) > 50:
            print(f"   ... {len(problems) - 50} more")


def cmd_ingest(p):
    raw = ingest.ingest(p)
    _print("ingest", raw.groupby(["source", "wave"]).size().to_dict() if not raw.empty else "no exports found")
    _problems("search log check", ingest.check_search_log(p, raw))


def cmd_extract(p):
    _problems("technical extraction", extraction.build_technical_sheet(p))
    _problems("quantitative extraction", extraction.build_quantitative_sheet(p))
    print("== extraction sheets updated:", p.technical, p.quantitative, sep="\n   ")


COMMANDS = {
    "pilot": lambda p, a: _print("pilot", pilot.run(p, a.precision_sample)),
    "ingest": lambda p, a: cmd_ingest(p),
    "dedup": lambda p, a: _print("dedup", dedup.deduplicate(p)),
    "screen-ta": lambda p, a: _print("title/abstract", screening.ta_stats(project=p) if a.stats
                                     else screening.build_ta_sheet(p)),
    "screen-ft": lambda p, a: _print("full text", screening.build_ft_sheet(p)),
    "prisma": lambda p, a: _print("prisma", prisma.run(p)),
    "qa": lambda p, a: _print("quality assessment", quality.build_qa_sheet(p)),
    "extract": lambda p, a: cmd_extract(p),
    "synthesis": lambda p, a: _print("synthesis report", str(synthesis.run(p))),
    "workbook": lambda p, a: _print("workbook", workbook.build(p)),
}


def run_all(p, a):
    for name in ("ingest", "dedup", "screen-ta", "screen-ft", "prisma", "qa", "extract", "synthesis", "workbook"):
        try:
            COMMANDS[name](p, a)
        except SystemExit as e:  # stage has no input yet - continue with the rest
            print(f"-- {name}: skipped ({e})")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m slr", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=list(COMMANDS) + ["all"])
    ap.add_argument("--root", default=".", help="project root (default: current directory)")
    ap.add_argument("--stats", action="store_true", help="screen-ta: only report agreement statistics")
    ap.add_argument("--precision-sample", type=int, default=100, help="pilot: size of precision sample")
    a = ap.parse_args(argv)
    p = Project(a.root)
    if a.command == "all":
        run_all(p, a)
    else:
        COMMANDS[a.command](p, a)


if __name__ == "__main__":
    sys.exit(main())
