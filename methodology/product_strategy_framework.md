# Product Strategy Framework

High-signal playbook for turning ambiguous product problems into falsifiable, economically sound product strategies.

## 1. Jobs-to-be-Done (JTBD) & Switching Forces
Frame demand around the customer's struggling moment rather than internal product features:
- **Context / Trigger**: What concrete event triggers the job? (e.g., billing shock, child's first phone, router/dacha SIM running out of traffic, MNP offer from competitor).
- **Functional Job**: What measurable outcome is the user trying to achieve?
- **Emotional / Social Job**: What anxiety, control need, or family obligation drives the choice?
- **Four Forces**: Push of current pain + Pull of new solution MUST exceed Anxiety of switching + Habit of status quo.
- **Real Alternatives**: Never compare only against direct telco rivals. Include DIY workarounds (separate cheap SIMs, manual top-ups, Wi-Fi tethering, messenger reminders, doing nothing).

## 2. Signal vs. Root Cause Discipline
Never mistake a top-line KPI movement for a diagnosis:
- **Signal**: Observable metric shift or funnel drop (e.g., high M1 churn, low invite acceptance, ARPU dilution). Always `[ФАКТ]` + `[SRC-ID]`.
- **Decompose Before Hypothesizing**: Split by cohort, tenure, channel, device/SIM type (human family member vs. router/tablet/IoT SIM), billing event, and UX step.
- **Root Cause**: Structural mechanism producing the signal (e.g., billing transparency gap, broken invite UX, wrong target segment, cannibalization of full-price plans). Label `[ГИПОТЕЗА]` until verified.

## 3. Strategic Alternatives & Explicit Trade-Offs
A strategy without explicit sacrifices is a wish list.
- Always compare **>= 3 distinct options**, including:
  1. **Keep as-is** (zero engineering cost counterfactual).
  2. **Close / Freeze** (reallocate OPEX/headcount to higher-ROI bets).
  3. **Active strategic bets** differing in mechanism (e.g., UX/onboarding fix vs. pricing/packaging redesign vs. segment pivot).
- For every option, state **What we give up**: cannibalization risk, engineering capacity, margin compression, segment exclusion, support load, or slower growth.

## 4. Unit Economics & Value Creation
All economic claims MUST be calculated via `tools/unit_econ_calc.py` (`[CALC]`):
- **Incremental Contribution Margin**: Separate *incremental* revenue/retention from *transferred* revenue (cannibalization of existing standalone ARPU or ARPC).
- **Retention Value**: Value of a saved subscriber/household = incremental retained months * monthly contribution margin - cost to serve - incentive/promo cost.
- **Break-Even & Payback**: Compute fixed dev/marketing cost recovery in months and required incremental conversions/saved churners to break even.
- **Sensitivity**: Always evaluate Pessimistic / Base / Optimistic scenarios on the top 2 uncertain `[ДОПУЩЕНИЕ]` variables.

## 5. Five-Part Product Strategy Template
Deliver Step 5 product strategy using this exact 5-part structure (written in Russian inside `projects/<name>/outputs/`):
1. **Diagnosis (Диагноз)**: Verified baseline metrics (`[ФАКТ]`), signal-to-cause decomposition, and prioritized constraints.
2. **Target Segment & JTBD (Целевой сегмент и JTBD)**: Who we win, who we explicitly exclude, triggering moments, and competing alternatives.
3. **Core Strategic Bet & Trade-Offs (Ключевая ставка и компромиссы)**: Chosen product/pricing/UX mechanism, why rejected alternatives lose, and explicit sacrifices.
4. **Unit Economics & Value Bridge (Юнит-экономика и мост ценности)**: Deterministic `[CALC]` model (incremental margin, cannibalization cap, payback, break-even sensitivity).
5. **Roadmap, Risks & Kill Criteria (План внедрения, риски и критерии остановки)**: MVP scope, dependencies (billing/IT/legal), pre-mortem failure modes, and hard stop-loss thresholds.
