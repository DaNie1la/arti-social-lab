#!/usr/bin/env python3
"""Summarize ARTi social experiments without mixing platforms or objectives."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


TEMPLATE_COLUMNS = (
    "content_template",
    "visual_template",
    "cover_template",
    "hook_template",
    "title_template",
    "cta_template",
    "visual_theme",
    "format",
)
ELIGIBLE_STATUSES = {"完整", "complete", "completed"}


def text(row: dict[str, Any], key: str, default: str = "未标注") -> str:
    value = str(row.get(key, "") or "").strip()
    return value or default


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    if raw.endswith("%"):
        return float(raw[:-1].replace(",", "")) / 100
    return float(raw.replace(",", ""))


def first_number(row: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def sum_available(*values: float | None) -> float | None:
    present = [value for value in values if value is not None]
    return sum(present) if present else None


def enrich(source: dict[str, str]) -> dict[str, Any]:
    row: dict[str, Any] = dict(source)
    platform = text(row, "platform").lower()

    impressions = first_number(row, "impressions_24h", "exposures_24h")
    views = first_number(row, "views_24h", "reads_24h")
    likes = first_number(row, "likes_24h")
    comments = first_number(row, "comments_24h")
    reposts = first_number(row, "reposts_24h", "shares_24h")
    saves = first_number(row, "saves_24h", "bookmarks_24h")
    clicks = first_number(row, "clicks_24h", "link_clicks_24h")
    profile_visits = first_number(row, "profile_visits_24h", "profile_visits_72h")
    follows = first_number(row, "new_follows_72h")
    questions = first_number(row, "product_questions_72h")
    trials = first_number(row, "trial_intents_72h")
    qualified_comments = first_number(row, "qualified_comments_72h", "effective_comments_72h")

    engagement = sum_available(likes, comments, reposts, saves)
    precise_interactions = sum_available(comments, reposts)
    save_denominator = impressions if platform in {"x", "twitter"} else (views or impressions)
    intent_denominator = profile_visits or views or impressions

    calculated = {
        "view_rate_24h": ratio(views, impressions),
        "engagement_rate_24h": ratio(engagement, impressions),
        "save_rate_24h": ratio(saves, save_denominator),
        "precise_interaction_rate_24h": ratio(precise_interactions, impressions),
        "comment_rate_24h": ratio(comments, views or impressions),
        "click_rate_24h": ratio(clicks, impressions),
        "profile_visit_rate_24h": ratio(profile_visits, impressions),
        "follow_rate_72h": ratio(follows, profile_visits),
        "product_intent_rate_72h": ratio(sum_available(questions, trials), intent_denominator),
        "qualified_comments_72h": qualified_comments,
        "impressions_24h": impressions,
    }
    for key, value in calculated.items():
        supplied = as_float(row.get(key))
        row[key] = supplied if supplied is not None else value
    return row


def metric_for(row: dict[str, Any]) -> tuple[str, float | None]:
    explicit = text(row, "primary_metric", default="").lower()
    aliases = {
        "阅读率": "view_rate_24h",
        "打开率": "view_rate_24h",
        "互动率": "engagement_rate_24h",
        "保存率": "save_rate_24h",
        "收藏率": "save_rate_24h",
        "精准互动率": "precise_interaction_rate_24h",
        "评论率": "comment_rate_24h",
        "点击率": "click_rate_24h",
        "主页访问率": "profile_visit_rate_24h",
        "关注转化率": "follow_rate_72h",
        "产品意向率": "product_intent_rate_72h",
    }
    if explicit in aliases:
        key = aliases[explicit]
        return key, as_float(row.get(key))
    if explicit in row:
        return explicit, as_float(row.get(explicit))

    objective = text(row, "objective").lower()
    platform = text(row, "platform").lower()
    if any(word in objective for word in ("收藏", "留存", "save")):
        key = "save_rate_24h"
    elif any(word in objective for word in ("精准互动", "评论", "discussion")):
        key = "precise_interaction_rate_24h"
    elif any(word in objective for word in ("站外", "点击", "traffic")):
        key = "click_rate_24h"
    elif any(word in objective for word in ("产品", "试用", "intent")):
        key = "product_intent_rate_72h"
    elif platform in {"小红书", "xiaohongshu", "xhs"}:
        key = "view_rate_24h"
    else:
        key = "engagement_rate_24h"
    return key, as_float(row.get(key))


def fmt(value: float | None, metric: str) -> str:
    if value is None:
        return "—"
    if metric.endswith("_rate_24h") or metric.endswith("_rate_72h"):
        return f"{value:.2%}"
    return f"{value:,.1f}"


def verdict(sample: int, min_sample: int) -> str:
    if sample < min_sample:
        return "单条信号"
    if sample < 6:
        return "初步方向，继续复测"
    return "当前可复用基线；检查是否跨两个时间块"


def summarize(rows: list[dict[str, Any]], template_col: str, min_sample: int) -> str:
    grouped: dict[tuple[str, ...], list[tuple[str, float]]] = defaultdict(list)
    for row in rows:
        template_id = text(row, template_col, default="")
        status = text(row, "status", default="").lower()
        if not template_id or status not in ELIGIBLE_STATUSES:
            continue
        metric, value = metric_for(row)
        if value is None:
            continue
        key = (
            text(row, "platform"),
            text(row, "account"),
            text(row, "objective"),
            text(row, "content_line"),
            template_id,
        )
        grouped[key].append((metric, value))

    lines = [
        f"### {template_col}",
        "",
        "| 平台 | 账号 | 目标 | 内容线 | 模板 | 可比样本 | 主指标 | 中位数 | 判断 |",
        "| --- | --- | --- | --- | --- | ---: | --- | ---: | --- |",
    ]
    if not grouped:
        lines.append("| — | — | — | — | — | 0 | — | — | 暂无完整可比数据 |")
        return "\n".join(lines)

    for key in sorted(grouped):
        platform, account, objective, content_line, template_id = key
        items = grouped[key]
        by_metric: dict[str, list[float]] = defaultdict(list)
        for metric, value in items:
            by_metric[metric].append(value)
        for metric, values in sorted(by_metric.items()):
            median = statistics.median(values)
            lines.append(
                f"| {platform} | {account} | {objective} | {content_line} | "
                f"{template_id} | {len(values)} | {metric} | {fmt(median, metric)} | "
                f"{verdict(len(values), min_sample)} |"
            )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize ARTi social experiment CSV data.")
    parser.add_argument("csv_path", type=Path, help="CSV exported from the Experiment Log sheet")
    parser.add_argument("--min-sample", type=int, default=3, help="Samples required for a directional signal")
    args = parser.parse_args()

    with args.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [enrich(row) for row in csv.DictReader(handle)]

    eligible = [row for row in rows if text(row, "status", default="").lower() in ELIGIBLE_STATUSES]
    print("# ARTi 社媒模板复盘")
    print()
    print(f"- CSV 行数：{len(rows)}")
    print(f"- 完整可比行数：{len(eligible)}")
    print(f"- 受控测试方向性样本：{args.min_sample}")
    print(f"- 广义模式置信度：{'低（少于 15 条）' if len(eligible) < 15 else '中' if len(eligible) < 30 else '较高'}")
    print("- 隔离维度：平台 × 账号 × 目标 × 内容线")
    print()
    for column in TEMPLATE_COLUMNS:
        if any(text(row, column, default="") for row in rows):
            print(summarize(rows, column, args.min_sample))
            print()
    print("注意：结果表示当前匹配样本中的相关性。主题、时间块、账号阶段和流量来源仍可能影响表现。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
