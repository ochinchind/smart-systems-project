"""Steps 22-27: taxonomy, method comparison, bibliometrics, quantitative synthesis,
meta-analysis feasibility and dependence control.

Every table is computed from data/extraction/*.csv; nothing is typed in by hand.
Quantitative statistics are reported twice: per evidence entry and per study family
(one value per family = median of its entries), the latter being the primary analysis.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config
from .project import Project, read_csv, split_multi, to_float, to_int, write_csv

PALETTE = ["#2a6f97", "#e07a5f", "#3d9970", "#f2a541", "#8e6c8a", "#5fa8d3", "#b5838d", "#6d6875",
           "#81b29a", "#c9ada7"]
MAIN_METRICS = ["travel_time", "waiting_time", "delay", "queue_length", "throughput"]


# ------------------------------------------------------------------ helpers

def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df is None or df.empty:
        return "_No data yet._\n"
    df = df.head(max_rows)
    cols = [str(c) for c in df.columns]
    fmt = lambda v: (f"{v:.1f}" if isinstance(v, float) and not math.isnan(v) else
                     ("" if isinstance(v, float) else str(v)).replace("|", "/"))
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines) + "\n"


def count_single(df: pd.DataFrame, col: str, label: str | None = None) -> pd.DataFrame:
    s = df[col].replace("", "not_reported")
    out = s.value_counts().rename_axis(label or col).reset_index(name="n_papers")
    out["percent"] = (100 * out["n_papers"] / max(len(df), 1)).round(1)
    return out


def count_multi(df: pd.DataFrame, col: str, label: str | None = None) -> pd.DataFrame:
    vals = df[col].map(split_multi)
    exploded = vals.explode().dropna()
    out = exploded.value_counts().rename_axis(label or col).reset_index(name="n_papers")
    out["percent"] = (100 * out["n_papers"] / max(len(df), 1)).round(1)
    n_missing = int((vals.map(len) == 0).sum())
    if n_missing:
        out = pd.concat([out, pd.DataFrame([{label or col: "not_reported", "n_papers": n_missing,
                                              "percent": round(100 * n_missing / len(df), 1)}])])
    return out


def describe(values: list[float]) -> dict:
    a = np.array([v for v in values if v is not None and not math.isnan(v)], dtype=float)
    if len(a) == 0:
        return {k: np.nan for k in ("min", "q1", "median", "q3", "max", "mean", "sd")}
    return {"min": a.min(), "q1": np.percentile(a, 25), "median": np.median(a),
            "q3": np.percentile(a, 75), "max": a.max(), "mean": a.mean(),
            "sd": a.std(ddof=1) if len(a) > 1 else np.nan}


def _savefig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _barh(df, label_col, value_col, title, path, color=PALETTE[0]):
    if df.empty:
        return
    d = df.iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 0.35 * len(d) + 1.2))
    ax.barh(d[label_col].astype(str), d[value_col], color=color)
    for y, v in enumerate(d[value_col]):
        ax.text(v, y, f" {v}", va="center", fontsize=8)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("Number of papers")
    ax.spines[["top", "right"]].set_visible(False)
    _savefig(fig, path)


# ------------------------------------------------------------------ loading

def load(project: Project) -> tuple[pd.DataFrame, pd.DataFrame]:
    tech = read_csv(project.technical)
    quant = read_csv(project.quantitative)
    qa = read_csv(project.qa_sheet)
    if tech.empty:
        return tech, quant
    tech["year_i"] = tech["year"].map(to_int)
    tech["vrl_i"] = tech["vrl"].map(to_int)
    if not qa.empty:
        qa_idx = qa.set_index("paper_id")
        tech["qa_total"] = tech["paper_id"].map(qa_idx["qa_total"]).fillna("")
        tech["qa_class"] = tech["paper_id"].map(qa_idx["qa_class"]).fillna("")
    else:
        tech["qa_total"], tech["qa_class"] = "", ""
    tech.loc[tech["study_family_id"] == "", "study_family_id"] = tech["paper_id"]
    if not quant.empty:
        quant["ri"] = quant["relative_improvement_pct"].map(to_float)
        quant = quant[quant["paper_id"].isin(tech["paper_id"])].copy()
        quant["qa_class"] = quant["paper_id"].map(tech.set_index("paper_id")["qa_class"])
        quant["vrl_i"] = quant["vrl_effective"].map(to_int)
    return tech, quant


# ------------------------------------------------------------------ Step 24

def bibliometrics(tech: pd.DataFrame, out: Path) -> dict[str, pd.DataFrame]:
    t = {}
    years = list(range(config.YEAR_MIN, config.YEAR_MAX + 1))
    py = tech.groupby(["year_i", "venue_type"]).size().unstack(fill_value=0).reindex(years, fill_value=0)
    py["total"] = py.sum(axis=1)
    t["papers_per_year"] = py.reset_index().rename(columns={"year_i": "year"})
    t["venues_top15"] = tech["venue"].value_counts().head(15).rename_axis("venue").reset_index(name="n_papers")
    t["venue_type"] = count_single(tech, "venue_type")
    t["countries"] = count_single(tech, "country_first_author", "country")
    t["application_context"] = count_single(tech, "application_context")
    t["traffic_modes"] = count_multi(tech, "traffic_modes")
    t["objective_focus"] = count_multi(tech, "objective_focus")
    t["rl_family"] = count_single(tech, "rl_family")
    t["algorithms_top15"] = tech["algorithm"].str.strip().replace("", "not_reported").value_counts() \
        .head(15).rename_axis("algorithm").reset_index(name="n_papers")
    t["agent_architecture"] = count_single(tech, "agent_architecture")
    t["coordination"] = count_single(tech, "coordination")
    t["state_repr"] = count_multi(tech, "state_repr")
    t["action_type"] = count_single(tech, "action_type")
    t["reward_type"] = count_multi(tech, "reward_type")
    t["function_approximator"] = count_single(tech, "function_approximator")
    t["simulator"] = count_multi(tech, "simulator")
    t["network_source"] = count_single(tech, "network_source")
    t["demand_source"] = count_single(tech, "demand_source")
    t["baseline_classes"] = count_multi(tech, "baseline_classes")
    vrl = tech["vrl_i"].value_counts().reindex(list(config.VRL_LABELS), fill_value=0)
    t["vrl"] = pd.DataFrame({"vrl": vrl.index, "label": [config.VRL_LABELS[k] for k in vrl.index],
                             "n_papers": vrl.values,
                             "percent": (100 * vrl.values / max(len(tech), 1)).round(1)})
    flags = []
    for f in ("transfer_test", "robustness_test", "safety_constraints", "code_available"):
        flags.append({"flag": f, "yes": int((tech[f] == "Y").sum()), "no": int((tech[f] == "N").sum()),
                      "not_coded": int((~tech[f].isin(["Y", "N"])).sum())})
    t["validation_flags"] = pd.DataFrame(flags)
    t["barriers"] = count_multi(tech, "barriers")
    if "qa_class" in tech:
        t["qa_classes"] = count_single(tech, "qa_class")
    for name, df in t.items():
        write_csv(df, out / "tables" / f"{name}.csv")

    figs = out / "figures"
    if tech["year_i"].notna().any():
        fig, ax = plt.subplots(figsize=(7.5, 3.6))
        bottom = np.zeros(len(years))
        for i, col in enumerate([c for c in py.columns if c != "total"]):
            ax.bar(years, py[col].values, bottom=bottom, label=col or "not coded", color=PALETTE[i % 10])
            bottom += py[col].values
        ax.set_xticks(years)
        ax.set_ylabel("Number of papers")
        ax.set_title("Included papers per year (RQ1)", fontsize=10)
        ax.legend(frameon=False, fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        _savefig(fig, figs / "fig_papers_per_year.png")

        fam = tech.assign(rl_family=tech["rl_family"].replace("", "not_coded"))
        ct = pd.crosstab(fam["year_i"], fam["rl_family"]).reindex(years, fill_value=0)
        fig, ax = plt.subplots(figsize=(7.5, 3.8))
        bottom = np.zeros(len(years))
        for i, col in enumerate(ct.columns):
            ax.bar(years, ct[col].values, bottom=bottom, label=col, color=PALETTE[i % 10])
            bottom += ct[col].values
        ax.set_xticks(years)
        ax.set_title("RL algorithm families over time (RQ2)", fontsize=10)
        ax.legend(frameon=False, fontsize=7, ncol=2)
        ax.spines[["top", "right"]].set_visible(False)
        _savefig(fig, figs / "fig_rl_family_by_year.png")

    vr = t["vrl"]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar([f"VRL{k}\n{l}" for k, l in zip(vr["vrl"], vr["label"])], vr["n_papers"],
           color=[PALETTE[0]] * 3 + [PALETTE[3]] + [PALETTE[2]] * 2)
    ax.set_title("Validation Realism Level of included studies (RQ3)", fontsize=10)
    ax.tick_params(axis="x", labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    _savefig(fig, figs / "fig_vrl_distribution.png")

    _barh(t["simulator"], "simulator", "n_papers", "Simulators (RQ3)", figs / "fig_simulators.png")
    _barh(t["barriers"], "barriers", "n_papers", "Deployment barriers (RQ5)", figs / "fig_barriers.png", PALETTE[1])
    _barh(t["baseline_classes"], "baseline_classes", "n_papers", "Baseline classes (RQ3/RQ4)",
          figs / "fig_baselines.png", PALETTE[2])

    hm = pd.crosstab(tech["rl_family"].replace("", "not_coded"), tech["vrl_i"]).reindex(
        columns=list(config.VRL_LABELS), fill_value=0)
    if not hm.empty:
        fig, ax = plt.subplots(figsize=(6.5, 0.45 * len(hm) + 1.5))
        ax.imshow(hm.values, cmap="Blues", aspect="auto")
        ax.set_xticks(range(len(hm.columns)), [f"VRL{c}" for c in hm.columns])
        ax.set_yticks(range(len(hm.index)), hm.index)
        for i in range(hm.shape[0]):
            for j in range(hm.shape[1]):
                ax.text(j, i, hm.values[i, j], ha="center", va="center", fontsize=8,
                        color="white" if hm.values[i, j] > hm.values.max() / 2 else "black")
        ax.set_title("RL family × Validation Realism Level", fontsize=10)
        _savefig(fig, figs / "fig_heatmap_family_vrl.png")
    return t


# ------------------------------------------------------------------ Step 27 (needed by 25/26)

def family_level(quant: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """One value per study family and cell: the median of the family's entries."""
    q = quant[quant["ri"].notna()]
    return q.groupby(keys + ["study_family_id"], as_index=False).agg(
        ri=("ri", "median"), n_entries=("ri", "size"), papers=("paper_id", lambda s: ";".join(sorted(set(s)))))


