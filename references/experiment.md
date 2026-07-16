# 实验与数据规则

## 记录时间点

- 1h：用于排查发布、追踪或异常问题，不提前判胜。
- 24h：用于比较首轮触达、互动、保存和点击。
- 72h：用于比较关注、有效评论、产品问题和试用意向。

只记录平台后台真实可见值。平台没有的字段留空，不用 0 代替。

## 通用原始字段

- `impressions_*`：曝光/展示
- `views_*`：阅读、打开或视频播放；不同平台定义不同，只能在同平台比较
- `likes_*`
- `comments_*`
- `reposts_*`：转发/分享
- `saves_*`：收藏/书签
- `clicks_*`：站外链接或指定链接点击
- `profile_visits_*`
- `new_follows_*`
- `qualified_comments_*`
- `product_questions_*`
- `trial_intents_*`

## 派生指标

- 打开/阅读率 = views / impressions
- 互动率 = (likes + comments + reposts + saves) / impressions
- 保存率 = saves / views；X 无可靠 views 时用 impressions，并在指标名注明
- 精准互动率 = (comments + reposts) / impressions
- 点击率 = clicks / impressions
- 主页访问率 = profile_visits / impressions
- 关注转化率 = new_follows / profile_visits
- 产品意向率 = (product_questions + trial_intents) / profile_visits；无主页访问数据时退回 views 或 impressions，并注明

分母为 0 或缺失时留空。

## 目标与主指标

| 目标 | 默认主指标 | 护栏指标 |
| --- | --- | --- |
| 认知/曝光 | 同时间块曝光；小红书可加阅读率 | 精准互动率 |
| 收藏/留存 | 保存率 | 负面反馈、互动率 |
| 精准互动 | 精准互动率、有效评论 | 主页访问率 |
| 站外访问 | 点击率 | 互动率、负面反馈 |
| 产品意向 | 产品意向率、产品问题/试用意向 | 关系披露与负面反馈 |

如果 `primary_metric` 已显式填写，复盘优先使用该字段。

## 必填字段

```json
{
  "post_id": "X-P005",
  "publish_date": "YYYY-MM-DD",
  "platform": "X",
  "account": "",
  "format": "single_post|thread|carousel|video",
  "content_line": "主线|桥接|副线",
  "content_pillar": "",
  "awareness_stage": "问题未知|问题已知|方案已知|产品已知",
  "topic": "",
  "objective": "认知|收藏/留存|精准互动|站外访问|产品意向",
  "desired_action": "",
  "proof_type": "截图|数据|真实输入|用户问题|使用判断",
  "source_reference": "",
  "content_template": "S6",
  "visual_template": "C5",
  "hook_template": "H5",
  "cta_template": "A5",
  "visual_theme": "V1",
  "test_block": "X-B1",
  "tested_variable": "钩子模板",
  "baseline": "H6",
  "variant": "H5",
  "hypothesis": "",
  "primary_metric": "精准互动率",
  "guardrail_metric": "主页访问率",
  "target_sample": 3,
  "status": "计划中|已发布|待补数据|完整|异常|不可归因",
  "notes": ""
}
```

## 可归因条件

以下条件同时满足才进入模板比较：

1. 只改变一个计划变量。
2. 主指标对应时间点的数据完整。
3. 平台、账号、目标、内容线和比较时间块一致。
4. 发布时间在常用时段 ±60 分钟内，或已配对/注明异常。
5. 没有付费投流、外部大号导流、删除重发或平台处罚。
6. 护栏指标已检查。

## 样本判断

受控模板测试：

| 可比样本数 | 允许措辞 |
| ---: | --- |
| 1–2 | 单条信号，不能下结论 |
| 3–5 | 初步方向，需要复测 |
| 6+ 且跨两个时间块 | 当前可复用基线 |

广义模式分析：

| 样本数 | 置信度 |
| ---: | --- |
| <15 | 低，只列线索 |
| 15–29 | 中，适合提出实验 |
| 30+ | 较高，可分析支柱 × 格式 × 钩子 |

优先看中位数；均值只作辅助。不要跨目标比较综合分。

## 停止条件

- 技术或追踪异常：暂停并修复，不判输赢。
- 护栏指标明显恶化：停止变体并记录原因。
- 未达目标样本：结果保持“进行中”，不因中途领先提前停止。
- 结果无差异：保留较易制作版本，或下一轮测试更大胆差异。

## 复盘输出

```markdown
### 范围
- 平台 / 账号 / 目标 / 内容线：
- 时间块：
- 可比样本：
- 分析置信度：

### 结论
- 当前信号：
- 主指标中位数差异：
- 护栏变化：
- 是否可归因：

### 决策
- 保留：
- 复测：
- 停止：

### 下一轮
- 唯一变量：
- 基线：
- 保持不变：
- 目标样本与停止条件：
```
