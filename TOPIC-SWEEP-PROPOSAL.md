# Re-sorting every example into the right category

**Applied in 12fddd0.** Kept as the record of why. Both open questions were
answered: hybrid (the six core-verb topics left alone) and all seven new
categories. The audio-pack rebuild it implies was deferred to the repo shrink.

The full move list is in
`topic-moves-proposed.tsv` — 329 rows, one per sentence, with where it is now,
where it would go, and why.

## 1. Why transport examples are sitting in Food

The topic is assigned to the **verb**, never to the sentence. `lib/assign_topics.py`
reads the verb and its English gloss and nothing else, and every one of that
verb's seven sentences inherits the result.

So `tomar` is filed under *Ordering & eating* — reasonable for the verb — and
drags these in with it:

| sentence | sits in | is actually about |
|---|---|---|
| Tomé el colectivo equivocado. | Ordering & eating | taking the wrong bus |
| He tomado mucho sol hoy. | Ordering & eating | the sun |
| He pedido el certificado dos veces. | Ordering & eating | paperwork |
| Compartimos un departamento. | Tereré & drinking | sharing a flat |
| Me picaron los mosquitos. | Ordering & eating | insect bites |
| Lo amenazaron por teléfono. | Ordering & eating | a threat |
| Escurrí bien la ropa. | Ordering & eating | laundry |

And a few verbs are in the wrong topic outright, which puts all their sentences
in the wrong place at once — `crear` ("Creé una cuenta nueva", "¿Creás vos el
documento o yo?") is filed under *Ordering & eating*.

## 2. The one decision I need from you

Two different kinds of topic are mixed together in the list, and they cannot
take the same rule.

**Situation topics** — Food, Transport, Health, Paperwork. The topic *is* the
situation, so a sentence that is not about that situation does not belong.
These get re-sorted strictly.

**Core-verb topics** — *Being & feeling*, *Doing & handling*, *Yes, no, maybe*,
*Seeing & noticing*, *Thinking & knowing*, *Change & cause*. These exist to
drill one verb across many situations. "Hace mucho calor", "Hice el trámite"
and "Hacé de cuenta que no pasó nada" are all under `hacer` **on purpose**.

Sorting those strictly by content would scatter `hacer` across four topics and
destroy the thing they teach. **My recommendation: leave the six core-verb
topics alone and re-sort the other 27.** That is what this proposal does; it
leaves 133 flagged sentences in place that a strict reading would move.

Say the word if you want the strict version instead.

## 3. Seven new categories

Each is a cluster that already exists in the corpus and is currently scattered.

| new topic | sentences | currently spread across | examples |
|---|---|---|---|
| **Studying & learning** | 29 | 19 topics | Aprobé el examen · Memoricé las primeras cien frases · Repaso todas las noches |
| **Building & construction** | 26 | 10 topics | Se derrumbó el techo con la lluvia · Apuntalaron la pared · Pavimentaron la calle recién |
| **Moving country & settling in** | 19 | 8 topics | Me naturalicé después de cinco años · Añoro el invierno de allá · Lo deportaron por papeles vencidos |
| **Travel: flights, boats & staying away** | 15 | 13 topics | El vuelo parte a medianoche · Nos hospedamos con una familia · Declaré todo en la aduana |
| **Cleaning & chores** | 14 | 15 topics | Odio planchar camisas · Barro el patio todas las mañanas · Asoleá las sábanas un rato |
| **The campo: farming & animals** | 9 | — | Ordeñan las vacas a las cinco · Siembran soja en toda esta zona · Crían ganado en el Chaco |
| **Celebrations, church & rites** | 7 | 6 topics | Veneran a la Virgen de Caacupé · Peregrinan a pie en diciembre · El cura bendijo la casa |

The last two are small. For scale, *Tereré & drinking* has 8 today and works
fine, and it grows to 20 under this proposal. If you would rather not have
topics that thin, the fold-ins are: **farming → The house & renting**, and
**celebrations → Family & friends**. I would keep both separate — the campo and
Caacupé are too central here to be footnotes in someone else's category.

## 4. What moves

329 sentences: 265 head sentences and 64 extras. That is 12% of the corpus.

| topic | now | after | |
|---|---|---|---|
| house-renting | 83 | 54 | −29 |
| transport-colectivo | 85 | 62 | −23 |
| directions-places | 61 | 39 | −22 |
| ordering-eating | 60 | 47 | −13 |
| cooking-kitchen | 73 | 60 | −13 |
| feelings-conflict | 187 | 167 | −20 |
| paperwork-bureaucracy | 88 | 77 | −11 |
| greeting-small-talk | 71 | 62 | −9 |
| buying-paying | 79 | 71 | −8 |
| weather-heat | 41 | 57 | **+16** |
| terere-drinking | 8 | 20 | **+12** |
| phone-computer | 64 | 73 | +9 |
| formal-written | 40 | 47 | +7 |
| bank-cash-credit | 48 | 53 | +5 |
| free-time | 134 | 138 | +4 |

No topic ends up empty. The six core-verb topics are untouched.

*Tereré* nearly triples, which is the clearest sign the old scheme was wrong:
"Tomamos tereré todas las tardes" was filed under *Ordering & eating* because
`tomar` is a verb about consuming things.

## 5. The change that makes it possible

`data/sentences_extra.tsv` has no `topic` column — extras inherit their verb's.
A sentence cannot sit in its own category until it can carry one. The proposal
adds that column, left empty for the ~90% of extras that should keep following
their verb.

The head sentences keep using the `topic` column they already have, so 265 of
the 329 moves are edits to files that already support them.

`lib/assign_topics.py` keeps its job of making the first guess for a new verb.
What changes is that a hand-made decision in the data wins, and `overrides.tsv`
grows to hold the verb-level corrections (`crear`, `compartir`, `servir`).

## 6. How the list was built

1. A high-precision pass over all 2,766 sentences, matching concrete domain
   nouns on word boundaries — *colectivo*, *empanada*, *farmacia*. It flagged
   384 sentences naming something from another topic.
2. I read every one of those 384 and rejected roughly a third. The matcher
   wanted to move "Me baño dos veces por día con este calor" to Weather; it is
   a daily routine that happens to mention the heat.
3. A keyword pass cannot see a verb in the wrong topic when its sentences name
   nothing at all, so I read the head sentence of every verb in the situation
   topics as well. That is how `crear`, `ensayar`, `caducar` and the farming
   and construction clusters surfaced.

Borderline cases were left where they are. The 329 are the clear ones.

## 7. What I need

1. **Strict or hybrid** (§2) — hybrid recommended.
2. **Seven new categories, or five** (§3) — whether farming and celebrations
   earn their own place.
3. Then I apply the moves, regenerate, run the gates and the browser suite,
   and push.
