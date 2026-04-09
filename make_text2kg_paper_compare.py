#!/usr/bin/env python3
"""
Text2KGBench paper-vs-reproduction comparison generator.

Inputs:
- reproduction_summary_2026-03-13.md
- Text2KGBench A Benchmark.pdf (source anchored via text2kgbench_layout.txt)

Outputs under ./paper_compare_outputs:
- fig1_f1_rh_comparison.png
- fig2_metric_delta_heatmap.png
- table1_metric_level_comparison.csv/.md
- table2_setting_level_summary.csv/.md
- captions_and_sources.md
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

METRICS = ["P", "R", "F1", "OC", "SH", "RH", "OH"]


def parse_summary_table(md_path: Path) -> List[Dict[str, object]]:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    rows: List[Dict[str, object]] = []

    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "设置" in line or "---" in line:
            continue
        # expected columns: | setting | paper vals | repro vals | diff |
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 3:
            continue
        if " / " not in parts[1] or " / " not in parts[2]:
            continue

        setting = parts[0]
        p_nums = [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", parts[1])]
        r_nums = [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", parts[2])]
        if len(p_nums) != 7 or len(r_nums) != 7:
            continue

        row = {
            "setting": setting,
            "paper": dict(zip(METRICS, p_nums)),
            "repro": dict(zip(METRICS, r_nums)),
        }
        rows.append(row)

    if len(rows) != 8:
        raise RuntimeError(f"Expected 8 comparison rows from summary, got {len(rows)}")
    return rows


def write_csv(path: Path, rows: List[Dict[str, object]], cols: List[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def md_table(rows: List[Dict[str, object]], cols: List[str]) -> str:
    out = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


def make_table1(data: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows = []
    for d in data:
        setting = d["setting"]
        for m in METRICS:
            p = d["paper"][m]
            r = d["repro"][m]
            rows.append(
                {
                    "setting": setting,
                    "metric": m,
                    "paper": f"{p:.4f}",
                    "reproduction": f"{r:.4f}",
                    "delta_repro_minus_paper": f"{(r - p):.4f}",
                    "abs_delta": f"{abs(r - p):.4f}",
                }
            )
    return rows


def make_table2(data: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows = []
    all_abs = []
    for d in data:
        setting = d["setting"]
        deltas = [d["repro"][m] - d["paper"][m] for m in METRICS]
        abs_d = [abs(x) for x in deltas]
        all_abs.extend(abs_d)
        max_idx = int(np.argmax(abs_d))
        rows.append(
            {
                "setting": setting,
                "avg_abs_delta": f"{np.mean(abs_d):.4f}",
                "max_abs_delta": f"{np.max(abs_d):.4f}",
                "max_delta_metric": METRICS[max_idx],
                "exact_match_metric_count": int(sum(1 for x in abs_d if x < 1e-12)),
                "metrics_with_abs_delta_ge_0p02": int(sum(1 for x in abs_d if x >= 0.02)),
            }
        )

    rows.append(
        {
            "setting": "OVERALL",
            "avg_abs_delta": f"{np.mean(all_abs):.4f}",
            "max_abs_delta": f"{np.max(all_abs):.4f}",
            "max_delta_metric": "-",
            "exact_match_metric_count": int(sum(1 for x in all_abs if x < 1e-12)),
            "metrics_with_abs_delta_ge_0p02": int(sum(1 for x in all_abs if x >= 0.02)),
        }
    )
    return rows


def plot_fig1(data: List[Dict[str, object]], out_path: Path) -> None:
    settings = [d["setting"] for d in data]
    x = np.arange(len(settings))
    w = 0.36

    paper_f1 = np.array([d["paper"]["F1"] for d in data]) * 100
    repro_f1 = np.array([d["repro"]["F1"] for d in data]) * 100
    paper_rh = np.array([d["paper"]["RH"] for d in data]) * 100
    repro_rh = np.array([d["repro"]["RH"] for d in data]) * 100

    fig, axes = plt.subplots(1, 2, figsize=(13.8, 5.4), dpi=170)

    axes[0].bar(x - w/2, paper_f1, width=w, label="Paper", color="#4E79A7")
    axes[0].bar(x + w/2, repro_f1, width=w, label="Reproduction", color="#F28E2B")
    axes[0].set_title("(a) F1 (%)")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(settings, rotation=20, ha="right", fontsize=8)
    axes[0].set_ylim(0, max(np.max(paper_f1), np.max(repro_f1)) * 1.2)
    axes[0].legend(fontsize=8)

    axes[1].bar(x - w/2, paper_rh, width=w, label="Paper", color="#4E79A7")
    axes[1].bar(x + w/2, repro_rh, width=w, label="Reproduction", color="#F28E2B")
    axes[1].set_title("(b) RH (%)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(settings, rotation=20, ha="right", fontsize=8)
    axes[1].set_ylim(0, max(np.max(paper_rh), np.max(repro_rh)) * 1.3)

    fig.suptitle("Paper vs Reproduction on Key Metrics (F1 and RH)", y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, format="png", bbox_inches="tight")
    plt.close(fig)


def plot_fig2(data: List[Dict[str, object]], out_path: Path) -> None:
    settings = [d["setting"] for d in data]
    delta = np.array([[d["repro"][m] - d["paper"][m] for m in METRICS] for d in data])

    fig, ax = plt.subplots(figsize=(11.6, 5.6), dpi=170)
    im = ax.imshow(delta, cmap="coolwarm", aspect="auto", vmin=-0.05, vmax=0.05)
    ax.set_xticks(np.arange(len(METRICS)))
    ax.set_xticklabels(METRICS)
    ax.set_yticks(np.arange(len(settings)))
    ax.set_yticklabels(settings, fontsize=8)
    ax.set_title("Metric Delta Heatmap (Reproduction - Paper)")

    for i in range(delta.shape[0]):
        for j in range(delta.shape[1]):
            ax.text(j, i, f"{delta[i, j]:+.2f}", ha="center", va="center", color="black", fontsize=7)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Delta value")
    fig.tight_layout()
    fig.savefig(out_path, format="png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    base = Path(__file__).resolve().parent
    summary_path = base / "reproduction_summary_2026-03-13.md"

    out_dir = base / "paper_compare_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = parse_summary_table(summary_path)

    # Table 1
    t1 = make_table1(data)
    t1_cols = ["setting", "metric", "paper", "reproduction", "delta_repro_minus_paper", "abs_delta"]
    write_csv(out_dir / "table1_metric_level_comparison.csv", t1, t1_cols)
    (out_dir / "table1_metric_level_comparison.md").write_text(
        "# Table 1. Metric-Level Comparison (Paper vs Reproduction)\n\n"
        + md_table(t1, t1_cols)
        + "\n",
        encoding="utf-8",
    )

    # Table 2
    t2 = make_table2(data)
    t2_cols = [
        "setting",
        "avg_abs_delta",
        "max_abs_delta",
        "max_delta_metric",
        "exact_match_metric_count",
        "metrics_with_abs_delta_ge_0p02",
    ]
    write_csv(out_dir / "table2_setting_level_summary.csv", t2, t2_cols)
    (out_dir / "table2_setting_level_summary.md").write_text(
        "# Table 2. Setting-Level Delta Summary\n\n"
        + md_table(t2, t2_cols)
        + "\n",
        encoding="utf-8",
    )

    # Figures
    plot_fig1(data, out_dir / "fig1_f1_rh_comparison.png")
    plot_fig2(data, out_dir / "fig2_metric_delta_heatmap.png")

    notes = """# Captions and Data Source Notes

