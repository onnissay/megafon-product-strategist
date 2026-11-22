# Skill: Steps 2 & 3 — Evidence Gathering, Research Plan & Synthesis

## Objective
Gather and structure all verifiable evidence, run deterministic baseline calculations, execute bounded exploratory checks where primary data is missing, and isolate root causes and Knowledge Gaps before generating strategic options.

## Procedure

### Step 2: Evidence Gathering & Research Plan
1. **Build Research Plan (`projects/<name>/research/research_plan.md`, Russian)**:
   - List key decision-blocking hypotheses (`H1`, `H2`, ...).
   - Map each hypothesis to: current status, cheapest falsifying data source (internal BI/SQL, UX audit, customer interviews, A/B test, secondary market data), owner, and priority (P0/P1/P2).
2. **Ingest Additional Data**:
   - Run `tools/doc_ingestor.py` on any supplementary CSV/XLSX/PDF/MD files.
3. **Baseline Quantitative Diagnostics**:
   - Run `tools/unit_econ_calc.py` to check baseline retention economics, break-even thresholds, and realistic A/B sample size / enrollment pace from brief numbers.
   - Save outputs or cite exact `[CALC]` parameters and results.
4. **Exploratory Subagents (Only When Primary Evidence Is Missing)**:
   - Run `subagents/synthetic_respondent.md` for targeted personas to surface behavioral barriers, language, and interview hypotheses.
   - **HARD RULE**: Prefix and tag every synthetic section and takeaway with `[СИНТЕТИКА — НЕ ДОКАЗЫВАЕТ СПРОС]`. Save transcripts in `projects/<name>/research/synthetic_interviews.md`.
   - Optionally run `subagents/ux_auditor.md` if funnel/screens/flows are provided.

### Step 3: Synthesis & Knowledge Gaps
1. **Create Synthesis Memo (`projects/<name>/outputs/evidence_synthesis.md`, Russian)**:
   - **Сводка верифицированных фактов и метрик**: Consolidated table (`Метрика | Значение | Источник | Статус`).
   - **Разделение сигналов и гипотез о корневых причинах**: Explicitly map observed `[ФАКТ]` signals -> candidate `[ГИПОТЕЗА]` causes -> falsification criteria.
   - **Инсайты синтетических интервью (если проводились)**: Strictly separated block marked `[СИНТЕТИКА — НЕ ДОКАЗЫВАЕТ СПРОС]` used ONLY to sharpen research questions and hypotheses.
   - **Базовые расчёты чувствительности (`[CALC]`)**: What must be true economically for an intervention to pay back.
   - **Реестр пробелов в знаниях (Knowledge Gaps)**: Prioritized table (`ID | Пробел | Влияние на выбор стратегии | Как закрыть | Критичность P0/P1/P2`).
2. **Update State & Ledger**:
   - Update `workflow_state.json`, append to `session_log.md`, and log via `tools/ledger.py`.

## Exit Criteria
- Clear boundary between `[ФАКТ]`, `[ГИПОТЕЗА]`, `[ДОПУЩЕНИЕ]`, and `[СИНТЕТИКА — НЕ ДОКАЗЫВАЕТ СПРОС]`.
- At least one deterministic baseline check run via `tools/unit_econ_calc.py` if quantitative baseline data exists.
- Prioritized Knowledge Gaps ready to inform Step 4 options (or HITL check-in if Step 1 pause was combined here).
