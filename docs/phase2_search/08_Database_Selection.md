# Document 08 — Database Selection (Step 8)

| Database | Platform | Coverage relevant to RL-TSC | Role |
|---|---|---|---|
| **Scopus** | Elsevier, scopus.com | Broadest multidisciplinary coverage; indexes ACM (KDD, CIKM), AAAI, IEEE, Elsevier (TR-C, ESWA), Springer, MDPI, Taylor & Francis | Core 1 (highest metadata priority in deduplication) |
| **Web of Science Core Collection** | Clarivate, webofscience.com — SCI-EXPANDED, SSCI, ESCI, CPCI-S | Independent curated index; strong for transport journals | Core 2 |
| **IEEE Xplore** | IEEE, ieeexplore.ieee.org | Domain-specific: IEEE T-ITS, T-VT, IoT-J, ITSC, CDC, CASE, SMC — many early-access papers not yet in Scopus/WoS | Core 3 (domain-specific) |
| Google Scholar | scholar.google.com | Forward citation chaining ("Cited by") | Other methods (Wave 3) — not a PRISMA database |
| ACM Digital Library | dl.acm.org | KDD/CIKM proceedings — cross-check during pilot only | Pilot check |

Principle followed: **three independent bibliographic databases** (two multidisciplinary + one domain-specific), as recommended for engineering SLRs (Scopus + WoS + domain database).

## Not used, with reason
* **arXiv** — preprints are excluded (E6); arXiv versions are only used to locate the peer-reviewed version.
* **PubMed / Embase** — not relevant to traffic engineering.
* **TRID (TRB)** — considered; excluded because export is limited and coverage of RL papers overlaps Scopus/WoS. Documented as a limitation.
