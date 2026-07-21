# ARTi 结构化字段与证据分级

字段名、枚举值和模板 ID 使用英文技术标识；面向用户的品牌名始终写 `ARTi`。

## 六个必填分析维度

| 字段 | 合法值 | 含义 |
| --- | --- | --- |
| `pillar` | `ai_tool_benchmark` | AI 工具横评：触达与比较 |
|  | `ai_workflow` | AI 效率方法：保存与复用 |
|  | `research_education` | AI / 公司研究教育：建立问题意识与方法 |
|  | `arti_product_test` | ARTi 产品实测：产品理解与意向 |
|  | `audience_cocreation` | 互动共创 / 构建过程：收集问题与反馈 |
| `audience_stage` | `problem_unaware` | 尚未意识到问题 |
|  | `problem_aware` | 已意识到问题，不知道解决方式 |
|  | `solution_aware` | 已知道解决方式，正在比较方案 |
|  | `product_aware` | 已知道 ARTi，正在判断是否使用 |
| `proof_type` | `real_product_usage` | 真实使用过程或输出，但未必有可展示 artifact |
|  | `screenshot_proof` | 可读截图、界面或结果证据 |
|  | `benchmark_data` | 有来源、口径或方法的横评/数据证据 |
|  | `subjective_opinion_only` | 只有观点或判断，无独立可核验证据 |
| `cta_type` | `save` | 保存/收藏 |
|  | `discussion` | 回复、评论或反例讨论 |
|  | `profile_visit` | 访问主页 |
|  | `dm` | 私信意向 |
|  | `link_click` | 站外链接意向 |
|  | `product_question` | 产品相关问题 |
|  | `trial_intent` | 试用意向 |
| `platform` | `xiaohongshu` | 小红书 |
|  | `x` | X |
| `hypothesis_variable` | `hook` | 首句或封面钩子 |
|  | `content_structure` | 卡片/线程推进结构 |
|  | `visual` | 视觉主题或信息呈现 |
|  | `cta` | CTA 类型或表达 |
|  | `format` | 单帖、线程、卡片、视频等 |
|  | `posting_time` | 发布时段 |
|  | `proof_type` | 证据呈现方式 |

## 证据必须单独记录

不要把“内容表现好”当成“证据强”。每条内容记录：

```json
{
  "proof_type": "screenshot_proof",
  "evidence_flags": {
    "real_product_usage": true,
    "screenshot_proof": true,
    "benchmark_data": false,
    "subjective_opinion_only": false
  },
  "evidence_strength_score": 4,
  "proof_artifacts": ["真实截图路径或来源 URL"],
  "source_reference": "来源、日期、方法或输入"
}
```
### 证据强度 1–4

| 分数 | 条件 | 解释 |
| ---: | --- | --- |
| 4 | 有方法与来源的 benchmark/data；或真实使用 + 可读 screenshot | 强可核验，仍需写口径与限制 |
| 3 | 有上下文与来源的 screenshot；或完整记录的真实使用过程 | 可核验，但外推能力有限 |
| 2 | real product usage，只有过程描述或零散输出 | 属于真实体验，证据 artifact 不完整 |
| 1 | subjective opinion only | 只能作为观点，不得包装成事实 |

若字段冲突，按较低等级处理。例如勾选 screenshot 但没有 artifact 时不得超过 2。证据分数只描述可信度，不参与内容胜率加分。

## 实验纯度

- `changed_variable_count = 1` 且唯一变量与 hypothesis 一致：`variable_discipline = pure`。
- `changed_variable_count = 0`：这是 baseline 采样，不是假设胜负测试。
- `changed_variable_count > 1`：`variable_discipline = mixed`，不能用于受控胜率。
- 缺失变量记录：`variable_discipline = unknown`，先补数据。

## Content package 最小实例

```json
{
  "action": "create_content_package",
  "package_id": "ARTI-X-20260720-001",
  "platform": "x",
  "pillar": "arti_product_test",
  "audience_stage": "solution_aware",
  "proof_type": "screenshot_proof",
  "cta_type": "discussion",
  "hypothesis_variable": "hook",
  "changed_variable_count": 1,
  "variable_discipline": "pure",
  "primary_metric": "x_qualified_reply_rate",
  "guardrail_metric": "x_profile_click_rate",
  "evaluation_status": "not_evaluated"
}
```

## Experiment result 最小实例

```json
{
  "action": "evaluate_experiment_result",
  "post_id": "ARTI-X-20260720-001",
  "platform": "x",
  "pillar": "arti_product_test",
  "audience_stage": "solution_aware",
  "proof_type": "screenshot_proof",
  "cta_type": "discussion",
  "hypothesis_variable": "hook",
  "changed_variable_count": 1,
  "status": "complete",
  "primary_metric": "x_qualified_reply_rate",
  "baseline_primary_value": 0.004
}
```
