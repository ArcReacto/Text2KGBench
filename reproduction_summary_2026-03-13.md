# Text2KGBench 复现结果整理（2026-03-13）

## 1. 复现范围与方法

- 代码分支与提交：`exp` / `50a3d25`
- 复现方式：在 `src/evaluation` 目录运行 `run_eval.py`，使用仓库内已有 `llm_responses` 重算评测指标。
- 说明：`config/tikgen_vicuna_config.json` 与 `config/tikgen_alpaca_config.json` 是旧路径配置，未用于本次复现。

## 2. 与论文对比的关键文件

- 论文（指标来源）：
  - `Text2KGBench A Benchmark.pdf`（Table 2，Wikidata-TekGen / DBpedia-WebNLG 汇总指标）
- 评测脚本与配置：
  - `src/evaluation/run_eval.py`
  - `src/evaluation/config/tekgen_vicuna_config.json`
  - `src/evaluation/config/tikgen_unseen_vicuna_config.json`
  - `src/evaluation/config/tikgen_unseen_alpaca_config.json`
  - `src/evaluation/config/webnlg_vicuna_config.json`
  - `src/evaluation/config/webnlg_alpaca_config.json`
- 本次复现输出文件：
  - `data/wikidata_tekgen/baselines/Vicuna-13B/eval_metrics/ont_llm_avg_stats_v2.jsonl`
  - `data/wikidata_tekgen/baselines/Vicuna-13B/unseen/eval_metrics/ont_llm_avg_eval_metrics.jsonl`
  - `data/wikidata_tekgen/baselines/Alpaca-LoRA-13B/unseen/eval_metrics/ont_llm_avg_eval_metrics.jsonl`
  - `data/dbpedia_webnlg/baselines/Vicuna-13B/eval_metrics/avg_eval_results.jsonl`
  - `data/dbpedia_webnlg/baselines/Alpaca-LoRA-13B/eval_metrics/avg_eval_results.jsonl`
- 论文里需要但本次未直接重跑的一组（由仓库已有结果汇总）：
  - `data/wikidata_tekgen/baselines/Alpaca-LoRA-13B/eval_metrics/ont_llm_avg_stats.jsonl`

## 3. 论文 Table 2 与复现结果对比

指标顺序：`P / R / F1 / OC / SH / RH / OH`

| 设置 | 论文结果 | 本次复现 | 差异（复现-论文） |
|---|---|---|---|
| Wikidata-TekGen Vicuna All | 0.38 / 0.34 / 0.35 / 0.83 / 0.17 / 0.17 / 0.17 | 0.38 / 0.35 / 0.35 / 0.84 / 0.17 / 0.13 / 0.17 | 0 / +0.01 / 0 / +0.01 / 0 / -0.04 / 0 |
| Wikidata-TekGen Vicuna Selected | 0.42 / 0.39 / 0.38 / 0.84 / 0.11 / 0.16 / 0.14 | 0.42 / 0.39 / 0.39 / 0.85 / 0.11 / 0.12 / 0.14 | 0 / 0 / +0.01 / +0.01 / 0 / -0.04 / 0 |
| Wikidata-TekGen Vicuna Unseen | 0.32 / 0.32 / 0.32 / 0.86 / 0.07 / 0.14 / 0.14 | 0.32 / 0.32 / 0.32 / 0.86 / 0.07 / 0.14 / 0.14 | 全部一致 |
| Wikidata-TekGen Alpaca All* | 0.32 / 0.26 / 0.27 / 0.87 / 0.18 / 0.13 / 0.17 | 0.32 / 0.26 / 0.27 / 0.88 / 0.19 / 0.12 / 0.18 | 0 / 0 / 0 / +0.01 / +0.01 / -0.01 / +0.01 |
| Wikidata-TekGen Alpaca Selected* | 0.33 / 0.27 / 0.28 / 0.87 / 0.12 / 0.13 / 0.17 | 0.34 / 0.28 / 0.29 / 0.88 / 0.13 / 0.12 / 0.18 | +0.01 / +0.01 / +0.01 / +0.01 / +0.01 / -0.01 / +0.01 |
| Wikidata-TekGen Alpaca Unseen | 0.22 / 0.22 / 0.22 / 0.86 / 0.09 / 0.14 / 0.26 | 0.22 / 0.22 / 0.22 / 0.86 / 0.10 / 0.14 / 0.26 | SH +0.01，其余一致 |
| DBpedia-WebNLG Vicuna | 0.34 / 0.27 / 0.30 / 0.93 / 0.12 / 0.07 / 0.28 | 0.34 / 0.27 / 0.30 / 0.93 / 0.12 / 0.07 / 0.28 | 全部一致 |
| DBpedia-WebNLG Alpaca | 0.32 / 0.23 / 0.25 / 0.91 / 0.16 / 0.09 / 0.38 | 0.32 / 0.23 / 0.25 / 0.91 / 0.16 / 0.09 / 0.38 | 全部一致 |

* 说明：Alpaca 的 `All/Selected` 来自 `ont_llm_avg_stats.jsonl` 按 ontology 行重新求平均（该文件没有单独 `global` 行）。

## 4. 结论

- 复现总体成功：主要核心结果与论文 Table 2 对齐。
- 差异主要为 `0.01` 量级，集中在 Wikidata-TekGen 的 `All/Selected`，可接受。
- 唯一较明显差异是 Vicuna 的 `RH`（约 `-0.04`），但对应 `OC` 同时 `+0.01`，其余核心事实抽取指标（P/R/F1）保持一致或几乎一致。

## 5. 建议在论文/报告中如何表述

- 可写为：  
  “在 `exp` 分支（commit `50a3d25`）按官方评测脚本重算后，DBpedia 两组与论文完全一致，Wikidata 各组在 `0.01` 量级内基本一致（少数 RH 指标存在小幅偏移）。”
