"""Curated Mandarin lexicon for SAMBU's Chinese creative-language tools.

The data are deduplicated from a user-supplied studio glossary. Russian glosses
are concise usage notes, not exhaustive dictionary definitions.
"""
from __future__ import annotations

import unicodedata
from typing import Callable

from .filtering import FilteringEngine
from .values import Record


_RAW_ENTRIES = r"""江湖|jiānghú|мир странствующих мастеров, братств и негласного кодекса|jianghu|literary|Культурный образ, а не просто «мир вне закона».
侠|xiá|рыцарь-странник; защитник слабых|jianghu|literary|Часть понятия 侠义 — рыцарская честь.
义|yì|справедливость, долг, верность принципам|jianghu|standard|В сочетаниях может означать верность братству.
气|qì|ци; жизненная сила, дыхание, энергия|jianghu|philosophical|Толкование зависит от контекста.
势|shì|положение, сила обстоятельств, импульс, потенциал|jianghu|standard|В музыкальном образе — напор и momentum.
道|dào|путь, принцип, способ; Дао|jianghu|philosophical|Многозначный базовый термин.
缘|yuán|связь, случай встречи, предопределённая связь|jianghu|literary|В культурном контексте часто имеет оттенок судьбоносной связи.
命|mìng|жизнь, судьба, предписание|jianghu|standard|Не всегда означает фатум.
运|yùn|судьба, удача, ход обстоятельств|jianghu|standard|好运 означает удачу.
魂|hún|душа, дух|jianghu|literary|Часто входит в образные сочетания.
魄|pò|телесная душа, дух, внутренняя сущность|jianghu|literary|В традиционных представлениях противопоставляется 魂.
煞|shà|злая сила, убийственная угроза; дурное влияние|jianghu|literary|Значение определяется сочетанием и контекстом.
戾|lì|жестокий, свирепый; ожесточённость|jianghu|literary|Преимущественно книжное словообразование.
傲|ào|гордый, высокомерный, независимый|jianghu|standard|Может быть как достоинством, так и недостатком.
狂|kuáng|безумный, необузданный, дерзкий|jianghu|standard|Сильная экспрессивная окраска.
悍|hàn|свирепый, жёсткий, стойкий|jianghu|literary|Чаще характеризует человека или силу.
狠|hěn|жёсткий, беспощадный, решительный|jianghu|colloquial|В разговорном и художественном употреблении.
酷|kù|крутой, стильный; cool|jianghu|colloquial|Современное разговорное значение заимствовано от cool.
霸|bà|гегемон; господствовать, доминировать|jianghu|literary|Оттенок власти и принуждения зависит от контекста.
雄|xióng|могучий, героический, выдающийся|jianghu|literary|Часто входит в составные слова.

赛博|sàibó|кибер-, кибернетический; cyber|cyberpunk|technical|Современная транслитерационная форма, часто в 赛博朋克.
朋克|péngkè|панк|cyberpunk|colloquial|Фонетическая передача слова punk.
霓虹|níhóng|неон; радужный свет|cyberpunk|standard|В значении neon обычно встречается в 霓虹灯 — неоновая вывеска.
迷幻|míhuàn|психоделический; гипнотический|cyberpunk|standard|Подходит для описания музыки и визуального стиля.
幻觉|huànjué|галлюцинация, иллюзия восприятия|cyberpunk|standard|Более конкретное значение, чем просто «фантом».
虚无|xūwú|пустота, небытие, нигилизм|cyberpunk|philosophical|Философское и литературное слово.
深渊|shēnyuān|бездна, пропасть|cyberpunk|literary|Образ глубины или опасности.
暗黑|ànhēi|тёмный, мрачный; dark|cyberpunk|colloquial|Часто используется в названиях и эстетических описаниях.
幽灵|yōulíng|призрак, дух|cyberpunk|literary|Может быть метафорой цифрового фантома.
影|yǐng|тень, отражение, изображение|cyberpunk|standard|Один иероглиф с широким спектром значений.
残影|cányǐng|остаточное изображение, шлейф, afterimage|cyberpunk|technical|Пиньинь исправлен: cán yǐng, не hán yǐng.
黑客|hēikè|хакер|cyberpunk|technical|Устойчивый современный термин.
矩阵|jǔzhèn|матрица|cyberpunk|technical|Техническое и математическое значение.
频率|pínlǜ|частота|cyberpunk|technical|Повторяется в исходном списке; хранится один раз.
共振|gòngzhèn|резонанс|cyberpunk|technical|Физический термин, также образно о взаимодействии.
震动|zhèndòng|вибрация, сотрясение|cyberpunk|standard|Для технического «колебания» возможны более специальные термины.
轰鸣|hōngmíng|грохот, рокот, громкий гул|cyberpunk|literary|Звук двигателя, толпы или мощной системы.
撕裂|sīliè|разрывать, рассекать; разрыв|cyberpunk|standard|В звуковом описании — искажённая, «разорванная» текстура.
压|yā|давить, сжимать; давление|cyberpunk|standard|В аудио-контексте это метафора, не точный термин компрессии.
爆|bào|взрываться, разрываться; взрыв|cyberpunk|colloquial|Для клиппинга точнее техническое 削波.
硬核|yìnghé|хардкор; жёсткий, бескомпромиссный|tactics|colloquial|Современное сочетание с разными предметными значениями.
生猛|shēngměng|сырой, энергичный, агрессивный; дикий|tactics|colloquial|Разговорное и экспрессивное описание.
锋芒|fēngmáng|остриё; резкость таланта или характера|tactics|literary|Часто метафорически — проявленная сила.
锋利|fēnglì|острый, режущий|tactics|standard|Буквальное и переносное употребление.
沉|chén|тяжёлый, глубокий; тонуть|tactics|standard|Контекст определяет значение.
沉稳|chénwěn|спокойный, устойчивый, уравновешенный|tactics|standard|Подходит для ровного исполнения или характера.
稳|wěn|устойчивый, надёжный, ровный|tactics|standard|Краткое слово для стабильности.
狠劲|hěnjìn|жёсткий напор, решимость|tactics|colloquial|Разговорное сочетание с сильной экспрессией.
冲锋|chōngfēng|идти в атаку, бросаться вперёд|tactics|standard|Военный и переносный контекст.
突袭|tūxí|внезапная атака, налёт|tactics|standard|Точное значение — surprise attack.
潜行|qiánxíng|скрытно передвигаться|tactics|standard|Также термин из игр и фантастики.
隐蔽|yǐnbì|скрывать, маскировать; скрытый|tactics|standard|Более нейтрально, чем 潜行.
掣肘|chèzhǒu|сдерживать, связывать руки; препятствие|tactics|literary|Устойчивый книжный оборот.
破局|pòjú|вырваться из тупика, изменить расклад|tactics|colloquial|Современная деловая и разговорная метафора.
逆袭|nìxí|контратаковать; совершить камбэк вопреки ожиданиям|tactics|colloquial|Часто используется в медиа и играх.
翻盘|fānpán|перевернуть ход игры; отыграться|tactics|colloquial|Разговорное слово о смене результата.
绝杀|juéshā|решающий удар; победный ход в последний момент|tactics|colloquial|Часто спортивный термин.
终结|zhōngjié|завершить, положить конец|tactics|standard|Нейтрально-официальное слово.
毁灭|huǐmiè|разрушение, уничтожение|tactics|standard|Сильное слово с драматическим оттенком.
涅槃|nièpán|нирвана; возрождение после разрушения|tactics|literary|Буддийский термин; «восстать из пепла» — художественная метафора.

孤高|gūgāo|одинокая гордость; отстранённая независимость|resolve|literary|Может звучать высокомерно или благородно.
孤狼|gūláng|одинокий волк|resolve|literary|Метафора автономного одиночки.
独行|dúxíng|идти одному; действовать самостоятельно|resolve|standard|Не обязательно несёт отрицательный оттенок.
冷血|lěngxuè|хладнокровный; бессердечный|resolve|standard|Может быть резко отрицательной характеристикой.
冷静|lěngjìng|спокойный, рассудительный|resolve|standard|Нейтральная характеристика самообладания.
沉着|chénzhuó|сдержанный, собранный, невозмутимый|resolve|standard|Обычное слово для самообладания под давлением.
泰然|tàirán|невозмутимый, спокойный|resolve|literary|Часто встречается в 泰然自若.
不动|bùdòng|не двигаться; неподвижный|resolve|standard|Для «непоколебимый» часто нужно более полное выражение.
如山|rúshān|как гора; подобный горе|resolve|literary|Обычно часть сравнения, например 稳如山.
如铁|rútiě|как железо; железный|resolve|literary|Пиньинь исправлен: rú tiě, не rǔ tiě.
钢骨|gānggǔ|стальной каркас, железный стержень|resolve|literary|Образное сочетание; не базовый устойчивый термин.
铁血|tiěxuè|железная воля; суровый, бескомпромиссный|resolve|literary|Образное политико-историческое и художественное слово.
烈火|lièhuǒ|яростное пламя, сильный огонь|resolve|literary|Часто употребляется метафорически.
寒霜|hánshuāng|сильный мороз, иней|resolve|literary|Поэтическое сочетание.
幽暗|yōuàn|тусклый, сумрачный, мрачный|resolve|literary|Литературное описание света или места.
诡异|guǐyì|странный, зловещий, причудливый|resolve|standard|Нередко с оттенком жути или аномальности.
妖孽|yāoniè|демоническое существо; чудовище|resolve|literary|Также бранное/гиперболическое обозначение необычного человека.
魔王|mówáng|повелитель демонов; демон-король|resolve|literary|Фэнтезийный образ «главного босса».
霸气|bàqì|властная, доминирующая харизма|resolve|colloquial|Разговорно-положительная оценка уверенной подачи.
气场|qìchǎng|аура, сильное присутствие, харизма|resolve|colloquial|Современное выражение; буквальный смысл — энергетическое поле.

音符|yīnfú|музыкальная нота, нотный знак|sound|technical|Точнее — знак нотной записи, а не сама мелодия.
旋律|xuánlǜ|мелодия|sound|standard|Линия высот и музыкальных фраз.
节奏|jiézòu|ритм|sound|technical|В музыке — организация длительностей и акцентов.
节拍|jiépāi|доля, метрический пульс, такт|sound|technical|Не полная замена слову «темп».
律动|lǜdòng|ритмическое движение, грув|sound|standard|Часто используется в музыкальном описании.
低音|dīyīn|низкий звук; низкий регистр, бас|sound|technical|Для басового инструмента также используют 低音贝斯.
重音|zhòngyīn|ударение, акцент|sound|technical|Может обозначать словесное или музыкальное ударение.
回音|huíyīn|эхо, отражённый звук|sound|standard|Не вполне эквивалентно студийному reverb.
回响|huíxiǎng|отзвук, эхо; резонансный отклик|sound|standard|Пиньинь: huí xiǎng. Для технического reverb точнее 混响.
混响|hùnxiǎng|реверберация, искусственное или акустическое послезвучие|sound|technical|Добавлено для точного обозначения reverb.
混音|hùnyīn|сведение, микширование|sound|technical|Работа с балансом и обработкой дорожек.
母带|mǔdài|мастер-носитель; мастер-запись|sound|technical|В сочетании 母带处理 — мастеринг.
采样|cǎiyàng|сэмплирование; образец данных или звука|sound|technical|В аудио — захват/использование фрагмента записи.
切片|qiēpiàn|срез, нарезанный фрагмент; слайс|sound|technical|В музыке — контекстная метафора нарезки сэмпла.
循环|xúnhuán|цикл, повторение; луп|sound|standard|Для музыкального loop употребляется в контексте.
音色|yīnsè|тембр|sound|technical|Качество окраски звука.
质感|zhìgǎn|текстура, ощущение материала, фактура|sound|standard|В аудио — субъективная фактура звучания.
大气|dàqì|масштабный, величественный; широкий по размаху|sound|standard|Не прямой эквивалент слова «атмосфера».
震撼|zhènhàn|потрясающий, ошеломляющий; сильное впечатление|sound|standard|Описывает воздействие, а не конкретную технику.
巅峰|diānfēng|вершина, пик, высшая точка|sound|standard|Подходит для обозначения пика мастерства.

龙|lóng|дракон|power|standard|Культурно значимый образ силы и удачи.
王|wáng|король, правитель|power|standard|Также компонент слов и титулов.
帝|dì|император; верховный правитель|power|literary|Самостоятельно звучит книжно или титульно.
尊|zūn|уважать; почётный, достойный уважения|power|standard|Самостоятельное 尊 также счётное слово для сосудов.
威|wēi|мощь, власть, авторитет|power|standard|Часто в 威严 — величие и внушительность.
豪|háo|богатый, щедрый, героический, смелый|power|standard|Значение зависит от сочетания.
爵|jué|аристократический титул; ранг знати|power|literary|Исторический титул.
皇|huáng|императорский; император|power|literary|Часто часть составных слов.

富|fù|богатый, состоятельный|wealth|standard|Прилагательное.
贵|guì|дорогой; знатный, почтенный|wealth|standard|Многозначно; не только о деньгах.
金|jīn|золото; металл|wealth|standard|Также фамилия и элемент составных слов.
财|cái|богатство, имущество, финансы|wealth|standard|Часто в 财富 и 财产.
赢|yíng|побеждать, выигрывать|wealth|standard|Не ограничивается денежным выигрышем.
赚|zhuàn|зарабатывать, получать прибыль|wealth|colloquial|Разговорный глагол.
顶|dǐng|верхушка, вершина; поддерживать|wealth|colloquial|В интернет-речи может означать «поддерживаю».
火|huǒ|огонь; популярный, «горячий»|wealth|colloquial|Сленговое значение — в тренде.
红|hóng|красный; популярный, успешный|wealth|standard|Успех и удача — контекстные ассоциации.
发|fā|отправлять, выпускать; процветать|wealth|standard|В 发财 — разбогатеть.

野|yě|дикий, необузданный|character|standard|Также «полевой», «за пределами города».
刚|gāng|твёрдый, жёсткий; только что|character|standard|Многозначный иероглиф.
胆|dǎn|смелость, храбрость; желчный пузырь|character|standard|В 胆量 — смелость.
忠|zhōng|верный, преданный, лояльный|character|standard|Часто о преданности делу или человеку.
勇|yǒng|храбрый, смелость|character|standard|Сильное положительное качество.
真|zhēn|истинный, настоящий, подлинный|character|standard|Также наречие «действительно».

燃|rán|гореть, сгорать; зажигать|action|standard|В сленге может описывать воодушевляющую сцену.
炸|zhà|взрывать, взрываться; жарить|action|standard|В сленге — очень мощный/впечатляющий.
飞|fēi|лететь, летать|action|standard|Сленговые значения зависят от контекста.
跑|pǎo|бежать, бегать|action|standard|Базовый глагол движения.
打|dǎ|ударять, бить; играть, делать|action|standard|Очень многозначный глагол.
杀|shā|убивать, уничтожать|action|standard|Слово буквальное; метафорическое «разнести трек» зависит от контекста.
拼|pīn|бороться, выкладываться; соединять|action|standard|Часто в 拼命 — изо всех сил.
搞|gǎo|делать, устраивать, заниматься чем-либо|action|colloquial|Разговорный широкий глагол.

美|měi|красивый, прекрасный|aesthetic|standard|Также «красота».
雅|yǎ|изысканный, элегантный, утончённый|aesthetic|standard|Часто противопоставляется грубости.
秀|xiù|показывать, демонстрировать; выдающийся|aesthetic|standard|Значение зависит от сочетания.
潮|cháo|прилив; модный, трендовый|aesthetic|colloquial|Разговорное значение «модный».
范|fàn|стиль, манера, образ|aesthetic|colloquial|Часто в 有范儿 — иметь стиль.
型|xíng|тип, модель, форма|aesthetic|standard|Не самостоятельный эквивалент «стиль» во всех контекстах.
色|sè|цвет, окраска; оттенок|aesthetic|standard|Также имеет другие значения в устойчивых сочетаниях.
光|guāng|свет, сияние; только, голый|aesthetic|standard|Базовый многозначный иероглиф.
梦|mèng|сон, мечта|aesthetic|standard|Поэтический образ.

兄|xiōng|старший брат|crew|standard|Чаще в обращениях и составных словах.
弟|dì|младший брат|crew|standard|Также обращение к младшему товарищу.
友|yǒu|друг; дружба|crew|standard|Часто в 朋友.
伴|bàn|спутник, компаньон; сопровождать|crew|standard|Часто в 伙伴.
家|jiā|дом, семья; специалист или деятель|crew|standard|Значение зависит от контекста.
帮|bāng|помогать; группа, объединение|crew|standard|В некоторых контекстах может означать группировку.
众|zhòng|многие, масса, толпа|crew|literary|Часто как компонент 众人.
人|rén|человек, люди|crew|standard|Базовый иероглиф.
己|jǐ|сам, себя|crew|standard|Часто в 自己.
心|xīn|сердце; ум, мысли, намерение|crew|standard|Широкий культурный и языковой диапазон.

天|tiān|небо; день; небеса|philosophy|standard|Контекстно может означать судьбу или высший порядок.
地|dì|земля, суша; место|philosophy|standard|Другое чтение de встречается в наречиях.
空|kōng|пустой, свободный; пустота|philosophy|standard|Не всегда означает космос.
灵|líng|дух, одухотворённость; действенный|philosophy|standard|Многозначное словообразование.
神|shén|божество, дух; необыкновенный|philosophy|standard|В разговорной речи также «крутой/гениальный».
魔|mó|демон, магический/демонический|philosophy|literary|Составная часть фэнтезийной лексики.
变|biàn|меняться, изменять; перемена|philosophy|standard|Базовый глагол и существительное.

牛|niú|корова; разговорно — очень крутой, впечатляющий|slang|colloquial|Похвала в сленге, не универсальна во всех регионах и ситуациях.
赞|zàn|хвалить, одобрять; лайк|slang|colloquial|Также часть слова 赞美.
屌|diǎo|грубое разговорное усиление; крутой (в некоторых контекстах)|slang|vulgar|Вульгарный и неприемлемый в формальной речи и ряде ситуаций.
衰|shuāi|слабеть, приходить в упадок; невезучий|slang|colloquial|Разговорное употребление «не везёт».
囧|jiǒng|неловкий, смущённый; интернет-символ|slang|internet|Современный мемный/сетевой оттенок.
喵|miāo|мяу; звукоподражание кошачьему мяуканью|slang|onomatopoeia|Не обычный термин для описания характера.
嘿|hēi|эй; приветственный или окликающий возглас|slang|colloquial|Междометие.
哈|hā|ха; звук смеха или выдоха|slang|colloquial|Значение зависит от интонации и контекста.
哇|wā|вау; возглас удивления|slang|colloquial|Междометие.
哦|ó|о; выражение понимания или реакции|slang|colloquial|Тон и контекст меняют оттенок.

雷|léi|гром|nature|standard|Также фамилия и часть слов.
电|diàn|электричество; электрический|nature|standard|Часто часть технических слов.
风|fēng|ветер; манера, стиль|nature|standard|Широкая метафорика.
云|yún|облако|nature|standard|В технической лексике также cloud.
雨|yǔ|дождь|nature|standard|Также глагол «лить дождём» в сочетаниях.
雪|xuě|снег|nature|standard|Также фамилия.
山|shān|гора|nature|standard|Частый компонент топонимов.
海|hǎi|море, океан|nature|standard|Также образ огромного пространства.
江|jiāng|крупная река|nature|standard|Входит в название реки Янцзы и другие топонимы.
石|shí|камень, скала; каменный|nature|standard|Также фамилия.

极|jí|предел, крайняя степень; экстремальный|climax|standard|Часто как наречный усилитель.
绝|jué|абсолютный; прекращать, разрывать|climax|standard|Значение резко зависит от сочетания.
妙|miào|тонкий, искусный, чудесный|climax|standard|Оценка изящества или мастерства.
奇|qí|необычный, удивительный, редкий|climax|standard|Также встречается в словах «странный».
特|tè|особый, специальный|climax|standard|Самостоятельное значение обычно требует контекста.
超|chāo|превосходить; сверх-, супер-|climax|standard|Часто как приставочный элемент.
最|zuì|самый; наиболее|climax|standard|Требует контекста сравнения.
全|quán|весь, полный, целый|climax|standard|Базовое прилагательное.
独|dú|один, единственный, самостоятельный|climax|standard|Часто в 独自 или 独特.
壹|yī|один; финансово-официальная форма числа 一|climax|formal|Финансовый вариант написания, а не обычная стилистическая замена."""

