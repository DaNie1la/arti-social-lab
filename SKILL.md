---
name: arti-social-lab
description: ARTi 专属 X 与小红书内容生产和社媒实验判断系统。用于 create_content_package：按固定内容支柱、受众阶段、证据类型、CTA、平台与唯一假设变量生成可发布内容包；或 evaluate_experiment_result：按平台独立指标、证据强度、归因条件和硬决策规则复盘真实数据，监测 pillar、proof type、platform × CTA、实验纯度与模板复用价值。用户提到 ARTi 社媒、X、小红书、封面/配图、内容模板、实验数据、A/B 测试、复盘或 playbook 时使用。
---

# ARTi 社媒实验系统

把内容生产和实验判断视为两个独立动作。技术标识保留 `arti-social-lab`；所有对外品牌文字统一写作 `ARTi`。

## 先选择唯一动作

### `create_content_package`

用于选题、内容、封面/配图、平台改写与实验设计。只输出待验证假设和预设指标，不读取结果、不判断输赢、不提升 baseline 或 playbook 权重。

### `evaluate_experiment_result`

用于回填、计算、归因、判定和下一轮动作。只分析已经发布的真实数据，不顺手重写帖子、生成新封面或改写 CTA 文案。

用户要求完整闭环时，先完成并冻结 `create_content_package`，再把已发布结果作为新的输入执行 `evaluate_experiment_result`。不要用刚生成的内容模拟数据或自评胜负。

## 共享结构化字段

每个 post 都必须记录以下字段，禁止用自由文本替代：

- `pillar`
- `audience_stage`
- `proof_type`
- `cta_type`
- `platform`
- `hypothesis_variable`

读取 [references/schema.md](references/schema.md) 获取枚举、证据分级与字段约束。创建动作遵循 [references/content_package.schema.json](references/content_package.schema.json)；评估动作遵循 [references/experiment_result.schema.json](references/experiment_result.schema.json)。

## 执行 `create_content_package`

1. 读取项目根目录存在的 `launch_plan.md`，再读取 [references/brand.md](references/brand.md)、[references/platforms.md](references/platforms.md)、[references/templates.md](references/templates.md) 和 [references/compliance.md](references/compliance.md)。
2. 验证六个结构化字段。缺失时明确标为 `needs_input`；可安全推断时写出假设来源，不静默猜测。
3. 只设一个 `hypothesis_variable`，并列出所有固定项。若同时改变两个以上变量，必须把 `variable_discipline` 标为 `mixed`，不得包装成受控实验。
4. 建立平台无关的 `content_core`：用户问题、唯一承诺、事实、证据、限制、ARTi 关系、CTA 意图。
5. 单独记录证据：填写 `evidence_flags`、`evidence_strength_score`、来源和 proof artifact。缺少可核验材料时保留 `[待补]`，不编造截图、数据、体验或评论。
6. 为指定平台单独适配。X 与小红书可以共享内容核心，但必须有独立 `post_id`、CTA、主指标和护栏。
7. 输出前检查合规、可访问性、品牌拼写和唯一变量。

### 创建动作输出

```text
content_package.json
content_core.md
platform/x.md 或 platform/xiaohongshu.md
visual_spec.md（需要视觉时）
```

`content_package.json` 必须包含 `action: "create_content_package"` 和 `evaluation_status: "not_evaluated"`。禁止出现 `winner`、`baseline_promoted`、`playbook_status: "admitted"` 等结果字段。

## 执行 `evaluate_experiment_result`

1. 读取 [references/schema.md](references/schema.md)、[references/metrics.md](references/metrics.md)、[references/decision-rules.md](references/decision-rules.md) 和 [references/experiment.md](references/experiment.md)。
2. 只接受平台后台真实值。平台没有的字段留空，不用 `0` 代替缺失。
3. 先检查证据强度和实验纯度，再计算指标。只有 `changed_variable_count = 1` 且归因条件全部通过的记录才进入受控胜率。
4. X 与小红书分别使用自己的 success metrics；禁止计算跨平台综合分或用同一个“互动率”统一判胜。
5. 先按 `platform × account × pillar × audience_stage × test_block` 找匹配 baseline，再判主指标和护栏。
6. 应用硬决策规则，输出机器可读 `next_action_code`。证据不足时输出 `insufficient_data`；不可归因的单条爆发只进入 `watchlist`。
7. 汇总五组监测：pillar 胜率、proof type 胜率、platform × CTA 转化、variable discipline、reuse value。
8. 只有重复至少 3 次且稳定、可归因的模板才允许进入 ARTi playbook。

### 评估动作输出

```text
experiment_evaluation.json
experiment_evaluation.md
```

输出必须包含范围、样本、平台指标、证据强度、归因状态、win status、硬规则命中、下一轮动作和置信度。不得在评估动作中提供新帖文案。

可直接分析从追踪表导出的 CSV：

```powershell
python scripts/evaluate_experiment_result.py experiment_log.csv --json-output experiment_evaluation.json
```

旧命令 `scripts/score_experiments.py` 保留为兼容入口。

## 平台胜利定义

- 小红书优先看收藏率、完读/滑完率、私信意向与主页访问；按目标选择一个主指标，其余作为护栏或辅助。
- X 优先看首屏后互动代理指标、有效回复率、主页点击率与链接意向率；没有 dwell/停留数据时必须明确写“代理指标”。
- 不用点赞代替产品意向，不用曝光代替转化，不用跨平台绝对值判模板优劣。

详细公式与 CTA 映射见 [references/metrics.md](references/metrics.md)。

## 硬决策

- 高曝光、低转化：保留 hook，重写 CTA。
- 高收藏/留存、低互动：保留结构，改变 discussion angle。
- 高互动、低产品相关性：降低该模板权重。
- 单条爆发但不可归因：不提升 baseline，只进入 watchlist。

阈值、优先级、playbook 准入和例外处理见 [references/decision-rules.md](references/decision-rules.md)。

## 最终质量门

- 动作边界没有混淆。
- 六个结构化字段全部使用合法枚举。
- `proof_type` 与 `evidence_strength_score` 分开记录。
- 主指标属于目标平台，且与 CTA 对应。
- 只有一个计划变量；否则明确标为 mixed / not attributable。
- ARTi 的产品关系、有效之处与限制同时可见。
- 投研内容保留必要边界声明。
- X 图片含 alt text；小红书图片关键结论在正文中可读。
