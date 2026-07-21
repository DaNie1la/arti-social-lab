# ARTi 实验记录与复盘协议

本文件只服务 `evaluate_experiment_result`。内容生成阶段只能预填计划字段，不得在这里模拟结果。

## 记录时间点

- 1h：排查发布、追踪或异常，不判胜。
- 24h：记录触达、保存、互动、主页和链接动作。
- 72h：补充有效回复、私信、产品问题和试用意向。

平台没有的指标留空，不用 0 代替缺失。

## 必填身份字段

- `post_id`
- `publish_date`
- `platform`
- `account`
- `pillar`
- `audience_stage`
- `proof_type`
- `evidence_strength_score`
- `cta_type`
- `hypothesis_variable`
- `changed_variable_count`
- `template_id`
- `test_block`
- `status`

枚举见 [schema.md](schema.md)。

## 原始计数字段

按平台可见口径填写：

- `impressions_24h`
- `views_24h`
- `saves_24h`
- `completed_views_24h`
- `likes_24h`
- `comments_24h`
- `replies_24h`
- `qualified_replies_72h`
- `reposts_24h`
- `bookmarks_24h`
- `engagements_24h`
- `profile_visits_24h`
- `profile_clicks_24h`
- `link_intents_24h`
- `dm_intents_72h`
- `product_questions_72h`
- `trial_intents_72h`

公式与平台限制见 [metrics.md](metrics.md)。

## Baseline 与 band

记录 `primary_metric`、`baseline_primary_value`、`guardrail_metric` 和 `baseline_guardrail_value`。如要触发硬规则，可再提供：

- `baseline_reach_value`
- `baseline_retention_value`
- `baseline_interaction_value`
- `baseline_conversion_value`
- `baseline_product_relevance_value`

评估器将根据平台指标计算 `reach_band`、`retention_band`、`interaction_band`、`conversion_band` 和 `product_relevance_band`。没有匹配 baseline 时为 `unknown`。

## 归因与异常

以下任一为真时，记录不可进入受控 win rate：

- 同时改了两个以上变量。
- 主指标或 baseline 缺失。
- 付费投流、外部大号导流、删除重发、平台处罚或明显时段异常。
- 比较组的平台、账号、pillar、audience stage 或 test block 不匹配。

不可归因内容仍可进入 watchlist，但不得提升 baseline 或 playbook。

## 样本措辞

| 可归因样本 | 允许措辞 |
| ---: | --- |
| 1–2 | 单条信号 |
| 3–5 | 初步方向，需要复测 |
| 6+ 且跨两个时间块 | 当前可复用 baseline |

模板进入 ARTi playbook 使用更严格的 3+ 稳定复用规则，见 [decision-rules.md](decision-rules.md)。

## 固定复盘顺序

1. 检查数据完整性。
2. 标记证据强度，但不把证据分数加进胜率。
3. 检查 variable discipline 和 attribution。
4. 按平台计算 success metrics。
5. 比较主指标与护栏的匹配 baseline。
6. 应用 hard decision rules。
7. 汇总 pillar、proof type、platform × CTA、实验纯度和 reuse value。

使用追踪表 `assets/arti_social_experiment_tracker.xlsx`，或运行：

```powershell
python scripts/evaluate_experiment_result.py experiment_log.csv --json-output experiment_evaluation.json
```
