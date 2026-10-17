# Document 09 — Database-Specific Search Strings (Step 9)

Each string implements `(Concept A) AND (Concept B)` from Document 07. The exact strings run, the date of the run and the number retrieved **must be recorded in `data/protocol/search_log.csv`** (PRISMA-S items 1–16). Copy the strings exactly; do not retype them.

---

## S1 — Scopus (Advanced search)

Fields: `TITLE-ABS-KEY` (title, abstract, author keywords, index keywords).

```
TITLE-ABS-KEY ( ( "reinforcement learning" OR "Q-learning" OR "deep Q-network*" OR "DQN" OR "actor-critic" OR "policy gradient" OR "proximal policy optimi*" ) AND ( "traffic signal*" OR "traffic light*" OR "signali?ed intersection*" OR "signal timing" OR "signal phas*" OR "adaptive signal control" ) ) AND PUBYEAR > 2018 AND PUBYEAR < 2027 AND ( LIMIT-TO ( DOCTYPE , "ar" ) OR LIMIT-TO ( DOCTYPE , "cp" ) ) AND ( LIMIT-TO ( LANGUAGE , "English" ) )
```

Export: *Export → CSV*, select **all** records and these field groups: Citation information, Bibliographical information, Abstract & keywords (include EID). Save as `data/raw/scopus/scopus_wave1_YYYYMMDD.csv`. Scopus allows 20 000 records per CSV export; if more, split by year.

---

## S2 — Web of Science Core Collection (Advanced search)

Editions: SCI-EXPANDED, SSCI, ESCI, CPCI-S. Field: `TS` (topic = title, abstract, author keywords, Keywords Plus).

```
TS=( ("reinforcement learning" OR "Q-learning" OR "deep Q-network*" OR DQN OR "actor-critic" OR "policy gradient" OR "proximal policy optimi*") AND ("traffic signal*" OR "traffic light*" OR "signali?ed intersection*" OR "signal timing" OR "signal phas*" OR "adaptive signal control") ) AND PY=(2019-2026)
```

Refine after running: Document Types = *Article*, *Proceedings Paper*, *Early Access*; Languages = *English*.
Export: *Export → Tab delimited file*, record content **Full Record**, in batches of 1 000 (`savedrecs.txt`, `savedrecs(1).txt`, …). Save as `data/raw/wos/wos_wave1_YYYYMMDD_partN.txt`.

---

## S3 — IEEE Xplore (Command Search)

Field: `All Metadata`. IEEE Xplore limits wildcards, so plural/spelling variants are written out.

```
("All Metadata":"reinforcement learning" OR "All Metadata":"Q-learning" OR "All Metadata":"deep Q-network" OR "All Metadata":"DQN" OR "All Metadata":"actor-critic" OR "All Metadata":"policy gradient" OR "All Metadata":"proximal policy optimization") AND ("All Metadata":"traffic signal" OR "All Metadata":"traffic signals" OR "All Metadata":"traffic light" OR "All Metadata":"traffic lights" OR "All Metadata":"signalized intersection" OR "All Metadata":"signalized intersections" OR "All Metadata":"signalised intersection" OR "All Metadata":"signal timing" OR "All Metadata":"signal phase" OR "All Metadata":"adaptive signal control")
```

Filters: Year 2019–2026; Content type = *Conferences*, *Journals*, *Early Access Articles*.
Export: *Export → Search Results → CSV* (max 2 000 per export; split by year if needed). Save as `data/raw/ieee/ieee_wave1_YYYYMMDD.csv`.

> IEEE "All Metadata" covers title, abstract, author keywords and IEEE index terms, but not the full text. It is therefore comparable to TITLE-ABS-KEY / TS. If the pilot shows a precision problem, restrict the search to the `"Document Title"`, `"Abstract"` and `"Author Keywords"` fields and record the change as a pilot iteration.

---

## Search log template (PRISMA-S)

Fill one row per executed search in `data/protocol/search_log.csv`:

| search_id | wave | database | platform | date_run (DD/MM/YYYY) | fields | query (exact) | filters | records_retrieved | export_file | run_by | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | Scopus | scopus.com | | TITLE-ABS-KEY | (string S1) | 2019–2026; ar, cp; English | | data/raw/scopus/… | R1 | |
| S2 | 1 | Web of Science CC | webofscience.com | | TS | (string S2) | 2019–2026; Article, Proc. Paper, Early Access; English | | data/raw/wos/… | R2 | |
| S3 | 1 | IEEE Xplore | ieeexplore.ieee.org | | All Metadata | (string S3) | 2019–2026; Conf., Journals, Early Access | | data/raw/ieee/… | R1 | |

`python -m slr ingest` compares the number of records parsed from each export with `records_retrieved` and warns about any mismatch.
