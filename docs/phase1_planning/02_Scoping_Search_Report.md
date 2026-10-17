# Document 02 — Preliminary Scoping Search Report (Step 2)

> **Important distinction.** This scoping search was used only to *design* the review (terminology, scope, existing reviews, likely gaps).
> None of the records found here are counted in the PRISMA flow. The formal evidence comes only from the locked database searches (Documents 09–12).

| Item | Value |
|---|---|
| Date | 17 Oct 2026 |
| Tool | General web search engine (exploratory, non-reproducible by design) |
| Queries run | 8 (listed in §1) |

## 1. Exploratory queries

1. systematic review reinforcement learning traffic signal control real-world deployment
2. reinforcement learning traffic signal control field deployment real intersection test 2023 2024
3. sim-to-real transfer reinforcement learning traffic signal control
4. survey deep reinforcement learning traffic signal control (Haydari & Yilmaz; Wei, Zheng, Gayah & Li)
5. benchmark traffic signal control reinforcement learning RESCO LibSignal CityFlow SUMO
6. multi-agent reinforcement learning traffic signal CoLight PressLight MPLight MA2C
7. "adaptive traffic signal control" reinforcement learning systematic review 2024 2025
8. field test / field trial deep reinforcement learning traffic signal controller real-world city
9. large language model traffic signal control LLMLight

## 2. Terminology and synonyms found

| Concept | Variants observed |
|---|---|
| Reinforcement learning | reinforcement learning, deep reinforcement learning (DRL/deep RL), multi-agent RL (MARL), Q-learning, deep Q-network (DQN, DDQN, D3QN), actor–critic (A2C, A3C), policy gradient, PPO / IPPO / MAPPO, DDPG, SAC, meta-RL, hierarchical RL, offline RL |
| Traffic signal | traffic signal control (TSC), adaptive traffic signal control (ATSC), traffic light control, intelligent traffic light, signalised/signalized intersection, signal timing / timing plan, signal phase / phase selection / phase duration, cycle length, green split, arterial coordination, network-level control |
| Deployment | real-world deployment, field test/trial, sim-to-real / sim2real, transfer, grounded action transformation, domain randomisation, hardware-in-the-loop, digital twin, real intersection |
| Emerging | large language model (LLM) agents for TSC (e.g., LLMLight), safe RL / action masking, robustness to detector failure |

## 3. Major existing reviews (to position our contribution)