def dependence(tech: pd.DataFrame, quant: pd.DataFrame, out: Path) -> dict[str, pd.DataFrame]:
    t = {}
    fam = tech.groupby("study_family_id").agg(
        n_reports=("paper_id", "size"), papers=("paper_id", lambda s: "; ".join(s)),
        datasets=("dataset_ids", lambda s: "; ".join(sorted({d for v in s for d in split_multi(v)})))
    ).reset_index()
    if not quant.empty:
        ent = quant.groupby("study_family_id").size()
        fam["n_quant_entries"] = fam["study_family_id"].map(ent).fillna(0).astype(int)
        total = max(int(fam["n_quant_entries"].sum()), 1)
        fam["share_of_entries_pct"] = (100 * fam["n_quant_entries"] / total).round(1)
        fam["dominant_family_gt10pct"] = np.where(fam["share_of_entries_pct"] > 10, "Y", "N")
    t["study_families"] = fam.sort_values("n_reports", ascending=False)
    ds = tech[["paper_id", "study_family_id", "dataset_ids"]].copy()
    ds["dataset"] = ds["dataset_ids"].map(split_multi)
    ds = ds.explode("dataset").dropna(subset=["dataset"])
    t["dataset_reuse"] = ds.groupby("dataset").agg(
        n_papers=("paper_id", "nunique"), n_families=("study_family_id", "nunique")
    ).reset_index().sort_values("n_papers", ascending=False)
    for name, df in t.items():
        write_csv(df, out / "tables" / f"{name}.csv")
    return t