_CATEGORY_LABELS = {
    "jianghu": "江湖, честь и братство",
    "cyberpunk": "киберпанк и ночной город",
    "tactics": "тактика, давление и манёвр",
    "resolve": "характер, стойкость и тьма",
    "sound": "звук, ритм и студия",
    "power": "власть и статус",
    "wealth": "деньги и успех",
    "character": "характер и качества",
    "action": "действие и движение",
    "aesthetic": "эстетика и стиль",
    "crew": "люди и отношения",
    "philosophy": "абстракции и философия",
    "slang": "современный сленг и междометия",
    "nature": "природа и стихии",
    "climax": "предел, вершина и итог",
}


def _fold(value: str) -> str:
    """Case- and tone-mark-insensitive search key for Pinyin and Russian text."""
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def _catalogue_rows() -> tuple[tuple[str, str, str, str, str, str], ...]:
    rows = []
    seen: set[str] = set()
    for line_number, line in enumerate(_RAW_ENTRIES.splitlines(), start=1):
        parts = line.split("|")
        if len(parts) != 6:
            raise RuntimeError(f"invalid Chinese lexicon row {line_number}")
        hanzi, pinyin, gloss, category, register, note = parts
        if not hanzi or not pinyin or not gloss or category not in _CATEGORY_LABELS:
            raise RuntimeError(f"incomplete Chinese lexicon row {line_number}")
        if hanzi in seen:
            raise RuntimeError(f"duplicate Chinese lexicon entry {hanzi!r}")
        seen.add(hanzi)
        rows.append((hanzi, pinyin, gloss, category, register, note))
    return tuple(rows)


