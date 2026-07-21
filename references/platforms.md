# 平台适配器

平台规格会变化。以下是制作默认值，不替代平台发布器和官方帮助页。

## 共用原则

- 先写 `content_core.md`，再做平台版本。
- 保持事实、证据、限制与品牌关系一致。
- 可改变的是钩子、长度、信息顺序、视觉比例和 CTA。
- 同一内容在 X 与小红书发布时，为每个平台建立独立 post ID 和实验记录。
- 不用跨平台绝对曝光判断哪个模板“更好”。

## 小红书

- 默认产物：封面 + 5–8 页卡片 + 发布正文 + 置顶评论。
- 默认画布：3:4，1080×1440。
- 首屏任务：一句冲突/收益 + 一个清晰视觉锚点。
- 正文任务：增加搜索语境、真实经历或方法补充，不重复卡片全文。
- 典型目标：收藏、完读/滑完、私信/主页访问、产品问题。
- 默认 CTA：低成本问题，例如“你最想测哪家公司/哪一步？”
- success metrics：`xhs_save_rate`、`xhs_completion_rate`、`xhs_profile_visit_rate`、`xhs_dm_intent_rate`；讨论或产品问题使用对应平台指标。

## X

- 默认产物：1 个单帖版本 + 可选 4–7 帖线程 + 1 张配图规范 + alt text。
- 未确认 Premium 时，主版本按 280 字符以内写；长内容优先拆线程。
- 单图可优先用 1:1 或 4:5；官方帮助页说明标准比例 2:1 到 3:4 的单图可完整显示。发布前在 composer 预览。
- 首帖不先铺背景，先给判断、反差或具体证据。
- 线程每帖只推进一步，最后一帖总结并给一个讨论/访问动作。
- 典型目标：首屏后互动、有效回复、主页访问、链接意向。
- success metrics：`x_first_screen_engaged_rate_proxy`、`x_qualified_reply_rate`、`x_profile_click_rate`、`x_link_intent_rate`。
- 没有 dwell/停留数据时，把互动率明确标成首屏代理，不写成真实停留率。
- 图片必须提供 alt text；避免把关键信息只放在图里。
- 官方参考：
  - `https://help.x.com/en/using-x/how-to-post`
  - `https://help.x.com/en/using-x/posting-gifs-and-pictures`
  - `https://help.x.com/en/using-x/write-image-descriptions`

## 平台输出命名

```text
content_core.md
platform/
  xiaohongshu.md
  x.md
visual_spec.md
content_package.json
```

只生成用户指定的平台，不为了“完整”制造无用版本。