# ------------------------------------------------------------------ Step 25

def quantitative(quant: pd.DataFrame, out: Path) -> dict[str, pd.DataFrame]:
    t = {}
    q = quant[quant["ri"].notna()]
    if q.empty:
        return t

    def stats(df, keys, level):
        rows = []
        for k, g in df.groupby(keys):
            k = k if isinstance(k, tuple) else (k,)
            d = describe(list(g["ri"]))
            rows.append({**dict(zip(keys, k)), "level": level, "n_values": len(g),
                         "n_papers": g["papers"].str.split(";").explode().nunique() if "papers" in g
                         else g["paper_id"].nunique(),
                         "n_families": g["study_family_id"].nunique(), **{x: round(v, 2) for x, v in d.items()}})
        return pd.DataFrame(rows)

    keys = ["metric", "baseline_class"]
    t["ri_by_metric_baseline_family"] = stats(family_level(q, keys), keys, "family")
    t["ri_by_metric_baseline_entry"] = stats(q, keys, "entry")
    keys_v = ["metric", "vrl_effective"]
    t["ri_by_metric_vrl_family"] = stats(family_level(q, keys_v), keys_v, "family")
    hq = q[q["qa_class"] != "Limited"]
    t["sensitivity_excl_limited_qa"] = stats(family_level(hq, keys), keys, "family (QA != Limited)") \
        if not hq.empty else pd.DataFrame()
    for name, df in t.items():
        write_csv(df, out / "tables" / f"{name}.csv")

    figs = out / "figures"
    fl = family_level(q, keys)
    metrics = [m for m in MAIN_METRICS if m in set(fl["metric"])]
    if metrics:
        fig, axes = plt.subplots(1, len(metrics), figsize=(3.2 * len(metrics), 3.6), sharey=True, squeeze=False)
        for ax, m in zip(axes[0], metrics):
            sub = fl[fl["metric"] == m]
            classes = [c for c in config.BASELINE_CLASSES if c in set(sub["baseline_class"])]
            data = [sub.loc[sub["baseline_class"] == c, "ri"].values for c in classes]
            ax.boxplot(data, showfliers=True)
            ax.set_xticks(range(1, len(classes) + 1), classes, rotation=45, ha="right", fontsize=7)
            for i, d in enumerate(data, start=1):
                ax.scatter(np.random.default_rng(0).normal(i, 0.05, len(d)), d, s=8, alpha=0.6, color=PALETTE[0])
            ax.axhline(0, color="#999999", lw=0.8)
            ax.set_title(m.replace("_", " "), fontsize=9)
        axes[0][0].set_ylabel("Relative improvement of RL (%)\n(one point per study family)")
        fig.suptitle("Reported improvement by baseline class (RQ4)", fontsize=10)
        _savefig(fig, figs / "fig_ri_by_baseline.png")

        fv = family_level(q, keys_v)
        fv["vrl_i"] = fv["vrl_effective"].map(to_int)
        fv = fv[fv["metric"].isin(metrics) & fv["vrl_i"].notna()]
        if not fv.empty:
            fig, ax = plt.subplots(figsize=(6.5, 3.6))
            for i, m in enumerate(metrics):
                sub = fv[fv["metric"] == m]
                ax.scatter(sub["vrl_i"] + (i - len(metrics) / 2) * 0.08, sub["ri"], s=14, label=m,
                           color=PALETTE[i % 10], alpha=0.75)
            ax.set_xticks(list(config.VRL_LABELS), [f"VRL{k}" for k in config.VRL_LABELS])
            ax.axhline(0, color="#999999", lw=0.8)
            ax.set_ylabel("Relative improvement (%)")
            ax.set_title("Reported improvement vs validation realism (RQ4)", fontsize=10)
            ax.legend(frameon=False, fontsize=7)
            ax.spines[["top", "right"]].set_visible(False)
            _savefig(fig, figs / "fig_ri_vs_vrl.png")
    return t


