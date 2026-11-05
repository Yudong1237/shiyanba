#!/usr/bin/env python3
"""Campus Coffee AI Marketing OS v1.0 的标准库核心。"""

from __future__ import annotations

import argparse
import csv
import json
import math
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from .db import init_db
except ImportError:
    from db import init_db


VERSION = "v1.0"
TOPICS = ["快速购买", "口味与配方", "价格优惠", "社交分享"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def consumer_insight(feedback: list[dict[str, str]]) -> dict[str, Any]:
    topic_counts: Counter[str] = Counter(row["topic"] for row in feedback)
    negative_counts: Counter[str] = Counter(row["topic"] for row in feedback if row["sentiment"] == "negative")
    total = len(feedback)
    metrics = []
    for topic in TOPICS:
        mentions = topic_counts[topic]
        negative = negative_counts[topic]
        negative_share = negative / mentions * 100 if mentions else 0
        importance = (mentions / total * 60 if total else 0) + negative_share * 0.4
        evidence_ids = [row["feedback_id"] for row in feedback if row["topic"] == topic]
        metrics.append({
            "topic": topic,
            "mentions": mentions,
            "negative_mentions": negative,
            "negative_share_pct": round(negative_share, 2),
            "user_importance_pct": round(importance, 2),
            "evidence_ids": ";".join(evidence_ids),
        })
    metrics.sort(key=lambda row: row["user_importance_pct"], reverse=True)
    return {
        "sample_size": total,
        "segments": dict(Counter(row["segment"] for row in feedback)),
        "topic_metrics": metrics,
        "top_pain_points": [row["topic"] for row in metrics if row["negative_mentions"] > 0][:3],
        "evidence_trace": ["data/raw/consumer_feedback.csv", "匿名且已同意用于课程分析"],
        "data_boundary": "样本为匿名模拟数据，不代表全体校园消费者",
    }


def competitive_analysis(competitors: list[dict[str, str]]) -> dict[str, Any]:
    ranked = []
    for row in competitors:
        price_fit = max(0.0, 100 - abs(float(row["price_index"]) - 100))
        threat = 0.30 * float(row["availability_score"]) + 0.25 * price_fit + 0.25 * float(row["brand_heat_index"]) + 0.20 * float(row["student_fit_score"])
        ranked.append({
            "competitor": row["competitor"],
            "threat_index": round(threat, 2),
            "availability_score": float(row["availability_score"]),
            "price_fit_score": round(price_fit, 2),
            "brand_heat_index": float(row["brand_heat_index"]),
            "student_fit_score": float(row["student_fit_score"]),
            "evidence": row["source"],
        })
    ranked.sort(key=lambda row: row["threat_index"], reverse=True)
    return {
        "ranked_competitors": ranked,
        "market_whitespace": [
            "把早八取杯动线和库存状态说清楚",
            "用透明冰量/甜度和学生优惠降低首次尝试门槛",
            "将社团套餐与真实试饮反馈绑定，而不是只做打卡传播",
        ],
        "evidence_trace": ["data/raw/competitor_snapshot.csv", "桌面竞品盘点，待真实市场数据复核"],
    }


def content_opportunity(coverage: list[dict[str, str]], insight: dict[str, Any]) -> dict[str, Any]:
    own = {(row["topic"]): float(row["coverage_pct"]) for row in coverage if row["brand"] == "Campus Coffee"}
    competitor_values: dict[str, list[float]] = defaultdict(list)
    for row in coverage:
        if row["brand"] != "Campus Coffee":
            competitor_values[row["topic"]].append(float(row["coverage_pct"]))
    metric_by_topic = {row["topic"]: row for row in insight["topic_metrics"]}
    ranked = []
    for topic in TOPICS:
        comp_avg = sum(competitor_values[topic]) / len(competitor_values[topic])
        gap = max(0.0, comp_avg - own.get(topic, 0))
        importance = float(metric_by_topic[topic]["user_importance_pct"])
        evidence = min(100.0, float(metric_by_topic[topic]["mentions"]) / max(float(row["mentions"]) for row in insight["topic_metrics"]) * 70 + float(metric_by_topic[topic]["negative_share_pct"]) * 0.3)
        score = 0.50 * importance + 0.30 * gap + 0.20 * evidence
        ranked.append({
            "topic": topic,
            "user_importance_pct": round(importance, 2),
            "own_coverage_pct": round(own.get(topic, 0), 2),
            "competitor_coverage_pct": round(comp_avg, 2),
            "content_gap_pct": round(gap, 2),
            "evidence_strength_pct": round(evidence, 2),
            "opportunity_score": round(score, 2),
            "priority": "P0" if score >= 55 else "P1" if score >= 35 else "P2",
        })
    ranked.sort(key=lambda row: row["opportunity_score"], reverse=True)
    return {"ranked_opportunities": ranked, "evidence_trace": ["data/raw/content_coverage.csv", "step:consumer_insight"]}


def campaign_planner(brand: dict[str, Any], insight: dict[str, Any], competition: dict[str, Any], opportunity: dict[str, Any], effect: dict[str, Any]) -> dict[str, Any]:
    top_topics = [row["topic"] for row in opportunity["ranked_opportunities"][:3]]
    return {
        "objective": "在校园场景提升新品认知、首购试饮和优惠券核销，并为下一轮内容迭代提供证据",
        "theme": "早八不空档，第一杯刚刚好",
        "target_consumer": "早八通勤者为主，图书馆学习者和社团活动人群为辅",
        "priority_topics": top_topics,
        "channels": [
            {"name": "校园小程序/公众号", "role": "领券和转化", "kpi": "领券率>=8%，核销率>=25%"},
            {"name": "校园社群与取杯点海报", "role": "覆盖早八动线", "kpi": "二维码访问>=1500"},
            {"name": "校园 KOC 试饮", "role": "口味与社交证明", "kpi": "有效互动率>=6%"},
            {"name": "门店/社团试饮", "role": "降低首次尝试门槛", "kpi": "试饮转购>=20%"},
        ],
        "risk_controls": ["价格、库存和券规则人工审核", "不作健康功效承诺", "校园拍摄取得授权", "A/B 结果达到样本门槛后再扩大投放"],
        "evidence_trace": ["step:brand_profile", "step:consumer_insight", "step:competitive_analysis", "step:content_opportunity", "step:effect_analysis"],
        "planner_note": f"品牌语气：{', '.join(brand['brand_voice']['personality'])}；历史 Campaign：{len(brand['historical_campaigns'])} 个；实验结果建议：{effect['recommendation']}",
    }


def _normal_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def effect_analysis(ab_rows: list[dict[str, str]], questionnaire: list[dict[str, str]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ab_rows:
        groups[row["variant"]].append(row)
    summary = []
    for variant, rows in sorted(groups.items()):
        n = len(rows)
        purchases = sum(int(row["purchased"]) for row in rows)
        clicks = sum(int(row["clicked_coupon"]) for row in rows)
        summary.append({
            "variant": variant,
            "sample_size": n,
            "click_rate_pct": round(clicks / n * 100, 2),
            "conversion_rate_pct": round(purchases / n * 100, 2),
            "avg_order_value_rmb": round(sum(float(row["order_value_rmb"]) for row in rows) / n, 2),
            "avg_feedback_score": round(sum(float(row["feedback_score"]) for row in rows) / n, 2),
        })
    by_variant = {row["variant"]: row for row in summary}
    a = by_variant.get("A")
    b = by_variant.get("B")
    if not a or not b:
        raise ValueError("A/B 数据必须同时包含 A 和 B")
    p_a = a["conversion_rate_pct"] / 100
    p_b = b["conversion_rate_pct"] / 100
    pooled = ((p_a * a["sample_size"]) + (p_b * b["sample_size"])) / (a["sample_size"] + b["sample_size"])
    se = math.sqrt(max(pooled * (1 - pooled) * (1 / a["sample_size"] + 1 / b["sample_size"]), 1e-12))
    z = (p_b - p_a) / se
    p_value = 2 * (1 - _normal_cdf(abs(z)))
    uplift = (p_b - p_a) / p_a * 100 if p_a else 0
    questionnaire_summary = []
    q_by_variant: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in questionnaire:
        q_by_variant[row["variant"]].append(row)
    for variant, rows in sorted(q_by_variant.items()):
        questionnaire_summary.append({
            "variant": variant,
            "sample_size": len(rows),
            "avg_trial_intent": round(sum(float(row["trial_intent_1_5"]) for row in rows) / len(rows), 2),
            "avg_purchase_intent": round(sum(float(row["purchase_intent_1_5"]) for row in rows) / len(rows), 2),
            "avg_brand_fit": round(sum(float(row["brand_fit_1_5"]) for row in rows) / len(rows), 2),
        })
    recommendation = "优先迭代 B 的取杯动线和首杯券表达，再扩大样本" if uplift > 0 else "保留 A，重新设计 B 的首屏信息后再测"
    return {
        "ab_summary": summary,
        "conversion_uplift_B_vs_A_pct": round(uplift, 2),
        "z_score": round(z, 3),
        "p_value_two_sided": round(p_value, 4),
        "statistical_caution": "每组仅 12 人且数据为模拟示例，不能宣称统计显著",
        "questionnaire_summary": questionnaire_summary,
        "recommendation": recommendation,
        "evidence_trace": ["data/raw/ab_test_anonymous.csv", "data/raw/questionnaire_anonymous.csv"],
    }


def write_report(path: Path, brand: dict[str, Any], insight: dict[str, Any], competition: dict[str, Any], opportunity: dict[str, Any], effect: dict[str, Any], campaign: dict[str, Any]) -> None:
    lines = [
        "# Campus Coffee AI Marketing OS 综合分析报告 v1.0",
        "",
        f"品牌：**{brand['brand']}**；产品：**{brand['product']}**；数据状态：课程演示模拟数据。",
        "",
        "## 1. 消费者洞察",
        "",
        f"样本量：{insight['sample_size']}；主要痛点主题：{', '.join(insight['top_pain_points'])}。",
        "",
        "| 主题 | 提及 | 负向 | 负向占比 | 用户重要度 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in insight["topic_metrics"]:
        lines.append(f"| {row['topic']} | {row['mentions']} | {row['negative_mentions']} | {row['negative_share_pct']}% | {row['user_importance_pct']} |")
    lines += ["", "## 2. 竞争情报", "", "| 排名 | 竞品 | 威胁指数 | 可得性 | 学生适配 |", "|---:|---|---:|---:|---:|"]
    for index, row in enumerate(competition["ranked_competitors"], start=1):
        lines.append(f"| {index} | {row['competitor']} | {row['threat_index']} | {row['availability_score']} | {row['student_fit_score']} |")
    lines += ["", "市场空白：" + "；".join(competition["market_whitespace"]), "", "## 3. Content Opportunity", "", "| 主题 | 我方覆盖 | 竞品覆盖 | 缺口 | 机会分数 | 优先级 |", "|---|---:|---:|---:|---:|---|"]
    for row in opportunity["ranked_opportunities"]:
        lines.append(f"| {row['topic']} | {row['own_coverage_pct']}% | {row['competitor_coverage_pct']}% | {row['content_gap_pct']}% | {row['opportunity_score']} | {row['priority']} |")
    lines += ["", "## 4. A/B 与问卷效果", "", f"B 相对 A 的转化 uplift：**{effect['conversion_uplift_B_vs_A_pct']}%**；p-value：{effect['p_value_two_sided']}。", "", "| 版本 | 样本 | 点击率 | 转化率 | 平均反馈 |", "|---|---:|---:|---:|---:|"]
    for row in effect["ab_summary"]:
        lines.append(f"| {row['variant']} | {row['sample_size']} | {row['click_rate_pct']}% | {row['conversion_rate_pct']}% | {row['avg_feedback_score']} |")
    lines += ["", f"建议：**{effect['recommendation']}**。{effect['statistical_caution']}", "", "## 5. Campaign Planner 输出", "", f"主题：**{campaign['theme']}**", "", campaign["objective"], "", "渠道：" + "、".join(item["name"] for item in campaign["channels"]), "", "## 6. 证据与限制", "", "所有模块均保留 evidence_trace；原始数据为匿名模拟数据，正式决策前需用真实门店、授权访谈、库存和核销数据复核。"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_os(base_dir: Path) -> dict[str, Any]:
    raw = base_dir / "data" / "raw"
    processed = base_dir / "data" / "processed"
    reports = base_dir / "reports"
    logs = base_dir / "logs"
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    run_id = f"os-{uuid.uuid4().hex[:12]}"
    started_at = now()
    log_path = logs / "marketing_os.jsonl"
    if log_path.exists():
        log_path.unlink()
    brand = read_json(raw / "brand_profile.json")
    feedback = read_csv(raw / "consumer_feedback.csv")
    competitors = read_csv(raw / "competitor_snapshot.csv")
    coverage = read_csv(raw / "content_coverage.csv")
    ab_rows = read_csv(raw / "ab_test_anonymous.csv")
    questionnaire = read_csv(raw / "questionnaire_anonymous.csv")
    questionnaire_by_user = {row["user_id"]: row for row in questionnaire}

    def event(module: str, status: str, evidence: list[str]) -> None:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp": now(), "run_id": run_id, "module": module, "status": status, "evidence_trace": evidence}, ensure_ascii=False) + "\n")

    event("brand_profile", "success", ["data/raw/brand_profile.json"])
    insight = consumer_insight(feedback)
    event("consumer_insight", "success", insight["evidence_trace"])
    competition = competitive_analysis(competitors)
    event("competitive_intelligence", "success", competition["evidence_trace"])
    opportunity = content_opportunity(coverage, insight)
    event("content_opportunity", "success", opportunity["evidence_trace"])
    effect = effect_analysis(ab_rows, questionnaire)
    event("effect_analysis", "success", effect["evidence_trace"])
    campaign = campaign_planner(brand, insight, competition, opportunity, effect)
    event("campaign_planner", "success", campaign["evidence_trace"])

    write_csv(processed / "consumer_topic_metrics.csv", insight["topic_metrics"], ["topic", "mentions", "negative_mentions", "negative_share_pct", "user_importance_pct", "evidence_ids"])
    write_csv(processed / "competitive_ranking.csv", competition["ranked_competitors"], list(competition["ranked_competitors"][0].keys()))
    write_csv(processed / "content_opportunity.csv", opportunity["ranked_opportunities"], list(opportunity["ranked_opportunities"][0].keys()))
    write_csv(processed / "ab_effect_results.csv", effect["ab_summary"], list(effect["ab_summary"][0].keys()))
    write_csv(processed / "questionnaire_summary.csv", effect["questionnaire_summary"], list(effect["questionnaire_summary"][0].keys()))
    init_db(base_dir / "data" / "marketing_os.db", brand, feedback, competitors, ab_rows, questionnaire_by_user, run_id, started_at)
    report = {"run_id": run_id, "version": VERSION, "started_at": started_at, "brand": brand, "consumer_insight": insight, "competitive_intelligence": competition, "content_opportunity": opportunity, "effect_analysis": effect, "campaign": campaign}
    write_json(reports / "run_result.json", report)
    write_report(reports / "analysis_report.md", brand, insight, competition, opportunity, effect, campaign)
    event("system", "complete", ["data/processed", "reports/run_result.json", "data/marketing_os.db"])
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    result = run_os(args.base_dir)
    print(f"AI Marketing OS {result['version']} complete: run_id={result['run_id']}; top_topic={result['content_opportunity']['ranked_opportunities'][0]['topic']}")


if __name__ == "__main__":
    main()
