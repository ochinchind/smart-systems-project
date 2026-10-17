"""Steps 19-21: extraction codebook (single source of truth, exported to data/protocol/codebook.csv).

type: text | int | enum (one value) | multi (';'-separated values) | yn (Y/N) | vrl (0-5)
"""

from __future__ import annotations

import pandas as pd

from . import config

YN = ["Y", "N"]

TECHNICAL = [
    # A. Bibliographic (pre-filled from the search records)
    ("paper_id", "A", "all", "text", [], "Stable paper ID (P001...)"),
    ("authors", "A", "RQ1", "text", [], "Authors"),
    ("year", "A", "RQ1", "int", [], "Publication year"),
    ("title", "A", "-", "text", [], "Title"),
    ("venue", "A", "RQ1", "text", [], "Journal or conference"),
    ("venue_type", "A", "RQ1", "enum", ["journal", "conference"], "Venue type"),
    ("doi", "A", "-", "text", [], "DOI"),
    ("country_first_author", "A", "RQ1", "text", [], "Country of first author's affiliation (pre-filled guess, verify)"),
    ("study_location", "A", "RQ1", "text", [], "City/country of the studied network, or 'synthetic'"),
    # B. Application
    ("application_context", "B", "RQ1", "enum",
     ["isolated_intersection", "arterial_corridor", "grid_network", "real_urban_network", "other"],
     "Spatial setting of the controlled intersections"),
    ("n_intersections", "B", "RQ1", "int", [], "Largest number of RL-controlled intersections evaluated"),
    ("traffic_modes", "B", "RQ1;RQ6", "multi",
     ["private_vehicles", "pedestrians", "cyclists", "public_transport", "emergency_vehicles",
      "cav_connected_vehicles", "freight", "mixed"],
     "Road users explicitly modelled/prioritised"),
    ("objective_focus", "B", "RQ1", "multi",
     ["efficiency", "safety", "emissions_energy", "equity_fairness", "priority", "robustness"],
     "Objectives explicitly optimised"),
    # C. Technology / RL formulation
    ("rl_family", "C", "RQ2", "enum",
     ["tabular", "value_based_deep", "policy_gradient", "actor_critic", "model_based",
      "hierarchical", "meta_rl", "offline_rl", "llm_rl_hybrid", "other"],
     "RL algorithm family of the proposed method"),
    ("algorithm", "C", "RQ2", "text", [], "Named algorithm (e.g. DQN, D3QN, PPO, A2C, MAPPO)"),
    ("agent_architecture", "C", "RQ2", "enum",
     ["single_agent", "multi_agent_independent", "multi_agent_cooperative", "centralised_multi_intersection"],
     "Agent architecture"),
    ("coordination", "C", "RQ2", "enum",
     ["none", "neighbour_observation", "explicit_communication", "graph_attention", "pressure_based",
      "hierarchical", "other"],
     "Coordination mechanism between intersections"),
    ("state_repr", "C", "RQ2", "multi",
     ["queue_length", "waiting_time", "vehicle_count", "occupancy", "speed", "position_matrix_image",
      "pressure", "current_phase", "phase_duration", "cv_trajectory", "raw_camera", "other"],
     "State features"),
    ("action_type", "C", "RQ2", "enum",
     ["phase_selection", "phase_switch_keep", "phase_duration", "cycle_split", "offset", "other"],
     "Action definition"),
    ("reward_type", "C", "RQ2", "multi",
     ["queue_length", "waiting_time", "delay", "pressure", "throughput", "travel_time", "speed",
      "emissions", "safety", "composite", "other"],
     "Reward components"),
    ("function_approximator", "C", "RQ2", "enum",
     ["table", "mlp", "cnn", "rnn_lstm", "gnn", "attention_transformer", "llm", "other"],
     "Policy/value function approximator"),
    ("simulator", "C", "RQ3", "multi",
     ["sumo", "cityflow", "vissim", "aimsun", "paramics", "cbengine", "custom", "other", "none"],
     "Simulation environment(s)"),
    ("sensing_source", "C", "RQ5", "multi",
     ["loop_detector", "camera", "radar_lidar", "connected_vehicle", "simulator_ground_truth", "other"],
     "Sensing assumed or used for the state"),
    # D/F. Methodology and validation
    ("network_source", "F", "RQ3", "enum", ["synthetic", "real"], "Road network geometry"),
    ("demand_source", "F", "RQ3", "enum", ["synthetic", "real_dataset", "calibrated", "field_live"],
     "Traffic demand used in evaluation"),
    ("dataset_ids", "F", "RQ3;Step27", "text", [],
     "Benchmark datasets/scenarios, ';'-separated canonical names (e.g. jinan_3x4; hangzhou_4x4; ny_28x7; monaco; ingolstadt7; cologne8)"),
    ("baseline_classes", "F", "RQ3;RQ4", "multi", config.BASELINE_CLASSES, "Classes of baselines compared"),
    ("vrl", "F", "RQ3;RQ4", "vrl", [str(k) for k in config.VRL_LABELS], "Validation Realism Level 0-5 (highest reached)"),
    ("transfer_test", "F", "RQ3", "yn", YN, "Evaluated on unseen scenarios / other simulator"),
    ("robustness_test", "F", "RQ3;RQ5", "yn", YN, "Detector noise/failure, demand surge or incident tests"),
    ("safety_constraints", "F", "RQ5", "yn", YN, "Min green, clearance, action masking or other constraints enforced"),
    ("n_seeds", "F", "QA5", "text", [], "Number of independent runs/seeds ('NR' if not reported)"),
    ("code_available", "F", "QA3", "yn", YN, "Code publicly available"),
    # G. Conclusions
    ("key_findings", "G", "RQ4", "text", [], "Main findings (1-2 sentences)"),
    ("advantages", "G", "RQ5", "text", [], "Advantages claimed"),
    ("limitations_authors", "G", "RQ5", "text", [], "Limitations stated by the authors"),
    # H. Reviewer interpretation
    ("barriers", "H", "RQ5", "multi",
     ["sensing_data", "sim_to_real_gap", "safety_compliance", "robustness", "computation",
      "communication", "interpretability", "scalability", "multimodality", "training_cost_sample_efficiency",
      "regulation_institutional", "none_reported"],
     "Deployment barriers discussed or evident"),
    ("mitigations", "H", "RQ5", "text", [], "Mitigations proposed for the barriers"),
    ("reviewer_strength", "H", "RQ6", "text", [], "Main methodological strength (reviewer)"),
    ("reviewer_weakness", "H", "RQ6", "text", [], "Main weakness (reviewer)"),
    ("research_gap_note", "H", "RQ6", "text", [], "Gap this study reveals or leaves open"),
    # Dependence control (Step 27)
    ("study_family_id", "DEP", "Step27", "text", [],
     "Same experiments/project/dataset family -> same ID (e.g. F01). Default = paper_id"),
    ("campaign_id", "DEP", "Step27", "text", [], "Field campaign or shared experiment ID, if any"),
    ("extracted_by", "META", "-", "enum", ["R1", "R2"], "Extractor"),
    ("verified_by", "META", "-", "enum", ["R1", "R2", ""], "Verifier (20 % sample)"),
]

