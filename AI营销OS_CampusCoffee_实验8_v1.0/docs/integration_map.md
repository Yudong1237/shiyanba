# 实验1—7整合映射

| 前序实验能力 | v1.0 模块 | 当前交付物 |
|---|---|---|
| 实验1：品牌与产品基础 | 品牌档案 | `data/raw/brand_profile.json` |
| 实验2：消费者需求整理 | 消费者洞察 | `src/marketing_os.py::consumer_insight` |
| 实验3：数据清洗与质量 | 数据输入、匿名和边界 | `data/raw/*.csv`、`docs/module_contracts.md` |
| 实验4：消费者洞察与证据 | 痛点统计、证据 ID | `data/processed/consumer_topic_metrics.csv` |
| 实验5：竞品情报 | 威胁排序和市场空白 | `data/processed/competitive_ranking.csv` |
| 实验6：Content Gap 与 Brand Voice | 内容机会与语气 Skill | `data/processed/content_opportunity.csv`、`skills/brand_voice/SKILL.md` |
| 实验7：AI Marketing Workflow | Campaign Planner 和状态编排 | `workflows/campaign_workflow.json`、`src/marketing_os.py::campaign_planner` |
| 实验8：OS 综合开发 | A/B/问卷效果分析与下一轮优化 | `src/marketing_os.py::effect_analysis`、`reports/analysis_report.md` |

每个模块都输出 `evidence_trace`，并在 `logs/marketing_os.jsonl` 中记录运行顺序和状态，形成可回放的闭环。
