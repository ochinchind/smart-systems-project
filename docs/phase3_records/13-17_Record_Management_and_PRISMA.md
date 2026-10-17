# Documents 13–17 — Record Management, Screening and PRISMA (Steps 13–17)

All commands are run from the repository root. `python -m slr all` runs every stage that has input.

## Step 13 — Master search register

The register has **CSV files as the source of truth** (versioned in git) and an Excel snapshot regenerated on every run:

| Workbook sheet | Source file | Who edits |
|---|---|---|
| Search_Log | `data/protocol/search_log.csv` | Reviewers |
| Raw_Records | `data/records/raw_records.csv` | Pipeline |
| Deduplication | `data/records/dedup_log.csv` (+ `dedup_candidates.csv`) | Pipeline (+ reviewers confirm fuzzy pairs) |
| Title_Abstract_Screening | `data/screening/title_abstract.csv` | Reviewers (decision columns) |
| Full_Text_Screening | `data/screening/full_text.csv` | Reviewers (decision columns) |
| Included_Studies | `data/screening/included_studies.csv` | Pipeline |
| Excluded_Full_Text | derived from full_text.csv | Pipeline |
| Quality_Assessment | `data/quality/quality_assessment.csv` | Reviewers (score columns) |
| Technical_Extraction | `data/extraction/technical_extraction.csv` | Reviewers |
| Quantitative_Extraction | `data/extraction/quantitative_extraction.csv` | Reviewers |
| RQ_Evidence | `data/synthesis/rq_evidence.csv` | Reviewers |
| Research_Gaps | `data/synthesis/research_gaps.csv` | Reviewers |
| PRISMA_Counts | `outputs/prisma/prisma_counts.csv` | Pipeline |
| Reference_Audit | `data/protocol/reference_audit_template.csv` | Reviewers (later steps) |
| Submission_Audit | `data/protocol/submission_audit_template.csv` | Reviewers (later steps) |

Build it: `python -m slr workbook` → `outputs/Master_Evidence_Register.xlsx`.

**Golden rule:** reviewers only type into the decision/score/extraction columns. Re-running any command keeps that input (merged by `record_id` / `paper_id`). Rows that disappear are saved to `*_orphans.csv`, so a decision is never lost silently.

## Workflow after the search is locked

1. Save exports in `data/raw/scopus/`, `data/raw/wos/`, `data/raw/ieee/` (and `data/raw/other/` for Wave 3), wave number in the file name (e.g. `scopus_wave1_20261020.csv`).
2. Fill one row per executed search in `data/protocol/search_log.csv` (date, exact string, filters, `records_retrieved`, `export_file`).
3. `python -m slr ingest` → parses all exports; warns if the parsed count ≠ `records_retrieved`.

## Step 14 — Deduplication

`python -m slr dedup`

* Automatic merge only when it is safe: same DOI, or identical normalised title + year ±1 + same first-author surname **without** conflicting DOIs.
* Similar titles (≥ 0.93) are **not** merged automatically. They are listed in `data/records/dedup_candidates.csv`; set `is_duplicate` = `Y` or `N` and re-run `dedup`.
  A conference paper and its journal extension usually have the same title but different DOIs. Mark these `N`: they are different *reports*, and they are linked later through a study family (Step 27).
* Metadata priority when merging: Scopus > WoS > IEEE > other. Empty fields (e.g. abstract) are filled from the other copies.
* Protocol filters (year, document type, language) are applied **after** deduplication and reported as "records removed for other reasons".
* The balance is checked by the tests: identified − duplicates − removed = screened.

## Step 15 — Title/abstract screening

`python -m slr screen-ta` creates `data/screening/title_abstract.csv`:

| Column | Meaning |
|---|---|
| `assigned_to` | `R1+R2` = calibration sample (10 %, min 50, random seed 2026); otherwise `R1` or `R2` (deterministic 50/50 split) |
| `relevance_score` | Keyword score used **only to sort**; never decides anything |
| `r1_decision`, `r2_decision` | `include` / `exclude` / `uncertain` (or I / E / U) |
| `r1_confidence`, `r2_confidence` | `low` for an uncertain exclusion; it then needs the other reviewer |
| `override_decision` | Consensus after discussion (optional) |
| `final_decision` | Computed with the conservative rule: include/uncertain from either reviewer → full text |

1. Both reviewers screen the calibration rows first, then run `python -m slr screen-ta --stats`. If κ < 0.60, discuss, clarify the criteria (record the clarification in the protocol amendments), and repeat with a new sample.
2. Screen your assigned rows. Mark any exclusion you are unsure about as `low`.
3. Re-run `python -m slr screen-ta` until no `pending` rows remain.

## Step 16 — Full-text eligibility

`python -m slr screen-ft` creates `data/screening/full_text.csv` for every record with final decision include/uncertain.

* `retrieved` = `Y` or `N`; if `N`, write the attempts made in `retrieval_note` (institutional access, open-access search, interlibrary loan, e-mail to the author).
* `r1_decision` and `r2_decision` = `include` / `exclude`. Every exclusion needs **exactly one** code E1–E10 (Protocol §5) in `r1_reason` / `r2_reason`.
* If the decisions disagree, the final decision is `conflict`. Discuss and fill `consensus_decision` (and `consensus_reason`).
* If both reviewers exclude but give different codes, the hierarchy (first applicable code, E1 → E10) decides automatically.
* Included reports receive stable IDs (`P001`, …) in `data/screening/included_studies.csv`.

## Step 17 — PRISMA flow diagram

`python -m slr prisma` → `outputs/prisma/prisma_flow.png|svg` and `prisma_counts.csv`.

* All numbers are computed from the files above, never typed in.
* Database counts are reported per database. Citation-searching records are reported in the separate "other methods" column.
* "Studies included" = number of distinct study families. "Reports" = number of included papers.
* While any stage is incomplete, the diagram carries a red **DRAFT** banner that names what is pending.