# ------------------------------------------------------------------ Step 26

def _dl_random_effects(y: np.ndarray, v: np.ndarray) -> dict:
    w = 1 / v
    fixed = np.sum(w * y) / np.sum(w)
    qstat = float(np.sum(w * (y - fixed) ** 2))
    dfree = len(y) - 1
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (qstat - dfree) / c) if c > 0 else 0.0
    wr = 1 / (v + tau2)
    est = np.sum(wr * y) / np.sum(wr)
    se = math.sqrt(1 / np.sum(wr))
    i2 = max(0.0, (qstat - dfree) / qstat) * 100 if qstat > 0 else 0.0
    return {"log_rr": est, "se": se, "tau2": tau2, "Q": qstat, "I2_pct": i2}


def meta_feasibility(quant: pd.DataFrame, out: Path) -> pd.DataFrame:
    """Pre-specified rule (Document 26): a cell (metric x baseline class) is eligible for an
    exploratory random-effects meta-analysis only if >= META_MIN_FAMILIES independent study
    families report means AND dispersion AND n_runs in a single unit."""
    if quant.empty:
        return pd.DataFrame()
    q = quant.copy()
    for c in ("rl_value", "baseline_value", "rl_sd", "baseline_sd"):
        q[c + "_f"] = q[c].map(to_float)
    q["n_f"] = q["n_runs"].map(to_int)
    q["has_disp"] = q[["rl_value_f", "baseline_value_f", "rl_sd_f", "baseline_sd_f", "n_f"]].notna().all(axis=1) \
        & (q["n_f"].fillna(0) > 1) & (q["rl_value_f"] > 0) & (q["baseline_value_f"] > 0)
    rows = []
    for (m, b), g in q.groupby(["metric", "baseline_class"]):
        gd = g[g["has_disp"]]
        units = set(gd["unit"].str.strip().str.lower()) - {""}
        n_fam = gd["study_family_id"].nunique()
        feasible = n_fam >= config.META_MIN_FAMILIES and len(units) <= 1 and m in config.METRIC_DIRECTION
        row = {"metric": m, "baseline_class": b, "families_total": g["study_family_id"].nunique(),
               "families_with_dispersion": n_fam, "units": "; ".join(sorted(units)),
               "meta_analysis_feasible": "Y" if feasible else "N"}
        if feasible:
            gd = gd.assign(
                y=np.log(gd["rl_value_f"] / gd["baseline_value_f"]),
                v=gd["rl_sd_f"] ** 2 / (gd["n_f"] * gd["rl_value_f"] ** 2)
                + gd["baseline_sd_f"] ** 2 / (gd["n_f"] * gd["baseline_value_f"] ** 2))
            per_fam = gd.groupby("study_family_id").agg(y=("y", "mean"), v=("v", "mean"))
            per_fam = per_fam[per_fam["v"] > 0]
            if len(per_fam) >= config.META_MIN_FAMILIES:
                r = _dl_random_effects(per_fam["y"].values, per_fam["v"].values)
                sign = -1 if config.METRIC_DIRECTION[m] == "lower" else 1
                pct = lambda x: round(100 * sign * (math.exp(x) - 1), 2)
                row.update({"pooled_improvement_pct": pct(r["log_rr"]),
                            "ci95_low_pct": min(pct(r["log_rr"] - 1.96 * r["se"]), pct(r["log_rr"] + 1.96 * r["se"])),
                            "ci95_high_pct": max(pct(r["log_rr"] - 1.96 * r["se"]), pct(r["log_rr"] + 1.96 * r["se"])),
                            "tau2": round(r["tau2"], 4), "I2_pct": round(r["I2_pct"], 1)})
        rows.append(row)
    df = pd.DataFrame(rows)
    write_csv(df, out / "tables" / "meta_analysis_feasibility.csv")
    return df


