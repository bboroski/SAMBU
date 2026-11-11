<!-- Title: SAMBU — експериментальна мова програмування, наукове моделювання та IDE -->
<p align="center"><img src="assets/duck-ui/duck-mark.svg" alt="Логотип SAMBU" width="76"></p>

# SAMBU — мова програмування, наукове моделювання та IDE

[![CI](https://github.com/bboroski/SAMBU/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/bboroski/SAMBU/actions/workflows/tests.yml) [![MIT License](https://img.shields.io/badge/license-MIT-FFD600?style=flat&labelColor=111111)](LICENSE)

**SAMBU** — експериментальне Python-hosted середовище для власної мови програмування, наукових обчислень, роботи з просторовими даними та відтворюваних інженерних workflow.

<sub>Оновлено: 2026-11-11 · Версія пакета: 0.11.0 · Стадія: alpha</sub>

> **TL;DR:** встановіть пакет командою нижче, запустіть перевірки, а потім відкрийте документацію мови або IDE. SAMBU перебуває в alpha: експериментальні модулі не слід вважати production-ready.

[Українська](README.md) · [English](README.en.md) · [Русский](README.ru.md)

## Зміст

- [Призначення](#призначення)
- [Можливості](#можливості)
- [Вимоги та швидкий старт](#вимоги-та-швидкий-старт)
- [Перевірка та розробка](#перевірка-та-розробка)
- [Структура й архітектура](#структура-й-архітектура)
- [Межі та безпека](#межі-та-безпека)
- [Зображення](#зображення)
- [Документація та пов'язані проєкти](#документація-та-повязані-проєкти)
- [FAQ](#faq)
- [Підтримка та внески](#підтримка-та-внески)
- [Ліцензія](#ліцензія)

## Призначення

SAMBU поєднує інтерпретатор власної мови, інструменти розробника та предметні моделі. Це не операційна система, універсальний sandbox або завершений native-компілятор.

## Можливості

- **Мова:** lexer/parser, AST, функції, області видимості, масиви та записи.
- **Наукові обчислення:** SI-величини, перевірка розмірностей, фізичні константи й відтворюване семплювання.
- **Просторові структури:** sparse voxel grids, чанки, Morton keys, octrees і графові операції.
- **Інструменти:** CLI, Tkinter IDE, тестовий runner та архітектурні перевірки.
- **Native-напрям:** частковий C11 compiler slice з типізованим IR; повного source-to-machine-code конвеєра ще немає.

## Вимоги та швидкий старт

Потрібен **Python 3.10 або новіший**. Базовий пакет не оголошує обов'язкових runtime-залежностей; для складання editable-пакета pip встановить build-залежності з pyproject.

~~~bash
python -m pip install -e .
~~~

Для перевірки встановіть pytest, якщо його ще немає, і виконайте:

~~~bash
python -m pytest
python one.py check
~~~

Необов'язкові web-інтеграції визначені extra-групами Flask, Django, FastAPI та web. Повний web-набір встановлюється командою:

~~~bash
python -m pip install -e ".[web]"
~~~

## Перевірка та розробка

| Завдання | Команда |
|---|---|
| Тестовий набір | python -m pytest |
| Перевірка репозиторію й архітектурних правил | python one.py check |
| Editable-встановлення | python -m pip install -e . |
| Запуск IDE після встановлення | sambu-ide |

CI: [workflow тестів](.github/workflows/tests.yml), [native-перевірки](.github/workflows/native.yml) та [quality gate](.github/workflows/duck-quality-gate.yml). Статус CI не замінює перевірку конкретної ОС або апаратної платформи.

## Структура й архітектура

| Каталог / файл | Призначення |
|---|---|
| sambu/ | ядро мови та runtime |
| sambu_ide/ | IDE |
| sambu_studio/ | Duck Studio |
| tests/ | автоматизовані тести |
| docs/ | специфікації, архітектура та інструкції |
| pyproject.toml | версія пакета, Python requirement та optional extras |
| sambu.module.json | machine-readable manifest модуля |

Почніть із [огляду мови](docs/LANGUAGE.md), [IDE](docs/IDE.md), [архітектури систем](docs/SYSTEMS_LANGUAGE_ARCHITECTURE.md) та [native-компілятора](docs/NATIVE_COMPILER_ARCHITECTURE.md).

## Межі та безпека

- Python-hosted workflow не виконує довільну native firmware.
- Доступ до процесів, пристроїв, мережі та обладнання потребує окремих явних адаптерів і дозволів.
- Native compiler slice є частковим; це не повноцінний компілятор.
- Наявність manifest або workflow-декларації не доводить, що зовнішня дія справді відбулася.
- Не додавайте до репозиторію токени, паролі, приватні ключі або персональні дані.

## Зображення

<p align="center"><img src="docs/images/duck-studio-overview.webp" alt="Duck Studio: головне робоче вікно" width="960"></p>
<p align="center"><img src="docs/images/duck-studio-reports-findings.webp" alt="Duck Studio: звіти та результати перевірок" width="960"></p>
<p align="center"><img src="docs/images/duck-studio-xml-inspector.webp" alt="Duck Studio: XML-інспектор" width="960"></p>

У README використані статичні локальні WebP-ілюстрації; анімації та важкі зовнішні ресурси не завантажуються.

## Документація та пов'язані проєкти

- [Duck Studio](docs/DUCK_STUDIO.md) · [IDE та редактор](docs/IDE.md)
- [Архітектура екосистеми](docs/ECOSYSTEM_ARCHITECTURE.md) · [інженерна доктрина](docs/SAMBU_ENGINEERING_DOCTRINE.md)
- [Зміни](CHANGELOG.md) · [manifest модуля](sambu.module.json)
- [Klipot](https://github.com/bboroski/Klipot) відображає каталог і контракти екосистеми; [ToolNG](https://github.com/bboroski/ToolNG) реалізує окремий Windows-інструмент діагностики.
- [NUN](https://github.com/bboroski/NUN) та [NUNLauncher](https://github.com/bboroski/NUNLauncher) мають окремі системні й boot-контракти.

## FAQ

**Чи готовий SAMBU для production?** Ні. Поточний статус пакета — alpha.

**Чи є повноцінний native-компілятор?** Ні. Доступний лише частковий C11 compiler slice.

**Чи обов'язкові Flask, Django або FastAPI?** Ні. Це optional extras, а не базові залежності.

## Підтримка та внески

Помилки й пропозиції: [Issue tracker](https://github.com/bboroski/SAMBU/issues) · [створити bug report](https://github.com/bboroski/SAMBU/issues/new). Pull Request має містити опис зміни, пов'язані issue (за наявності), тести та оновлення документації.

Профіль супроводу: [bboroski](https://github.com/bboroski). Для вразливостей не публікуйте експлуатаційні деталі або секрети у відкритому issue; скористайтеся приватним каналом GitHub, якщо він доступний для репозиторію.

## Ліцензія

SAMBU поширюється за **MIT License**. Повний текст — у [LICENSE](LICENSE).
