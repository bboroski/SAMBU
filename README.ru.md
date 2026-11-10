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

**Экспериментальная среда для программирования, научных моделей, пространственных данных и воспроизводимых процессов.** SAMBU объединяет интерпретируемое языковое ядро, инструменты на Python и отдельное раннее направление нативного компилятора.

## Для чего нужен SAMBU

SAMBU рассчитан на инженеров и исследователей, которым нужны понятные модели, контролируемые вычисления и проверяемые инструменты. Цель — связать язык, научные предметные области и рабочие процессы, не скрывая реальные границы реализации.

## Возможности

- **Языковое ядро:** lexer/parser, AST с source spans, функции, области видимости, массивы, записи, классы и ограниченные циклы.
- **Научные вычисления:** величины SI, проверка размерностей, физические константы, статистическая механика и воспроизводимая выборка.
- **Пространственные модели:** sparse voxel grids, чанки, Morton keys, octrees, геометрия поверхностей и графовые операции.
- **Workflow и инструменты:** CLI, Tkinter IDE, тестовый runner, архитектурные проверки и модели workflow.
- **Текстовые метаданные:** детерминированный анализ структуры, повторов, приблизительной просодии и семантических маркеров. Это анализ данных, а не генерация текста и не оценка художественного качества.
- **Срез native-компилятора:** изолированное направление на C11 с типизированными HIR/MIR/LIR и проверкой IR; это ещё не полноценный нативный компилятор.

## Быстрый старт

Нужны Python 3.10+ и Git. Интерпретатор не требует обязательных сторонних runtime-зависимостей.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Запуск программы:

~~~bash
sambu examples/ideal_gas.sambu
sambu -c 'print("Hello from SAMBU")'
~~~

Проверки и единая точка запуска:

~~~bash
python -m pytest
python one.py check
~~~

В Windows также доступен файл <code>one.cmd</code>. Команда <code>python one.py</code> запускает стандартный сценарий проекта.

## Инструменты разработчика

IDE уже поддерживает редактирование файлов, запуск, вывод и базовую диагностику. Это рабочий интерфейс, но пока не полноценная LSP-IDE.

<p align="center">
  <img src="assets/duck-ui/duck-studio-preview.svg" alt="Предпросмотр SAMBU Studio" width="49%" />
  <img src="assets/duck-ui/ide-editor-preview.svg" alt="Предпросмотр редактора SAMBU IDE" width="49%" />
</p>

## Управление проектом и критерии готовности

| Контрольная точка | Текущая политика |
|---|---|
| Зрелость | Experimental alpha; API и возможности могут меняться |
| Проверки | pytest, CLI smoke tests и архитектурные проверки |
| Native path | Отдельный экспериментальный срез; не заменяет Python-интерпретатор |
| Интеграции | Наличие адаптера или профиля не означает завершённую production-интеграцию |
| Изменения API | Совместимые пути сохраняются до отдельной документированной миграции |

## Архитектура и ограничения

SAMBU — alpha-проект на базе Python. Расширения Flask, Django и FastAPI необязательны. В native compiler path пока нет полного source-parser bridge, поддержки CFG/phi-node, конвейера оптимизаций, object writer и генерации машинного кода. Полная статическая система типов/эффектов и LSP остаются направлениями развития.

Документация:
- [Артикуляционная грамматика](docs/ARTICULATORY_SYNTAX.md)
- [Архитектура экосистемы](docs/ECOSYSTEM_ARCHITECTURE.md)
- [Мультиязычный конвейер сигналов](docs/MULTILINGUAL_SIGNAL_PIPELINE.md)
- [Энциклопедия SAMBU](wiki/README.md)

## Экосистема

SAMBU — языковой и модельный слой семейства: [ToolNG](https://github.com/bboroski/ToolNG) · [ReaperCripple](https://github.com/bboroski/ReaperCripple) · [Kloz](https://github.com/bboroski/Kloz) · [CO](https://github.com/bboroski/CO) · [SaintSI](https://github.com/bboroski/SaintSI) · [Klipot](https://github.com/bboroski/Klipot) · [NUN](https://github.com/bboroski/NUN) · [NUNLauncher](https://github.com/bboroski/NUNLauncher).

## Название и совместимость

**SAMBU** — каноническое имя среды и CLI-алиас. Исторические названия дистрибутива, Python-пакета и расширение .sambu сохранены для совместимости; их замена требует отдельной миграции API.

## Лицензия

MIT — см. [LICENSE](LICENSE).
