<p align="center"><img src="assets/duck-ui/duck-mark.svg" alt="SAMBU mark" width="92"></p>
<h1 align="center">SAMBU</h1>
<p align="center"><strong>Scientific Modeling &amp; Automation Environment</strong></p>
<p align="center">
<img src="https://img.shields.io/badge/STATUS-EXPERIMENTAL%20ALPHA-FFD600?style=for-the-badge&labelColor=111111" alt="Experimental alpha">
<img src="https://img.shields.io/badge/CORE-PYTHON%20%2B%20C11-FFD600?style=for-the-badge&labelColor=111111" alt="Python and C11">
<img src="https://img.shields.io/badge/LICENSE-MIT-FFD600?style=for-the-badge&labelColor=111111" alt="MIT">
</p>
<p align="center"><a href="README.md">🇺🇦 Українська</a> · <a href="README.en.md">🇬🇧 English</a> · <a href="README.ru.md">🇷🇺 Русский</a></p>


<p align="center"><sub><a href="design/DUCK_UI_SYSTEM.md">Duck Black / Yellow UI standard</a> · <a href="assets/duck-ui/duck-ui-preview.svg">Vector UI preview</a></sub></p>

**SAMBU об'єднує програмування, наукове моделювання та відтворювані робочі процеси в одній експериментальній інженерній середі.** Проєкт орієнтований на тих, кому потрібні зрозумілі моделі, контрольовані обчислення й перевірювані результати.

## Цінність і можливості

- **Мовне ядро:** lexer/parser, AST із source spans, функції, області видимості, масиви, записи, класи та обмежені цикли.
- **Науковий шар:** SI-величини, перевірка розмірностей, фізичні константи, статистична механіка та відтворюване семплювання.
- **Просторові дані:** sparse voxel grids, чанки, Morton keys, octrees, геометрія поверхонь і графові операції.
- **Інструменти:** CLI, Tkinter IDE, тестовий runner, архітектурні перевірки та моделі workflow.
- **Текстові метадані:** детермінований структурний аналіз, повтори, приблизна просодія й семантичні маркери.
- **Native compiler slice:** окремий C11-напрям із типізованими HIR/MIR/LIR та перевірками IR; це ще не повний native-компілятор.

## Швидкий старт

Потрібні Python 3.10+ і Git. Для інтерпретатора обов'язкові сторонні runtime-залежності не потрібні.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Запуск прикладу та перевірки:

~~~bash
sambu examples/ideal_gas.sambu
sambu -c 'print("Hello from SAMBU")'
python -m pytest
python one.py check
~~~

У Windows доступний <code>one.cmd</code>. Команда <code>python one.py</code> запускає стандартний сценарій проєкту.

## Архітектура та межі

SAMBU — Python-hosted experimental alpha. IDE надає редагування файлів, запуск, вивід і базову діагностику, але ще не є повноцінною LSP-IDE. Native compiler slice поки не має повного source-parser bridge, CFG/phi-node підтримки, оптимізаційного конвеєра, object writer або генерації машинного коду. Повна статична система типів та ефектів залишається напрямом розвитку.

## Управління якістю

| Контроль | Критерій |
|---|---|
| Відтворюваність | Однакові вхідні дані та налаштування дають перевірюваний результат |
| Якість | pytest, CLI smoke tests та архітектурні перевірки |
| Межі реалізації | Експериментальні функції позначаються як такі |
| Сумісність | API-зміни супроводжуються явними примітками |
| Інтеграції | Наявність адаптера не означає завершену production-інтеграцію |

Документація: [граматика](docs/ARTICULATORY_SYNTAX.md) · [архітектура екосистеми](docs/ECOSYSTEM_ARCHITECTURE.md) · [мовний конвеєр](docs/MULTILINGUAL_SIGNAL_PIPELINE.md) · [wiki](wiki/README.md).

## Екосистема

SAMBU — мовний і modeling-шар. Суміжні проєкти: [ToolNG](https://github.com/bboroski/ToolNG), [ReaperCripple](https://github.com/bboroski/ReaperCripple), [Kloz](https://github.com/bboroski/Kloz), [CO](https://github.com/bboroski/CO), [SaintSI](https://github.com/bboroski/SaintSI), [Klipot](https://github.com/bboroski/Klipot), [NUN](https://github.com/bboroski/NUN), [NUNLauncher](https://github.com/bboroski/NUNLauncher), [Fragile-Baby](https://github.com/bboroski/Fragile-Baby) і [Luci](https://github.com/bboroski/Luci).

## Ліцензія та внесок

MIT — див. [LICENSE](LICENSE). Перед внеском ознайомтеся з архітектурою та тестами; зміни мають бути локальними, відтворюваними й документованими.

---

**Створено з любов'ю до знань, інженерії та людей.**