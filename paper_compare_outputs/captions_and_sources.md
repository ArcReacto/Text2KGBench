# Captions and Data Source Notes

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
