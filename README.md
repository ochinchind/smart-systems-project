# Smart Traffic Lights That Learn

**A Systematic Literature Review of Reinforcement Learning for Traffic Signal Control — From Simulation to Real Streets**

Rakhimzhanov Amangeldy · Nurkin Aidar

This repository holds the SLR as a reproducible research project. It contains the planning and protocol documents, the locked search strategy, and a Python pipeline (`slr/`) for Steps 13–27. The pipeline produces the master evidence register, the PRISMA 2020 flow diagram, the quality-assessment and extraction sheets, and all synthesis tables and figures, computed directly from the database exports and the reviewers' decisions. The original project proposal is `docs/00_Project_Proposal.docx`.

## Status of Steps 1–27

| Step | Deliverable | Status |
|---|---|---|
| 1 Topic | `docs/phase1_planning/01_Topic_Feasibility_Note.md` | ✅ Done |
| 2 Scoping search | `docs/phase1_planning/02_Scoping_Search_Report.md` | ✅ Done (existing reviews, terminology, platforms, early gaps) |
| 3 Scope | `docs/phase1_planning/03_Scope_Statement.md` | ✅ Done |
| 4–5 Objectives, RQs | `docs/phase1_planning/04_05_Objectives_and_Research_Questions.md` | ✅ Done (6 RQs + Validation Realism Level scale) |
| 6 Protocol | `docs/phase1_planning/06_Review_Protocol.md` | ✅ v1.0 (register on OSF before searching) |
| 7 Concept matrix | `docs/phase2_search/07_Search_Concept_Matrix.md` | ✅ Done |
| 8 Databases | `docs/phase2_search/08_Database_Selection.md` | ✅ Scopus + WoS CC + IEEE Xplore |
| 9 Search strings | `docs/phase2_search/09_Database_Search_Strings.md`, `data/protocol/search_strings.json` | ✅ Written for all three databases |
| 10 Pilot | `docs/phase2_search/10_Pilot_Search.md`, `data/protocol/known_relevant_papers.csv`, `python -m slr pilot` | 🔶 Procedure, 20-paper gold set and recall tool ready. **The team runs the pilot.** |
| 11 Lock | `docs/phase2_search/11_Search_Protocol_v1.0_LOCKED.md` | 🔶 Sign after the pilot |
| 12 Multi-wave plan | `docs/phase2_search/12_Multi_Wave_Search_Plan.md` | ✅ Plan ready; waves are tracked automatically |
| 13 Master register | `outputs/Master_Evidence_Register.xlsx` (15 sheets), `python -m slr workbook` | ✅ Built (empty until the searches are imported) |
| 14 Deduplication | `python -m slr dedup` | ✅ Tool ready and tested |
| 15 Title/abstract screening | `python -m slr screen-ta` | ✅ Tool ready (calibration sample, κ, conservative rule) |
| 16 Full-text screening | `python -m slr screen-ft` | ✅ Tool ready (E1–E10 reasons, conflicts, stable paper IDs) |
| 17 PRISMA diagram | `python -m slr prisma` | ✅ Generated from the records (no manual counts) |
| 18 Quality assessment | `docs/phase4_quality/18_Quality_Assessment.md`, `python -m slr qa` | ✅ Rubric + tool (weighted κ) |
| 19–21 Extraction | `docs/phase5_extraction/19-21_Data_Extraction.md`, `data/protocol/codebook.csv`, `python -m slr extract` | ✅ Codebook, validation, traceable evidence register |
| 22–27 Synthesis | `docs/phase6_synthesis/22-27_Synthesis_Plan.md`, `python -m slr synthesis` | ✅ Taxonomy, method comparison, bibliometrics, statistics, meta-analysis rule, dependence control |

### What the tools cannot do for you

* **Running the database searches.** Scopus and Web of Science need the university subscription. Export the results as described in Document 09.
* **Screening, quality and extraction decisions.** These are human judgements by R1 and R2. The pipeline organises them, checks them, measures agreement and computes everything downstream.

No PRISMA count, quality score or extracted number in this repository is estimated or invented. Each one is computed from the files in `data/`, as PRISMA requires.

## Quick start

```bash
pip install -r requirements.txt
python -m pytest -q              # tests on synthetic fixture exports

# Step 10 – pilot
#   put pilot exports in data/raw/<db>/pilot_*.csv|txt
python -m slr pilot

# Steps 13-27 – after the search is locked
#   1. put exports in data/raw/scopus|wos|ieee|other/ and fill data/protocol/search_log.csv
python -m slr ingest
python -m slr dedup              # then confirm data/records/dedup_candidates.csv (is_duplicate Y/N) and re-run
python -m slr screen-ta          # reviewers fill data/screening/title_abstract.csv; re-run; --stats for kappa
python -m slr screen-ft          # reviewers fill data/screening/full_text.csv; re-run
python -m slr qa                 # reviewers fill data/quality/quality_assessment.csv; re-run
python -m slr extract            # reviewers fill data/extraction/*.csv; re-run (validates + computes RI)
python -m slr prisma             # outputs/prisma/prisma_flow.png
python -m slr synthesis          # outputs/synthesis/synthesis_report.md, tables/, figures/
python -m slr workbook           # outputs/Master_Evidence_Register.xlsx

python -m slr all                # every stage that has input, in order

python scripts/build_report.py   # all documents in one file: outputs/SLR_Project_Documentation.docx + .pdf
```

Every command can be re-run at any time. Reviewer input is never overwritten.

## Repository layout

```
docs/                    planning, protocol and procedure documents (Steps 1-27)
data/protocol/           locked search strings, search log, gold set, codebook, amendments, templates
data/raw/<source>/       unmodified database exports (input)
data/records/            raw records, deduplicated master records, dedup log/candidates (generated)
data/screening/          title/abstract + full-text sheets, included studies (reviewers fill decisions)
data/quality/            quality assessment sheet (reviewers fill scores)
data/extraction/         technical + quantitative extraction sheets (reviewers fill)
data/synthesis/          RQ evidence and research-gap tables (reviewers fill)
outputs/                 PRISMA diagram, synthesis report, tables, figures, master workbook (generated)
slr/                     pipeline source code
tests/                   unit + end-to-end tests with synthetic fixtures (not review evidence)
```

## Research questions

1. **RQ1 Landscape** — How has RL-based traffic signal control research evolved between 2019 and 2026?
2. **RQ2 Methods** — Which RL formulations are used (family, agents, state, action, reward)?
3. **RQ3 Validation** — How are the methods evaluated, and how realistic is the validation (VRL 0 synthetic simulation → VRL 5 sustained deployment)?
4. **RQ4 Performance** — How much do they improve waiting time, queue length and travel time over fixed-time, actuated, Max-Pressure and RL baselines, and does the improvement depend on validation realism?
5. **RQ5 Barriers** — What stops deployment on real streets, and what mitigations are proposed?
6. **RQ6 Gaps** — Which gaps remain, and what should future research focus on?
