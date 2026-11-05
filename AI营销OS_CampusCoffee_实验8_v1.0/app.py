"""Streamlit 入口：上传数据、运行 OS、查看证据与下载报告。"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
from marketing_os import run_os  # noqa: E402

st.set_page_config(page_title="Campus Coffee AI Marketing OS", layout="wide")
st.title("Campus Coffee AI Marketing OS")
st.caption("v1.0 · 数据 → 洞察 → 决策 → 内容 → 实验 → 优化")

raw_dir = ROOT / "data" / "raw"
st.sidebar.header("数据输入")
upload_map = {
    "品牌档案 JSON": ("brand_profile.json", ["json"]),
    "消费者反馈 CSV": ("consumer_feedback.csv", ["csv"]),
    "竞品快照 CSV": ("competitor_snapshot.csv", ["csv"]),
    "内容覆盖 CSV": ("content_coverage.csv", ["csv"]),
    "A/B 匿名数据 CSV": ("ab_test_anonymous.csv", ["csv"]),
    "问卷匿名数据 CSV": ("questionnaire_anonymous.csv", ["csv"]),
}
for label, (filename, types) in upload_map.items():
    uploaded = st.sidebar.file_uploader(label, type=types, key=filename)
    if uploaded is not None and st.sidebar.button(f"保存 {label}", key=f"save-{filename}"):
        (raw_dir / filename).write_bytes(uploaded.getvalue())
        st.sidebar.success(f"已保存 {filename}")

if st.button("运行整合分析", type="primary"):
    with st.spinner("正在执行品牌、洞察、竞品、内容、Campaign 和效果分析..."):
        result = run_os(ROOT)
    st.session_state["result"] = result
    st.success(f"运行完成：{result['run_id']}")

result = st.session_state.get("result")
if result:
    insight = result["consumer_insight"]
    effect = result["effect_analysis"]
    opportunity = result["content_opportunity"]
    tabs = st.tabs(["总览", "消费者洞察", "竞品与内容机会", "效果分析", "证据与下载"])
    with tabs[0]:
        st.subheader(result["campaign"]["theme"])
        st.write(result["campaign"]["objective"])
        cols = st.columns(4)
        cols[0].metric("反馈样本", insight["sample_size"])
        cols[1].metric("最高机会主题", opportunity["ranked_opportunities"][0]["topic"])
        cols[2].metric("B相对A uplift", f"{effect['conversion_uplift_B_vs_A_pct']}%")
        cols[3].metric("版本", result["version"])
        st.json(result["campaign"])
    with tabs[1]:
        st.dataframe(insight["topic_metrics"], use_container_width=True)
        st.write("证据来源：", insight["evidence_trace"])
    with tabs[2]:
        st.dataframe(result["competitive_intelligence"]["ranked_competitors"], use_container_width=True)
        st.dataframe(opportunity["ranked_opportunities"], use_container_width=True)
    with tabs[3]:
        st.dataframe(effect["ab_summary"], use_container_width=True)
        st.dataframe(effect["questionnaire_summary"], use_container_width=True)
        st.info(effect["statistical_caution"])
        st.write(effect["recommendation"])
    with tabs[4]:
        report_path = ROOT / "reports" / "analysis_report.md"
        result_path = ROOT / "reports" / "run_result.json"
        log_path = ROOT / "logs" / "marketing_os.jsonl"
        st.write("证据链：", result["campaign"]["evidence_trace"])
        st.download_button("下载分析报告", report_path.read_bytes(), file_name="analysis_report.md")
        st.download_button("下载运行结果 JSON", result_path.read_bytes(), file_name="run_result.json")
        st.download_button("下载运行日志", log_path.read_bytes(), file_name="marketing_os.jsonl")
else:
    st.info("请确认数据文件后点击“运行整合分析”。默认样例为匿名模拟数据。")
