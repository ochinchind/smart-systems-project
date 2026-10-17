# Documents 04–05 — Review Objectives and Research Questions (Steps 4–5)

## Step 4 — Main objective

> The objective of this systematic literature review is to identify, classify, compare and critically evaluate peer-reviewed research (2019–2026) on reinforcement learning for traffic signal control, with particular emphasis on RL formulations, evaluation environments and **validation realism**, reported traffic performance, deployment barriers and research gaps that separate simulation results from real-street use.

### Specific objectives

| # | Specific objective | Answered in |
|---|---|---|
| SO1 | Quantify publication trends, venues, countries and application contexts | RQ1 |
| SO2 | Classify RL methods (algorithm family, single vs multi-agent, state, action, reward) | RQ2 |
| SO3 | Identify simulators, road networks, demand data and baselines used | RQ3 |
| SO4 | Code every study on the Validation Realism Level scale (VRL 0–5) | RQ3 |
| SO5 | Compare reported improvements in waiting time, queue length, travel time/delay and secondary outcomes | RQ4 |
| SO6 | Examine whether improvements depend on baseline strength and validation realism | RQ4 |
| SO7 | Catalogue advantages, limitations and deployment barriers, and the solutions proposed | RQ5 |
| SO8 | Assess methodological quality and reproducibility | QA (supports all RQs) |
| SO9 | Identify research gaps | RQ6 |
| SO10 | Recommend future research directions to move RL-TSC to real streets | RQ6 |

## Step 5 — Research questions

The project proposal posed four questions; they are refined into six answerable RQs.

| RQ | Question | Proposal question | Main extraction fields |
|---|---|---|---|
| **RQ1 — Landscape** | How has research on RL-based traffic signal control evolved between 2019 and 2026 in terms of volume, publication venues, countries and application contexts? | "how fast is this research area growing?" | year, venue, venue type, country, network scale, application context |
| **RQ2 — Methods** | Which RL formulations are used — algorithm family, agent architecture (single/multi-agent, centralised/decentralised, coordination mechanism), state, action and reward design — and how have they changed over time? | "Which RL methods are used…" | rl_family, algorithm, agent_architecture, coordination, state_repr, action_type, reward_type |
| **RQ3 — Validation** | How are RL-TSC methods evaluated (simulators, networks, demand data, baselines, robustness/transfer tests), and how are studies distributed across Validation Realism Levels 0–5? | "How are these methods tested: only in simulators, or also on real intersections?" | simulator, network_source, demand_source, baselines, vrl, transfer_test, robustness_test |
| **RQ4 — Performance** | What improvements in waiting time, queue length, travel time / delay (and throughput, stops, emissions, safety surrogates) are reported relative to fixed-time, actuated/Max-Pressure and RL baselines, and do they differ by baseline class and validation realism? | "How much do they actually improve traffic…?" | Quantitative evidence register (metric, RL value, baseline class, baseline value, relative improvement) |
| **RQ5 — Strengths, limitations and barriers** | What advantages, limitations and deployment barriers (sensing/data, sim-to-real gap, safety and regulatory compliance, robustness, computation/communication, interpretability, multimodality, scalability) are reported, and which mitigations are proposed? | "What stops them from being used in real cities…?" | barriers (coded), mitigations, limitations (authors' and reviewers') |
| **RQ6 — Gaps and future research** | Which scientific, methodological, technological and application gaps remain, and which approaches appear most promising for closing the simulation-to-street gap? | "…what should future research focus on?" | gap matrix, reviewer interpretation, future work statements |

### Validation Realism Level (VRL) — central coding scheme for RQ3/RQ4

| VRL | Name | Definition (highest level reached by the study) |
|---|---|---|
| 0 | Synthetic simulation | Synthetic network (e.g., grid) and synthetic demand |
| 1 | Real-geometry simulation | Real road-network geometry, synthetic or uncalibrated demand |
| 2 | Real-data simulation | Simulation driven by observed demand data (detector/camera/trajectory datasets) and/or calibrated against field measurements |
| 3 | Hardware-in-the-loop / live-data shadow mode | Real controller hardware or live sensor feeds in the loop, but the RL policy does **not** actuate street signals |
| 4 | Field test | RL policy actuates real signals at ≥ 1 real intersection during a limited trial |
| 5 | Sustained deployment | RL controller in continuous operational use (≥ 1 month) with reported outcomes |

Supplementary flags (independent of VRL): `transfer_test` (evaluated on unseen scenarios/simulators), `robustness_test` (detector noise/failure, demand surges, incidents), `safety_constraints` (min green, pedestrian clearance, action masking).
