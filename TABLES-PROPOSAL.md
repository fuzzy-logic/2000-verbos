# Proposed reference tables — "Tables" tab

18 tables, ~700 rows. Original content, written for **Paraguay** (voseo, local
vocabulary, Guaraní) rather than generic Spanish. Designed to complement the
2000-verb deck, not repeat it: the deck gives you verbs in sentences, these give
you the scaffolding — the words you need *around* the verb.

Format: one TSV per table in `data/tables/`, matching the existing pipeline, so
`build.py` picks them up and inlines them. Columns throughout:

    spanish | english | note

**Approve, cut or reorder before I write the content.** Row counts are estimates.

---

## A. Essentials (the first week)

### 1. `question-words` — ~16 rows
Every question you'll need to ask. The thing generic courses miss: `¿Cómo andás?`
is the normal greeting here, not `¿Cómo estás?`.

| spanish | english | note |
|---|---|---|
| ¿qué? | what? | |
| ¿dónde? | where? | ¿dónde está…? = where is…? |
| ¿adónde? | where to? | motion, not location |
| ¿cuánto cuesta? | how much does it cost? | the single most useful question |
| ¿cómo andás? | how's it going? | voseo; the standard greeting here |

### 2. `pronouns` — ~20 rows
Includes the Paraguay-specific point that `vosotros` does not exist here —
plural "you" is always `ustedes`.

| spanish | english | note |
|---|---|---|
| vos | you (singular, informal) | not `tú` — this is the normal form |
| ustedes | you (plural) | `vosotros` is never used here |
| me / te / se | me / you / himself | the clitics that confuse beginners |

### 3. `numbers` — ~45 rows
0–20, the 21–29 pattern, tens, hundreds, thousands — **plus a money block**,
because Paraguayan prices run in tens of thousands and you will hear `mil`
constantly. Misreading a price by a factor of ten is the classic new-arrival mistake.

| spanish | english | note |
|---|---|---|
| mil | one thousand | written 1.000 — a full stop, not a comma |
| diez mil | ten thousand | ≈ a cheap lunch |
| cincuenta mil | fifty thousand | the common banknote |
| ¿cuánto sale? | what does it come to? | more common than `¿cuánto cuesta?` in shops |

### 4. `time-and-dates` — ~40 rows
Days, months, telling the time, and relative days. Flags that the seasons are
**inverted** — summer is December to February, and January is the hottest month.

| spanish | english | note |
|---|---|---|
| ¿qué hora es? | what time is it? | |
| a las ocho y media | at half past eight | |
| anteayer | the day before yesterday | one word, no English equivalent |
| verano | summer | December–February here |

---

## B. Core vocabulary by topic

### 5. `top-verbs-voseo` — ~45 rows
A conjugation quick-reference the main deck deliberately doesn't give you: the
most essential verbs with `yo` and `vos` forms side by side, so the pattern
becomes visible. Directly addresses not being able to connect `ir` to `voy`.

| spanish | english | note |
|---|---|---|
| ir — voy, vas | to go — I go, you go | irregular: no form contains "ir" |
| tener — tengo, tenés | to have — I have, you have | voseo: drop -r, stress the end |
| poder — puedo, podés | to be able — I can, you can | stem change o→ue in `yo` |

### 6. `people-and-family` — ~35 rows
Family, relationships, describing people. Family matters more socially here than
you may be used to, and `mi señora`, `mi viejo` etc. are everyday usage.

### 7. `food-and-drink` — ~55 rows
The highest-value table in the list. Includes the traps: **`sopa paraguaya` is a
cornbread, not a soup.** Plus `chipa`, `mandioca`, `tereré`, `cocido`, `mbejú`,
`asado`, `milanesa`, `empanada`, and how to order.

| spanish | english | note |
|---|---|---|
| sopa paraguaya | Paraguayan cornbread | NOT soup — it's solid and you slice it |
| mandioca | cassava | served with almost everything |
| tereré | cold yerba mate infusion | shared; refusing the guampa is rude |
| ¿me trae la cuenta? | could you bring the bill? | |

### 8. `places-and-directions` — ~40 rows
Getting around and asking the way, including `despensa` (corner shop) and the
`cuadra` (block) as the local unit of distance.

### 9. `house-and-objects` — ~45 rows
Renting and living. Heavy on Paraguayan words that differ from textbook Spanish:
`heladera` (fridge), `canilla` (tap), `pieza` (room), `ventilador`, `patio`.

### 10. `body-and-health` — ~40 rows
Body parts, symptoms, and pharmacy language. Includes `dengue`, which is a real
and seasonal concern here, and how to describe pain (`me duele…`).

### 11. `clothes-and-shopping` — ~35 rows
`remera` (t-shirt), `pollera` (skirt), `plata` (money), `vuelto` (change),
plus haggling language for the market.

### 12. `transport` — ~30 rows
`colectivo` / `micro` (bus), `remís`, motorbikes everywhere, `ruta`, and the
phrases for telling a driver where to stop.

### 13. `adjectives` — ~50 rows
Arranged as **opposite pairs**, which is far easier to retain than a flat list.

### 14. `colours-and-weather` — ~30 rows
Weather gets heavy weight because it dominates daily life here: `calor`,
`humedad`, `tormenta`, `se largó a llover`.

---

## C. The glue (why sentences look the way they do)

### 15. `prepositions-and-connectors` — ~35 rows
`a, de, en, con, sin, para, por, pero, porque, aunque, entonces` — plus `igual`
and `nomás`, which Paraguayans use constantly and no course teaches.

### 16. `small-words-explained` — ~25 rows
**This is the table that answers your `al` question.** The grammar words that
make sentences unreadable to a beginner.

| spanish | english | note |
|---|---|---|
| al | to the | `a + el` contracted — not a word of its own |
| del | of the / from the | `de + el` contracted |
| hay | there is / there are | from `haber`; never changes for plural |
| me gusta | I like it | literally "it pleases me" — the subject is the thing, not you |
| se | himself / oneself / one | reflexive, and impersonal: `se habla guaraní` |

### 17. `expressions-and-survival` — ~50 rows
Greetings, courtesy, and the phrases that buy you time when you're lost:
`no entiendo`, `¿cómo se dice…?`, `¿me lo repetís más despacio?`, `disculpá mi
español`. Plus emergencies.

### 18. `jopara-and-guarani` — ~40 rows
The table you won't find in any Spanish course, and the one most likely to win
people over. Everyday Guaraní mixed into Spanish: `na` (softener), `nomás`,
`luego` in its local sense, `mitã` (kid), `che`, `anga`, plus `Mba'éichapa`
(hello) and `Aguyje` (thank you).

---

## Proposed UI

A fourth tab, **Tables**, beside Listen / Recall / Table:

- Sections collapsed by default, tap to open — 700 rows shouldn't land on you at once
- One search box across all tables
- A speak button per row, same as the main table

One limitation to flag: the pre-rendered Paraguayan audio only covers the 2000
deck sentences, so these rows would use the device voice. If you want real
`es-PY` audio here too, that's a second pack — about 700 clips, roughly 10
minutes of synthesis and maybe 3 MB. Worth doing, but say so and I'll include it.

## Open questions

1. Cut anything? 18 tables is a lot; 5, 7, 16 and 18 are the highest value.
2. Row counts sensible, or do you want some deeper (numbers to 1000?) or shallower?
3. Want `es-PY` audio for these rows as well?
