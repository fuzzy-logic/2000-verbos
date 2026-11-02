# Notes for Claude

## Resuming the conjugation audio pack

The one outstanding build. Renders all 6,399 forms in `data/conjugations.tsv`
(6,325 distinct strings) into `dist/audio/conj.mp3` plus a `verb|slot` seek
index in `conj.json`. The app already reads it — `playForm()` in
`src/template.html` falls back to the device voice when it isn't downloaded.

```sh
.venv/bin/python3 audio/make_conj_track.py --concurrency 10   # ~35 min from cold
python3 build.py
git add dist/audio/conj.mp3 dist/audio/conj.json && git commit && git push
```

Safe to re-run: clips are cached by `sha1(voice|rate|text)`. Delete any
`audio/clips/*.part` first if a run was interrupted.

**`audio/clips/` does not travel.** It is gitignored and container-local
(~146 MB when full). A fresh container re-synthesises every clip. As of the
last run, 2,995 of 6,325 were cached in the then-current container.

Do NOT rebuild the 33 topic packs — they are already built and committed.

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
python3 -I lib/check_extra.py
python3 build.py              # fails loudly on broken references
```

## Repo conventions

- Netlify deploys from `master`; keep the working branch fast-forwarded into
  it or the site does not update.
- `dist/audio` is tracked in git because Netlify serves it from the repo.
  `.git` is ~216 MB and growing. The user has agreed to a shrink (history
  rewrite, or moving the audio off the repo) as a later piece of work.
- Never commit `PLAN.local.md` — gitignored, holds personal details.

## Still open

- Repo shrink, as above.
- "Wander" mode: a study mode where a card offers three sideways jumps
  instead of next/prev, keeping the trail. `jumpToVerb()` is the primitive
  and the edges exist.
- Family trees: small radial SVGs for the ~20 prefix families with 3+ members
  (tener -> mantener/detener/retener/sostener), which share a conjugation.