# ------------------------------------------------------------------ Steps 22-23

TAXONOMY_BRANCHES = [
    ("Application context", "application_context", False),
    ("Road users", "traffic_modes", True),
    ("RL family", "rl_family", False),
    ("Agent architecture", "agent_architecture", False),
    ("Coordination", "coordination", False),
    ("State", "state_repr", True),
    ("Action", "action_type", False),
    ("Reward", "reward_type", True),
    ("Function approximator", "function_approximator", False),
    ("Simulator", "simulator", True),
    ("Baselines", "baseline_classes", True),
    ("Deployment barriers", "barriers", True),
]


def taxonomy(tech: pd.DataFrame, out: Path) -> str:
    lines = ["mindmap", "  root((RL for traffic signal control))"]
    md = ["# Taxonomy of included studies (Step 22)\n",
          "Counts are numbers of included papers; multi-valued fields can sum to more than N.\n"]
    for title, col, multi in TAXONOMY_BRANCHES:
        cnt = (count_multi if multi else count_single)(tech, col)
        cnt = cnt[cnt.iloc[:, 0] != "not_reported"]
        lines.append(f"    {title}")
        md.append(f"\n**{title}**\n")
        for _, r in cnt.iterrows():
            lines.append(f"      {r.iloc[0]} ({r['n_papers']})")
            md.append(f"- {r.iloc[0]}: {r['n_papers']}")
    vr = tech["vrl_i"].value_counts()
    lines.append("    Validation realism")
    md.append("\n**Validation realism**\n")
    for k, lab in config.VRL_LABELS.items():
        lines.append(f"      VRL{k} {lab} ({int(vr.get(k, 0))})")
        md.append(f"- VRL{k} {lab}: {int(vr.get(k, 0))}")
    text = "\n".join(md) + "\n\n```mermaid\n" + "\n".join(lines) + "\n```\n"
    (out / "taxonomy.md").write_text(text, encoding="utf-8")
    return text


