<div align="center">

<img src="assets/architecture-map.svg" alt="Багаторівнева архітектура обчислювального середовища" width="100%" />

# MCL — Multidomain Computation Language

### Мова обчислень · наукове моделювання · системні workflow

**Формалізуй. Обчислюй. Перевіряй.**

MCL — експериментальне інтерпретоване середовище з Python-інструментарієм для наукових обчислень, явного моделювання, системної архітектури, обмежених робочих процесів і розріджених voxel-структур.

[Українська](README.md) · [English](README.en.md) · [Русский](README.ru.md)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-26866B?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/bboroski/SAMBU/tests.yml?branch=main&style=for-the-badge&label=checks)](https://github.com/bboroski/SAMBU/actions)

</div>

---

> **Зрілість: experimental alpha.** Інтерпретатор, вибрані предметні модулі та CLI-інструменти реалізовані й тестуються. Нативний компілятор, повна статична система типів та ефектів, завершена LSP-IDE й частина інтеграцій залишаються напрямами розвитку.

## Призначення

MCL поєднує інтерпретовану мову з Python-пакетом для науки, інженерного моделювання та автоматизованих процесів. Основні принципи: явні припущення, обмежені операції, відтворювані результати, перевірювані контракти й модульна еволюція.

## Карта можливостей

| Область | Реалізовані можливості |
|---|---|
| **Мовне ядро** | Lexer/parser, незмінний AST із source spans, області видимості, функції, обмежені цикли, масиви, записи, класи та наслідування. |
| **Наукові обчислення** | SI-величини, перевірка розмірностей, фізичні константи, теплова енергія, розподіли швидкостей, фактори Больцмана, статистичні суми, ентропія та відтворюване семплювання. |
| **Розріджена геометрія** | Обмежені чанки, афінні координатні системи, Morton keys, побудова поверхонь, 3D DDA, sparse octrees, графові лапласіани та VOX interchange. |
| **Інженерні моделі** | Графи архітектури, маршрутизація inference, UI/MVC/RBAC-моделі, workflow, перевірки довіри та оборотні патчі. |
| **Runtime-експерименти** | Обмежені actor-mailbox, послідовна фіксація стану, dead-letter записи, supervision і типізовані програмні канали; це не нативне паралельне виконання. |
| **Інструменти** | Командний інтерфейс, read-only аналіз XML-каталогів, Tkinter IDE, тестовий runner та перевірка архітектурних профілів. |
| **Аналіз тексту** | Детермінований розбір секцій і повторів, змішаних письменностей, приблизної просодії, performance-cues та дев’яти кластерів метаданих. |

### Артикуляційна граматика

Додаткова синтаксична поверхня визначається матрицею: **10 семантичних приголосних сімейств × 5 градацій голосних × 4 граматичні закінчення = 200 форм**. Це формальний parser-рівень, а не обробка природної мови чи генерація коду мовною моделлю. Специфікація: [ARTICULATORY_SYNTAX](docs/ARTICULATORY_SYNTAX.md).

<img src="assets/articulatory-syntax.svg" alt="Матриця формальної артикуляційної граматики" width="100%" />

### Конвеєр sparse voxel

<img src="assets/voxel-pipeline.svg" alt="Перетворення зайнятих комірок на просторові структури та геометрію" width="100%" />

Стартові адаптери доступні для Unity, Unreal Engine, Godot, Bevy та Open 3D Engine. Наявність профілю або стартового коду не означає завершений чи апаратно перевірений плагін.

## Швидкий старт

**Вимоги:** Python 3.10+ та Git. Основний інтерпретатор не має обов’язкових сторонніх runtime-залежностей.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
mcl --version
~~~

Створіть файл hello.sambu:

~~~sambu
let temperature = 300 * K
let particle_mass = 6.6e-26 * kg
let profile = maxwell(temperature, particle_mass)
print(profile.most_probable)
print(profile.mean)
print(profile.rms)
~~~

Запуск:

~~~bash
mcl hello.sambu
mcl -c 'print("Hello from MCL")'
~~~

Розширення .sambu та попередні команди sambu* залишаються для сумісності. Нові команди mcl* є рекомендованим інтерфейсом.

## Інструменти

| Команда | Призначення |
|---|---|
| mcl | Запуск файлів та inline-коду; генерація каркасів. |
| mcl-ide | Легка Tkinter IDE. |
| mcl-studio inspect PATH | Read-only аналіз підтримуваних XML-структур commerce-каталогів. |
| mcl-test tests --repeat 2 | Повторні тести та зведення варіативності. |
| mcl machine architecture | Перевірка оголошених архітектурних шарів. |
| mcl machine sample FILE --ratio 100 --seed 17 | Відтворюване семплювання AST. |

IDE підтримує редагування, відкриття/збереження файлів, запуск F5, вивід, діагностику та перемикання RU/EN. Це ще не LSP-клієнт. Повний статичний аналіз типів/ефектів і нативна компіляція не заявляються як готові.

## Текстова аналітика та метадані

Функції аналізу описують структуру, а не оцінюють художню якість: секції, точні повтори приспівів, компактні хуки, змішення письма, приблизні склади, орфографічні групи рим, внутрішні співзвуччя та письмові performance-cues. Вони не прогнозують популярність, не виводять особу мовця чи емоційний стан і не переписують авторський текст.

Онтологія анотацій містить дев’ять кластерів. Приклади корпусу позначені NEEDS_REVIEW: це тестові fixtures, а не схвалені навчальні дані.

Документація: [Text Craft](docs/text_craft.md) · [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md) · [Open System and Hook Craft](docs/OPEN_SYSTEM_AND_HOOK_CRAFT.md).

## Інженерні принципи

- **Safety:** явні дозволи та межі довіри.
- **Adaptive exploration:** відтворювані експерименти на основі гіпотез.
- **Managed recovery:** обмеження пам’яті, черг, роботи та повторів.
- **Branchable design:** модульні шари й явні контракти.
- **Interoperability:** стабільні інтерфейси та свобода інтегратора.

Профілі inspection та sandbox не є OS sandbox. Зарезервовані host/device-адаптери не надають автоматичного доступу до shell, мережі або обладнання.

## Перевірка та статус

~~~bash
python -m unittest discover -s tests -v
mcl-test tests --repeat 2
mcl-test tests --repeat 2 --json
~~~

**Реалізовано:** інтерпретатор, Python-модулі, наукові функції, sparse voxel-операції, окремі actor/channel-примітиви, CLI, архітектурна інспекція та IDE-сервіси.

**Розвивається:** статичний аналіз, ownership/effect semantics, інтеграція IDE, native toolchain та host/device-адаптери.

**Не заявляється як готове:** нативний компілятор, self-hosting, повна сумісність із C++ ABI чи іншими мовами, production web-framework, автоматичне розгортання або повноцінна LSP IDE.

## Документація та участь

- [Артикуляційний синтаксис](docs/ARTICULATORY_SYNTAX.md) · [Інженерна доктрина](docs/SAMBU_ENGINEERING_DOCTRINE.md)
- [Системна архітектура](docs/CRIPPLE_SYSTEMS_ARCHITECTURE.md) · [Voxel Reference](docs/VOXELS.md)
- [Керування творчими даними](docs/CREATIVE_DATA_GOVERNANCE.md) · [Посібник IDE](docs/DUCK_STUDIO.md)
- [Вихідний код](https://github.com/bboroski/SAMBU/tree/main) · [Issues](https://github.com/bboroski/SAMBU/issues)

Ідентифікатори зовнішніх API, платформ і форматів залишаються точними заради сумісності. Міграція внутрішніх імен не повинна змінювати формат уже збережених програм без окремого перехідного механізму.

## Ліцензія

MIT — див. [LICENSE](LICENSE).