_ROWS = _catalogue_rows()
_INDEX = {
    hanzi: row for row in _ROWS
    for hanzi in (row[0],)
}


def _record(row: tuple[str, str, str, str, str, str]) -> Record:
    hanzi, pinyin, gloss, category, register, note = row
    return Record({
        "hanzi": hanzi,
        "pinyin": pinyin,
        "pinyin_ascii": _fold(pinyin),
        "gloss": gloss,
        "category": category,
        "category_label": _CATEGORY_LABELS[category],
        "register": register,
        "note": note,
        "source": "user_supplied_studio_glossary_curated",
    })


def zh_terms(args: list[object]) -> list[Record]:
    """Return the full deduplicated lexicon or one named category."""
    if len(args) > 1:
        raise TypeError("zh_terms(category?) expects zero or one argument")
    category = args[0] if args else None
    if category is not None:
        if not isinstance(category, str):
            raise TypeError("Chinese lexicon category must be a string")
        category = category.strip().lower()
        if category not in _CATEGORY_LABELS:
            raise ValueError(f"unknown Chinese lexicon category {category!r}")
    return [
        _record(row) for row in _ROWS
        if category is None or row[3] == category
    ]


def zh_categories(args: list[object]) -> list[Record]:
    """Return the stable category catalogue and term counts."""
    if args:
        raise TypeError("zh_categories() expects no arguments")
    return [
        Record({
            "id": category,
            "label": label,
            "count": sum(1 for row in _ROWS if row[3] == category),
        })
        for category, label in _CATEGORY_LABELS.items()
    ]


