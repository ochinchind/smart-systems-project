# Documents 22–27 — Classification and Synthesis (Steps 22–27)

`python -m slr synthesis` computes everything below from the extraction sheets and writes:
* `outputs/synthesis/synthesis_report.md` — all results in one place, with tables and figure links;
* `outputs/synthesis/tables/*.csv` — every table, ready for the manuscript;
* `outputs/synthesis/figures/*.png` — 200-dpi figures;
* `outputs/synthesis/taxonomy.md` — the taxonomy with counts and a Mermaid mind map.

## Step 22 — Taxonomy

Hierarchy (preliminary, built from scoping; the counts are filled from the data):

```
RL for traffic signal control
├── Application context: isolated · arterial corridor · grid · real urban network
├── Road users: private vehicles · pedestrians · cyclists · public transport · emergency · CAV
├── RL formulation
│   ├── Family: tabular · value-based deep · policy gradient · actor–critic · model-based · hierarchical · meta-RL · offline RL · LLM–RL hybrid
│   ├── Agents: single · independent MARL · cooperative MARL · centralised
│   ├── Coordination: none · neighbour observation · communication · graph attention · pressure-based · hierarchical
│   ├── State / Action / Reward
│   └── Function approximator: table · MLP · CNN · RNN · GNN · attention · LLM
├── Evaluation: simulator · network source · demand source · baselines
├── Validation realism: VRL0 → VRL5 (+ transfer, robustness, safety flags)
├── Performance indicators: travel time · waiting time · delay · queue · throughput · stops · emissions · safety
├── Deployment barriers: sensing · sim-to-real · safety/compliance · robustness · computation · communication · interpretability · scalability · multimodality · training cost · regulation
└── Research gaps (gap matrix)
```

The final taxonomy figure for the manuscript is drawn from `taxonomy.md`.

## Step 23 — Comparison of methodological families

`tables/method_family_comparison.csv` combines:
* **computed** columns: number of papers, top algorithms, median and maximum VRL, % with transfer, robustness and code-availability tests, median RI against fixed-time, Max-Pressure and RL baselines, top barriers;
* **conceptual** columns (`data/protocol/method_families.csv`): principle, advantages, limitations, typical validation, best application. Revise these after extraction so that they reflect the evidence.

## Step 24 — Bibliometric and descriptive analysis

Papers per year (split by journal/conference), top venues, countries, application context, road users, objectives, RL family over time, algorithms, agent architecture, coordination, state, action, reward, approximator, simulators, network and demand sources, baselines, **VRL distribution**, validation flags, barriers, QA classes. Heat map: RL family × VRL.

## Step 25 — Quantitative synthesis

* Effect measure: relative improvement RI (%), positive = RL better.
* Stratification: metric × baseline class (primary), metric × VRL (to test whether gains shrink as validation becomes more realistic), and a sensitivity analysis that excludes Limited-QA studies.
* Statistics: n values, n papers, n families, min, Q1, median, Q3, max, mean, SD.
* **Primary level = study family**: one value per family and cell, the median of its entries. Entry-level statistics are reported as a secondary analysis.
* Figures: box plots (RI by baseline class, one panel per metric, with every family shown as a point) and a scatter of RI against VRL.
* Different metrics are never pooled together; the relative scale makes units comparable only *within* a metric.

## Step 26 — Is a meta-analysis appropriate?

Pre-specified rule: a cell (metric × baseline class) is eligible only if **≥ 5 independent study families** report mean, SD and number of runs, all in the same unit. For eligible cells, `meta_analysis_feasibility.csv` gives an *exploratory* random-effects (DerSimonian–Laird) pooled log response ratio, converted back to %, with a 95 % CI, τ² and I².

Expected outcome, based on scoping: most cells will **not** be eligible (dispersion is rarely reported and scenarios are heterogeneous). In that case the review uses a structured narrative synthesis with subgroup comparison and descriptive statistics, and says so explicitly. A meta-analysis is not forced.

## Step 27 — Dependence between publications

* `study_family_id`: reports of the same experiments, project or code base share an ID (e.g. a conference paper and its journal extension; a series that reuses the same trained agents).
* `campaign_id`: the same field trial.
* `dataset_ids` / `scenario_id`: the same benchmark dataset. Reuse is counted in `dataset_reuse.csv`. Shared *public* datasets (e.g. Jinan, Hangzhou) do **not** by themselves make studies dependent, but the reuse is reported because it limits external validity.
* `study_families.csv` flags families that contribute **> 10 %** of the quantitative entries (`dominant_family_gt10pct`). These are checked in the sensitivity analysis.
* PRISMA reports both *studies* (families) and *reports* (papers).
