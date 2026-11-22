# Communications Strategy Framework

Playbook for aligning go-to-market messaging strictly with actual product mechanics and preventing phantom attribution.

## 1. Core Alignment Principle
**Message MUST match product reality.** Communications cannot fix a broken product mechanic, hide billing friction, or promise value the UX does not deliver within the first session. Every promise must trace to a live product capability or scheduled MVP deliverable.

## 2. Six-Element Communications Architecture
Define each element explicitly per target segment (in Russian for project deliverables):
1. **Audience (Аудитория)**: Behavioral + contract criteria (not vague demographics) — e.g., active base owner with >=2 SIMs/transfers, recent top-up for relative, high-data router SIM user; plus explicit exclusion list (recent churned, low-margin tariff if cannibalization risk).
2. **Trigger (Триггер)**: Exact lifecycle or contextual moment when receptivity peaks (e.g., recurring P2P top-up to another number, tariff renewal, family SIM purchase, traffic exhaustion alert).
3. **Barrier (Барьер)**: Primary psychological, financial, or operational friction blocking action (e.g., "they will see my calls/texts", "hidden fees later", "hard to unlink if we split", "my relative is on another operator").
4. **Core Message (Ключевое сообщение)**: Single concrete value proposition directly neutralizing the barrier and matching the actual product feature (no abstract brand slogans).
5. **Reason to Believe — RTB (Доказательство / RTB)**: Verifiable proof embedded in copy/UX (exact price in RUB, 1-click unlink guarantee, privacy boundary, transparent billing preview before confirmation).
6. **Channel Mix & Cadence (Каналы и частотность)**: Match channel cost and intrusiveness to intent (in-app contextual banner, push at trigger moment, USSD/SMS, retail/call-center script, paid media only if CAC fits `[CALC]` payback). Enforce frequency caps and fatigue guardrails.

## 3. Anti-Double-Counting & Attribution Discipline
In telecom/ecosystem stacks, multiple campaigns and organic funnels compete for the same subscriber. Prevent inflated ROI:
- **Global Holdout / Control Group**: Never attribute 100% of exposed conversions to comms; measure *incremental lift* against an unexposed control group randomized at the same unit (household/owner).
- **Single-Owner Attribution Rule**: A saved churner or activated group cannot be counted simultaneously in Product UX lift, CRM Retention lift, and Paid Media ROI. Define one primary attribution hierarchy.
- **Cannibalization Audit**: Track net ARPU / household contribution across ALL linked MSISDNs (owner + invited members), not just the newly attached line.
- **Organic Baseline Separation**: Discount baseline organic activation rate before computing comms payback via `tools/unit_econ_calc.py`.
