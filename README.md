<p align="center">
  <img src="assets/duck-ui/duck-mark.svg" alt="Duck mark" width="104" />
</p>
<h1 align="center">SAMBU</h1>
<p align="center"><strong>Scientific Modeling &amp; Automation Environment</strong></p>
<p align="center">
  <img src="https://img.shields.io/badge/STATUS-EXPERIMENTAL%20ALPHA-FFD600?style=for-the-badge&labelColor=111111" alt="Project status" />
  <img src="https://img.shields.io/badge/CORE-PYTHON%20%2B%20C11-FFD600?style=for-the-badge&labelColor=111111" alt="Core technologies" />
  <img src="https://img.shields.io/badge/LICENSE-MIT-FFD600?style=for-the-badge&labelColor=111111" alt="MIT license" />
</p>
<p align="center">
  <a href="README.md">🇺🇦 Українська</a> ·
  <a href="README.en.md">🇬🇧 English</a> ·
  <a href="README.ru.md">🇷🇺 Русский</a>
</p>
<hr />

**Одна експериментальна середа для програмування, наукових моделей, просторових даних і відтворюваних workflow.** SAMBU поєднує інтерпретоване мовне ядро, Python-інструментарій та окремий ранній native-компіляторний напрям.

## Для чого SAMBU

SAMBU створюється для інженерів і дослідників, яким потрібні читабельні моделі, контрольовані обчислення та інструменти, що можна перевіряти. Мета — звести мову, наукові домени й робочі процеси в одну узгоджену середу, не приховуючи межі реалізації.

## Можливості

- **Мовне ядро:** lexer/parser, AST із source spans, функції, області видимості, масиви, записи, класи та обмежені цикли.
- **Наукові обчислення:** SI-величини, перевірка розмірностей, фізичні константи, статистична механіка та відтворюване семплювання.
- **Просторові моделі:** sparse voxel grids, чанки, Morton keys, octrees, геометрія поверхонь і графові операції.
- **Workflow та інструменти:** CLI, Tkinter IDE, тестовий runner, архітектурні перевірки й моделі workflow.
- **Текстові метадані:** детермінований аналіз структури, повторів, приблизної просодії та семантичних маркерів. Це аналіз даних, а не генерація тексту чи оцінювання художньої якості.
- **Native compiler slice:** ізольований C11-напрям із типізованими HIR/MIR/LIR та перевірками IR; це ще не повний native-компілятор.

## Швидкий старт

Потрібні Python 3.10+ і Git. Обов'язкових сторонніх runtime-залежностей для інтерпретатора немає.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Запуск програми:

~~~bash
sambu examples/ideal_gas.sambu
sambu -c 'print("Hello from SAMBU")'
~~~

Стандартна перевірка та one-knob запуск:

~~~bash
python -m pytest
python one.py check
~~~

У Windows доступний файл <code>one.cmd</code>. Звичайний <code>python one.py</code> виконує стандартний сценарій проєкту.

## Інструменти та візуальна система

IDE зараз надає редагування файлів, запуск, вивід і базову діагностику. Це корисний робочий інтерфейс, але ще не повноцінна LSP-IDE.

<p align="center">
  <img src="assets/duck-ui/duck-studio-preview.svg" alt="SAMBU Studio preview" width="49%" />
  <img src="assets/duck-ui/ide-editor-preview.svg" alt="SAMBU IDE editor preview" width="49%" />
</p>

## Управління розробкою та критерії готовності

| Контрольна точка | Поточна політика |
|---|---|
| Зрілість | Experimental alpha; API та можливості можуть змінюватися |
| Перевірки | pytest, CLI smoke tests і архітектурні перевірки |
| Native path | Окремий експериментальний зріз; не замінює Python-інтерпретатор |
| Інтеграції | Наявність адаптера або профілю не означає завершену production-інтеграцію |
| Зміни API | Сумісні шляхи зберігаються до окремої міграції з явними примітками |

## Архітектура та обмеження

SAMBU — Python-hosted alpha-проєкт. Розширення для Flask, Django та FastAPI необов'язкові. Нативний compiler path поки не має повного source parser bridge, CFG/phi-node підтримки, оптимізаційного конвеєра, object writer або генерації машинного коду. Повна статична система типів/ефектів і LSP залишаються напрямами розвитку.

Документація:
- [Артикуляційна граматика](docs/ARTICULATORY_SYNTAX.md)
- [Архітектура екосистеми](docs/ECOSYSTEM_ARCHITECTURE.md)
- [Мультимовний конвеєр сигналів](docs/MULTILINGUAL_SIGNAL_PIPELINE.md)
- [Енциклопедія SAMBU](wiki/README.md)

## Екосистема

SAMBU є мовним і modeling-шаром сімейства: [ToolNG](https://github.com/bboroski/ToolNG) · [ReaperCripple](https://github.com/bboroski/ReaperCripple) · [Kloz](https://github.com/bboroski/Kloz) · [CO](https://github.com/bboroski/CO) · [SaintSI](https://github.com/bboroski/SaintSI) · [Klipot](https://github.com/bboroski/Klipot) · [NUN](https://github.com/bboroski/NUN) · [NUNLauncher](https://github.com/bboroski/NUNLauncher).

## Назва та сумісність

**SAMBU** — канонічна назва середовища й CLI-аліас. Історичні назви дистрибутива, Python-пакета та розширення .sambu збережені для сумісності; їх заміна потребує окремої міграції API.

## Ліцензія

MIT — див. [LICENSE](LICENSE).

## Академический биологический словарь

- [500 академических терминов EN–RU](data/biology/academic_terms_500.tsv)
- [Контракт и правила использования](docs/BIOLOGY_DOMAIN_PACK.md)

Справочный офлайн-набор для обучения и метаданных; он не управляет системами, устройствами и диагностикой.


## Reaper-inspired engineering domain pack

- [50 curated engineering patterns](data/reaper/engineering_patterns_50.tsv)
- [Domain pack and scientific scope](docs/REAPER_DOMAIN_PACK.md)
- Validate the reference datasets with `python tools/validate_biology_terms.py` and `python tools/validate_reaper_domain.py`.


## Application UI preview

Open `ui/index.html` for the SAMBU Studio concept. Its abstract node field represents source → AST → model → result, supported by a project explorer, scientific inspector and local output panel. All displayed values are synthetic; the preview does not execute the SAMBU interpreter.
