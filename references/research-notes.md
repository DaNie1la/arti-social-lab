# 公开 skill 调研记录

调研日期：2026-07-16

## 吸收的方法

### Marketing Skills / Social 与 A/B Testing

- 来源：
  - `https://github.com/coreyhaines31/marketingskills`
  - `https://raw.githubusercontent.com/coreyhaines31/marketingskills/main/skills/social/SKILL.md`
  - `https://raw.githubusercontent.com/coreyhaines31/marketingskills/main/skills/ab-testing/SKILL.md`
- 采用：
  - 生成前先读取产品营销语境。
  - 内容支柱、钩子、复用和平台适配分层。
  - 假设、唯一变量、主指标、护栏指标、预设样本和实验 playbook。
- ARTi 优化：
  - 不做通用平台日历，改成“内容核心 + 平台适配器”。
  - 不用网站 A/B 的统计显著性套低流量自然社媒；改用配对时间块、中位数与分级置信措辞。

### BlackTwist / Content Pattern Analyzer

- 来源：
  - `https://github.com/blacktwist/social-media-skills`
  - `https://raw.githubusercontent.com/blacktwist/social-media-skills/main/skills/content-pattern-analyzer-sms/SKILL.md`
- 采用：
  - 按支柱、格式、钩子、语气和时间拆解。
  - 少于 15 条时只列线索，30 条以上再做广义模式分析。
  - 输出“多做 / 少做 / 下一步实验”，不只展示原始数据。
- ARTi 优化：
  - 加入平台、账号、目标和内容线隔离，避免不同渠道混算。
  - 将“未测试组合”写入 backlog，不直接宣布成功模式。

### Xiaohongshu Images Skill

- 来源：`https://github.com/iamzifei/xiaohongshu-images-skill`
- 采用：
  - 小红书 3:4、1080×1440 的制作基线。
  - 连续卡片、文字边界和模板化输出思路。
- ARTi 优化：
  - 视觉不绑定米白或单一模板，改用 ARTi 官网 V1/V2/V3 色彩主题。
  - 小红书与 X 使用同一内容核心，但不把 3:4 规则套到 X。

## 未采用

- 需要未知外部 API key、带自动发布或安全审计不佳的 skill：不复制其脚本和权限设计。
- 把高互动直接称为“爆款公式”的方法：样本与归因不足。
- 逐平台原样复制内容：会让钩子、格式和评价指标失真。
- 仅按点赞排名：不能代表收藏、站外访问或产品意向。
