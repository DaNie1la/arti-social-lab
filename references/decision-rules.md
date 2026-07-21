# ARTi 实验硬决策规则

## 判定基线

优先使用同平台、同账号、同 pillar、同 audience stage、同时间块的匹配 baseline。

- `high`：相对匹配 baseline 提升至少 20%。
- `low`：相对匹配 baseline 下降至少 20%。
- `normal`：介于 -20% 与 +20%。
- `unknown`：没有可靠 baseline 或指标缺失。

样本较多时可用同组历史第 75 / 25 百分位替代 ±20%，但必须记录所用口径。不得在复盘后为了制造结论临时改阈值。

## 决策优先级

从上到下命中第一条，不同时输出互相冲突的动作。

| 优先级 | 条件 | `next_action_code` | 动作 |
| ---: | --- | --- | --- |
| 1 | 追踪异常或关键指标缺失 | `FIX_TRACKING` | 暂停判定，修复追踪 |
| 2 | 护栏相对 baseline 下降 20% 以上 | `STOP_VARIANT_GUARDRAIL` | 停止变体，记录损害 |
| 3 | 单条高曝光/高主指标，但不可归因 | `WATCHLIST_ONLY` | 不升 baseline，只进 watchlist |
| 4 | `reach = high` 且 `conversion = low` | `KEEP_HOOK_REWRITE_CTA` | 保留 hook，下一轮只改 CTA |
| 5 | `retention = high` 且 `interaction = low` | `KEEP_STRUCTURE_CHANGE_DISCUSSION_ANGLE` | 保留结构，下一轮只改讨论角度 |
| 6 | `interaction = high` 且 `product_relevance = low` | `DOWNWEIGHT_TEMPLATE` | 降低模板权重，避免高互动稀释产品相关性 |
| 7 | 可归因且主指标提升至少 20%，护栏未恶化 | `RETEST_WINNER` | 保留变体，再做同变量复测 |
| 8 | 可归因且主指标下降至少 20% | `RETURN_TO_BASELINE` | 返回 baseline，记录失败条件 |
| 9 | 差异不足或样本不足 | `COLLECT_MORE_DATA` | 保持实验，不提前宣判 |

## 归因门槛

以下全部满足才是 `attributable`：

1. `changed_variable_count = 1`。
2. 变更字段与 `hypothesis_variable` 一致。
3. 主指标和护栏数据完整。
4. 平台、账号、pillar、audience stage 和比较时间块匹配。
5. 没有付费投流、外部大号导流、删除重发、平台处罚或明显时段异常。

不满足时可以观察表现，但不能计入受控 win rate。

## Playbook 准入

模板只有同时满足以下条件才可标为 `playbook_candidate`：

- 同一 `template_id` 至少 3 条完整、可归因使用记录。
- 至少 2 条 win，受控 win rate 不低于 66.7%。
- 主指标 lift 中位数大于 0。
- 没有 guardrail fail。
- 至少覆盖 2 个 test block；若只有一个 block，保持 watchlist。

进入 playbook 后继续记录适用平台、pillar、audience stage、proof type、CTA 和失败条件。单条爆发永远不能直接进入 playbook。

## 监测面板

- `pillar_win_rate`：每个 pillar 的 attributable wins / attributable complete。
- `proof_type_win_rate`：每种 proof type 的 attributable wins / attributable complete；证据分数另列，不给胜率加权。
- `platform_cta_conversion`：平台 × CTA 的主转化率和 lift，不跨平台合并。
- `variable_discipline`：pure 条数 / 已完成实验条数；mixed 不进入受控胜率。
- `reuse_value`：template 使用次数、wins、win rate、主指标 lift 中位数、跨 block 数与 playbook 状态。
