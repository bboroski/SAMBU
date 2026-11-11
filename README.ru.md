<p align="center"><img src="assets/duck-ui/duck-mark.svg" alt="SAMBU mark" width="92"></p>
<h1 align="center">SAMBU</h1>
<p align="center"><strong>Scientific Modeling &amp; Automation Environment</strong></p>
<p align="center">
<img src="https://img.shields.io/badge/STATUS-EXPERIMENTAL%20ALPHA-FFD600?style=for-the-badge&labelColor=111111" alt="Experimental alpha">
<img src="https://img.shields.io/badge/CORE-PYTHON%20%2B%20C11-FFD600?style=for-the-badge&labelColor=111111" alt="Python and C11">
<img src="https://img.shields.io/badge/LICENSE-MIT-FFD600?style=for-the-badge&labelColor=111111" alt="MIT">
</p>
<p align="center"><a href="README.md">🇺🇦 Українська</a> · <a href="README.en.md">🇬🇧 English</a> · <a href="README.ru.md">🇷🇺 Русский</a></p>

---

**SAMBU объединяет программирование, научное моделирование и воспроизводимые рабочие процессы в одной экспериментальной инженерной среде.** Проект предназначен для тех, кому нужны проверяемые модели, контролируемые вычисления и прозрачные результаты.

## Ценность и возможности

- **Языковое ядро:** lexer/parser, AST с source spans, функции, области видимости, массивы, записи, классы и ограниченные циклы.
- **Научный слой:** величины SI, проверка размерностей, физические константы, статистическая механика и воспроизводимая выборка.
- **Пространственные данные:** sparse voxel grids, чанки, Morton keys, octrees, геометрия поверхностей и графовые операции.
- **Инструменты:** CLI, Tkinter IDE, тестовый runner, архитектурные проверки и модели workflow.
- **Текстовые метаданные:** детерминированный структурный анализ, повторы, приблизительная просодия и семантические маркеры.
- **Native compiler slice:** отдельное направление C11 с типизированными HIR/MIR/LIR и проверками IR; это пока не полноценный native-компилятор.

## Быстрый старт

Требуются Python 3.10+ и Git. Интерпретатор не требует обязательных сторонних runtime-зависимостей.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Запуск примера и проверок:

~~~bash
sambu examples/ideal_gas.sambu
sambu -c 'print("Hello from SAMBU")'
python -m pytest
python one.py check
~~~

В Windows доступен <code>one.cmd</code>. Команда <code>python one.py</code> запускает стандартный сценарий проекта.

## Архитектура и ограничения

SAMBU — экспериментальная alpha-среда на Python. IDE поддерживает редактирование файлов, запуск, вывод и базовую диагностику, но пока не является полноценной LSP-средой. В native compiler slice ещё нет полного source-parser bridge, поддержки CFG/phi-node, конвейера оптимизации, object writer и генерации машинного кода. Полная статическая система типов и эффектов остаётся направлением развития.

## Управление качеством

| Контроль | Критерий готовности |
|---|---|
| Воспроизводимость | Одинаковые входные данные и настройки дают проверяемый результат |
| Качество | pytest, CLI smoke tests и архитектурные проверки |
| Область реализации | Экспериментальные функции обозначены точно |
| Совместимость | Изменения API сопровождаются примечаниями о миграции |
| Интеграции | Наличие адаптера не означает завершённую production-интеграцию |

Документация: [грамматика](docs/ARTICULATORY_SYNTAX.md) · [архитектура экосистемы](docs/ECOSYSTEM_ARCHITECTURE.md) · [мультиязычный конвейер](docs/MULTILINGUAL_SIGNAL_PIPELINE.md) · [wiki](wiki/README.md).

## Экосистема

SAMBU — языковой и модельный слой. Связанные проекты: [ToolNG](https://github.com/bboroski/ToolNG), [ReaperCripple](https://github.com/bboroski/ReaperCripple), [Kloz](https://github.com/bboroski/Kloz), [CO](https://github.com/bboroski/CO), [SaintSI](https://github.com/bboroski/SaintSI), [Klipot](https://github.com/bboroski/Klipot), [NUN](https://github.com/bboroski/NUN), [NUNLauncher](https://github.com/bboroski/NUNLauncher), [Fragile-Baby](https://github.com/bboroski/Fragile-Baby) и [Luci](https://github.com/bboroski/Luci).

## Лицензия и участие

MIT — см. [LICENSE](LICENSE). Перед отправкой изменений изучите архитектуру и тесты. Изменения должны быть локальными, воспроизводимыми и документированными.

---

**Создано с любовью к знаниям, инженерии и людям.**

## NUN Mesh

<p align="center"><img src="assets/nun-mesh.svg" alt="NUN Mesh — семь инженерных репозиториев, связанных версионированными контрактами" width="100%"></p>

SAMBU — авторский и исследовательский слой NUN Mesh: язык, IDE, Duck Studio, научные модели и воспроизводимые workflow. Описания интеграций и политики не предоставляют скрытого доступа к оборудованию и не запускают внешние действия без подтверждения.

Общий интерфейсный контракт: [Adaptive Workspace Integration](docs/ADAPTIVE_WORKSPACE_INTEGRATION.md).

## Продуктовая система

Единые правила дизайна Duck, трёхъязычной документации, управления возможностями, маркетинговых заявлений и выпусков: [docs/PRODUCT_SYSTEM.md](docs/PRODUCT_SYSTEM.md). Реестр на 10 000 ID — это ёмкость планирования, а не заявление о 10 000 готовых функциях.


## GUI и правила внесения изменений

Общая визуальная основа: глубокий чёрный `#111111` и жёлтый Duck `#FFD600`. Границы GUI, различие реального интерфейса и концепт-макета, доступность и требования к доказательствам описаны в [GUI Design Standard](docs/gui/GUI_DESIGN_STANDARD.md). Для изменений используйте [шаблон Pull Request](.github/PULL_REQUEST_TEMPLATE.md); перед слиянием требуются два независимых одобрения и успешные обязательные CI-проверки при включённой защите ветки.