def zh_lookup(args: list[object]) -> Record:
    """Find exact Hanzi or exact Pinyin (tone marks may be omitted)."""
    if len(args) != 1 or not isinstance(args[0], str) or not args[0].strip():
        raise TypeError("zh_lookup(term_or_pinyin) expects one non-empty string")
    query = args[0].strip()
    folded = _fold(query)
    matches = [
        _record(row) for row in _ROWS
        if query == row[0] or folded == _fold(row[1])
    ]
    return Record({
        "found": bool(matches),
        "query": query,
        "count": len(matches),
        "matches": matches,
        "match_mode": "exact_hanzi_or_tone_insensitive_pinyin",
    })


def zh_search(args: list[object]) -> Record:
    """Search Hanzi, Pinyin, Russian glosses, notes or an optional category."""
    if not 1 <= len(args) <= 2 or not isinstance(args[0], str) or not args[0].strip():
        raise TypeError("zh_search(query, category?) expects a non-empty query and optional category")
    query = args[0].strip()
    query_hanzi = query.casefold()
    query_folded = _fold(query)
    category = args[1] if len(args) == 2 else None
    if category is not None:
        if not isinstance(category, str):
            raise TypeError("Chinese lexicon category must be a string")
        category = category.strip().lower()
        if category not in _CATEGORY_LABELS:
            raise ValueError(f"unknown Chinese lexicon category {category!r}")
    matches = []
    for row in _ROWS:
        hanzi, pinyin, gloss, row_category, _, note = row
        if category is not None and row_category != category:
            continue
        searchable = (hanzi, pinyin, gloss, note, row_category, _CATEGORY_LABELS[row_category])
        if any(
            query_hanzi in value.casefold() or query_folded in _fold(value)
            for value in searchable if value
        ):
            matches.append(_record(row))
    return Record({
        "query": query,
        "category": category,
        "count": len(matches),
        "matches": matches,
        "method": "unicode_casefold_and_pinyin_folded_substring",
    })


