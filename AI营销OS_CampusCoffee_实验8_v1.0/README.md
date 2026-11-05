# AI Marketing OS：Campus Coffee 实验八 v1.0

这是把实验1—7合并后的完整营销系统示例，面向 Campus Coffee 的“晨光燕麦冷萃拿铁”新品。系统闭环为：**数据 → 洞察 → 决策 → 内容 → 实验 → 优化**。

## 最低功能范围

1. **品牌档案**：品牌资料、目标人群、Brand Voice 版本和历史 Campaign。
2. **消费者洞察**：读取匿名反馈，统计需求主题、痛点和证据 ID。
3. **竞争情报**：计算竞品威胁指数、排序和市场空白。
4. **内容机会**：比较我方/竞品覆盖率，计算用户重要度、内容缺口和机会分数。
5. **Campaign Planner**：组合上游结果，输出目标、主题、渠道、KPI 和风险控制。
6. **营销效果分析**：比较 A/B 点击和购买转化，读取问卷意愿，生成下一轮优化建议。

## 目录

- `app.py`：Streamlit 上传、运行、结果、证据和下载页面。
- `src/marketing_os.py`：六大模块和统一编排入口。
- `src/db.py`、`db/init_db.sql`：SQLite 初始化和结果落库。
- `data/raw/`：品牌档案、匿名反馈、竞品快照、内容覆盖、A/B 和问卷样例。
- `data/processed/`：运行生成的主题、竞品、机会和效果 CSV。
- `reports/analysis_report.md`、`reports/run_result.json`：综合报告和完整结果。
- `skills/brand_voice/SKILL.md`：可调用的品牌语气规则。
- `workflows/campaign_workflow.json`：模块节点和状态合同。
- `tests/`：自动化测试；`demo/demo_script.md`：8 分钟演示脚本。

## 启动与运行

Python 3.10+：

```powershell
pip install -r requirements.txt
streamlit run app.py
```

无 Streamlit 环境时可直接运行核心：

```powershell
python src/marketing_os.py
python -m unittest discover -s tests -v
```

## 数据、合规与限制

所有样例 CSV 明确标注 `is_mock=true`，A/B 每组 12 人，仅用于演示流程；真实测试应扩充到每组 20–30 人，取得用户同意，使用匿名 ID，并记录撤回机制。系统不会把模拟 uplift 或 p-value 直接解释为真实市场效果。价格、库存、优惠券、校园拍摄授权和健康功效文案都设置了人工审核点。

## 答辩口径

- **解决的问题**：把分散的洞察、竞品、内容和 Campaign 决策统一到可追踪流程，并能根据实验结果提出下一轮优化。
- **数据来源**：品牌档案和模拟匿名样例；正式项目应替换为有授权的门店、访谈、核销和广告数据。
- **程序与 AI 边界**：主题统计、指标、排序、uplift 和数据库由程序计算；品牌语气、市场假设和策略需要人工审核。
- **证据回链**：每个模块输出 `evidence_trace`，原始 ID、source、consent_status 保留在输入和 SQLite 中。
- **下一版本**：扩大 A/B 样本，分层比较早八/图书馆/社团场景，补充真实库存和券核销数据。

版本：`v1.0`
