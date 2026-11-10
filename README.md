<div align="center">

<img src="assets/sambu-ducklings.svg" alt="Родина качок SAMBU — векторна ілюстрація" width="100%" />

# SAMBU

### Statistical Analysis · Modeling · Systems · Trust

**Невелика мова з широким горизонтом.**

Експериментальна інтерпретована мова та Python-інструментарій для наукових обчислень, моделювання, системної архітектури, workflow та розріджених voxel-світів.

[Українська](README.md) · [English](README.en.md) · [Русский](README.ru.md)

[![Version](https://img.shields.io/badge/version-0.11.0--alpha-536D8E?style=for-the-badge)](https://github.com/bboroski/SAMBU)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-26866B?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/bboroski/SAMBU/tests.yml?branch=main&style=for-the-badge&label=checks)](https://github.com/bboroski/SAMBU/actions)

[Швидкий старт](#-швидкий-старт) · [Мова](#-мова-sambu) · [Можливості](#-карта-можливостей) · [Інструменти](#-інструменти) · [Документація](#-документація)

</div>

---

> **Стадія зрілості: експериментальна alpha.** Інтерпретатор, вибрані предметні модулі та CLI-інструменти реалізовані й тестуються. Нативний компілятор, повна статична система типів та ефектів, повноцінна LSP-IDE й частина інтеграцій залишаються напрямами розвитку.

## Що таке SAMBU

SAMBU поєднує мову для програм <code>.sambu</code> з Python-пакетом для наукових, архітектурних і workflow-завдань. Основні принципи: явні припущення, обмежені операції, перевірювані результати та модульна еволюція.

## Карта можливостей

<img src="assets/architecture-map.svg" alt="Багаторівнева архітектура SAMBU: мовні поверхні, runtime, наукові модулі, voxel-системи й інструментарій" width="100%" />

| Напрям | Реалізовані можливості |
|---|---|
| **Мовне ядро** | Lexer/parser, незмінний AST із source spans, області видимості, функції, обмежені цикли, масиви, записи, класи та наслідування. |
| **Наукові обчислення** | SI-величини, перевірка розмірностей, фізичні константи, теплова енергія, швидкості Максвелла, фактори Больцмана, статистичні суми, ентропія та відтворюване семплювання. |
| **Sparse voxel** | Обмежені чанки, афінні системи координат, Morton keys, побудова поверхонь, 3D DDA, sparse octrees, графові лапласіани та VOX interchange. |
| **Інженерні модулі** | Nun — відтворювані початкові стани й граничні контракти; Judo — архітектурні графи; Aikido — маршрутизація inference; Jiu-Jitsu — UI/MVC/RBAC-моделі; workflow, trust-перевірки та оборотні патчі. |
| **Runtime-експерименти** | Обмежені actor-mailbox, послідовна фіксація стану, dead-letter записи, supervision і типізовані програмні канали. Це не нативне паралельне виконання. |
| **Інструменти** | CLI sambu, read-only аналізатор Magento XML sambu-studio, Tkinter IDE sambu-ide, sambu-test і SAMBU Machine. |
| **Аналіз творчого тексту** | Детермінований розбір секцій, повторів припіву та компактних хуків, змішення письменностей, приблизна просодія, письмові performance-cues і дев’ять кластерів перевірюваних метаданих. |

### Артикуляційний синтаксис

Друга детермінована поверхня синтаксису утворюється матрицею: **10 семантичних приголосних сімейств × 5 голосних градацій × 4 граматичні закінчення = 200 форм**. Поточний словник містить 25 граматичних форм, 137 вбудованих і 38 зарезервованих.

<img src="assets/articulatory-syntax.svg" alt="Матриця артикуляційного синтаксису SAMBU: фонетичні сімейства та граматичні ролі" width="100%" />

Це формальний синтаксичний пласт над собою, а не обробка природної мови чи генерація коду мовною моделлю. [Специфікація](docs/ARTICULATORY_SYNTAX.md).

### Конвеєр sparse voxels

<img src="assets/voxel-pipeline.svg" alt="Конвеєр sparse voxel: від зайнятих комірок до просторових структур, геометрії та renderer-neutral payload" width="100%" />

Стартовий bridge-код доступний для Unity, Unreal Engine, Godot, Bevy та Open 3D Engine. Наявність профілю чи starter-коду не означає завершений або апаратно перевірений плагін.

## Швидкий старт

**Вимоги:** Python 3.10+, Git. Основний інтерпретатор не має обов’язкових сторонніх runtime-залежностей.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Створіть hello.sambu:

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
sambu hello.sambu
# або
sambu -c 'print("Hello from SAMBU")'
~~~

Приклади:

~~~bash
sambu examples/ideal_gas.sambu
sambu examples/boltzmann_weights.sambu
sambu examples/oop_and_games.sambu
sambu examples/voxel_world.sambu
sambu examples/supervised_runtime.sambu
~~~

## Мова SAMBU

Мова підтримує оголошення, вирази, користувацькі функції, умовні конструкції, обмежену ітерацію, масиви, записи, доступ до полів та експериментальну об’єктну модель.

~~~sambu
fn square(value) {
  return value * value
}
for number in range(1, 5) {
  print(square(number))
}
let distance = 12 * m
let duration = 3 * s
print(distance / duration)
~~~

Фізичні величини зберігаються в SI-нормалізованій формі. Додавання й порівняння потребують сумісних розмірностей; множення та ділення комбінують їхні показники. Документовані цикли й range обмежено 100 000 елементами.

Артикуляційний приклад:

~~~sambu
kava temperature = 300 * K
kava particle_mass = 6.6e-26 * kg
kava profile = vava(temperature, particle_mass)
lava(profile.rms)
~~~

## Інструменти

| Команда | Призначення |
|---|---|
| sambu | Запуск файлів та inline-коду; генерація каркасів проєктів. |
| sambu-ide | Легка Tkinter IDE. |
| sambu-studio inspect PATH | Read-only аналіз підтримуваних Magento / Adobe Commerce XML. |
| sambu-test tests --repeat 2 | Повторні тести та зведення варіативності. |
| sambu machine architecture | Перевірка оголошених архітектурних шарів. |
| sambu machine sample FILE --ratio 100 --seed 17 | Відтворюване семплювання AST. |

IDE має редактор, відкриття/збереження файлів, запуск F5, вивід, діагностику та перемикання RU/EN. Це ще не LSP-клієнт. Machine підтримує архітектурну перевірку та детерміноване семплювання, але не повний статичний аналіз типів/ефектів і не нативну компіляцію.

Необов’язкові адаптери:

~~~bash
python -m pip install -e ".[flask]"
python -m pip install -e ".[django]"
python -m pip install -e ".[fastapi]"
~~~

Автентифікація, транспортна безпека, збереження даних і авторизація залишаються відповідальністю host-застосунку.

## Творчий текст і семантичні метадані

SAMBU містить версійну онтологію creative metadata **2026.12** із дев’ятьма кластерами T-001…T-009. Метадані зберігають людські анотації, а не вихідні тексти. У прикладах корпусу всі записи мають прапорець \`NEEDS_REVIEW\`; це тестові fixtures, а не схвалений набір для навчання.

Text Craft надає детерміновані описи структури й звуку:

- заголовки секцій, точні повтори припіву та компактна структура хуку;
- видиме змішення латиниці, кирилиці та інших письменностей;
- приблизні слогові підрахунки, орфографічні групи рим, внутрішні співзвуччя й алітерація;
- авторські регістрові наголоси та письмові performance-cues: сценічні ремарки, скобкові ad-lib, цитати й фонетичні повтори.

\`hook_profile(text)\` аналізує компактний хук із 2–4 непорожніх рядків, повторювані слова/рядки, наближені рими та розкид кількості складів. Він не прогнозує хітовість або реакцію аудиторії. \`performance_cues_profile(text)\` повертає тип маркера та його позицію у вихідному рядку, але не виводить емоцію, особу мовця чи реальну манеру виконання.

Приклад:

~~~sambu
let draft = "[Verse:]\nПерший рух\n[Melody sing Chorus:]\nМелодія повертається\n[Chorus:]\nМелодія повертається\n(Verse 2)\nІнший рух\n*Phone rings*\n(Mm-mm)\nру-ру-Русско"
let structure = text_structure_profile(draft)
let cues = performance_cues_profile(draft)
print(structure.refrain_groups[0].repeat_count)
print(structure.sections[1].performance_hint)
print(cues.marker_count)
~~~

Перевірка metadata fixture:

~~~bash
sambu creative clusters --json
sambu creative validate examples/creative_corpus_metadata.sample.json --json
sambu examples/performance_cues.sambu
~~~

Це не автоматичний класифікатор, не embeddings і не fine-tuning pipeline. Мова визначається окремо від письма; рими й скла — приблизні орфографічні евристики. Текст автора не переписується.

Документація: [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md), [Text Craft](docs/text_craft.md), [Hook Craft і моделі відкритих систем](docs/OPEN_SYSTEM_AND_HOOK_CRAFT.md), [JSON Schema](schemas/creative-metadata.schema.json).

## Інженерна доктрина

- **Safety** — явні дозволи та межі довіри.
- **Adaptive exploration** — відтворювані експерименти на основі гіпотез.
- **Managed recovery** — обмеження пам’яті, черг, роботи та повторів.
- **Branchable design** — модульні шари й явні контракти.
- **Unforced interoperability** — стабільні інтерфейси та свобода користувача.

Machine додає capability-профілі, детерміноване семплювання AST 1:100 і обмежений Ghost Ledger. Профіль sealed призначений для інспекції; sandbox дозволяє виконання в інтерпретаторі SAMBU. Жоден із них не є OS sandbox. Host/device — зарезервовані межі адаптерів, а не готовий доступ до shell, мережі чи обладнання.

## Перевірка та статус

~~~bash
python -m unittest discover -s tests -v
sambu-test tests --repeat 2
sambu-test tests --repeat 2 --json
~~~

**Реалізовано:** інтерпретатор, Python-модулі, наукові функції, sparse voxel-операції, окремі actor/channel-примітиви, CLI, Machine inspection, IDE-сервіси й Tkinter-редактор.

**Розвивається:** статичний аналіз, семантика ownership/effects, інтеграція IDE, етапи нативного toolchain та адаптери host/device.

**Не заявляється як готове:** нативний компілятор, self-hosting, сумісність із C++ ABI, повна сумісність із Pascal/Delphi/Fortran, production web-framework, автоматичне розгортання, OS sandbox або повноцінна LSP IDE.

## Документація

- [Артикуляційний синтаксис](docs/ARTICULATORY_SYNTAX.md) · [Інженерна доктрина](docs/SAMBU_ENGINEERING_DOCTRINE.md)
- [Системна архітектура](docs/CRIPPLE_SYSTEMS_ARCHITECTURE.md) · [Nun: genesis і початкові умови](docs/NUN_GENESIS.md) · [Voxel Reference](docs/VOXELS.md)
- [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md) · [Text Craft](docs/text_craft.md) · [Hook Craft](docs/OPEN_SYSTEM_AND_HOOK_CRAFT.md) · [Studio Guide](docs/DUCK_STUDIO.md)
- [Вихідний код і тести](https://github.com/bboroski/SAMBU/tree/main) · [Issues](https://github.com/bboroski/SAMBU/issues)

## Участь і ліцензія

Вітаються цільові pull request із відтворюваним прикладом, тестами та описом припущень. MIT — див. [LICENSE](LICENSE).

<div align="center">

**SAMBU — моделюй чітко. Поєднуй обережно. Перевіряй чесно.** 🦆

</div>
