# Reorganisation proposal — sample of the new structure

Nothing has been built. This is the shape of it, for approval.

---

## 1. What replaces "Verbs 101–200"

The chunk selector is retired. In its place, one **group picker** shared by
Listen, Recall and Deck, with two views you toggle between:

```
┌──────────────────────────────────────────┐
│  BY TOPIC   │   by tense                 │   ← toggle
├──────────────────────────────────────────┤
│  Day one survival                        │
│    Greeting & small talk            42 ▸ │
│    Asking & understanding           38 ▸ │
│    Yes, no, maybe                   31 ▸ │
│    Being & feeling                  27 ▸ │
│  Transactions                            │
│    Buying & paying                  58 ▸ │
│    ...                                   │
└──────────────────────────────────────────┘
```

Tapping a topic loads those cards. Same picker, "by tense" view:

```
│  Present — vos (tenés, podés)      312 ▸ │
│  Present — yo                      266 ▸ │
│  Present — él / ella / usted       241 ▸ │
│  Commands (vos) — ¡vení! ¡mirá!     94 ▸ │
│  Preterite — one completed thing   188 ▸ │
│  Imperfect — used to / was -ing     97 ▸ │
│  Near future — voy a + verb         63 ▸ │
│  Perfect — he + -ado                41 ▸ │
│  Subjunctive — present              58 ▸ │
```

Counts above are illustrative; the real ones come out of the tagging pass.

---

## 2. The 30 topics, in learning order

Order is "what you need first in Asunción", not frequency.

| # | Section | Topic | Example verbs |
|---|---------|-------|---------------|
| 1 | **Day one survival** | Greeting & small talk | saludar, andar, presentar, llamarse, conocer |
| 2 | | Asking & understanding | preguntar, entender, repetir, explicar, significar |
| 3 | | Yes, no, maybe | querer, poder, deber, necesitar, gustar |
| 4 | | Being & feeling | ser, estar, tener, sentir, parecer |
| 5 | **Transactions** | Buying & paying | comprar, pagar, costar, cobrar, gastar |
| 6 | | Haggling & quantities | bajar, llevar, pesar, contar, sobrar |
| 7 | | Bank, cash & phone credit | sacar, cargar, transferir, depositar, alcanzar |
| 8 | **Food & drink** | Ordering & eating | pedir, comer, tomar, probar, servir |
| 9 | | Cooking & the kitchen | cocinar, hervir, freír, cortar, mezclar |
| 10 | | Tereré & drinking together | cebar, convidar, preparar, invitar, compartir |
| 11 | **Getting around** | Transport & the colectivo | ir, venir, subir, bajar, parar |
| 12 | | Directions & places | doblar, seguir, cruzar, quedar, pasar |
| 13 | | Driving & the moto | manejar, estacionar, arrancar, frenar, chocar |
| 14 | **Home & daily life** | The house & renting | alquilar, mudarse, vivir, arreglar, limpiar |
| 15 | | Daily routine | levantarse, bañarse, vestirse, acostarse, dormir |
| 16 | | Fixing, breaking, power | romper, funcionar, andar, prender, apagar |
| 17 | | Weather & the heat | hacer, llover, calentar, refrescar, mojarse |
| 18 | **People** | Family & friends | visitar, cuidar, acompañar, querer, extrañar |
| 19 | | Conversation & opinion | decir, contar, opinar, discutir, coincidir |
| 20 | | Feelings & conflict | enojarse, preocuparse, disculparse, perdonar |
| 21 | | Arranging to meet | quedar, avisar, esperar, cancelar, atrasarse |
| 22 | **Work & admin** | Work & tasks | trabajar, ganar, entregar, reunirse, encargarse |
| 23 | | Paperwork & bureaucracy | firmar, presentar, tramitar, renovar, sellar |
| 24 | | Phone & computer | mandar, descargar, conectarse, borrar, actualizar |
| 25 | **Health** | Body, illness & pharmacy | doler, enfermarse, curar, recetar, mejorarse |
| 26 | | Emergencies | ayudar, avisar, robar, caerse, lastimarse |
| 27 | **Abstract & formal** | Thinking & knowing | suponer, considerar, dudar, deducir, constatar |
| 28 | | Change & cause | convertirse, provocar, generar, influir, derivar |
| 29 | | Formal & written Spanish | constar, consistir, establecer, disponer, regir |
| 30 | | News & institutions | declarar, aprobar, denunciar, financiar, vetar |