QUANTITATIVE = [
    ("entry_id", "E", "-", "text", [], "Q0001..."),
    ("paper_id", "E", "-", "text", [], "Paper ID"),
    ("scenario_id", "E", "Step27", "text", [], "Dataset/scenario canonical name for this number"),
    ("metric", "E", "RQ4", "enum", list(config.METRIC_DIRECTION) + ["other"], "Outcome metric"),
    ("rl_method_name", "E", "RQ4", "text", [], "Name of the proposed RL method"),
    ("rl_value", "E", "RQ4", "float", [], "Value for the proposed RL method"),
    ("baseline_name", "E", "RQ4", "text", [], "Baseline name as in the paper"),
    ("baseline_class", "E", "RQ4", "enum", config.BASELINE_CLASSES, "Baseline class"),
    ("baseline_value", "E", "RQ4", "float", [], "Value for the baseline"),
    ("reported_improvement_pct", "E", "RQ4", "float", [],
     "Use only if the paper gives the % improvement but not both raw values"),
    ("unit", "E", "RQ4", "text", [], "Unit (s, veh, veh/h, m, g...)"),
    ("rl_sd", "E", "Step26", "float", [], "SD/dispersion of RL value, if reported"),
    ("baseline_sd", "E", "Step26", "float", [], "SD of baseline value, if reported"),
    ("n_runs", "E", "Step26", "int", [], "Number of runs behind the values"),
    ("vrl", "E", "RQ4", "vrl", [str(k) for k in config.VRL_LABELS], "Validation level of this experiment (defaults to paper VRL)"),
    ("context", "E", "-", "text", [], "Demand level, peak/off-peak, test condition..."),
    ("source_location", "E", "audit", "text", [], "Page/table/figure, e.g. 'Table 4, p. 9'"),
    ("extracted_by", "META", "-", "enum", ["R1", "R2"], "Extractor"),
    ("verified_by", "META", "-", "enum", ["R1", "R2", ""], "Verifier (100 % of entries)"),
]


def codebook_frame() -> pd.DataFrame:
    rows = []
    for table, spec in (("technical", TECHNICAL), ("quantitative", QUANTITATIVE)):
        for field, section, rq, typ, allowed, desc in spec:
            rows.append({"table": table, "field": field, "section": section, "supports": rq,
                         "type": typ, "allowed_values": "; ".join(allowed), "description": desc})
    return pd.DataFrame(rows)


def validate(df: pd.DataFrame, spec) -> list[str]:
    """Return human-readable problems; empty cells are allowed (extraction in progress)."""
    problems = []
    for field, _, _, typ, allowed, _ in spec:
        if field not in df.columns:
            continue
        key = df.columns[0]
        for idx, v in df[field].items():
            v = str(v).strip()
            if not v:
                continue
            where = f"{df.at[idx, key]}.{field}={v!r}"
            if typ in ("enum", "yn") and allowed and v not in allowed:
                problems.append(f"{where}: not one of {allowed}")
            elif typ == "multi":
                bad = [x.strip() for x in v.split(";") if x.strip() and x.strip() not in allowed]
                if bad:
                    problems.append(f"{where}: unknown value(s) {bad}")
            elif typ == "vrl" and v not in allowed:
                problems.append(f"{where}: VRL must be 0-5")
            elif typ == "int" and not v.lstrip("-").isdigit():
                problems.append(f"{where}: integer expected")
            elif typ == "float":
                try:
                    float(v.replace(",", ".").rstrip("%"))
                except ValueError:
                    problems.append(f"{where}: number expected")
    return problems
