# Document 03 — Scope Statement (Step 3)

## Formal scope statement

> This systematic review investigates **peer-reviewed primary studies** concerning **reinforcement learning (RL)–based controllers** applied to **road traffic signals at one or more intersections**, for the purpose of **adaptively selecting or timing signal phases to improve traffic performance**, published between **1 January 2019 and the date of the final search (2026)**, with particular attention to **how realistically the controllers were validated (simulation → field)**.

## 3.1 Subject scope

The phenomenon studied is **learning-based adaptive signal control**: a controller that *learns* its policy (phase choice, phase duration, cycle length, green split or offset) through RL from a reward signal.

In scope:
* tabular RL (Q-learning, SARSA), deep value-based (DQN family), policy-gradient / actor–critic (A2C, A3C, PPO, DDPG, SAC…), multi-agent RL, hierarchical RL, meta-RL, offline RL, model-based RL;
* hybrid methods where RL is the decision layer (e.g., RL + graph neural network, RL + fuzzy rules, RL + Max-Pressure reward, LLM agents whose policy is refined with RL).

Out of scope:
* signal optimisation by non-RL methods only (genetic algorithms, MPC, fuzzy logic, supervised prediction) — unless RL is the evaluated controller;
* LLM/prompting-only controllers with no RL component;
* RL used only as a minor comparison baseline.

## 3.2 Application scope

In scope: urban and suburban **road intersections** (isolated, arterial corridor, grid/network), including signal control for mixed traffic, connected/automated vehicles, pedestrians, cyclists, public-transport or emergency-vehicle priority **when RL controls the signal**.

Out of scope: ramp metering only, variable speed limits only, lane-use control only, routing/navigation, autonomous-vehicle driving policies, railway/air/maritime traffic, telecommunications "traffic" and "signals".

## 3.3 Technology scope

Any sensing source (loop detectors, cameras, radar, connected-vehicle data, simulation ground truth) and any evaluation environment (SUMO, CityFlow, VISSIM, Aimsun, Paramics, custom simulators, hardware-in-the-loop, field).

## 3.4 Geographic scope

**No geographic restriction.** Country of authors and location of studied networks are extracted as variables (RQ1).

## 3.5 Publication period

**1 January 2019 – final search date (2026).**

Justification:
1. **Continuity with the previous SLR.** Noaeen et al. (2022) cover up to March 2020; starting in 2019 gives a deliberate one-year overlap to check consistency, and our focus (validation realism, deployment) is different.
2. **Technological shift.** 2019 is when open, large-scale RL-TSC tooling became standard (CityFlow released 2019; real-data benchmark datasets of Jinan/Hangzhou/New York; landmark DRL models PressLight, CoLight, FRAP published 2019). This made studies comparable and sharply increased publication volume.
3. **Deployment debate.** Sim-to-real, robustness and deployment-barrier papers appear from 2021 onwards; a 2019 start captures the full arc.

## 3.6 Publication type

| Type | Decision | Reason |
|---|---|---|
| Journal articles (incl. early access/articles in press) | **Include** | Peer-reviewed primary evidence |
| Full conference papers (proceedings, ≥ 4 pages) | **Include** | Key venues in this field are conferences (KDD, CIKM, AAAI, NeurIPS, ITSC) |
| Book chapters | Exclude | Rarely primary, inconsistent peer review |
| Reviews / surveys | Exclude from evidence base; **used for citation chaining (Wave 3) and Discussion** | Not primary studies |
| Preprints (arXiv etc.), theses, reports, patents, grey literature | Exclude | Not peer-reviewed; a preprint is replaced by its peer-reviewed version if one exists |
| Extended abstracts, posters, editorials | Exclude | Insufficient technical information |

Language: **English only** (documented as a limitation).
