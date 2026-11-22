# Агент «Стратег Фабрики продуктов» (Product Factory Strategist)

Автономная операционная система для разработки, экономической верификации и пост-релизного пересмотра продуктовых и коммуникационных стратегий. Реализована в виде переносимого набора инструкций, методологических фреймворков, специализированных субагентов и детерминированных Python CLI-инструментов (совместима с **Gemini CLI**, **Cursor**, **OpenAI Codex CLI** и **Claude Code**).

В качестве сквозного демонстрационного проекта в репозитории выполнен полный 6-шаговый цикл по кейсу **`megafon_family_connect`** («Связь для близких и собственных устройств» на базе `demo_input/Бриф по стратегу Мегафона.pdf`).

---

## 1. Пошаговая инструкция первого запуска (без скрытых настроек)

### Шаг 1–2. Клонирование, установка зависимостей и проверка инструментов (Tier 0)
Требуется **Python 3.10+**. Внешние API-ключи, базы данных или платные сторонние сервисы для работы Python-инструментов **не требуются** — все утилиты полностью локальны и офлайн-детерминированы.

Состав `requirements.txt`: `pypdf>=4.0.0`, `pandas>=2.0.0`, `numpy>=1.26.0`, `openpyxl>=3.1.0`.

Выберите вашу операционную систему:

<details open>
<summary><b>🪟 Windows (PowerShell)</b></summary>

1. Клонируйте репозиторий и перейдите в папку проекта:
```powershell
git clone [https://github.com/onnissay/megafon-product-strategist.git](https://github.com/onnissay/megafon-product-strategist.git)
cd megafon-product-strategist
```

2. Создайте и активируйте виртуальное окружение:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(Если PowerShell заблокирует запуск скрипта, сначала выполните `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` и повторите активацию.)*

3. Установите зависимости:
```powershell
pip install -r requirements.txt
```

4. Убедитесь, что все 4 детерминированных CLI-инструмента (Tier 0) запускаются без ошибок:
```powershell
python tools/doc_ingestor.py --help
python tools/unit_econ_calc.py --help
python tools/ledger.py status --project megafon_family_connect
python tools/decision_tracker.py list --project megafon_family_connect
```

</details>

<details>
<summary><b>🍎 macOS / 🐧 Linux (bash / zsh)</b></summary>

1. Клонируйте репозиторий и перейдите в папку проекта:
```bash
git clone [https://github.com/onnissay/megafon-product-strategist.git](https://github.com/onnissay/megafon-product-strategist.git)
cd megafon-product-strategist
```

2. Создайте и активируйте виртуальное окружение:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Убедитесь, что все 4 детерминированных CLI-инструмента (Tier 0) запускаются без ошибок:
```bash
python3 tools/doc_ingestor.py --help
python3 tools/unit_econ_calc.py --help
python3 tools/ledger.py status --project megafon_family_connect
python3 tools/decision_tracker.py list --project megafon_family_connect
```

</details>

### Шаг 3. Запуск агента в вашей CLI / IDE-среде

Репозиторий содержит кросс-платформенные точки входа (`GEMINI.md`, `AGENTS.md`, `.cursorrules`), поэтому агент автоматически подхватывает правила при открытии корня репозитория:

- **Gemini CLI**:
  ```bash
  cd megafon-product-strategist
  gemini
  ```
  *(Автоматически загружает `GEMINI.md`.)*
- **Cursor**:
  Откройте папку `megafon-product-strategist` в Cursor — файл `.cursorrules` автоматически подключит `AGENTS.md` и `GEMINI.md`.
- **OpenAI Codex CLI / Claude Code**:
  ```bash
  cd megafon-product-strategist
  codex      # автоматически читает AGENTS.md
  ```

### Шаг 4. Примеры первых запросов к агенту
- **Запуск нового проекта (Шаг 1 — Task Intake)**:
  > «Прочитай `GEMINI.md`, создай проект `my_product`, инжестируй бриф `demo_input/my_brief.pdf` через `tools/doc_ingestor.py` и выполни Шаг 1 до первой паузы HITL.»
