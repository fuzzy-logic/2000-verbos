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

Three passes, which the app implements as modes:

1. **Listen** — read the Spanish while you hear it, glancing at the English. Fast, low
   pressure, high volume.
2. **Recall** — the Spanish is hidden. Read the English, say it aloud in Spanish, then
   reveal and check. You will get most of them wrong at first; that is the exercise
   working, not failing.
3. **The walking track** — a pre-rendered MP3 per chunk that plays, for each sentence:
   the verb twice (3s apart), the verb in English, the sentence slowly, a 7-second gap
   to repeat it yourself, the English, then the sentence at full speed.

Then **sandwich** it: once the sentences feel easy, speed them to 1.25–1.5× and alternate
with real native podcasts — five minutes of the hard thing, back to the easy thing when it
gets tiring. That gap is where listening comprehension actually gets built.

## Paraguayan Spanish notes

**Voseo.** `vos sos`, `vos tenés`, `vos podés`, `vos querés`. Imperatives lose the `-r` and
take the stress on the last syllable: `vení`, `mirá`, `tomá`, `andá`, `poné`. It's
easier than `tú` — fewer stem changes.

**Guaraní.** Around 90% of Paraguayans speak Spanish and Guaraní side by side; Paraguay is
the only country where an indigenous language is spoken by the non-indigenous majority.
Everyday speech is *jopara* — Spanish with Guaraní words and particles mixed in. A couple
of dozen jopara words buys more goodwill than hundreds of Spanish ones.

**No yeísmo.** `ll` and `y` are distinct sounds here, unlike most of Latin America.

The sentences in `data/` lean into all of this: `tereré`, `chipa`, `colectivo`, `plata`,
`heladera`, `lapicera`, `pileta`, `asado`, `departamento`.

## Layout

```
data/*.tsv          rank, verb_es, verb_en, sentence_es, sentence_en, note
src/template.html   the app; /*__DATA__*/ is replaced with the deck at build time
build.py            data/*.tsv + src/ -> dist/   (validates ranks, duplicates, charset)
audio/make_track.py edge-tts + ffmpeg -> dist/audio/*.mp3 and a seek index
dist/               what gets deployed
```

## Build

```bash
python3 build.py
```

Audio needs [edge-tts](https://github.com/rany2/edge-tts):

```bash
python3 -m venv .venv && .venv/bin/pip install edge-tts
.venv/bin/python3 audio/make_track.py --start 1 --end 100
python3 build.py        # regenerates dist/audio/packs.json
```

100 verbs is about 90 seconds of synthesis, 40 minutes of audio, and 6 MB.

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
