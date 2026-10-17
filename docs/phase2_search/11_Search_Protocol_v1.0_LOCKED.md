# Document 11 — SEARCH PROTOCOL VERSION 1.0 — LOCKED (Step 11)

> Locking takes effect when the pilot (Document 10) meets its recall criterion and both reviewers sign below. After that, any change is an **amendment** (Document 06 §12, `data/protocol/amendments.csv`).

| Element | Locked value |
|---|---|
| Databases | Scopus; Web of Science Core Collection (SCI-EXPANDED, SSCI, ESCI, CPCI-S); IEEE Xplore |
| Strings | S1, S2, S3 exactly as in Document 09 (machine-readable copy: `data/protocol/search_strings.json`) |
| Fields | Scopus TITLE-ABS-KEY; WoS TS; IEEE All Metadata |
| Period | 2019-01-01 to date of final search |
| Document types | Journal article (incl. early access), conference paper |
| Language | English |
| Inclusion criteria | IC1–IC6 (Document 06 §5) |
| Exclusion criteria | E1–E10, applied in hierarchical order (Document 06 §5) |
| QA | QA1–QA5, 0/1/2, thresholds 8–10 / 5–7 / 0–4 (Document 18) |
| Extraction | Codebook v1.0 (`data/protocol/codebook.csv`) |

Machine-readable configuration used by the pipeline: `slr/config.py`.

| Role | Name | Date | Signature |
|---|---|---|---|
| Reviewer 1 | Rakhimzhanov Amangeldy | | |
| Reviewer 2 | Nurkin Aidar | | |
