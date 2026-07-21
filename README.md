# ARTi Social Lab

ARTi 专属的 X + 小红书内容生产与实验判断 skill。

它把两个容易混淆的任务严格拆开：

- `create_content_package`：生成选题、内容核心、平台版本、视觉规范与待验证假设。
- `evaluate_experiment_result`：读取真实发布数据，按平台指标、证据强度和归因条件输出结果与下一轮动作。

生成动作不会顺手宣布赢家；评估动作不会顺手重写内容。

## 结构化实验维度

每条内容都记录：

- `pillar`
- `audience_stage`
- `proof_type`
- `cta_type`
- `platform`
- `hypothesis_variable`

另外单独记录证据 flags 与 `evidence_strength_score`，避免把“有说服力”和“有表现”混为一谈。

## 平台胜利定义

小红书主要观察收藏率、完读/滑完率、私信意向与主页访问；X 主要观察首屏后互动代理、有效回复、主页点击与链接意向。所有结果都在同平台匹配 baseline 内判断，不计算跨平台综合分。

## 硬决策规则

- 高曝光低转化 → 保留 hook，重写 CTA。
- 高收藏/留存低互动 → 保留结构，改变 discussion angle。
- 高互动低产品相关性 → 降低模板权重。
- 单条爆发但不可归因 → 不升 baseline，只进入 watchlist。

模板至少重复 3 次、可归因胜率不低于 66.7%、主指标 lift 中位数为正、无护栏失败并覆盖两个 test block，才会成为 ARTi playbook candidate。

## 安装

```bash
npx skills add DaNie1la/arti-social-lab
```

也可以复制到项目的 `.agents/skills/arti-social-lab/`。

## 使用示例

```text
使用 arti-social-lab 执行 create_content_package：为 ARTi 做一篇小红书产品实测，只测试封面 hook。
```

```text
使用 arti-social-lab 执行 evaluate_experiment_result：读取这批 24h/72h 数据，按 pillar、proof type、platform × CTA、实验纯度和 reuse value 复盘。
```

## CSV 评估

从追踪表导出 Experiment Log 后运行：

```bash
python scripts/evaluate_experiment_result.py experiment_log.csv \
  --json-output experiment_evaluation.json \
  --markdown-output experiment_evaluation.md
```

旧入口 `scripts/score_experiments.py` 仍可使用。

## 实验追踪表

`assets/arti_social_experiment_tracker.xlsx` 包含：

- 双动作使用说明
- 结构化 Content Inputs
- 平台独立 Experiment Log
- Metric Definitions
- Decision Rules
- ARTi Dashboard
- Template Library 与 Playbook

黄色区域为人工输入，灰色区域为公式或评估结果。平台未提供的指标留空，不要填 0。

## 品牌与合规

- 对外品牌名统一为 `ARTi`。
- ARTi 产品实测明确项目关系，同时写有效之处与限制。
- 不编造使用结果、用户数据、评论或平台表现。
- 投研内容不提供买卖建议或收益承诺。
- X 图片提供 alt text。
- 不自动发布、私信或批量互动，除非用户明确授权。

## License

当前未指定开源许可证。公开可见不代表自动授予复制、修改或再分发权限。
