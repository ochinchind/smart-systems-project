"""End-to-end test of the SLR pipeline on synthetic fixture exports (not review evidence)."""

import shutil
from pathlib import Path

import pandas as pd
import pytest

from slr import dedup, extraction, ingest, prisma, quality, screening, synthesis, workbook
from slr.project import Project, read_csv, write_csv

FIX = Path(__file__).parent / "fixtures"
PROTOCOL = Path(__file__).parents[1] / "data" / "protocol"


@pytest.fixture
def project(tmp_path):
    for src, name in (("scopus", "scopus_wave1_test.csv"), ("wos", "wos_wave1_test.txt"),
                      ("ieee", "ieee_wave1_test.csv"), ("other", "citation_chaining_wave3_test.csv")):
        d = tmp_path / "data" / "raw" / src
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy(FIX / name, d / name)
    shutil.copytree(PROTOCOL, tmp_path / "data" / "protocol")
    return Project(tmp_path)


def _fill(path, key, values: dict):
    df = read_csv(path)
    for k, cols in values.items():
        for c, v in cols.items():
            df.loc[df[key] == k, c] = v
    write_csv(df, path)


def _rid(project, title_start):
    m = read_csv(project.master_records)
    hits = m[m["title"].str.startswith(title_start)]
    return list(hits["record_id"])


