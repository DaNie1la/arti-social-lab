# ARTi 平台指标定义

X 与小红书分别定义胜利。不存在跨平台综合分。

## 共用原则

- 只记录平台后台真实值；没有的字段留空。
- 分母为 0 或缺失时，派生指标留空。
- 每条实验只指定一个 `primary_metric`，其余为 guardrail 或诊断指标。
- 用匹配 baseline 的相对变化判断 high / normal / low：`(value / baseline) - 1`。
- “首屏停留”如平台未提供 dwell 数据，只能使用明确标注的互动代理指标。

## 小红书 success metrics

| 指标 ID | 公式 | 适用 CTA / 目标 |
| --- | --- | --- |
| `xhs_save_rate` | `saves_24h / views_24h` | `save`、可复用价值 |
| `xhs_completion_rate` | `completed_views_24h / views_24h` | 完读/滑完、结构质量 |
| `xhs_profile_visit_rate` | `profile_visits_24h / views_24h` | `profile_visit`、产品探索 |
| `xhs_dm_intent_rate` | `dm_intents_72h / views_24h` | `dm`、高意向 |
| `xhs_discussion_rate` | `comments_24h / views_24h` | `discussion`、共创 |
| `xhs_product_relevance_rate` | `(product_questions_72h + trial_intents_72h) / views_24h` | 产品相关性护栏 |

如果后台没有 `completed_views_24h`，不要用 likes 或停留时间猜完读率。

## X success metrics

| 指标 ID | 公式 | 适用 CTA / 目标 |
| --- | --- | --- |
| `x_first_screen_engaged_rate_proxy` | `engagements_24h / impressions_24h` | 首屏后互动代理；不是 dwell rate |
| `x_qualified_reply_rate` | `qualified_replies_72h / impressions_24h` | `discussion`、reply quality |
| `x_profile_click_rate` | `profile_clicks_24h / impressions_24h` | `profile_visit` |
| `x_link_intent_rate` | `link_intents_24h / impressions_24h` | `link_click` |
| `x_bookmark_rate` | `bookmarks_24h / impressions_24h` | `save`，只在 X 内比较 |
| `x_product_relevance_rate` | `(product_questions_72h + trial_intents_72h) / impressions_24h` | 产品相关性护栏 |

`qualified_replies_72h` 只统计提出真实问题、给出反例、表达使用场景或继续讨论的回复；emoji、泛夸赞和机器人回复不计入。

## Platform × CTA 默认主指标

| CTA | 小红书 | X |
| --- | --- | --- |
| `save` | `xhs_save_rate` | `x_bookmark_rate` |
| `discussion` | `xhs_discussion_rate` | `x_qualified_reply_rate` |
| `profile_visit` | `xhs_profile_visit_rate` | `x_profile_click_rate` |
| `dm` | `xhs_dm_intent_rate` | 若无稳定 DM 口径，改用 `x_profile_click_rate` 并注明代理 |
| `link_click` | 仅平台可见链接数据；否则不设该 CTA | `x_link_intent_rate` |
| `product_question` | `xhs_product_relevance_rate` | `x_product_relevance_rate` |
| `trial_intent` | `xhs_product_relevance_rate` | `x_product_relevance_rate` |

## 诊断维度映射

- `reach`：`impressions_24h`；小红书有独立曝光和打开时也保留二者。
- `retention`：小红书优先 `xhs_save_rate` 与 `xhs_completion_rate`；X 可用 `x_bookmark_rate`，但不要称为完读。
- `interaction`：小红书 `xhs_discussion_rate`；X `x_qualified_reply_rate`，首屏代理只作辅助。
- `conversion`：按 CTA 使用主页访问、DM、链接或产品意向率。
- `product_relevance`：使用平台各自的 product relevance rate。
