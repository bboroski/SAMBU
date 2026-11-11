<p align="center"><img src="assets/duck-ui/duck-mark.svg" alt="SAMBU mark" width="92"></p>
<h1 align="center">SAMBU</h1>
<p align="center"><img src="assets/nun-mesh.svg" alt="NUN Mesh ecosystem overview" width="100%"></p>
<p align="center"><strong>Scientific Modeling & Automation Environment</strong></p>
<p align="center"><strong>Экспериментальная alpha-версия</strong></p>
<p align="center"><a href="README.md">🇺🇦 Українська</a> · <a href="README.en.md">🇬🇧 English</a> · <a href="README.ru.md">🇷🇺 Русский</a></p>

> **SAMBU** — SAMBU — экспериментальная среда на Python для программирования, научного моделирования и воспроизводимых рабочих процессов.

## Текущие возможности
- Языковое ядро: lexer/parser, AST, функции, области видимости, массивы и записи.
- Научный слой: величины SI, проверка размерностей, физические константы и воспроизводимая выборка.
- Пространственные данные: sparse voxel grids, чанки, Morton keys, octrees и графовые операции.
- CLI, Tkinter IDE, тестовый runner и частичный C11 native-compiler slice.

## Быстрый старт и проверка
```bash
python -m pip install -e .
python -m pytest
python one.py check
```

## Архитектура и подтверждённые границы
Native compiler slice пока не является полным конвейером source-to-machine-code. IDE не является полноценной LSP-системой. Экспериментальные функции нельзя описывать как готовые для production.

## Инженерное качество
- Запускайте проверки для целевой платформы; host CI не заменяет аппаратную квалификацию.
- Статусы implemented, partial и planned должны подтверждаться кодом, тестами и доказательствами.
- Макет, спецификация или открытый Pull Request не доказывают production-ready реализацию.
- Внешние интеграции должны быть явными, версионированными, изолированными и тестируемыми.

## NUN Mesh и связанные репозитории
[SAMBU](https://github.com/bboroski/SAMBU) · [ToolNG](https://github.com/bboroski/ToolNG) · [ReaperCripple](https://github.com/bboroski/ReaperCripple) · [Kloz](https://github.com/bboroski/Kloz) · [CO](https://github.com/bboroski/CO) · [SaintSI](https://github.com/bboroski/SaintSI) · [Klipot](https://github.com/bboroski/Klipot) · [NUN](https://github.com/bboroski/NUN) · [NUNLauncher](https://github.com/bboroski/NUNLauncher) · [Fragile-Baby](https://github.com/bboroski/Fragile-Baby) · [Luci](https://github.com/bboroski/Luci)

Каждый репозиторий сохраняет каноническое имя, собственный код, API, цикл выпуска и границы ответственности. Интеграция означает версионированные контракты, а не автоматическое слияние независимых runtime.

## Дизайн и документация
Общее направление интерфейсов — **Duck Black / Yellow**: глубокий чёрный `#111111` для поверхностей и сигнальный жёлтый `#FFD600` для действий и состояний, читаемая типографика, доступный контраст, клавиатурная навигация и поддержка reduced motion. Подробности — в [design/DUCK_UI_SYSTEM.md](design/DUCK_UI_SYSTEM.md), если файл присутствует.

## Лицензия
MIT

---
**Создано с любовью к инженерии, системности и людям.**