## Generated Files
- `fig1_f1_rh_comparison.png`
- `fig2_metric_delta_heatmap.png`
- `table1_metric_level_comparison.csv` / `.md`
- `table2_setting_level_summary.csv` / `.md`

## Figure Captions (ready to use)
- **Figure 1. Paper vs reproduction comparison on key metrics (F1 and RH) across all benchmark settings.**
  Panel (a) shows F1; panel (b) shows relation hallucination (RH).

- **Figure 2. Heatmap of metric deltas (reproduction minus paper).**
  Rows are settings, columns are metrics `P/R/F1/OC/SH/RH/OH`.

## Table Notes
- **Table 1** provides metric-level comparison (`paper`, `reproduction`, `delta`).
- **Table 2** summarizes stability per setting (average absolute delta, max delta, exact-match count).

## Paper Source Anchors
- Paper table location: `text2kgbench_layout.txt:505-526` (Table 2 rows and metric schema)
- Metric order in paper: `P / R / F1 / OC / SH / RH / OH`

## Reproduction Source
- `Text2KGBench/reproduction_summary_2026-03-13.md` section: "3. 论文 Table 2 与复现结果对比"

## Interpretation Notes
- Most settings are exact or near-exact match; larger deviation is concentrated on RH for Wikidata-TekGen Vicuna All/Selected.
- Delta sign convention: `reproduction - paper`.
"""
    (out_dir / "captions_and_sources.md").write_text(notes, encoding="utf-8")

    print(f"Done. Outputs written to: {out_dir}")


if __name__ == "__main__":
    main()

