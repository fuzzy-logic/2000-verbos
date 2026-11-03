# Pronunciation on every card

A plan, for approval before any of it is built.

## 1. What already exists

`lib/pron.py` respells Spanish for an English reader — syllabify, find the
stress, map each syllable, with Paraguayan values (seseo, `v` read as `b`, no
yeísmo so `ll` stays `ly`). It is already wired into `lib/make_conjugations.py`,
which writes a `pron` column into `data/conjugations.tsv`.

So pronunciation already shows in exactly two places: the **Forms panel** and
the **Verbs tab**. Both read `c.p`.

The engine is good. Spot-checked at word level:

| word | respelling | |
|---|---|---|
| punto | `PUN-toh` | ✓ |
| perdoname | `per-doh-NAH-meh` | ✓ enclitic stress |
| guaraní | `gwah-rah-NEE` | ✓ |
| construir | `kons-troo-IR` | ✓ hiatus |
| ñandutí | `nyan-doo-TEE` | ✓ |
| bicicleta | `bee-see-KLEH-tah` | ✓ seseo + cluster |
| extranjero | `eks-tran-HEH-roh` | ✓ |

## 2. What is missing

Pronunciation is absent from every **card** — the thing you actually study:

| surface | rows | has pronunciation |
|---|---|---|
| Listen / Recall card (sentence) | 2,764 | ✗ |
| Listen / Recall card (headword verb) | 1,919 | ✗ |
| Wander card (verb + sentence) | — | ✗ |
| Basics tables | 745 | ✗ |
| Deck rows | 2,766 | ✗ |
| Forms panel, Verbs tab | 6,399 | ✓ |

## 3. The one real problem

`phrase()` works on a conjugated form (`he tenido`, `voy a instalar`) because
it deliberately stresses only the last word. **Run it on a sentence and it
falls apart**, in two separate ways:

```
Almorzamos a mediodía en punto.
   al-mor-sah-mos ah meh-dee-oh-dee-ah en pun-TO.
```

1. **Only the last word is stressed.** Every other word comes out flat, so the
   line shows none of the sentence's rhythm.
2. **That last word is stressed wrongly.** Words are split on whitespace, so
   the token is `punto.` with the full stop attached. A word ending in a
   consonant takes final stress by rule — hence `pun-TO` instead of `PUN-toh`.
   Same for `blanca.` → `blan-KA`, and `¿Cuánto cuesta?` → `koo-es-TA?`.

Neither affects anything shipped: conjugated forms carry no punctuation, so
the existing `pron` column is correct. This is a gap in reach, not a live bug.

Smaller word-level defects found while probing:

- `y` → `y` (no vowel in the table). Should be `ee`.
- `México` → `MEH-ksee-koh`. Mexican `x` is an h-sound: `MEH-hee-koh`.
- `examen` → `eh-KSAH-men`; should be `ek-SAH-men` (the `ks` is split across
  the syllable break, not held together as an onset).
- Guaraní words (`mitã`) fall outside Spanish orthography and come out wrong.
- Digits are passed through untouched (`Hay 20 personas` keeps `20`). I would
  leave that alone rather than half-expand numbers.

## 4. Design

**Reuse `lib/pron.py`; do not port it to JavaScript.** It is the single source
of truth, it is already right, and a JS twin would drift from it silently. The
respellings get generated at build time.

**Add `sentence()` alongside `phrase()`**, which is the actual new code:

- tokenise into words *and* punctuation, so `punto.` is respelled as `punto`
  and the `.` is put back afterwards;
- give every word its own stress, not just the last;
- except for a curated list of ~40 **function words** (`el la los de que en y a
  con por un se me te lo…`), which are rendered unstressed. Without this the
  line SHOUTS AT YOU IN EVERY WORD and the real rhythm is lost. With it:

```
Almorzamos a mediodía en punto.
   al-mor-SAH-mos ah meh-dee-oh-DEE-ah en PUN-toh
```

**Ship it as a fetched `pron.json`, keyed by rank**, precached by the service
worker — the same pattern as `conjugations.json` and `edges.json`, so first
paint does not wait for it.

| option | raw | gzipped |
|---|---|---|
| inline into index.html | +222 KB on 673 KB | +75 KB on 171 KB |
| `pron.json` keyed by sentence text | 222 KB | 75 KB |
| **`pron.json` keyed by rank** | **107 KB** | **34 KB** |

34 KB gzipped, fetched after paint, against `conjugations.json` at 729 KB raw
which the app already fetches. This is cheap.

## 5. UI

A third line under the Spanish, dimmer and smaller than the translation, in
the same style as the `pr` line the Forms panel already uses — so the app
gains no new visual vocabulary.

Two things that need care:

- **Recall mode must hide it with the Spanish.** The whole point of Recall is
  producing the sentence yourself; a respelling sitting there gives away the
  answer. It hides and reveals exactly as `esText` does.
- **A Settings toggle, default on.** Some learners find respellings a crutch
  that slows real reading. One switch, remembered per device.

## 6. Work, in order

| # | | gate |
|---|---|---|
| 1 | `sentence()` in `lib/pron.py`: punctuation-safe tokeniser, per-word stress, function-word list | — |
| 2 | Fix `y`, `México`, `examen`; decide Guaraní words | — |
| 3 | `lib/test_pron.py` — ~120 hand-checked cases: the three stress classes, diphthong vs hiatus, `ll`/`y` kept apart, seseo, `v`→`b`, `qu`/`gu`, silent `h`, `rr`, `ñ`, enclitic stress, punctuation, function words | new gate, same shape as `test_conjugate.py` |
| 4 | `build.py` emits `dist/pron.json`; service worker precaches it | `python3 build.py` |
| 5 | Card, Wander card, Deck rows, Basics tables read it | — |
| 6 | Settings toggle + Recall hiding | browser test at 390 and 320 px |

Steps 1–3 are the real work. 4–6 are small.

## 7. What I need decided

1. **Function words unstressed** — recommended, as in §4. The alternative is
   stressing every word, which is louder and less truthful.
2. **Default on or off** for the toggle. I suggest on; you are three weeks from
   arriving and the stress pattern is the thing that makes you intelligible.
3. **Guaraní words** — respell `mitã`, `chipa`, `cocido` with Spanish rules
   (mostly right, occasionally wrong), or leave them as written? I lean to
   leaving genuinely Guaraní spellings alone and respelling the rest.
4. **Basics tables too?** They are not "cards", but numbers, questions and
   greetings are where a beginner most needs the stress marked. I would include
   them.
