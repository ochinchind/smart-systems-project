# Document 10 — Pilot Search Procedure (Step 10)

## Purpose
Check **recall** (does the search find papers we already know are relevant?) and **precision** (how much noise?) before locking the strategy.

## Benchmark ("gold") set
`data/protocol/known_relevant_papers.csv` lists 20 papers identified during scoping (Document 02) that any adequate search must retrieve. It deliberately mixes:
* landmark DRL methods (PressLight, CoLight, FRAP, MPLight, MetaLight, AttendLight, MA2C, Advanced-XLight, CoSLight);
* deployment/realism papers (Müller et al. 2021; Müller & Sabatelli 2022; Egea et al. 2020; UGAT 2023; PromptGAT 2024);
* benchmark and LLM papers (RESCO 2021, LibSignal, LLMLight);
* reviews (Noaeen 2022; Haydari & Yilmaz 2022; Michailidis 2025) — retrieved by the search but later excluded with E3; they are needed for Wave 3 chaining.

Some gold papers appear in venues that are not indexed by every database (e.g., NeurIPS). Recall is therefore assessed **across the union of the three databases**, and per database for information.

## Procedure
1. Run S1–S3 (Document 09) and export results into `data/raw/<db>/` with file names starting `pilot_`.
2. Run `python -m slr pilot --raw-glob "data/raw/*/pilot_*"`.
   The tool matches gold papers to the exports by DOI or normalised title and writes `outputs/pilot/pilot_recall.csv` plus a summary.
3. **Recall criterion:** ≥ 90 % of the gold papers that are indexed in at least one of the databases must be retrieved by the union of searches. For each miss, record *why* (not indexed / terminology not covered / filter problem).
4. **Precision check:** screen a random sample of 100 retrieved titles (`python -m slr pilot --precision-sample 100` writes the sample). Report the proportion that is plausibly relevant.
5. If a miss is caused by terminology, add the missing synonym to Concept A/B (Document 07), re-run and repeat. If precision < 20 %, consider adding context terms — but never tune the search towards preferred papers only.
6. Record every iteration in `data/protocol/pilot_log.csv` (iteration, change, recall, precision, decision).

## Result
To be completed after the pilot is run:

| Iteration | Change | Gold retrieved (union) | Recall | Precision (sample) | Decision |
|---|---|---|---|---|---|
| 1 | Strings S1–S3 v0.9 | | | | |

The pilot exports are **not** used as review evidence; Wave 1 is re-run after locking.