def test_full_pipeline(project):
    raw = ingest.ingest(project)
    assert len(raw) == 15
    assert raw.groupby("source").size().to_dict() == {"ieee": 3, "other": 2, "scopus": 5, "wos": 5}
    assert set(raw.loc[raw["source"] == "other", "wave"]) == {"3"}

    s = dedup.deduplicate(project)
    assert s["unique"] == 11 and s["duplicates_removed"] == 4
    assert s["removed_protocol_filter"] == 3  # review, 2017, Spanish
    master = read_csv(project.master_records)
    a = master[master["doi"] == "10.9999/test.0001"].iloc[0]
    assert a["sources"] == "scopus; wos; ieee; other" and a["origin"] == "database"
    # conference + journal version with different DOIs must NOT be merged automatically
    assert len(_rid(project, "TEST Sim-to-real")) == 2
    cand = read_csv(project.dedup_candidates)
    assert len(cand) == 2  # graph-attention spelling variant + sim-to-real pair

    # reviewer confirms the spelling variant is a duplicate, rejects the conference/journal pair
    cand.loc[cand["title_a"].str.contains("Graph"), "is_duplicate"] = "Y"
    cand.loc[cand["title_a"].str.contains("Sim-to-real"), "is_duplicate"] = "N"
    write_csv(cand, project.dedup_candidates)
    s = dedup.deduplicate(project)
    assert s["unique"] == 10 and s["pending_fuzzy_pairs"] == 0
    assert s["eligible_for_screening"] == 7

    st = screening.build_ta_sheet(project)
    assert st["records"] == 7 and st["calibration_records"] == 7
    ta = read_csv(project.ta_sheet)
    for rid in ta["record_id"]:
        excl = ta.loc[ta["record_id"] == rid, "title"].iloc[0].startswith("TEST PPO")
        _fill(project.ta_sheet, "record_id", {rid: {
            "r1_decision": "E" if excl else "I", "r2_decision": "exclude" if excl else "uncertain"}})
    st = screening.build_ta_sheet(project)  # re-run keeps reviewer input
    assert st["final_decisions"] == {"include": 6, "exclude": 1}
    assert st["kappa_3class"] is not None

    screening.build_ft_sheet(project)
    ft = read_csv(project.ft_sheet)
    assert len(ft) == 6
    vals = {}
    for _, r in ft.iterrows():
        t = r["title"]
        if t.startswith("TEST Sim-to-real") and r["year"] == "2024":
            vals[r["record_id"]] = {"retrieved": "N"}
        elif t.startswith("TEST Graph"):
            vals[r["record_id"]] = {"retrieved": "Y", "r1_decision": "exclude", "r1_reason": "E10",
                                    "r2_decision": "exclude", "r2_reason": "E4"}
        else:
            vals[r["record_id"]] = {"retrieved": "Y", "r1_decision": "include", "r2_decision": "include"}
    _fill(project.ft_sheet, "record_id", vals)
    out = screening.build_ft_sheet(project)
    assert out["exclusion_reasons"] == {"E4": 1}  # hierarchy picks the first applicable code
    inc = read_csv(project.included)
    assert list(inc["paper_id"]) == ["P001", "P002", "P003", "P004"]

    # extraction
    extraction.build_technical_sheet(project)
    tech = read_csv(project.technical)
    tech["rl_family"] = ["value_based_deep", "actor_critic", "value_based_deep", "offline_rl"]
    tech["vrl"] = ["2", "1", "4", "2"]
    tech["simulator"] = ["sumo", "cityflow; sumo", "sumo", "none"]
    tech["traffic_modes"] = ["private_vehicles", "private_vehicles; pedestrians", "private_vehicles", ""]
    tech["barriers"] = ["sim_to_real_gap", "scalability; communication", "safety_compliance", "sensing_data"]
    tech["dataset_ids"] = ["jinan_3x4", "jinan_3x4; hangzhou_4x4", "", ""]
    tech.loc[2, "study_family_id"] = "P001"  # same project as P001
    write_csv(tech, project.technical)
    assert extraction.build_technical_sheet(project) == []

    q = pd.DataFrame([
        {"paper_id": "P001", "metric": "travel_time", "rl_value": "80", "baseline_class": "fixed_time",
         "baseline_value": "100", "unit": "s", "source_location": "Table 3"},
        {"paper_id": "P002", "metric": "throughput", "rl_value": "1100", "baseline_class": "max_pressure",
         "baseline_value": "1000", "unit": "veh/h", "source_location": "Fig. 5"},
        {"paper_id": "P003", "metric": "travel_time", "rl_value": "90", "baseline_class": "fixed_time",
         "baseline_value": "100", "unit": "s", "source_location": "Table 2"},
        {"paper_id": "P004", "metric": "waiting_time", "reported_improvement_pct": "12.5",
         "baseline_class": "actuated", "unit": "s", "source_location": ""},
    ])
    write_csv(q, project.quantitative)
    problems = extraction.build_quantitative_sheet(project)
    assert any("source_location missing" in p for p in problems)
    q = read_csv(project.quantitative)
    assert list(q["entry_id"]) == ["Q0001", "Q0002", "Q0003", "Q0004"]
    assert list(q["relative_improvement_pct"]) == ["20", "10", "10", "12.5"]
    assert q.loc[2, "study_family_id"] == "P001"

    # QA
    quality.build_qa_sheet(project)
    qa = read_csv(project.qa_sheet)
    for qi in ("QA1", "QA2", "QA3", "QA4", "QA5"):
        qa[f"r1_{qi}"] = "2"
        qa[f"r2_{qi}"] = "2"
    qa.loc[0, "r2_QA5"] = "1"  # conflict on one item
    write_csv(qa, project.qa_sheet)
    res = quality.build_qa_sheet(project)
    assert res["conflicts"] == [["P001", "QA5"]]
    assert res["classes"] == {"High": 3}

    # PRISMA
    c = prisma.run(project)
    assert c["db_identified"] == 13 and c["other_identified"] == 2
    assert c["db_duplicates"] == 4 and c["other_duplicates"] == 1  # 4 = 3 exact + 1 manual fuzzy
    assert c["database_screened"] == 6 and c["database_ta_excluded"] == 1
    assert c["database_sought"] == 5 and c["database_not_retrieved"] == 1
    assert c["database_assessed"] == 4 and c["database_excluded_by_reason"] == {"E4": 1}
    assert c["reports_included"] == 4 and c["studies_included"] == 3
    assert (project.outputs_dir / "prisma" / "prisma_flow.png").exists()

    # synthesis + workbook
    rep = synthesis.run(project)
    text = rep.read_text()
    assert "Included reports: **4**" in text and "independent study families: **3**" in text
    fam = read_csv(project.outputs_dir / "synthesis" / "tables" / "ri_by_metric_baseline_family.csv")
    tt = fam[(fam["metric"] == "travel_time") & (fam["baseline_class"] == "fixed_time")].iloc[0]
    assert tt["n_values"] == "1" and float(tt["median"]) == 15.0  # P001+P003 collapsed to one family
    assert (project.outputs_dir / "synthesis" / "figures" / "fig_vrl_distribution.png").exists()
    assert (project.outputs_dir / "synthesis" / "taxonomy.md").exists()
    path = workbook.build(project)
    sheets = pd.ExcelFile(path).sheet_names
    assert len(sheets) == 15 and sheets[0] == "Search_Log"
