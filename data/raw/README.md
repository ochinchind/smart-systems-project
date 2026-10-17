# Raw database exports

Put the unmodified export files here, one folder per source. The wave number goes in the file name:

| Folder | Export format | File name example |
|---|---|---|
| `scopus/` | Scopus CSV (all fields incl. abstract, keywords, EID, affiliations) | `scopus_wave1_20261020.csv` |
| `wos/` | Web of Science tab-delimited **Full Record** (or plain text) | `wos_wave1_20261020_part1.txt` |
| `ieee/` | IEEE Xplore CSV | `ieee_wave1_20261020.csv` |
| `other/` | Unified CSV (see Document 12) or RIS, for citation chaining and other methods | `citation_chaining_wave3.csv` |

* Files starting with `pilot_` are used only by `python -m slr pilot`; they are never treated as evidence.
* Never edit an export by hand. If a record is wrong, correct it in the screening sheet's notes.
* Record every export in `data/protocol/search_log.csv` (`export_file`, `records_retrieved`).
