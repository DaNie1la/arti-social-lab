#!/usr/bin/env python3
"""Evaluate ARTi social experiments with platform-specific metrics and hard rules."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


PLATFORMS = {"xiaohongshu", "x"}
PILLARS = {
    "ai_tool_benchmark",
    "ai_workflow",
    "research_education",
    "arti_product_test",
    "audience_cocreation",
}
AUDIENCE_STAGES = {"problem_unaware", "problem_aware", "solution_aware", "product_aware"}
PROOF_TYPES = {"real_product_usage", "screenshot_proof", "benchmark_data", "subjective_opinion_only"}
CTA_TYPES = {"save", "discussion", "profile_visit", "dm", "link_click", "product_question", "trial_intent"}
HYPOTHESIS_VARIABLES = {"hook", "content_structure", "visual", "cta", "format", "posting_time", "proof_type"}
COMPLETE_STATUSES = {"complete", "completed", "完整"}
ANOMALY_STATUSES = {"anomaly", "not_attributable", "异常", "不可归因"}
TRUE_VALUES = {"1", "true", "yes", "y", "是"}
EPSILON = 1e-12

ALIASES = {
    "pillar": ("pillar", "content_pillar"),
    "audience_stage": ("audience_stage", "awareness_stage"),
    "proof_type": ("proof_type",),
    "cta_type": ("cta_type", "desired_action"),
    "hypothesis_variable": ("hypothesis_variable", "tested_variable"),
    "template_id": ("template_id", "content_template"),
    "qualified_replies_72h": ("qualified_replies_72h", "qualified_comments_72h"),
    "profile_clicks_24h": ("profile_clicks_24h", "profile_visits_24h"),
    "link_intents_24h": ("link_intents_24h", "link_clicks_24h", "clicks_24h"),
    "dm_intents_72h": ("dm_intents_72h", "dm_intents_24h"),
}

PLATFORM_ALIASES = {
    "x": "x",
    "twitter": "x",
    "xiaohongshu": "xiaohongshu",
    "xhs": "xiaohongshu",
    "小红书": "xiaohongshu",
}

PROOF_SCORES = {
    "subjective_opinion_only": 1,
    "real_product_usage": 2,
    "screenshot_proof": 3,
    "benchmark_data": 4,
}

DEFAULT_PRIMARY = {
    ("xiaohongshu", "save"): "xhs_save_rate",
    ("xiaohongshu", "discussion"): "xhs_discussion_rate",
    ("xiaohongshu", "profile_visit"): "xhs_profile_visit_rate",
    ("xiaohongshu", "dm"): "xhs_dm_intent_rate",
    ("xiaohongshu", "product_question"): "xhs_product_relevance_rate",
    ("xiaohongshu", "trial_intent"): "xhs_product_relevance_rate",
    ("x", "save"): "x_bookmark_rate",
    ("x", "discussion"): "x_qualified_reply_rate",
    ("x", "profile_visit"): "x_profile_click_rate",
    ("x", "dm"): "x_profile_click_rate",
    ("x", "link_click"): "x_link_intent_rate",
    ("x", "product_question"): "x_product_relevance_rate",
    ("x", "trial_intent"): "x_product_relevance_rate",
}


def raw_text(row: dict[str, Any], key: str) -> str:
    keys = ALIASES.get(key, (key,))
    for candidate in keys:
        value = str(row.get(candidate, "") or "").strip()
        if value:
            return value
    return ""


def number(value: Any) -> float | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        if raw.endswith("%"):
            return float(raw[:-1].replace(",", "")) / 100
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def get_number(row: dict[str, Any], key: str) -> float | None:
    keys = ALIASES.get(key, (key,))
    for candidate in keys:
        value = number(row.get(candidate))
        if value is not None:
            return value
    return None


def integer(value: Any) -> int | None:
    parsed = number(value)
    return int(parsed) if parsed is not None and parsed.is_integer() else None


def truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def sum_known(*values: float | None) -> float | None:
    present = [value for value in values if value is not None]
    return sum(present) if present else None


def median_or_none(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.median(present) if present else None


def mean_or_none(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.fmean(present) if present else None


def lift(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline is None or baseline == 0:
        return None
    return value / baseline - 1


def band(value: float | None, baseline: float | None) -> tuple[str, float | None]:
    delta = lift(value, baseline)
    if delta is None:
        return "unknown", None
    if delta >= 0.20 - EPSILON:
        return "high", delta
    if delta <= -0.20 + EPSILON:
        return "low", delta
    return "normal", delta


def normalize_platform(value: str) -> str:
    return PLATFORM_ALIASES.get(value.strip().lower(), value.strip().lower())


def normalize_row(source: dict[str, str], row_number: int) -> dict[str, Any]:
    row: dict[str, Any] = dict(source)
    row["_row_number"] = row_number
    row["platform"] = normalize_platform(raw_text(row, "platform"))
    row["pillar"] = raw_text(row, "pillar")
    row["audience_stage"] = raw_text(row, "audience_stage")
    row["proof_type"] = raw_text(row, "proof_type")
    row["cta_type"] = raw_text(row, "cta_type")
    row["hypothesis_variable"] = raw_text(row, "hypothesis_variable")
    row["template_id"] = raw_text(row, "template_id")
    return row


def validate_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("post_id", "platform", "pillar", "audience_stage", "proof_type", "cta_type", "hypothesis_variable", "status")
    for field in required:
        if not raw_text(row, field):
            errors.append(f"missing:{field}")
    checks = (
        ("platform", PLATFORMS),
        ("pillar", PILLARS),
        ("audience_stage", AUDIENCE_STAGES),
        ("proof_type", PROOF_TYPES),
        ("cta_type", CTA_TYPES),
        ("hypothesis_variable", HYPOTHESIS_VARIABLES),
    )
    for field, allowed in checks:
        value = raw_text(row, field)
        if value and value not in allowed:
            errors.append(f"invalid:{field}={value}")
    changed = integer(row.get("changed_variable_count"))
    if changed is None:
        errors.append("missing_or_invalid:changed_variable_count")
    return errors


def evidence_score(row: dict[str, Any]) -> int:
    supplied = integer(row.get("evidence_strength_score"))
    flags = {
        key: truthy(row.get(key))
        for key in ("real_product_usage", "screenshot_proof", "benchmark_data", "subjective_opinion_only")
    }
    has_artifact = bool(raw_text(row, "proof_artifact") or raw_text(row, "source_reference"))
    if flags["benchmark_data"] and has_artifact:
        supported = 4
    elif flags["real_product_usage"] and flags["screenshot_proof"] and has_artifact:
        supported = 4
    elif flags["screenshot_proof"] and has_artifact:
        supported = 3
    elif flags["real_product_usage"]:
        supported = 2
    else:
        supported = PROOF_SCORES.get(raw_text(row, "proof_type"), 1)
    if supplied is not None and 1 <= supplied <= 4:
        return min(supplied, supported)
    return supported


def calculate_metrics(row: dict[str, Any]) -> dict[str, float | None]:
    impressions = get_number(row, "impressions_24h")
    views = get_number(row, "views_24h")
    saves = get_number(row, "saves_24h")
    completed = get_number(row, "completed_views_24h")
    likes = get_number(row, "likes_24h")
    comments = get_number(row, "comments_24h")
    replies = get_number(row, "replies_24h")
    qualified_replies = get_number(row, "qualified_replies_72h")
    reposts = get_number(row, "reposts_24h")
    bookmarks = get_number(row, "bookmarks_24h")
    engagements = get_number(row, "engagements_24h")
    if engagements is None:
        engagements = sum_known(likes, replies if replies is not None else comments, reposts, bookmarks)
    profile_visits = get_number(row, "profile_visits_24h")
    profile_clicks = get_number(row, "profile_clicks_24h")
    link_intents = get_number(row, "link_intents_24h")
    dm_intents = get_number(row, "dm_intents_72h")
    questions = get_number(row, "product_questions_72h")
    trials = get_number(row, "trial_intents_72h")
    product_actions = sum_known(questions, trials)

    metrics: dict[str, float | None] = {
        "reach_value": impressions,
        "xhs_save_rate": safe_ratio(saves, views),
        "xhs_completion_rate": safe_ratio(completed, views),
        "xhs_profile_visit_rate": safe_ratio(profile_visits, views),
        "xhs_dm_intent_rate": safe_ratio(dm_intents, views),
        "xhs_discussion_rate": safe_ratio(comments, views),
        "xhs_product_relevance_rate": safe_ratio(product_actions, views),
        "x_first_screen_engaged_rate_proxy": safe_ratio(engagements, impressions),
        "x_qualified_reply_rate": safe_ratio(qualified_replies, impressions),
        "x_profile_click_rate": safe_ratio(profile_clicks, impressions),
        "x_link_intent_rate": safe_ratio(link_intents, impressions),
        "x_bookmark_rate": safe_ratio(bookmarks, impressions),
        "x_product_relevance_rate": safe_ratio(product_actions, impressions),
    }
    platform = row["platform"]
    cta = row["cta_type"]
    primary_default = DEFAULT_PRIMARY.get((platform, cta))
    metrics["cta_conversion_rate"] = metrics.get(primary_default) if primary_default else None
    if platform == "xiaohongshu":
        metrics["retention_value"] = median_or_none((metrics["xhs_save_rate"], metrics["xhs_completion_rate"]))
        metrics["interaction_value"] = metrics["xhs_discussion_rate"]
        metrics["product_relevance_value"] = metrics["xhs_product_relevance_rate"]
    else:
        metrics["retention_value"] = metrics["x_bookmark_rate"]
        metrics["interaction_value"] = metrics["x_qualified_reply_rate"]
        metrics["product_relevance_value"] = metrics["x_product_relevance_rate"]
    metrics["conversion_value"] = metrics["cta_conversion_rate"]
    return metrics


def metric_value(row: dict[str, Any], metrics: dict[str, float | None], metric_name: str) -> float | None:
    supplied = get_number(row, f"{metric_name}_value")
    if supplied is not None:
        return supplied
    supplied = get_number(row, "primary_metric_value") if metric_name == raw_text(row, "primary_metric") else None
    if supplied is not None:
        return supplied
    return metrics.get(metric_name)


def evaluate_row(row: dict[str, Any]) -> dict[str, Any]:
    errors = validate_row(row)
    metrics = calculate_metrics(row)
    platform = row["platform"]
    cta = row["cta_type"]
    primary_metric = raw_text(row, "primary_metric") or DEFAULT_PRIMARY.get((platform, cta), "")
    guardrail_metric = raw_text(row, "guardrail_metric")
    primary_value = metric_value(row, metrics, primary_metric) if primary_metric else None
    guardrail_value = metric_value(row, metrics, guardrail_metric) if guardrail_metric else None
    baseline_primary = get_number(row, "baseline_primary_value")
    baseline_guardrail = get_number(row, "baseline_guardrail_value")
    primary_lift = lift(primary_value, baseline_primary)
    guardrail_lift = lift(guardrail_value, baseline_guardrail) if guardrail_metric else None

    changed = integer(row.get("changed_variable_count"))
    if changed == 1:
        discipline = "pure"
    elif changed == 0:
        discipline = "baseline"
    elif changed is not None and changed > 1:
        discipline = "mixed"
    else:
        discipline = "unknown"

    status = raw_text(row, "status").lower()
    anomaly_flags = any(
        truthy(row.get(key))
        for key in ("anomaly_flag", "paid_support", "external_boost", "deleted_reposted", "platform_penalty")
    ) or status in ANOMALY_STATUSES
    attribution_reasons: list[str] = []
    if status not in COMPLETE_STATUSES:
        attribution_reasons.append("status_not_complete")
    if discipline != "pure":
        attribution_reasons.append(f"variable_discipline_{discipline}")
    if anomaly_flags:
        attribution_reasons.append("anomaly_or_external_influence")
    if primary_value is None:
        attribution_reasons.append("missing_primary_value")
    if baseline_primary is None:
        attribution_reasons.append("missing_baseline_primary")
    if guardrail_metric and (guardrail_value is None or baseline_guardrail is None):
        attribution_reasons.append("missing_guardrail_comparison")
    if errors:
        attribution_reasons.append("schema_error")
    attributable = not attribution_reasons

    diagnostic_values = {
        "reach": metrics["reach_value"],
        "retention": metrics["retention_value"],
        "interaction": metrics["interaction_value"],
        "conversion": metrics["conversion_value"],
        "product_relevance": metrics["product_relevance_value"],
    }
    bands: dict[str, str] = {}
    band_lifts: dict[str, float | None] = {}
    for name, value in diagnostic_values.items():
        supplied_band = raw_text(row, f"{name}_band").lower()
        if supplied_band in {"high", "normal", "low", "unknown"}:
            bands[name] = supplied_band
            band_lifts[name] = get_number(row, f"{name}_lift")
        else:
            bands[name], band_lifts[name] = band(value, get_number(row, f"baseline_{name}_value"))

    tracking_issue = status in COMPLETE_STATUSES and (
        bool(errors) or primary_value is None or baseline_primary is None
    )
    guardrail_failed = guardrail_lift is not None and guardrail_lift <= -0.20 + EPSILON
    viral_unattributable = not attributable and (
        bands["reach"] == "high" or (primary_lift is not None and primary_lift >= 0.20 - EPSILON)
    )

    if status not in COMPLETE_STATUSES:
        win_status = "not_evaluated"
    elif tracking_issue:
        win_status = "insufficient_data"
    elif guardrail_failed:
        win_status = "guardrail_fail"
    elif viral_unattributable:
        win_status = "watchlist"
    elif not attributable:
        win_status = "insufficient_data"
    elif primary_lift is not None and primary_lift >= 0.20 - EPSILON:
        win_status = "win"
    elif primary_lift is not None and primary_lift <= -0.20 + EPSILON:
        win_status = "loss"
    else:
        win_status = "inconclusive"

    if tracking_issue:
        next_action = "FIX_TRACKING"
    elif guardrail_failed:
        next_action = "STOP_VARIANT_GUARDRAIL"
    elif viral_unattributable:
        next_action = "WATCHLIST_ONLY"
    elif bands["reach"] == "high" and bands["conversion"] == "low":
        next_action = "KEEP_HOOK_REWRITE_CTA"
    elif bands["retention"] == "high" and bands["interaction"] == "low":
        next_action = "KEEP_STRUCTURE_CHANGE_DISCUSSION_ANGLE"
    elif bands["interaction"] == "high" and bands["product_relevance"] == "low":
        next_action = "DOWNWEIGHT_TEMPLATE"
    elif win_status == "win":
        next_action = "RETEST_WINNER"
    elif win_status == "loss":
        next_action = "RETURN_TO_BASELINE"
    else:
        next_action = "COLLECT_MORE_DATA"

    return {
        "post_id": raw_text(row, "post_id"),
        "platform": platform,
        "account": raw_text(row, "account"),
        "pillar": row["pillar"],
        "audience_stage": row["audience_stage"],
        "proof_type": row["proof_type"],
        "evidence_strength_score": evidence_score(row),
        "cta_type": cta,
        "hypothesis_variable": row["hypothesis_variable"],
        "changed_variable_count": changed,
        "variable_discipline": discipline,
        "template_id": row["template_id"],
        "test_block": raw_text(row, "test_block"),
        "status": status,
        "schema_errors": errors,
        "metrics": metrics,
        "primary_metric": primary_metric,
        "primary_metric_value": primary_value,
        "baseline_primary_value": baseline_primary,
        "primary_lift": primary_lift,
        "guardrail_metric": guardrail_metric,
        "guardrail_metric_value": guardrail_value,
        "baseline_guardrail_value": baseline_guardrail,
        "guardrail_lift": guardrail_lift,
        "bands": bands,
        "band_lifts": band_lifts,
        "attribution_status": "attributable" if attributable else "not_attributable",
        "attribution_reasons": attribution_reasons,
        "win_status": win_status,
        "next_action_code": next_action,
    }


def win_rate_by(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(field, "") or "unlabeled")].append(row)
    result = []
    for key in sorted(groups):
        items = groups[key]
        evaluated = [r for r in items if r["attribution_status"] == "attributable" and r["win_status"] != "not_evaluated"]
        wins = sum(r["win_status"] == "win" for r in evaluated)
        result.append({
            field: key,
            "records": len(items),
            "attributable_complete": len(evaluated),
            "wins": wins,
            "win_rate": wins / len(evaluated) if evaluated else None,
            "average_evidence_strength": mean_or_none(r["evidence_strength_score"] for r in items),
        })
    return result


def platform_cta_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["platform"], row["cta_type"])].append(row)
    result = []
    for (platform, cta), items in sorted(groups.items()):
        evaluated = [r for r in items if r["attribution_status"] == "attributable"]
        wins = sum(r["win_status"] == "win" for r in evaluated)
        result.append({
            "platform": platform,
            "cta_type": cta,
            "records": len(items),
            "attributable_complete": len(evaluated),
            "wins": wins,
            "win_rate": wins / len(evaluated) if evaluated else None,
            "median_cta_conversion_rate": median_or_none(r["metrics"].get("cta_conversion_rate") for r in evaluated),
            "median_primary_lift": median_or_none(r["primary_lift"] for r in evaluated),
        })
    return result


def reuse_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["template_id"]:
            groups[(row["platform"], row["template_id"])].append(row)
    result = []
    for (platform, template_id), items in sorted(groups.items()):
        eligible = [r for r in items if r["attribution_status"] == "attributable"]
        uses = len(eligible)
        wins = sum(r["win_status"] == "win" for r in eligible)
        guardrail_fails = sum(r["win_status"] == "guardrail_fail" for r in eligible)
        block_count = len({r["test_block"] for r in eligible if r["test_block"]})
        median_lift = median_or_none(r["primary_lift"] for r in eligible)
        win_rate = wins / uses if uses else None
        candidate = (
            uses >= 3
            and wins >= 2
            and win_rate is not None
            and win_rate >= 2 / 3
            and median_lift is not None
            and median_lift > 0
            and guardrail_fails == 0
            and block_count >= 2
        )
        if candidate:
            status = "playbook_candidate"
        elif uses >= 1:
            status = "watchlist"
        else:
            status = "not_eligible"
        result.append({
            "platform": platform,
            "template_id": template_id,
            "attributable_uses": uses,
            "wins": wins,
            "win_rate": win_rate,
            "median_primary_lift": median_lift,
            "test_blocks": block_count,
            "guardrail_fails": guardrail_fails,
            "reuse_value": status,
        })
    return result


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [row for row in rows if row["status"] in COMPLETE_STATUSES]
    pure = [row for row in completed if row["variable_discipline"] == "pure"]
    return {
        "action": "evaluate_experiment_result",
        "summary": {
            "records": len(rows),
            "complete_records": len(completed),
            "attributable_records": sum(row["attribution_status"] == "attributable" for row in completed),
            "wins": sum(row["win_status"] == "win" for row in rows),
            "watchlist_records": sum(row["win_status"] == "watchlist" for row in rows),
            "variable_discipline_purity": len(pure) / len(completed) if completed else None,
        },
        "pillar_win_rate": win_rate_by(rows, "pillar"),
        "proof_type_win_rate": win_rate_by(rows, "proof_type"),
        "platform_cta_conversion": platform_cta_summary(rows),
        "reuse_value": reuse_summary(rows),
        "rows": rows,
    }


def fmt_pct(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def markdown_table(headers: list[str], records: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for record in records:
        lines.append("| " + " | ".join(str(value) for value in record) + " |")
    return "\n".join(lines)


def markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# ARTi 实验评估",
        "",
        f"- 记录：{summary['records']}",
        f"- 完整记录：{summary['complete_records']}",
        f"- 可归因记录：{summary['attributable_records']}",
        f"- 实验纯度：{fmt_pct(summary['variable_discipline_purity'])}",
        f"- Wins：{summary['wins']}；Watchlist：{summary['watchlist_records']}",
        "",
        "## 单条决策",
        "",
        markdown_table(
            ["post_id", "平台", "pillar", "主指标 lift", "归因", "结果", "下一步"],
            [[
                row["post_id"], row["platform"], row["pillar"], fmt_pct(row["primary_lift"]),
                row["attribution_status"], row["win_status"], row["next_action_code"],
            ] for row in report["rows"]],
        ),
        "",
        "## Pillar 胜率",
        "",
        markdown_table(
            ["pillar", "记录", "可归因", "wins", "win rate", "平均证据分"],
            [[r["pillar"], r["records"], r["attributable_complete"], r["wins"], fmt_pct(r["win_rate"]),
              "—" if r["average_evidence_strength"] is None else f"{r['average_evidence_strength']:.2f}"]
             for r in report["pillar_win_rate"]],
        ),
        "",
        "## Proof type 胜率",
        "",
        markdown_table(
            ["proof type", "记录", "可归因", "wins", "win rate", "平均证据分"],
            [[r["proof_type"], r["records"], r["attributable_complete"], r["wins"], fmt_pct(r["win_rate"]),
              "—" if r["average_evidence_strength"] is None else f"{r['average_evidence_strength']:.2f}"]
             for r in report["proof_type_win_rate"]],
        ),
        "",
        "## Platform × CTA",
        "",
        markdown_table(
            ["平台", "CTA", "记录", "可归因", "win rate", "中位转化", "中位 lift"],
            [[r["platform"], r["cta_type"], r["records"], r["attributable_complete"], fmt_pct(r["win_rate"]),
              fmt_pct(r["median_cta_conversion_rate"]), fmt_pct(r["median_primary_lift"])]
             for r in report["platform_cta_conversion"]],
        ),
        "",
        "## Reuse value",
        "",
        markdown_table(
            ["平台", "template", "uses", "wins", "win rate", "中位 lift", "blocks", "状态"],
            [[r["platform"], r["template_id"], r["attributable_uses"], r["wins"], fmt_pct(r["win_rate"]),
              fmt_pct(r["median_primary_lift"]), r["test_blocks"], r["reuse_value"]]
             for r in report["reuse_value"]],
        ),
        "",
        "> 结果只表示匹配样本中的当前信号；不可归因单条不会提升 baseline 或 playbook。",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate ARTi social experiment CSV data.")
    parser.add_argument("csv_path", type=Path, help="CSV exported from the Experiment Log sheet")
    parser.add_argument("--json-output", type=Path, help="Optional path for machine-readable JSON")
    parser.add_argument("--markdown-output", type=Path, help="Optional path for Markdown report")
    args = parser.parse_args()

    with args.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    rows = [evaluate_row(normalize_row(row, index + 2)) for index, row in enumerate(source_rows)]
    report = build_report(rows)
    markdown = markdown_report(report)
    print(markdown)

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
