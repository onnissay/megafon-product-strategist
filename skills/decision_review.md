# Skill: Step 6 — Post-Decision Support & Strategy Revision

## Objective
Maintain strategic integrity after launch or decision approval by systematically evaluating incoming facts, experiment readouts, and constraint changes against registered assumptions and kill-switches.

## Procedure
1. **Ingest New Evidence**:
   - If new files/readouts arrive, ingest via `tools/doc_ingestor.py` to assign `[SRC-XX]` and check for prompt injection.
2. **Run Automated Impact Check**:
   - Execute `python3 tools/decision_tracker.py --project <name> check-impact --fact "<new verified fact>"`.
   - Review all matched decisions, linked assumptions, and kill-switch conditions.
3. **Evaluate Severity**:
   - **Green (Aligned)**: Fact stays within modeled `[ДОПУЩЕНИЕ]` bounds -> log observation, continue execution.
   - **Amber (Assumption Shifted)**: Parameter moved outside Base case but above kill-switch -> re-run `tools/unit_econ_calc.py` to check whether payback/MDE still holds; propose tactical adjustment.
   - **Red (Kill-Switch / Thesis Broken)**: Core causal hypothesis falsified, SRM detected, or guardrail breached -> recommend immediate rollback, pivot, or sunset.
4. **Issue Revision Memo (`projects/<name>/outputs/decision_revision_<YYYY-MM-DD>.md`, Russian)**:
   - Never silently overwrite historical strategy documents.
   - Document: New `[ФАКТ]` + `[SRC-XX]`, affected Decision IDs (`DEC-XX`), updated `[CALC]` economics, and explicit recommendation (Continue / Adjust / Pause / Kill).
5. **Update Decision Registry, State & Ledger**:
   - Update decision status (`active`, `under_review`, `revised`, `killed`) via `tools/decision_tracker.py`.
   - Update `workflow_state.json`, append `session_log.md`, and log via `tools/ledger.py`.

## Exit Criteria
- Impact analysis executed via `tools/decision_tracker.py check-impact`.
- Transparent audit trail connecting new `[ФАКТ]` to strategic revision or continuation.
