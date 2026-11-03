# Notes for Claude

## Building an audio pack

All 34 packs are built and committed: 33 topic tracks and `conj.mp3` (every
one of the 6,399 forms in `data/conjugations.tsv`, 116 min, 29 MB, with a
`verb|slot` seek index). **Do not rebuild them** without a reason — each is
hours of synthesis.

```sh
.venv/bin/python3 audio/make_conj_track.py --concurrency 10   # ~35 min from cold
python3 build.py
```

Safe to re-run: clips are cached by `sha1(voice|rate|text)`. Delete any
`audio/clips/*.part` first if a run was interrupted.

### Concatenate by stream copy, never by re-encode

`-c copy`, which is what both builders now do. Re-encoding on concat decodes
each input first, and the decoder honours the LAME gapless tags, so **every
input loses one frame** — 0.048s at 24 kHz. Over the 12,798 clips and gaps in
conj.mp3 that was 757 seconds of index drift, and the seek index was useless.

The 33 topic packs do not show this because they were built on a machine
whose ffmpeg did not trim. On ffmpeg 6.1 the same script drifts. If a drift
figure comes out large and negative, this is why.

Stream copy also keeps the audio first-generation and joins in seconds. The
Xing header survives it, so browsers still seek accurately.

**`audio/clips/` does not travel.** It is gitignored and container-local
(~146 MB when full). A fresh container re-synthesises every clip.

### Prerequisites that have each cost an hour

- `edge-tts >= 7.3.1`. 7.2.8 returns 403 on everything: Microsoft rotated the
  Sec-MS-GEC token in October 2026 and 7.3.0 fixed it.
  `python3 -m venv .venv && .venv/bin/pip install 'edge-tts>=7.3.1'`
- `ffmpeg` and `ffprobe` must be on PATH. If the environment lacks them, say
  so rather than working around it.
- **In a cloud container**, edge-tts pins its own CA bundle via certifi, so
  the agent proxy's CA has to be appended to it or every request fails TLS
  verification:
  ```sh
  cat /root/.ccr/ca-bundle.crt >> $(.venv/bin/python3 -c "import certifi;print(certifi.where())")
  ```
  `SSL_CERT_FILE` alone does not work. Concurrency 10 is fine through the
  proxy (~180 clips/min, vs ~56/min at 6 locally).

### Verifying a pack

Index drift under 0.5s (the script prints it), every `conjugations.tsv` row
present in the map, and sample offsets:

```sh
ffmpeg -v info -ss START -t DUR -i conj.mp3 -af volumedetect -f null -
```

Speech reads about -20 dB mean, silence about -91. `-v error` suppresses
volumedetect output — it reports at info level. That mistake has been made
twice now.

## Gates

```sh
python3 -I lib/test_conjugate.py
python3 -I lib/test_pron.py
python3 -I lib/check_extra.py
python3 build.py              # fails loudly on broken references
```

`lib/pron.py` is the only respeller — it feeds the Forms panel, the Verbs tab
and, via `dist/pron.json`, every card. Do not add a JavaScript copy of the
rules; the page reads the generated file. `say()` always marks the stress;
`sentence()` is the one that leaves grammatical and one-syllable words alone.

## Repo conventions

- Netlify deploys from `master`; keep the working branch fast-forwarded into
  it or the site does not update.
- `dist/audio` is tracked in git because Netlify serves it from the repo.
  `.git` is ~240 MB. The user has agreed to a shrink (history rewrite, or
  moving the audio off the repo) as a later piece of work.
- Never commit `PLAN.local.md` — gitignored, holds personal details.

## Still open

- Repo shrink, as above.
- Family trees: small radial SVGs for the ~20 prefix families with 3+ members
  (tener -> mantener/detener/retener/sostener), which share a conjugation.
- More hand-written edges. `data/edges-manual.tsv` has 116 pairs; the graph is
  still thin, and Wander tops up from the same topic because only 179 of 1,919
  verbs have three real links. Every pair added there is a door that means
  something. `build.py` fails loudly if either end is not in the corpus.
