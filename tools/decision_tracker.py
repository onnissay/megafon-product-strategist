#!/usr/bin/env python3
"""Strategic decision registry and post-decision impact checker.

Manages projects/<project>/state/decisions.json and evaluates incoming facts
against registered assumptions and kill-switch conditions via `check-impact`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NL = chr(10)

STOPWORDS = {
    # English
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were",
    "have", "has", "not", "but", "into", "over", "under", "will", "should", "can",
    # Russian
    "что", "как", "для", "при", "или", "это", "все", "его", "она", "они", "без",
    "под", "над", "про", "так", "уже", "если", "чем", "после", "между", "через",
}

RISK_KEYWORDS = {
    "churn", "отток", "arpu", "арпу", "cannibal", "каннибал", "srm", "error", "ошибк",
    "kill", "стоп", "бюджет", "budget", "delay", "задержк", "legal", "регулят",
    "жалоб", "complaint", "марж", "margin", "конверс", "convers", "паден", "drop",
    "снижен", "роутер", "router", "семь", "famil", "приглаш", "invit", "тари",
}


def tokenize_stems(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text.lower())
    stems: set[str] = set()
    for tok in tokens:
        if len(tok) < 3 or tok in STOPWORDS:
            continue
        if tok.isdigit():
            stems.add(tok)
        else:
            stems.add(tok[:5] if len(tok) > 5 else tok)
    return stems


def load_decisions(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"decisions": []}


def save_decisions(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + NL, encoding="utf-8")


def next_dec_id(decisions: list[dict[str, Any]]) -> str:
    max_num = 0
    for d in decisions:
        m = re.match(r"^DEC-(\d+)$", str(d.get("decision_id", "")))
        if m:
            max_num = max(max_num, int(m.group(1)))
    return f"DEC-{max_num + 1:02d}"


def split_items(raw_list: list[str] | None) -> list[str]:
    items: list[str] = []
    for raw in raw_list or []:
        for part in raw.split(";"):
            cleaned = part.strip()
            if cleaned:
                items.append(cleaned)
    return items


def cmd_add(args: argparse.Namespace) -> int:
    path = Path(args.projects_root) / args.project / "state" / "decisions.json"
    db = load_decisions(path)
    dec_id = next_dec_id(db["decisions"])
    sources = [s.strip() for s in (args.sources or "").split(",") if s.strip()]

    record: dict[str, Any] = {
        "decision_id": dec_id,
        "title": args.title,
        "summary": args.summary,
        "owner": args.owner,
        "status": args.status,
        "assumptions": split_items(args.assumption),
        "kill_switches": split_items(args.kill_switch),
        "sources": sources,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "history": [],
    }
    db["decisions"].append(record)
    save_decisions(path, db)
    print(json.dumps({"status": "added", "decision": record}, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    path = Path(args.projects_root) / args.project / "state" / "decisions.json"
    db = load_decisions(path)
    items = db.get("decisions", [])
    if args.status:
        items = [d for d in items if d.get("status") == args.status]

    if args.format == "json":
        print(json.dumps({"project": args.project, "decisions": items}, ensure_ascii=False, indent=2))
        return 0

    lines = [
        f"### Decisions Registry: `{args.project}` ({len(items)} items)",
        "",
        "| ID | Title | Status | Owner | Assumptions | Kill-Switches |",
        "|---|---|---|---|---:|---:|",
    ]
    for d in items:
        lines.append(
            f"| {d['decision_id']} | {d['title']} | {d['status']} | {d['owner']} | "
            f"{len(d.get('assumptions', []))} | {len(d.get('kill_switches', []))} |"
        )
    print(NL.join(lines))
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    path = Path(args.projects_root) / args.project / "state" / "decisions.json"
    db = load_decisions(path)
    for d in db.get("decisions", []):
        if d.get("decision_id") == args.id:
            if args.status:
                d["status"] = args.status
            if args.note:
                d.setdefault("history", []).append(
                    {"timestamp": datetime.now(timezone.utc).isoformat(), "status": d["status"], "note": args.note}
                )
            save_decisions(path, db)
            print(json.dumps({"status": "updated", "decision": d}, ensure_ascii=False, indent=2))
            return 0
    raise ValueError(f"Decision {args.id} not found in {path}")


def _overlap_score(fact_stems: set[str], text: str) -> tuple[float, list[str]]:
    target_stems = tokenize_stems(text)
    if not fact_stems or not target_stems:
        return 0.0, []
    matched = sorted(fact_stems.intersection(target_stems))
    denom = min(len(fact_stems), len(target_stems))
    base_score = len(matched) / max(1, denom)
    risk_hits = [m for m in matched if any(rk in m or m in rk for rk in RISK_KEYWORDS)]
    score = min(1.0, base_score + 0.15 * len(risk_hits))
    return round(score, 3), matched


def cmd_check_impact(args: argparse.Namespace) -> int:
    path = Path(args.projects_root) / args.project / "state" / "decisions.json"
    db = load_decisions(path)
    decisions = db.get("decisions", [])
    fact_stems = tokenize_stems(args.fact)

    impacts: list[dict[str, Any]] = []
    for d in decisions:
        matched_assumptions: list[dict[str, Any]] = []
        matched_kills: list[dict[str, Any]] = []

        for a in d.get("assumptions", []):
            score, terms = _overlap_score(fact_stems, a)
            if score >= args.threshold and terms:
                matched_assumptions.append({"assumption": a, "score": score, "matched_stems": terms})

        for ks in d.get("kill_switches", []):
            score, terms = _overlap_score(fact_stems, ks)
            if score >= args.threshold and terms:
                matched_kills.append({"kill_switch": ks, "score": score, "matched_stems": terms})

        title_score, title_terms = _overlap_score(fact_stems, f"{d.get('title', '')} {d.get('summary', '')}")
        max_score = max(
            [title_score]
            + [m["score"] for m in matched_assumptions]
            + [m["score"] for m in matched_kills]
        )

        if matched_kills:
            severity = "HIGH"
            action = "KILL_SWITCH_REVIEW: Immediately audit kill-switch threshold and re-run unit_econ_calc.py."
        elif matched_assumptions or max_score >= max(args.threshold, 0.25):
            severity = "MEDIUM"
            action = "ASSUMPTION_REVIEW: Check whether modeled bounds still hold; consider revision memo."
        else:
            severity = "LOW"
            action = "NO_DIRECT_TRIGGER"

        if severity != "LOW" or args.include_all:
            impacts.append(
                {
                    "decision_id": d["decision_id"],
                    "title": d["title"],
                    "status": d["status"],
                    "severity": severity,
                    "max_score": max_score,
                    "matched_kill_switches": matched_kills,
                    "matched_assumptions": matched_assumptions,
                    "title_matched_stems": title_terms,
                    "recommended_action": action,
                }
            )

    impacts.sort(key=lambda x: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["severity"]], -x["max_score"]))
    result = {
        "project": args.project,
        "fact": args.fact,
        "evaluated_decisions": len(decisions),
        "affected_decisions": len([i for i in impacts if i["severity"] != "LOW"]),
        "impacts": impacts,
    }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    lines = [
        f"### Impact Check (`{args.project}`)",
        f"- **New fact**: {args.fact}",
        f"- **Evaluated decisions**: {result['evaluated_decisions']} | **Affected**: {result['affected_decisions']}",
        "",
    ]
    if not impacts:
        lines.append("No active assumptions or kill-switches matched above threshold.")
    else:
        for imp in impacts:
            lines.append(f"#### {imp['decision_id']} — {imp['title']} (`{imp['severity']}`, status: `{imp['status']}`)")
            lines.append(f"- **Recommended action**: {imp['recommended_action']}")
            if imp["matched_kill_switches"]:
                lines.append("- **Matched kill-switches**:")
                for mk in imp["matched_kill_switches"]:
                    lines.append(f"  - {mk['kill_switch']} (score={mk['score']}, stems={mk['matched_stems']})")
            if imp["matched_assumptions"]:
                lines.append("- **Matched assumptions**:")
                for ma in imp["matched_assumptions"]:
                    lines.append(f"  - {ma['assumption']} (score={ma['score']}, stems={ma['matched_stems']})")
            lines.append("")
    print(NL.join(lines))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage strategic decisions in decisions.json and check impact of new facts."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Register a strategic decision with assumptions and kill-switches")
    p_add.add_argument("--project", required=True, help="Project slug under projects/")
    p_add.add_argument("--projects-root", default="projects", help="Root directory for projects (default: projects)")
    p_add.add_argument("--title", required=True, help="Short decision title")
    p_add.add_argument("--summary", required=True, help="Decision summary and rationale")
    p_add.add_argument("--owner", default="Product Lead", help="Decision owner")
    p_add.add_argument("--status", choices=["proposed", "active", "under_review", "revised", "killed"], default="active")
    p_add.add_argument("--assumption", action="append", default=[], help="Key assumption (repeatable or ';'-separated)")
    p_add.add_argument("--kill-switch", action="append", default=[], help="Kill-switch condition (repeatable or ';'-separated)")
    p_add.add_argument("--sources", default="", help="Comma-separated SRC-IDs (e.g., SRC-01,CALC)")

    p_list = sub.add_parser("list", help="List decisions for a project")
    p_list.add_argument("--project", required=True, help="Project slug under projects/")
    p_list.add_argument("--projects-root", default="projects", help="Root directory for projects")
    p_list.add_argument("--status", default=None, help="Filter by status")
    p_list.add_argument("--format", choices=["table", "json"], default="table")

    p_upd = sub.add_parser("update", help="Update decision status and append audit note")
    p_upd.add_argument("--project", required=True, help="Project slug under projects/")
    p_upd.add_argument("--projects-root", default="projects", help="Root directory for projects")
    p_upd.add_argument("--id", required=True, help="Decision ID (e.g., DEC-01)")
    p_upd.add_argument("--status", choices=["proposed", "active", "under_review", "revised", "killed"], default=None)
    p_upd.add_argument("--note", default="", help="Audit note describing why status changed")

    p_imp = sub.add_parser("check-impact", help="Evaluate how a new verified fact impacts registered decisions")
    p_imp.add_argument("--project", required=True, help="Project slug under projects/")
    p_imp.add_argument("--projects-root", default="projects", help="Root directory for projects")
    p_imp.add_argument("--fact", required=True, help="New verified fact to evaluate against assumptions and kill-switches")
    p_imp.add_argument("--threshold", type=float, default=0.15, help="Stem overlap threshold (default: 0.15)")
    p_imp.add_argument("--include-all", action="store_true", help="Include unaffected decisions in output")
    p_imp.add_argument("--format", choices=["markdown", "json"], default="markdown")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            return cmd_add(args)
        if args.command == "list":
            return cmd_list(args)
        if args.command == "update":
            return cmd_update(args)
        if args.command == "check-impact":
            return cmd_check_impact(args)
        raise ValueError(f"Unknown command: {args.command}")
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
