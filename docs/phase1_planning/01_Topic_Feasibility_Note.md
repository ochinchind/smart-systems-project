# Document 01 — Topic Feasibility Note (Step 1)

| Item | Value |
|---|---|
| Project | Smart Traffic Lights That Learn |
| Authors | Rakhimzhanov Amangeldy, Nurkin Aidar |
| Document version | 1.0 |
| Status | Final (planning phase) |

## 1. Topic decomposition

| Level | Content |
|---|---|
| Broad field | Intelligent transportation systems / smart systems / artificial intelligence |
| Technology / method | Reinforcement learning (RL), including deep RL (DRL) and multi-agent RL (MARL) |
| Application / context | Traffic signal control (TSC) at urban signalised intersections and networks of intersections |
| Specific angle | Gap between simulation results and real-world (field) deployment |

## 2. Provisional title

**"Smart Traffic Lights That Learn: A Systematic Literature Review of Reinforcement Learning for Traffic Signal Control — From Simulation to Real Streets"**

Alternative (guideline template form):
"Reinforcement Learning for Adaptive Traffic Signal Control: A Systematic Review of Methods, Validation Realism, Performance, Deployment Barriers and Future Research Directions"

## 3. Motivation

* Most urban signals still run fixed-time or simple actuated plans that do not adapt to real demand.
* RL lets a signal controller learn a timing policy from interaction (sense → decide → act → reward), which makes it a textbook *smart system* (perception, decision, actuation in a closed loop).
* Hundreds of papers report reductions in waiting time, queue length and travel time **in simulation**, but published field deployments remain very rare (Chen, Fang & Sadeh 2022; Müller & Sabatelli 2022; see Document 02).
* There is no recent systematic review that codes **how realistic the validation of each study is** and links it to reported gains and deployment barriers.

## 4. Broad research problem

Why do RL-based traffic signal controllers that perform well in simulation rarely reach real streets, and what evidence exists on methods, validation practice, performance and deployment barriers that could close this gap?

## 5. Feasibility questions (guideline Step 1)

| # | Question | Assessment |
|---|---|---|
| 1 | Enough published research? | **Yes.** The topic is very active (KDD, CIKM, AAAI, NeurIPS, IEEE T-ITS, IEEE ITSC, Transportation Research Part C, Expert Systems with Applications…). An earlier SLR (Noaeen et al., 2022) already found 160 network-level articles up to March 2020 alone. |
| 2 | Scientifically important? | **Yes.** Congestion costs time, fuel, emissions and safety; signal control is a cheap lever because the infrastructure already exists. |
| 3 | Similar recent SLR published? | **Partly.** Noaeen et al. (2022, ESWA) — systematic, but corpus ends March 2020 and focus is network-level. Haydari & Yilmaz (2022, IEEE T-ITS) — narrative survey of DRL in ITS. Zhang, Cui & Ma (2024, Transport Reviews) — focus on connected/automated vehicles. Michailidis et al. (2025, Infrastructures) — review of high-impact methods. Chen, Fang & Sadeh (2022) — position paper on deployment barriers, not systematic. |
| 4 | Meaningful new contribution? | **Yes.** (a) covers 2019–2026, including the sim-to-real, LLM-based and safety-constrained work published after 2022; (b) introduces an explicit **Validation Realism Level (VRL 0–5)** coding of every study; (c) relates reported improvements to the baseline strength and validation realism; (d) controls double counting of shared benchmark datasets (Study Family IDs). |
| 5 | Can the topic be defined for systematic searching? | **Yes.** Two well-delimited concepts (RL × traffic signals) with stable vocabulary; see Document 07. |
| 6 | Quantitative / methodological comparison possible? | **Yes, descriptively.** Most papers report average waiting time, queue length, travel time or delay against fixed-time / actuated / Max-Pressure baselines, so relative improvement can be computed. A formal meta-analysis is unlikely to be appropriate (heterogeneous scenarios, variance rarely reported); see Document 26. |
| 7 | Important gaps likely? | **Yes.** Field validation, robustness to sensor failure, safety, pedestrians/cyclists/public transport, interpretability and regulatory compliance. |

## 6. Preliminary keywords

reinforcement learning; deep reinforcement learning; multi-agent reinforcement learning; Q-learning; deep Q-network (DQN); actor–critic; policy gradient; PPO; traffic signal control; traffic light control; adaptive traffic signal control; signalised/signalized intersection; signal timing; signal phase; sim-to-real; field deployment; real-world deployment.

## 7. Preliminary databases

Core: **Scopus**, **Web of Science Core Collection**, **IEEE Xplore**.
Supplementary (not counted as databases in PRISMA): Google Scholar and publisher pages for citation chaining, and ACM Digital Library as a cross-check for KDD/CIKM papers.

## 8. Review period

**1 January 2019 – date of the final search (2026).** Justification is given in Document 03 §3.5.

## 9. Expected contribution

1. An up-to-date, reproducible map of RL-for-TSC research 2019–2026.
2. A taxonomy of RL formulations (state, action, reward, agent architecture, algorithm family).
3. The first systematic coding of **validation realism** (simulation → calibrated simulation → hardware-in-the-loop → field test → sustained operation).
4. A descriptive quantitative synthesis of reported improvements, stratified by baseline type and validation realism, with dependence control.
5. A structured catalogue of deployment barriers and a prioritised research agenda.
