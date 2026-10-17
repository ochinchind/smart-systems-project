"""Locked protocol parameters (Search Protocol v1.0) used by the pipeline.

Changing anything here after the search is locked is a protocol amendment:
record it in data/protocol/amendments.csv and docs/phase1_planning/06_Review_Protocol.md.
"""

PROTOCOL_VERSION = "1.0"

YEAR_MIN = 2019
YEAR_MAX = 2026

ALLOWED_DOC_TYPES = {"article", "conference_paper"}
ALLOWED_LANGUAGES = {"english"}

# Metadata priority when merging duplicates (lower = preferred).
SOURCE_PRIORITY = {"scopus": 0, "wos": 1, "ieee": 2, "other": 3}
SOURCE_LABELS = {
    "scopus": "Scopus",
    "wos": "Web of Science",
    "ieee": "IEEE Xplore",
    "other": "Other methods",
}
DATABASE_SOURCES = ("scopus", "wos", "ieee")

# Deduplication
FUZZY_TITLE_THRESHOLD = 0.93

# Screening
TA_DECISIONS = {"include", "exclude", "uncertain"}
TA_DECISION_ALIASES = {"i": "include", "e": "exclude", "u": "uncertain", "?": "uncertain"}
FT_DECISIONS = {"include", "exclude"}
CALIBRATION_FRACTION = 0.10
CALIBRATION_MIN = 50
RANDOM_SEED = 2026
KAPPA_TARGET = 0.60

# Exclusion reasons, in hierarchical order (Protocol §5).
EXCLUSION_REASONS = {
    "E1": "Wrong application (not road traffic signal control)",
    "E2": "Wrong method (RL is not the evaluated controller)",
    "E3": "Wrong publication type (review, survey, position paper, chapter)",
    "E4": "No empirical evaluation / no quantitative traffic outcome",
    "E5": "Outside date range",
    "E6": "Not peer-reviewed (preprint, thesis, poster, extended abstract)",
    "E7": "Not in English",
    "E8": "Duplicate record not detected at deduplication",
    "E9": "Full text not retrievable",
    "E10": "Insufficient technical information",
}

# Quality assessment (Document 18): 0 = No, 1 = Partial, 2 = Yes.
QA_ITEMS = {
    "QA1": "Research design: objective and RL formulation (state, action, reward, agents) clearly defined",
    "QA2": "Data quality: network and demand realistic and described",
    "QA3": "Reproducibility: training details, simulator/version, code or scenario files",
    "QA4": "Validation: appropriate baselines (non-RL adaptive + RL) or unseen-scenario / field test",
    "QA5": "Results reporting: multiple runs with dispersion and limitations discussed",
}
QA_SCORES = {0, 1, 2}
QA_CLASSES = [(8, 10, "High"), (5, 7, "Moderate"), (0, 4, "Limited")]

# Validation Realism Level (Documents 04-05).
VRL_LABELS = {
    0: "Synthetic simulation",
    1: "Real-geometry simulation",
    2: "Real-data simulation",
    3: "HIL / live-data shadow mode",
    4: "Field test",
    5: "Sustained deployment",
}

# Quantitative synthesis: metric -> direction ("lower" is better / "higher" is better).
METRIC_DIRECTION = {
    "travel_time": "lower",
    "waiting_time": "lower",
    "delay": "lower",
    "queue_length": "lower",
    "stops": "lower",
    "fuel": "lower",
    "co2": "lower",
    "emissions_other": "lower",
    "safety_conflicts": "lower",
    "throughput": "higher",
    "speed": "higher",
}
BASELINE_CLASSES = [
    "fixed_time", "actuated", "max_pressure", "sotl", "scats_scoot",
    "other_adaptive", "rl", "other",
]

# Meta-analysis feasibility rule (Document 26).
META_MIN_FAMILIES = 5

# Relevance score (used only to sort the screening list, never to decide).
RELEVANCE_TERMS_A = [
    "reinforcement learning", "q-learning", "deep q", "dqn", "actor-critic", "actor critic",
    "policy gradient", "proximal policy", "ppo", "multi-agent", "marl",
]
RELEVANCE_TERMS_B = [
    "traffic signal", "traffic light", "signalized intersection", "signalised intersection",
    "signal timing", "signal phase", "intersection", "signal control",
]
RELEVANCE_NEGATIVE = [
    "ramp metering", "wireless", "power system", "smart grid", "spectrum", "network traffic",
    "packet", "railway", "autonomous driving", "lane change", "routing",
]
