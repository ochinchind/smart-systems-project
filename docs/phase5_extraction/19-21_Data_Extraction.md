# Documents 19–21 — Data Extraction (Steps 19–21)

## Step 19 — Extraction schema (designed before extraction)

The codebook is defined once in `slr/codebook.py` and exported to `data/protocol/codebook.csv`, with the field, guideline section A–H, supported RQ, type, allowed values and a description. Controlled vocabularies are validated automatically: a misspelt value is reported every time `python -m slr extract` runs.

| Guideline section | Fields (technical table) | RQ |
|---|---|---|
| A Bibliographic | paper_id, authors, year, title, venue, venue_type, doi, country_first_author, study_location | RQ1 |
| B Application | application_context, n_intersections, traffic_modes, objective_focus | RQ1, RQ6 |
| C Technology / RL formulation | rl_family, algorithm, agent_architecture, coordination, state_repr, action_type, reward_type, function_approximator, simulator, sensing_source | RQ2, RQ3 |
| D/F Methodology & validation | network_source, demand_source, dataset_ids, baseline_classes, **vrl**, transfer_test, robustness_test, safety_constraints, n_seeds, code_available | RQ3, RQ4 |
| E Quantitative results | separate table (Step 21) | RQ4 |
| G Conclusions | key_findings, advantages, limitations_authors | RQ4, RQ5 |
| H Reviewer interpretation | barriers, mitigations, reviewer_strength, reviewer_weakness, research_gap_note | RQ5, RQ6 |
| Dependence | study_family_id, campaign_id | Step 27 |

Coding rules
* **VRL** is the *highest* level the study reaches (definitions in Document 04–05). A study with a calibrated simulation and a two-week field test is VRL 4.
* **dataset_ids** use canonical names so that reuse can be counted: `jinan_3x4`, `hangzhou_4x4`, `ny_16x3`, `ny_28x7`, `manhattan_large`, `shanghai`, `monaco`, `ingolstadt1/7/21`, `cologne1/3/8`, `atlanta`, `synthetic_grid_NxM`. Add new names to this list when you first use them.
* `barriers` records what the paper **discusses or evidently faces**, e.g. a camera-based state with no noise test → `sensing_data`.
* Pilot the form on 5 papers (both reviewers), compare, refine the descriptions (not the categories), then extract the rest.

## Step 20 — Traceable evidence register

Every number goes into `data/extraction/quantitative_extraction.csv` as **one row per value pair**:

| entry_id | paper_id | scenario_id | metric | rl_value | baseline_name | baseline_class | baseline_value | unit | source_location |
|---|---|---|---|---|---|---|---|---|---|
| Q0001 | P014 | hangzhou_4x4 | travel_time | 287.3 | MaxPressure | max_pressure | 312.1 | s | Table 4, p. 9 |

* `entry_id` is assigned automatically. `source_location` is **mandatory**, and the pipeline lists every entry that has none.
* When a paper reports several experiments, use one row per experiment and describe the condition in `context` (demand level, peak/off-peak). Never average across experiments yourself.
* When the paper gives only a % improvement, put it in `reported_improvement_pct` and leave the raw values empty.
* Values read off a figure: add "(read from figure)" in `context`.
* R2 verifies **100 %** of the quantitative entries (`verified_by`).

## Step 21 — Two separate evidence tables

* **Technical evidence** — `technical_extraction.csv`, one row per paper. Pre-filled with the bibliographic data and a guess of the first author's country; check the guess.
* **Quantitative evidence** — `quantitative_extraction.csv`, one row per number. The pipeline adds:
  * `direction` (lower or higher is better, from the metric);
  * `relative_improvement_pct` = (B − RL)/B × 100 for lower-is-better metrics, or (RL − B)/B × 100 for higher-is-better metrics. Positive always means RL is better;
  * `study_family_id` and `vrl_effective`, inherited from the technical table.

Commands: `python -m slr extract` (creates or updates both sheets, validates them and computes the derived columns).
