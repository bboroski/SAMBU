# SAMBU
**Наукове моделювання, автоматизація та експериментальна мова програмування.**

Python-hosted середовище для програмування, наукових моделей і відтворюваних workflow. Проєкт експериментальний.

![Duck Studio](docs/images/duck-studio-overview.webp)

## Можливості
- Lexer, parser, AST, функції, області видимості, масиви та записи.
- SI-величини, перевірка розмірностей, фізичні константи й відтворюване семплювання.
- Sparse voxel grids, чанки, Morton keys, octrees і графові операції.
- Статичний семантичний аналіз, CLI, Tkinter IDE та тестовий runner.
- Експериментальний C11 compiler slice з типізованим IR; це ще не повний native-компілятор.

## Запуск і перевірка
```bash
python -m pip install -e .
python -m pytest
python one.py check
```

## Додатково
![Звіти Duck Studio](docs/images/duck-studio-reports-findings.webp)
![XML inspector](docs/images/duck-studio-xml-inspector.webp)

## Межі
Native compiler slice не має повного source-to-machine-code конвеєра. IDE не є повноцінною LSP-системою. Експериментальні функції не слід вважати production-ready.

## Пов'язані проєкти
[Luci](https://github.com/bboroski/Luci) · [Hellduck](https://github.com/bboroski/Hellduck)

## Ліцензія
MIT

---
**「愿得一心人，白头不相离。」**
*«Знайти людину, віддану серцем, і не розлучатися до сивини».*
— «Біла голова» (《白头吟》), давня юефуська поезія