def zh_filter(args: list[object]) -> Record:
    """Filter lexicon records using 04coq's declarative predicate engine."""
    if len(args) not in {1, 2}:
        raise TypeError("zh_filter(rules, mode='all') expects one or two arguments")
    mode = args[1] if len(args) == 2 else "all"
    return FilteringEngine().filter(zh_terms([]), args[0], mode)


def zh_lexicon_stats(args: list[object]) -> Record:
    """Report catalogue size, category counts and editorial corrections."""
    if args:
        raise TypeError("zh_lexicon_stats() expects no arguments")
    counts = {
        category: sum(1 for row in _ROWS if row[3] == category)
        for category in _CATEGORY_LABELS
    }
    return Record({
        "term_count": len(_ROWS),
        "category_count": len(_CATEGORY_LABELS),
        "category_counts": [Record({"category": key, "count": value}) for key, value in counts.items()],
        "deduplicated": True,
        "pinyin_search_ignores_tone_marks": True,
        "editorial_corrections": [
            Record({"hanzi": "残影", "pinyin": "cányǐng", "correction": "replaced incorrect hán yǐng"}),
            Record({"hanzi": "如铁", "pinyin": "rútiě", "correction": "corrected first syllable tone"}),
            Record({"hanzi": "回响", "pinyin": "huíxiǎng", "correction": "corrected tone on second syllable"}),
            Record({"hanzi": "混响", "pinyin": "hùnxiǎng", "correction": "added the precise studio term for reverberation"}),
        ],
    })


CHINESE_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "zh_terms": zh_terms,
    "zh_categories": zh_categories,
    "zh_lookup": zh_lookup,
    "zh_search": zh_search,
    "zh_filter": zh_filter,
    "zh_lexicon_stats": zh_lexicon_stats,
}
