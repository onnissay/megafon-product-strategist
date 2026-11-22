# Skill: Step 4 — Strategic Options & Red-Team Critique

## Objective
Formulate mutually exclusive strategic options, quantify each deterministically, stress-test them adversarially via `subagents/red_team_critic.md`, and present an executive decision matrix for **HITL Pause #2**.

## Procedure
1. **Generate >= 3 Distinct Strategic Options**:
   - **Option A — «Оставить как есть» (Keep as-is / Status Quo)**: Baseline trajectory without new investment; quantify expected drift, churn cost, and opportunity cost.
   - **Option B — «Закрыть / заморозить» (Close / Freeze / Sunset)**: Reallocate budget/engineering to higher-ROI initiatives; quantify migration/PR/churn risks and freed OPEX.
   - **Option C, D, ... — Active Strategic Bets** (1–3 genuinely different mechanisms: e.g., onboarding/UX friction removal vs. tariff/pricing repackaging vs. target-segment pivot). Do NOT create cosmetic variations of the same idea.
2. **Deterministic Economic & Feasibility Modeling**:
   - For EVERY option, run `tools/unit_econ_calc.py` (`retention-profit`, `breakeven`, and `ab-size` where applicable) across Pessimistic / Base / Optimistic scenarios.
   - Tag every modeled parameter `[ДОПУЩЕНИЕ]` with explicit bounds and every output `[CALC]`.
   - Explicitly model cannibalization risk and household-level net margin.
3. **Mandatory Red-Team Hook**:
   - Invoke `subagents/red_team_critic.md` on the draft options matrix.
   - Attack: unverified `[ДОПУЩЕНИЕ]` leaps, synthetic data treated as proof, double-counting, hidden billing/legal friction, cannibalization blindness, and unfeasible A/B test durations.
   - Incorporate Red-Team findings verbatim in a dedicated section of `projects/<name>/outputs/options_and_red_team.md` (in Russian), along with strategist responses/mitigations.
4. **Build Executive Comparison Matrix (`outputs/options_and_red_team.md`, Russian)**:
   - Compare options on: Mechanism, Target Segment, Incremental Profit (Pess/Base/Opt `[CALC]`), Payback, Cannibalization Risk, Implementation Complexity, Time-to-Verify, and Key Trade-Offs.
   - Provide a reasoned recommendation (clearly stating which assumption must hold for it to win).
5. **Update State, Ledger & Pause**:
   - Update `workflow_state.json` (`hitl_pause: true`, `current_step: 4`), append `session_log.md`, log via `tools/ledger.py`.
   - **[HITL PAUSE #2]**: Ask user to pick an option (or adjust constraints) before executing Step 5.

## Exit Criteria
- >= 3 distinct options including both «Оставить как есть» and «Закрыть / заморозить».
- All math verified via `tools/unit_econ_calc.py`.
- Mandatory `subagents/red_team_critic.md` critique completed and documented.
