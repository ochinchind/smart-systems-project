from pathlib import Path

import pandas as pd

from slr import config
from slr.extraction import relative_improvement
from slr.ingest import parse_wos
from slr.project import first_author_surname, normalize_doi, normalize_title
from slr.screening import cohen_kappa, ft_final, ta_final, weighted_kappa
from slr.synthesis import _dl_random_effects

FIX = Path(__file__).parent / "fixtures"


def test_normalisers():
    assert normalize_doi("https://doi.org/10.1/ABC.") == "10.1/abc"
    assert normalize_doi("doi: 10.1/x") == "10.1/x"
    assert normalize_title("Deep <i>RL</i>: Traffic—Lights!") == "deep rl traffic lights"


def test_first_author_surname_formats():
    assert first_author_surname("Wei H.; Chen C.") == "wei"
    assert first_author_surname("Wei, Hua; Chen, C") == "wei"
    assert first_author_surname("H. Wei; C. Chen") == "wei"
    assert first_author_surname("Van der Berg J.-P.") == "van der berg"


def test_wos_tagged_parser():
    df = parse_wos(FIX / "wos_tagged_test.txt")
    assert len(df) == 1
    r = df.iloc[0]
    assert r["title"] == "TEST Tagged format reinforcement learning traffic signal record"
    assert r["authors"] == "Mu, M; Nu, N"
    assert r["doc_type"] == "article"


def test_kappa():
    assert cohen_kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]) == 1.0
    assert round(cohen_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]), 3) == 0.0
    assert weighted_kappa([0, 1, 2], [0, 1, 2]) == 1.0


def test_ta_final_is_conservative():
    assert ta_final({"assigned_to": "R1+R2", "r1_decision": "exclude", "r2_decision": "uncertain"}) == "uncertain"
    assert ta_final({"assigned_to": "R1+R2", "r1_decision": "exclude", "r2_decision": ""}) == "pending"
    assert ta_final({"assigned_to": "R1", "r1_decision": "e"}) == "exclude"
    assert ta_final({"assigned_to": "R1", "r1_decision": "e", "r1_confidence": "low"}).startswith("pending")
    assert ta_final({"assigned_to": "R1", "r1_decision": "e", "override_decision": "include"}) == "include"


def test_ft_final_requires_reason_and_consensus():
    assert ft_final({"retrieved": "N"})[0] == "not_retrieved"
    assert ft_final({"retrieved": "Y", "r1_decision": "exclude", "r2_decision": "include"})[0] == "pending"
    assert ft_final({"retrieved": "Y", "r1_decision": "exclude", "r1_reason": "E2",
                     "r2_decision": "include"})[0] == "conflict"
    assert ft_final({"retrieved": "Y", "r1_decision": "exclude", "r1_reason": "E2", "r2_decision": "include",
                     "consensus_decision": "exclude", "consensus_reason": "E2"})[:2] == ("exclude", "E2")


def test_relative_improvement_direction():
    assert relative_improvement("travel_time", "80", "100", "") == 20.0
    assert relative_improvement("throughput", "1100", "1000", "") == 10.0
    assert relative_improvement("queue_length", "120", "100", "") == -20.0
    assert relative_improvement("other", "1", "2", "7") == 7.0


def test_random_effects_homogeneous():
    import numpy as np
    r = _dl_random_effects(np.array([0.1, 0.1, 0.1]), np.array([0.01, 0.01, 0.01]))
    assert abs(r["log_rr"] - 0.1) < 1e-12 and r["tau2"] == 0.0


def test_config_consistency():
    assert list(config.EXCLUSION_REASONS)[0] == "E1"
    assert set(config.VRL_LABELS) == set(range(6))
