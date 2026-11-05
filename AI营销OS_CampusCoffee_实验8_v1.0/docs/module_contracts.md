# 模块合同与数据边界

| 模块 | 输入 | 输出 | 追溯字段 |
|---|---|---|---|
| 品牌档案 | `brand_profile.json` | 品牌人格、Brand Voice、历史 Campaign | `data_boundary`、`version` |
| 消费者洞察 | 匿名反馈 CSV | 主题提及、痛点、证据 ID | `feedback_id`、`source`、`consent_status` |
| 竞争情报 | 竞品快照 CSV | 威胁排序、市场空白 | `source`、`is_mock` |
| 内容机会 | 内容覆盖 CSV + 洞察 | 用户重要度、竞品覆盖、机会分数 | `evidence_trace` |
| Campaign Planner | 前四模块 + 效果分析 | 目标、主题、渠道、KPI、风险 | `campaign.evidence_trace` |
| 效果分析 | A/B CSV + 问卷 CSV | 版本对比、uplift、下一轮建议 | `user_id`、`variant`、`consent_status` |

所有样例数据都标注 `is_mock=true`，不能直接当作真实市场结论。匿名 ID 不包含姓名、手机号、学号或设备标识；真实项目应在采集前取得授权并保留撤回机制。
