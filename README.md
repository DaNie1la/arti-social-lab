# ARTi Social Lab

面向 **X + 小红书** 的 ARTi 社媒内容与实验优化 skill。

它先建立一份可信的 `content_core`，再根据平台分别生成：

- 小红书：封面、5–8 页卡片、正文、置顶评论
- X：单帖、可选线程、配图规范、alt text

同时记录每条内容的唯一测试变量、主指标、护栏指标和 1h / 24h / 72h 数据，避免用单条高表现或跨平台混算得出错误结论。

## 能做什么

- 生成 ARTi 的 X 与小红书内容包
- 把同一主题改写为两个平台版本
- 生成官网同源的封面或配图规范
- 管理内容、视觉、钩子和 CTA 模板
- 规划单变量实验
- 回填和复盘真实发布数据
- 按平台、账号、目标和内容线隔离分析

## 安装

使用 skills CLI：

```bash
npx skills add yudanning1221-tech/arti-social-lab
```

也可以把整个仓库复制到项目的 `.agents/skills/arti-social-lab/`。

## 使用示例

```text
用 ARTi 做下一篇小红书，测试收藏型封面。
```

```text
把这篇 ARTi 实测改成一个 X 单帖和一条 5 帖线程。
```

```text
同一个内容核心分别做小红书和 X 版本，各自只测试一个变量。
```

```text
回填昨天 24 小时数据，按平台判断哪个模板更好。
```

## 首轮实验建议

### 小红书

- H2 数字清单 vs H6 证据先行
- C1 结论档案 vs C3 证据卡
- A2 保存动作 vs A1 低成本回复

### X

- H6 证据先行 vs H5 反常识
- 单帖 vs 线程
- A5 观点讨论 vs A4 产品探索

每组先做 3 条获得初步方向；至少 6 条且跨两个时间块后，才可作为当前可复用基线。

## 实验追踪表

`assets/arti_social_experiment_tracker.xlsx` 包含：

- Creative Brief
- Experiment Log
- Metric Map
- Template Library
- Experiment Plan
- Dashboard

黄色单元格为人工输入，灰色区域为公式计算。平台没有提供的指标应留空，不要填 0。

## CSV 分析

从 Experiment Log 导出 CSV 后运行：

```bash
python scripts/score_experiments.py experiment_log.csv --min-sample 3
```

脚本不会把 X 和小红书混在一起排名。

## 品牌与合规

- 对外品牌名统一为 `ARTi`
- ARTi 产品实测需披露项目关系
- 不编造使用结果、用户数据或评论
- 投研内容不提供买卖建议或收益承诺
- X 图片需要 alt text
- 不自动发布或批量互动，除非用户明确授权

详细规则见 `references/`。

## 仓库范围

本仓库只包含 skill、参考文件、分析脚本和实验追踪表，不包含账号密码、API key、平台 token、历史发布素材或私有运营数据。

## License

当前未指定开源许可证。公开可见不代表自动授予复制、修改或再分发权限。
