# SAMBU — Product System / Продуктова система / Продуктовая система

> Revision: 2026-11-11 · Canonical repository identity: **SAMBU** · Product claims must match code and evidence.

## Українська

### Позиціонування
**Scientific Modeling & Automation Environment.** Python-hosted language runtime, scientific modeling, spatial data, reproducible workflows and an experimental native compiler slice.

### Поточна спроможність
Lexer/parser and AST; SI dimensional checks; reproducible sampling; spatial data structures; CLI/IDE; experimental typed IR. Native code generation and a complete compiler are not yet claimed.

### Дизайн-стандарт Duck
- Полотно: `#111111`; основний акцент: `#FFD600`; поверхні: `#1B1B1B` і `#252525`; основний текст: `#F5F5F5`; допоміжний: `#B8B8B8`.
- Чітка типографіка, контрастні стани, видимий клавіатурний фокус, адаптивні макети та зрозумілі повідомлення про помилки.
- Рух і анімація мають поважати `prefers-reduced-motion`; колір не є єдиним носієм статусу.
- Не змінювати канонічну назву репозиторію, API-префікси та історичні шляхи без міграційного плану.

### Реєстр можливостей: масштаб до 10 000
Ідентифікатори `SAMBU-CAP-00001` … `SAMBU-CAP-10000` резервують простір каталогу, а не заявляють про 10 000 реалізованих функцій. Запис переходить через стани **IDEA → SPECIFIED → IMPLEMENTED → VERIFIED → RELEASED → DEPRECATED**. Кожен перехід підтверджується артефактом.

Обов'язковий контракт функції: проблема й користувач; публічний інтерфейс; очікувана поведінка та помилки; критерії приймання; тести; безпека й приватність; сумісність; документація українською, англійською та російською; власник ролі; план відкату.

### Пріоритети та менеджмент
Оцінювати вплив для користувача, впевненість у рішенні, вартість, ризик і готовність залежностей. Спочатку виправляти коректність та безпеку, потім інтеграції, продуктивність і розширення. Не призначати вигаданих власників чи дат. Вимірювати проходження тестів, покриття заявлених платформ доказами, відкриті дефекти, час усунення та повноту документації.

### Маркетинг і реліз
Пояснювати конкретну проблему, цільову аудиторію, перевірену користь і спосіб перевірки результату. Розділяти **реалізовано**, **експериментально**, **заплановано** та **не підтримується**. Не рекламувати симуляцію як реальне обладнання, host-тест як hardware qualification або пропозицію як готовий продукт. Реліз дозволений після тестів, перевірки залежностей, changelog, тримовної документації та збереження rollback-шляху.

## English

### Positioning
**Scientific Modeling & Automation Environment.** Python-hosted language runtime, scientific modeling, spatial data, reproducible workflows and an experimental native compiler slice.

### Current capability
Lexer/parser and AST; SI dimensional checks; reproducible sampling; spatial data structures; CLI/IDE; experimental typed IR. Native code generation and a complete compiler are not yet claimed.

### Duck design standard
- Canvas `#111111`; primary accent `#FFD600`; surfaces `#1B1B1B` and `#252525`; primary text `#F5F5F5`; secondary text `#B8B8B8`.
- Use legible typography, high-contrast states, visible keyboard focus, responsive layouts and actionable error messages.
- Respect `prefers-reduced-motion`; never communicate status by color alone.
- Preserve the canonical repository name, API prefixes and historical paths unless a migration plan exists.

### Capability registry: scale to 10,000
Identifiers `SAMBU-CAP-00001` through `SAMBU-CAP-10000` reserve catalog capacity; they do not claim 10,000 implemented functions. Records move through **IDEA → SPECIFIED → IMPLEMENTED → VERIFIED → RELEASED → DEPRECATED**, with evidence required for every transition.

Each feature needs a user problem, public interface, expected and failure behavior, acceptance criteria, tests, security/privacy review, compatibility notes, Ukrainian/English/Russian documentation, an owner role and a rollback plan.

### Prioritization and management
Score user impact, confidence, effort, risk and dependency readiness. Prioritize correctness and security, then integration, performance and expansion. Never invent owners or delivery dates. Track test pass rate, evidence-backed platform coverage, open defects, time to resolution and documentation completeness.

### Marketing and release
State the concrete problem, audience, verified benefit and how the result can be checked. Distinguish **implemented**, **experimental**, **planned** and **unsupported**. Never market a simulation as physical hardware, a host test as hardware qualification, or a proposal as a finished product. Release only after tests, dependency review, changelog, three-language docs and a rollback path are ready.

## Русский

### Позиционирование
**Scientific Modeling & Automation Environment.** Python-hosted language runtime, scientific modeling, spatial data, reproducible workflows and an experimental native compiler slice.

### Текущие возможности
Lexer/parser and AST; SI dimensional checks; reproducible sampling; spatial data structures; CLI/IDE; experimental typed IR. Native code generation and a complete compiler are not yet claimed.

### Дизайн-стандарт Duck
- Фон: `#111111`; основной акцент: `#FFD600`; поверхности: `#1B1B1B` и `#252525`; основной текст: `#F5F5F5`; вторичный: `#B8B8B8`.
- Применять читаемую типографику, контрастные состояния, заметный фокус клавиатуры, адаптивные макеты и понятные ошибки.
- Учитывать `prefers-reduced-motion`; статус нельзя передавать только цветом.
- Сохранять каноническое имя репозитория, префиксы API и исторические пути без плана миграции не менять.

### Реестр возможностей: масштаб до 10 000
Идентификаторы `SAMBU-CAP-00001` … `SAMBU-CAP-10000` задают ёмкость каталога, а не означают наличие 10 000 готовых функций. Статусы: **IDEA → SPECIFIED → IMPLEMENTED → VERIFIED → RELEASED → DEPRECATED**. Каждый переход требует подтверждающего артефакта.

Для каждой функции обязательны: проблема и пользователь; публичный интерфейс; нормальное и ошибочное поведение; критерии приёмки; тесты; проверка безопасности и приватности; совместимость; документация на украинском, английском и русском; ответственная роль; план отката.

### Приоритеты и управление
Оценивать пользовательский эффект, уверенность, трудоёмкость, риск и готовность зависимостей. Сначала исправлять корректность и безопасность, затем интеграции, производительность и расширение. Не выдумывать ответственных и сроки. Отслеживать прохождение тестов, подтверждённое платформенное покрытие, дефекты, время исправления и полноту документации.

### Маркетинг и выпуск
Показывать конкретную проблему, аудиторию, подтверждённую пользу и способ проверки результата. Разделять **реализовано**, **экспериментально**, **запланировано** и **не поддерживается**. Не выдавать симуляцию за реальное оборудование, host-тест за аппаратную квалификацию, а предложение — за готовый продукт. Выпускать релиз после тестов, проверки зависимостей, changelog, трёхъязычной документации и подготовки отката.