- **Возобновление существующего проекта после перерыва**:
  > «Проверь состояние проекта `megafon_family_connect` в `state/` и статус в `tools/ledger.py`. Кратко отчитайся, на каком шаге мы остановились.»
- **Проверка влияния новых данных (Шаг 6)**:
  > «Поступил новый факт: задержка биллинга выросла до 4 часов. Выполни Шаг 6 через `tools/decision_tracker.py check-impact` и оцени влияние на решения `DEC-01`–`DEC-04`.»

---

## 2. Карта репозитория

```text
megafon-product-strategist/
├── GEMINI.md                        # Каноническая инструкция для Gemini CLI (6 шагов, хуки, политика языков)
├── AGENTS.md                        # Кросс-платформенная точка входа (Codex / Claude Code / универсальный агент)
├── .cursorrules                     # Точка входа для Cursor IDE
├── requirements.txt                 # Зависимости Python CLI-утилит (pypdf, pandas, numpy, openpyxl)
├── README.md                        # Инструкция запуска, архитектура и безопасность (этот файл)
├── docs/
│   ├── project_report.md            # Полное описание работы (исходник для PDF)
│   └── video_script.md              # Поминутный сценарий 10-минутного демо-видео
├── instructions/                    # [Контур 1: Политики и управление] (EN)
│   ├── epistemic_and_security.md    # Теги [ФАКТ]/[ГИПОТЕЗА]/[ДОПУЩЕНИЕ], защита от prompt-injection
│   └── routing_and_hooks.md         # Матрица маршрутизации моделей (Tier 0/1/2) и 6 обязательных хуков
├── methodology/                     # [Контур 2: Доменная методология] (EN)
│   ├── product_strategy_framework.md # JTBD, Сигнал vs Причина, опции с компромиссами, 5-частный шаблон
│   ├── comms_strategy_framework.md  # 6-элементная коммуникация и анти-двойной счёт (Holdout, Single-Owner)
│   └── experiment_design.md         # SUTVA (рандомизация по домохозяйству), ITT, 3-уровневые метрики, SRM
├── skills/                          # [Контур 3: Пошаговые SOP] (EN)
│   ├── task_intake.md               # Шаг 1 — Постановка задачи и HITL Pause #1
│   ├── evidence_synthesis.md        # Шаги 2–3 — План исследований, синтез и реестр пробелов
│   ├── options_and_red_team.md      # Шаг 4 — Опции (вкл. «Оставить как есть» и «Закрыть») + Red-Team
│   └── decision_review.md           # Шаг 6 — Поддержка решений и пересмотр при новых фактах
├── subagents/                       # Изолированные промпты субагентов (EN)
│   ├── red_team_critic.md           # Обязательный враждебный аудит по 8 векторам (Шаги 4 и 5)
│   ├── synthetic_respondent.md      # Разведочная симуляция скептичных клиентов ([СИНТЕТИКА — НЕ ДОКАЗЫВАЕТ СПРОС])
│   └── ux_auditor.md                # Аудит воронок, приглашений, приватности и биллинг-трения
├── tools/                           # Детерминированные Python CLI-инструменты — Tier 0 (EN)
│   ├── doc_ingestor.py              # Извлечение PDF/CSV/XLSX/MD/TXT, SHA-256, сканер prompt-injection
│   ├── unit_econ_calc.py            # retention-profit, breakeven, ab-size (JSON + Markdown, тег [CALC])
│   ├── ledger.py                    # Append-only журнал запусков, токенов, стоимости USD/RUB и артефактов
│   └── decision_tracker.py          # Реестр решений (decisions.json) и check-impact по новым фактам
├── demo_input/
│   └── Бриф по стратегу Мегафона.pdf # Исходный демонстрационный бриф (11 стр.)
└── projects/                        # [Контур 4: Изолированные рабочие пространства проектов] (RU)
    └── megafon_family_connect/
        ├── research/                # Извлечённые источники, sources.json, 46 JSON-расчётов, синтетика
        ├── state/                   # task_brief.md, workflow_state.json, session_log.md, decisions.json, run_ledger.json
        └── outputs/                 # evidence_synthesis.md, options_and_red_team.md, final_strategy.md, decision_revision_01.md
```