def method_comparison(tech: pd.DataFrame, quant: pd.DataFrame, descriptions: pd.DataFrame,
                      out: Path) -> pd.DataFrame:
    rows = []
    fl = family_level(quant, ["metric", "baseline_class"]) if not quant.empty else pd.DataFrame()
    fam_of = dict(zip(tech["paper_id"], tech["rl_family"]))
    if not fl.empty:
        fl["rl_family"] = fl["papers"].map(lambda p: fam_of.get(p.split(";")[0], ""))
    for fam, g in tech.groupby(tech["rl_family"].replace("", "not_coded")):
        row = {"rl_family": fam, "n_papers": len(g),
               "top_algorithms": ", ".join(g["algorithm"].replace("", np.nan).dropna().value_counts().head(3).index),
               "median_vrl": g["vrl_i"].median(),
               "max_vrl": g["vrl_i"].max(),
               "pct_transfer_test": round(100 * (g["transfer_test"] == "Y").mean(), 1),
               "pct_robustness_test": round(100 * (g["robustness_test"] == "Y").mean(), 1),
               "pct_code_available": round(100 * (g["code_available"] == "Y").mean(), 1),
               "top_barriers": ", ".join(g["barriers"].map(split_multi).explode().dropna().value_counts().head(3).index)}
        for b in ("fixed_time", "max_pressure", "rl"):
            if not fl.empty:
                sub = fl[(fl["rl_family"] == fam) & (fl["baseline_class"] == b) &
                         fl["metric"].isin(["travel_time", "waiting_time", "delay"])]
                row[f"median_RI_vs_{b}_pct"] = round(sub["ri"].median(), 1) if len(sub) else np.nan
        rows.append(row)
    df = pd.DataFrame(rows)
    if not descriptions.empty and not df.empty:
        df = df.merge(descriptions, on="rl_family", how="left")
    write_csv(df, out / "tables" / "method_family_comparison.csv")
    return df


# ------------------------------------------------------------------ RQ6 gap matrix

def gap_matrix(tech: pd.DataFrame, out: Path) -> pd.DataFrame:
    rows = []
    for dim, col, multi in (("road users", "traffic_modes", True),
                            ("application context", "application_context", False),
                            ("objective", "objective_focus", True),
                            ("RL family", "rl_family", False)):
        vals = tech[col].map(split_multi) if multi else tech[col].map(lambda v: [v] if v else [])
        exp = tech.assign(_v=vals).explode("_v").dropna(subset=["_v"])
        for v, g in exp.groupby("_v"):
            row = {"dimension": dim, "value": v, "n_papers": g["paper_id"].nunique()}
            for k in config.VRL_LABELS:
                row[f"VRL{k}"] = int((g["vrl_i"] == k).sum())
            row["n_field_VRL4plus"] = int((g["vrl_i"] >= 4).sum())
            row["candidate_gap"] = "Y" if row["n_field_VRL4plus"] == 0 or row["n_papers"] <= 2 else "N"
            rows.append(row)
    df = pd.DataFrame(rows)
    write_csv(df, out / "tables" / "gap_matrix.csv")
    return df


# ------------------------------------------------------------------ driver

