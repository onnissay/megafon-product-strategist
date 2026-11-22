#!/usr/bin/env python3
"""Run ledger CLI for tracking workflow steps, models, token/cost telemetry, and artifacts.

Stores append-only run entries in projects/<project>/state/run_ledger.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NL = chr(10)

# Indicative pricing per 1M tokens (input_usd, output_usd) for cost estimation
MODEL_PRICING_PER_1M: dict[str, tuple[float, float]] = {
    "gemini-2.5-pro": (1.25, 10.00),
    "gemini-2.5-flash": (0.30, 2.50),
    "claude-sonnet-4": (3.00, 15.00),
    "claude-opus-4": (15.00, 75.00),
    "gpt-5": (1.25, 10.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "python-cli": (0.00, 0.00),
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    key = model.lower().strip()
    in_rate, out_rate = MODEL_PRICING_PER_1M.get(key, (1.25, 10.00))
    return (input_tokens / 1_000_000.0) * in_rate + (output_tokens / 1_000_000.0) * out_rate


def load_ledger(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"entries": []}


def save_ledger(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + NL, encoding="utf-8")


def cmd_log(args: argparse.Namespace) -> int:
    ledger_path = Path(args.projects_root) / args.project / "state" / "run_ledger.json"
    ledger = load_ledger(ledger_path)

    cost_usd = (
        args.cost_usd
        if args.cost_usd is not None
        else estimate_cost_usd(args.model, args.input_tokens, args.output_tokens)
    )
    cost_rub = cost_usd * args.usd_rub

    artifacts: list[str] = []
    for raw in args.artifact or []:
        for item in raw.split(","):
            cleaned = item.strip()
            if cleaned:
                artifacts.append(cleaned)

    entry: dict[str, Any] = {
        "run_id": f"RUN-{len(ledger['entries']) + 1:03d}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": args.step,
        "model": args.model,
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
        "total_tokens": args.input_tokens + args.output_tokens,
        "cost_usd": round(cost_usd, 6),
        "cost_rub": round(cost_rub, 2),
        "usd_rub_rate": args.usd_rub,
        "status": args.status,
        "artifacts": artifacts,
        "notes": args.notes,
    }
    ledger["entries"].append(entry)
    save_ledger(ledger_path, ledger)
    print(json.dumps({"status": "logged", "entry": entry}, ensure_ascii=False, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    ledger_path = Path(args.projects_root) / args.project / "state" / "run_ledger.json"
    ledger = load_ledger(ledger_path)
    entries = ledger.get("entries", [])

    total_in = sum(int(e.get("input_tokens", 0)) for e in entries)
    total_out = sum(int(e.get("output_tokens", 0)) for e in entries)
    total_usd = round(sum(float(e.get("cost_usd", 0.0)) for e in entries), 6)
    total_rub = round(sum(float(e.get("cost_rub", 0.0)) for e in entries), 2)
    latest = entries[-1] if entries else None
    all_artifacts = sorted({a for e in entries for a in e.get("artifacts", [])})

    summary = {
        "project": args.project,
        "runs_count": len(entries),
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "total_tokens": total_in + total_out,
        "total_cost_usd": total_usd,
        "total_cost_rub": total_rub,
        "latest_step": latest["step"] if latest else None,
        "latest_status": latest["status"] if latest else None,
        "artifacts_count": len(all_artifacts),
        "artifacts": all_artifacts,
        "entries": entries,
    }

    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    lines = [
        f"### Run Ledger Status: `{args.project}`",
        "",
        f"- **Runs logged**: {summary['runs_count']}",
        f"- **Latest step / status**: `{summary['latest_step']}` / `{summary['latest_status']}`",
        f"- **Total tokens**: {summary['total_tokens']:,} (in: {total_in:,}, out: {total_out:,})",
        f"- **Estimated cost**: ${total_usd:.4f} USD / {total_rub:.2f} RUB",
        f"- **Artifacts tracked**: {summary['artifacts_count']}",
        "",
        "| Run ID | Step | Model | Tokens | Cost (USD / RUB) | Status |",
        "|---|---|---|---:|---:|---|",
    ]
    for e in entries:
        lines.append(
            f"| {e['run_id']} | {e['step']} | {e['model']} | {e['total_tokens']:,} | "
            f"${e['cost_usd']:.4f} / {e['cost_rub']:.2f} ₽ | {e['status']} |"
        )
    print(NL.join(lines))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Log workflow execution telemetry (step, model, tokens, USD/RUB cost, artifacts) to run_ledger.json."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_log = sub.add_parser("log", help="Append a run record to projects/<project>/state/run_ledger.json")
    p_log.add_argument("--project", required=True, help="Project slug under projects/")
    p_log.add_argument("--projects-root", default="projects", help="Root directory for projects (default: projects)")
    p_log.add_argument("--step", required=True, help="Workflow step name (e.g., step_1_intake, step_2_3_synthesis)")
    p_log.add_argument("--model", required=True, help="Model or engine used (e.g., gemini-2.5-pro, python-cli)")
    p_log.add_argument("--input-tokens", type=int, default=0, help="Estimated input tokens")
    p_log.add_argument("--output-tokens", type=int, default=0, help="Estimated output tokens")
    p_log.add_argument("--cost-usd", type=float, default=None, help="Explicit cost in USD (auto-estimated if omitted)")
    p_log.add_argument("--usd-rub", type=float, default=95.0, help="USD/RUB exchange rate (default: 95.0)")
    p_log.add_argument(
        "--status",
        choices=["completed", "in_progress", "paused_hitl", "failed"],
        default="completed",
        help="Run status",
    )
    p_log.add_argument("--artifact", action="append", default=[], help="Artifact path(s); repeatable or comma-separated")
    p_log.add_argument("--notes", default="", help="Optional summary notes")

    p_status = sub.add_parser("status", help="Show aggregated run ledger status for a project")
    p_status.add_argument("--project", required=True, help="Project slug under projects/")
    p_status.add_argument("--projects-root", default="projects", help="Root directory for projects (default: projects)")
    p_status.add_argument("--format", choices=["table", "json"], default="table", help="Output format")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "log":
            return cmd_log(args)
        if args.command == "status":
            return cmd_status(args)
        raise ValueError(f"Unknown command: {args.command}")
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
