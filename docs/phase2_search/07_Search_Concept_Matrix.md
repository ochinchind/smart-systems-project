# Document 07 — Search Concept Matrix (Step 7)

The topic is split into concepts. Synonyms are joined with OR inside a concept; the concepts are joined with AND.

| Concept | Role | Terms (OR-joined) | Used in |
|---|---|---|---|
| **A — Reinforcement learning** | Technology | "reinforcement learning" · "Q-learning" · "deep Q-network(s)" · DQN · "actor-critic" · "policy gradient" · "proximal policy optimization/optimisation" | Core (Wave 1) |
| **B — Traffic signal control** | Application | "traffic signal(s)" · "traffic light(s)" · "signalized/signalised intersection(s)" · "signal timing" · "signal phase(s)/phasing" · "adaptive signal control" | Core (Wave 1) |
| C — Deployment / realism | Target phenomenon (precision/targeting only) | "field test" · "field trial" · "real-world deployment" · deploy* · "sim-to-real" · sim2real · "hardware-in-the-loop" · "digital twin" · "real intersection" · "transfer learning" · "domain randomization" | Wave 2 & Wave 4 targeted searches |
| D — Expansion terms found during Wave 1 | Terminology expansion | SARSA · "temporal difference" · DDPG · "soft actor-critic" · A2C/A3C · MARL · "multi-agent learning" · "learning-based signal" · "traffic light controller" · "intersection controller" · "phase selection" | Wave 2 |
| E — Context (optional) | Context | urban · arterial · corridor · network · pedestrian · "public transport" · "emergency vehicle" · "connected vehicle" | Wave 4 gap-targeted |

## Combination logic

* **Core query (Wave 1):** `(A) AND (B)` in title/abstract/keywords, 2019–2026, articles + conference papers, English.
* Concept C is **not** used in the core query because it would remove the large simulation-only literature that is needed to answer RQ3/RQ4 (the gap itself is the object of study). It is used only to *add* recall for deployment studies (Wave 2/4).

## Design notes

* "signal control" alone was rejected: in the pilot it retrieves power-electronics and telecommunications records (low precision).
* "intersection" alone was rejected: too broad (vehicle intersection management without signals, set intersection in maths).
* Truncation is used where the database supports it inside phrases (Scopus, WoS); IEEE Xplore variants are written out in full (see Document 09).
