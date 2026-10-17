# Document 06 — Systematic Review Protocol (Step 6)

| Field | Value |
|---|---|
| Protocol version | **1.0** |
| Date | 17 Oct 2026 |
| Reporting framework | PRISMA 2020 (27-item checklist + abstract checklist + flow diagram, new review, databases + other sources); PRISMA-S for search reporting |
| Registration | Planned: OSF Registries (open, free). Record the OSF DOI here once registered. |
| Reviewers | **R1** — Rakhimzhanov Amangeldy; **R2** — Nurkin Aidar |

## 1. Title
Smart Traffic Lights That Learn: A Systematic Literature Review of Reinforcement Learning for Traffic Signal Control — From Simulation to Real Streets.

## 2. Objectives and research questions
See Document 04–05 (main objective, SO1–SO10, RQ1–RQ6, VRL scale).

## 3. Information sources (databases)
Scopus, Web of Science Core Collection, IEEE Xplore (core). Other sources: backward/forward citation chaining (Google Scholar, publisher pages), recorded separately as "other methods" in PRISMA. Details: Document 08.

## 4. Search period and strategy
1 Jan 2019 – final search date. Two-concept Boolean strategy (RL × traffic signal) searched in title, abstract and keywords. Database-specific strings: Document 09. Pilot: Document 10. Locked version: Document 11. Multi-wave plan: Document 12.

## 5. Eligibility criteria

### Inclusion criteria (all must be met)
| Code | Criterion |
|---|---|
| IC1 | Primary study that proposes, adapts or evaluates an **RL-based controller** for **road traffic signals** (phase selection, phase duration, cycle, split or offset) at ≥ 1 intersection |
| IC2 | Reports an **empirical evaluation** (simulation, hardware-in-the-loop or field) with ≥ 1 **quantitative traffic performance outcome** |
| IC3 | Published 1 Jan 2019 – final search date (online first date counts) |
| IC4 | Peer-reviewed **journal article** or **full conference paper** |
| IC5 | Written in **English** |
| IC6 | Full text retrievable by the review team (institutional access, open access, interlibrary loan or author request) |

### Exclusion criteria (one primary reason is recorded per excluded full text)
| Code | Reason |
|---|---|
| E1 | Wrong application — not road traffic signal control (ramp metering only, routing, autonomous driving, power/telecom "signals", etc.) |
| E2 | Wrong method — RL is not the evaluated controller (non-RL optimisation, prediction only, prompting-only LLM, RL only as minor baseline) |
| E3 | Wrong publication type — review, survey, editorial, position paper, book chapter |
| E4 | No empirical evaluation or no quantitative traffic outcome |
| E5 | Outside date range |
| E6 | Not peer-reviewed (preprint, thesis, report, poster, extended abstract < 4 pages) |
| E7 | Not in English |
| E8 | Duplicate record not detected at deduplication (same report) |
| E9 | Full text not retrievable after documented attempts (IC6) |
| E10 | Insufficient technical information to identify the RL formulation or the results |

The order E1 → E10 is the **hierarchy**: when several reasons apply, the first applicable code is recorded.

## 6. Study selection procedure
1. **Deduplication** (Step 14): automatic merge on DOI and on exact normalised title + year + first-author surname; fuzzy-title matches (similarity ≥ 0.93) are *flagged* and confirmed manually. Tool: `python -m slr dedup`.
2. **Title/abstract screening** (Step 15)
   * Calibration: R1 and R2 independently screen a random 10 % sample (minimum 50 records); Cohen's κ is computed (`python -m slr screen-ta --stats`). Target κ ≥ 0.60; otherwise discuss, clarify criteria (logged as protocol clarification) and repeat with a new sample.
   * Remaining records are split between R1 and R2. Every record a reviewer marks *Exclude – low confidence* is checked by the other reviewer.
   * Decisions: Include / Exclude / Uncertain. **Conservative rule:** Include or Uncertain from either reviewer → full-text stage.
   * A keyword relevance score is shown only to sort the list; it never makes a decision.
3. **Full-text eligibility** (Step 16): both reviewers assess **all** full texts independently; one primary exclusion code per excluded report; disagreements resolved by discussion, recorded in the `notes` field.
4. **Reports vs studies:** a journal extension of a conference paper reporting the same experiments is kept as a *report* but linked through a **Study Family ID** (Step 27), so it is not double counted in the synthesis.

## 7. Quality assessment (Step 18)
Five domains scored 0 (No) / 1 (Partial) / 2 (Yes), maximum 10. Thresholds fixed **a priori**: High 8–10, Moderate 5–7, Limited 0–4. QA is **not** an exclusion criterion; it is used for interpretation and sensitivity analysis. Both reviewers score all included studies; κ (weighted) is reported. Full rubric: Document 18.

## 8. Data extraction (Steps 19–21)
Codebook with controlled vocabularies: Document 19–21 and `data/protocol/codebook.csv`. Two evidence tables: Technical extraction (one row per report) and Quantitative evidence register (one row per number, with source page/table/figure). R1 extracts, R2 verifies 100 % of quantitative entries and a 20 % random sample of technical entries.

## 9. Synthesis plan (Steps 22–27)
* Taxonomy of methods and validation (Step 22); method-family comparison table (Step 23).
* Descriptive bibliometrics (Step 24).
* Quantitative synthesis of **relative improvement** RI = (baseline − RL)/baseline × 100 % for lower-is-better metrics (and (RL − baseline)/baseline × 100 % for higher-is-better), stratified by metric × baseline class × VRL; median, IQR, min, max, mean, SD (Step 25).
* Meta-analysis only if the pre-specified feasibility rule (Document 26) is met; otherwise structured narrative synthesis with subgroup comparison.
* Dependence control: Study Family ID and Dataset/Scenario ID; summary statistics computed at family level (Step 27).
* Sensitivity analysis: excluding Limited-quality studies; excluding families that contribute > 10 % of entries.

## 10. Reviewer responsibilities
| Task | R1 (Amangeldy) | R2 (Aidar) |
|---|---|---|
| Search execution & export | Scopus, IEEE Xplore | Web of Science, citation chaining |
| Search log / PRISMA-S | Owner | Verifier |
| Title/abstract screening | Calibration + 50 % | Calibration + 50 % |
| Full-text screening | 100 % | 100 % |
| QA | 100 % | 100 % |
| Technical extraction | Owner | 20 % verification |
| Quantitative extraction | Owner | 100 % verification |
| Synthesis & figures | Shared | Shared |
| Disagreements | Discussion; unresolved → decided by consensus with supervisor | |

## 11. Tools
Python pipeline in this repository (`slr/`), master evidence workbook (`outputs/Master_Evidence_Register.xlsx`), reference manager (Zotero) for PDFs.

## 12. Amendments log
Any change to scope, search concepts, eligibility, RQs or QA after the search is locked is recorded here (and in `data/protocol/amendments.csv`) with date, reason and impact.

| # | Date | Section | Change | Reason | Impact |
|---|---|---|---|---|---|
| — | — | — | (none yet) | — | — |