Sections 1–6 (topics 1–26) are the useful ones. Section 7–8 is where the
bookish verbs go, last, as agreed.

---

## 3. A conjugation table, as it will actually render

**tener** — to have · irregular (yo is irregular, vos is regular) · rank 4

### A1 — shown by default

| | Form | Say it | English |
|---|---|---|---|
| yo | **tengo** | TEN-go | I have |
| vos | **tenés** | teh-NESS | you have *(Paraguay)* |
| tú | tienes | tee-EH-ness | you have *(elsewhere)* |
| usted / él / ella | **tiene** | tee-EH-neh | you (formal) / he / she has |
| nosotros | **tenemos** | teh-NEH-moss | we have |
| ustedes / ellos | **tienen** | tee-EH-nen | you all / they have |
| command (vos) | **¡tené!** | teh-NEH | have! / take it! |
| going to | **voy a tener** | boy a teh-NEHR | I'm going to have |
| -ing | **teniendo** | teh-nee-EN-doh | having |

### A2 — one tap away  ▸

| Preterite (yo) | **tuve** | TOO-beh | I had (once) |
| Imperfect (yo) | **tenía** | teh-NEE-ah | I used to have |
| Perfect (yo) | **he tenido** | eh teh-NEE-doh | I have had |
| Negative command | **no tengas** | no TEN-gass | don't have |

### B1 — one more tap  ▸

| Future (yo) | **tendré** | ten-DREH | I will have |
| Conditional (yo) | **tendría** | ten-DREE-ah | I would have |
| Subjunctive (yo) | **tenga** | TEN-gah | (that) I have |

**B2 / C1 rows** (imperfect subjunctive *tuviera*, past perfect *había tenido*,
full paradigms rather than yo-only) have their slots in the data model and the
renderer from day one, filled in a later pass. The level switch is a single
setting — raising your ceiling later is a data change, not a rebuild.

Two deliberate changes from your sketch: **voy a tener** replaces the simple
future at A1 (it's what people actually say, and it's three words you already
know), and the simple future drops to B1. *tú* stays but is greyed, labelled
"elsewhere" — you need to recognise it, never to say it.

---

## 4. Extra sentences — tener, as a sample

The top 150 verbs each gain ~5 sentences so every A1/A2 form appears in
context. For tener:

| Form | Spanish | English |
|---|---|---|
| pres-vos | ¿Tenés cambio de cincuenta mil? | Do you have change for fifty thousand? *(existing, rank 4)* |
| pres-yo | Tengo que irme, ya es tarde. | I have to go, it's late already. |
| pret-yo | Ayer tuve un problema con la moto. | Yesterday I had a problem with the moto. |
| imp-yo | Antes tenía otro teléfono. | I used to have a different phone. |
| cmd-vos | Tené cuidado con el perro. | Be careful of the dog. |
| perf-yo | Nunca he tenido dengue. | I've never had dengue. |

Every one of these is a new recording in the es-PY voice.

---

## 5. Data model

Existing files change shape; nothing is thrown away.

**`data/verbs_*.tsv`** — two new columns appended:

```
rank  verb_es  verb_en        sentence_es                       sentence_en                              note          topic                form
4     tener    to have        ¿Tenés cambio de cincuenta mil?   Do you have change for fifty thousand?   voseo: tenés  being-and-feeling    pres-vos
13    llegar   to arrive      El colectivo llega en diez min.   The bus arrives in ten minutes.                        transport-colectivo  pres-3s
```

**`data/topics/_index.tsv`** — same pattern as `data/tables/_index.tsv`:

```
order  slug                 section            title                 blurb
10     greeting-small-talk  Day one survival   Greeting & small talk  ¿Cómo andás? is the whole opening move here.
```

**`data/conjugations.tsv`** — one file, ~6,400 rows for 400 verbs:

```
verb   level  slot      form        pron          english              note
tener  A1     pres-1s   tengo       TEN-go        I have
tener  A1     pres-2s   tenés       teh-NESS      you have             voseo
tener  A2     pret-1s   tuve        TOO-beh       I had (once)         irregular preterite stem tuv-
```

**`data/sentences_extra.tsv`** — the ~750 new ones:

```
verb   form     sentence_es                      sentence_en                       note
tener  pret-1s  Ayer tuve un problema con la moto.  Yesterday I had a problem with the moto.
```

Build-time validation gets stricter: every `topic` must exist in the index,
every `form` must be a known slot, every conjugated verb must have a complete
A1 block, and no verb may be assigned a topic it has no business being in
(checked by hand on review, not by machine).

---

## 6. Card UI

```
┌────────────────────────────────────────────┐
│  Buying & paying          ·  12 / 58       │
│                                            │
│  pagar  ·  to pay                          │
│  present · vos                             │
│                                            │
│  ¿Dónde pago?                              │
│  Where do I pay?                           │
│                                            │
│  [ ▸ play ]   [ conjugations ▾ ]           │
│                                            │
│  ── conjugations (unfolded) ───────────────│
│  yo        pago     PAH-go    I pay        │
│  vos       pagás    pah-GAHSS you pay      │
│  ...                                       │
│  ▸ show A2    ▸ show B1                    │
│                                            │
│  Also in: Haggling & quantities            │
│  See also: Numbers & money (Basics)        │
└────────────────────────────────────────────┘
```

The form the sentence uses is **highlighted in the table** — that is the
card→table link, and it's what makes the grouping teach something.

---

## 7. Audio

The 20 rank packs are replaced by **30 topic packs**, one per topic, each
containing its verbs' walking track in topic order, including the new
sentences. Total stays around 130 MB; sizes range from ~2 MB (Emergencies)
to ~12 MB (Buying & paying).

This invalidates every pack already on your phone — you re-download once. The
app will say so plainly rather than silently re-fetching 130 MB on mobile data.

**Open question I haven't put to you yet:** whether the conjugated *forms*
themselves get audio (tap "tenés" to hear it). For the top 150 verbs' A1 rows
that's ~1,350 clips, about 4 MB, and it's the single highest-value addition
for pronunciation. For all 400 verbs at all levels it's ~6,400 clips and
~20 MB. My recommendation is the former, as a 31st pack.

---

## 8. What does not change

- The hyperpolyglot method itself: read-while-listening, then active recall.
- Frequency order still exists — it's the sort order inside every topic, so
  within "Buying & paying" you still meet *comprar* before *regatear*.
- The Basics tab and its 18 tables, untouched.
- The PWA, IndexedDB offline storage, MediaSession, walking-track structure
  (verb ×2, gap, English, slow sentence, gap, English, fast sentence).
- All 2000 sentences and all existing recordings. Nothing is rewritten; the
  MP3s are re-cut from the cached clips, not re-synthesised.

---

## 9. The graph question

Verdict: **yes for verbs, no for tenses, and no for a force-directed picture.**

### Verbs genuinely form a graph

Measured against the real corpus:

- **182 verbs** are prefixed derivatives of another verb already in the 2000
  (131 families, 35 of them with two or more members): *tener →
  mantener, detener, retener, sostener*; *poner → componer, exponer,
  posponer, reponer*; *volver → devolver, envolver, revolver*; *pedir →
  impedir, despedir, expedir*.
- Most of those **inherit the base verb's entire conjugation**. Learn *tener*
  and four more verbs come free, including their irregular preterites.
  (Not all: *compensar* is regular where *pensar* is e→ie. The engine
  computes both, so the inheritance claim gets checked per family rather
  than assumed.)

That is a real edge with real teaching value, and it falls out of work we're
doing anyway.

### Tenses do not

There are 9–16 of them in a fixed lattice. A graph of sixteen nodes is a
table drawn badly. What's actually wanted there is two navigation moves,
which are not graph-shaped:

- **down a verb** — the conjugation table, already in §3
- **across the verbs** — "show me every verb's vos command", i.e. the
  by-tense view in §1, which is the same traversal

### A force-directed node cloud: no

2000 nodes is a hairball, the hit targets are thumb-hostile, and you cannot
use it while walking — which is where most of your listening hours are going
to happen. The value of graph structure is in **navigation**, not in
visualisation. I'd rather spend the effort on edges than on physics.

### What I'd build instead

**`data/edges.tsv`** — `from, to, type, note`:

| type | count | source | example |
|---|---|---|---|
| `family` | ~182 | derived, then verified | tener → mantener |
| `pattern` | 2000 | from the conjugation engine | regatear → *conjugates like* hablar |
| `confusable` | ~60 | hand-written | ser / estar · saber / conocer · pedir / preguntar · tomar / llevar |
| `opposite` | ~80 | hand-written | subir / bajar · prender / apagar · entrar / salir |
| `reflexive` | ~90 | derived, note hand-written | ir / irse · dormir / dormirse · llamar / llamarse |
| `cooccurs` | ~300 | from the corpus | tener → ir *(«Tengo que irme»)* |

`confusable` is the highest-value set in that table — those pairs are the
actual mistakes English speakers make, and no frequency list surfaces them.

Surfaced two ways:

**1. A sideways row on every card.** Costs one line of UI:

```
│  ¿Dónde pago?                              │
│  Where do I pay?                           │
│                                            │
│  ↔  cobrar (they charge)   ·   pagarse     │
│  ≈  conjugates like hablar                 │
└────────────────────────────────────────────┘
```

**2. "Wander" — a third study mode** beside Listen and Recall. No list, no
order: each card offers three sideways jumps and you follow whichever you
like, with the trail kept so you can see where you've been. This is the graph
as a *study surface* rather than a diagram, and it's the one thing here that
no flashcard app does.

**3. Family trees** — for the ~20 families with three or more members, a small
hand-laid-out radial diagram (base verb centre, derivatives around it with
their meanings and the one note that distinguishes them). Static SVG, eight
nodes, readable on a phone. Worth it precisely because those families share a
conjugation, so the picture is carrying real information.

### Cost

The derived edges are nearly free. The hand-written ones — ~140 pairs of
confusables and opposites, with a note each — are the real work, maybe a
quarter of the authoring effort of the 750 new sentences. Wander mode is
small once the edges exist, because it reuses the card renderer.

### Recommendation

Build the edge table in **phase 1** alongside the topics (derived edges
only — they're free), ship the card's sideways row with it, and hold
`confusable`/`opposite` authoring, Wander mode and the family trees for a
phase of their own once the reorganisation has landed and you've used it.

---

## 10. Build order (approved 2026-11-02)

Decisions locked: topic list §2 approved · conjugation audio for **all 400
verbs at every level** (~6,400 clips, ~20 MB) · hand-written
`confusable`/`opposite` edges, Wander mode and family trees deferred to
phase 2.

### Phase 1 — the data layer

The keystone is a **conjugation engine**, because three separate problems
collapse into it:

1. it generates the 400 tables of §3;
2. run over all 2000 rows it identifies **which token in each sentence is the
   verb** and **what form it is in** — the `form` tag of §1's by-tense view,
   and the unsolved token-marking problem from before;
3. it finds the corpus bugs, starting with the known one at rank 260
   (*cargar* paired with «Se me descargó el celular»).

| Step | Output | Verification |
|---|---|---|
| 1a | `conjugate.py` — rules + irregular table | must reproduce all 45 rows of `data/tables/top-verbs-voseo.tsv` exactly, plus hand-checked spot sample |
| 1b | `form` column on all 2000 rows; verb-token offsets | every row's verb must be locatable in its sentence; failures are data bugs, listed not silently dropped |
| 1c | `data/conjugations.tsv`, top 400, A1–B1 | complete A1 block per verb; no empty slots |
| 1d | `pron.py` — syllabify, stress, respell | Spanish is phonetic, so this is deterministic; checked against the pronunciations hand-written in §3 |
| 1e | `data/topics/_index.tsv` + `topic` column on all 2000 | every topic non-empty; every verb assigned exactly once |
| 1f | `data/edges.tsv` — derived types only | family inheritance verified per family, not assumed |
| 1g | `build.py` ingest + validation | build fails loudly on any broken reference |

### Phase 1.5 — content
~750 extra sentences for the top 150 verbs, covering every A1/A2 form.

### Phase 2 — the app
Group picker with the topic/tense toggle · conjugation panel on the card with
the sentence's own form highlighted · the Verbs tab · the sideways row.
Then the deferred items: hand-written edges, Wander mode, family trees.

### Phase 3 — audio
30 topic packs replacing the 20 rank packs, re-cut from cached clips rather
than re-synthesised · ~6,400 new conjugation-form clips as their own pack ·
a plain warning before the one-off re-download.

Each phase is a commit, and the app keeps working at every commit: the new
columns are additive, and the UI reads them only once phase 2 lands.
