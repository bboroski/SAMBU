# SAMBU
**Scientific Modeling & Automation Environment**

[Українська](README.md) · [English](README.en.md) · [Русский](README.ru.md)

Экспериментальная среда на Python для программирования, научного моделирования и воспроизводимых рабочих процессов.

## Возможности
- Ядро языка: lexer/parser, AST, функции, области видимости, массивы и записи.
- Величины SI, проверка размерностей, физические константы и воспроизводимая выборка.
- Sparse voxel grids, чанки, Morton keys, octrees и графовые операции.
- Статический семантический анализ, CLI, Tkinter IDE и тестовый runner.
- Частичный native compiler на C11; это не полноценный компилятор.

## Запуск и проверка
```bash
python -m pip install -e .
python -m pytest
python one.py check
```

## Границы
Native compiler пока не обеспечивает полный конвейер source-to-machine-code. IDE не является полноценной LSP-системой. Экспериментальные функции не готовы к production.

## Документация проекта
![Duck Studio — рабочее пространство](docs/images/duck-studio-overview.webp)

![Duck Studio — отчёты](docs/images/duck-studio-reports-findings.webp)

![Duck Studio — XML inspector](docs/images/duck-studio-xml-inspector.webp)

## Связанные проекты
[Duck Studio](docs/DUCK_STUDIO.md) · [IDE](docs/IDE.md) · [семантический анализ](docs/SEMANTIC_ANALYSIS.md)

[Luci](https://github.com/bboroski/Luci) · [Hellduck](https://github.com/bboroski/Hellduck)

## Лицензия
MIT

---
**两情若是久长时，又岂在朝朝暮暮。**
*Если чувство длится вечно, разве нужно быть вместе каждый день?*
— Цинь Гуань, 《鹊桥仙》
