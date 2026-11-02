# 2000 Verbos

A frequency-ordered Spanish verb trainer with **Paraguayan** audio — voseo, not `tú`.

Most Spanish courses teach you `tú puedes`. In Paraguay (and Argentina, Uruguay, much of
Central America) people say **`vos podés`**. This builds a verb-and-sentence deck in the
dialect you'll actually hear, with real `es-PY` neural audio for every sentence.

Install it to your phone, download an audio pack once, and it works offline — including
with the screen off while you walk.

## The method

Based on the "learn 2000 verbs with example sentences" approach
([video](https://www.youtube.com/watch?v=etywD4c7S6U)). The idea: verbs carry most of a
sentence's meaning, and frequency is brutally top-heavy, so a few hundred of them plus a
natural example sentence each buys you a disproportionate amount of comprehension.

Frequency decides *which* verbs, but not the order you meet them in. Learning verbs 1–100
and then 101–200 is arbitrary: you get a bus verb, a legal verb and a cooking verb in the
same sitting. So the deck is cut two ways instead, and frequency survives as the sort
order *inside* each group:

- **By topic** — 33 topics in 9 sections, ordered by what you need first after landing:
  greeting and small talk, then buying and paying, then the colectivo, and so on down to
  the bookish verbs you will read rather than say.
- **By tense** — every card the corpus has in the vos imperative, or the preterite, or the
  imperfect, grouped together. Learning *tenés* and *tuve* and *tenía* near each other
  teaches the shape of the verb, not just the word.

Three passes, which the app implements as modes:

1. **Listen** — read the Spanish while you hear it, glancing at the English. Fast, low
   pressure, high volume.
2. **Recall** — the Spanish is hidden. Read the English, say it aloud in Spanish, then
   reveal and check. You will get most of them wrong at first; that is the exercise
   working, not failing.
3. **The walking track** — a pre-rendered MP3 per topic that plays, for each sentence:
   the verb twice (3s apart), the verb in English, the sentence slowly, a 7-second gap
   to repeat it yourself, the English, then the sentence at full speed.

Then **sandwich** it: once the sentences feel easy, speed them to 1.25–1.5× and alternate
with real native podcasts — five minutes of the hard thing, back to the easy thing when it
gets tiring. That gap is where listening comprehension actually gets built.

## Paraguayan Spanish notes

**Voseo.** `vos sos`, `vos tenés`, `vos podés`, `vos querés`. Imperatives lose the `-r` and
take the stress on the last syllable: `vení`, `mirá`, `tomá`, `andá`, `poné`. It's
easier than `tú` — fewer stem changes, because the vos ending carries the stress and the
stem never diphthongises: `podés`, not `puedés`.

**Negative commands** are the one place the sources disagree. Several say Paraguay simply
uses the `tú` subjunctive (`no tengas`), while `no tengás` is widely heard across the Río
de la Plata. The tables show the first and name the second, because you need to recognise
the spoken form but should write the standard one.

**Guaraní.** Around 90% of Paraguayans speak Spanish and Guaraní side by side; Paraguay is
the only country where an indigenous language is spoken by the non-indigenous majority.
Everyday speech is *jopara* — Spanish with Guaraní words and particles mixed in. A couple
of dozen jopara words buys more goodwill than hundreds of Spanish ones.

**No yeísmo.** `ll` and `y` are distinct sounds here, unlike most of Latin America.

The sentences in `data/` lean into all of this: `tereré`, `chipa`, `colectivo`, `plata`,
`heladera`, `lapicera`, `pileta`, `asado`, `departamento`.

## Layout

```
data/verbs_*.tsv         rank, verb_es, verb_en, sentence_es, sentence_en, note,
                         topic, form, verb_token
data/sentences_extra.tsv the extra forms of the top 150 verbs
data/conjugations.tsv    verb, rank, level, slot, label, form, pron, english, note
data/edges.tsv           from_verb, to_verb, type, note
data/topics/_index.tsv   order, slug, section, title, blurb
data/tables/             the Basics reference tables

lib/corpus.py            the merged deck, shared by the build and the audio
lib/conjugate.py         conjugation engine (rules + stem-change + irregular tables)
lib/pron.py              Spanish -> respelling for an English reader
lib/english.py           just enough English morphology to gloss a table
lib/tag_forms.py         which token is the verb, and what form it is in
lib/assign_topics.py     verb -> topic
lib/make_conjugations.py -> data/conjugations.tsv
lib/make_edges.py        -> data/edges.tsv
lib/test_conjugate.py    the engine's gate
lib/check_extra.py       asserts each extra sentence is really in the form it claims

src/template.html        the app; placeholders are filled at build time
build.py                 data + src -> dist/, and fails loudly on a broken reference
audio/make_track.py      one walking track per topic, plus a seek index
audio/make_conj_track.py one clip per conjugated form, plus a seek index
dist/                    what gets deployed
```

## Build

```bash
python3 build.py
```

Regenerating the derived data after a content change:

```bash
python3 -I lib/tag_forms.py        # re-tag forms, then .write() to save
python3 -I lib/make_conjugations.py
python3 -I lib/make_edges.py
python3 -I lib/test_conjugate.py   # must pass
python3 -I lib/check_extra.py      # must pass
```

Audio needs [edge-tts](https://github.com/rany2/edge-tts) **7.3.1 or later** — Microsoft
rotated the `Sec-MS-GEC` token in October 2026 and anything older returns 403 on every
request:

```bash
python3 -m venv .venv && .venv/bin/pip install 'edge-tts>=7.3.1'
.venv/bin/python3 audio/make_track.py --topic buying-paying
.venv/bin/python3 audio/make_track.py --all
.venv/bin/python3 audio/make_conj_track.py
python3 build.py        # regenerates dist/audio/packs.json
```

Clips are cached by a hash of voice, rate and text, so editing one sentence
re-synthesises only that sentence's five clips and re-rolls only its topic pack.

## Deploy

`dist/` is a static folder — any host will do. `netlify.toml` is set up for Netlify with
immutable cache headers on `/audio/*`.

## Design notes

A few things that are deliberate, because the obvious approach doesn't work:

- **Audio lives in IndexedDB as Blobs, not Cache Storage.** Media elements seek by issuing
  Range requests, which a cached `Response` won't satisfy unless the service worker
  hand-rolls 206 replies. An object URL over a Blob seeks natively.
- **Walking mode plays one continuous media element**, not a scripted sequence of clips.
  Mobile browsers throttle background timers, so a JS-driven playback loop stalls once the
  screen locks; a media element keeps going and gets lock-screen controls via MediaSession.
- **Each track ships a seek index** (`verbos_XXXX-YYYY.json`) giving every clip's offset
  and duration, so the same downloaded file serves both the walking track and the
  per-sentence buttons. No duplicated audio.
- **VBR, not CBR.** About two thirds of a track is deliberate silence, which at a constant
  bitrate costs exactly as much to store as speech.
- **Blur applies instantly in Recall mode** (no CSS transition on the way in), otherwise
  advancing to the next card flashes the answer for 180ms before hiding it.

## Licence

MIT for the code. The sentences are written for this project; the audio is generated with
Microsoft's neural voices via edge-tts, so check their terms before redistributing it.
