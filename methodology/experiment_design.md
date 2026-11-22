# Experiment Design Playbook

Rigorous A/B and quasi-experimental verification framework tailored to multi-SIM, household, and subscription products.

## 1. Randomization Unit & Interference Control
- **Default Unit = Household / Account Owner (Payer)**, NEVER individual MSISDN when product mechanics link multiple numbers (e.g., family group, shared balances, invite flows).
- **Why**: Randomizing by individual SIM causes SUTVA spillover (control member gets invited by treatment owner), contaminating churn and ARPU estimates.
- **Pre-Assignment Stratification**: Stratify by baseline tenure, ARPU decile, number of active SIMs/devices, and region/channel to reduce variance.
- **Exclusion Criteria**: Define upfront (e.g., B2B/corporate accounts, employee SIMs, accounts already in conflicting pricing tests).

## 2. Three-Tier Metric Hierarchy
Every experiment MUST specify exactly one Primary Decision Metric plus Reliability and Guardrail metrics:
1. **Value / Primary Metric (Метрика ценности)**: Directly tied to incremental profit or validated north-star proxy (e.g., 60-day household net retention, incremental monthly contribution margin per household, active paid group conversion at D30).
2. **Reliability / Diagnostic Metrics (Метрики надёжности и воронки)**: Step-level mechanics verifying the causal chain (invite sent -> invite accepted -> second SIM active -> first billing cycle renewed, UX error rate, time-to-activate).
3. **Guardrail Metrics (Защитные метрики)**: Hard ceilings protecting the core business:
   - Total household ARPU / contribution cannibalization floor
   - Owner & member voluntary churn
   - Support tickets / NPS / complaints per 1,000 exposed users
   - Opt-out / notification unsubscribe rate

## 3. Sample Size, Power & Enrollment Pace
Never guess sample sizes. Always compute via `tools/unit_econ_calc.py ab-size`:
- Standard defaults (unless justified otherwise): two-sided `alpha = 0.05`, `power = 0.80` (or `0.90` for high-stakes pricing changes).
- Define **MDE (Minimum Detectable Effect)** from economics (minimum lift needed to beat break-even / payback threshold), NOT wishful thinking.
- **Enrollment Pace Feasibility**:
  - `weeks_needed = total_sample_size / weekly_eligible_enrollment`
  - Add maturation window (e.g., +30 or +60 days for billing-cycle retention).
  - If total duration exceeds business window (e.g., >12 weeks), either raise MDE (acknowledge lower sensitivity), narrow scope to a faster leading indicator (with explicit validity risk `[ДОПУЩЕНИЕ]`), or switch to phased rollout / geo-holdout.

## 4. Decision Rules & Kill-Switch
Pre-register BEFORE launch:
- **Ship Criteria**: Primary metric positive & statistically significant (`p < alpha`), effect size >= economic MDE, and zero guardrail breaches.
- **Iterate Criteria**: Positive directional signal on diagnostic funnel, primary inconclusive due to friction fixable in <2 sprints.
- **Kill-Switch (Аварийная остановка)**: Automated/daily monitored thresholds that halt the test immediately:
  - Billing/technical error rate > threshold (e.g., >1.0%)
  - Guardrail ARPU/margin drop > threshold (e.g., >2% household margin dilution)
  - Support complaint spike > 2x control baseline
  - SRM (Sample Ratio Mismatch) chi-square `p < 0.001` -> invalidate test and debug allocation immediately.
