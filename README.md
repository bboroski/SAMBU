<p align="center"><img src="assets/duck-ui/duck-mark.svg" alt="SAMBU mark" width="92"></p>
<h1 align="center">SAMBU</h1>
<p align="center"><strong>Scientific Modeling & Automation Environment</strong></p>
<p align="center"><img src="https://img.shields.io/badge/STATUS-EXPERIMENTAL%20ALPHA-FFD600?style=for-the-badge&labelColor=111111" alt="Experimental alpha"></p>
<p align="center"><a href="README.md">🇺🇦 Українська</a> · <a href="README.en.md">🇬🇧 English</a> · <a href="README.ru.md">🇷🇺 Русский</a></p>
<sub>Оновлено: 2026-11-12</sub>


## Навигация

- [Поточні можливості](#поточні-можливості)
- [Швидкий старт і перевірка](#швидкий-старт-і-перевірка)
- [Архітектура, межі та достовірність](#архітектура-межі-та-достовірність)
- [Скриншоти Duck Studio](#скриншоти-duck-studio)
- [Інженерна якість](#інженерна-якість)
- [Карта документації](#карта-документації)
- [NUN Mesh та пов'язані репозиторії](#nun-mesh-та-повязані-репозиторії)
- [Дизайн і документація](#дизайн-і-документація)
- [Ліцензія](#ліцензія)

> **SAMBU** — SAMBU — експериментальне Python-hosted середовище для програмування, наукового моделювання та відтворюваних workflow.

## Поточні можливості
- Мовне ядро з lexer/parser, AST, функціями, областями видимості, масивами, записами та emoji-синтаксисом команд і операторів.
- Наукові моделі: SI-величини, перевірка розмірностей, фізичні константи й відтворюване семплювання.
- Просторові дані: sparse voxel grids, чанки, Morton keys, octrees та графові операції.
- Статичний семантичний аналіз імен/областей, арності відомих функцій і явних помилок примітивних операторів (`sambu check`).
- CLI, Tkinter IDE, тестовий runner і архітектурні перевірки.
- Окремий C11 native-compiler slice з типізованими IR; це ще не повний native-компілятор.

## Швидкий старт і перевірка
```bash
python -m pip install -e .
python -m pytest
python one.py check
```

## Вимірювання якості workflow

`ExperienceJournal` додає opt-in, local-only метрики завершення, помилок, тривалості та повторюваного тертя. Буфер обмежений і очищається після відкликання згоди. Деталі: [docs/EXPERIENCE_ENGINEERING.md](docs/EXPERIENCE_ENGINEERING.md).

## Архітектура, межі та достовірність
Native compiler slice не має повного source-to-machine-code конвеєра; IDE не є повноцінною LSP-системою. Експериментальні можливості не слід трактувати як production-ready.

## Скриншоти Duck Studio

Нижче — знімки інтерфейсу застосунку з репозиторію. Вони ілюструють робочий простір, звіти та XML-інспектор.

<p align="center"><img src="docs/images/duck-studio-overview.webp" alt="Duck Studio: головний робочий простір" width="960"></p>
<p align="center"><em>Duck Studio — головний робочий простір</em></p>

<p align="center"><img src="docs/images/duck-studio-reports-findings.webp" alt="Duck Studio: звіти та результати перевірок" width="960"></p>
<p align="center"><em>Звіти та результати перевірок</em></p>

<p align="center"><img src="docs/images/duck-studio-xml-inspector.webp" alt="Duck Studio: XML-інспектор" width="960"></p>
<p align="center"><em>XML-інспектор</em></p>

## Інженерна якість
- Перевіряйте збірку й тести саме для цільової платформи; host CI не замінює hardware qualification.
- Статуси **implemented**, **partial**, **planned** мають підтверджуватися кодом, тестами та документацією.
- Не оголошуйте функцію production-ready лише на підставі макета, специфікації чи відкритого Pull Request.
- Зовнішні інтеграції мають бути явними, версіонованими, ізольованими й перевірюваними.

## Карта документації

- [Duck Studio](docs/DUCK_STUDIO.md)
- [IDE та редактор](docs/IDE.md)
- [Статичний семантичний аналіз](docs/SEMANTIC_ANALYSIS.md)
- [Emoji-програмування](docs/EMOJI_PROGRAMMING.md)
- [Архітектура native-компілятора](docs/NATIVE_COMPILER_ARCHITECTURE.md)
- [Архітектура екосистеми](docs/ECOSYSTEM_ARCHITECTURE.md)

## Ліцензія
MIT

---

## Статус інтеграцій

- Репозиторій зберігає власні API, збірку, тести та цикл випуску; міжпроєктна взаємодія відбувається через явні версіоновані контракти.
- STaas (SaaS integration control plane) і MoonTreach (CI/test acceleration) розвиваються окремими Pull Requests. Їх не слід вважати можливостями `main` або production-ready до злиття та проходження обов'язкових перевірок.
- Правила федерації та інтеграції: [Hellduck Integration Playbook](https://github.com/bboroski/Hellduck/blob/main/docs/INTEGRATION_PLAYBOOK.md).

## Інженерний стандарт
Індекс аудиту, тестових воріт, безпеки, супроводу та критеріїв інтеграції: [Engineering Improvement Index](docs/ENGINEERING_IMPROVEMENT_INDEX.md).

## Інтеграційні межі
Зберігайте незалежні API, runtime та цикли випуску; інтегруйте через версіоновані контракти. Практичні правила взаємодії: [Hellduck Integration Playbook](https://github.com/bboroski/Hellduck/blob/main/docs/INTEGRATION_PLAYBOOK.md).

---
**「在天愿作比翼鸟，在地愿为连理枝。」**

*«У небі — птахами-нерозлучниками, на землі — гілками одного дерева».*
