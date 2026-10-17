# Document 18 — Quality Assessment Framework (Step 18)

The five generic domains of the guideline, adapted to RL traffic-signal-control studies. Each item is scored **0 = No, 1 = Partial, 2 = Yes**; maximum **10**.

| Item | Domain | 2 = Yes | 1 = Partial | 0 = No |
|---|---|---|---|---|
| **QA1** | Research design | Objective stated **and** full MDP formulation given: state, action, reward, agent architecture (and, for MARL, coordination) | Objective clear, but one of state/action/reward is vague | Objective or RL formulation unclear |
| **QA2** | Data quality | Real road network **and** real or calibrated demand, fully described (source, period, volumes) | Synthetic network/demand that is fully described (reproducible), **or** real data that is poorly described | Network/demand not described |
| **QA3** | Reproducibility | Hyperparameters, training procedure and simulator/version reported **and** code or scenario files publicly available | Details reported but no code/scenario files | Insufficient details to re-implement |
| **QA4** | Validation | Compared with ≥ 1 non-RL adaptive baseline (actuated / Max-Pressure / SOTL / SCATS-SCOOT-like) **and** (a state-of-the-art RL baseline **or** a test on unseen scenarios **or** a field/HIL test) | Only fixed-time, or only one baseline, or only training scenarios | No baseline |
| **QA5** | Results reporting | Results over multiple runs/seeds **with** dispersion (SD/CI) **and** limitations discussed | One of the two | Neither |

## Thresholds (fixed a priori — do not change after seeing results)

| Total | Class |
|---|---|
| 8–10 | High |
| 5–7 | Moderate |
| 0–4 | Limited |

## Use of QA
* QA is **not** an exclusion criterion.
* Uses: (1) the interpretation in the Discussion section; (2) a sensitivity analysis that excludes Limited studies (`sensitivity_excl_limited_qa.csv`); (3) choosing the seed set for Wave 3 citation chaining (QA ≥ 8).

## Procedure
1. `python -m slr qa` creates `data/quality/quality_assessment.csv` (one row per included paper).
2. R1 fills `r1_QA1…r1_QA5`, R2 fills `r2_QA1…r2_QA5`, independently.
3. Re-run `python -m slr qa`. Items where the reviewers disagree are listed in `qa_conflicts`. Discuss them and fill `consensus_QAx`.
4. Report the linear weighted κ for each item (printed by the command) in the Methods section.