| Review | Type | Coverage | Relation to our SLR |
|---|---|---|---|
| Noaeen et al. (2022), *Reinforcement learning in urban network traffic signal control: A systematic literature review*, Expert Systems with Applications | SLR | 160 articles, 1994 – Mar 2020, network-level | Closest prior SLR; we extend the period and add validation-realism coding |
| Haydari & Yilmaz (2022), *Deep Reinforcement Learning for Intelligent Transportation Systems: A Survey*, IEEE T-ITS 23(1) | Narrative survey | DRL in ITS incl. TSC | Background for taxonomy |
| Wei, Zheng, Gayah & Li (2019/2021), *A Survey on Traffic Signal Control Methods* (arXiv 1904.08117) / *Recent advances in RL for TSC* (SIGKDD Explorations) | Narrative survey | Classical and RL TSC | Background for method families |
| Zhang, Cui & Ma (2024), Transport Reviews 44(6) | Systematic review | RL-TSC with CAVs | Different focus (CAV) |
| Michailidis et al. (2025), *Traffic Signal Control via Reinforcement Learning: A Review on Applications and Innovations*, Infrastructures 10(5):114 | Review | High-impact RL-TSC methods | Recent; not deployment-centred |
| Chen, Fang & Sadeh (2022), *The Real Deal: A Review of Challenges and Opportunities in Moving Reinforcement Learning-Based Traffic Signal Control Systems Towards Reality* (ATT'22) | Position review | Deployment barriers | Motivates our RQ5; not systematic |
| TU Delft repository review on deep Q-learning controllers | Systematic review | DQN design choices | Narrow algorithm focus |

## 4. Dominant technologies, platforms and benchmarks

* **Simulators:** SUMO and CityFlow dominate; also VISSIM, Aimsun, CityFlow-based LibSignal, RESCO (SUMO-based benchmark: Ingolstadt, Cologne scenarios).
* **Benchmark datasets reused across many papers:** Jinan (3×4), Hangzhou (4×4), New York (16×3, 28×7), Shanghai, Monaco, Ingolstadt, Cologne. → strong dependence between publications (handled in Step 27).
* **Landmark method families:** single-intersection DQN; phase-competition (FRAP); pressure-based rewards (PressLight, MPLight, Advanced-XLight); graph/attention communication (CoLight, CoSLight); meta-RL (MetaLight); universal/attention models (AttendLight); MARL with actor–critic (MA2C); sim-to-real (UGAT, GAT-CASE23, PromptGAT); LLM agents (LLMLight).
* **Common baselines:** fixed-time (Webster), actuated, Max-Pressure, SOTL, SCOOT/SCATS-like adaptive systems (rare).

## 5. Typical study designs and quantitative variables

* Design: algorithm proposal + simulation experiment versus baselines; occasional real-data-calibrated simulation; very rare field tests.
* Variables: average travel time, average waiting time, average delay, queue length, throughput, number of stops, fuel/CO₂ emissions, safety surrogates (conflicts, TTC), training episodes / convergence.
* Dispersion (SD over random seeds) is inconsistently reported.

## 6. Potential research gaps already visible

1. Field validation (very few peer-reviewed live tests; scoping searches found mostly simulation work and position papers).
2. Robustness to detector noise/failure and partial observability.
3. Safety constraints, minimum green / pedestrian clearance compliance.
4. Multimodality (pedestrians, cyclists, public-transport priority, emergency vehicles).
5. Interpretability and acceptance by traffic engineers.
6. Comparison against strong adaptive baselines (Max-Pressure, SCATS/SCOOT) rather than fixed-time only.
7. Reproducibility (code, seeds, scenario files).

## 7. Sources consulted (scoping only)

- https://arxiv.org/abs/2206.11996 (Chen, Fang & Sadeh — The Real Deal)
- https://arxiv.org/abs/2103.16223 (Müller et al. — Towards Real-World Deployment of RL for TSC)
- https://arxiv.org/pdf/2206.10122 (Müller & Sabatelli — Safe and psychologically pleasant TSC with action masking)
- https://datalearner.com/academic/journal-papers/0957-4174/volumes-and-issues/403/paper-detail/18449 (Noaeen et al. SLR record)
- https://arxiv.org/abs/2005.00935 (Haydari & Yilmaz survey)
- https://arxiv.org/pdf/1904.08117 (Wei et al. survey)
- https://ideas.repec.org/a/taf/transr/v44y2024i6p1187-1208.html (Zhang, Cui & Ma 2024)
- https://doi.org/10.3390/infrastructures10050114 (Michailidis et al. 2025)
- https://trid.trb.org/View/2713949 (RL for ATSC: an overview)
- https://repository.tudelft.nl/file/File_dd04ad92-3d98-4c41-998e-45c1c3b6fe01 (TU Delft DQN review)
- https://arxiv.org/abs/2307.12388v2 (UGAT sim-to-real)
- https://ojs.aaai.org/index.php/AAAI/article/view/27758 (PromptGAT, AAAI 2024)
- https://digitalcommons.njit.edu/fac_pubs/2219 (Sim2Real transfer for TSC, CASE 2023)
- https://arxiv.org/pdf/2211.10649 (LibSignal)
- https://github.com/behradkoohy/RESCO (RESCO benchmark)
- https://arxiv.org/abs/1905.05717 (CoLight)
- https://arxiv.org/html/2405.17152v2 (CoSLight)
- https://arxiv.org/pdf/2204.12190 (UniComm)
- https://arxiv.org/abs/2312.16044v5 (LLMLight)
- https://arxiv.org/pdf/2008.11634 (Egea et al. — reward functions under real-world limitations)
- https://www.nature.com/articles/s41598-025-18449-1 (Hierarchical RL-based TSC, 2025)
- https://traffic-signal-control.github.io/ (community resource list)

> Bibliographic details of these items must be verified against the publisher record before being cited in the manuscript.