---

## 3. Ключевые архитектурные решения

1. **Четыре изолированных контура знаний**: системные политики (`instructions/`), доменная методология (`methodology/`), пошаговые SOP (`skills/` + `subagents/`) и данные конкретного проекта (`projects/<name>/`) строго разделены. Ни одна цифра из кейса МегаФона не «вшита» в промпты или код — агент готов к запуску на любом новом продукте без переписывания инструкций.
2. **Гибридный языковой режим (экономия токенов + качество русского вывода)**:
   - Внутренний системный слой (`instructions/`, `methodology/`, `skills/`, `subagents/`, `tools/`, `GEMINI.md`, `AGENTS.md`) написан на **английском языке** — это снижает расход контекстных токенов на ~25–35% и обеспечивает максимальную точность следования инструкциям у флагманских моделей.
   - Вся коммуникация с пользователем и все проектные артефакты (`projects/<name>/**`) ведутся **строго на русском языке**.
3. **Детерминированная математика в Python CLI (Tier 0 вместо «счёта в уме» LLM)**:
   - Все расчёты удержания (`retention-profit`), окупаемости (`breakeven`) и размеров A/B-выборок (`ab-size`) вынесены в `tools/unit_econ_calc.py` (NumPy / точная статистика). Каждый расчёт сохраняется в JSON (`research/calculations/*.json`) и маркируется тегом `[CALC]`.
4. **Непрерывность сессий и Human-in-the-Loop (HITL)**:
   - Машиночитаемое состояние (`state/workflow_state.json`), append-only журнал (`state/session_log.md`), журнал запусков (`state/run_ledger.json`) и реестр решений (`state/decisions.json`) позволяют безопасно закрывать чат и возобновлять работу с любого шага без потери контекста.
5. **Обязательный Red-Team аудит и контрфактуалы**:
   - На Шаге 4 агент обязан моделировать не только активные ставки, но и контрфактуалы **«Оставить как есть»** и **«Закрыть/заморозить»**, после чего прогонять стратегию через 8-векторный чеклист `subagents/red_team_critic.md`.

---

## 4. Данные и безопасность

- **Защита от Prompt-Injection (Untrusted Data Policy)**: все файлы из `demo_input/`, загружаемые PDF/CSV/XLSX и внешние тексты рассматриваются строго как **недоверенные пассивные данные**. Перед анализом каждый файл обязан пройти через `tools/doc_ingestor.py`, который:
  1. Вычисляет криптографический хэш **SHA-256** и регистрирует уникальный `SRC-ID` в `research/sources.json`.
  2. Сканирует содержимое по 12+ русско- и англоязычным сигнатурам prompt-injection (попытки переопределения роли, отключения Red-Team/HITL, запуска shell-команд, утечки `.env`) и проверяет аномалии невидимых zero-width символов.
  3. Оборачивает извлечённый текст в заголовок `EXTRACTED UNTRUSTED DATA`. Для демо-брифа `SRC-01` статус проверки — `CLEAN` (`0` флагов).
- **Эпистемическая гигиена (ноль выдуманной уверенности)**: каждое существенное утверждение маркируется источником (`[SRC-XX]`, `[CALC]`, `[USER]`, `[СИНТЕТИКА — НЕ ДОКАЗЫВАЕТ СПРОС]`) и статусом (`[ФАКТ]`, `[ГИПОТЕЗА]`, `[ДОПУЩЕНИЕ]`). Синтетические интервью запрещено использовать как доказательство рыночного спроса.
- **Гигиена секретов и PII**: `.gitignore` блокирует попадание `.env`, ключей `*.pem`/`*.key`, `*secret*`, `credentials*.json`, кэшей `__pycache__/` и временных файлов. Репозиторий не содержит API-ключей, токенов доступа или реальных персональных данных абонентов (демо-бриф использует вымышленного мобильного оператора).