def run(project: Project) -> Path:
    out = project.outputs_dir / "synthesis"
    out.mkdir(parents=True, exist_ok=True)
    tech, quant = load(project)
    report = out / "synthesis_report.md"
    if tech.empty:
        report.write_text("# Synthesis report\n\nNo included studies extracted yet.\n", encoding="utf-8")
        return report
    desc = read_csv(project.protocol_dir / "method_families.csv")
    biblio = bibliometrics(tech, out)
    dep = dependence(tech, quant, out)
    qt = quantitative(quant, out) if not quant.empty else {}
    meta = meta_feasibility(quant, out) if not quant.empty else pd.DataFrame()
    tax = taxonomy(tech, out)
    comp = method_comparison(tech, quant, desc, out)
    gaps = gap_matrix(tech, out)

    n_rep, n_fam = len(tech), tech["study_family_id"].nunique()
    parts = [
        "# Synthesis report (Steps 22–27)\n",
        f"Generated by `python -m slr synthesis` from the extraction sheets. "
        f"Included reports: **{n_rep}**; independent study families: **{n_fam}**; "
        f"quantitative evidence entries: **{len(quant)}**.\n",
        "Figures are in `figures/`, all tables as CSV in `tables/`.\n",
        "## Step 24 — Descriptive and bibliometric analysis (RQ1–RQ3)\n",
        "### Papers per year\n", md_table(biblio["papers_per_year"]),
        "![papers per year](figures/fig_papers_per_year.png)\n",
        "### Top venues\n", md_table(biblio["venues_top15"]),
        "### Countries (first author)\n", md_table(biblio["countries"]),
        "### Application context\n", md_table(biblio["application_context"]),
        "### Road users\n", md_table(biblio["traffic_modes"]),
        "### RL family\n", md_table(biblio["rl_family"]),
        "![rl family by year](figures/fig_rl_family_by_year.png)\n",
        "### Agent architecture\n", md_table(biblio["agent_architecture"]),
        "### State / action / reward\n", md_table(biblio["state_repr"]), md_table(biblio["action_type"]),
        md_table(biblio["reward_type"]),
        "### Simulators\n", md_table(biblio["simulator"]),
        "### Validation Realism Level\n", md_table(biblio["vrl"]),
        "![vrl](figures/fig_vrl_distribution.png)\n![heatmap](figures/fig_heatmap_family_vrl.png)\n",
        "### Validation flags\n", md_table(biblio["validation_flags"]),
        "### Baselines\n", md_table(biblio["baseline_classes"]),
        "### Deployment barriers (RQ5)\n", md_table(biblio["barriers"]),
        "## Step 22 — Taxonomy\n", "See `taxonomy.md` (includes a Mermaid mind map).\n",
        "## Step 23 — Comparison of methodological families\n", md_table(comp),
        "## Step 25 — Quantitative synthesis (RQ4)\n",
        "Relative improvement RI (%) is positive when the RL controller is better than the baseline. "
        "Primary analysis: one value per study family (median of its entries).\n",
        "### By metric and baseline class (family level)\n",
        md_table(qt.get("ri_by_metric_baseline_family", pd.DataFrame())),
        "![ri by baseline](figures/fig_ri_by_baseline.png)\n",
        "### By metric and validation realism (family level)\n",
        md_table(qt.get("ri_by_metric_vrl_family", pd.DataFrame())),
        "![ri vs vrl](figures/fig_ri_vs_vrl.png)\n",
        "### Sensitivity: excluding Limited-quality studies\n",
        md_table(qt.get("sensitivity_excl_limited_qa", pd.DataFrame())),
        "## Step 26 — Meta-analysis feasibility\n",
        f"Rule: ≥ {config.META_MIN_FAMILIES} independent families with mean, SD and n for the same metric, "
        "baseline class and unit. Pooled values (random effects, DerSimonian–Laird, log response ratio) are "
        "exploratory and only computed for eligible cells.\n",
        md_table(meta),
        "## Step 27 — Dependence between publications\n",
        "### Study families with more than one report\n",
        md_table(dep["study_families"][dep["study_families"]["n_reports"] > 1]),
        "### Benchmark dataset reuse\n", md_table(dep["dataset_reuse"]),
        "## RQ6 — Gap matrix (candidate gaps: no VRL ≥ 4 evidence or ≤ 2 papers)\n",
        md_table(gaps[gaps["candidate_gap"] == "Y"] if not gaps.empty else gaps),
    ]
    report.write_text("\n".join(parts), encoding="utf-8")
    return report
