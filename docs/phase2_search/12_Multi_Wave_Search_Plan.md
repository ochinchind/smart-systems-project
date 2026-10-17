# Document 12 — Multi-Wave Search Strategy (Step 12)

Every wave is logged in `data/protocol/search_log.csv` (column `wave`) and its exports are stored in `data/raw/<source>/` with the wave in the file name (`…_wave2_…`). The pipeline reads the wave from the file name and reports PRISMA counts per source and wave.

| Wave | Purpose | How | PRISMA box |
|---|---|---|---|
| **1 — Core database search** | Main evidence base | Run locked S1–S3 in all three databases | Records from databases |
| **2 — Terminology expansion** | Recall for synonyms found in Wave 1 (Concept D) and deployment terms (Concept C) | Strings S1b–S3b = `(A ∪ D) AND (B)` *NOT* already-retrieved results; and `(A ∪ D) AND (B) AND (C)`; same filters | Records from databases (wave 2) |
| **3 — Citation chaining** | Find studies missed by keywords | **Backward:** reference lists of (a) all included studies with QA ≥ 8 and (b) the reviews in Document 02. **Forward:** Google Scholar "Cited by" for the same set. Candidates entered in `data/raw/other/citation_chaining.csv` (unified format) | Records from other methods: citation searching |
| **4 — Gap-targeted and update search** | (a) Under-represented contexts found in the gap matrix (e.g., pedestrians, public transport, field tests); (b) update to capture papers published after Wave 1 | (a) `(A) AND (B) AND (E-term)`; (b) re-run S1–S3 restricted to the load date ≥ Wave 1 date, immediately before submission | (a) databases; (b) databases — reported as update |

Rules
1. A record found in several waves is deduplicated like any other; its first wave is kept as `first_wave`.
2. Supplementary searches never change eligibility criteria.
3. Citation-chaining candidates are screened with the same two-stage process.
4. The date of the last search (Wave 4b) is the review's "search date" reported in the abstract (PRISMA item 7).

Unified CSV columns for `data/raw/other/*.csv`:
`source, title, authors, year, venue, doi, abstract, keywords, doc_type, language, url, found_via`
