#!/usr/bin/env python3
"""Deterministic unit economics and A/B test sizing calculator.

Provides three subcommands:
  - retention-profit: cohort survival profit, cannibalization, ROI, and payback
  - breakeven: LTV contribution, break-even units, and payback horizon
  - ab-size: two-proportion z-test sample size and weekly enrollment feasibility

Outputs structured JSON and Markdown reports so LLMs never do ad-hoc math.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

import numpy as np

NL = chr(10)


def _validate_prob(val: float, name: str) -> None:
    if not (0.0 <= val <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {val}")


def calc_retention_profit(
    base_users: int,
    baseline_churn: float,
    new_churn: float,
    arpu: float,
    margin: float = 0.70,
    horizon_months: int = 12,
    promo_cost_per_user: float = 0.0,
    fixed_cost: float = 0.0,
    cannibalization_per_user: float = 0.0,
) -> dict[str, Any]:
    if base_users <= 0:
        raise ValueError("base_users must be > 0")
    if horizon_months <= 0:
        raise ValueError("horizon_months must be > 0")
    _validate_prob(baseline_churn, "baseline_churn")
    _validate_prob(new_churn, "new_churn")
    _validate_prob(margin, "margin")

    months = np.arange(1, horizon_months + 1, dtype=float)
    base_active = base_users * np.power(1.0 - baseline_churn, months)
    new_active = base_users * np.power(1.0 - new_churn, months)

    monthly_inc_users = new_active - base_active
    monthly_gross_contrib = monthly_inc_users * arpu * margin
    monthly_cannibalization = new_active * cannibalization_per_user * margin
    monthly_net_contrib = monthly_gross_contrib - monthly_cannibalization

    total_upfront = fixed_cost + base_users * promo_cost_per_user
    cum_net_profit = np.cumsum(monthly_net_contrib) - total_upfront

    payback_month: int | None = None
    reached = np.where(cum_net_profit >= 0.0)[0]
    if reached.size > 0:
        payback_month = int(reached[0] + 1)

    base_user_months = float(np.sum(base_active))
    new_user_months = float(np.sum(new_active))
    inc_user_months = float(new_user_months - base_user_months)
    gross_inc_margin = float(np.sum(monthly_gross_contrib))
    total_cannib = float(np.sum(monthly_cannibalization))
    total_promo = float(base_users * promo_cost_per_user)
    net_profit = float(gross_inc_margin - total_cannib - total_promo - fixed_cost)
    roi_pct = (net_profit / total_upfront * 100.0) if total_upfront > 0 else None

    return {
        "calculation": "retention_profit",
        "inputs": {
            "base_users": base_users,
            "baseline_churn_monthly": baseline_churn,
            "new_churn_monthly": new_churn,
            "churn_reduction_pp": round((baseline_churn - new_churn) * 100.0, 4),
            "arpu_rub": arpu,
            "margin": margin,
            "horizon_months": horizon_months,
            "promo_cost_per_user_rub": promo_cost_per_user,
            "fixed_cost_rub": fixed_cost,
            "cannibalization_per_user_monthly_rub": cannibalization_per_user,
        },
        "results": {
            "baseline_user_months": round(base_user_months, 2),
            "new_user_months": round(new_user_months, 2),
            "incremental_user_months": round(inc_user_months, 2),
            "saved_users_end_of_horizon": round(float(new_active[-1] - base_active[-1]), 2),
            "gross_incremental_margin_rub": round(gross_inc_margin, 2),
            "cannibalization_loss_rub": round(total_cannib, 2),
            "total_promo_cost_rub": round(total_promo, 2),
            "fixed_cost_rub": round(fixed_cost, 2),
            "net_incremental_profit_rub": round(net_profit, 2),
            "roi_pct": round(roi_pct, 2) if roi_pct is not None else None,
            "payback_month": payback_month,
        },
    }


def calc_breakeven(
    fixed_cost: float,
    unit_margin: float,
    avg_lifetime_months: float = 12.0,
    cac_or_promo: float = 0.0,
    monthly_opex: float = 0.0,
    monthly_new_units: float | None = None,
    max_horizon_months: int = 60,
) -> dict[str, Any]:
    if avg_lifetime_months <= 0:
        raise ValueError("avg_lifetime_months must be > 0")
    if fixed_cost < 0 or monthly_opex < 0 or cac_or_promo < 0:
        raise ValueError("Costs must be non-negative")

    unit_ltv_contrib = unit_margin * avg_lifetime_months - cac_or_promo
    breakeven_units_fixed = (fixed_cost / unit_ltv_contrib) if unit_ltv_contrib > 0 else None
    monthly_units_for_opex = (monthly_opex / unit_ltv_contrib) if (unit_ltv_contrib > 0 and monthly_opex > 0) else 0.0

    payback_month: int | None = None
    steady_monthly_net: float | None = None
    if monthly_new_units is not None and monthly_new_units > 0:
        lifetime_int = max(1, int(round(avg_lifetime_months)))
        cum_cash = -fixed_cost
        for m in range(1, max_horizon_months + 1):
            active_units = monthly_new_units * min(m, lifetime_int)
            monthly_cash = active_units * unit_margin - monthly_new_units * cac_or_promo - monthly_opex
            cum_cash += monthly_cash
            if m == lifetime_int:
                steady_monthly_net = monthly_cash
            if payback_month is None and cum_cash >= 0.0:
                payback_month = m
        if steady_monthly_net is None:
            steady_monthly_net = (
                monthly_new_units * avg_lifetime_months * unit_margin
                - monthly_new_units * cac_or_promo
                - monthly_opex
            )

    return {
        "calculation": "breakeven",
        "inputs": {
            "fixed_cost_rub": fixed_cost,
            "monthly_opex_rub": monthly_opex,
            "unit_margin_monthly_rub": unit_margin,
            "avg_lifetime_months": avg_lifetime_months,
            "cac_or_promo_rub": cac_or_promo,
            "monthly_new_units": monthly_new_units,
        },
        "results": {
            "unit_ltv_contribution_rub": round(unit_ltv_contrib, 2),
            "unit_economics_positive": unit_ltv_contrib > 0,
            "breakeven_units_for_fixed_cost": math.ceil(breakeven_units_fixed) if breakeven_units_fixed is not None else None,
            "monthly_units_to_cover_opex": math.ceil(monthly_units_for_opex) if unit_ltv_contrib > 0 else None,
            "payback_months_at_pace": payback_month,
            "steady_state_monthly_net_rub": round(steady_monthly_net, 2) if steady_monthly_net is not None else None,
        },
    }


def calc_ab_size(
    p1: float,
    mde: float | None = None,
    relative_mde: float | None = None,
    alpha: float = 0.05,
    power: float = 0.80,
    ratio: float = 1.0,
    two_sided: bool = True,
    weekly_enrollment: float | None = None,
    maturation_days: int = 0,
) -> dict[str, Any]:
    _validate_prob(p1, "p1")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0, 1)")
    if not (0.0 < power < 1.0):
        raise ValueError("power must be in (0, 1)")
    if ratio <= 0:
        raise ValueError("ratio must be > 0")
    if (mde is None) == (relative_mde is None):
        raise ValueError("Provide exactly one of --mde (absolute) or --relative-mde")

    abs_mde = mde if mde is not None else p1 * float(relative_mde)
    if abs_mde == 0:
        raise ValueError("MDE must be non-zero")
    p2 = p1 + abs_mde
    if not (0.0 < p2 < 1.0):
        raise ValueError(f"Resulting treatment proportion p2={p2:.4f} must be strictly in (0, 1)")

    nd = statistics.NormalDist()
    z_alpha = nd.inv_cdf(1.0 - alpha / 2.0) if two_sided else nd.inv_cdf(1.0 - alpha)
    z_beta = nd.inv_cdf(power)

    p_bar = (p1 + ratio * p2) / (1.0 + ratio)
    num = (
        z_alpha * math.sqrt(p_bar * (1.0 - p_bar) * (1.0 + 1.0 / ratio))
        + z_beta * math.sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2) / ratio)
    ) ** 2
    n_control = math.ceil(num / ((p2 - p1) ** 2))
    n_treatment = math.ceil(n_control * ratio)
    total_sample = n_control + n_treatment

    enrollment_weeks: float | None = None
    maturation_weeks = maturation_days / 7.0
    total_weeks: float | None = None
    feasible_12w: bool | None = None
    if weekly_enrollment is not None:
        if weekly_enrollment <= 0:
            raise ValueError("weekly_enrollment must be > 0")
        enrollment_weeks = total_sample / weekly_enrollment
        total_weeks = enrollment_weeks + maturation_weeks
        feasible_12w = total_weeks <= 12.0

    return {
        "calculation": "ab_sample_size",
        "inputs": {
            "p1_baseline": p1,
            "p2_target": round(p2, 6),
            "absolute_mde": round(abs_mde, 6),
            "relative_mde_pct": round((abs_mde / p1) * 100.0, 2) if p1 > 0 else None,
            "alpha": alpha,
            "power": power,
            "ratio_treatment_to_control": ratio,
            "two_sided": two_sided,
            "weekly_enrollment": weekly_enrollment,
            "maturation_days": maturation_days,
        },
        "results": {
            "n_control": n_control,
            "n_treatment": n_treatment,
            "total_sample_size": total_sample,
            "enrollment_weeks": round(enrollment_weeks, 2) if enrollment_weeks is not None else None,
            "maturation_weeks": round(maturation_weeks, 2),
            "total_duration_weeks": round(total_weeks, 2) if total_weeks is not None else None,
            "feasible_within_12_weeks": feasible_12w,
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    calc_type = payload["calculation"]
    lines = [f"### Deterministic Calculation: `{calc_type}` `[CALC]`", "", "| Metric | Value |", "|---|---|"]
    for k, v in payload["results"].items():
        if isinstance(v, float):
            formatted = f"{v:,.2f}"
        elif isinstance(v, int) and not isinstance(v, bool):
            formatted = f"{v:,}"
        else:
            formatted = str(v)
        lines.append(f"| `{k}` | {formatted} |")
    lines.append("")
    lines.append("**Inputs:** " + ", ".join(f"`{k}={v}`" for k, v in payload["inputs"].items()))
    return NL.join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic unit economics & A/B test sizing CLI (outputs JSON + Markdown)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=["both", "json", "markdown"], default="both", help="Stdout format")
    common.add_argument("--output-json", default=None, help="Optional file path to save JSON output")
    common.add_argument("--output-md", default=None, help="Optional file path to save Markdown output")

    p_ret = sub.add_parser("retention-profit", parents=[common], help="Calculate retention cohort profit, ROI, and payback")
    p_ret.add_argument("--base-users", type=int, required=True, help="Cohort size (users or households)")
    p_ret.add_argument("--baseline-churn", type=float, required=True, help="Baseline monthly churn rate (e.g., 0.035)")
    p_ret.add_argument("--new-churn", type=float, required=True, help="Post-intervention monthly churn rate (e.g., 0.025)")
    p_ret.add_argument("--arpu", type=float, required=True, help="Monthly ARPU in RUB")
    p_ret.add_argument("--margin", type=float, default=0.70, help="Contribution margin ratio (default: 0.70)")
    p_ret.add_argument("--horizon-months", type=int, default=12, help="Evaluation horizon in months (default: 12)")
    p_ret.add_argument("--promo-cost-per-user", type=float, default=0.0, help="Upfront promo/incentive cost per user in RUB")
    p_ret.add_argument("--fixed-cost", type=float, default=0.0, help="Fixed dev/launch cost in RUB")
    p_ret.add_argument("--cannibalization-per-user", type=float, default=0.0, help="Monthly ARPU dilution per active user in RUB")

    p_be = sub.add_parser("breakeven", parents=[common], help="Calculate break-even units and payback horizon")
    p_be.add_argument("--fixed-cost", type=float, required=True, help="One-time fixed investment in RUB")
    p_be.add_argument("--unit-margin", type=float, required=True, help="Net monthly contribution margin per unit in RUB")
    p_be.add_argument("--avg-lifetime-months", type=float, default=12.0, help="Average retained lifetime in months (default: 12)")
    p_be.add_argument("--cac-or-promo", type=float, default=0.0, help="One-time CAC or promo cost per unit in RUB")
    p_be.add_argument("--monthly-opex", type=float, default=0.0, help="Ongoing monthly fixed OPEX in RUB")
    p_be.add_argument("--monthly-new-units", type=float, default=None, help="Expected new units/month to estimate payback months")

    p_ab = sub.add_parser("ab-size", parents=[common], help="Calculate two-proportion A/B sample size and enrollment pace")
    p_ab.add_argument("--p1", type=float, required=True, help="Baseline conversion/retention proportion (0..1)")
    p_ab.add_argument("--mde", type=float, default=None, help="Absolute minimum detectable effect (e.g., 0.02 for +2 pp)")
    p_ab.add_argument("--relative-mde", type=float, default=None, help="Relative MDE (e.g., 0.10 for +10%% relative)")
    p_ab.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05)")
    p_ab.add_argument("--power", type=float, default=0.80, help="Statistical power (default: 0.80)")
    p_ab.add_argument("--ratio", type=float, default=1.0, help="Treatment-to-control allocation ratio (default: 1.0)")
    p_ab.add_argument("--one-sided", action="store_true", help="Use one-sided test instead of two-sided")
    p_ab.add_argument("--weekly-enrollment", type=float, default=None, help="Eligible households/users enrolled per week")
    p_ab.add_argument("--maturation-days", type=int, default=0, help="Metric maturation window in days (e.g., 30 or 60)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "retention-profit":
            payload = calc_retention_profit(
                base_users=args.base_users,
                baseline_churn=args.baseline_churn,
                new_churn=args.new_churn,
                arpu=args.arpu,
                margin=args.margin,
                horizon_months=args.horizon_months,
                promo_cost_per_user=args.promo_cost_per_user,
                fixed_cost=args.fixed_cost,
                cannibalization_per_user=args.cannibalization_per_user,
            )
        elif args.command == "breakeven":
            payload = calc_breakeven(
                fixed_cost=args.fixed_cost,
                unit_margin=args.unit_margin,
                avg_lifetime_months=args.avg_lifetime_months,
                cac_or_promo=args.cac_or_promo,
                monthly_opex=args.monthly_opex,
                monthly_new_units=args.monthly_new_units,
            )
        elif args.command == "ab-size":
            payload = calc_ab_size(
                p1=args.p1,
                mde=args.mde,
                relative_mde=args.relative_mde,
                alpha=args.alpha,
                power=args.power,
                ratio=args.ratio,
                two_sided=not args.one_sided,
                weekly_enrollment=args.weekly_enrollment,
                maturation_days=args.maturation_days,
            )
        else:
            raise ValueError(f"Unknown command: {args.command}")
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    md_text = render_markdown(payload)
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_json).write_text(json_text + NL, encoding="utf-8")
    if args.output_md:
        Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output_md).write_text(md_text + NL, encoding="utf-8")

    if args.format == "json":
        print(json_text)
    elif args.format == "markdown":
        print(md_text)
    else:
        print(md_text)
        print(f"{NL}```json{NL}{json_text}{NL}```")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
