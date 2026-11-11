<p align="center"><img src="assets/duck-ui/duck-mark.svg" alt="SAMBU mark" width="92"></p>
<h1 align="center">SAMBU</h1>
<p align="center"><strong>Scientific Modeling & Automation Environment</strong></p>
<p align="center"><img src="https://img.shields.io/badge/STATUS-EXPERIMENTAL%20ALPHA-FFD600?style=for-the-badge&labelColor=111111" alt="Experimental alpha"></p>
<p align="center"><a href="README.md">🇺🇦 Українська</a> · <a href="README.en.md">🇬🇧 English</a> · <a href="README.ru.md">🇷🇺 Русский</a></p>

> **SAMBU** — SAMBU — експериментальне Python-hosted середовище для програмування, наукового моделювання та відтворюваних workflow.

## Поточні можливості
- Мовне ядро з lexer/parser, AST, функціями, областями видимості, масивами та записами.
- Наукові моделі: SI-величини, перевірка розмірностей, фізичні константи й відтворюване семплювання.
- Просторові дані: sparse voxel grids, чанки, Morton keys, octrees та графові операції.
- CLI, Tkinter IDE, тестовий runner і архітектурні перевірки.
- Окремий C11 native-compiler slice з типізованими IR; це ще не повний native-компілятор.

## Швидкий старт і перевірка
```bash
python -m pip install -e .
python -m pytest
python one.py check
```

## Архітектура, межі та достовірність
Native compiler slice не має повного source-to-machine-code конвеєра; IDE не є повноцінною LSP-системою. Експериментальні можливості не слід трактувати як production-ready.

## Інженерна якість
- Перевіряйте збірку й тести саме для цільової платформи; host CI не замінює hardware qualification.
- Статуси **implemented**, **partial**, **planned** мають підтверджуватися кодом, тестами та документацією.
- Не оголошуйте функцію production-ready лише на підставі макета, специфікації чи відкритого Pull Request.
- Зовнішні інтеграції мають бути явними, версіонованими, ізольованими й перевірюваними.

## NUN Mesh та пов'язані репозиторії
[SAMBU](https://github.com/bboroski/SAMBU) · [ToolNG](https://github.com/bboroski/ToolNG) · [ReaperCripple](https://github.com/bboroski/ReaperCripple) · [Kloz](https://github.com/bboroski/Kloz) · [CO](https://github.com/bboroski/CO) · [SaintSI](https://github.com/bboroski/SaintSI) · [Klipot](https://github.com/bboroski/Klipot) · [NUN](https://github.com/bboroski/NUN) · [NUNLauncher](https://github.com/bboroski/NUNLauncher) · [Fragile-Baby](https://github.com/bboroski/Fragile-Baby) · [Luci](https://github.com/bboroski/Luci)

Репозиторії зберігають власні назви, код, API, цикли випуску та межі відповідальності. Інтеграція означає узгоджені контракти, а не автоматичне злиття незалежних runtime.

## Дизайн і документація
Базовий інтерфейсний напрям екосистеми — **Duck Black / Yellow**: чорні поверхні, жовтий акцент для дій і станів, читабельна типографіка, доступний контраст, клавіатурна навігація та підтримка reduced motion. Деталі дивіться в [design/DUCK_UI_SYSTEM.md](design/DUCK_UI_SYSTEM.md), якщо файл присутній у цьому репозиторії.

## Ліцензія
MIT

---
**Створено з любов'ю до інженерії, системності та людей.**
